import pytest

from app.api.utils.security import create_token


pytestmark = pytest.mark.unitary


def test_create_token(user) -> None:
    """Verify the token generation"""
    r = create_token(user["id"])
    assert r
    assert isinstance(r, bytes)
    assert len(r) == 141
