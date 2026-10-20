# Progress -- Plan 000019

Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

## Codebase Patterns
<!-- Subagents consolidate reusable patterns here -->
- Ferramentas: `python3` (nao `python`); pytest e ruff via `uvx --with pyyaml --with markdown pytest .claude/skills/scripts/tests/ -q --ignore=.../test_generate_spo.py --ignore=.../test_generate_spo_design_system.py` e `uvx ruff check`. Baseline: 4 falhas pre-existentes em `test_summarize_artifacts.py` (2026-10-07).
- ID de artefato: importar de `artifact_id` (`ARTIFACT_ID` sem grupo de captura, para embutir em `rf"...({ARTIFACT_ID})..."`; `normalize_id` so faz zfill em numerico <= 6 digitos). Script `library` novo entra em `harness-reference.md` na tabela `### Hook and CI` e no indice alfabetico do fim.

## Iteration Log

### Plan -- reflection-on-action | 2026-10-06 23:32 UTC | Upgrade multi-dev: identidade por ULID, gramatica aditiva e verificador
- happened: Plano de 11 steps escrito a partir da research-000018 (R2-1..R2-3) e de D-005; revisao deep com 6 deep-dives (DATA, SEC, ARCH, COMPAT, TEST, DX) emendou o plano para 13 steps.
- deviated: Do brief ao plano: o author do registro de nascimento deixou de ser o nome da pessoa (constituicao C2) e virou token pseudonimo; o ID visivel passou a derivar a data do proprio ULID; tres regexes de QA companheiro e o --finalize entraram no Step 3; CHANGELOG ganhou nota de upgrade; dois steps foram divididos para caber em 5 arquivos.
- less-sure: Se 6 chars do ULID bastam a longo prazo (P(colisao/dia) ~ n^2/2^31) ou se o sufixo deve crescer; se o estreitamento de 'autor' em D-005 deve ser registrado via /design; se o bump do CHANGELOG deve ser minor ou major.
- gate: not-applicable
- communication: _output/communication/2026-10-07/communication-000021-end-users.md (USR)

### Step 1 -- reflection-on-action | 2026-10-07 18:53 UTC | Criar o modulo artifact_id.py
- happened: artifact_id.py criado (stdlib) com new_ulid, ulid_timestamp, visible_id, regexes LEGACY_ID/ULID_ID/ARTIFACT_ID sem grupo de captura, normalize_id, is_legacy_id/is_ulid_id, default_author (sha256 do user.email, fallback $USER, senao unknown) e birth_record schema_version 1; 24 testes escritos antes, vermelhos por ImportError, depois verdes; linhas acrescentadas nas tabelas Hook and CI e no indice alfabetico de harness-reference.md.
- deviated: Nenhum desvio de escopo. pytest e ruff nao estao no PATH: rodados via uvx (com pyyaml e markdown). ruff pediu check=False explicito no subprocess.run. Suite completa: 1648 passed, 4 failed em test_summarize_artifacts.py, que ja falhavam sem as mudancas deste step.
- less-sure: O plugin harness-reference-coverage ja dava PASS antes de a linha existir, entao a verificacao nao prova que a linha era exigida. ulid_timestamp usa ms/1000 em float; para datas do intervalo atual a precisao de ms basta, mas nao foi testada fora dele.
- gate: not-installed
