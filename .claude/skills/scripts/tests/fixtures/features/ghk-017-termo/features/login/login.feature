Feature: Entrar

  @REQ-login-001
  Scenario: Termos fora do modelo
    Given o usuário tem uma conta
    When o usuário abre a Fatura
    Then o sistema mostra "Premium" e "Cobrança"
