"""
Unit Tests for Phase 5: Hallucination Prevention & Message Validation.
Verifies that fabricated claims, unfilled placeholders, and missing names
are correctly caught and marked as REVIEW or FAIL.
"""

import pytest
from app.models.profile_models import VerifiedProfileData
from app.validators.hallucination_validator import HallucinationValidator


@pytest.fixture
def recipient_profile():
    return VerifiedProfileData(
        first_name="Bilal",
        headline="Full Stack Developer",
        connection_level="1st"
    )


def test_clean_grounded_message_passes(recipient_profile):
    """Test that an accurate, grounded message gets a PASS."""
    template = "Hi {{FIRST_NAME}}, let's connect regarding {{HEADLINE}}."
    message = "Hi Bilal, let's connect regarding Full Stack Developer."

    result = HallucinationValidator.validate_message(message, template, recipient_profile)

    assert result.status == "PASS"
    assert len(result.detected_hallucinations) == 0


def test_hallucination_triggers_downgrade_to_review(recipient_profile):
    """Test that inventing an unverified post/claim flags status as REVIEW."""
    template = "Hi {{FIRST_NAME}}, let's connect."
    # Fabricating: 'I noticed your recent post'
    hallucinated_message = "Hi Bilal, I noticed your recent post about AI. Let's connect."

    result = HallucinationValidator.validate_message(hallucinated_message, template, recipient_profile)

    assert result.status == "REVIEW"
    assert len(result.detected_hallucinations) > 0
    assert "i noticed your recent post" in result.detected_hallucinations


def test_unfilled_placeholders_fail(recipient_profile):
    """Test that broken or unfilled placeholders mark the message as FAIL."""
    template = "Hi {{FIRST_NAME}}, welcome to {{COMPANY}}."
    broken_message = "Hi Bilal, welcome to {{COMPANY}}."

    result = HallucinationValidator.validate_message(broken_message, template, recipient_profile)

    assert result.status == "FAIL"
    assert any("Unfilled template placeholders" in reason for reason in result.reasons)


def test_missing_recipient_name_fails(recipient_profile):
    """Test that failing to include the recipient's name marks message as FAIL."""
    template = "Hi {{FIRST_NAME}}, let's connect."
    message_without_name = "Hi there, let's connect."

    result = HallucinationValidator.validate_message(message_without_name, template, recipient_profile)

    assert result.status == "FAIL"
    assert any("first name 'Bilal' is missing" in reason for reason in result.reasons)