import pytest
from app.models.profile_models import VerifiedProfileData
from app.services.profile_interpreter import ProfileInterpreter

def test_standard_profile_interpretation():
    profile = VerifiedProfileData(first_name="  ahmed  ", last_name="khan", headline="AI Engineer at TechCorp", connection_level="1st", profile_url="https://linkedin.com/in/ahmedkhan")
    summary = ProfileInterpreter.interpret(profile)
    assert summary.preferred_name == "Ahmed"
    assert summary.headline_clean == "AI Engineer at TechCorp"
    assert summary.is_first_degree is True
    assert summary.verified_data_points == 4

def test_minimal_profile_preserves_missing_data():
    profile = VerifiedProfileData(first_name="Sara", connection_level="1st")
    summary = ProfileInterpreter.interpret(profile)
    assert summary.preferred_name == "Sara"
    assert summary.headline_clean is None
    assert summary.verified_data_points == 1

def test_reject_non_first_degree_connection():
    profile = VerifiedProfileData(first_name="Zubair", connection_level="2nd")
    is_eligible, reason = ProfileInterpreter.validate_eligibility(profile)
    assert is_eligible is False
    assert "1st-degree connections only" in reason

def test_first_name_cannot_be_empty():
    with pytest.raises(ValueError):
        VerifiedProfileData(first_name="   ", connection_level="1st")
