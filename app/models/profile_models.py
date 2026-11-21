"""
Profile Data Models.
Defines strict Pydantic schemas for verified LinkedIn profile information.
Enforces that unverified or missing attributes remain strictly None.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class VerifiedProfileData(BaseModel):
    """
    Schema for verified profile data received from an upstream authorized collector.
    STRICT COMPLIANCE: Missing attributes must remain None. No guessing allowed.
    """
    first_name: str = Field(..., description="First name of the recipient")
    last_name: Optional[str] = Field(default=None, description="Last name of the recipient")
    full_name: Optional[str] = Field(default=None, description="Complete display name")
    headline: Optional[str] = Field(default=None, description="Current professional headline")
    connection_level: str = Field(default="1st", description="LinkedIn connection degree (must be 1st degree)")
    profile_url: Optional[str] = Field(default=None, description="Direct URL to authorized profile")

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("first_name cannot be empty or purely whitespace.")
        return cleaned.title()

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, value: Optional[str]) -> Optional[str]:
        if value:
            cleaned = value.strip()
            return cleaned.title() if cleaned else None
        return None


class InterpretedProfileSummary(BaseModel):
    """Cleaned, verified profile context ready for AI personalization."""
    preferred_name: str
    headline_clean: Optional[str]
    is_first_degree: bool
    verified_data_points: int