import secrets

from envparse import env
from dotenv import load_dotenv
load_dotenv(verbose=True)

API_V1_STR = env.str("API_V1_STR", default="/v1")

SERVER_NAME = env.str("SERVER_NAME", default="localhost")
SERVER_HOST = env.str("SERVER_HOST", default="localhost")
# a string of origins separated by commas, e.g:
# http://localhost, https://localhost, http://localhost:8080
BACKEND_CORS_ORIGINS = env.str("BACKEND_CORS_ORIGINS")
PROJECT_NAME = env.str("PROJECT_NAME")

# Sentry is the logging system for Heroku. Leave it empty in dev
SENTRY_DSN = env.str("SENTRY_DSN", default="")

SQLALCHEMY_DATABASE_URI = env.str("DATABASE_URL", default="sqlite:///./sqlite.db")

# sqlite need special parameters
if SQLALCHEMY_DATABASE_URI.startswith('sqlite'):
    SQLALCHEMY_CONNECT_ARGS = {"check_same_thread": False}
else:
    SQLALCHEMY_CONNECT_ARGS = {}  # pragma: no cover


SMTP_TLS = env.bool("SMTP_TLS", default=True)
SMTP_PORT = env.int("SMTP_PORT", default=587)
SMTP_HOST = env.str("SMTP_HOST", default="localhost")
SMTP_USER = env.str("SMTP_USER")
SMTP_PASSWORD = env.str("SMTP_PASSWORD")
EMAILS_FROM_EMAIL = env.str("EMAILS_FROM_EMAIL", default="root@localhost")
EMAILS_FROM_NAME = PROJECT_NAME
EMAIL_RESET_TOKEN_EXPIRE_HOURS = 48
EMAIL_TEMPLATES_DIR = "app/email-templates/build"
EMAILS_ENABLED = SMTP_HOST and SMTP_PORT and EMAILS_FROM_EMAIL

FIRST_SUPERUSER = env.str("FIRST_SUPERUSER", default="admin")
FIRST_SUPERUSER_PASSWORD = env.str("FIRST_SUPERUSER_PASSWORD")

USERS_OPEN_REGISTRATION = env.bool("USERS_OPEN_REGISTRATION", default=False)
USERS_PASSWORDLESS_REGISTRATION = env.bool("USERS_PASSWORDLESS_REGISTRATION", default=True)


EMAIL_TEST_USER = env.str("EMAIL_TEST_USER", default="test2@fastapi.test")
PASS_TEST_USER = env.str("PASS_TEST_USER", default="test")

FASTAPI_ENV = env.str("FASTAPI_ENV", default="development")

# security
MIN_PASSWORD_LENGTH = env.int("MIN_PASSWORD_LENGTH", default=8)
SECRET_KEY = env.str("SECRET_KEY", default=secrets.token_urlsafe(32))
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8  # 60 minutes * 24 hours * 8 days = 8 days
PASSWORD_DB_PATH = env.str("PASSWORD_DB_PASS", default='data/pwned-passwords-v5.bin')
PASSWORD_PWNED_CHECK = env.bool("PASSWORD_PWNED_CHECK", default=True)
PASSWORD_ALLOW_SPECIAL = env.bool("PASSWORD_ALLOW_SPECIAL", default=True)
