"""
Unit Tests for Phase 2: AI Search Query Generation.
Verifies parsing, prompt formatting, schema validation, and error recovery.
"""

from unittest.mock import MagicMock, patch
import pytest

from app.models.search_models import NormalizedKeywordResult, AISearchQueryOutput
from app.services.query_generator import AISearchQueryGenerator


@pytest.fixture
def sample_normalized_input():
    return NormalizedKeywordResult(
        original_input="AI founders in Lahore",
        normalized_query="AI founders Lahore",
        tokens=["ai", "founders", "lahore"],
        identified_connectors=["in"],
        token_count=3,
        is_valid=True,
        rejection_reason=None
    )


def test_missing_api_key_fails_gracefully(sample_normalized_input):
    """Test that missing API key returns structured failure instead of crashing."""
    generator = AISearchQueryGenerator(api_key="")
    response = generator.generate(sample_normalized_input)

    assert response.status == "FAILED"
    assert "GEMINI_API_KEY is not configured" in response.error_message
    assert response.search_query is None


@patch("google.generativeai.GenerativeModel")
def test_successful_query_generation(mock_gemini_class, sample_normalized_input):
    """Test successful response parsing from Gemini output."""
    mock_response = MagicMock()
    mock_response.text = """
    {
        "keywords": ["AI"],
        "target_roles": ["Founder"],
        "location": "Lahore",
        "industry": "Artificial Intelligence",
        "intent": "Find founders of AI companies in Lahore"
    }
    """
    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_gemini_class.return_value = mock_model_instance

    generator = AISearchQueryGenerator(api_key="mock_test_key")
    result = generator.generate(sample_normalized_input)

    assert result.status == "SUCCESS"
    assert result.search_query is not None
    assert result.search_query.location == "Lahore"
    assert "Founder" in result.search_query.target_roles