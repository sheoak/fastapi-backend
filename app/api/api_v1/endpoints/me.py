"""
Current user endpoint: /me/*
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy_mixins import ModelNotFoundError

from app.db.base_class import ModelExistError
from app.api.utils.security import get_current_active_superuser, get_current_active_user
from app.core import config
from app.models.user import User as UserModel
from app.schemas.user import User, UserCreate, UserUpdate


router = APIRouter()


@router.get("/", response_model=User)
def read_user_me(
    *,
    current_user: UserModel = Depends(get_current_active_user),
):
    """Get current user."""
    return current_user


@router.put("/", response_model=User)
def update_user_me(
    *,
    user_in: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user),
):
    """description: Update myself"""
    user = UserModel.find(current_user.id)
    user.update(user_in)
    return user


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_me(
    *,
    current_user: UserModel = Depends(get_current_active_user),
)-> None:
    current_user.delete()
    return
