# language: pt
Funcionalidade: Contas da semana

  @REQ-contas-da-semana-001
  Cenário: Ver as contas que vencem nos próximos 7 dias
    Dado que eu tenho uma conta que vence daqui a 3 dias
    E eu tenho uma conta que vence daqui a 10 dias
    Quando eu abro a tela inicial
    Então eu vejo a conta que vence daqui a 3 dias
    E eu não vejo a conta que vence daqui a 10 dias

  @REQ-contas-da-semana-002
  Cenário: Marcar uma conta como paga
    Dado que a lista da semana mostra uma conta a pagar
    Quando eu marco a conta como paga
    Então a conta sai da lista da semana
    E eu vejo a opção de desfazer

  @REQ-contas-da-semana-002 @skip
  Cenário: Desfazer uma conta marcada como paga por engano
    Dado que eu marquei uma conta como paga
    Quando eu escolho desfazer
    Então a conta volta para a lista da semana

  @REQ-contas-da-semana-003
  Esquema do Cenário: A lista abre logo com muitas contas
    Dado que eu tenho <quantidade> contas cadastradas
    Quando eu abro a tela inicial
    Então eu vejo a lista em até <segundos> segundos

    Exemplos:
      | quantidade | segundos |
      | 100        | 2        |
      | 500        | 2        |
