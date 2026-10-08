---
slug: lista-de-compras
status: approved
approved_at: 2026-10-06T16:30Z
approved_by: usuario
serve: []
---

# Lista de compras

## Nas suas palavras

Pedido:

- F1: "1. Adicionar um item à lista de compras."
- F2: "2. Marcar um item como comprado."
- F3: "3. A lista fica guardada no celular."
- F4: "Não precisa dividir a lista com ninguém."

Respostas na entrevista:

- A1 (rodada 1): "Abro a lista quando estou no mercado."
- A2 (rodada 1): "Não deixa, e pronto."
- A3 (rodada 1): "Isso."

## Requisitos

| REQ | Tipo | Nas suas palavras | Requisito | Critério | Para que | rev | Estado |
|---|---|---|---|---|---|---|---|
| REQ-lista-de-compras-001 | comportamento | F1, A2 | Você adiciona um item à lista. | Quando você escreve um item e confirma, o sistema mostra o item no fim da lista. | Você não esquece o que comprar. | 1 | ativo |
| REQ-lista-de-compras-002 | comportamento | F2 | Você marca um item como comprado. | Quando você toca num item, o sistema mostra o item riscado. | Você vê o que ainda falta. | 1 | ativo |

## Dimensões

| Dimensão | Resposta | Fonte |
|---|---|---|
| quem | Uma pessoa que faz compras com o celular na mão. | F1 |
| o que faz | Adicionar itens e marcar os comprados. | F1, F2 |
| gatilho | A pessoa abre a lista quando chega ao mercado. | A1 |
| resultado | A lista mostra os itens e os comprados riscados. | F1, F2 |
| não faz | fora do escopo: a lista é só sua | F4 |
| erros e limites | Item vazio não entra na lista. | A2 |

## Modelo e termos

| Termo | O que quer dizer | Fonte |
|---|---|---|
| item | Uma coisa a comprar, escrita numa linha. | F1 |

## Fora do escopo

- Dividir a lista com outras pessoas (F4). Motivo: a lista é só sua.

## Premissas

| Premissa | Fonte | Confirmado |
|---|---|---|
| A lista fica só no seu celular, sem conta na internet. | F3, agente, A3 | sim |

## Perguntas abertas

- nenhuma

## Mudanças

| Data | REQ | O que mudou | rev |
|---|---|---|---|
