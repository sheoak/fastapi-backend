"""Misc. utils

TODO: refactor mail sending helpers
"""
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import random
import emails
import hashlib
import pwnedpass
from emails.template import JinjaTemplate
from jose import jwt

from app.core import config


def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> None:
    """Send a generic email"""
    assert config.EMAILS_ENABLED, "no provided configuration for email variables"
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(config.EMAILS_FROM_NAME, config.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": config.SMTP_HOST, "port": config.SMTP_PORT}
    if config.SMTP_TLS:
        smtp_options["tls"] = True
    if config.SMTP_USER:
        smtp_options["user"] = config.SMTP_USER
    if config.SMTP_PASSWORD:
        smtp_options["password"] = config.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logging.info(f"send email result: {response}")


def send_test_email(email_to: str) -> None:
    """Send a test email"""
    project_name = config.PROJECT_NAME
    subject = f"{project_name} - Test email"
    with open(Path(config.EMAIL_TEMPLATES_DIR) / "test_email.html") as f:
        template_str = f.read()
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": config.PROJECT_NAME, "email": email_to},
    )


def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    """Send an email to reset your password"""
    project_name = config.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    with open(Path(config.EMAIL_TEMPLATES_DIR) / "reset_password.html") as f:
        template_str = f.read()
    server_host = config.FRONTEND_HOST + config.FRONTEND_RESET_PASSWORD_URL
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": config.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": config.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": server_host.format(token=token)
        },
    )


def send_confirmation_email(email_to: str, token: str) -> None:
    """Send an email to validate an email update"""
    project_name = config.PROJECT_NAME
    subject = f"{project_name} - Email modification"
    with open(Path(config.EMAIL_TEMPLATES_DIR) / "email_confirmation.html") as f:
        template_str = f.read()
    server_host = config.FRONTEND_HOST + config.FRONTEND_CONFIRM_EMAIL
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": config.PROJECT_NAME,
            "username": email_to,
            "email": email_to,
            "valid_hours": config.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": server_host.format(token=token)
        },
    )


def send_generate_password_email(email_to: str, email: str, password: str):
    """Send a temporary password by email with a magic link to login"""
    project_name = config.PROJECT_NAME
    subject = f"{project_name} - Magic link for user {email}"
    with open(Path(config.EMAIL_TEMPLATES_DIR) / "generate_password.html") as f:
        template_str = f.read()
    server_host = config.FRONTEND_HOST + config.FRONTEND_MAGICLINK_URL
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": config.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": config.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": server_host.format(token=password),
        },
    )


def send_new_account_email(
    email_to: str,
    username: str,
    token: str = None,
    open_registration: bool = False
) -> None:
    """Send an email after sign-up"""
    if open_registration:
        template = 'new_account_open.html'
    else:
        template = 'new_account.html'

    project_name = config.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    with open(Path(config.EMAIL_TEMPLATES_DIR) / template) as f:
        template_str = f.read()

    # we send a magic link if the token was given, otherwise we go to login
    server_host = config.FRONTEND_HOST
    if token:
        server_host += config.FRONTEND_MAGICLINK_URL
        server_host = server_host.format(token=token)
    else:
        server_host += config.FRONTEND_LOGIN_URL

    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": config.PROJECT_NAME,
            "username": username,
            "email": email_to,
            "link": server_host,
        },
    )


# TODO: factorize
def generate_password_reset_token(email: str) -> str:
    """Generate a token to reset your password"""
    delta = timedelta(hours=config.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email}, config.SECRET_KEY, algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        return decoded_token["sub"]
    except jwt.JWTError:
        return None


def generate_email_confirmation_token(email: str, new_email: str) -> str:
    delta = timedelta(hours=config.EMAIL_CONFIRMATION_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {
            "exp": exp,
            "nbf": now,
            "sub": email,
            "email": new_email,
        },
        config.SECRET_KEY, algorithm="HS256",
    )
    return encoded_jwt


def verify_email_confirmation_token(token) -> Tuple:
    try:
        decoded_token = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        return (decoded_token["sub"], decoded_token["email"])
    except jwt.JWTError:
        return None


def is_password_corrupted(password: str) -> bool:
    with open(config.PASSWORD_DB_PATH, 'rb') as f:
        if pwnedpass.search(f, hashlib.sha1(password.encode()).digest()):
            return True
        return False


def random_word():
    with open(config.RANDOM_WORD_FILE) as f:
        line = next(f)
        for num, aline in enumerate(f, 2):
            if random.randrange(num):
                continue
            line = aline
        return line.strip()


def random_n_words(n=4):
    return '-'.join(random_word() for i in range(0, n))
