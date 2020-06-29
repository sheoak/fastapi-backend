"""
Current user endpoint: /me/*
"""
from fastapi import APIRouter, Depends, status, HTTPException
# from sqlalchemy_mixins import ModelNotFoundError

# from app.db.base_class import ModelExistError
from app.api.utils.security import get_current_active_user
from app.models.user import User as UserModel
from app.schemas.msg import Msg
from app.schemas.user import User, UserUpdate, UserUpdateFull
from app.utils import send_confirmation_email, generate_email_confirmation_token, verify_email_confirmation_token


router = APIRouter()


@router.get("/me", response_model=User)
def read_user_me(
    *,
    current_user: UserModel = Depends(get_current_active_user),
):
    """Get current user."""
    return current_user


# TODO: test
# TODO: check that you can't update your password directly
@router.put("/me", response_model=User)
def update_user_me(
    *,
    user_in: UserUpdate,
    old_password: str = None,
    current_user: UserModel = Depends(get_current_active_user),
):
    """Update myself"""
    user = UserModel.find(current_user.id)

    if user_in.password:

        # updating a non-set password is forbidden
        if not current_user.password_set:
            raise HTTPException(
                status_code=400,
                detail="You must first define a password",
            )

        # updating a password requires to provide the old password
        if not old_password:
            raise HTTPException(
                status_code=400,
                detail="You must provide the old password",
            )

        if not user.authenticate(old_password):
            raise HTTPException(
                status_code=400,
                detail="Old password is invalid",
            )

    user.update(user_in)
    return user


# TODO: test actual deletion
# TODO: ask for password or code
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_me(
    *,
    current_user: UserModel = Depends(get_current_active_user),
) -> None:
    """Delete my account"""
    current_user.delete()
    return


# TODO: ask for password or code
@router.post("/me/change-email/{email}", response_model=Msg)
def change_email(
    *,
    email: str,
    current_user: UserModel = Depends(get_current_active_user),
):
    """Send a confirmation link to the new email"""
    token = generate_email_confirmation_token(email=current_user.email, new_email=email)
    send_confirmation_email(email_to=email, token=token)

    return {"msg": "A confirmation email has been sent."}


# TODO: test
@router.post("/validate-email/{token}", response_model=Msg)
def validate_email(
    *,
    token: str
):
    """Confirm a new email from a token"""
    # decode the token
    decoded_token = verify_email_confirmation_token(token)

    if not decoded_token:
        raise HTTPException(status_code=400, detail="Invalid token")

    (old_email, new_email) = decoded_token

    user = UserModel.where(email=old_email).first()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    # updating the email
    user_in = UserUpdateFull(email=new_email)
    user.update(user_in)

    return {"msg": "Email updated successfully"}
