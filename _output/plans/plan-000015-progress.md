# Progress -- Plan 000015

Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

## Codebase Patterns
<!-- Subagents consolidate reusable patterns here -->

- Terreno herdado do plan-000007 (ler `_output/plans/plan-000007-progress.md`, secoes "Codebase Patterns", "Step 1" e "Step 7"): repositorio de execucao e este (sem prefixo `open-seja/`); `seja-as-intended.md` -> `product-design/product-design-as-intended.md` (§3); numeracao D-NNN do Doutourado nao vale aqui (D-004 = contrato Gherkin; D-005..D-008 = plan-000007; proximo livre D-009); "D-006 do Doutourado" citada nos planos = D-004 aqui.
- O contrato existe: `.claude/references/general/extended-cycle-contract.md` (CYC-001..026); esquema `features/<slug>/` em `.claude/references/template/feature-layout.md`; formato v2 em `.claude/references/template/plan-step.md`.
- Fixtures do harness ficam em `.claude/skills/scripts/tests/fixtures/<tema>/` (logo `<fixtures>/drift/` = `.claude/skills/scripts/tests/fixtures/drift/`).
- `python3` (nao `python`); pytest via `uvx --with pyyaml pytest ... --ignore=.claude/skills/scripts/tests/test_generate_spo.py --ignore=.claude/skills/scripts/tests/test_generate_spo_design_system.py`.
- Baseline (Q1): `run_all_checks.py` 19 PASS / 14 FAIL (PASS extras: check_intent, check_features, check_specify, check_plan_scenarios) com contadores 17 undefined (check_conventions), 2 error(s) (check_i18n_keys), 9 error(s) (check_skill_system); pytest 1440+ passed / 12 failed (os 12 pre-existentes; apos plans 000009-000014). Rodar `run_all_checks.py` com `timeout 200`, saida em arquivo, nunca dois ao mesmo tempo, nunca checks isolados, nunca `pkill -f`.
- Arquivos do harness: UTF-8, sem travessao tipografico nem aspas curvas; nada de nome de pessoa, parceiro, instituicao ou empresa.
- Portao nao instalado no open-seja: notas com `--gate not-installed`.
- Commits: `git -c user.name=arodrigues-puc-rio -c user.email=arodrigues-puc-rio@users.noreply.github.com commit ...`; nunca `--no-verify`.
- Decisoes pendentes do plano: o designer aceitou todas as recomendacoes em 2026-10-06; marcar como `[default; aceito 2026-10-06]`.
- `run_all_checks.py` deve rodar com `< /dev/null` (sem isso `check_skill_system` pode travar 120 s e dar ERROR; com isso leva ~3,5 s).

- Planos ja entregues neste roadmap: ver a coluna Status da Wave Summary em `_output/roadmaps/roadmap-000006-*.md` e os `## Implementation summary` dos planos DONE; os progress files deles listam lacunas que este plano deve absorver no Step 1.

## Iteration Log

### Step 1 -- terreno e baseline (2026-10-06)

Decisao: **seguir**. Os planos 000007 a 000014 executaram (todos DONE). Nada foi escrito no harness neste step. Decisoes pendentes 1-8 do plano: 1=A, 2=A, 3=A, 4=B, 5=A, 6=C, 7=A (gatilho para B), 8=A, todas `[default; aceito 2026-10-06]`.

| Item | Estado | Onde / o que vale |
|---|---|---|
| (a) planos 000007-000014 e IDs reais | existe | `CYC-001..030` (proxima livre CYC-031), `GRL-001..015`, `GHK-001..019`, `SPC-001..018`, `PFS-001..015`, `ITF-001..025` (o plano dizia `TFB`), `DRM-001..014`, `DRP-001..019`; codigos `NM-*` do DRM-009 mais `NM-SEM-RETRADUCAO-POS-CODIGO` e `NM-SEM-MARCA-ADOCAO` (so em `drift-report.md`). CLIs: `check_intent.py [<intent.md> --d0 / --require-approved --strict]`; `check_features.py [raiz] [--feature s] --json --matrix [--steps d] [--strict]`; `check_specify.py [raiz] --feature s --status [--json]` / `--approve --at --by --contract-by`; `check_plan_scenarios.py <plano> --json`; `drift_report.py --feature s [--plan p] --moment M1|M2 --freeze --at <UTC> / --compare / --md / --citizen / --html / --audit-sample`; `build_checks.py` (14 subcomandos + `snapshot`). D-NNN no as-intended: D-001..D-008 (proxima livre D-009); propostas nos progress: D-009 (000009), D-010 (000010), D-011 (000011), D-012 (000012), D-013 (000014), D-014 (000013). |
| (b) os quatro checks sem argumentos | existe, ja condicionais | Na raiz do open-seja e num projeto vazio (scratchpad): `check_intent` "nenhum features/*/intent.md; nada a verificar.", `check_features` e `check_specify` "nenhum features/<slug>/intent.md; nada a verificar.", `check_plan_scenarios` "nenhum plano v2 em _output/plans/; nada a verificar."; todos exit 0. `run_all_checks.py`: glob `check_*.py` em `scripts/` e nos diretorios de skill, subprocesso `[python, script]` sem argumentos, cwd = raiz, le so o exit code (0 PASS, outro FAIL, timeout 120 s ERROR). Os quatro **ja estao** no `check_plugin_registry.json` (`stack: any`, `critical: false`, `scope` intent/features/features/plans). A lacuna 5 do plano (risco de exit 2 sem argumento) **ja estava fechada** pelos planos 000009-000012; o Step 6 so prova com teste agregado. Palavra impressa: "nada a verificar" (o plano dizia "pulado"); mantida, sem renomear saida entregue. |
| (c) valores de `scenarios:` | `approved` e ausente | `check_specify.compute_status`: `marked = (scenarios == "approved")`; qualquer outro valor (inclusive `draft`) = nao marcado. Com lock e campo != approved: `stale` com razao `sem-campo`; sem lock e sem campo: `draft`. `check_features.load_intent`: `scenarios_approved = None` se ausente, senao `== "approved"` (`draft` -> `False`). `drift_report` e `check_plan_scenarios` usam `--status` (nunca o campo). Logo `scenarios: draft` e aceito por todos os leitores (decisao 2 = A sem emenda de esquema). Varredura do `check_specify` falha so com `marked and status != approved`: depois do `--reconcile` (campo `draft`) a varredura volta a 0 e o `--status` continua `stale`. |
| (d) `skill-body-length` | medido | `check_docs.py --plugins skill-body-length --verbose`: `plan` 72/500 (heavy; o corpo da fase vive em `_internal/plan/standard/SKILL.md`, que o plugin nao mede), `implement` 254/500, `explain` 65/300, `reflect` 248/300 (83%), `help` 70/150, `seja-setup` 85/300; 0 erros, 2 warnings (citacoes, pre-existentes). Folga ampla; o baseline do arquivo `check_docs_skill_body_length_baseline.md` esta defasado (v0.9.1: plan 423, explain 259). |
| (e) versao e CHANGELOG | existe | tag corrente **v0.10.1** (`git tag`); arquivo de versao real = `.seja-version` (`v0.10.1`) e `CHANGELOG.md` na raiz (`## [Unreleased]` vazio, `## [v0.10.1] - 2026-10-04`), conforme `tools/release-process.md` passo 1. `check_version_changelog_sync.py` **nao cobre** esses arquivos: compara `.claude/skills/VERSION` (0.7.1) com `.claude/CHANGELOG.md` (0.9.1) e ja e um dos 14 FAIL do baseline. Proxima minor: **v0.11.0**. |
| (f) 000074 | ausente | `lint_controlled_language.py` e `select_diagram.py` nao existem; `--html` do 000074 nao existe (existe `md_to_html.py`, de outro uso). Step 8 degrada: contagem propria e `flowchart LR`; `voz: nao verificada pelo lint`. |
| (g) baseline | medido | `run_all_checks.py` (timeout 200, `< /dev/null`): **19 PASS / 14 FAIL** (check_docs, check_plan_coverage, check_api_auth_decorators, check_backend_test_coverage, check_conventions, check_frontend_test_coverage, check_i18n_keys, check_migration_chain, check_po_parity, check_skill_system, check_validation_constants_sync, check_version_changelog_sync, check_vuln_patterns, check_worktree_health), contadores 17 undefined / 2 error(s) / 9 error(s). pytest: **1440 passed / 12 failed** (test_html_report x8, test_summarize_artifacts x4). Medicao do caso (i) do 000013 (Stop hook com arvore vermelha): chamadas 1-3 exit 2 ("Quality gate FAIL (exit 3)"), chamada 4 exit 0 ("released after 3 blocks; the human decides"); n = 1, papeis roteirizados. |

**Ordem de edicao dos `SKILL.md`**: seguida (000007 ponteiro -> 000009 grill -> 000011 specify -> 000012 v2 -> 000013 `--pipeline` -> 000014 reflect/explain). Nenhum plano anterior ficou sem executar.

**Achados do Step 1 que mudam o escopo dos steps seguintes** (terreno prevalece sobre o plano):
1. **Step 2**: CYC-028 (chave de cenario) e CYC-029 (proxy do skip) **ja existem** (emenda 000012), e `plan-step.md` ja traz a chave com exemplo. O Step 2 nao os reescreve: a secao nova do contrato aponta para eles e acrescenta so o que falta (M1, reconciliacao, ordem dos SKILL.md, ciclo por upgrade, quem escreve `adoption.json` e `retraducao-pos-codigo.md`, quando usar `--citizen`). `drift-metric.md` e `drift-report.md` entram no Step 2 (emendas pedidas pelo orquestrador; fora dos Files do plano).
2. **Step 5**: a fiacao do M1 **ja existe** (plan-000013 Step 7): `implement/SKILL.md` Phase 2 passo 12 cita "M1 freeze" e `implement-test-first.md` Procedimento item 9 e ITF-019 trazem `drift_report.py --feature <slug> --moment M1 --freeze --at <UTC>`. O Step 5 **nao** acrescenta linha ao `SKILL.md` (duplicaria); acrescenta so a secao normativa "Congelar o M1 (emenda 000015)" com a semantica de falha (avisa e segue) e o teste de costura.
3. **Step 6**: o comportamento sem argumentos e o registro ja existem; o Step 6 reduz-se ao teste agregado `test_default_cycle_checks.py`.
4. **Step 7**: folga grande em todos os SKILL.md medidos; a medida e o baseline atualizado bastam.
5. **Step 9**: o arquivo de versao e `.seja-version` + `CHANGELOG.md` (raiz); `check_version_changelog_sync.py` mede outro par e ja falha no baseline.

### Step 1 -- reflection-on-action | 2026-10-06 19:26 UTC | Conferir o terreno e fixar o baseline
- happened: Li os progress 000007-000014, as CLIs reais e o run_all_checks; os quatro checks ja saem 0 sem argumentos e ja estao no registro; medi o baseline (19/14, 17/2/9; pytest 1440/12).
- deviated: A chave de cenario, o proxy do skip e a fiacao do M1 ja existiam; os Steps 2, 5 e 6 encolhem; o arquivo de versao real e .seja-version.
- less-sure: Se o designer quer que check_version_changelog_sync passe a cobrir .seja-version.
- gate: not-installed
