"""
Embedding generation service using sentence-transformers
"""
from sentence_transformers import SentenceTransformer
from typing import List, Union
import logging
from services.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings"""

    _model: SentenceTransformer = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        """Get or load the embedding model (singleton)"""
        if cls._model is None:
            try:
                logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
                cls._model = SentenceTransformer(settings.EMBEDDING_MODEL)
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
        return cls._model

    @classmethod
    def generate_embedding(cls, text: str) -> List[float]:
        """
        Generate embedding vector for a single text

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector
        """
        try:
            model = cls.get_model()
            embedding = model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    @classmethod
    def generate_embeddings(cls, texts: List[str]) -> List[List[float]]:
        """
        Generate embedding vectors for multiple texts (batched)

        Args:
            texts: List of input texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            model = cls.get_model()
            embeddings = model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise


# Convenience function
def generate_embedding(text: str) -> List[float]:
    """Generate embedding for a single text"""
    return EmbeddingService.generate_embedding(text)
