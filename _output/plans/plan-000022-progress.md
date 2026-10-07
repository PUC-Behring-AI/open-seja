# Progress -- Plan 000022

Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

## Codebase Patterns
<!-- Subagents consolidate reusable patterns here -->

## Iteration Log

### Plan -- reflection-on-action | 2026-10-07 15:51 UTC | specify-switch: interruptor da specify por projeto e escolha por plano
- happened: Plano de 11 steps a partir do adendo 2026-10-07 do roadmap-000006; grill curta (harness) com duas respostas do designer; revisao deep com 6 deep-dives e emendas A1-A6 aplicadas nos Steps.
- deviated: O plano reabre mais que D-009 e CYC-004: tambem D-005, CYC-018, CYC-029 e CYC-033. Steps 4, 5, 8, 9 e 11 passaram a ter Tests reais (a premissa de que o PFS-013 exigia N/A estava errada). O CHANGELOG ja tem a secao v0.11.0 cortada sem tag, entao o Step 11 escreve nela, nao em Unreleased. Antes do plano, foi preciso integrar dev com origin/dev (colisao de D-005 e do contador de IDs).
- less-sure: Nome da flag de desligar (--no-specify ou --without-specify) e sequencia de release com o plan-000020 ficam para o Step 2; a leitura por protocolo de H-009 so e mensuravel no piloto com oraculo.
- gate: not-applicable
- communication: declined

### Step 1 -- reflection-on-action | 2026-10-07 16:03 UTC | Rascunho da revisão para o /design
- happened: Rascunho escrito em _output/tmp com a nova D-NNN que substitui a D-009, a revisão da D-005 em duas formas, o ajuste a H-009 (ITT e por protocolo, mensurável só no piloto com oráculo), o alcance no contrato e no protocolo, e as três decisões do designer.
- deviated: Erro no adendo do roadmap escrito hoje (braço B no lugar de A), corrigido por apensamento (T3).
- less-sure: Se a forma 1 da revisão da D-005 (só citar) basta para quem lê só as decisões.
- gate: not-installed
