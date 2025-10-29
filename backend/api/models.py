"""
Pydantic models for API request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Literal


class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query: str = Field(..., min_length=1, max_length=500, description="User's question")
    session_id: Optional[str] = Field(None, description="Optional session identifier")
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
    url: Optional[str] = Field(None, description="Source URL")
    relevance_score: float = Field(..., ge=0, le=1, description="Relevance score (0-1)")


class CrisisResource(BaseModel):
    """Crisis resource information"""
    name: str = Field(..., description="Resource name")
    phone: str = Field(..., description="Phone number")
    description: str = Field(..., description="Resource description")
    url: Optional[str] = Field(None, description="Resource URL")
    priority: int = Field(..., description="Priority level")


class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    response: str = Field(..., description="Generated response text")
    citations: List[Citation] = Field(default=[], description="List of citations")
    crisis_detected: bool = Field(default=False, description="Whether crisis was detected")
    crisis_severity: Optional[str] = Field(None, description="Crisis severity level")
    crisis_resources: List[CrisisResource] = Field(default=[], description="Crisis resources")
    disclaimers: Optional[List[str]] = Field(default=None, description="Legal/medical disclaimers")


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


class IngestionRequest(BaseModel):
    """Request model for document ingestion"""
    title: str = Field(..., description="Document title")
    source_url: Optional[str] = Field(None, description="Source URL")
    content_type: Optional[str] = Field(None, description="Content type (PDF, DOCX, etc.)")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")


class IngestionResponse(BaseModel):
    """Response model for document ingestion"""
    document_id: int = Field(..., description="Created document ID")
    title: str = Field(..., description="Document title")
    chunks_created: int = Field(..., description="Number of chunks created")
    storage_path: str = Field(..., description="Storage path")
    status: str = Field(..., description="Ingestion status")
