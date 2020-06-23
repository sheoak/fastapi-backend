from typing import Dict

import pytest
from pydantic import ValidationError

import app.tests.data.samples as samples
from app.schemas.user import UserCreate, UserUpdate


pytestmark = pytest.mark.unitary


@pytest.mark.parametrize("email", samples.invalid_emails)
def test_create_invalid_email(
    email: str,
    base_user: Dict,
) -> None:
    """It should not be possible to register with an invalid email"""
    with pytest.raises(ValidationError):
        base_user["email"] = email
        UserCreate(**base_user)


# TODO: fix non-passing values
@pytest.mark.parametrize("email", samples.valid_emails)
def test_create_valid_email(
    email: Dict,
    base_user: Dict,
) -> None:
    """It should  be possible to register with a valid email"""
    base_user["email"] = email
    user = UserCreate(**base_user)
    assert user.email == email


def test_update_password(
    base_user: Dict
) -> None:
    """It should be possible to use the update schema"""
    user = UserUpdate(**base_user)
    assert user.email == base_user["email"]


@pytest.mark.usefixtures('enable_pwned_password')
@pytest.mark.parametrize("password", samples.corrupted_passwords)
def test_create_user_pwned_password(
    password: Dict,
    base_user: Dict,
) -> None:
    """It should not be possible to use a pwned password"""
    with pytest.raises(ValueError):
        base_user["password"] = password
        UserCreate(**base_user)


@pytest.mark.parametrize("password", samples.valid_passwords)
def test_create_user_valid_password(
    password: Dict,
    base_user: Dict,
) -> None:
    """It should be possible to create an account with valid passwords"""
    base_user["password"] = password

    user = UserCreate(**base_user)

    assert user.email == base_user["email"]
    assert user.password == password


@pytest.mark.parametrize("password", samples.invalid_passwords)
def test_create_user_invalid_password(
    password: Dict,
    base_user: Dict,
) -> None:
    """It should not be possible to use an invalid password"""
    with pytest.raises(ValueError):
        base_user["password"] = password
        UserCreate(**base_user)
