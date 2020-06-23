import pytest  # noqa
from typing import Dict

from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User as UserModel

from sqlalchemy.orm import Session

pytestmark = pytest.mark.functional


# ----------------------------------------------------------------------------
# Test failsafe
# This is to make sure the database is rollback to avoid debugging nightmare
# ---------------------------------------------------------------------------

def test_rb_a(db: Session, users):
    user = UserModel.find(users[0]["id"])
    assert user.email == users[0]["email"]


def test_rb_b(db: Session, users):
    user = UserModel.find(users[0]["id"])
    user_in = UserUpdate(email="modify@domain.com")
    user.update(user_in)


@pytest.mark.usefixtures("db")
def test_create_user(base_user: Dict):
    user_in = UserCreate(**base_user)
    user = UserModel.create(user_in)
    assert user.email == base_user["email"]
    assert hasattr(user, "hashed_password")
    assert user.hashed_password


@pytest.mark.usefixtures("db")
def test_authenticate_user(normal_users: Dict):
    user = UserModel.get(email=normal_users[0]["email"])
    credentials = {
        "email": normal_users[0]["email"],
        "password": normal_users[0]["password"],
    }
    user = user.authenticate(**credentials)
    assert user
    assert user.email == normal_users[0]["email"]


@pytest.mark.usefixtures("db")
def test_not_authenticate_user(base_user: Dict):
    user = UserModel.authenticate(**base_user)
    assert user is None


@pytest.mark.usefixtures("db")
def test_check_if_user_is_active(normal_users: Dict):
    user = UserModel.get(email=normal_users[0]["email"])
    assert user.is_active


@pytest.mark.usefixtures("db")
def test_check_if_user_is_inactive(inactive_users: Dict):
    user = UserModel.get(email=inactive_users[0]["email"])
    assert not user.is_active


@pytest.mark.usefixtures("db")
def test_check_if_user_is_superuser(super_users: Dict):
    user = UserModel.get(email=super_users[0]["email"])
    assert user.is_superuser


@pytest.mark.usefixtures("db")
def test_check_if_user_is_not_superuser(normal_users: Dict):
    user = UserModel.get(email=normal_users[0]["email"])
    assert not user.is_superuser


@pytest.mark.usefixtures("db")
def test_get_user(users: Dict):
    user = UserModel.get(email=users[0]["email"])
    assert user, "User not found"
    assert user.email == users[0]["email"], "User email do not match"


@pytest.mark.usefixtures("db")
def test_find_user(users: Dict):
    user = UserModel.find(users[0]["id"])
    assert user, "User not found"
    assert user.email == users[0]["email"], "User email do not match"
