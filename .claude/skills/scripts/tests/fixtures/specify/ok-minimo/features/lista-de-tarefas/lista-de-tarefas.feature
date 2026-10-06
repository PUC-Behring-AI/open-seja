# language: pt
Funcionalidade: Lista de tarefas

  @REQ-lista-de-tarefas-001
  Cenário: Acrescentar uma tarefa
    Dado que a lista está vazia
    Quando eu acrescento uma tarefa
    Então a lista mostra a tarefa
