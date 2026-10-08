Feature: Sair

  Rule: Sair em duas etapas

    @REQ-login-001
    Scenario: Pedir para sair
      Given o usuário está na conta
      When o usuário pede para sair
      Then o sistema pede a confirmação

  Rule: Entrar (JM-TB-009)

    @REQ-login-001
    Scenario: Informar a senha
      Given o usuário tem uma conta
      When o usuário informa a senha certa
      Then o sistema abre a conta
