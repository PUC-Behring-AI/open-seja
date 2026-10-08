Feature: Entrar

  @REQ-login-001
  Scenario: Começar com E
    And o usuário tem uma conta
    When o usuário informa a senha certa
    Then o sistema abre a conta

  @REQ-login-001
  Scenario Outline: Coluna que falta
    Given o usuário tem uma conta
    When o usuário informa a senha <senha>
    Then o sistema responde <resposta>

    Examples:
      | senha |
      | certa |

  @REQ-login-001
  Scenario Outline: Coluna que sobra
    Given o usuário tem uma conta
    When o usuário informa a senha <senha>
    Then o sistema abre a conta

    Examples:
      | senha | extra |
      | certa | nada  |
