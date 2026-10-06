---
slug: reserva-de-sala
status: approved
approved_at: 2026-10-06T16:10Z
approved_by: usuario
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
- A5 (rodada 2): "Não precisa reservar sala de outro prédio."
- A6 (rodada 2): "Tem que avisar que está ocupada e não reservar."
- A7 (rodada 2): "Tem que ser rápido."
- A8 (rodada 3): "Uns três segundos no máximo."
- A9 (rodada 3): "Está, uma hora."

## Requisitos

| REQ | Tipo | Nas suas palavras | Requisito | Critério | Para que | rev | Estado |
|---|---|---|---|---|---|---|---|
| REQ-reserva-de-sala-001 | comportamento | F1, A3, A4 | Você reserva uma sala livre para um horário. | Quando você escolhe uma sala livre e um horário, o sistema mostra a reserva em minhas reservas. | Você garante a sala antes da reunião. | 1 | ativo |
| REQ-reserva-de-sala-002 | comportamento | F3 | Você cancela uma reserva sua. | Quando você cancela uma reserva sua, o sistema tira a reserva de minhas reservas. | A sala fica livre para outra pessoa. | 1 | ativo |
| REQ-reserva-de-sala-003 | comportamento | F2, A6 | Você não consegue reservar uma sala ocupada. | Quando você escolhe uma sala ocupada naquele horário, o sistema avisa que a sala está ocupada e não faz a reserva. | Duas reuniões não caem na mesma sala. | 1 | ativo |
| REQ-reserva-de-sala-004 | restrição | A7, A8 | A reserva confirma em pouco tempo. | Quando você confirma uma reserva, o sistema mostra a confirmação em até 3 segundos. | Você não fica esperando na tela. | 1 | ativo |

## Dimensões

| Dimensão | Resposta | Fonte |
|---|---|---|
| quem | Uma pessoa da equipe que usa o celular e não programa. | A2 |
| o que faz | Reservar e cancelar uma sala de reunião. | F1, F3 |
| gatilho | A pessoa abre a lista de salas e escolhe um horário. | A3 |
| resultado | A reserva aparece em minhas reservas. | A4 |
| não faz | Não reserva sala de outro prédio. | A5 |
| erros e limites | Sala ocupada não é reservada, e o sistema avisa. A confirmação vem em até 3 segundos. | F2, A6, A8 |

## Modelo e termos

| Termo | O que quer dizer | Fonte |
|---|---|---|
| sala | Uma sala de reunião que se reserva por horário. | F1 |
| ocupada | Sala que já tem reserva naquele horário. | F2, A6 |
| reserva | Uma sala presa para você por uma hora. | F1, A9 |

## Fora do escopo

- Reservar sala de outro prédio (A5). Motivo: a equipe usa só as salas deste prédio.

## Premissas

| Premissa | Fonte | Confirmado |
|---|---|---|
| Uma reserva dura uma hora. | agente, A9 | sim |

## Perguntas abertas

- nenhuma

## Mudanças

| Data | REQ | O que mudou | rev |
|---|---|---|---|
