---
name: weekly-review
description: Conduz a revisão semanal do GTD em ~15 minutos e produz a nota da semana (logs/Resumos/YYYY-Www.md). Processa o inbox, verifica objetivos e projetos, resume a semana a partir dos diários, sugere links e faz commit. Use para "revisão semanal", "fecha a semana", "review" ou quando detectar semana encerrada sem nota.
metadata:
  last-updated: 2026-10-04 00:51 UTC
  version: 1.0.0
  category: utility
  context_budget: heavy
  references: []
---

> Overview: see [./SKILL-quickguide.md](./SKILL-quickguide.md)

# weekly-review

"Revisão rima com versão." O usuário responde perguntas; você faz o bookkeeping. Ao final existe uma
nota da semana e um commit.

## Convenção
- Antes de escrever, confira a estrutura de `logs/` (diários em `logs/YYYY/`, resumos em
  `logs/Resumos/`). Diários fora do padrão são corrigidos (com confirmação) antes de serem resumidos,
  senão o resumo linka para caminhos que vão mudar.
- Caminho: `logs/Resumos/YYYY-Www.md`, semana ISO (segunda a domingo). Ex.: `2026-W40.md`.
- Frontmatter: `tipo: resumo-semanal`, `periodo: YYYY-Www`, `inicio: YYYY-MM-DD`, `fim: YYYY-MM-DD`,
  `origem: assistente`, `tags: []`.
- A nota linka para todos os diários da semana. O que não está no resumo continua nos diários; o
  resumo não substitui.

## Passos (nesta ordem; pare em cada pergunta)

Inbox → objetivos e projetos → diários → nota da semana → links → índices → commit.

1. **Delimite a semana.** Por padrão, a semana ISO corrente (ou a anterior, se hoje é segunda). Diga as
   datas. Verifique se a nota já existe; se sim, ofereça atualizar em vez de recriar.
2. **Inbox** → invoque `process-inbox`. Se o inbox está vazio, diga e siga.
3. **Objetivos e projetos.** Para cada objetivo em `Objetivos.md`:
   - O status e o próximo passo ainda são verdade? Atualize `Última movimentação` só nos que de fato se
     moveram; os parados há mais de 14 dias ficam visíveis, sem julgamento. Não crie objetivos; pergunte.
   Para cada projeto do seu arquivo (use `index.md` para localizá-los):
   - Tem próximo passo definido? Se não, pergunte (lógica de `next-action`).
   - Terminou? → proponha arquivar (histórico git preserva; Q2) com uma nota de fechamento de 3 linhas.
   - Parado há >14 dias? → mencione; pergunte se continua projeto, vira referência ou é arquivado.
   Faça tudo em uma rodada de perguntas, não uma por projeto.
4. **Leia os diários da semana** (`logs/YYYY/YYYY-MM-DD.md` no intervalo). Se não houver diários, use
   `git log --since` e as notas modificadas na semana como matéria-prima, e diga que o resumo está
   baseado nisso.
5. **Escreva a nota da semana** no formato abaixo. Regras:
   - Cada afirmação linka para o diário ou nota de origem.
   - Decisões e aprendizados vêm dos callouts `[!decision]` e `[!learning]` dos diários, mais o que o
     usuário disser agora.
   - Seção **Fora do resumo**: liste em uma linha cada o que você leu e deixou de fora. Perda por
     compressão fica visível.
6. **Conexões.** Proponha até 3 `[[links]]` entre notas tocadas nesta semana e notas antigas, citando o
   trecho que justifica cada um. O usuário aceita ou recusa; aplique só os aceitos.
7. **Atualize** `index.md` (nota da semana + o que foi movido) e `logs/log.md`:
   `## [YYYY-MM-DD] skill | weekly-review: YYYY-Www (N inbox, P projetos, A arquivados)`.
8. **Commit**: `git add -A && git commit -m "Revisão semanal YYYY-Www"`. Ofereça push.
9. **Feche** em 3 linhas: o que mudou, o próximo passo mais urgente, quando é a próxima revisão.

## Formato da nota

Use `Templates/Resumo semanal.md` (preencha os campos `{{date:...}}` com o período revisado, não com
hoje). Se o template não existir, use o formato em `references/nota-semanal.md`.

## O que esta skill não faz
- Não pula etapas para ganhar tempo. Se o usuário tem 5 minutos, faça só o passo 2 e diga que a
  revisão ficou incompleta.
- Não arquiva, descarta ou reescreve sem confirmação.
- Não escreve o resumo com opinião própria sobre a semana. Padrões e travas vêm do que está registrado
  ou do que o usuário disse.
