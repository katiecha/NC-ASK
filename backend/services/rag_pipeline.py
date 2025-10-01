"""
Complete RAG (Retrieval-Augmented Generation) pipeline
"""
from typing import Dict, Any, List
import logging
from services.retrieval import RetrievalService
from services.llm_service import LLMService
from services.crisis_detection import CrisisDetector

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Main RAG pipeline orchestrator"""

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

    @classmethod
    async def process_query(
        cls,
        query: str,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the complete RAG pipeline

        Args:
            query: User's question
            session_id: Optional session identifier

        Returns:
            Dictionary containing response, citations, and metadata
        """
        try:
            # Step 1: Validate query
            is_valid, error_msg = cls.validate_query(query)
            if not is_valid:
                return {
                    "response": error_msg,
                    "citations": [],
                    "crisis_detected": False,
                    "error": True
                }

            # Step 2: Sanitize query
            sanitized_query = cls.sanitize_query(query)
            logger.info(f"Processing query (session: {session_id})")

            # Step 3: Crisis detection
            is_crisis, severity, crisis_keywords = CrisisDetector.detect_crisis(
                sanitized_query
            )

            # Step 4: Retrieve relevant documents
            retrieval_results = RetrievalService.retrieve_similar_chunks(
                sanitized_query
            )

            # Step 5: Format context for LLM
            context = RetrievalService.format_context_for_llm(retrieval_results)

            # Step 6: Generate response
            response = LLMService.generate_response(
                query=sanitized_query,
                context=context
            )

            # Step 7: Add disclaimers
            response = LLMService.add_disclaimers(response, sanitized_query)

            # Step 8: If crisis detected, prepend crisis resources
            if is_crisis:
                crisis_message = CrisisDetector.format_crisis_response(
                    severity=severity,
                    standard_response=response
                )
                response = crisis_message

            # Step 9: Extract citations
            citations = RetrievalService.extract_citations(retrieval_results)

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
                "crisis_resources": CrisisDetector.get_crisis_resources() if is_crisis else [],
                "error": False
            }

        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}", exc_info=True)
            return {
                "response": "I apologize, but I encountered an error processing your question. "
                           "Please try again or contact NC Autism resources directly at 1-800-442-2762.",
                "citations": [],
                "crisis_detected": False,
                "error": True,
                "error_message": str(e)
            }
