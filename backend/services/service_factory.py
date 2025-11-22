"""
Service Factory for Dependency Injection.

This module is the "glue" that wires together all service dependencies.
It's the ONLY place where you specify which concrete implementations to use.

Want to swap Gemini for OpenAI? Change ONE line here.
Want to swap Supabase for Pinecone? Change ONE line here.
No other code needs to change!

Example:
    >>> # Get all services configured and ready to use
    >>> factory = ServiceFactory()
    >>> rag_pipeline = factory.create_rag_pipeline()
    >>> result = rag_pipeline.process_query("What is an IEP?")
"""
import logging

from services.config import settings
from services.crisis_detection import KeywordCrisisDetector

# Import concrete implementations
from services.embeddings import SentenceTransformerEmbedding
from services.openshift_embeddings import OpenShiftEmbedding
from services.interfaces import CrisisDetector as CrisisDetectorProtocol

# Import interfaces
from services.interfaces import EmbeddingProvider, LLMProvider, VectorStore
from services.interfaces import RetrievalService as RetrievalServiceProtocol
from services.llm_service import GeminiLLM
from services.openshift_llm import OpenShiftLLM
from services.retrieval import DocumentRetrieval
from services.vector_store import InMemoryVectorStore, SupabaseVectorStore

logger = logging.getLogger(__name__)


class ServiceFactory:
    """
    Factory for creating and wiring service dependencies.

    This class follows the Factory pattern to centralize service creation.
    It makes it easy to:
    - Swap implementations (change config, not code)
    - Test with mocks (inject test dependencies)
    - Manage service lifecycles

    Usage:
        >>> # Production usage
        >>> factory = ServiceFactory()
        >>> rag_pipeline = factory.create_rag_pipeline()

        >>> # Testing usage
        >>> from unittest.mock import Mock
        >>> mock_llm = Mock(spec=LLMProvider)
        >>> factory = ServiceFactory(llm_provider=mock_llm)
        >>> rag_pipeline = factory.create_rag_pipeline()
        >>> # Now uses your mock instead of real Gemini API!
    """

    def __init__(
        self,
        # Allow dependency injection for testing
        embedding_provider: EmbeddingProvider | None = None,
        vector_store: VectorStore | None = None,
        llm_provider: LLMProvider | None = None,
        crisis_detector: CrisisDetectorProtocol | None = None,
        use_in_memory_store: bool = False
    ):
        """
        Initialize service factory.

        Args:
            embedding_provider: Optional override for embedding service
            vector_store: Optional override for vector store
            llm_provider: Optional override for LLM service
            crisis_detector: Optional override for crisis detector
            use_in_memory_store: If True, use in-memory vector store (for testing)
        """
        # Create or use provided dependencies
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._llm_provider = llm_provider
        self._crisis_detector = crisis_detector
        self._use_in_memory_store = use_in_memory_store

        logger.info("Initialized ServiceFactory")

    # =================================================================
    # Individual Service Getters (lazy initialization)
    # =================================================================

    def get_embedding_provider(self) -> EmbeddingProvider:
        """
        Get embedding provider.

        Default: OpenShiftEmbedding with BGE-large-en-v1.5 (deployed on OpenShift)

        To swap back to local embeddings:
            Return SentenceTransformerEmbedding(model_name=settings.EMBEDDING_MODEL) instead
        """
        if self._embedding_provider is None:
            logger.info("Creating OpenShiftEmbedding provider")
            self._embedding_provider = OpenShiftEmbedding(
                model_name=settings.EMBEDDING_MODEL
            )
        return self._embedding_provider

    def get_vector_store(self) -> VectorStore:
        """
        Get vector store.

        Default: SupabaseVectorStore with pgvector
        Test mode: InMemoryVectorStore

        To swap for Pinecone:
            1. Create PineconeVectorStore class implementing VectorStore
            2. Return PineconeVectorStore() here instead
        """
        if self._vector_store is None:
            if self._use_in_memory_store:
                logger.info("Creating InMemoryVectorStore (test mode)")
                self._vector_store = InMemoryVectorStore()
            else:
                logger.info("Creating SupabaseVectorStore")
                self._vector_store = SupabaseVectorStore()

        return self._vector_store

    def get_llm_provider(self) -> LLMProvider:
        """
        Get LLM provider.

        Default: OpenShiftLLM with OpenAI-compatible API (deployed on OpenShift)

        To swap back to Gemini:
            Return GeminiLLM(model_name=settings.LLM_MODEL, temperature=settings.LLM_TEMPERATURE) instead
        """
        if self._llm_provider is None:
            logger.info("Creating OpenShiftLLM provider")
            self._llm_provider = OpenShiftLLM(
                model_name=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE
            )
        return self._llm_provider

    def get_crisis_detector(self) -> CrisisDetectorProtocol:
        """
        Get crisis detector.

        Default: KeywordCrisisDetector

        To swap for ML-based detector:
            1. Create MLCrisisDetector class implementing CrisisDetector
            2. Return MLCrisisDetector() here instead
        """
        if self._crisis_detector is None:
            logger.info("Creating KeywordCrisisDetector")
            self._crisis_detector = KeywordCrisisDetector()
        return self._crisis_detector

    def get_retrieval_service(self) -> RetrievalServiceProtocol:
        """
        Get retrieval service.

        This wires together:
        - Vector store (for similarity search)
        - Embedding provider (for query embeddings)
        """
        logger.info("Creating DocumentRetrieval service")
        return DocumentRetrieval(
            vector_store=self.get_vector_store(),
            embedding_provider=self.get_embedding_provider()
        )

    # =================================================================
    # High-Level Service Creation
    # =================================================================

    def create_rag_pipeline(self):
        """
        Create fully-configured RAG pipeline.

        This is the main entry point for the application.
        Returns a RAG pipeline with all dependencies wired up.

        Returns:
            RAGPipeline instance ready to process queries
        """
        # Import here to avoid circular dependency
        from services.rag_pipeline import RAGPipeline

        logger.info("Creating RAG pipeline with all dependencies")

        pipeline = RAGPipeline(
            retrieval_service=self.get_retrieval_service(),
            llm_provider=self.get_llm_provider(),
            crisis_detector=self.get_crisis_detector()
        )

        logger.info(
            f"RAG pipeline created with: "
            f"embedding={type(self.get_embedding_provider()).__name__}, "
            f"vector_store={type(self.get_vector_store()).__name__}, "
            f"llm={type(self.get_llm_provider()).__name__}, "
            f"crisis_detector={type(self.get_crisis_detector()).__name__}"
        )

        return pipeline


# =================================================================
# Global Factory Instance (for easy access)
# =================================================================

_default_factory: ServiceFactory | None = None


def get_service_factory() -> ServiceFactory:
    """
    Get the default service factory (singleton).

    This provides a convenient way to access services throughout the app.

    Usage:
        >>> from services.service_factory import get_service_factory
        >>> factory = get_service_factory()
        >>> rag = factory.create_rag_pipeline()
    """
    global _default_factory
    if _default_factory is None:
        _default_factory = ServiceFactory()
    return _default_factory


def create_test_factory(**overrides) -> ServiceFactory:
    """
    Create a factory for testing with optional overrides.

    Example:
        >>> # Create factory with in-memory vector store for fast tests
        >>> factory = create_test_factory(use_in_memory_store=True)

        >>> # Create factory with mock LLM
        >>> mock_llm = Mock(spec=LLMProvider)
        >>> factory = create_test_factory(llm_provider=mock_llm)
    """
    return ServiceFactory(**overrides)
