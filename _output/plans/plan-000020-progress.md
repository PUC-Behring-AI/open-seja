# Progress -- Plan 000020

Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

## Codebase Patterns
<!-- Subagents consolidate reusable patterns here -->

## Iteration Log

### Plan -- reflection-on-action | 2026-10-07 00:21 UTC | PKB inbox automatico, as-expressed em H-005, release v0.11.0 e upgrade do Doutourado
- happened: Plano unico com 13 steps (12 + split 7a/7b) em tres frentes: camada PKB (template + pkb_inbox.py init/capture/digest + post-skill 7f), rascunho para o /design (H-005 as-expressed, Q-014, limiar) e release + upgrade cross-repo. Revisao deep com 6 deep-dives e 10 emendas aplicadas.
- deviated: O brief pedia a tag v0.10.1; o plano publica v0.11.0 (funcionalidade nova = MINOR; v0.10.x nunca foi taggeado) e deixa o caminho de dois releases como alternativa. As 5 skills PKB ficam so no template (nao entram no .claude/skills do open-seja) depois da revisao ARCH. O interruptor da captura passou de 'existe inbox/' para 'PKB_DIR nao vazio e inbox/README.md existe'. A emenda a H-005 nao e aplicada pelo agente: vira rascunho + pendencia para o /design (T4).
- less-sure: Se o designer aceita a excecao de i18n (SKILL.md PKB em pt-BR no main); se o residuo as-expressed vs brief e um sinal util ou so ruido antes de haver limiar fixado; se o upgrade do Doutourado com o script antigo (v0.9.1) se comporta como previsto no dry-run.
- gate: not-applicable
- communication: declined
