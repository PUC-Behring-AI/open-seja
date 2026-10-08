# language: pt
Funcionalidade: Gerenciar tarefas

  @REQ-task-list-001
  Cenário: Acrescentar uma tarefa
    Dado que a lista de tarefas está vazia
    Quando eu acrescento a tarefa "tarefa de compras"
    Então a lista mostra a tarefa "tarefa de compras" como pendente

  @REQ-task-list-001
  Esquema do Cenário: Acrescentar tarefas de nomes diferentes
    Dado que a lista de tarefas está vazia
    Quando eu acrescento a tarefa "<titulo>"
    Então a lista mostra a tarefa "<titulo>" como pendente

    Exemplos:
      | titulo           |
      | tarefa de estudo |
      | tarefa de casa   |

  @REQ-task-list-002
  Cenário: Marcar uma tarefa como feita
    Dado que a lista tem a tarefa pendente "tarefa de compras"
    Quando eu marco a tarefa "tarefa de compras" como feita
    Então a lista mostra a tarefa "tarefa de compras" como feita

  @REQ-task-list-002 @skip
  Cenário: Desfazer a marcação de uma tarefa
    Dado que a lista tem a tarefa feita "tarefa de compras"
    Quando eu desfaço a marcação da tarefa "tarefa de compras"
    Então a lista mostra a tarefa "tarefa de compras" como pendente
