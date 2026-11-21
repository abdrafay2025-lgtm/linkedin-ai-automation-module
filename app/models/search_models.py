from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class KeywordNormalizationRequest(BaseModel):
    raw_keywords: str

class NormalizedKeywordResult(BaseModel):
    original_input: str
    normalized_query: str
    tokens: List[str] = []
    identified_connectors: List[str] = []
    token_count: int
    is_valid: bool = True
    rejection_reason: Optional[str] = None

class AISearchQueryOutput(BaseModel):
    keywords: List[str] = []
    target_roles: List[str] = []
    location: Optional[str] = None
    industry: Optional[str] = None
    intent: str

class SearchGenerationResponse(BaseModel):
    status: str
    prompt_version: str
    normalized_input: NormalizedKeywordResult
    search_query: Optional[AISearchQueryOutput] = None
    error_message: Optional[str] = None
