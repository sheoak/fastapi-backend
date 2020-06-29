"""
Users endpoint: /users/*

TODO: refactor errors (code repetition)
TODO: add pagination in headers
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy_mixins import ModelNotFoundError

from app.db.base_class import ModelExistError
from app.api.utils.security import get_current_active_superuser
from app.core import config
from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate, UserUpdateFull, UserCreateFull
from app.utils import send_new_account_email


router = APIRouter()


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _create_account(user_in: UserCreate, open_registration: bool = False):
    """Generic user creation helper"""
    try:
        user = UserModel.create(user_in)
    except ModelExistError:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    if config.EMAILS_ENABLED and user_in.email:

        # if not password was given, we send a magiclink by email
        if not user_in.password:
            token = UserModel.generate_password(email=user_in.email)
        else:
            token = None

        send_new_account_email(
            email_to=user_in.email,
            username=user_in.email,
            token=token,
            open_registration=open_registration
        )
    return user


def _get_account_or_error(user_id: int):
    """Return the account or generate an error"""
    try:
        user = UserModel.find_or_fail(user_id)
    except ModelNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this username does not exist in the system",
        )
    return user


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@router.get("/", response_model=List[User])
def read_users(
    *,
    page: int = 0,
    limit: int = 20,
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """Retrieve users."""
    users = UserModel.all_by_page(page=page, limit=limit)
    return users


# TODO: handle password set or not
@router.post("/", response_model=User)
def create_user(
    *,
    user_in: UserCreateFull,
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """Create new user."""
    return _create_account(user_in)


# TODO: handle password set or not
@router.post("/open", response_model=User)
def create_user_open(
    *,
    user_in: UserCreate,
):
    """Create new user without the need to be logged in."""
    if not config.USERS_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Open user registration is forbidden on this server",
        )
    return _create_account(user_in, open_registration=True)


@router.get("/{user_id}", response_model=User)
def read_user_by_id(
    *,
    user_id: int,
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """Get a specific user by id."""
    return _get_account_or_error(user_id)


@router.put("/{user_id}", response_model=User)
def update_user(
    *,
    user_id: int,
    user_in: UserUpdateFull,
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """Update a user"""
    user = _get_account_or_error(user_id)
    return user.update(user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    *,
    user_id: int,
    current_user: UserModel = Depends(get_current_active_superuser),
):
    user = _get_account_or_error(user_id)
    user.delete()
    return
