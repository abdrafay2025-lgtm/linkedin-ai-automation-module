"""
Profile Interpreter Service.
Sanitizes and extracts only explicitly verified data points from recipient profiles.
Enforces zero hallucination / zero inference on missing personal attributes.
"""

from typing import Tuple
from app.models.profile_models import VerifiedProfileData, InterpretedProfileSummary
from app.utils.logging_config import setup_logger

logger = setup_logger(__name__)


class ProfileInterpreter:
    """
    Deterministic interpreter for verified recipient profile information.
    Ensures missing fields stay missing.
    """

    @classmethod
    def interpret(cls, profile: VerifiedProfileData) -> InterpretedProfileSummary:
        """
        Extracts verified attributes without guessing or inferring unstated facts.
        """
        # Determine preferred greeting name safely
        preferred_name = profile.first_name

        # Clean headline
        headline_clean = profile.headline.strip() if profile.headline else None

        # Verify 1st degree connection constraint
        is_first_degree = (profile.connection_level.lower().strip() in ("1st", "1"))

        # Count explicitly verified data points
        points = 1  # first_name is guaranteed
        if profile.last_name:
            points += 1
        if headline_clean:
            points += 1
        if profile.profile_url:
            points += 1

        logger.info(f"Interpreted verified profile for: {preferred_name} ({points} data points)")

        return InterpretedProfileSummary(
            preferred_name=preferred_name,
            headline_clean=headline_clean,
            is_first_degree=is_first_degree,
            verified_data_points=points
        )

    @classmethod
    def validate_eligibility(cls, profile: VerifiedProfileData) -> Tuple[bool, str]:
        """
        Pre-checks whether this profile is eligible for personalized outreach.
        """
        summary = cls.interpret(profile)
        if not summary.is_first_degree:
            return False, "Outreach is strictly restricted to 1st-degree connections only."
        return True, "Profile is eligible for personalized message generation."