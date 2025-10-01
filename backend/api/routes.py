"""
API route handlers
"""
from fastapi import APIRouter, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
import logging
from api.models import (
    QueryRequest,
    QueryResponse,
    HealthResponse,
    ErrorResponse,
    Citation,
    CrisisResource
)
from services.rag_pipeline import RAGPipeline
from services.crisis_detection import CrisisDetector

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Main query endpoint for asking questions

    Args:
        request: QueryRequest with user's question

    Returns:
        QueryResponse with answer, citations, and crisis info
    """
    try:
        logger.info(f"Received query request (session: {request.session_id})")

        # Process query through RAG pipeline
        result = await RAGPipeline.process_query(
            query=request.query,
            session_id=request.session_id
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
        )


@router.get("/crisis-resources")
async def get_crisis_resources():
    """
    Get list of crisis resources

    Returns:
        List of crisis resources
    """
    try:
        resources = CrisisDetector.get_crisis_resources()
        return {"resources": resources}
    except Exception as e:
        logger.error(f"Error getting crisis resources: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving crisis resources"
        )


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


@router.get("/api/health", response_model=HealthResponse)
async def api_health_check():
    """
    Alternative health check endpoint (with /api prefix for backwards compatibility)

    Returns:
        Health status
    """
    return HealthResponse(
        status="healthy",
        service="NC-ASK Backend API"
    )
