"""Testing account features
Uses pytest-bdd
See features/ for the Gerkan definitions
"""
import pytest  # noqa

from typing import Dict, Callable

from requests.models import Response
from pytest_bdd import scenarios, given, when, then, parsers

from app.models.user import User as UserModel
from app.utils import generate_password_reset_token, generate_email_confirmation_token


# Loading the scenarios
# Note that scenarios can be override *before* this line to add more
# configuration, like parametrize fixtures.
scenarios("features/login.feature")
scenarios("features/user.feature")


# -----------------------------------------------------------------------------
# GIVEN…
# For generic @given, see conftest.py
# -----------------------------------------------------------------------------


@given("I have a recovery token")
def recovery_token(
    user: Dict
) -> str:
    """Return a valid auth token"""
    token = generate_password_reset_token(email=user["email"])
    return token


@given("I have a recovery token with an invalid email", target_fixture="recovery_token")
def recovery_token_invalid_email(
) -> str:
    """Return a valid auth token"""
    token = generate_password_reset_token(email="invalidemail@fastapi.test")
    return token


@given("I have an invalid recovery token", target_fixture="recovery_token")
def recovery_invalid_token(
) -> str:
    """Return a valid auth token"""
    return 'wrong'


@given("I have a temporary password", target_fixture="user")
def password_generated(
    user: Dict
) -> str:
    """Return a valid auth token"""
    user['password'] = UserModel.generate_password(user['email'])
    return user


@given("I set myself as an admin", target_fixture="user")
def set_as_admin(
    user: Dict
):
    del user["password"]
    user["is_superuser"] = True
    return user


@given("I have an email modification token", target_fixture='token')
def get_email_modification_token(
    user: Dict
):
    new_email = "newemail@fastapi.test"
    return generate_email_confirmation_token(email=user["email"], new_email=new_email)


# @given("My account gets disabled")
# def account_gets_disabled(
#     user: Dict
# ):


# -----------------------------------------------------------------------------
# WHEN
# -----------------------------------------------------------------------------

@when("I request an email modification")
def request_new_email(
    post: Callable,
    new_email: str,
    context: Dict,
):
    context.data = new_email
    context.response = post(f"/me/change-email/{new_email['email']}")


@when("I confirm the email modification")
def confirm_email(
    user: Dict,
    post: Callable,
    context: Dict,
    token: str,
):
    context.data = user
    context.response = post(f"/validate-email/{token}")


@when("I request a token")
def request_token(
    post: Callable,
    context: Dict,
    user: Dict[str, str],
) -> Dict[str, str]:
    """Trying to get a token and store the response"""
    credentials = {
        "username": user["email"],
        "password": user["password"]
    }
    context.data = user
    context.response = post("/login/access-token", data=credentials)


@when('I request a temporary password')
def request_temporary_password(
    post: Callable,
    context: Dict,
    user: Dict[str, str],
) -> Dict[str, str]:
    """Requesting a temporary password"""
    context.data = user
    context.response = post(f"/login/generate-password/{user['email']}")


@when("I request a token with invalid data")
def request_token_invalid(
    post: Callable,
    context: Dict,
    user: Dict[str, str],
) -> Dict[str, str]:
    """Trying to get a token with invalid data and store the response"""
    credentials = {
        "username": user["email"],
        "password": "totallywrong"
    }
    context.data = user
    context.response = post("/login/access-token", data=credentials)


@when("I verify my token")
def verify_token(
    post: Callable,
    context: Dict,
    user: Dict,
) -> None:
    """A simple call to the test-token endpoint"""
    context.data = user
    context.response = post("/login/test-token")


@when("I retrieve my profile")
def get_profile(
    get: Callable,
    context: Dict,
    user: Dict,
) -> None:
    """Retrieve a profile and store the response"""
    context.data = user
    context.response = get("/me/")


@when("I create an account")
def create_account(
    post: Callable,
    context: Dict,
    user: Dict[str, str],
) -> None:
    """Create an account and store the response"""
    context.data = user
    user["full_name"] = 'John'
    context.response = post("/users/open", json=user)


@when("I create an account on the admin endpoint")
def create_account_admin(
    post: Callable,
    context: Dict,
    user: Dict[str, str],
) -> None:
    """Create an account on the admin endpoint and store the response"""
    context.data = user
    context.response = post("/users/", json=user)


# TODO: modify the data
# TODO: email modification system
@when("I update my account")
def update_account(
    put: Callable,
    context: Dict,
    user: Dict[str, str],
) -> None:
    """Create an account and store the response"""
    context.data = user
    context.response = put("/me", json=user)


@when(parsers.parse('I update the account'))
def update_an_account(
    put: Callable,
    context: Dict,
    user: Dict,
) -> None:
    data = {
        "email": "another-email@domain.com"
    }
    context.data = user
    context.data["email"] = data["email"]
    context.response = put(f'/users/{user["id"]}', json=data)


@when(parsers.re('I update the account "(?P<user_name>.+)"'))
def update_an_account_by_name(
    put: Callable,
    context: Dict,
    users: Dict,
    user_name: str,
) -> None:
    """Create an account and store the response"""
    user = next(filter(lambda user: user['full_name'] == user_name, users))

    data = {
        "email": "a-brand-new-email@domain.com",
    }
    # context update
    user["email"] = data["email"]
    context.data = user
    context.response = put(f'/users/{user["id"]}', json=data)


@when(parsers.parse('I retrieve the user by id "{user_id:d}"'))
def get_user_by_id(
    get: Callable,
    context: Dict,
    user_id: int,
) -> None:
    """Get a user profile by its id and store the reponse"""
    context.response = get(f'/users/{user_id}')


@when(parsers.parse('I retrieve the user "{fullname:l}"'))
def get_user(
    get: Callable,
    context: Dict,
    users: Dict,
    fullname: str,
) -> None:
    """Get a user profile by its id and store the reponse"""
    user = next(filter(lambda user: user['full_name'] == fullname, users))
    context.data = user
    context.response = get(f'/users/{user["id"]}')


@when("I request a new password")
def pasword_recovery(
    post: Callable,
    context: Dict,
    user: Dict[str, str],
) -> None:
    context.response = post(f'/password-recovery/{user["email"]}')


# TODO: test with default limit
@when("I retrieve the list of users")
def get_users(
    get: Callable,
    context: Dict,
    page: int,
) -> Dict[str, str]:

    if page is None:
        limit = 2
        """Retrieve the list of users and store the response"""
        context.response = get(f"/users?limit={limit}")
    else:
        limit = 2
        context.response = get(f"/users/?page={page}&limit={limit}")


@when("I visit the recovery link with my token")
def recovery_link(
    post: Callable,
    recovery_token: str,
    context: Dict,
):
    data = {
        "new_password": "validpassword",
        "token": recovery_token
    }
    context.data = {
        "password": data["new_password"]
    }
    context.response = post(f"/reset-password/?token={recovery_token}", json=data)


@when("I delete the user")
def delete_user(
    user: Dict,
    delete: Callable,
    context: Dict,
):
    context.response = delete(f"/users/{user['id']}")


@when(parsers.parse('I delete the user by id "{user_id:d}"'))
def delete_user_by_id(
    user_id: Dict,
    delete: Callable,
    context: Dict,
):
    context.response = delete(f"/users/{user_id}")


@when(parsers.parse('I delete the user "{fullname:l}"'))
def delete_user_by_name(
    fullname: str,
    users: Dict,
    delete: Callable,
    context: Dict,
):
    user = next(filter(lambda user: user['full_name'] == fullname, users))
    context.response = delete(f"/users/{user['id']}")


@when("I delete my account")
def delete_my_account(
    delete: Callable,
    context: Dict,
):
    context.response = delete("/me")

# -----------------------------------------------------------------------------
# THEN
# -----------------------------------------------------------------------------


@then("I should be admin")
@then("It should be admin")
def check_admin(
    response: Response,
) -> None:
    """Ensure that the returned user is not an admin"""
    r = response.json()
    assert "is_superuser" in r
    assert r["is_superuser"]


@then("I should not be admin")
@then("It should not be admin")
def check_not_admin(
    response: Response,
) -> None:
    """Ensure that the returned user is not an admin"""
    r = response.json()
    assert "is_superuser" in r
    assert not r["is_superuser"]


@then("I should be active")
@then("It should be active")
def check_active(
    response: Response,
) -> None:
    """Ensure that the returned user is active"""
    r = response.json()
    assert "is_active" in r
    assert r["is_active"]


@then("I should be inactive")
@then("It should be inactive")
def check_inactive(
    response: Response,
) -> None:
    """Ensure that the returned user is active"""
    r = response.json()
    assert "is_active" in r
    assert not r["is_active"]


@then('The response should be empty')
def check_empty_response(response: Response) -> None:
    """Ensure that no response is returned"""
    r = response.json()
    assert r is None


@then("The response should only contain the error")
def check_empty_error_response(
    response: Response,
) -> None:
    """Ensure that error response do not leak informations"""
    r = response.json()
    assert "detail" in r
    assert len(r) == 1


@then(parsers.re('The response error type should be "(?P<error>.+)"'))
def check_error_type(
    response: Response,
    error: str,
) -> None:
    """Ensure that the response return the proper error types"""
    r = response.json()
    assert r["detail"][0]["type"]
    assert r["detail"][0]["type"] == error


@then(parsers.re('The response error should contain "(?P<error>.+)"'))
def check_error_response(
    response: Response,
    error: str,
) -> None:
    """Ensures that the response return the proper error strings"""
    r = response.json()
    assert "detail" in r
    assert error in r["detail"]


@then(parsers.re('The error list should contain "(?P<error>.+)" in field "(?P<field>.+)"'))
def check_error_response_for_field(
    response: Response,
    error: str,
    field: str,
) -> None:
    """Ensures that the response return the proper error strings"""
    r = response.json()
    assert "detail" in r
    found = False
    for e in r["detail"]:
        assert "loc" in e, "Error data does not contain field 'loc'"
        assert isinstance(e["loc"], list)
        if e["loc"][2] == field:
            assert e["msg"] and error in e["msg"]
            found = True

    assert found, f"String not found in error message: {error}"


@then(parsers.parse("The list should contain all the users for page {n:d}"))
def check_page_content(
    response: Response,
    users: Dict[str, str],
    page: int,
):
    limit = 2
    data = response.json()
    # make sure the test data is enough
    assert len(users) > limit, "The limit is not high enough for tests"
    # then test the result
    assert len(data) == limit, "Number of results do not match"

    page = 1 if page is None else page
    i = (page - 1) * limit
    for user in data:
        assert user["id"] == users[i]["id"], "user id does not match"
        assert user["email"] == users[i]["email"], "user email does not match"
        i += 1


@then("The list should not contain passwords")
def check_list_user_passwords(
    response: Response
) -> None:
    """Ensure that the user list return matches the test base"""
    r = response.json()
    for user in r:
        assert "password" not in user, "password is present!"
        assert "hashed_password" not in user, "hashed password is present!"


@then(parsers.re(r'The following user fields should match: "(?P<listing>.+)"'))
def field_matching(
    response: Response,
    data: Dict[str, str],
    listing: str
) -> None:
    """Check that the given response fields match the current user"""
    r = response.json()
    for field in [f.strip() for f in listing.split(',')]:
        assert field in r
        assert r[field] == data[field]


# @then(parsers.re(r'The response should contain the following fields: "(?P<listing>.+)"'))
# def fields_exist(
#     response: Response,
#     listing: str
# ) -> None:
#     """Check that the given fields exist in the response"""
#     r = response.json()
#     for field in [f.strip() for f in listing.split(',')]:
#         assert field in r


@then(parsers.re(r'The response should contain the following non-empty fields: "(?P<listing>.+)"'))
def fields_non_empty(response: Response, listing: str) -> None:
    """Check that the given fields exist in the response"""
    r = response.json()
    for field in [f.strip() for f in listing.split(',')]:
        assert field in r


@then(parsers.re(r'The response field "(?P<field>.+)" should be "(?P<value>.+)"'))
def fields_equal_to(response: Response, field: str, value: str) -> None:
    """Check that the given fields exist in the response"""
    r = response.json()
    assert field in r
    assert r[field] == value


@then("The response should not contain my password")
def check_password_absent(
    response: Response,
    # user: Dict[str, str],
    data: Dict,
) -> None:
    r = response.json()
    assert data["password"] not in r.values()
