---
name: next-action
description: Encontra o próximo passo concreto quando o usuário está travado ou pergunta o que fazer agora. Varre os objetivos e os projetos ativos e devolve uma única ação, não uma lista. Use para "o que eu faço agora", "estou travado", "por onde começo" ou quando um projeto está sem próximo passo.
metadata:
  last-updated: 2026-10-04 00:51 UTC
  version: 1.0.0
  category: utility
  context_budget: light
  references: []
---

> Overview: see [./SKILL-quickguide.md](./SKILL-quickguide.md)

# next-action

O GTD trava quando um projeto não tem próxima ação definida. Esta skill acha a ação, ou acha o projeto
que precisa de uma.

## Passos

1. **Leia** `Objetivos.md` e as notas-raiz dos projetos do seu arquivo (uma por projeto; use `index.md`
   para localizá-las). Não leia o conteúdo inteiro das pastas.
2. **Para cada objetivo/projeto ativo**, extraia: próximo passo declarado, prazo, data da última
   modificação (`git log -1 --format=%cs -- <arquivo>`).
3. **Se o usuário nomeou um projeto**, restrinja a ele.
4. **Escolha uma ação**, nesta ordem de prioridade:
   1. Projeto com prazo mais próximo que tem próximo passo definido → devolva esse passo.
   2. Projeto **sem** próximo passo → esse é o problema. Pergunte: "qual é a menor coisa que move
      `[[projeto]]`?" Ajude a formular até caber em uma frase que começa com verbo e pode ser feita em
      uma sentada. Registre no `Objetivos.md` ou na nota do projeto.
   3. Projeto parado há mais tempo (sem commit há >14 dias) → devolva o próximo passo dele e diga há
      quanto tempo está parado, sem julgamento.
5. **Responda com uma ação só**, no formato: `Próximo passo: <verbo + objeto> (projeto [[X]], prazo Y).`
   Se o usuário quiser a lista completa, ele pede.
6. Se o usuário disse que está travado *nesse* passo, quebre-o: "qual é a primeira metade disso?" até
   chegar em algo que ele diga "isso eu consigo agora".
7. Se hoje tem nota de diário (`logs/YYYY/YYYY-MM-DD.md`), acrescente a ação escolhida na seção
   **Próximo passo** dela. Se não tem, não crie.
8. **Registre** em `logs/log.md` só quando alterou uma nota de objetivo/projeto:
   `## [YYYY-MM-DD] skill | next-action: definido próximo passo de <projeto>`.

## O que esta skill não faz
- Não devolve lista de tarefas. Uma ação.
- Não cria projetos nem move notas. Se descobrir que um "projeto" é na verdade uma área ou já terminou,
  diga e sugira tratar na revisão semanal.
- Não dá conselho genérico ("organize seu tempo"). Se não há informação suficiente, pergunta.
