"""
Query Validator.
Deterministic validation checks to ensure search queries and normalized tokens
meet safety and structural criteria before invoking downstream AI pipelines.
"""

from typing import Tuple
from app.models.search_models import NormalizedKeywordResult


class QueryValidator:
    """
    Validates normalized keywords to ensure they represent meaningful search intent
    and prevents passing garbage data to the LLM.
    """

    # Ambiguous or non-actionable queries that lack professional search context
    PROHIBITED_GENERIC_TOKENS = {
        "anyone", "someone", "people", "user", "users", "profile", "profiles", "test"
    }

    @classmethod
    def validate_for_search_generation(
        cls, normalized_result: NormalizedKeywordResult
    ) -> Tuple[bool, str]:
        """
        Validates whether a NormalizedKeywordResult is eligible for AI query generation.

        Returns:
            Tuple[bool, str]: (is_eligible, reason_message)
        """
        if not normalized_result.is_valid:
            return False, f"Keyword input previously rejected: {normalized_result.rejection_reason}"

        if normalized_result.token_count == 0:
            return False, "No usable tokens found in query."

        # Reject queries made purely of overly generic single words
        if normalized_result.token_count == 1 and normalized_result.tokens[0] in cls.PROHIBITED_GENERIC_TOKENS:
            return False, f"Query '{normalized_result.tokens[0]}' is too generic to determine search intent."

        # Queries must have at least 1 token of length >= 2
        has_substantive_token = any(len(token) >= 2 for token in normalized_result.tokens)
        if not has_substantive_token:
            return False, "Query contains no substantive search criteria."

        return True, "Query passed deterministic pre-validation."