# language: pt
Funcionalidade: Contas da semana

  @REQ-contas-da-semana-001
  Cenário: Ver as contas que vencem nos próximos 7 dias
    Dado que eu tenho uma conta que vence daqui a 3 dias
    E eu tenho uma conta que vence daqui a 10 dias
    Quando eu abro https://app.local/contas
    Então eu vejo a conta que vence daqui a 3 dias
    E eu não vejo a conta que vence daqui a 10 dias

  @REQ-contas-da-semana-003
  Esquema do Cenário: A lista abre logo com muitas contas
    Dado que eu tenho <quantidade> contas cadastradas
    Quando eu abro a tela inicial
    Então eu vejo a lista em até <segundos> segundos

    Exemplos:
      | quantidade | segundos |
      | 100        | 2        |
      | 500        | 2        |
