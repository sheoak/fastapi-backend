from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import status

from app.api.utils.security import get_current_user, create_token
from app.models.user import User as UserModel
from app.schemas.user import UserUpdate
from app.schemas.msg import Msg
from app.schemas.token import Token
from app.schemas.user import User
from app.utils import (
    generate_password_reset_token,
    send_reset_password_email,
    send_generate_password_email,
    verify_password_reset_token,
)

router = APIRouter()


@router.post("/login/access-token", response_model=Token, tags=["login"])
def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """OAuth2 compatible token login, get an access token for future requests"""
    user = UserModel.authenticate(
        email=form_data.username,
        password=form_data.password
    )
    # we do not send information about disabled users to avoid informations leaks
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    return {
        "access_token": create_token(user.id),
        "token_type": "bearer",
    }


# TODO: handle errors
# TODO: send email
@router.post("/login/generate-password/{email}", tags=["login"], response_model=Msg)
def generate_password(email: str):
    """Generate a temporary password and send it by email"""
    password = UserModel.generate_password(email=email)

    if password:
        send_generate_password_email(
            email_to=email, email=email, password=password
        )

    return {"msg": "If this email is valid you will receive a magic link shortly."}


@router.post("/login/test-token", tags=["login"], response_model=User)
def test_token(current_user: UserModel = Depends(get_current_user)):
    """Test access token"""
    return current_user


@router.post("/password-recovery/{email}", tags=["login"], response_model=Msg)
def recover_password(email: str):
    """Password Recovery"""
    user = UserModel.get(email=email)

    if user:
        password_reset_token = generate_password_reset_token(email=email)
        send_reset_password_email(
            email_to=user.email, email=email, token=password_reset_token
        )

    # we do not leak informations about existing users
    return {"msg": "If this email is valid, you will receive an email with your recovery link shortly."}


@router.post("/reset-password/", tags=["login"], response_model=Msg)
def reset_password(token: str = Body(...), new_password: str = Body(...)):
    """Reset password"""

    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = UserModel.get(email=email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )

    user_in = UserUpdate(password=new_password)
    user.update(user_in)
    return {"msg": "Password updated successfully"}
