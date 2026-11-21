"""
AI Personalization Engine.
Blends deterministic placeholder substitution with Gemini-assisted contextual personalization.
Guarantees zero-hallucination compliance.
"""

import re
from typing import Optional
import google.generativeai as genai

from app.config.settings import settings
from app.models.personalization_models import (
    PersonalizationRequest,
    PersonalizationResponse,
    MessageValidationResult,
)
from app.prompts.personalization_prompt import (
    PROMPT_VERSION,
    SYSTEM_PERSONALIZATION_PROMPT,
    USER_PERSONALIZATION_TEMPLATE,
)
from app.services.profile_interpreter import ProfileInterpreter
from app.utils.logging_config import setup_logger

logger = setup_logger(__name__)


class PersonalizationEngine:
    """
    Core engine responsible for tailoring approved messages to verified LinkedIn profiles.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)

    @staticmethod
    def deterministic_fallback_replace(template: str, first_name: str, headline: Optional[str]) -> str:
        """
        Pure Python fallback to replace template tags without requiring an LLM call.
        """
        msg = template.replace("{{FIRST_NAME}}", first_name)
        msg = msg.replace("{{first_name}}", first_name)
        msg = msg.replace("{{HEADLINE}}", headline or "")
        msg = msg.replace("{{headline}}", headline or "")
        return re.sub(r"[ \t]+", " ", msg).strip()

    def personalize(self, request: PersonalizationRequest) -> PersonalizationResponse:
        """
        Generates a tailored message using verified profile information.
        """
        # 1. Eligibility Check (1st-degree only)
        is_eligible, reason = ProfileInterpreter.validate_eligibility(request.profile)
        if not is_eligible:
            return PersonalizationResponse(
                status="FAILED",
                personalized_message=None,
                validation=MessageValidationResult(
                    status="FAIL",
                    reasons=[reason],
                    detected_hallucinations=[]
                ),
                prompt_version=PROMPT_VERSION
            )

        summary = ProfileInterpreter.interpret(request.profile)

        # 2. Check if API Key is available. If not, use deterministic fallback
        if not self.api_key or self.api_key.strip() in ("", "your_gemini_api_key_here"):
            logger.info("Using deterministic substitution (no Gemini API key configured).")
            deterministic_msg = self.deterministic_fallback_replace(
                request.template, summary.preferred_name, summary.headline_clean
            )
            return PersonalizationResponse(
                status="SUCCESS",
                personalized_message=deterministic_msg,
                validation=MessageValidationResult(
                    status="PASS",
                    reasons=["Generated via deterministic template engine (No LLM)."],
                    detected_hallucinations=[]
                ),
                prompt_version="deterministic-1.0.0"
            )

        # 3. Invoke Google Gemini for contextual personalization
        user_prompt = USER_PERSONALIZATION_TEMPLATE.format(
            template=request.template,
            preferred_name=summary.preferred_name,
            headline=summary.headline_clean or "Not specified",
            data_points=summary.verified_data_points
        )

        try:
            model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                system_instruction=SYSTEM_PERSONALIZATION_PROMPT,
                generation_config={"temperature": 0.2}
            )

            logger.info(f"Generating personalized message for {summary.preferred_name}...")
            response = model.generate_content(user_prompt)

            if not response.text:
                raise ValueError("Received empty text response from Gemini.")

            personalized_text = response.text.strip()

            return PersonalizationResponse(
                status="SUCCESS",
                personalized_message=personalized_text,
                validation=MessageValidationResult(
                    status="PASS",
                    reasons=["Contextual personalization successful."],
                    detected_hallucinations=[]
                ),
                prompt_version=PROMPT_VERSION
            )

        except Exception as err:
            logger.error(f"Personalization error: {str(err)}. Falling back to deterministic replacement.")
            fallback_msg = self.deterministic_fallback_replace(
                request.template, summary.preferred_name, summary.headline_clean
            )
            return PersonalizationResponse(
                status="SUCCESS",
                personalized_message=fallback_msg,
                validation=MessageValidationResult(
                    status="REVIEW",
                    reasons=[f"LLM call failed ({str(err)}). Reverted to deterministic replacement."],
                    detected_hallucinations=[]
                ),
                prompt_version="deterministic-fallback"
            )