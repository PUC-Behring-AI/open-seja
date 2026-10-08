Feature: Login

  Scenario: Log in
    Given a user
    When they log in
    Then they see the home page
