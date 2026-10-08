Feature: Entrar

  @REQ-login-001
  Scenario: Entrar duas vezes
    Given o usuário tem uma conta
    And o usuário tem uma conta
    When o usuário informa a senha certa
    Then o sistema abre a conta
