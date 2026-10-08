# Transcrição simulada -- (c) brief já detalhado

> **Simulada.** Entrevista fictícia escrita pelo executor do plan-000009. Nenhuma pessoa real respondeu. Nenhum dado real.

Brief (verbatim, colado com requisitos):

"1. Adicionar um item à lista de compras. 2. Marcar um item como comprado. 3. A lista fica guardada no celular. Não precisa dividir a lista com ninguém."

Índice do pedido: F1 a F4 (um item de lista ou frase cada).

Aviso C1 (GRL-005): o citizen responde "Pode guardar como está."

## Reescrita (antes da rodada de confirmação) -> `intent-rodada-0.md`

O agente reescreve F1 e F2 como requisitos em voz controlada, com critério. F3 vira premissa proposta pelo agente ("a lista fica no próprio celular, sem conta na internet"), ainda sem confirmação. F4 vai para "Fora do escopo". A rodada aponta o que falta em P1 a P5: gatilho e erros e limites.

`check_intent.py --require-approved` sobre a reescrita: P1 (gatilho, erros e limites), P3 (premissa não confirmada), P6.

## Rodada de confirmação (3 perguntas) -> `intent-final.md`

1. Agente: "Quando isso começa? O que você faz primeiro?" -- Citizen: "Abro a lista quando estou no mercado." (A1)
2. Agente: "O que acontece se você tentar adicionar um item vazio?" -- Citizen: "Não deixa, e pronto." (A2)
3. Agente: "Eu supus que a lista fica só no seu celular, sem conta na internet. Está certo?" -- Citizen: "Isso." (A3)

`check_intent.py --require-approved --strict`: nenhum `error`. Citizen escolhe **Aprovar**.

Contagem: 1 rodada, 3 perguntas. D0: F3 não virou requisito nem fora do escopo; ficou só em premissa. A leitura `--d0` o lista com a nota `só em premissa` (DRM-010: leitura, não portão).
