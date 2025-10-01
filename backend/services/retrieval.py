"""
Vector similarity search and retrieval service
"""
from typing import List, Dict, Any
import logging
from services.supabase_client import get_supabase
from services.embeddings import generate_embedding
from services.config import settings

logger = logging.getLogger(__name__)


class RetrievalResult:
    """Represents a retrieved document chunk"""

    def __init__(
        self,
        chunk_id: int,
        chunk_text: str,
        document_id: int,
        similarity_score: float,
        metadata: Dict[str, Any] = None,
        document_title: str = None,
        source_url: str = None
    ):
        self.chunk_id = chunk_id
        self.chunk_text = chunk_text
        self.document_id = document_id
        self.similarity_score = similarity_score
        self.metadata = metadata or {}
        self.document_title = document_title
        self.source_url = source_url

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "chunk_id": self.chunk_id,
            "chunk_text": self.chunk_text,
            "document_id": self.document_id,
            "similarity_score": self.similarity_score,
            "metadata": self.metadata,
            "document_title": self.document_title,
            "source_url": self.source_url
        }


class RetrievalService:
    """Service for retrieving relevant document chunks"""

    @staticmethod
    def retrieve_similar_chunks(
        query: str,
        top_k: int = None
    ) -> List[RetrievalResult]:
        """
        Retrieve top-k most similar document chunks for a query

        Args:
            query: Search query text
            top_k: Number of results to return

        Returns:
            List of RetrievalResult objects ordered by similarity
        """
        try:
            top_k = top_k or settings.TOP_K_RETRIEVAL

            # Generate query embedding
            query_embedding = generate_embedding(query)

            # Perform vector similarity search using Supabase RPC function
            supabase = get_supabase()

            # Call the match_document_chunks function (to be created in Supabase)
            result = supabase.rpc(
                'match_document_chunks',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': 0.1,  # Minimum similarity threshold
                    'match_count': top_k
                }
            ).execute()

            # Parse results
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

            logger.info(f"Retrieved {len(retrieval_results)} chunks for query")
            return retrieval_results

        except Exception as e:
            logger.error(f"Error retrieving similar chunks: {e}")
            # Return empty list on error rather than failing
            return []

    @staticmethod
    def format_context_for_llm(
        retrieval_results: List[RetrievalResult],
        max_tokens: int = None
    ) -> str:
        """
        Format retrieved chunks into context string for LLM

        Args:
            retrieval_results: List of retrieved chunks
            max_tokens: Maximum tokens to include (approximate)

        Returns:
            Formatted context string
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
                break

            context_parts.append(formatted_chunk)
            total_chars += len(formatted_chunk)

        context = "\n---\n".join(context_parts)
        return context

    @staticmethod
    def extract_citations(
        retrieval_results: List[RetrievalResult]
    ) -> List[Dict[str, Any]]:
        """
        Extract citation information from retrieval results

        Args:
            retrieval_results: List of retrieved chunks

        Returns:
            List of citation dictionaries
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

        return citations
