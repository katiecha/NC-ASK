"""
LLM service using Google Gemini for response generation
"""
from typing import Dict, Any, Optional
import logging
import google.generativeai as genai
from services.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for generating responses using Google Gemini"""

    _model = None

    # System prompt for plain language responses
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

    @classmethod
    def get_model(cls):
        """Initialize and return Gemini model"""
        if cls._model is None:
            try:
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                cls._model = genai.GenerativeModel(settings.LLM_MODEL)
                logger.info(f"Initialized Gemini model: {settings.LLM_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini model: {e}")
                raise
        return cls._model

    @classmethod
    def generate_response(
        cls,
        query: str,
        context: str,
        temperature: float = None
    ) -> str:
        """
        Generate a response using Gemini

        Args:
            query: User's question
            context: Retrieved context from documents
            temperature: Generation temperature (0-1)

        Returns:
            Generated response text
        """
        try:
            model = cls.get_model()
            temperature = temperature or settings.LLM_TEMPERATURE

            # Build the prompt
            prompt = cls._build_prompt(query, context)

            # Generate response
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=1024,
                )
            )

            response_text = response.text.strip()
            logger.info(f"Generated response ({len(response_text)} chars)")

            return response_text

        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            # Return fallback response
            return cls._get_fallback_response()

    @classmethod
    def _build_prompt(cls, query: str, context: str) -> str:
        """
        Build the complete prompt for the LLM

        Args:
            query: User's question
            context: Retrieved context

        Returns:
            Complete prompt string
        """
        prompt = f"""{cls.SYSTEM_PROMPT}

CONTEXT FROM KNOWLEDGE BASE:
{context if context else "No specific context available."}

USER QUESTION:
{query}

RESPONSE (in plain language, at 8th grade reading level):
"""
        return prompt

    @staticmethod
    def _get_fallback_response() -> str:
        """
        Get a fallback response when LLM fails

        Returns:
            Fallback response text
        """
        return """I'm sorry, I'm having trouble generating a response right now.

Please try again in a moment, or contact:
- NC Autism Society: 1-800-442-2762
- NC DHHS: 1-800-662-7030

For urgent questions, please call these resources directly."""

    @classmethod
    def add_disclaimers(cls, response: str, query: str) -> str:
        """
        Add appropriate disclaimers to the response

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

    @classmethod
    def simplify_language(cls, text: str) -> str:
        """
        Apply additional language simplification if needed

        Args:
            text: Input text

        Returns:
            Simplified text
        """
        # This is a placeholder for future language simplification
        # Could integrate with readability checkers or simplification models
        return text
