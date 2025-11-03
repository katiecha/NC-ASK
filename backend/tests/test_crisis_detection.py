from typing import List, Tuple

import pytest

from services.crisis_detection import KeywordCrisisDetector, CrisisDetector


@pytest.mark.parametrize(
    "query,expected",
    [
        ("I am feeling suicidal and want to end my life", "critical"),
        ("I'm thinking about taking pills and overdosing", "high"),
        ("I feel hopeless and it's unbearable right now, help me please", "moderate"),
        ("What are resources for autism support?", "none"),
    ],
)
def test_detect_various_severities(query: str, expected: str):
    detector = KeywordCrisisDetector()
    is_crisis, severity, matches = detector.detect_crisis(query)

    if expected == "none":
        assert is_crisis is False
        assert severity == "none"
        assert matches == []
    else:
        assert is_crisis is True
        assert severity == expected
        assert len(matches) > 0


def test_get_crisis_resources_and_format():
    detector = KeywordCrisisDetector()
    resources = detector.get_crisis_resources()

    assert isinstance(resources, list)
    assert any(r.get("phone") for r in resources)

    # Test formatting includes the standard_response when provided
    text = detector.format_crisis_response("critical", standard_response="Please seek help immediately.")
    assert "Please seek help immediately." in text


@pytest.mark.parametrize(
    "query",
    [
        ("I'm suicidal"),
        ("I might hurt myself"),
    ],
)
def test_deprecated_wrapper_equivalence(query: str):
    # Ensure the deprecated class wrapper returns same results as instance
    is_crisis_a, severity_a, matches_a = KeywordCrisisDetector().detect_crisis(query)
    is_crisis_b, severity_b, matches_b = CrisisDetector.detect_crisis(query)

    assert is_crisis_a == is_crisis_b
    assert severity_a == severity_b
    assert matches_a == matches_b
