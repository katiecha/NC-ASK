"""
Embedding generation service using OpenAI-compatible API (for OpenShift-deployed models).

This implementation uses the OpenAI SDK to connect to embedding models deployed on
RedHat OpenShift (e.g., BGE-large-en-v1.5). It can be used with any OpenAI-compatible
embedding API endpoint.
"""
import logging

from openai import OpenAI

from services.config import settings

logger = logging.getLogger(__name__)


class OpenShiftEmbedding:
    """
    Embedding service using OpenAI-compatible API for OpenShift-deployed models.

    Features:
    - Lazy loading: Client configured on first use
    - Batched processing: Efficient for multiple texts
    - Configurable: Model name and base URL from settings
    - OpenAI-compatible: Works with BGE, E5, Instructor, or any embedding model
      served via OpenAI-compatible API
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model_name: str | None = None
    ):
        """
        Initialize OpenShift embedding service.

        Args:
            api_key: Optional API key override. If None, uses settings.OPENSHIFT_EMBEDDING_API_KEY
            base_url: Optional base URL override. If None, uses settings.OPENSHIFT_EMBEDDING_BASE_URL
                     Should NOT include /v1 suffix - will be added automatically by OpenAI SDK
            model_name: Optional model name override. If None, uses settings.EMBEDDING_MODEL
        """
        self.api_key = api_key or settings.OPENSHIFT_EMBEDDING_API_KEY
        raw_base_url = base_url or settings.OPENSHIFT_EMBEDDING_BASE_URL

        # Ensure /v1 suffix is present (OpenAI SDK requires it for custom base_url)
        base = raw_base_url.rstrip('/')
        if not base.endswith('/v1'):
            base = f"{base}/v1"
        self.base_url = base
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._client: OpenAI | None = None
        logger.info(f"Initialized OpenShiftEmbedding with model: {self.model_name}, base_url: {self.base_url}")

    @property
    def client(self) -> OpenAI:
        """
        Get or initialize OpenAI client (lazy loading).

        Returns:
            Configured OpenAI client for embedding endpoint
        """
        if self._client is None:
            try:
                logger.info(f"Initializing OpenAI client for embedding endpoint: {self.base_url}")
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                logger.info("Embedding client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize embedding client: {e}")
                raise
        return self._client

    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding vector for a single text.

        Implements EmbeddingProvider.generate_embedding()

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector
            (dimension: 1024 for BGE-large-en-v1.5)
        """
        try:
            response = self.client.embeddings.create(
                model=self.model_name,
                input=text
            )
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding for text ({len(text)} chars)")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embedding vectors for multiple texts (batched for efficiency).

        Implements EmbeddingProvider.generate_embeddings()

        Args:
            texts: List of input texts to embed

        Returns:
            List of embedding vectors
        """
        try:
            # OpenAI API supports batching natively
            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts
            )
            # Extract embeddings in the same order as input
            embeddings = [item.embedding for item in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings in batch")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
