---
slug: task-list
status: approved
approved_at: 2026-10-06T15:00Z
approved_by: usuario
scenarios: approved
serve: [JM-TB-001]
---

<!-- Exemplo fictício do plan-000010: nenhum dado real, nenhum nome de pessoa ou de organização. -->

# Lista de tarefas

## Nas suas palavras

Pedido:

- F1: "Quero anotar o que preciso fazer."
- F2: "Quero marcar o que já fiz."
- F3: "Não precisa de prazo nem de lembrete."

Respostas na entrevista:

- A1 (rodada 1): "Sou eu que uso, no computador. Não sei programar."
- A2 (rodada 1): "Se eu marcar por engano, quero desfazer."

## Requisitos

| REQ | Tipo | Nas suas palavras | Requisito | Critério | Para que | rev | Estado |
|---|---|---|---|---|---|---|---|
| REQ-task-list-001 | comportamento | F1, A1 | Você acrescenta uma tarefa à lista. | Quando você acrescenta uma tarefa, o sistema mostra a tarefa na lista como pendente. | Você não esquece o que precisa fazer. | 1 | ativo |
| REQ-task-list-002 | comportamento | F2, A2 | Você marca uma tarefa como feita e pode desfazer. | Quando você marca uma tarefa como feita, o sistema mostra a tarefa como feita e oferece desfazer. | Você sabe o que já fez. | 1 | ativo |

## Dimensões

| Dimensão | Resposta | Fonte |
|---|---|---|
| quem | Uma pessoa que anota as próprias tarefas no computador. Ela não programa. | A1 |
| o que faz | Acrescentar tarefas e marcar as que fez. | F1, F2 |
| gatilho | A pessoa abre a lista. | A1 |
| resultado | A lista mostra cada tarefa como pendente ou feita. | F1, F2 |
| não faz | fora do escopo: prazo e lembrete não entram | F3 |
| erros e limites | Marcar por engano se desfaz. | A2 |

## Modelo e termos

| Termo | O que quer dizer | Fonte |
|---|---|---|
| tarefa | Algo que você precisa fazer. | F1 |
| lista | Onde você vê as tarefas. | F1 |
| pendente | Tarefa que você ainda não fez. | F2 |
| feita | Tarefa que você marcou como feita. | F2 |

## Fora do escopo

- Prazo e lembrete (F3). Motivo: o pedido diz que não precisa.

## Premissas

| Premissa | Fonte | Confirmado |
|---|---|---|
| Há uma única lista por pessoa. | A1 | sim |

## Perguntas abertas

- nenhuma

## Mudanças

| Data | REQ | O que mudou | rev |
|---|---|---|---|
