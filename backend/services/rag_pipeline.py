"""
Complete RAG (Retrieval-Augmented Generation) pipeline with dependency injection.

This is the main orchestrator that combines all services to answer user queries.
"""
import logging
from typing import Any, Literal

from services.interfaces import CrisisDetector as CrisisDetectorProtocol
from services.interfaces import LLMProvider
from services.interfaces import RetrievalService as RetrievalServiceProtocol

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Main RAG pipeline orchestrator with dependency injection.

    This class coordinates the entire query processing flow:
    1. Validation & sanitization
    2. Crisis detection
    3. Document retrieval
    4. LLM response generation
    5. Disclaimer addition
    6. Citation extraction

    Example:
        >>> from services.service_factory import get_service_factory
        >>> factory = get_service_factory()
        >>> pipeline = factory.create_rag_pipeline()
        >>> result = await pipeline.process_query("What is an IEP?")
        >>> print(result["response"])
    """

    def __init__(
        self,
        retrieval_service: RetrievalServiceProtocol,
        llm_provider: LLMProvider,
        crisis_detector: CrisisDetectorProtocol
    ):
        """
        Initialize RAG pipeline with dependencies.

        Args:
            retrieval_service: Service for retrieving relevant documents
            llm_provider: LLM service for generating responses
            crisis_detector: Service for detecting crisis situations
        """
        self.retrieval_service = retrieval_service
        self.llm_provider = llm_provider
        self.crisis_detector = crisis_detector

        logger.info(
            f"Initialized RAGPipeline with "
            f"retrieval={type(retrieval_service).__name__}, "
            f"llm={type(llm_provider).__name__}, "
            f"crisis_detector={type(crisis_detector).__name__}"
        )

    @staticmethod
    def validate_query(query: str, max_length: int = 500) -> tuple[bool, str]:
        """
        Validate user query

        Args:
            query: User query text
            max_length: Maximum allowed length

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not query or not query.strip():
            return False, "Query cannot be empty"

        if len(query) > max_length:
            return False, f"Query exceeds maximum length of {max_length} characters"

        return True, ""

    @staticmethod
    def sanitize_query(query: str) -> str:
        """
        Sanitize user input

        Args:
            query: Raw user query

        Returns:
            Sanitized query
        """
        # Remove excessive whitespace
        query = " ".join(query.split())

        # Remove potentially harmful characters (basic sanitization)
        dangerous_chars = ["<", ">", "{", "}"]
        for char in dangerous_chars:
            query = query.replace(char, "")

        return query.strip()

    async def process_query(
        self,
        query: str,
        session_id: str | None = None,
        view_type: Literal["provider", "patient"] = "patient"
    ) -> dict[str, Any]:
        """
        Process a user query through the complete RAG pipeline.

        This is the main method that orchestrates all services.

        Args:
            query: User's question
            session_id: Optional session identifier for logging
            view_type: User view type ("provider" or "patient") for response tailoring

        Returns:
            Dictionary containing:
                - response: str - Generated answer
                - citations: List[Dict] - Source citations
                - crisis_detected: bool - Whether crisis was detected
                - crisis_severity: Optional[str] - Severity level if crisis
                - crisis_resources: List[Dict] - Crisis resources if applicable
                - error: bool - Whether an error occurred
        """
        try:
            # Step 1: Validate query
            is_valid, error_msg = self.validate_query(query)
            if not is_valid:
                return {
                    "response": error_msg,
                    "citations": [],
                    "crisis_detected": False,
                    "error": True
                }

            # Step 2: Sanitize query
            sanitized_query = self.sanitize_query(query)
            logger.info(f"Processing query (session: {session_id}, view: {view_type})")

            # Step 3: Crisis detection (using injected detector)
            is_crisis, severity, crisis_keywords = self.crisis_detector.detect_crisis(
                sanitized_query
            )

            # Step 4: Retrieve relevant documents (using injected retrieval service)
            retrieval_results = self.retrieval_service.retrieve_similar_chunks(
                sanitized_query
            )

            # Step 5: Format context for LLM (using injected retrieval service)
            context = self.retrieval_service.format_context_for_llm(retrieval_results)

            # Step 6: Generate response (using injected LLM provider with view-specific prompt)
            response = self.llm_provider.generate_response(
                query=sanitized_query,
                context=context,
                view_type=view_type
            )

            # Step 7: Add disclaimers (using injected LLM provider)
            response = self.llm_provider.add_disclaimers(response, sanitized_query)

            # Step 8: If crisis detected, prepend crisis resources (using injected detector)
            if is_crisis:
                crisis_message = self.crisis_detector.format_crisis_response(
                    severity=severity,
                    standard_response=response
                )
                response = crisis_message

            # Step 9: Extract citations (using injected retrieval service)
            citations = self.retrieval_service.extract_citations(retrieval_results)

            # Log completion (de-identified)
            logger.info(
                f"Query processed successfully. "
                f"Retrieved: {len(retrieval_results)} chunks, "
                f"Crisis: {is_crisis}, "
                f"Severity: {severity}"
            )

            return {
                "response": response,
                "citations": citations,
                "crisis_detected": is_crisis,
                "crisis_severity": severity if is_crisis else None,
                "crisis_resources": self.crisis_detector.get_crisis_resources() if is_crisis else [],
                "error": False
            }

        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}", exc_info=True)
            return {
                "response": "I apologize, but I encountered an error processing your question. "
                           "Please try again or contact NC Ask directly at 1-800-442-2762.",
                "citations": [],
                "crisis_detected": False,
                "error": True,
                "error_message": str(e)
            }
