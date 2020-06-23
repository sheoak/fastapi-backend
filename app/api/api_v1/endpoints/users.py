"""
Users endpoint: /users/*

TODO: try to add some response_model_exclude_unset=True
Response Model: https://fastapi.tiangolo.com/tutorial/response-model/
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy_mixins import ModelNotFoundError

from app.db.base_class import ModelExistError
from app.api.utils.security import get_current_active_superuser, get_current_active_user
from app.core import config
from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate, UserUpdate
from app.utils import send_new_account_email


router = APIRouter()


@router.get("/", response_model=List[User])
def read_users(
    *,
    page: int = 0,
    limit: int = 20,
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """Retrieve users."""
    # TODO: pagination in headers
    users = UserModel.all_by_page(page=page, limit=limit)
    return users


@router.post("/", response_model=User)
def create_user(
    *,
    user_in: UserCreate,
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """Create new user."""
    try:
        user = UserModel.create(user_in)
    except ModelExistError:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    if config.EMAILS_ENABLED and user_in.email:
        send_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
    return user


@router.put("/me", response_model=User)
def update_user_me(
    *,
    user_in: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user),
):
    """Update myself"""
    user = UserModel.find(current_user.id)
    user.update(user_in)
    return user


@router.get("/me", response_model=User)
def read_user_me(
    *,
    current_user: UserModel = Depends(get_current_active_user),
):
    """Get current user."""
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_me(
    *,
    current_user: UserModel = Depends(get_current_active_user),
):
    current_user.delete()
    return


# TODO: send an email
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
    try:
        user = UserModel.create(user_in)
    except ModelExistError:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    return user


@router.get("/{user_id}", response_model=User)
def read_user_by_id(
    *,
    user_id: int,
    current_user: UserModel = Depends(get_current_active_user),
):
    """Get a specific user by id."""
    try:
        user = UserModel.find_or_fail(user_id)
    except ModelNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )

    # retrieving myself
    if user == current_user:
        return user

    # if i'm not this user, then I must be admin to retrieve it
    if not current_user.is_superuser or not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return user


@router.put("/{user_id}", response_model=User)
def update_user(
    *,
    user_id: int,
    user_in: UserUpdate,
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """Update a user"""
    try:
        user = UserModel.find_or_fail(user_id)
    except ModelNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this username does not exist in the system",
        )
    return user.update(user_in)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    *,
    user_id: int,
    current_user: UserModel = Depends(get_current_active_superuser),
):
    try:
        user = UserModel.find_or_fail(user_id)
    except ModelNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this username does not exist in the system",
        )
    user.delete()
    return
