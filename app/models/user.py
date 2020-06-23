"""
Generic User model
"""
from __future__ import annotations

from typing import Optional

# import jwt
# from jwt import PyJWTError
# from app.core.jwt import ALGORITHM
# from app.core.jwt import create_access_token
# from app.schemas.token import TokenPayload

from passlib.context import CryptContext
# from fastapi import Security
# from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import Boolean, Column, Integer, String

from app.db.base_class import BaseModel, ModelExistError
from app.schemas.user import UserCreate, UserUpdate, UserBaseInDB


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/v1/login/access-token")


class User(BaseModel):
    __repr_attrs__ = ['id', 'email', 'full_name']

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    # items = relationship("Item", back_populates="owner")

    @classmethod
    def _set_hash(cls, data):
        if 'password' in data and data["password"]:
            hash = pwd_context.hash(data["password"])
            del data["password"]
            data["hashed_password"] = hash
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
        """Try to authenticate the given user and return the user in cas of
        success. Note that inactive users can be authenticate.
        Example:
            User.authenticate("mymail@domain.com", "greatpassword")
        """
        # note that we get the user and don't make a direct search in the
        # database to avoid leaking informations in logs
        user = cls.get(email=email)
        if user and user.verify_password(password):
            return user
        return None

    # TODO: finish this, find a way to load the configuration
    # in a generic way
    # def get_from_token(
    #     self,
    #     token: str = Security(reusable_oauth2),
    # ):
    #     # TODO: user model
    #     try:
    #         payload = jwt.decode(token, config.SECRET_KEY, algorithms=[ALGORITHM])
    #         token_data = TokenPayload(**payload)
    #     except PyJWTError:
    #         return None

    #     return self.find_or_fail(token_data.user_id)

    def update(self, user: UserUpdate) -> User:
        """Update the user with given data
        Example:
            user.update(password="thisisasecret")
        """
        data = self._import(user)
        return super().update(**data)

    def verify_password(self, password: str) -> bool:
        """Check that the password match the user password
        Example:
            if user.verify_password(wrong_password):
                print('Wrong password')
        """
        return pwd_context.verify(password, self.hashed_password)
