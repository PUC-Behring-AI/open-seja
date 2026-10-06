# Progress -- Plan 000011

Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

## Codebase Patterns
<!-- Subagents consolidate reusable patterns here -->

- Terreno herdado do plan-000007 (ler `_output/plans/plan-000007-progress.md`, secoes "Codebase Patterns", "Step 1" e "Step 7"): repositorio de execucao e este (sem prefixo `open-seja/`); `seja-as-intended.md` -> `product-design/product-design-as-intended.md` (§3); numeracao D-NNN do Doutourado nao vale aqui (D-004 = contrato Gherkin; D-005..D-008 = plan-000007; proximo livre D-009); "D-006 do Doutourado" citada nos planos = D-004 aqui.
- O contrato existe: `.claude/references/general/extended-cycle-contract.md` (CYC-001..026); esquema `features/<slug>/` em `.claude/references/template/feature-layout.md`; formato v2 em `.claude/references/template/plan-step.md`.
- Fixtures do harness ficam em `.claude/skills/scripts/tests/fixtures/<tema>/` (logo `<fixtures>/drift/` = `.claude/skills/scripts/tests/fixtures/drift/`).
- `python3` (nao `python`); pytest via `uvx --with pyyaml pytest ... --ignore=.claude/skills/scripts/tests/test_generate_spo.py --ignore=.claude/skills/scripts/tests/test_generate_spo_design_system.py`.
- Baseline (Q1): `run_all_checks.py` 17 PASS / 14 FAIL (PASS extras: check_intent.py e check_features.py) com contadores 17 undefined (check_conventions), 2 error(s) (check_i18n_keys), 9 error(s) (check_skill_system); pytest 863 passed / 12 failed (apos plans 000009-000010). Rodar `run_all_checks.py` com `timeout 200`, saida em arquivo, nunca dois ao mesmo tempo, nunca checks isolados, nunca `pkill -f`.
- Arquivos do harness: UTF-8, sem travessao tipografico nem aspas curvas; nada de nome de pessoa, parceiro, instituicao ou empresa.
- Portao nao instalado no open-seja: notas com `--gate not-installed`.
- Commits: `git -c user.name=arodrigues-puc-rio -c user.email=arodrigues-puc-rio@users.noreply.github.com commit ...`; nunca `--no-verify`.
- Decisoes pendentes do plano: o designer aceitou todas as recomendacoes em 2026-10-06; marcar como `[default; aceito 2026-10-06]`.
- `run_all_checks.py` deve rodar com `< /dev/null` (sem isso `check_skill_system` pode travar 120 s e dar ERROR; com isso leva ~3,5 s).

- Planos ja entregues neste roadmap: ver a coluna Status da Wave Summary em `_output/roadmaps/roadmap-000006-*.md` e os `## Implementation summary` dos planos DONE; os progress files deles listam lacunas que este plano deve absorver no Step 1.

## Iteration Log

## Step 1 -- terreno e dependencias (2026-10-06, executor)

Decisoes pendentes 1 a 6 aceitas nos defaults (1=A, 2=B, 3=A, 4=A, 5=A, 6=A) `[default; aceito 2026-10-06]`.

| item | resultado |
|---|---|
| (a) planos 000007, 000009, 000010 | existem. `extended-cycle-contract.md` CYC-001..027 (proximo livre **CYC-028**); specify = CYC-003, CYC-004, CYC-006 (`--specify` "reservada"), CYC-007, CYC-008, CYC-013 (degrau x receptor), CYC-014 (teste da surpresa). `grill-phase.md` GRL-001..015 (GRL-014 ainda diz "`--specify` continua reservada"). `gherkin-spec-format.md` GHK-001..019 (3 alem das 16 do plano). `drift-metric.md` ja cita `check_specify.py --status` (DRM-006 `scenario_status` = approved/stale/draft/missing) e `NM-CENARIOS-STALE` (inclusive "REQ editado (`rev` novo)", DRM-013). |
| (b) CLI `check_features.py` | `[root] [--feature <slug>] [--steps <dir>] [--json] [--matrix] [--strict] [--quiet]`; exit 0 sem erro, 1 com erro (ou aviso sob `--strict`), 2 uso/raiz ilegivel/`--feature` sem pasta/falha interna; JSON `schema_version: 1` (`summary`, `findings[{rule,severity,file,line,scenario,message,hint}]`, `features`, `matrix`). Funcoes publicas importaveis: `discover`, `validate`, `build_matrix`, `cited_reqs`, `scenario_key`, `parse_feature`, `load_intent`. |
| (b) CLI `check_intent.py` | `<path> [--require-approved] [--strict] [--json] [--d0]`; sem path varre `features/*/intent.md`. **`--strict` so sai 1 com `error`** (avisos VOZ/TAMANHO/SERVE nao falham). Funcoes publicas: `check_intent(text, require_approved=)`, `parse`, `table`, `ressalvas`, `MAX_SENTENCE_WORDS`, `MAX_SENTENCES_PER_PARAGRAPH`, `VOICE_LINTER`. Le com `utf-8-sig`. |
| (c) chaves extras no frontmatter | **sim, toleradas**: `_parse_frontmatter` le `chave: valor` sem lista fechada; `check_features.load_intent` le so `slug`, `status`, `scenarios`, `serve`. Secao nova `## Retradução` tambem e tolerada (secoes desconhecidas sao ignoradas; so "requisitos" e lida como tabela de REQ). Decisao pendente 1 fica em A. |
| (d) `/plan` | `_internal/plan/standard/SKILL.md` tem o passo **2b Grill phase** (antes do passo 3, criacao do plano); a specify entra como 2c. `plan/SKILL.md`: `--grill [<slug>]` na tabela e na Mode Detection; `--specify` na tabela como "Reserved ... not implemented". |
| (e) voz controlada | `lint_controlled_language.py` **ausente**. Constantes vem de `check_intent` (`MAX_SENTENCE_WORDS = 25`, `MAX_SENTENCES_PER_PARAGRAPH = 6`, ja com o try-import do 000074) e a ressalva `voz: nao verificada` (`check_intent.ressalvas()`). |
| (f) onde moram | scripts `.claude/skills/scripts/`; testes `.claude/skills/scripts/tests/test_<mod>.py` (importam `from check_x import ...`); fixtures `.claude/skills/scripts/tests/fixtures/specify/` (nao `tests/fixtures/specify/`). |
| (g) `run_all_checks.py` | descobre `check_*.py` por glob e roda `python <script>` sem argumentos, `cwd=raiz`, timeout 120 s; nao ha "pulado". O check condicional e o proprio script: `check_specify.py` sem argumentos varre `features/*/` e so reprova `stale` em feature com `scenarios: approved`; sem `features/` imprime "nada a verificar" e sai 0. Logo o registro do Step 7 e automatico (glob) mais a linha em `check_plugin_registry.json`; `run_all_checks.py` nao precisa ser editado. |

Termos de C1 usados nos Steps seguintes (grep case-insensitive sobre os arquivos novos/alterados): `stone`, `tecgraf`, `petrobras`, `puc`, `behring` (o repositorio ja tem `PUC-Behring-AI` em URLs de remote, pre-existente e fora do escopo).

Baseline confirmado: `run_all_checks.py` 17 PASS / 14 FAIL, contadores 17 undefined / 2 error(s) / 9 error(s); pytest 863 passed / 12 failed (`test_html_report` x8, `test_summarize_artifacts` x4). `git status` limpo.

Emenda central aplicada a todos os Steps (D-004 do as-intended; "D-006 do Doutourado" no plano): o citizen aprova a **retradução** em primeira pessoa e os exemplos narrados (a mensagem); o `.feature` e derivado e aprovado como **contrato** por quem le codigo; secao `## Retradução` com `rev` no `intent.md`; "Fora do escopo" sem cenario (SPC-006) mas presente na mensagem; teste da surpresa (CYC-014). Onde o plano mostra o `.feature` ao citizen ("Fluxo da fase", itens 3; Step 2 item 4; Step 5 item 6), vale a emenda; desvio registrado em cada Step.

Conflito de lacuna registrado: o progress do 000010 sugere usar `check_features.py --feature <slug>` sem `--strict` ("avisos sao do power dev"); o plano (SPC-007/SPC-008) usa `--strict`. Sigo o plano: aviso GHK bloqueia a aprovacao (vira SPC-008 aviso); quem resolve e quem le codigo, ao aprovar o contrato. O 000010 tambem diz "cenario `@REQ` de REQ `retirado` nao e erro" (no validador); aqui SPC-003 acusa como erro na **aprovacao** (a specify e mais estrita que o validador; o cenario de REQ retirado sai com linha em "Mudancas").

### Step 1 -- reflection-on-action | 2026-10-06 17:53 UTC | Terreno e dependencias
- happened: Conferi contrato, grill, convencao Gherkin, CLIs de check_intent e check_features, o passo 2b do /plan e o run_all_checks; baseline 17/14 e 863/12.
- deviated: Fixtures em .claude/skills/scripts/tests/fixtures/specify; run_all_checks nao precisa de edicao (glob); emenda D-004 muda o objeto de aprovacao do citizen.
- less-sure: Se o aviso GHK deve bloquear a aprovacao (plano) ou ficar so com quem le codigo (lacuna do 000010).
- gate: not-installed
