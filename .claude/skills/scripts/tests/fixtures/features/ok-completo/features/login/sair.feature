# language: pt
Funcionalidade: Sair da conta

  Regra: Jornada de saída (JM-TB-001)

    @REQ-login-002
    Cenário: Pedir para sair
      Dado que o usuário está na conta
      Quando o usuário pede para sair
      Então o sistema pede a confirmação

    @REQ-login-002
    Cenário: Confirmar a saída
      Dado que o usuário pediu para sair
      Quando o usuário confirma
      Então o sistema fecha a conta
