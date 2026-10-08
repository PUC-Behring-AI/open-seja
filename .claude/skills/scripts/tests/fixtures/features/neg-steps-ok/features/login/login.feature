Feature: Dois cenários, mesmo step

  @REQ-login-001
  Scenario: Entrar uma vez
    Given o usuário tem uma conta
    When o usuário informa a senha certa
    Then o sistema abre a conta

  @REQ-login-002
  Scenario: Entrar de novo
    Given o usuário tem uma conta
    When o usuário informa a senha "9" certa
    And o usuário informa a senha "7" certa
    Then o sistema abre a conta
    And o sistema registra a sessão
