Feature: Entrar

  Background:
    Given o usuário abre a página
    And o usuário tem uma conta
    And o usuário tem uma senha
    And o usuário tem uma sessão

  @REQ-login-001
  Scenario: Dois comportamentos
    Given o usuário tem uma conta nova
    When o usuário informa a senha certa
    Then o sistema abre a conta
    When o usuário pede para sair
    Then o sistema fecha a conta

  @REQ-login-001
  Scenario: Cenário comprido
    Given o usuário tem uma conta antiga
    And o usuário tem a senha 1
    And o usuário tem a senha 2
    And o usuário tem a senha 3
    And o usuário tem a senha 4
    And o usuário tem a senha 5
    When o usuário informa a senha certa
    Then o sistema abre a conta
    And o sistema mostra a página inicial
    And o sistema mostra o nome do usuário
    And o sistema mostra a sessão
