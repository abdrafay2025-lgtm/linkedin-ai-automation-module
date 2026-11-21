from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from app.models.profile_models import VerifiedProfileData

class PersonalizationRequest(BaseModel):
    template: str
    profile: VerifiedProfileData

class MessageValidationResult(BaseModel):
    status: Literal["PASS", "REVIEW", "FAIL"]
    reasons: List[str] = []
    detected_hallucinations: List[str] = []

class PersonalizationResponse(BaseModel):
    status: Literal["SUCCESS", "FAILED"]
    personalized_message: Optional[str] = None
    validation: MessageValidationResult
    prompt_version: str = "1.0.0"
