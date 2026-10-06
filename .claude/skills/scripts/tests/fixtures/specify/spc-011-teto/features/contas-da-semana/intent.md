---
slug: contas-da-semana
status: approved
approved_at: 2026-10-06T14:20Z
approved_by: usuario
serve: [JM-TB-001]
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

- A1 (rodada 1): "Sou eu mesmo que uso, no celular. Sei usar aplicativo de banco, mas não sei programar."
- A2 (rodada 1): "Semana é de hoje até daqui a sete dias."
- A3 (rodada 2): "Se a lista da semana aparece quando eu abro, já me lembra. Aviso no celular não precisa."
- A4 (rodada 2): "Umas quinhentas contas no ano, mais ou menos."
- A5 (rodada 2): "Se eu marcar paga por engano, quero desfazer."

## Requisitos

| REQ | Tipo | Nas suas palavras | Requisito | Critério | Para que | rev | Estado |
|---|---|---|---|---|---|---|---|
| REQ-contas-da-semana-001 | comportamento | F1, A2 | Você vê as contas que vencem nos próximos 7 dias. | Quando você abre a tela inicial, o sistema mostra as contas que vencem nos próximos 7 dias. | Você sabe o que pagar nesta semana. | 1 | ativo |
| REQ-contas-da-semana-002 | comportamento | F2, A5 | Você marca uma conta como paga e pode desfazer. | Quando você marca uma conta como paga, o sistema tira a conta da lista da semana e mostra a opção de desfazer. | Você não paga a mesma conta duas vezes. | 1 | ativo |
| REQ-contas-da-semana-003 | restrição | F5, A4 | A lista abre sem espera longa, mesmo com muitas contas. | Quando você abre a tela inicial com 500 contas cadastradas, o sistema mostra a lista em até 2 segundos. | Você não desiste de abrir a lista. | 1 | ativo |

## Dimensões

| Dimensão | Resposta | Fonte |
|---|---|---|
| quem | Uma pessoa que paga as próprias contas pelo celular. Ela usa aplicativo de banco e não programa. | A1 |
| o que faz | Ver as contas da semana e marcar as que pagou. | F1, F2 |
| gatilho | A pessoa abre o aplicativo. | A3 |
| resultado | A tela inicial mostra as contas dos próximos 7 dias, sem as pagas. | F1, A2 |
| não faz | fora do escopo: a pessoa paga as contas no banco, não no aplicativo | F4 |
| erros e limites | Marcar como paga por engano se desfaz. A lista abre em até 2 segundos com 500 contas. | A5, A4 |

## Modelo e termos

| Termo | O que quer dizer | Fonte |
|---|---|---|
| conta | Um valor a pagar com uma data de vencimento. | F1 |
| semana | De hoje até daqui a 7 dias. | A2 |
| paga | Conta que você marcou como paga. | F2 |

## Fora do escopo

- Pagar a conta pelo aplicativo (F4). Motivo: a pessoa paga no banco.
- Aviso no celular antes do vencimento (F3). Motivo: "a lista da semana já me lembra" (A3).

## Premissas

| Premissa | Fonte | Confirmado |
|---|---|---|
| A lista da semana conta a partir do dia de hoje, não a partir de segunda-feira. | A2 | sim |

## Perguntas abertas

- nenhuma

## Retradução

rev: 5

Eu entendi que você quer saber o que pagar nesta semana. Você paga no banco, não no aplicativo.

- Eu mostro as contas que vencem nos próximos 7 dias, para que você saiba o que pagar nesta semana. (REQ-contas-da-semana-001)
  - Exemplo: hoje é segunda-feira. A conta de luz vence na quarta e a de água no mês que vem. Você abre o aplicativo e vê só a de luz.
- Eu tiro da lista a conta que você marca como paga e deixo você desfazer, para que você não pague duas vezes. (REQ-contas-da-semana-002)
  - Exemplo: você marca a conta de luz como paga e ela sai da lista. Você percebe o engano, escolhe desfazer, e ela volta.
- Eu abro a lista em até 2 segundos, mesmo com 500 contas, para que você não desista de abrir. (REQ-contas-da-semana-003)
  - Exemplo: você tem as contas de um ano inteiro cadastradas. Você abre o aplicativo e a lista aparece antes de você contar até 3.

O que eu não vou fazer:

- Eu não pago a conta pelo aplicativo. Você continua pagando no banco. (F4)
- Eu não mando aviso no celular antes do vencimento. A lista da semana já lembra você. (F3)

## Mudanças

| Data | REQ | O que mudou | rev |
|---|---|---|---|
| 2026-10-06 | - | Retradução rev 2: ajuste do exemplo. | - |
| 2026-10-06 | - | Retradução rev 3: ajuste do exemplo. | - |
| 2026-10-06 | - | Retradução rev 4: ajuste do exemplo. | - |
| 2026-10-06 | - | Retradução rev 5: ajuste do exemplo. | - |
