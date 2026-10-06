@REQ-login-001
Feature: Entrar

  @REQ-login-001 @REQ-login-1
  Scenario: Entrar com a senha certa
    Given o usuário tem uma conta
    When o usuário informa a senha certa
    Then o sistema abre a conta

  @REQ-login-001 @REQ-outro-001
  Scenario: Entrar de outro modo
    Given o usuário está na conta
    When o usuário pede para sair
    Then o sistema fecha a conta
