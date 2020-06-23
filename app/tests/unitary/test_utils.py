import pytest

from app.utils import generate_password_reset_token, verify_password_reset_token


pytestmark = pytest.mark.unitary


def test_generate_password_reset_token():
    """It should return a valid token (bytes)"""
    email = 'avalidemail@domain.com'
    token = generate_password_reset_token(email)
    assert isinstance(token, bytes)


@pytest.mark.depends(on=['test_generate_password_reset_token'])
def test_verify_password_reset_token():
    """It should return the email if the token is valid"""
    email = 'avalidemail@domain.com'
    token = generate_password_reset_token(email)
    result = verify_password_reset_token(token)
    assert result == email


def test_verify_password_reset_token_invalid():
    """It should return None if the token is invalid"""
    token = b"wrong"
    result = verify_password_reset_token(token)
    assert result is None
