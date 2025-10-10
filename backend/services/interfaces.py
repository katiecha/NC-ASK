"""
Service interfaces using Python Protocol for dependency injection and modularity.
"""
from typing import Protocol, List, Dict, Any, Tuple
from dataclasses import dataclass


# ============================================================================
# Data Models (shared across interfaces)
# ============================================================================

@dataclass
class RetrievalResult:
    """Represents a retrieved document chunk from vector search"""
    chunk_id: int
    chunk_text: str
    document_id: int
    similarity_score: float
    metadata: Dict[str, Any]
    document_title: str | None = None
    source_url: str | None = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "chunk_id": self.chunk_id,
            "chunk_text": self.chunk_text,
            "document_id": self.document_id,
            "similarity_score": self.similarity_score,
            "metadata": self.metadata,
            "document_title": self.document_title,
            "source_url": self.source_url
        }


# ============================================================================
# Service Protocols (Interfaces)
# ============================================================================

class EmbeddingProvider(Protocol):
    """Interface for embedding generation services."""

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector
        """
        ...

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts (batched for efficiency).

        Args:
            texts: List of input texts to embed

        Returns:
            List of embedding vectors
        """
        ...


class VectorStore(Protocol):
    """Interface for vector database operations."""

    def search_similar(
        self,
        query_embedding: List[float],
        top_k: int,
        threshold: float = 0.1
    ) -> List[RetrievalResult]:
        """
        Search for similar document chunks using vector similarity.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            threshold: Minimum similarity threshold

        Returns:
            List of RetrievalResult objects ordered by similarity
        """
        ...

    def store_document_chunks(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[int]:
        """
        Store document chunks with their embeddings.

        Args:
            chunks: List of chunk dictionaries with text, embeddings, and metadata

        Returns:
            List of created chunk IDs
        """
        ...


class LLMProvider(Protocol):
    """Interface for Large Language Model services."""

    def generate_response(
        self,
        query: str,
        context: str,
        temperature: float = 0.3
    ) -> str:
        """
        Generate a response to a query given context.

        Args:
            query: User's question
            context: Retrieved context from knowledge base
            temperature: Generation temperature (0-1)

        Returns:
            Generated response text
        """
        ...

    def add_disclaimers(self, response: str, query: str) -> str:
        """
        Add appropriate disclaimers (medical/legal) to response.

        Args:
            response: Generated response
            query: Original query

        Returns:
            Response with disclaimers added
        """
        ...


class CrisisDetector(Protocol):
    """Interface for crisis detection services."""

    def detect_crisis(self, query: str) -> Tuple[bool, str, List[str]]:
        """
        Detect if a query contains crisis indicators.

        Args:
            query: User query text

        Returns:
            Tuple of (is_crisis, severity_level, matched_keywords)
            - is_crisis: Boolean indicating if crisis was detected
            - severity_level: "critical", "high", "moderate", or "none"
            - matched_keywords: List of matched crisis keywords
        """
        ...

    def get_crisis_resources(self) -> List[Dict[str, Any]]:
        """
        Get list of crisis resources.

        Returns:
            List of crisis resource dictionaries
        """
        ...

    def format_crisis_response(
        self,
        severity: str,
        standard_response: str | None = None
    ) -> str:
        """
        Format a crisis response message.

        Args:
            severity: Crisis severity level
            standard_response: Optional standard response to append

        Returns:
            Formatted crisis response text
        """
        ...


class RetrievalService(Protocol):
    """Interface for document retrieval and context formatting."""

    def retrieve_similar_chunks(
        self,
        query: str,
        top_k: int = 5
    ) -> List[RetrievalResult]:
        """
        Retrieve top-k most similar document chunks for a query.

        Args:
            query: Search query text
            top_k: Number of results to return

        Returns:
            List of RetrievalResult objects ordered by similarity
        """
        ...

    def format_context_for_llm(
        self,
        retrieval_results: List[RetrievalResult],
        max_tokens: int = 2000
    ) -> str:
        """
        Format retrieved chunks into context string for LLM.

        Args:
            retrieval_results: List of retrieved chunks
            max_tokens: Maximum tokens to include (approximate)

        Returns:
            Formatted context string
        """
        ...

    def extract_citations(
        self,
        retrieval_results: List[RetrievalResult]
    ) -> List[Dict[str, Any]]:
        """
        Extract citation information from retrieval results.

        Args:
            retrieval_results: List of retrieved chunks

        Returns:
            List of citation dictionaries
        """
        ...
