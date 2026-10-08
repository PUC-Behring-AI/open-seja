Feature: Entrar

  @REQ-login-001
  Scenario: Entrar uma vez
    Given o usuário tem uma conta
    When o usuário informa a senha certa
    Then o sistema abre a conta

  @REQ-login-001
  Scenario: Entrar outra vez
    Given O usuário tem uma conta.
    When o usuário informa a senha certa
    Then o sistema abre a conta
