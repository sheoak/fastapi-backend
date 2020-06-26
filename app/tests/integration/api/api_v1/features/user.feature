@integration
Feature: User endpoints
    As a user
    I want to be able to manage accounts

Background:
    Given Some users are in the system
    And The server is set to not check corrupted passwords
    And I have a smtp server running


# ----------------------------------------------------------------------------
# Create an account
# ----------------------------------------------------------------------------
Scenario: Open registration with a valid account
    Given I'm a new user
    And The server accepts open registration
    When I create an account
    Then I should get a '200' response
    And The following user fields should match: "email"
    And I should not be admin
    And The response should not contain my password
    And I should receive an email

Scenario: Open passwordless registration with a valid account
    Given I'm a new user
    And I don't have a password
    And The server accepts open registration
    And The server accepts passwordless registration
    When I create an account
    Then I should get a '200' response
    And The following user fields should match: "email"
    And I should not be admin
    And I should receive an email

Scenario: Forbidden passwordless registration with a valid account
    Given I'm a new user
    And I don't have a password
    And The server accepts open registration
    And The server refuses passwordless registration
    When I create an account
    Then I should get a '422' response
    And The response should only contain the error

Scenario: Forbidden access to account creation on the admin endpoint
    Given I'm an active user
    And I have a valid token
    And The server accepts open registration
    When I create an account on the admin endpoint
    Then I should get a '403' response
    And The response error should contain "The user doesn't have enough privileges"
    And The response should only contain the error

Scenario: Authorized access to account creation on the admin endpoint
    Given I'm an admin
    And I have a valid token
    And I have a new user
    When I create an account on the admin endpoint
    Then I should get a '200' response
    And The following user fields should match: "email"

Scenario: Register with an invalid email
    Given I have an invalid email
    And The server accepts open registration
    When I create an account
    Then I should get a '422' response
    And The response error type should be "value_error.email"
    And The error list should contain "valid email" in field "email"
    And The response should only contain the error
    And The response should not contain my password

Scenario: Register with an invalid password
    Given I have an invalid password
    And The server accepts open registration
    When I create an account
    Then I should get a '422' response
    And The response error type should be "value_error"
    And The error list should contain "too short" in field "password"
    And The response should only contain the error
    And The response should not contain my password

@local
Scenario: Register with a corrupted password
    Given I have a corrupted password
    And The server accepts open registration
    And The server is set to check corrupted passwords
    When I create an account
    Then I should get a '422' response
    And The error list should contain "compromised" in field "password"
    And The response should only contain the error
    And The response should not contain my password

@local
Scenario: Register with a non-corrupted password
    Given I have a non-corrupted password
    And The server accepts open registration
    And The server is set to check corrupted passwords
    When I create an account
    Then I should get a '200' response

# TODO: 400 error?
Scenario: Open registration with a unavailable email
    Given I have an unavailable email
    And The server accepts open registration
    When I create an account
    Then I should get a '400' response
    And The response error should contain "The user with this username already exists in the system"
    And The response should only contain the error
    And The response should not contain my password

Scenario: Open registration with a missing email
    Given I have no email
    And The server accepts open registration
    When I create an account
    Then I should get a '422' response
    And The error list should contain "valid email" in field "email"
    And The response should only contain the error
    And The response should not contain my password

Scenario: Close registration with a unavailable email
    Given I'm an admin
    And I have a valid token
    And I have an unavailable email
    When I create an account on the admin endpoint
    Then I should get a '400' response
    And The response error should contain "The user with this username already exists in the system"
    And The response should only contain the error
    And The response should not contain my password

Scenario: Open registration when it's disabled
    Given I'm a new user
    And The server refuses open registration
    When I create an account
    Then I should get a '403' response
    And The response error should contain "registration is forbidden"
    And The response should only contain the error
    And The response should not contain my password

# ----------------------------------------------------------------------------
# Update an account
# TODO: check that the user can not set theirselves as admin
# TODO: check that the user cannot change their mail directly
# TODO: check that the user need to confirm current password for change
# ----------------------------------------------------------------------------
# Scenario: Update my account
#     Given I'm an active user
#     And I have a valid token
#     And I have a new email
#     When I update my account
#     Then I should get a '200' response
#     And The following user fields should match: "email, full_name"
#     And I should not be admin
#     And I should be active
#     And The response should not contain my password

# Scenario: Update my account with an invalid email
#     Given I'm an active user
#     And I have a valid token
#     And I have an invalid email
#     When I update my account
#     Then I should get a '422' response
#     And The response should only contain the error
#     And The error list should contain "valid email" in field "email"

# TODO: update an inactive user
Scenario: Update an account
    Given I'm an admin
    And I have a valid token
    When I update the account "Tintin"
    Then I should get a '200' response
    And The following user fields should match: "email, full_name"
    And It should not be admin
    And It should be active

Scenario: Update an inactive account
    Given I'm an admin
    And I have a valid token
    When I update the account "Capitaine Haddock"
    Then I should get a '200' response
    And It should be inactive

Scenario: Update an non existing account
    Given I'm an admin
    And I have a valid token
    And I have a non existing user
    When I update the account
    Then I should get a '404' response
    And The response should only contain the error

# ----------------------------------------------------------------------------
# Retrieve an account
# ----------------------------------------------------------------------------
Scenario: Retrieve my account
    Given I'm an active user
    And I have a valid token
    When I retrieve my profile
    Then I should get a '200' response
    And The following user fields should match: "id, email, is_superuser, is_active"

Scenario: Retrieve any account as an admin
    Given I'm an admin
    And I have a valid token
    When I retrieve the user "Tintin"
    Then I should get a '200' response
    And The following user fields should match: "id, email"

Scenario: Retrieve an non-existing account as an admin
    Given I'm an admin
    And I have a valid token
    When I retrieve the user by id "9999999999"
    Then I should get a '404' response

Scenario: Accessing profiles without authentification
    Given I'm an anonymous user
    When I retrieve the user "Tintin"
    Then I should get a '401' response
    And The response error should contain "Not authenticated"
    And The response should only contain the error

Scenario: Accessing profiles without privileges
    Given I'm an active user
    And I have a valid token
    When I retrieve the user "Tintin"
    Then I should get a '403' response
    And The response error should contain "privileges"
    And The response should only contain the error

# ----------------------------------------------------------------------------
# Listing users
#
# TODO: pagination
# ----------------------------------------------------------------------------

# TODO: add more user and test default pagination
Scenario: Listing users
    Given I'm an admin
    And I have a valid token
    When I retrieve the list of users
    Then I should get a '200' response
    And The list should contain all the users for page 1
    And The list should not contain passwords

Scenario: Listing users by page
    Given I'm an admin
    And I have a valid token
    And I set the page to 2
    When I retrieve the list of users
    Then I should get a '200' response
    And The list should contain all the users for page 2

# ----------------------------------------------------------------------------
# Password recovery
#
# TODO: mail mocking
# TODO: password reset
# TODO: mail is invalid?
# ----------------------------------------------------------------------------
Scenario: Password recovery
    Given: I'm an active user
    When I request a new password
    Then I should get a '200' response
    And The response should contain the following non-empty fields: "msg"
    And I should receive an email
    # TODO: check the email, using a mock?

Scenario: Password reset
    Given I'm an active user
    And I have a recovery token
    When I visit the recovery link with my token
    Then I should get a '200' response
    And The response field "msg" should be "Password updated successfully"
    And I should receive an email

Scenario: Password reset with an invalid token
    Given I'm an active user
    And I have an invalid recovery token
    When I visit the recovery link with my token
    Then I should get a '400' response
    And The response error should contain "Invalid token"
    And The response should only contain the error

Scenario: Password reset with an invalid email
    Given I'm an active user
    And I have a recovery token with an invalid email
    When I visit the recovery link with my token
    Then I should get a '404' response
    And The response error should contain "does not exist"
    And The response should only contain the error

Scenario: Password recovery does not leak information
    Given: I'm a new user
    When I request a new password
    Then I should get a '200' response
    And The response should contain the following non-empty fields: "msg"

# ----------------------------------------------------------------------------
# Deleting accounts
# ----------------------------------------------------------------------------
Scenario: Delete my account
    Given I'm an active user
    And I have a valid token
    When I delete my account
    Then I should get a '204' response
    And The response should be empty

Scenario: Delete an user
    Given I'm an admin
    And I have a valid token
    And I have an active user
    When I delete the user
    Then I should get a '204' response
    And The response should be empty

Scenario: Delete an non existing user
    Given I'm an admin
    And I have a valid token
    When I delete the user by id "9999999999"
    Then I should get a '404' response
    And The response should only contain the error

Scenario: Delete an user without permissions
    Given I'm an active user
    And I have a valid token
    When I delete the user "Tintin"
    Then I should get a '403' response
    And The response should only contain the error

Scenario: Delete an user without a token
    Given I'm an active user
    When I delete the user "Tintin"
    Then I should get a '401' response
    And The response should only contain the error

# Scenario: Delete an user verification
#     Given I'm an admin
#     And I have a valid token
#     And I have deleted the user "2"
#     When I retrieve the user by id "2"
#     Then I should get a '404' response
