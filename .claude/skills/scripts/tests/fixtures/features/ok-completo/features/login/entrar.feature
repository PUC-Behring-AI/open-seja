Feature: Entrar e sair

  Background:
    Given o usuário está na página inicial
    And o usuário tem uma conta

  @REQ-login-001 @REQ-login-002
  Scenario: Entrar com a senha certa
    When o usuário informa a senha certa
    Then o sistema abre a conta

  @REQ-login-003
  Scenario Outline: Recusar a senha errada
    When o usuário informa a senha <senha>
    Then o sistema recusa a senha com a mensagem <mensagem>

    Examples:
      | senha | mensagem |
      | curta | pequena  |
      | vazia | falta    |
      | velha | antiga   |

  @REQ-login-003 @nao-faz
  Scenario: Não entrar com conta de terceiros
    When o usuário informa a senha de outra conta
    Then o sistema não abre a conta
