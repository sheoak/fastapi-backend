from datetime import datetime

from pydantic import BaseModel, EmailStr, validator
from typing import Optional
# import re

# TODO: migrate to a pip package
from app.utils import is_password_corrupted
from app.core import config


# TODO: move to validators module?
def validate_password(password: str):
    """
    Enforce password do not contain unusual characters and are long enough

    While decreasing allowed characters also decrease the security,
    we need to consider that the UI might not have all chars available,
    for example when using a mobile phone. For that reason the password
    need to match the folowing rules:
    """

    if not config.USERS_PASSWORDLESS_REGISTRATION and not password:
        raise ValueError("password cannot be empty")

    if config.USERS_PASSWORDLESS_REGISTRATION and not password:
        return password

    if len(password) < config.MIN_PASSWORD_LENGTH:
        raise ValueError("password is too short")

    # TODO: move to options
    # if not re.match(r"^(\s|\w|[-$#\"|\\+%=/<>@^_{}~*:;!?&'])+$", password):
    #     raise ValueError("passwords contains forbidden characters")

    if (not config.PASSWORD_PWNED_CHECK):
        return password

    if is_password_corrupted(password):
        raise ValueError("Please use a different password. This one has been compromised.")
    return password


# Shared properties
class UserBase(BaseModel):
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    full_name: Optional[str] = None


class UserBaseInDB(UserBase):
    id: Optional[int] = None
    email: Optional[EmailStr] = None

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: Optional[str]

    _normalize_password = validator('password', allow_reuse=True, always=True)(validate_password)


# Properties to receive via API on update
# Updating email is forbidden
# TODO: manage errors if email is given
class UserUpdate(UserBase):
    password: Optional[str] = None

    _normalize_password = validator('password', allow_reuse=True, always=True)(validate_password)


# Updating email is allowed
class UserUpdateFull(UserUpdate):
    email: Optional[EmailStr] = None


# Additional properties to return via API
class User(UserBaseInDB):
    pass


# Additional properties stored in DB
class UserInDB(UserBaseInDB):
    hashed_password: str
    time_creation: datetime
    time_update: datetime
    login_retry: int
    password_set: bool
    password_expire: datetime
