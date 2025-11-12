"""
API route handlers with dependency injection.
"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status

from api.models import Citation, CrisisResource, HealthResponse, QueryRequest, QueryResponse
from services.service_factory import get_service_factory

logger = logging.getLogger(__name__)

router = APIRouter()

# Lazy initialization: Services created on first request, not at import time
_rag_pipeline = None


def get_rag_pipeline():
    """
    Dependency function for RAG pipeline (lazy initialization).

    This is called on first request, not at module import time.
    This prevents Docker from trying to connect to Supabase during startup.
    """
    global _rag_pipeline
    if _rag_pipeline is None:
        logger.info("Initializing RAG pipeline (first request)")
        service_factory = get_service_factory()
        _rag_pipeline = service_factory.create_rag_pipeline()
    return _rag_pipeline


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(
    request: QueryRequest,
    rag_pipeline=Depends(get_rag_pipeline)
):
    """
    Main query endpoint for asking questions.

    Uses dependency-injected RAG pipeline for processing.

    Args:
        request: QueryRequest with user's question and view type
        rag_pipeline: Injected RAG pipeline (lazy-loaded on first use)

    Returns:
        QueryResponse with answer, citations, and crisis info
    """
    try:
        logger.info(f"Received query request (session: {request.session_id}, view: {request.view_type})")

        # Process query through RAG pipeline (using injected dependencies with view-specific prompting)
        result = await rag_pipeline.process_query(
            query=request.query,
            session_id=request.session_id,
            view_type=request.view_type
        )

        # Convert to response model
        citations = [Citation(**cite) for cite in result.get("citations", [])]
        crisis_resources = [
            CrisisResource(**res) for res in result.get("crisis_resources", [])
        ]

        response = QueryResponse(
            response=result["response"],
            citations=citations,
            crisis_detected=result.get("crisis_detected", False),
            crisis_severity=result.get("crisis_severity"),
            crisis_resources=crisis_resources
        )

        return response

    except Exception as e:
        logger.error(f"Error in query endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your query"
        ) from e


@router.get("/crisis-resources")
async def get_crisis_resources():
    """
    Get list of crisis resources.

    Uses dependency-injected crisis detector.

    Returns:
        List of crisis resources
    """
    try:
        # Get crisis detector from the factory (no DB connection needed)
        factory = get_service_factory()
        crisis_detector = factory.get_crisis_detector()
        resources = crisis_detector.get_crisis_resources()
        return {"resources": resources}
    except Exception as e:
        logger.error(f"Error getting crisis resources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving crisis resources"
        ) from e


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint

    Returns:
        Health status
    """
    return HealthResponse(
        status="healthy",
        service="NC-ASK Backend API"
    )
