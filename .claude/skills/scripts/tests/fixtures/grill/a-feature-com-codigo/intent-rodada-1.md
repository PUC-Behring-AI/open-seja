---
slug: reserva-de-sala
status: grilling
serve: []
---

# Reserva de sala

## Nas suas palavras

Pedido:

- F1: "Quero reservar uma sala de reunião pelo celular."
- F2: "Não quero reservar uma sala que já está ocupada."
- F3: "Quero cancelar a minha reserva."

Respostas na entrevista:

- A1 (rodada 1): "Serve."
- A2 (rodada 1): "Qualquer pessoa da equipe. Todo mundo usa o celular, ninguém programa."
- A3 (rodada 1): "Ela abre a lista de salas e escolhe um horário."
- A4 (rodada 1): "A reserva aparece em minhas reservas."

## Requisitos

| REQ | Tipo | Nas suas palavras | Requisito | Critério | Para que | rev | Estado |
|---|---|---|---|---|---|---|---|
| REQ-reserva-de-sala-001 | comportamento | F1, A3, A4 | Você reserva uma sala livre para um horário. | Quando você escolhe uma sala livre e um horário, o sistema mostra a reserva em minhas reservas. | Você garante a sala antes da reunião. | 1 | ativo |
| REQ-reserva-de-sala-002 | comportamento | F3 | Você cancela uma reserva sua. | Quando você cancela uma reserva sua, o sistema tira a reserva de minhas reservas. | A sala fica livre para outra pessoa. | 1 | ativo |

## Dimensões

| Dimensão | Resposta | Fonte |
|---|---|---|
| quem | Uma pessoa da equipe que usa o celular e não programa. | A2 |
| o que faz | Reservar e cancelar uma sala de reunião. | F1, F3 |
| gatilho | A pessoa abre a lista de salas e escolhe um horário. | A3 |
| resultado | A reserva aparece em minhas reservas. | A4 |
| não faz |  |  |
| erros e limites |  |  |

## Modelo e termos

| Termo | O que quer dizer | Fonte |
|---|---|---|
| sala | Uma sala de reunião que se reserva por horário. | F1 |

## Fora do escopo

## Premissas

| Premissa | Fonte | Confirmado |
|---|---|---|

## Perguntas abertas

- Quanto tempo dura uma reserva?

## Mudanças

| Data | REQ | O que mudou | rev |
|---|---|---|---|
