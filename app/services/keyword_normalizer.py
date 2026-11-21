"""
Keyword Normalizer Service.
Fully deterministic processor for sanitizing, deduplicating, and preparing user input.
STRICT RULE: No LLM/AI is used here. Deterministic operations remain purely algorithmic.
"""

import re
from typing import Set, Tuple, List
from app.config.settings import settings
from app.models.search_models import NormalizedKeywordResult


class KeywordNormalizer:
    """
    Deterministic normalizer for candidate search keywords.
    Handles excessive whitespace, case normalization, deduplication,
    noise filtering, and input bounds checking.
    """

    # Common prepositions/conjunctions that link search terms but are not search entities themselves
    STOP_CONNECTORS: Set[str] = {
        "in", "at", "on", "for", "with", "and", "or", "of", "to", "by", "from", "the", "a", "an"
    }

    # Minimum token length to be considered an entity or role
    MIN_TOKEN_CHAR_LENGTH: int = 2

    @classmethod
    def normalize(cls, raw_input: str) -> NormalizedKeywordResult:
        """
        Executes a deterministic pipeline on the input string.
        
        Steps:
        1. Bound checking (length and nullity)
        2. Unicode/special character sanitation (retaining alphanumeric, hyphens, and quotes)
        3. Whitespace collapsing
        4. Token extraction and deduplication while preserving sequence order
        5. Stop-connector separation
        """
        # 1. Null / Empty Check
        if not raw_input or not raw_input.strip():
            return NormalizedKeywordResult(
                original_input=raw_input or "",
                normalized_query="",
                tokens=[],
                identified_connectors=[],
                token_count=0,
                is_valid=False,
                rejection_reason="Input keywords string is empty or contains only whitespace."
            )

        # 2. Bound Check against configured limits
        if len(raw_input) > settings.MAX_KEYWORD_LENGTH:
            return NormalizedKeywordResult(
                original_input=raw_input,
                normalized_query="",
                tokens=[],
                identified_connectors=[],
                token_count=0,
                is_valid=False,
                rejection_reason=(
                    f"Input length ({len(raw_input)}) exceeds maximum permitted "
                    f"threshold of {settings.MAX_KEYWORD_LENGTH} characters."
                )
            )

        # 3. Collapse excessive whitespace and sanitize unprintable characters
        cleaned_str = re.sub(r"[\s\t\n\r]+", " ", raw_input).strip()

        # Remove unsupported symbols, retain letters, digits, spaces, hyphens, and periods (e.g. for "Ph.D." or "Node.js")
        sanitized_str = re.sub(r"[^\w\s\.\-]", "", cleaned_str, flags=re.UNICODE)
        sanitized_str = re.sub(r"[\s]+", " ", sanitized_str).strip()

        if not sanitized_str:
            return NormalizedKeywordResult(
                original_input=raw_input,
                normalized_query="",
                tokens=[],
                identified_connectors=[],
                token_count=0,
                is_valid=False,
                rejection_reason="Input contains no recognizable alphanumeric search terms."
            )

        # 4. Extract individual terms preserving initial occurrence order
        raw_terms = sanitized_str.split(" ")
        unique_tokens: List[str] = []
        seen_lower: Set[str] = set()
        connectors_found: List[str] = []

        for term in raw_terms:
            lower_term = term.lower().strip()
            if not lower_term:
                continue

            if lower_term in cls.STOP_CONNECTORS:
                if lower_term not in connectors_found:
                    connectors_found.append(lower_term)
                continue

            if len(lower_term) < cls.MIN_TOKEN_CHAR_LENGTH and not lower_term.isdigit():
                # Filter out isolated 1-character noise (except recognized single digits)
                continue

            if lower_term not in seen_lower:
                seen_lower.add(lower_term)
                unique_tokens.append(term)  # Retain original casing representation for token

        # 5. Check if query became completely empty after noise removal
        if not unique_tokens:
            return NormalizedKeywordResult(
                original_input=raw_input,
                normalized_query="",
                tokens=[],
                identified_connectors=connectors_found,
                token_count=0,
                is_valid=False,
                rejection_reason="Input consists entirely of stop-words or sub-length noise."
            )

        # 6. Max distinct terms check
        if len(unique_tokens) > settings.MAX_NORMALIZED_TERMS:
            return NormalizedKeywordResult(
                original_input=raw_input,
                normalized_query=" ".join(unique_tokens),
                tokens=unique_tokens,
                identified_connectors=connectors_found,
                token_count=len(unique_tokens),
                is_valid=False,
                rejection_reason=(
                    f"Extracted {len(unique_tokens)} distinct terms, which exceeds the limit "
                    f"of {settings.MAX_NORMALIZED_TERMS}."
                )
            )

        # Reconstructed normalized representation
        normalized_query = " ".join(unique_tokens)

        return NormalizedKeywordResult(
            original_input=raw_input,
            normalized_query=normalized_query,
            tokens=[t.lower() for t in unique_tokens],
            identified_connectors=connectors_found,
            token_count=len(unique_tokens),
            is_valid=True,
            rejection_reason=None
        )