from fastapi import APIRouter
from app.config import settings
from app.schemas import HealthResponse

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        ai_enabled=settings.is_ai_enabled,
        ai_provider=settings.AI_PROVIDER if settings.is_ai_enabled else "heuristic_engine",
        ai4bharat_enabled=settings.has_ai4bharat
    )
