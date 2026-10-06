# Transcrição simulada -- (a) feature com código

> **Simulada.** Entrevista fictícia escrita pelo executor do plan-000009 para provar a regra de parada. Nenhuma pessoa real respondeu; o "citizen" é um papel. Nenhum dado real.

Brief (verbatim): "Quero reservar uma sala de reunião pelo celular. Não quero reservar uma sala que já está ocupada. Quero cancelar a minha reserva."

Índice do pedido: F1, F2, F3 (uma frase cada).

Aviso C1 (GRL-005), antes da rodada 1: "Eu vou guardar o seu pedido como você escreveu, numa pasta do projeto. Quem lê o projeto lê o pedido. Quer trocar algum nome por um marcador?" -- Resposta: "Não tem nome nenhum, pode guardar."

## Rodada 1 (4 perguntas) -> `intent-rodada-1.md`

1. Agente: "Eu proponho o nome `reserva-de-sala` para esta feature. Serve?" -- Citizen: "Serve." (A1)
2. Agente: "Quem vai usar isto? O que essa pessoa já sabe fazer sem ajuda?" -- Citizen: "Qualquer pessoa da equipe. Todo mundo usa o celular, ninguém programa." (A2)
3. Agente: "Quando isso começa? O que a pessoa faz primeiro?" -- Citizen: "Ela abre a lista de salas e escolhe um horário." (A3)
4. Agente: "Quando der certo, o que você vê na tela?" -- Citizen: "A reserva aparece em minhas reservas." (A4)

`check_intent.py --require-approved` depois da rodada 1: P1 (não faz, erros e limites sem resposta), P3 (uma pergunta aberta), P6 (não aprovado).

## Rodada 2 (3 perguntas) -> `intent-rodada-2.md`

1. Agente: "O que isto não deve fazer, mesmo que pareça útil?" -- Citizen: "Não precisa reservar sala de outro prédio." (A5)
2. Agente: "O que acontece quando a sala já está ocupada?" -- Citizen: "Tem que avisar que está ocupada e não reservar." (A6)
3. Agente: "Quanto tempo a confirmação pode demorar?" -- Citizen: "Tem que ser rápido." (A7)

O agente propõe que uma reserva dure uma hora; o citizen não sabe ("não sei, acho que sim") e a proposta vira premissa com `Confirmado: não`.

`check_intent.py --require-approved` depois da rodada 2: P2 (critério de REQ-004 com "rápido" sem número), P3 (premissa não confirmada), P6.

## Rodada 3 (2 perguntas) -> `intent-final.md`

1. Agente: "Você disse que a confirmação tem que ser rápida. Em quantos segundos?" -- Citizen: "Uns três segundos no máximo." (A8)
2. Agente: "Eu supus que uma reserva dura uma hora. Está certo?" -- Citizen: "Está, uma hora." (A9)

`check_intent.py --require-approved --strict` depois da rodada 3: nenhum `error`. Resumo mostrado ao citizen (voz controlada):

- Você reserva uma sala livre para um horário. (REQ-reserva-de-sala-001)
- Você cancela uma reserva sua. (REQ-reserva-de-sala-002)
- Você não consegue reservar uma sala ocupada. (REQ-reserva-de-sala-003)
- A reserva confirma em pouco tempo. (REQ-reserva-de-sala-004)
- Não faz: reservar sala de outro prédio.

Citizen escolhe **Aprovar**. O agente grava `status: approved`, `approved_at`, `approved_by: usuario`.

Contagem: 3 rodadas, 9 perguntas, 0 pedidos de reformulação (citizen simulado: dado de calibração **não observado**).
