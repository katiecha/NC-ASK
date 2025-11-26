"""
Document retrieval service for RAG pipeline.

This service orchestrates embedding generation and vector search to find
relevant document chunks for a given query.
"""
import logging
from typing import Any

from services.config import settings
from services.interfaces import EmbeddingProvider, RetrievalResult, VectorStore

logger = logging.getLogger(__name__)


class DocumentRetrieval:
    """
    Service for retrieving relevant document chunks.

    Implements the RetrievalService interface using dependency injection.
    This orchestrator combines:
    - Embedding generation (via EmbeddingProvider)
    - Vector similarity search (via VectorStore)
    - Context formatting for LLM consumption

    Example:
        >>> from services.openshift_embeddings import OpenShiftEmbedding
        >>> from services.vector_store import SupabaseVectorStore
        >>>
        >>> embedding_provider = OpenShiftEmbedding()
        >>> vector_store = SupabaseVectorStore()
        >>> retrieval = DocumentRetrieval(vector_store, embedding_provider)
        >>>
        >>> results = retrieval.retrieve_similar_chunks("What is an IEP?")
        >>> for result in results:
        >>>     print(result.document_title)
    """

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_provider: EmbeddingProvider
    ):
        """
        Initialize retrieval service with dependencies.

        Args:
            vector_store: Vector database implementation (Supabase, Pinecone, etc.)
            embedding_provider: Embedding generation service
        """
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        logger.info(
            f"Initialized DocumentRetrieval with "
            f"vector_store={type(vector_store).__name__}, "
            f"embedding_provider={type(embedding_provider).__name__}"
        )

    def retrieve_similar_chunks(
        self,
        query: str,
        top_k: int | None = None
    ) -> list[RetrievalResult]:
        """
        Retrieve top-k most similar document chunks for a query.

        Implements RetrievalService.retrieve_similar_chunks()

        This method:
        1. Generates embedding for the query (via embedding_provider)
        2. Searches for similar chunks (via vector_store)
        3. Returns ranked results

        Args:
            query: Search query text
            top_k: Number of results to return. If None, uses settings.TOP_K_RETRIEVAL

        Returns:
            List of RetrievalResult objects ordered by similarity (highest first)
        """
        try:
            top_k = top_k or settings.TOP_K_RETRIEVAL

            # Step 1: Generate query embedding using the injected provider
            # This could be SentenceTransformer, OpenAI, Cohere, etc.
            query_embedding = self.embedding_provider.generate_embedding(query)

            # Step 2: Search vector store using the injected store
            # This could be Supabase, Pinecone, Weaviate, etc.
            retrieval_results = self.vector_store.search_similar(
                query_embedding=query_embedding,
                top_k=top_k,
                threshold=0.1  # Minimum similarity threshold
            )

            logger.info(f"Retrieved {len(retrieval_results)} chunks for query")
            return retrieval_results

        except Exception as e:
            logger.error(f"Error retrieving similar chunks: {e}", exc_info=True)
            # Return empty list on error rather than failing entire request
            return []

    def format_context_for_llm(
        self,
        retrieval_results: list[RetrievalResult],
        max_tokens: int | None = None
    ) -> str:
        """
        Format retrieved chunks into context string for LLM.

        Implements RetrievalService.format_context_for_llm()

        Args:
            retrieval_results: List of retrieved chunks
            max_tokens: Maximum tokens to include (approximate). If None, uses settings

        Returns:
            Formatted context string with source attributions
        """
        max_tokens = max_tokens or settings.MAX_CONTEXT_TOKENS

        if not retrieval_results:
            return ""

        context_parts = []
        total_chars = 0
        # Rough estimate: 1 token ≈ 4 characters
        max_chars = max_tokens * 4

        for i, result in enumerate(retrieval_results, 1):
            chunk_text = result.chunk_text.strip()
            source_info = result.document_title or f"Document {result.document_id}"

            formatted_chunk = f"[Source {i}: {source_info}]\n{chunk_text}\n"

            # Check if adding this chunk would exceed limit
            if total_chars + len(formatted_chunk) > max_chars:
                logger.info(f"Truncated context at {i-1} chunks (char limit reached)")
                break

            context_parts.append(formatted_chunk)
            total_chars += len(formatted_chunk)

        context = "\n---\n".join(context_parts)
        logger.info(f"Formatted context: {len(context_parts)} chunks, {total_chars} chars")
        return context

    def extract_citations(
        self,
        retrieval_results: list[RetrievalResult]
    ) -> list[dict[str, Any]]:
        """
        Extract citation information from retrieval results.

        Implements RetrievalService.extract_citations()

        Args:
            retrieval_results: List of retrieved chunks

        Returns:
            List of citation dictionaries (one per unique document)
        """
        citations = []
        seen_docs = set()

        for result in retrieval_results:
            # Avoid duplicate citations from the same document
            if result.document_id not in seen_docs:
                citation = {
                    "title": result.document_title or f"Document {result.document_id}",
                    "url": result.source_url,
                    "relevance_score": round(result.similarity_score, 2)
                }
                citations.append(citation)
                seen_docs.add(result.document_id)

        logger.info(f"Extracted {len(citations)} unique citations")
        return citations
