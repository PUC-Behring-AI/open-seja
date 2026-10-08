Feature: Entrar

  @REQ-login-001
  Scenario: Detalhes demais
    Given o usuário abre https://exemplo.test/entrar
    When o usuário preenche o campo #senha
    Then o sistema roda SELECT * FROM contas
    And o sistema grava em dados/contas.json
    And o sistema chama abrir_conta()
