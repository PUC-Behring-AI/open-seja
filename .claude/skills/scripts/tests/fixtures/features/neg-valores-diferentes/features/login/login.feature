Feature: Valores diferentes

  @REQ-login-001
  Scenario: Primeiro valor
    Given o usuário tem 1 conta
    When o usuário informa a senha certa
    Then o sistema abre a conta

  @REQ-login-002
  Scenario: Segundo valor
    Given o usuário tem 2 conta
    When o usuário informa a senha certa
    Then o sistema abre a conta
