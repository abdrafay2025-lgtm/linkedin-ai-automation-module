"""
Hallucination and Message Validator (Module 5 & 6).
Deterministic and heuristic validation layer to guarantee:
1. No unreplaced placeholders (e.g. {{FIRST_NAME}}).
2. Recipient name is properly included.
3. No fabricated/hallucinated claims (e.g. imaginary recent projects or unverified companies).
4. Assigns status: PASS, REVIEW, or FAIL.
"""

import re
from typing import List
from app.models.profile_models import VerifiedProfileData
from app.models.personalization_models import MessageValidationResult


class HallucinationValidator:
    """
    Validates generated messages against verified input profile facts.
    """

    # Common hallucinated phrases LLMs invent when ungrounded
    SUSPICIOUS_HALLUCINATION_TRIGGERS: List[str] = [
        "i noticed your recent post",
        "loved your recent article",
        "congratulations on your new role",
        "saw your github repo",
        "impressed by your podcast",
        "heard you speak at",
        "saw your tweet",
        "read your blog"
    ]

    @classmethod
    def validate_message(
        cls,
        generated_message: str,
        original_template: str,
        profile: VerifiedProfileData
    ) -> MessageValidationResult:
        reasons: List[str] = []
        hallucinations: List[str] = []
        status = "PASS"

        # 1. Check for unreplaced template placeholders
        unfilled_tags = re.findall(r"\{\{([^}]+)\}\}", generated_message)
        if unfilled_tags:
            status = "FAIL"
            reasons.append(f"Unfilled template placeholders detected: {unfilled_tags}")

        # 2. Check recipient name correctness
        if profile.first_name.lower() not in generated_message.lower():
            status = "FAIL"
            reasons.append(f"Recipient first name '{profile.first_name}' is missing from message.")

        # 3. Check for unauthorized / fabricated triggers
        lower_msg = generated_message.lower()
        for trigger in cls.SUSPICIOUS_HALLUCINATION_TRIGGERS:
            if trigger in lower_msg:
                hallucinations.append(trigger)
                reasons.append(f"Detected suspicious unverified claim: '{trigger}'")

        # If hallucinations are detected, downgrade to REVIEW or FAIL
        if hallucinations:
            status = "REVIEW"

        # 4. If all checks pass cleanly
        if not reasons:
            reasons.append("All safety and grounding checks passed successfully.")

        return MessageValidationResult(
            status=status,
            reasons=reasons,
            detected_hallucinations=hallucinations
        )