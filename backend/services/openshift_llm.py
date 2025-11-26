"""
LLM service using OpenAI-compatible API (for OpenShift-deployed models).

This implementation uses the OpenAI SDK to connect to models deployed on
RedHat OpenShift. It can be used with any OpenAI-compatible API endpoint
(open source models like Llama, Mistral, etc. served via vLLM, TGI, etc.).
"""
import logging
from typing import Literal

from openai import OpenAI

from config.examples import format_examples_for_prompt, get_examples
from config.prompts import get_system_prompt
from services.config import settings

logger = logging.getLogger(__name__)


class OpenShiftLLM:
    """
    LLM service using OpenAI-compatible API for OpenShift-deployed models.

    Implements the LLMProvider interface for dependency injection.
    Compatible with any OpenAI-compatible API endpoint.

    Features:
    - Lazy loading: Client configured on first use
    - Configurable temperature and model name
    - Custom base URL for OpenShift endpoints
    - Automatic fallback on errors
    - Plain language optimization (8th grade reading level)
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model_name: str | None = None,
        temperature: float | None = None
    ):
        """
        Initialize OpenShift LLM service.

        Args:
            api_key: Optional API key override. If None, uses settings.OPENSHIFT_API_KEY
            base_url: Optional base URL override. If None, uses settings.OPENSHIFT_BASE_URL
                     Should NOT include /v1 suffix - will be added automatically by OpenAI SDK
            model_name: Optional model name override. If None, uses settings.LLM_MODEL
            temperature: Optional default temperature. If None, uses settings.LLM_TEMPERATURE
        """
        self.api_key = api_key or settings.OPENSHIFT_API_KEY
        raw_base_url = base_url or settings.OPENSHIFT_BASE_URL

        # Ensure /v1 suffix is present (OpenAI SDK requires it for custom base_url)
        base = raw_base_url.rstrip('/')
        if not base.endswith('/v1'):
            base = f"{base}/v1"
        self.base_url = base
        self.model_name = model_name or settings.LLM_MODEL
        self.default_temperature = temperature or settings.LLM_TEMPERATURE
        self._client: OpenAI | None = None
        logger.info(f"Initialized OpenShiftLLM with model: {self.model_name}, base_url: {self.base_url}")

    @property
    def client(self) -> OpenAI:
        """
        Get or initialize OpenAI client (lazy loading).

        Returns:
            Configured OpenAI client
        """
        if self._client is None:
            try:
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                logger.info(f"OpenAI client initialized for OpenShift endpoint: {self.base_url}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                raise
        return self._client

    def generate_response(
        self,
        query: str,
        context: str,
        temperature: float | None = None,
        view_type: Literal["provider", "patient"] = "patient"
    ) -> str:
        """
        Generate a response using OpenShift-deployed LLM.

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

            # Generate response using OpenAI API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temp,
                max_tokens=1024,
            )

            response_text = response.choices[0].message.content.strip()
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
