# Progress -- Plan 000019

Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

## Codebase Patterns
<!-- Subagents consolidate reusable patterns here -->

## Iteration Log

### Plan -- reflection-on-action | 2026-10-06 23:32 UTC | Upgrade multi-dev: identidade por ULID, gramatica aditiva e verificador
- happened: Plano de 11 steps escrito a partir da research-000018 (R2-1..R2-3) e de D-005; revisao deep com 6 deep-dives (DATA, SEC, ARCH, COMPAT, TEST, DX) emendou o plano para 13 steps.
- deviated: Do brief ao plano: o author do registro de nascimento deixou de ser o nome da pessoa (constituicao C2) e virou token pseudonimo; o ID visivel passou a derivar a data do proprio ULID; tres regexes de QA companheiro e o --finalize entraram no Step 3; CHANGELOG ganhou nota de upgrade; dois steps foram divididos para caber em 5 arquivos.
- less-sure: Se 6 chars do ULID bastam a longo prazo (P(colisao/dia) ~ n^2/2^31) ou se o sufixo deve crescer; se o estreitamento de 'autor' em D-005 deve ser registrado via /design; se o bump do CHANGELOG deve ser minor ou major.
- gate: not-applicable
- communication: _output/communication/2026-10-07/communication-000021-end-users.md (USR)
