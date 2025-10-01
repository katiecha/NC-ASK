"""
Crisis detection service for identifying urgent mental health concerns
"""
from typing import List, Dict, Any, Tuple
import logging
import re

logger = logging.getLogger(__name__)


class CrisisDetector:
    """Service for detecting crisis situations in user queries"""

    # Crisis keywords organized by severity
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

    @classmethod
    def detect_crisis(cls, query: str) -> Tuple[bool, str, List[str]]:
        """
        Detect if a query contains crisis indicators

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
        for keyword in cls.CRITICAL_KEYWORDS:
            if keyword in query_lower:
                matched_keywords.append(keyword)

        if matched_keywords:
            logger.warning(f"CRITICAL crisis detected. Keywords: {matched_keywords}")
            return True, "critical", matched_keywords

        # Check high priority keywords
        for keyword in cls.HIGH_PRIORITY_KEYWORDS:
            if keyword in query_lower:
                matched_keywords.append(keyword)

        if matched_keywords:
            logger.warning(f"HIGH priority crisis detected. Keywords: {matched_keywords}")
            return True, "high", matched_keywords

        # Check moderate keywords
        for keyword in cls.MODERATE_KEYWORDS:
            if keyword in query_lower:
                matched_keywords.append(keyword)

        if matched_keywords:
            logger.info(f"MODERATE distress detected. Keywords: {matched_keywords}")
            return True, "moderate", matched_keywords

        return False, "none", []

    @staticmethod
    def get_crisis_resources() -> List[Dict[str, Any]]:
        """
        Get list of crisis resources

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

    @staticmethod
    def format_crisis_response(
        severity: str,
        standard_response: str = None
    ) -> str:
        """
        Format a crisis response message

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
