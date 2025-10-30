"""
Crisis detection service for identifying urgent mental health concerns.

This implementation uses keyword-based detection. It can be swapped for
ML-based or hybrid approaches via the CrisisDetector interface.
"""
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

# Crisis keywords organized by severity (shared across implementations)
CRITICAL_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end my life", "want to die",
    "going to die", "better off dead", "no reason to live",
    "plan to hurt myself", "plan to kill"
]

HIGH_PRIORITY_KEYWORDS = [
    "self harm", "self-harm", "cut myself", "hurt myself",
    "overdose", "pills", "harm to others", "hurt someone",
    "abuse", "neglect", "violence"
]

MODERATE_KEYWORDS = [
    "hopeless", "can't go on", "unbearable", "desperate",
    "crisis", "emergency", "help me please"
]


class KeywordCrisisDetector:
    """
    Crisis detection using keyword matching.

    Implements the CrisisDetector interface for dependency injection.
    Can be swapped for ML-based detectors or hybrid approaches.

    Features:
    - Three-tier severity classification (critical, high, moderate)
    - Comprehensive NC crisis resources
    - De-identified logging for monitoring
    """

    def __init__(
        self,
        critical_keywords: List[str] | None = None,
        high_priority_keywords: List[str] | None = None,
        moderate_keywords: List[str] | None = None
    ):
        """
        Initialize crisis detector with custom keywords.

        Args:
            critical_keywords: Optional override for critical keywords
            high_priority_keywords: Optional override for high priority keywords
            moderate_keywords: Optional override for moderate keywords
        """
        self.critical_keywords = critical_keywords or CRITICAL_KEYWORDS
        self.high_priority_keywords = high_priority_keywords or HIGH_PRIORITY_KEYWORDS
        self.moderate_keywords = moderate_keywords or MODERATE_KEYWORDS
        logger.info("Initialized KeywordCrisisDetector")

    def detect_crisis(self, query: str) -> Tuple[bool, str, List[str]]:
        """
        Detect if a query contains crisis indicators.

        Implements CrisisDetector.detect_crisis()

        Args:
            query: User query text

        Returns:
            Tuple of (is_crisis, severity_level, matched_keywords)
            - is_crisis: Boolean indicating if crisis was detected
            - severity_level: "critical", "high", "moderate", or "none"
            - matched_keywords: List of matched crisis keywords
        """
        query_lower = query.lower()
        matched_keywords = []

        # Check critical keywords
        for keyword in self.critical_keywords:
            if keyword in query_lower:
                matched_keywords.append(keyword)

        if matched_keywords:
            logger.warning(f"CRITICAL crisis detected. Keywords: {matched_keywords}")
            return True, "critical", matched_keywords

        # Check high priority keywords
        for keyword in self.high_priority_keywords:
            if keyword in query_lower:
                matched_keywords.append(keyword)

        if matched_keywords:
            logger.warning(f"HIGH priority crisis detected. Keywords: {matched_keywords}")
            return True, "high", matched_keywords

        # Check moderate keywords
        for keyword in self.moderate_keywords:
            if keyword in query_lower:
                matched_keywords.append(keyword)

        if matched_keywords:
            logger.info(f"MODERATE distress detected. Keywords: {matched_keywords}")
            return True, "moderate", matched_keywords

        return False, "none", []

    def get_crisis_resources(self) -> List[Dict[str, Any]]:
        """
        Get list of crisis resources.

        Implements CrisisDetector.get_crisis_resources()

        Returns:
            List of crisis resource dictionaries
        """
        return [
            {
                "name": "988 Suicide & Crisis Lifeline",
                "phone": "988",
                "description": "24/7 free and confidential support for people in distress",
                "url": "https://988lifeline.org/",
                "priority": 1
            },
            {
                "name": "Crisis Text Line",
                "phone": "Text HOME to 741741",
                "description": "24/7 text-based crisis support",
                "url": "https://www.crisistextline.org/",
                "priority": 2
            },
            {
                "name": "NC Hope4NC Helpline",
                "phone": "1-855-587-3463",
                "description": "North Carolina's free 24/7 crisis and emotional support line",
                "url": "https://www.mhanc.org/hope4nc/",
                "priority": 3
            },
            {
                "name": "Emergency Services",
                "phone": "911",
                "description": "For immediate life-threatening emergencies",
                "url": None,
                "priority": 4
            }
        ]

    def format_crisis_response(
        self,
        severity: str,
        standard_response: str | None = None
    ) -> str:
        """
        Format a crisis response message.

        Implements CrisisDetector.format_crisis_response()

        Args:
            severity: Crisis severity level
            standard_response: Optional standard response to append

        Returns:
            Formatted crisis response text
        """
        crisis_message = """
⚠️ **IMPORTANT CRISIS RESOURCES** ⚠️

If you or someone you know is in crisis or considering self-harm, please reach out for immediate help:

• **988 Suicide & Crisis Lifeline**: Call or text 988 (available 24/7)
• **Crisis Text Line**: Text HOME to 741741
• **NC Hope4NC Helpline**: 1-855-587-3463 (24/7 support)
• **Emergency**: Call 911 for immediate life-threatening situations

You are not alone. Trained counselors are available right now to help.

---
"""

        if standard_response:
            crisis_message += f"\n{standard_response}"

        return crisis_message


# ============================================================================
# Backward Compatibility Layer (DEPRECATED - will be removed in future)
# ============================================================================

class CrisisDetector:
    """
    DEPRECATED: Legacy static wrapper for backward compatibility.

    Use KeywordCrisisDetector instance instead for better testability
    and dependency injection.
    """
    _instance: KeywordCrisisDetector | None = None

    @classmethod
    def get_instance(cls) -> KeywordCrisisDetector:
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = KeywordCrisisDetector()
        return cls._instance

    @classmethod
    def detect_crisis(cls, query: str) -> Tuple[bool, str, List[str]]:
        """DEPRECATED: Use KeywordCrisisDetector instance instead"""
        return cls.get_instance().detect_crisis(query)

    @classmethod
    def get_crisis_resources(cls) -> List[Dict[str, Any]]:
        """DEPRECATED: Use KeywordCrisisDetector instance instead"""
        return cls.get_instance().get_crisis_resources()

    @classmethod
    def format_crisis_response(
        cls,
        severity: str,
        standard_response: str | None = None
    ) -> str:
        """DEPRECATED: Use KeywordCrisisDetector instance instead"""
        return cls.get_instance().format_crisis_response(severity, standard_response)
