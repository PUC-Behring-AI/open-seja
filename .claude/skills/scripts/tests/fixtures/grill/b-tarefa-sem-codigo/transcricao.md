# Transcrição simulada -- (b) tarefa sem código

> **Simulada.** Entrevista fictícia escrita pelo executor do plan-000009. Nenhuma pessoa real respondeu. Nenhum dado real.

Brief (verbatim): "Atualize o README do projeto de exemplo para explicar como instalar."

Classificação (GRL-012): tarefa sem código (documentação). Nenhum step terá `Tests:` não-N/A. A grill roda curta, sem slug, sem pasta `features/`, sem REQ IDs.

## Entrevista curta (1 rodada, 4 perguntas) -> seção `## Intenção` em `plano-trecho.md`

1. Agente: "Para que serve esta mudança?" -- Citizen: "Quem chega no projeto não sabe instalar."
2. Agente: "No fim, o que você vê?" -- Citizen: "Uma seção Instalação no README com os passos."
3. Agente: "O que isto não deve fazer?" -- Citizen: "Não mexe no código nem no resto do README."
4. Agente: "Como você sabe que está pronto?" -- Citizen: "Alguém novo segue os passos e instala sem me perguntar."

A aprovação vai junto com a aprovação do plano (mesmo AskUserQuestion). `check_intent.py` não se aplica: não há `intent.md`. A varredura sem argumento num projeto sem `features/` sai 0.

Contagem: 1 rodada, 4 perguntas.
