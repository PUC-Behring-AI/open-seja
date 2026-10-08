Feature: Entrar

  @REQ-login-001
  Scenario: Entrar com a senha certa
    Given o usuário tem uma conta
    When o usuário informa a senha certa
    Then o sistema abre a conta
