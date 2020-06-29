"""Test initialisation

Tests are divided in 3 categories:

- unitary tests     : use pytest
- functionnal tests : use pytest
- integration tests : use pytest-bdd

Note that @given is a pytest-bdd decorator that will also produce a global
fixture. For homogeneity and clarity this decorator is used everywhere

TODO: run unitary test with xdist in parrallel
TODO: try pdbpp
"""
import os
import random
import string
from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, Generator

import pytest  # noqa
# import smtpmock
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, then
from sqlalchemy.orm.scoping import scoped_session
from requests.models import Response

import app.tests.data.samples as samples
from app.api.utils.security import create_token
from app.core import config
from app.core.jwt import create_access_token
from app.db.base_class import Base
from app.db.session import engine, SessionScope
from app.main import app
from app.models.user import User, pwd_context
from app.tests.utils.utils import tweak_config

# import asyncore
# import re
# import smtpd
# import threading

# class MockSMTPServer(smtpd.SMTPServer, threading.Thread):
#     '''
#     A mock SMTP server. Runs in a separate thread so can be started from
#     existing test code.
#     '''

#     def __init__(self, hostname, port):
#         threading.Thread.__init__(self)
#         smtpd.SMTPServer.__init__(self, (hostname, port), None)
#         self.daemon = True
#         self.received_messages = []
#         self.start()

#     def run(self):
#         asyncore.loop()

#     def process_message(self, peer, mailfrom, rcpttos, data):
#         self.received_messages.append(data)

#     def reset(self):
#         self.received_messages = []

#     # helper methods for assertions in test cases

#     def received_message_matching(self, template):
#         for message in self.received_messages:
#             if re.match(template, message): return True
#         return False

#     def received_messages_count(self):
#         return len(self.received_messages)


@given("I have a smtp server running", scope="session")
def smtp_server():
    pass
    # return MockSMTPServer(config.SMTP_HOST, config.SMTP_PORT)


@given("The test database is empty", scope="session")
def empty_session() -> Generator:
    """Prepare an empty test database"""

    file = ''
    dsn = config.SQLALCHEMY_DATABASE_URI

    # Before the test we setup the database temp dir
    if dsn.startswith('sqlite:///'):
        file = dsn.replace('sqlite:///', '')
        dir = os.path.dirname(os.path.realpath(file))
        try:
            os.mkdir(dir)
        except Exception:
            pass

    # Re-contruct the database for each run
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # we don't want to commit data during tests
    def mock_commit():
        pass
    SessionScope.commit = mock_commit

    yield SessionScope

    if (file):
        os.remove(file)


@given("I have a test database ready", scope="session")
def session(empty_session: scoped_session, users_hashed: Dict) -> Generator:
    """Build the test database from alembic and insert test data"""

    engine.execute(User.__table__.insert(), users_hashed)

    yield empty_session


@given("Some users are in the system", scope="function")
def db(session: scoped_session) -> Generator:
    """Return a session on a test-populated database.
    Restore database after every test
    This allow tests to be independant.
    Operation via engine are much faster and do not depend on pydantic methods.
    """
    s = session()
    yield s
    # this will rollback uncommited changes for next test
    s.close()


@given("No user are in the system", scope="function")
def empty_db(empty_session: scoped_session) -> Generator:
    """Return a session on an empty database.
    Restore database after every test.
    This allow tests to be independant.
    Operation via engine are much faster and do not depend on pydantic methods.
    """
    s = empty_session()
    yield s
    # this will rollback uncommited changes for next test
    s.close()


@given("I have test data", scope="session")
def sample_data() -> Dict:
    """"Test data so that test are predictibles"""
    return samples


# ----------------------------------------------------------------------------
# TEST CLIENT
# ----------------------------------------------------------------------------
@given("I have a Test client", scope="session")
def client() -> Generator:
    """ A test client to be used in any test """
    with TestClient(app) as c:
        yield c


@given("I have a test client proxy method")
def api_request(
    client: TestClient,
    headers: Dict,
):
    # return a method builder: get the method from the name and the headers
    def build_method(method):
        # return the client method (ie: post, get, put, delete)
        def get_method(url, **kwargs):
            caller = getattr(client, method)
            return caller(f"{config.API_V1_STR}{url}", headers=headers, **kwargs)
        return get_method
    return build_method


@given("I'm ready to send a get request")
def get(api_request):
    return api_request('get')


@given("I'm ready to do a post request")
def post(api_request):
    return api_request('post')


@given("I'm ready to do a put request")
def put(api_request):
    return api_request('put')


@given("I'm ready to do a delete request")
def delete(api_request):
    return api_request('delete')


@given("I don't have a token", scope="function")
def headers():
    return {}


@given("I have a valid token", target_fixture="headers", scope="function")
def headers_auth(
    user: Dict[str, str],
) -> Dict[str, str]:
    token = create_token(user["id"]).decode("utf-8")
    return {"Authorization": f"Bearer {token}"}


@given("I have an expired token", target_fixture="headers", scope="function")
def headers_auth_expired(
    user: Dict[str, str],
) -> Dict[str, str]:

    token = create_access_token(
        data={"user_id": user["id"]}, expires_delta=timedelta(minutes=-1)
    ).decode('utf-8')
    return {"Authorization": f"Bearer {token}"}


@given("I have a token with an invalid id", target_fixture="headers", scope="function")
def headers_auth_invalid_id(
) -> Dict[str, str]:
    token = create_token(8888888888).decode("utf-8")
    return {"Authorization": f"Bearer {token}"}


# TODO: create an expired token
@given("I have an invalid token", target_fixture="headers", scope="function")
def headers_auth_invalid(
    user: Dict[str, str],
) -> Dict[str, str]:
    """Create a invalid expired token from the user id"""
    token = 'wrong'
    return {"Authorization": f"Bearer {token}"}


# ----------------------------------------------------------------------------
# TESTS CONTEXT
# ----------------------------------------------------------------------------
@given("I have a context for tests", scope="function")
def context():
    """Return the context for @then steps
    We need this because @when steps do not return a fixture.
    Action usually don't return data, but with an API it's impossible
    To do without it in integration tests.
    """
    @dataclass
    class Context():
        response: Dict = None
        data: Dict = None

    return Context()


@given("I have a context for tests response")
def response(context):
    """Shortcut to the response in context"""
    return context.response


@given("I have the data from the previous request")
def data(context):
    """Shortcut to the response in context"""
    return context.data


# ----------------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------------
@given("The server accepts open registration")
def enable_open_registration() -> None:
    """Enable open registration configuation"""
    yield from tweak_config('USERS_OPEN_REGISTRATION', True)


@given("The server accepts passwordless registration")
def enable_passwordless_registration() -> None:
    """Enable open registration configuation"""
    yield from tweak_config('USERS_PASSWORDLESS_REGISTRATION', True)


@given("The server refuses passwordless registration")
def disable_passwordless_registration() -> None:
    """Enable open registration configuation"""
    yield from tweak_config('USERS_PASSWORDLESS_REGISTRATION', False)


@given("The server refuses open registration")
def disable_open_registration() -> None:
    """Disable open registration configuation"""
    yield from tweak_config('USERS_OPEN_REGISTRATION', False)


@given("The server is set to check corrupted passwords")
def enable_pwned_password() -> None:
    """Enable password verification in pwned database"""
    yield from tweak_config('PASSWORD_PWNED_CHECK', True)


@given("The server is set to not check corrupted passwords")
def disable_pwned_password() -> None:
    """Disable password verification in pwned database"""
    yield from tweak_config('PASSWORD_PWNED_CHECK', False)


@given("The server is set to not check special chars in passwords")
def enable_password_special_chars() -> None:
    """Disable special chars password verification"""
    yield from tweak_config('PASSWORD_MATCH_REG', None)


# ----------------------------------------------------------------------------
# USERS (fixtures)
# ----------------------------------------------------------------------------
@given("I have sample users", scope="session")
def users(sample_data: Dict) -> Dict:
    """"Return all sample users"""
    return sample_data.users.copy()


@given("I have sample active users", scope="session")
def active_users(users: Dict) -> Dict:
    """"Return only active users"""
    return [user for user in users if user["is_active"]]


@given("I have sample normal users", scope="session")
def normal_users(active_users: Dict) -> Dict:
    """"Return only normal active users"""
    return [user for user in active_users if not user["is_superuser"]]


@given("I have sample admin users", scope="session")
def super_users(active_users: Dict) -> Dict:
    """"Return only active admins"""
    return [user for user in active_users if user["is_superuser"]]


@given("I have sample inactive users", scope="session")
def inactive_users(users: Dict) -> Dict:
    """"Return only inactive users"""
    return [user for user in users if not user["is_active"]]


@given("I have sample users with hashed passwords", scope="session")
def users_hashed(users: Dict) -> Dict:
    """Return the user data with hashed_password field populated"""
    result = users.copy()
    for user in result:
        user["hashed_password"] = pwd_context.hash(user["password"])

    return result


@given("I have an active user", scope="function")
@given("I'm an active user", scope="function")
def user(normal_users: Dict[str, str]) -> Dict[str, str]:
    """A standard, non admin user"""
    return normal_users[0].copy()


@given("I have a new user", target_fixture="user")
@given("I'm a new user", target_fixture="user")
def base_user() -> Dict[str, str]:
    """A user that is not in the database"""
    return {
        "email": "anewemail@domain.com",
        "password": "avalidpassword_99!"
    }


@given("I don't have a password", target_fixture="user")
def base_user_passwordless(user: Dict[str, str]) -> Dict[str, str]:
    del user['password']
    return user


@given("I have a non existing user", target_fixture="user")
def non_existing_user() -> Dict[str, str]:
    """A user that is not in the database, with an id"""
    return {
        "id": 9999999999,
        "email": "anewemail@domain.com",
        "password": "avalidpassword_99!"
    }


@given("I'm an anonymous user", target_fixture="user")
def anon_user() -> Dict:
    """An empty user"""
    return {}


@given("I'm an inactive user", target_fixture="user")
@given("And There is an existing inactive user", target_fixture="user")
def inactive_user(inactive_users: Dict[str, str]) -> Dict[str, str]:
    """An inactive user"""
    return inactive_users[0].copy()


@given("I'm an admin", target_fixture="user")
def admin(super_users: Dict[str, str]) -> Dict[str, str]:
    """An admin user"""
    return super_users[0].copy()


@given("I have no email", target_fixture="user")
def no_email(base_user: Dict[str, str]) -> Dict[str, str]:
    u = base_user.copy()
    u["email"] = ""
    return u


@given("I have an invalid password", target_fixture="user")
def invalid_password(base_user: Dict[str, str]) -> Dict[str, str]:
    u = base_user.copy()
    u["password"] = "short"
    return u


@given("I have a corrupted password", target_fixture="user")
def corrupted_password(base_user: Dict[str, str]) -> Dict[str, str]:
    u = base_user.copy()
    u["password"] = "azerty123"
    return u


@given("I have a non-corrupted password", target_fixture="user")
def non_corrupted_password(base_user: Dict[str, str]) -> Dict[str, str]:
    # TODO: random helper, fast
    u = base_user.copy()
    u["password"] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=100))
    return u


@given("I have an unavailable email", target_fixture="user")
def unavailable_email(base_user: Dict[str, str]) -> Dict[str, str]:
    u = base_user.copy()
    u["email"] = config.EMAIL_TEST_USER
    return u


@given("I have a new email", target_fixture="user")
def new_email(user: Dict[str, str]) -> Dict[str, str]:
    u = user.copy()
    u["email"] = "a-brand-new-mail@domain.com"
    return u


@given("I have an invalid email", target_fixture="user")
def new_invalid_email(user: Dict[str, str]) -> Dict[str, str]:
    u = user.copy()
    u["email"] = "invalid"
    return u


@given("I don't set a page number")
def page():
    return None


@given(parsers.parse('I set the page to {n:d}'), target_fixture="page")
def page_n(n):
    return n


@then(parsers.parse("I should get a '{code:d}' response"))
def check_response_status(
    response: Response,
    code: int,
) -> None:
    """Ensure that the status code matches"""
    assert hasattr(response, "status_code"), \
        "Response status code is missing"
    assert response.status_code == code, \
        f"Expected status code {code} but got {response.status_code}"


@then("I should receive an email")
def check_get_email(
    smtp_server
) -> None:
    pass
    # assert(smtp_server.received_message_matching("From: .*\\nTo: .*\\n+.+tent"))


@then("I should not receive an email")
def check_get_no_email(
    smtp_server
) -> None:
    pass
