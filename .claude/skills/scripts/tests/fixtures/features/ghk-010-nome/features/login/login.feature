Feature: Entrar e sair

  @REQ-login-001
  Scenario: Entrar com a senha certa
    Given o usuário tem uma conta
    When o usuário informa a senha certa
    Then o sistema abre a conta

  @REQ-login-002
  Scenario: Entrar com a senha certa
    Given o usuário está na conta
    When o usuário pede para sair
    Then o sistema fecha a conta
