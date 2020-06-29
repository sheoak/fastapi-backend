"""
Generic User model
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.db.base_class import BaseModel, ModelExistError
from app.schemas.user import UserCreate, UserUpdate, UserBaseInDB

from app.utils import random_n_words


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    __repr_attrs__ = ['id', 'email', 'full_name']

    id = Column(Integer, primary_key=True, index=True)

    # user defined
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    # admin only
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)

    # generated
    login_retry = Column(Integer)
    hashed_password = Column(String)
    password_set = Column(Boolean(), default=False)
    password_expire = Column(DateTime(timezone=True), default=None)
    time_creation = Column(DateTime(timezone=True), default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    @classmethod
    def _set_hash(cls, data):
        if 'password' in data and data["password"]:
            hash = pwd_context.hash(data["password"])
            del data["password"]
            data["hashed_password"] = hash
            data["password_set"] = True
            data["password_expire"] = None
            data["login_retry"] = 0
        return data

    @classmethod
    def _import(cls, user: UserBaseInDB):
        data = user.dict(exclude_unset=True)
        cls._set_hash(data)
        return data

    @classmethod
    def create(cls, user: UserCreate) -> User:
        """Create a new user and return the new instance.
        Example:
            user = User.create(obj)
        """
        if cls.get(email=user.email):
            raise ModelExistError

        data = cls._import(user)
        return super().create(**data)

    @classmethod
    def authenticate(cls, email: str, password: str) -> Optional[User]:
        """Try to authenticate the given user and return the user in case of
        success. Note that inactive users can be authenticate.
        Example:
            User.authenticate("mymail@fastapi.test", "greatpassword")
        """
        # note that we get the user and don't make a direct search in the
        # database to avoid leaking informations in logs
        user = cls.get(email=email)
        if user and user.verify_password(password):
            user.login_retry = 0
            # temporary code cannot be re-use
            if not user.password_set:
                user.hashed_password = None
            return user
        return None

    # TODO: handle errors
    # TODO: move duration to configuration
    @classmethod
    def generate_password(cls, email: str) -> str:
        user = cls.get(email=email)

        if not user:
            return None

        if user.password_set:
            return None

        user.login_retry = 0
        user.password_expire = datetime.now() + timedelta(hours=1)
        password = random_n_words()
        user.hashed_password = pwd_context.hash(password)
        return password

    def update(self, user: UserUpdate) -> User:
        """Update the user with given data
        Example:
            user.update(password="thisisasecret")
        """

        data = self._import(user)
        return super().update(**data)

    # TODO: handle errors
    def verify_password(self, password: str) -> bool:
        """Check that the password match the user password
        Example:
            if not user.verify_password(wrong_password):
                print('Wrong password')
        """
        # password was never defined or generated
        if not self.hashed_password:
            return False

        # password expired
        if self.password_expire and self.password_expire < datetime.now():
            return False

        return pwd_context.verify(password, self.hashed_password)
