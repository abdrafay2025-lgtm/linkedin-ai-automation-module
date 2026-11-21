import json
import re
import httpx
from typing import Optional

from app.config.settings import settings
from app.models.search_models import (
    NormalizedKeywordResult,
    AISearchQueryOutput,
    SearchGenerationResponse,
)
from app.prompts.search_prompt import (
    PROMPT_VERSION,
    SYSTEM_SEARCH_PROMPT,
    USER_SEARCH_PROMPT_TEMPLATE,
)

class AISearchQueryGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY

    def _fallback_parse(self, norm: NormalizedKeywordResult) -> AISearchQueryOutput:
        # Instant Deterministic Fallback if network hangs
        roles = [t.title() for t in norm.tokens if t in ["scientist", "developer", "founder", "engineer", "ceo", "director", "manager"]]
        loc = norm.tokens[-1].title() if norm.identified_connectors and norm.tokens else None
        keywords = [t for t in norm.tokens if t.title() not in roles and (not loc or t.title() != loc)]
        return AISearchQueryOutput(
            keywords=keywords,
            target_roles=roles or ["Professional"],
            location=loc,
            industry="Technology",
            intent=f"Search for {norm.normalized_query}"
        )

    def generate(self, normalized_data: NormalizedKeywordResult) -> SearchGenerationResponse:
        if not normalized_data.is_valid:
            return SearchGenerationResponse(
                status="FAILED", prompt_version=PROMPT_VERSION,
                normalized_input=normalized_data, search_query=None,
                error_message=f"Input invalid: {normalized_data.rejection_reason}"
            )

        if not self.api_key or self.api_key.strip() in ("", "your_gemini_api_key_here"):
            return SearchGenerationResponse(
                status="SUCCESS", prompt_version="deterministic-fallback",
                normalized_input=normalized_data, search_query=self._fallback_parse(normalized_data),
                error_message=None
            )

        user_prompt = USER_SEARCH_PROMPT_TEMPLATE.format(
            normalized_query=normalized_data.normalized_query,
            tokens=", ".join(normalized_data.tokens),
            connectors=", ".join(normalized_data.identified_connectors) or "None"
        )

        try:
            # Bypass Google SDK, use direct REST with STRICT 3-SECOND TIMEOUT
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": user_prompt}]}],
                "systemInstruction": {"parts": [{"text": SYSTEM_SEARCH_PROMPT}]},
                "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
            }

            with httpx.Client(timeout=3.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                ai_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]

            # Clean and parse JSON
            cleaned_json = ai_text.strip()
            cleaned_json = re.sub(r"^```(?:json)?\s*", "", cleaned_json, flags=re.MULTILINE)
            cleaned_json = re.sub(r"\s*```$", "", cleaned_json, flags=re.MULTILINE)
            parsed_dict = json.loads(cleaned_json)

            return SearchGenerationResponse(
                status="SUCCESS", prompt_version=PROMPT_VERSION,
                normalized_input=normalized_data,
                search_query=AISearchQueryOutput(**parsed_dict),
                error_message=None
            )
        except Exception as e:
            # If Google API hangs for more than 3 seconds, Fallback kicks in instantly!
            return SearchGenerationResponse(
                status="SUCCESS", prompt_version="fallback-due-to-network-hang",
                normalized_input=normalized_data, search_query=self._fallback_parse(normalized_data),
                error_message=str(e)
            )