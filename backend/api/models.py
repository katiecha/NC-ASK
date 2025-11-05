"""
Pydantic models for API request/response validation
"""
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query: str = Field(..., min_length=1, max_length=500, description="User's question")
    session_id: str | None = Field(None, description="Optional session identifier")
    view_type: Literal["provider", "patient"] = Field(
        default="patient",
        description="User view type: 'provider' for healthcare professionals, 'patient' for parents/caregivers"
    )

    @field_validator('query')
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        """Validate query is not just whitespace"""
        if not v.strip():
            raise ValueError('Query cannot be empty or just whitespace')
        return v.strip()


class Citation(BaseModel):
    """Citation information"""
    title: str = Field(..., description="Document title")
    url: str | None = Field(None, description="Source URL")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score (0-1)")


class CrisisResource(BaseModel):
    """Crisis resource information"""
    name: str = Field(..., description="Resource name")
    phone: str = Field(..., description="Phone number")
    description: str = Field(..., description="Resource description")
    url: str | None = Field(None, description="Resource URL")
    priority: int = Field(..., description="Priority level")


class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    response: str = Field(..., description="Generated response text")
    citations: list[Citation] = Field(default=[], description="List of citations")
    crisis_detected: bool = Field(default=False, description="Whether crisis was detected")
    crisis_severity: str | None = Field(None, description="Crisis severity level")
    crisis_resources: list[CrisisResource] = Field(default=[], description="Crisis resources")
    disclaimers: list[str] | None = Field(default=None, description="Legal/medical disclaimers")


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")


class IngestionRequest(BaseModel):
    """Request model for document ingestion"""
    title: str = Field(..., description="Document title")
    source_url: str | None = Field(None, description="Source URL")
    content_type: str | None = Field(None, description="Content type (PDF, DOCX, etc.)")
    metadata: dict[str, Any] | None = Field(default={}, description="Additional metadata")


class IngestionResponse(BaseModel):
    """Response model for document ingestion"""
    document_id: int = Field(..., description="Created document ID")
    title: str = Field(..., description="Document title")
    chunks_created: int = Field(..., description="Number of chunks created")
    storage_path: str = Field(..., description="Storage path")
    status: str = Field(..., description="Ingestion status")
