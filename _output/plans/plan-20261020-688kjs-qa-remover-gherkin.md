# QA log | plan-20261020-688kjs | 2026-10-20 21:38 UTC | Linhagem sem Gherkin

## Brief

> quero planejar mudanças no open seja, a partir da minha reflexão recente sobre o gherking. quero remove-lo

## Q&A log

1. **Agente (entrevista, rodada 1):** o que a reflexão concluiu; o que fica no lugar do degrau cenário; alcance da remoção; um plano ou roadmap.
   **Designer:** "Contrato não é mensagem"; "o proprio artefato do plano seja pode ser usado para colocar o conteúdo do intend.md + casos de uso + testes"; "Remover tudo, incluindo legado"; "Plano único".
2. **Agente (rodada 2):** o que acontece com a grill; onde fica a linha com a T3; o que o upgrade faz com `features/`.
   **Designer:** "Grill fica, escreve no plano"; "Também reescrever H-009 e decisões"; "Aviso no upgrade".
3. **Agente:** resumo da intenção para aprovação. **Designer:** "Aprovar".
4. **Agente:** a revisão Deep achou 11 problemas; corrigido, o plano iria a cerca de 24 steps. Roadmap ou plano longo?
   **Designer:** "AO INVÉS de seguir desta forma, porque não voltamos no tempo: olhamos as tags e continuamos de algum lugar de antes do gherking ? precisamos manter o multi dev"; depois, "avaliar esta possibilidade".
5. **Agente:** avaliação: o ponto limpo é `pre-plan-000007` (`6c3e41f`); portar o ULID e a PKB custa resolver cerca de 25 arquivos à mão; a tag `v0.11.0` está em `origin/main`, então é branch nova. Recomendação: voltar e portar.
   **Designer:** "Voltar e portar (Recomendado)".
6. **Designer:** "revise o plano". **Agente:** achados: base melhor em `2b17d27` (a branch do multi-dev sai de `6c3e41f`); o plano v2 com ID ULID não roda no harness da base; dois clientes estão em v0.11.0 e um terceiro em v0.9.1; o upgrade desfaria o desvio do jogo de linguagem no Doutourado; nomes no plano (C2).
7. **Designer:** "eu gostei do experimento do jogo de linguagem. quero trocar o grill também. será que não é melhor somente pegar o multidev + escada requisito + use cases + testes no artefato gerado pelo plan ? acho que fica mais simples."
   **Agente:** sim; perguntou sobre a camada PKB e sobre um ou dois planos.
   **Designer:** "o que exatamente está colocado como camada PKB ? eu instalei por fora no doutourado e já fiz algumas modificações. podemos remover do open-seja para simplificar"; "Um plano só".
8. **Agente:** explicou o que é a camada PKB (plano 20) e que, no Doutourado, `pkb_inbox.py` e o post-skill têm o mesmo hash do v0.11.0; reescreveu o plano (13 steps).
9. **Designer:** "o plano v3 traz ## Intenção, ## Requisitos, ## Casos de uso, ## Retradução e Covers: em cada step; Em cada step do plano ?"
   **Agente:** não; as seções vêm uma vez por plano, e `Covers:` só nos steps com `Tests:` diferente de N/A. O Step 7 foi ajustado.
10. **Designer:** "ok, vmaos commitar".

## Pendente no commit

A terceira revisão Deep voltou antes do commit (a identidade do git faltava); as emendas A1 a A8 foram aplicadas ao plano antes de commitar.

## /implement (2026-10-20 22:35 UTC a 2026-10-21 10:43 UTC)

> /implement plan-20261020-688kjs --manual --skip-checks

1. **Agente** (Step 4): pediu para gravar `<!-- STATUS: proposed | plan-000019 | 2026-10-07 -->` acima de `### D-005` no as-intended do worktree. **Designer:** "Gravar o marcador".
2. **Agente** (Step 6, ponto de parada): mostrou o rascunho `_output/tmp/design-rascunho-d006-2026-10-20.md` (D-006, D-004 superseded, H-009 reescrita, seções derivadas). **Designer:** "Gravar como está".
3. **Agente** (Step 6): listou as 86 linhas que `check_human_markers_only --staged` acusou, todas da reescrita. **Designer:** "Aceito, pode commitar".
4. **Agente** (Step 14): rodou a revisão de código; ela parou uma vez no limite de uso e foi retomada; 3 críticos e 4 advisórios corrigidos no worktree.
5. **Agente** (fechamento): ofereceu medir a deriva. **Designer:** "Seguir sem medir".
