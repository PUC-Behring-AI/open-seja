Feature: Saldo

  @REQ-login-001
  Scenario: Ver o saldo
    Given o saldo é 10
    When o usuário abre a conta
    Then o saldo é 10
