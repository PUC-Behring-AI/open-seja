---
slug: contas-da-semana
status: approved
approved_at: 2026-10-06T14:20Z
approved_by: usuario
scenarios: approved
scenarios_approved_at: 2026-10-06T15:00Z
scenarios_approved_by: usuario
scenarios_contract_by: usuario
scenarios_rev: 1
---

# Contas da semana

## Nas suas palavras

Pedido:

- F1: "Quero ver as contas que vencem nesta semana."
- F2: "Quero marcar uma conta como paga."
- F3: "Me avise antes de vencer."
- F4: "Não precisa pagar pelo aplicativo."
- F5: "Tenho muitas contas, então a lista não pode demorar."

Respostas na entrevista:

- A1 (rodada 1): "Sou eu mesmo que uso, no celular."
- A2 (rodada 1): "Semana é de hoje até daqui a sete dias."
- A3 (rodada 2): "A lista da semana já me lembra."
- A4 (rodada 2): "Umas quinhentas contas no ano."
- A5 (rodada 2): "Se eu marcar paga por engano, quero desfazer."

## Requisitos

| REQ | Tipo | Nas suas palavras | Requisito | Critério | Para que | rev | Estado |
|---|---|---|---|---|---|---|---|
| REQ-contas-da-semana-001 | comportamento | F1, A2 | Você vê as contas que vencem nos próximos 7 dias. | Quando você abre a tela inicial, o sistema mostra as contas que vencem nos próximos 7 dias. | Você sabe o que pagar nesta semana. | 1 | retirado |

## Fora do escopo

- Pagar a conta pelo aplicativo (F4). Motivo: a pessoa paga no banco.
- Aviso no celular antes do vencimento (F3). Motivo: "a lista da semana já me lembra" (A3).

## Premissas

| Premissa | Fonte | Confirmado |
|---|---|---|
| A semana conta a partir de hoje. | A2 | sim |

## Retradução

rev: 1

Eu entendi que você quer saber o que pagar nesta semana.

O que eu não vou fazer:

- Eu não pago a conta pelo aplicativo. (F4)
- Eu não mando aviso no celular. (F3)
