"""
Main FastAPI Application Entrypoint.
Exposes clean RESTful endpoints for integration by the backend developer.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.models.search_models import (
    KeywordNormalizationRequest,
    SearchGenerationResponse,
)
from app.models.personalization_models import (
    PersonalizationRequest,
    PersonalizationResponse,
)
from app.services.keyword_normalizer import KeywordNormalizer
from app.validators.query_validator import QueryValidator
from app.services.query_generator import AISearchQueryGenerator
from app.services.personalization_engine import PersonalizationEngine
from app.validators.hallucination_validator import HallucinationValidator
from app.utils.logging_config import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="AI & Automation Layer for LinkedIn Outreach Workflow"
)

# Enable CORS for developer integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services singletons
query_generator = AISearchQueryGenerator()
personalization_engine = PersonalizationEngine()


@app.get("/health", tags=["System"])
def health_check():
    """Confirms AI service is running and healthy."""
    return {
        "status": "HEALTHY",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV
    }


@app.post(
    "/ai/search-query",
    response_model=SearchGenerationResponse,
    status_code=status.HTTP_200_OK,
    tags=["Search Intelligence"]
)
def generate_search_query(request: KeywordNormalizationRequest):
    """
    Pipeline 1:
    User Keywords -> Normalization -> Validation -> AI Search Intent Generation
    """
    # 1. Deterministic Normalization
    normalized = KeywordNormalizer.normalize(request.raw_keywords)
    if not normalized.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=normalized.rejection_reason
        )

    # 2. Deterministic Validation
    is_valid, reason = QueryValidator.validate_for_search_generation(normalized)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=reason
        )

    # 3. AI Generation
    return query_generator.generate(normalized)


@app.post(
    "/ai/personalize",
    response_model=PersonalizationResponse,
    status_code=status.HTTP_200_OK,
    tags=["Personalization Intelligence"]
)
def personalize_message(request: PersonalizationRequest):
    """
    Pipeline 2:
    Approved Template + Verified Profile -> AI Personalization -> Hallucination Audit
    """
    # 1. Generate Personalized Message
    response = personalization_engine.personalize(request)
    if response.status == "FAILED":
        return response

    # 2. Strict Hallucination & Fact Check
    if response.personalized_message:
        audit_result = HallucinationValidator.validate_message(
            generated_message=response.personalized_message,
            original_template=request.template,
            profile=request.profile
        )
        response.validation = audit_result

    return response