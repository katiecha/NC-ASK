import pytest

from services.config import Settings


@pytest.mark.parametrize(
    "input_val,expected",
    [
        ('["http://a","http://b"]', ["http://a", "http://b"]),
        ('http://a,http://b', ["http://a", "http://b"]),
        (None, None),
    ],
)
def test_allowed_origins_parsing(input_val, expected):
    s = Settings(ALLOWED_ORIGINS=input_val)
    result = s.allowed_origins
    assert isinstance(result, list)
    if expected is not None:
        assert result == expected
    else:
        # default should include known localhosts
        assert "http://localhost:5173" in result
