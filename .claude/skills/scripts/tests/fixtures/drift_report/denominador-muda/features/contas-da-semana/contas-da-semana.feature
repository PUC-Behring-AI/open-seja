# language: pt
Funcionalidade: Contas da semana

  @REQ-contas-da-semana-001
  Cenário: Ver as contas que vencem nos próximos 7 dias
    Dado que a lista existe
    Quando eu abro a tela
    Então eu vejo o resultado

  @REQ-contas-da-semana-002
  Cenário: Marcar uma conta como paga
    Dado que a lista existe
    Quando eu abro a tela
    Então eu vejo o resultado

  @REQ-contas-da-semana-002
  Cenário: Desfazer uma conta marcada como paga por engano
    Dado que a lista existe
    Quando eu abro a tela
    Então eu vejo o resultado

  @REQ-contas-da-semana-003
  Esquema do Cenário: A lista abre logo com muitas contas
    Dado que a lista existe
    Quando eu abro a tela
    Então eu vejo o resultado

    Exemplos:
      | quantidade |
      | 100 |
      | 500 |

  @REQ-contas-da-semana-004
  Cenário: Ver o total das contas da semana
    Dado que a lista existe
    Quando eu abro a tela
    Então eu vejo o resultado
