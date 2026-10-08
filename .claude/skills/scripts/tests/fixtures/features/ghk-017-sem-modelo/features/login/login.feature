Feature: Entrar

  @REQ-login-001
  Scenario: Entrar com a senha certa
    Given o usuário tem uma conta
    When o usuário abre a Fatura
    Then o sistema abre a conta
