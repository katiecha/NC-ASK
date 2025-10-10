"""
Embedding generation service using sentence-transformers.
"""
from sentence_transformers import SentenceTransformer
from typing import List
import logging
from services.config import settings

logger = logging.getLogger(__name__)


class SentenceTransformerEmbedding:
    """
    Embedding service using sentence-transformers library.

    Features:
    - Lazy loading: Model loaded on first use
    - Batched processing: Efficient for multiple texts
    - Configurable: Model name from settings
    """

    def __init__(self, model_name: str | None = None):
        """
        Initialize embedding service.

        Args:
            model_name: Optional model name override. If None, uses settings.EMBEDDING_MODEL
        """
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model: SentenceTransformer | None = None
        logger.info(f"Initialized SentenceTransformerEmbedding with model: {self.model_name}")

    @property
    def model(self) -> SentenceTransformer:
        """
        Get or load the embedding model (lazy loading).

        Returns:
            Loaded SentenceTransformer model
        """
        if self._model is None:
            try:
                logger.info(f"Loading embedding model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
        return self._model

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for a single text.

        Implements EmbeddingProvider.generate_embedding()

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector (dimension: 384 for all-MiniLM-L6-v2)
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts (batched for efficiency).

        Implements EmbeddingProvider.generate_embeddings()

        Args:
            texts: List of input texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise


# ============================================================================
# Backward Compatibility Layer (DEPRECATED - will be removed in future)
# ============================================================================
# This section provides backward compatibility for existing code that uses
# the old static class methods. New code should use dependency injection instead.

class EmbeddingService:
    """
    DEPRECATED: Legacy static wrapper for backward compatibility.

    Use SentenceTransformerEmbedding instance instead for better testability
    and dependency injection.
    """
    _instance: SentenceTransformerEmbedding | None = None

    @classmethod
    def get_instance(cls) -> SentenceTransformerEmbedding:
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = SentenceTransformerEmbedding()
        return cls._instance

    @classmethod
    def generate_embedding(cls, text: str) -> List[float]:
        """DEPRECATED: Use SentenceTransformerEmbedding instance instead"""
        return cls.get_instance().generate_embedding(text)

    @classmethod
    def generate_embeddings(cls, texts: List[str]) -> List[List[float]]:
        """DEPRECATED: Use SentenceTransformerEmbedding instance instead"""
        return cls.get_instance().generate_embeddings(texts)


def generate_embedding(text: str) -> List[float]:
    """
    DEPRECATED: Convenience function for backward compatibility.

    Use dependency injection with SentenceTransformerEmbedding instance instead.
    """
    return EmbeddingService.generate_embedding(text)
