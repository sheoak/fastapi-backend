from datetime import timedelta

import jwt

from fastapi import HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from fastapi import status
from jwt import PyJWTError
from sqlalchemy_mixins import ModelNotFoundError

from app.core import config
from app.core.jwt import ALGORITHM
from app.core.jwt import create_access_token
from app.models.user import User as UserModel
from app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/v1/login/access-token")


# TODO: migrate to proper util file
def create_token(user_id: int):
    """Create a token from the user id"""
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        data={"user_id": user_id}, expires_delta=access_token_expires
    )


def get_current_user(
    token: str = Security(reusable_oauth2)
):
    # TODO: user model
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
        )
    # TODO: this code sequence is repeated many times in the app — refactor it
    try:
        user = UserModel.find_or_fail(token_data.user_id)
    except ModelNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def get_current_active_user(current_user: UserModel = Security(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


def get_current_active_superuser(current_user: UserModel = Security(get_current_user)):
    if not current_user.is_superuser or not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user
