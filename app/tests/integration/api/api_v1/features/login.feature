@integration
Feature: Login
    As a user
    I want to be able to login an logout
    So that I can use the API safely

Background:
    Given Some users are in the system
    And The server is set to not check corrupted passwords
    And The server is set to not check special chars in passwords
    And I have a smtp server running


# ----------------------------------------------------------------------------
# Login
# ----------------------------------------------------------------------------
Scenario: Verifying a token
    Given I'm an active user
    And I have a valid token
    When I verify my token
    Then I should get a '200' response
    And The following user fields should match: "email"
    And I should not be admin

Scenario: Verifying a token with an invalid email
    Given I'm an active user
    And I have a token with an invalid id
    When I verify my token
    Then I should get a '404' response
    And The response error should contain "not found"
    And The response should only contain the error

# TODO
# Scenario: Verifying a token with an inactive user
#     Given I'm an active user
#     And I have a valid token
#     And My account gets disabled
#     When I verify my token
#     Then I should get a '400' response
#     And The response error should contain "inactive user"
#     And The response should only contain the error

Scenario: Verifying an invalid token
    Given I'm an active user
    And I have an invalid token
    When I verify my token
    Then I should get a '401' response
    And The response should only contain the error

Scenario: Verifying an expired token
    Given I'm an active user
    And I have an expired token
    When I verify my token
    Then I should get a '401' response
    And The response should only contain the error

Scenario: Verifying an admin token
    Given I'm an admin
    And I have a valid token
    When I verify my token
    Then I should get a '200' response
    And The following user fields should match: "email"
    And I should be admin

Scenario: Login as a user
    Given I'm an active user
    When I request a token
    Then I should get a '200' response
    And The response should contain the following non-empty fields: "access_token, token_type"

# TODO: verify the response does not contain the password
# TODO: verify email is sent
Scenario: Get a temporary password
    Given I'm an active user
    When I request a temporary password
    Then I should get a '200' response
    And I should receive an email

# Verify we don't leak information about existing accounts
# TODO: check no email is send?
Scenario: Get a temporary password with an invalid email
    Given I'm a new user
    When I request a temporary password
    Then I should get a '200' response
    And I should not receive an email

# TODO: create fixtures with and without passwords
# Scenario: Get a temporary password with a password set
#     Given I'm an active user
#     When I request a temporary password
#     Then I should get a '200' response
#     And I should not receive an email

Scenario: Login as a user with temporary password
    Given I'm an active user
    And I have a temporary password
    When I request a token
    Then I should get a '200' response
    And The response should contain the following non-empty fields: "access_token, token_type"

Scenario: Login as an admin
    Given I'm an admin
    When I request a token
    Then I should get a '200' response
    And The response should contain the following non-empty fields: "access_token, token_type"

Scenario: Login as a user with invalid data
    Given I'm an active user
    When I request a token with invalid data
    Then I should get a '400' response
    And The response error should contain "Incorrect email"
    And The response should only contain the error

Scenario: Login as an inactive user does not leak information
    Given I'm an inactive user
    When I request a token
    Then I should get a '400' response
    And The response error should contain "Incorrect email"
    And The response should only contain the error
