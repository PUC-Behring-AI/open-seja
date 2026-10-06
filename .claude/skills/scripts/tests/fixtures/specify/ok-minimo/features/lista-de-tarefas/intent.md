---
slug: lista-de-tarefas
status: approved
approved_at: 2026-10-06T14:20Z
approved_by: usuario
serve: []
---

# Lista de tarefas

## Nas suas palavras

Pedido:

- F1: "Quero anotar o que preciso fazer."

Respostas na entrevista:

- A1 (rodada 1): "Sou eu que uso, no computador."

## Requisitos

| REQ | Tipo | Nas suas palavras | Requisito | Critério | Para que | rev | Estado |
|---|---|---|---|---|---|---|---|
| REQ-lista-de-tarefas-001 | comportamento | F1 | Você acrescenta uma tarefa à lista. | Quando você acrescenta uma tarefa, o sistema mostra a tarefa na lista. | Você não esquece o que precisa fazer. | 1 | ativo |

## Dimensões

| Dimensão | Resposta | Fonte |
|---|---|---|
| quem | Uma pessoa que anota as próprias tarefas no computador. | A1 |
| o que faz | Anotar tarefas. | F1 |
| gatilho | A pessoa escreve uma tarefa. | F1 |
| resultado | A tarefa aparece na lista. | F1 |
| não faz | fora do escopo: a pessoa não pediu nada além de anotar | A1 |
| erros e limites | fora do escopo: a pessoa não citou limite | A1 |

## Modelo e termos

| Termo | O que quer dizer | Fonte |
|---|---|---|
| tarefa | Uma coisa que você precisa fazer. | F1 |

## Fora do escopo

- nenhum

## Premissas

| Premissa | Fonte | Confirmado |
|---|---|---|
| Há uma lista só. | A1 | sim |

## Perguntas abertas

- nenhuma

## Retradução

rev: 1

Eu entendi que você quer anotar o que precisa fazer.

- Eu mostro na lista cada tarefa que você acrescenta, para que você não esqueça. (REQ-lista-de-tarefas-001)
  - Exemplo: você escreve comprar pão e confirma. A lista mostra comprar pão.

O que eu não vou fazer:

- Eu não faço nada além da lista. Você só pediu para anotar. (A1)

## Mudanças

| Data | REQ | O que mudou | rev |
|---|---|---|---|
