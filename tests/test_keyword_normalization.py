"""
Unit Tests for Module 1: Keyword Normalization.
Ensures deterministic behavior across whitespace, casing, deduplication, 
bounds, and edge cases without relying on an LLM.
"""

import pytest
from app.services.keyword_normalizer import KeywordNormalizer
from app.validators.query_validator import QueryValidator


def test_standard_input():
    """Test standard multi-word input normalization."""
    raw = "AI founders Lahore"
    result = KeywordNormalizer.normalize(raw)

    assert result.is_valid is True
    assert result.tokens == ["ai", "founders", "lahore"]
    assert result.token_count == 3
    assert result.normalized_query == "AI founders Lahore"
    assert result.rejection_reason is None


def test_excessive_whitespace_and_tabs():
    """Test handling of irregular whitespace, tabs, and newlines."""
    raw = "AI    founders  \t\n   Lahore   "
    result = KeywordNormalizer.normalize(raw)

    assert result.is_valid is True
    assert result.tokens == ["ai", "founders", "lahore"]
    assert result.normalized_query == "AI founders Lahore"


def test_case_insensitivity_and_deduplication():
    """Test that duplicates with varying casing are deduplicated while preserving order."""
    raw = "AI founders ai Lahore AI"
    result = KeywordNormalizer.normalize(raw)

    assert result.is_valid is True
    assert result.tokens == ["ai", "founders", "lahore"]
    assert result.token_count == 3
    assert result.normalized_query == "AI founders Lahore"


def test_stop_connector_extraction():
    """Test extraction of relational prepositions without dropping core search tokens."""
    raw = "ai startup founders in lahore"
    result = KeywordNormalizer.normalize(raw)

    assert result.is_valid is True
    assert "in" in result.identified_connectors
    assert result.tokens == ["ai", "startup", "founders", "lahore"]
    assert result.normalized_query == "ai startup founders lahore"


def test_empty_and_whitespace_only_inputs():
    """Test empty string and space-only inputs are properly rejected."""
    empty_result = KeywordNormalizer.normalize("")
    assert empty_result.is_valid is False
    assert "empty" in empty_result.rejection_reason.lower()

    spaces_result = KeywordNormalizer.normalize("     \t  ")
    assert spaces_result.is_valid is False
    assert "empty" in spaces_result.rejection_reason.lower()


def test_special_characters_handling():
    """Test special characters are stripped while preserving technical terms (e.g. Node.js)."""
    raw = "Senior AI Engineer (Node.js) @ Lahore! #hiring"
    result = KeywordNormalizer.normalize(raw)

    assert result.is_valid is True
    assert "ai" in result.tokens
    assert "engineer" in result.tokens
    assert "node.js" in result.tokens
    assert "lahore" in result.tokens
    assert "hiring" in result.tokens


def test_input_exceeding_max_length():
    """Test that inputs exceeding MAX_KEYWORD_LENGTH are rejected."""
    oversized_input = "word " * 60  # > 200 characters
    result = KeywordNormalizer.normalize(oversized_input)

    assert result.is_valid is False
    assert "exceeds maximum permitted threshold" in result.rejection_reason


def test_only_connectors_input():
    """Test inputs that contain only connectors/stop-words."""
    raw = "in at on and or of"
    result = KeywordNormalizer.normalize(raw)

    assert result.is_valid is False
    assert "stop-words" in result.rejection_reason.lower()


def test_query_validator_generic_tokens():
    """Test that overly generic single-word queries are flagged by the validator."""
    result = KeywordNormalizer.normalize("people")
    is_eligible, reason = QueryValidator.validate_for_search_generation(result)

    assert is_eligible is False
    assert "too generic" in reason


def test_query_validator_valid_query():
    """Test that a well-formed query passes validation."""
    result = KeywordNormalizer.normalize("AI startup founders in Lahore")
    is_eligible, reason = QueryValidator.validate_for_search_generation(result)

    assert is_eligible is True
    assert "passed" in reason