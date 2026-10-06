---
designer_description: "When /plan interviews you about a feature, I'm the shape of the file it writes: your request split into numbered sentences, each requirement with where it came from, what it is for and one sentence that says how you will see it working, plus what stays out, what was assumed and what changed -- so you approve a list you can read and a tool can check."
slug: contas-da-semana
status: approved
approved_at: 2026-10-06T14:20Z
approved_by: usuario
serve: [JM-TB-001]
---

<!--
Modelo de intent.md da fase grill (.claude/references/general/grill-phase.md).
Exemplo fictício completo: nenhum dado real, nenhum nome de pessoa ou de organização.

Esquema mínimo do plan-000007 (feature-layout.md): frontmatter `slug` e `status`;
seções "Nas suas palavras", "Requisitos" (REQ / Texto / Critério), "Fora do escopo", "Premissas".
Tudo o que está marcado "emenda 000009" abaixo é extensão aditiva (decisão pendente 1 = B,
[default; aceito 2026-10-06]): este modelo é um superconjunto do mínimo; um intent.md mínimo
continua válido em check_intent.py sem --require-approved.

Extensões no frontmatter (emenda 000009): approved_at, approved_by, serve. `serve:` aceita IDs do as-intended (`REQ-<TIPO>-NNN` em maiúsculas, `JM-TB-NNN`, `D-NNN`); `REQ-<slug>-NNN` de feature (minúsculas) não é alvo de `serve:` e gera warning.
`designer_description` só existe porque este arquivo é uma referência do harness; um intent.md
de projeto não o usa.
-->

# Contas da semana

## Nas suas palavras

<!-- emenda 000009: frases do pedido indexadas (F) e respostas da entrevista indexadas (A).
Texto verbatim: fora da regra de voz. O índice nunca é renumerado. -->

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

<!-- emenda 000009: colunas Tipo, Nas suas palavras, Para que, rev e Estado.
A coluna Texto do mínimo chama-se Requisito aqui; os dois nomes são aceitos. -->

| REQ | Tipo | Nas suas palavras | Requisito | Critério | Para que | rev | Estado |
|---|---|---|---|---|---|---|---|
| REQ-contas-da-semana-001 | comportamento | F1, A2 | Você vê as contas que vencem nos próximos 7 dias. | Quando você abre a tela inicial, o sistema mostra as contas que vencem nos próximos 7 dias. | Você sabe o que pagar nesta semana. | 1 | ativo |
| REQ-contas-da-semana-002 | comportamento | F2, A5 | Você marca uma conta como paga e pode desfazer. | Quando você marca uma conta como paga, o sistema tira a conta da lista da semana e mostra a opção de desfazer. | Você não paga a mesma conta duas vezes. | 1 | ativo |
| REQ-contas-da-semana-003 | restrição | F5, A4 | A lista abre sem espera longa, mesmo com muitas contas. | Quando você abre a tela inicial com 500 contas cadastradas, o sistema mostra a lista em até 2 segundos. | Você não desiste de abrir a lista. | 1 | ativo |

## Dimensões

<!-- emenda 000009: regra de parada P1. Seis linhas, nenhuma vazia. -->

| Dimensão | Resposta | Fonte |
|---|---|---|
| quem | Uma pessoa que paga as próprias contas pelo celular. Ela usa aplicativo de banco e não programa. | A1 |
| o que faz | Ver as contas da semana e marcar as que pagou. | F1, F2 |
| gatilho | A pessoa abre o aplicativo. | A3 |
| resultado | A tela inicial mostra as contas dos próximos 7 dias, sem as pagas. | F1, A2 |
| não faz | fora do escopo: a pessoa paga as contas no banco, não no aplicativo | F4 |
| erros e limites | Marcar como paga por engano se desfaz. A lista abre em até 2 segundos com 500 contas. | A5, A4 |

## Modelo e termos

<!-- emenda 000009: os substantivos no sentido de quem pediu. -->

| Termo | O que quer dizer | Fonte |
|---|---|---|
| conta | Um valor a pagar com uma data de vencimento. | F1 |
| semana | De hoje até daqui a 7 dias. | A2 |
| paga | Conta que você marcou como paga. | F2 |

## Fora do escopo

- Pagar a conta pelo aplicativo (F4). Motivo: a pessoa paga no banco.
- Aviso no celular antes do vencimento (F3). Motivo: "a lista da semana já me lembra" (A3).

## Premissas

<!-- emenda 000009: tabela com Fonte e Confirmado. Regra de parada P3. -->

| Premissa | Fonte | Confirmado |
|---|---|---|
| A lista da semana conta a partir do dia de hoje, não a partir de segunda-feira. | A2 | sim |

## Perguntas abertas

<!-- emenda 000009: regra de parada P3. Vazia ou "nenhuma" para aprovar. -->

- nenhuma

## Mudanças

<!-- emenda 000009: histórico de reentrada (GRL-011). Todo REQ com rev > 1 ou retirado tem linha aqui. -->

| Data | REQ | O que mudou | rev |
|---|---|---|---|
