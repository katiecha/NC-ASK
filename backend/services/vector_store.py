"""
Vector store implementations for document storage and similarity search.

This module provides concrete implementations of the VectorStore interface,
allowing easy swapping between different vector databases (Supabase, Pinecone, Weaviate, etc.).
"""
import logging
from typing import Any

from services.interfaces import RetrievalResult
from services.supabase_client import get_supabase

logger = logging.getLogger(__name__)


class SupabaseVectorStore:
    """
    Vector store implementation using Supabase with pgvector extension.

    Implements the VectorStore interface for dependency injection.
    This wraps all Supabase-specific vector operations, making it easy to
    swap for other vector databases like Pinecone, Weaviate, or Qdrant.

    Features:
    - PostgreSQL + pgvector extension for vector similarity search
    - Integrated with Supabase ecosystem (auth, storage, etc.)
    - Cosine similarity search via RPC functions
    - Metadata filtering support

    Example swap:
        # Current
        vector_store = SupabaseVectorStore()

        # Future: Switch to Pinecone
        vector_store = PineconeVectorStore(api_key="...", index="nc-ask")

        # Your code doesn't change - same interface!
        results = vector_store.search_similar(embedding, top_k=5)
    """

    def __init__(self, table_name: str = "document_chunks"):
        """
        Initialize Supabase vector store.

        Args:
            table_name: Name of the table storing document chunks.
                       Default is "document_chunks"
        """
        self.table_name = table_name
        self.client = get_supabase()
        logger.info(f"Initialized SupabaseVectorStore with table: {table_name}")

    def search_similar(
        self,
        query_embedding: list[float],
        top_k: int,
        threshold: float = 0.1
    ) -> list[RetrievalResult]:
        """
        Search for similar document chunks using vector similarity.

        Implements VectorStore.search_similar()

        This uses a Supabase RPC function `match_document_chunks` that performs
        cosine similarity search using pgvector. The RPC function should be created
        in your Supabase database (see setup scripts).

        Args:
            query_embedding: Query embedding vector (e.g., 384-dim for all-MiniLM-L6-v2)
            top_k: Number of results to return
            threshold: Minimum similarity threshold (0-1). Lower = more permissive

        Returns:
            List of RetrievalResult objects ordered by similarity (highest first)

        Example:
            >>> store = SupabaseVectorStore()
            >>> embedding = [0.1, 0.2, ...]  # 384-dim vector
            >>> results = store.search_similar(embedding, top_k=5, threshold=0.3)
            >>> for result in results:
            >>>     print(f"{result.document_title}: {result.similarity_score:.2f}")
        """
        try:
            # Call the match_document_chunks RPC function in Supabase
            # This function performs: SELECT * FROM match_document_chunks(...)
            result = self.client.rpc(
                'match_document_chunks',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': threshold,
                    'match_count': top_k
                }
            ).execute()

            # Parse Supabase response into RetrievalResult objects
            retrieval_results = []
            if result.data:
                for row in result.data:
                    retrieval_result = RetrievalResult(
                        chunk_id=row['id'],
                        chunk_text=row['chunk_text'],
                        document_id=row['document_id'],
                        similarity_score=row['similarity'],
                        metadata=row.get('metadata', {}),
                        document_title=row.get('document_title'),
                        source_url=row.get('source_url')
                    )
                    retrieval_results.append(retrieval_result)

            logger.info(
                f"Vector search returned {len(retrieval_results)} results "
                f"(threshold={threshold}, top_k={top_k})"
            )
            return retrieval_results

        except Exception as e:
            logger.error(f"Error performing vector search in Supabase: {e}", exc_info=True)
            # Return empty list on error rather than failing the entire request
            # This allows graceful degradation
            return []

    def store_document_chunks(
        self,
        chunks: list[dict[str, Any]]
    ) -> list[int]:
        """
        Store document chunks with their embeddings in Supabase.

        Implements VectorStore.store_document_chunks()

        Args:
            chunks: List of chunk dictionaries containing:
                - chunk_text: str - The text content
                - embedding: List[float] - The embedding vector
                - document_id: int - Parent document ID
                - chunk_index: int - Position in document
                - metadata: Dict[str, Any] - Optional metadata

        Returns:
            List of created chunk IDs

        Example:
            >>> chunks = [
            >>>     {
            >>>         "chunk_text": "IEP stands for...",
            >>>         "embedding": [0.1, 0.2, ...],
            >>>         "document_id": 1,
            >>>         "chunk_index": 0,
            >>>         "metadata": {"section": "definitions"}
            >>>     }
            >>> ]
            >>> chunk_ids = store.store_document_chunks(chunks)
            >>> print(f"Created chunks: {chunk_ids}")
        """
        try:
            # Insert chunks into Supabase table
            result = self.client.table(self.table_name).insert(chunks).execute()

            if result.data:
                chunk_ids = [row['id'] for row in result.data]
                logger.info(f"Stored {len(chunk_ids)} chunks in Supabase vector store")
                return chunk_ids
            else:
                logger.warning("No chunks were stored")
                return []

        except Exception as e:
            logger.error(f"Error storing document chunks in Supabase: {e}", exc_info=True)
            raise

    def delete_document_chunks(self, document_id: int) -> int:
        """
        Delete all chunks belonging to a document.

        Useful for re-ingesting updated documents or cleaning up deleted documents.

        Args:
            document_id: ID of the document whose chunks should be deleted

        Returns:
            Number of chunks deleted
        """
        try:
            result = self.client.table(self.table_name).delete().eq(
                'document_id', document_id
            ).execute()

            count = len(result.data) if result.data else 0
            logger.info(f"Deleted {count} chunks for document {document_id}")
            return count

        except Exception as e:
            logger.error(f"Error deleting document chunks: {e}", exc_info=True)
            raise

    def get_chunk_count(self) -> int:
        """
        Get total number of chunks in the vector store.

        Useful for monitoring and diagnostics.

        Returns:
            Total chunk count
        """
        try:
            result = self.client.table(self.table_name).select(
                'id', count='exact'
            ).execute()

            count = result.count if hasattr(result, 'count') else 0
            logger.info(f"Total chunks in vector store: {count}")
            return count

        except Exception as e:
            logger.error(f"Error getting chunk count: {e}", exc_info=True)
            return 0


# ============================================================================
# Example: Alternative Vector Store Implementation
# ============================================================================
# This demonstrates how easy it is to swap vector store implementations!
# The InMemoryVectorStore is useful for:
# - Unit testing (no database required)
# - Local development
# - Demo/prototype environments

class InMemoryVectorStore:
    """
    Simple in-memory vector store for testing and development.

    Implements the VectorStore interface but stores everything in memory.
    No database required! Great for:
    - Unit tests (fast, isolated, no mocking needed)
    - Local development without Supabase
    - Integration tests

    Example:
        >>> # In your tests
        >>> mock_store = InMemoryVectorStore()
        >>> mock_store.store_document_chunks([{
        >>>     "chunk_text": "test",
        >>>     "embedding": [0.1] * 384,
        >>>     "document_id": 1,
        >>>     "chunk_index": 0
        >>> }])
        >>> results = mock_store.search_similar([0.1] * 384, top_k=1)
        >>> assert len(results) == 1
    """

    def __init__(self):
        """Initialize in-memory storage"""
        self.chunks: list[dict[str, Any]] = []
        self.next_id = 1
        logger.info("Initialized InMemoryVectorStore (no database)")

    def search_similar(
        self,
        query_embedding: list[float],
        top_k: int,
        threshold: float = 0.1
    ) -> list[RetrievalResult]:
        """
        Search for similar chunks using cosine similarity.

        Pure Python implementation - no database needed!
        """
        if not self.chunks:
            return []

        try:
            import numpy as np
        except ImportError:
            logger.error("numpy required for InMemoryVectorStore")
            return []

        # Calculate cosine similarity for each chunk
        query_vec = np.array(query_embedding)
        similarities = []

        for chunk in self.chunks:
            if 'embedding' not in chunk:
                continue

            chunk_vec = np.array(chunk['embedding'])

            # Cosine similarity = dot product / (norm1 * norm2)
            norm_product = np.linalg.norm(query_vec) * np.linalg.norm(chunk_vec)
            if norm_product == 0:
                continue

            similarity = np.dot(query_vec, chunk_vec) / norm_product

            if similarity >= threshold:
                similarities.append((chunk, float(similarity)))

        # Sort by similarity (descending) and take top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_results = similarities[:top_k]

        # Convert to RetrievalResult objects
        results = []
        for chunk, similarity in top_results:
            result = RetrievalResult(
                chunk_id=chunk['id'],
                chunk_text=chunk['chunk_text'],
                document_id=chunk['document_id'],
                similarity_score=similarity,
                metadata=chunk.get('metadata', {}),
                document_title=chunk.get('document_title'),
                source_url=chunk.get('source_url')
            )
            results.append(result)

        logger.info(f"In-memory search returned {len(results)} results")
        return results

    def store_document_chunks(
        self,
        chunks: list[dict[str, Any]]
    ) -> list[int]:
        """Store chunks in memory"""
        chunk_ids = []

        for chunk in chunks:
            chunk_id = self.next_id
            self.next_id += 1

            chunk_copy = chunk.copy()
            chunk_copy['id'] = chunk_id
            self.chunks.append(chunk_copy)
            chunk_ids.append(chunk_id)

        logger.info(f"Stored {len(chunk_ids)} chunks in memory")
        return chunk_ids

    def clear(self):
        """Clear all chunks (useful for tests)"""
        self.chunks = []
        self.next_id = 1
        logger.info("Cleared all chunks from memory")
