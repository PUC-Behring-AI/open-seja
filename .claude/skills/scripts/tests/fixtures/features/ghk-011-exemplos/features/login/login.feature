Feature: Entrar

  @REQ-login-001
  Scenario Outline: Sem exemplos
    Given o usuário tem uma conta
    When o usuário informa a senha certa
    Then o sistema abre a conta

  @REQ-login-001
  Scenario Outline: Exemplos vazios
    Given o usuário tem uma conta
    When o usuário informa a senha <senha>
    Then o sistema abre a conta

    Examples:
      | senha |
