Feature: Entrar e sair

  @REQ-login-002
  Scenario: Mesmo nome
    Given o usuário tem uma conta
    When o usuário informa a senha certa
    Then o sistema abre a conta

