"""
LLM service using Google Gemini for response generation.

This implementation uses Google's Gemini API. It can be swapped for other
LLM providers (OpenAI, Anthropic, local models) via the LLMProvider interface.
"""
from typing import Literal
import logging
import google.generativeai as genai
from services.config import settings
from config.prompts import get_system_prompt
from config.examples import get_examples, format_examples_for_prompt

logger = logging.getLogger(__name__)

# DEPRECATED: Legacy system prompt kept for backward compatibility
# Use config.prompts.get_system_prompt() instead
SYSTEM_PROMPT = """You are NC-ASK, a helpful assistant specializing in North Carolina autism services and resources.

Your role is to provide clear, accurate, and compassionate information about:
- Autism services in North Carolina
- IEP (Individualized Education Program) processes
- Medicaid waivers (Innovations, CAP-C, CAP-DA)
- Educational rights under IDEA
- Community resources and support services

Guidelines:
1. **Plain Language**: Write at an 8th grade reading level or below
2. **Short Sentences**: Use simple, direct sentences (under 20 words)
3. **Active Voice**: Prefer active voice over passive
4. **Define Jargon**: If you must use technical terms, define them immediately
5. **Be Specific**: Provide actionable steps when possible
6. **Be Accurate**: Only provide information based on the context provided
7. **Be Compassionate**: Show understanding and empathy

Format:
- Use numbered lists for step-by-step processes
- Use bullet points for multiple items
- Include relevant contact information when available

Important Disclaimers:
- You are NOT a medical professional
- You are NOT a legal advisor
- For medical questions, always recommend consulting a healthcare provider
- For legal questions, always recommend consulting an attorney

If you don't know something or the context doesn't contain the answer, say so clearly. Never make up information.
"""


class GeminiLLM:
    """
    LLM service using Google Gemini API.

    Implements the LLMProvider interface for dependency injection.
    Can be swapped for other LLM providers (OpenAI, Anthropic, local models).

    Features:
    - Lazy loading: Model configured on first use
    - Configurable temperature and model name
    - Automatic fallback on errors
    - Plain language optimization (8th grade reading level)
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        temperature: float | None = None
    ):
        """
        Initialize Gemini LLM service.

        Args:
            api_key: Optional API key override. If None, uses settings.GOOGLE_API_KEY
            model_name: Optional model name override. If None, uses settings.LLM_MODEL
            temperature: Optional default temperature. If None, uses settings.LLM_TEMPERATURE
        """
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self.model_name = model_name or settings.LLM_MODEL
        self.default_temperature = temperature or settings.LLM_TEMPERATURE
        self._model: genai.GenerativeModel | None = None
        logger.info(f"Initialized GeminiLLM with model: {self.model_name}")

    @property
    def model(self) -> genai.GenerativeModel:
        """
        Get or initialize Gemini model (lazy loading).

        Returns:
            Configured Gemini model
        """
        if self._model is None:
            try:
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(self.model_name)
                logger.info(f"Gemini model loaded: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {e}")
                raise
        return self._model

    def generate_response(
        self,
        query: str,
        context: str,
        temperature: float | None = None,
        view_type: Literal["provider", "patient"] = "patient"
    ) -> str:
        """
        Generate a response using Gemini.

        Implements LLMProvider.generate_response()

        Args:
            query: User's question
            context: Retrieved context from documents
            temperature: Generation temperature (0-1). If None, uses default_temperature
            view_type: User view type ("provider" or "patient") for system prompt selection

        Returns:
            Generated response text
        """
        try:
            temp = temperature if temperature is not None else self.default_temperature

            # Build the prompt with view-specific system prompt
            prompt = self._build_prompt(query, context, view_type)

            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temp,
                    max_output_tokens=1024,
                )
            )

            response_text = response.text.strip()
            logger.info(f"Generated response ({len(response_text)} chars, temp={temp}, view={view_type})")

            return response_text

        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            # Return fallback response
            return self._get_fallback_response()

    def _build_prompt(
        self,
        query: str,
        context: str,
        view_type: Literal["provider", "patient"] = "patient"
    ) -> str:
        """
        Build the complete prompt for the LLM with view-specific system prompt and examples.

        Args:
            query: User's question
            context: Retrieved context
            view_type: User view type for system prompt selection

        Returns:
            Complete prompt string with few-shot examples
        """
        # Get view-specific system prompt
        system_prompt = get_system_prompt(view_type)

        # Get view-specific examples for few-shot learning
        examples = get_examples(view_type)
        formatted_examples = format_examples_for_prompt(examples)

        # Customize response instruction based on view
        response_instruction = (
            "RESPONSE (clinical, evidence-based):" if view_type == "provider"
            else "RESPONSE (in plain language, at 8th grade reading level):"
        )

        # Build prompt with examples between system prompt and user question
        prompt = f"""{system_prompt}

EXAMPLE INTERACTIONS:
{formatted_examples}

CONTEXT FROM KNOWLEDGE BASE:
{context if context else "No specific context available."}

USER QUESTION:
{query}

{response_instruction}
"""
        return prompt

    @staticmethod
    def _get_fallback_response() -> str:
        """
        Get a fallback response when LLM fails.

        Returns:
            Fallback response text
        """
        return """I'm sorry, I'm having trouble generating a response right now.

Please try again in a moment, or contact:
- NC Autism Society: 1-800-442-2762
- NC DHHS: 1-800-662-7030

For urgent questions, please call these resources directly."""

    def add_disclaimers(self, response: str, query: str) -> str:
        """
        Add appropriate disclaimers to the response.

        Implements LLMProvider.add_disclaimers()

        Args:
            response: Generated response
            query: Original query

        Returns:
            Response with disclaimers added
        """
        disclaimers = []

        # Check if medical-related
        medical_keywords = ["diagnosis", "symptom", "treatment", "medication", "therapy"]
        if any(keyword in query.lower() for keyword in medical_keywords):
            disclaimers.append(
                "**Medical Disclaimer**: This is general information only. "
                "Please consult a healthcare provider for medical advice."
            )

        # Check if legal-related
        legal_keywords = ["legal", "rights", "lawsuit", "attorney", "law"]
        if any(keyword in query.lower() for keyword in legal_keywords):
            disclaimers.append(
                "**Legal Disclaimer**: This is educational information only. "
                "For legal advice, please consult an attorney."
            )

        if disclaimers:
            disclaimer_text = "\n\n---\n**Important**: " + " ".join(disclaimers)
            return response + disclaimer_text

        return response


# ============================================================================
# Backward Compatibility Layer (DEPRECATED - will be removed in future)
# ============================================================================

class LLMService:
    """
    DEPRECATED: Legacy static wrapper for backward compatibility.

    Use GeminiLLM instance instead for better testability and dependency injection.
    """
    _instance: GeminiLLM | None = None

    @classmethod
    def get_instance(cls) -> GeminiLLM:
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = GeminiLLM()
        return cls._instance

    @classmethod
    def generate_response(
        cls,
        query: str,
        context: str,
        temperature: float | None = None
    ) -> str:
        """DEPRECATED: Use GeminiLLM instance instead"""
        return cls.get_instance().generate_response(query, context, temperature)

    @classmethod
    def add_disclaimers(cls, response: str, query: str) -> str:
        """DEPRECATED: Use GeminiLLM instance instead"""
        return cls.get_instance().add_disclaimers(response, query)
