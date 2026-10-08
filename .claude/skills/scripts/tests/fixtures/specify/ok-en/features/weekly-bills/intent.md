---
slug: weekly-bills
status: approved
approved_at: 2026-10-06T14:20Z
approved_by: user
serve: [JM-TB-001]
---

# Weekly bills

## Nas suas palavras

Request:

- F1: "I want to see the bills due this week."
- F2: "I want to mark a bill as paid."
- F3: "I have many bills, so the list must not take long."
- F4: "No need to pay through the app."

Interview answers:

- A1 (round 1): "I use it myself, on my phone. I do not program."
- A2 (round 1): "A week is from today to seven days from now."
- A3 (round 2): "If I mark one as paid by mistake, I want to undo it."

## Requisitos

| REQ | Tipo | Nas suas palavras | Requisito | Critério | Para que | rev | Estado |
|---|---|---|---|---|---|---|---|
| REQ-weekly-bills-001 | comportamento | F1, A2 | You see the bills due in the next 7 days. | When you open the home screen, the system shows the bills due in the next 7 days. | You know what to pay this week. | 1 | ativo |
| REQ-weekly-bills-002 | comportamento | F2, A3 | You mark a bill as paid and can undo it. | When you mark a bill as paid, the system removes it from the weekly list and shows an undo option. | You do not pay the same bill twice. | 1 | ativo |
| REQ-weekly-bills-003 | restrição | F3 | The list opens without a long wait, even with many bills. | When you open the home screen with 500 bills saved, the system shows the list within 2 seconds. | You do not give up opening the list. | 1 | ativo |

## Dimensões

| Dimensão | Resposta | Fonte |
|---|---|---|
| quem | A person who pays their own bills on the phone and does not program. | A1 |
| o que faz | See the bills of the week and mark the paid ones. | F1, F2 |
| gatilho | The person opens the app. | F1 |
| resultado | The home screen shows the bills of the next 7 days. | F1, A2 |
| não faz | fora do escopo: the person pays at the bank | F4 |
| erros e limites | Marking as paid by mistake can be undone. The list opens within 2 seconds with 500 bills. | A3, F3 |

## Modelo e termos

| Termo | O que quer dizer | Fonte |
|---|---|---|
| bill | An amount to pay with a due date. | F1 |
| week | From today to 7 days from now. | A2 |

## Fora do escopo

- Paying the bill through the app (F4). Reason: the person pays at the bank.

## Premissas

| Premissa | Fonte | Confirmado |
|---|---|---|
| The week starts today, not on Monday. | A2 | sim |

## Perguntas abertas

- none

## Retradução

rev: 1

I understood that you want to know what to pay this week.

- I show the bills due in the next 7 days, so that you know what to pay this week. (REQ-weekly-bills-001)
  - Example: today is Monday. The power bill is due on Wednesday and the water bill next month. You open the app and see only the power bill.
- I remove from the list the bill you mark as paid and let you undo it, so that you do not pay twice. (REQ-weekly-bills-002)
  - Example: you mark the power bill as paid and it leaves the list. You notice the mistake, choose undo, and it comes back.
- I open the list within 2 seconds, even with 500 bills, so that you do not give up. (REQ-weekly-bills-003)
  - Example: you have a whole year of bills saved. You open the app and the list shows up before you count to 3.

What I will not do:

- I do not pay the bill through the app. You keep paying at the bank. (F4)

## Mudanças

| Data | REQ | O que mudou | rev |
|---|---|---|---|
