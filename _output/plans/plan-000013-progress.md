# Progress -- Plan 000013

Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

## Codebase Patterns
<!-- Subagents consolidate reusable patterns here -->

- Terreno herdado do plan-000007 (ler `_output/plans/plan-000007-progress.md`, secoes "Codebase Patterns", "Step 1" e "Step 7"): repositorio de execucao e este (sem prefixo `open-seja/`); `seja-as-intended.md` -> `product-design/product-design-as-intended.md` (§3); numeracao D-NNN do Doutourado nao vale aqui (D-004 = contrato Gherkin; D-005..D-008 = plan-000007; proximo livre D-009); "D-006 do Doutourado" citada nos planos = D-004 aqui.
- O contrato existe: `.claude/references/general/extended-cycle-contract.md` (CYC-001..026); esquema `features/<slug>/` em `.claude/references/template/feature-layout.md`; formato v2 em `.claude/references/template/plan-step.md`.
- Fixtures do harness ficam em `.claude/skills/scripts/tests/fixtures/<tema>/` (logo `<fixtures>/drift/` = `.claude/skills/scripts/tests/fixtures/drift/`).
- `python3` (nao `python`); pytest via `uvx --with pyyaml pytest ... --ignore=.claude/skills/scripts/tests/test_generate_spo.py --ignore=.claude/skills/scripts/tests/test_generate_spo_design_system.py`.
- Baseline (Q1): `run_all_checks.py` 19 PASS / 14 FAIL (PASS extras: check_intent, check_features, check_specify, check_plan_scenarios) com contadores 17 undefined (check_conventions), 2 error(s) (check_i18n_keys), 9 error(s) (check_skill_system); pytest 1120+ passed / 12 failed (os 12 pre-existentes; apos plans 000009-000012). Rodar `run_all_checks.py` com `timeout 200`, saida em arquivo, nunca dois ao mesmo tempo, nunca checks isolados, nunca `pkill -f`.
- Arquivos do harness: UTF-8, sem travessao tipografico nem aspas curvas; nada de nome de pessoa, parceiro, instituicao ou empresa.
- Portao nao instalado no open-seja: notas com `--gate not-installed`.
- Commits: `git -c user.name=arodrigues-puc-rio -c user.email=arodrigues-puc-rio@users.noreply.github.com commit ...`; nunca `--no-verify`.
- Decisoes pendentes do plano: o designer aceitou todas as recomendacoes em 2026-10-06; marcar como `[default; aceito 2026-10-06]`.
- `run_all_checks.py` deve rodar com `< /dev/null` (sem isso `check_skill_system` pode travar 120 s e dar ERROR; com isso leva ~3,5 s).

- Planos ja entregues neste roadmap: ver a coluna Status da Wave Summary em `_output/roadmaps/roadmap-000006-*.md` e os `## Implementation summary` dos planos DONE; os progress files deles listam lacunas que este plano deve absorver no Step 1.

## Iteration Log

### Step 1 -- terreno e fontes de dado (2026-10-06)

Decisao: **seguir**. O plan-000012 executou (DONE); todas as dependencias existem. Nada foi escrito no harness neste step.

| Item | Estado | Onde / o que vale |
|---|---|---|
| (a) planos 000007, 000009-000012 | existe | regras `CYC-001..029` (`extended-cycle-contract.md`; proxima livre CYC-030), `GRL-001..015`, `GHK-001..019`, `SPC-001..018`, `PFS-001..015`, `DRM-001..014`; `DRP-001..019` do plan-000014 (em paralelo). Ordem de edicao de `implement/SKILL.md`: ponteiro do 000007 (linha 29) -> version check do 000012 (Phase 0 passo 3; Manual passo 2) -> **este plano** (estende o passo 3, nao o refaz). `_internal/plan/standard/SKILL.md` nao e tocado aqui. |
| (b) linha de parada do 000012 | existe | decisao 4 = A: v2 roda `check_plan_scenarios.py` e para sem corrigir se exit != 0. Herdada. |
| (c) chave do lock e funcao de chave | existe | `scenarios.lock.json` `index` = lista ordenada de `<slug>/<arquivo>.feature::<nome>`; `check_features.scenario_key(slug, path, name)` (linha 762). O plugin, que roda no projeto sem o harness no caminho, copia a funcao e um teste de igualdade a compara. |
| (d) conftest modelo e pytest-bdd | existe | `feature-example/conftest.py.example` so implementa `pytest_bdd_apply_tag` (REQ-* e nao-faz); **nao** grava propriedade `req` (o plano supunha que sim). `pytest-bdd` 9.0.0 / pytest 9.1.1 por `uvx --with pytest-bdd`; hooks `pytest_bdd_apply_tag`, `pytest_bdd_step_error(request, feature, scenario, step, step_func, step_func_args, exception)`, `pytest_bdd_step_func_lookup_error(request, feature, scenario, step, exception)`; `Step` tem `type`, `keyword`, `line_number`. Exemplo: `test_feature_example.py` exige que `feature-example/` nao tenha `*.py` (sufixo `.example`). |
| (e) gate.py | existe (nao muda) | flags: `--fast`, `--full`, `--files`, `--json`, `--init-baseline`, `--accept-baseline` (+`--yes`, so humano), `--out-dir`. **Nao ha override de `crap_max_touched` por linha de comando** (so `[tool.seja-gate]` no `pyproject.toml`, edicao humana). Saida `version: 1`, `status` PASS/FAIL/ERROR, `exit_code` 0..7, `stages`, `findings[{category,key,message,value,limit,severity}]`, `baseline` (caminho). CRAP so aparece como achado **acima** do limite: o alvo 8 do Cleaner precisa de calculo proprio (radon + `coverage.json`) -> subcomando `build_checks.py crap` (desvio: nao estava na lista do Step 5). Mutacao: com `--files`, alvo = **todas** as funcoes desses arquivos; sem `--files`, funcoes tocadas contra `diff_base` (default `origin/main`); sobrevivente vira achado categoria 6 com `key` = `arquivo::funcao` e o nome do mutante na mensagem. `coverage.json` e escrito na raiz com `--cov-branch`. `--cov-context` nao e usado pelo gate; a cobertura so dos cenarios e uma rodada propria do pipeline (`pytest -m scenario --cov --cov-branch --cov-report=json:<arq>`), sem mexer no gate. `quality-baseline.json` = `{version, functions{key:{cc,cov,crap,survived}}, markers, mutation{survived_total}}`. |
| (f) /implement | existe | Auto Mode passo 8: contrato do subagente (TDD red-green, 3 tentativas, PARTIAL), portao `GATE_FAST_CMD --files` ate 3 rodadas, `step_notes.py append --gate-json/--gate-attempts`. Ponto de extensao de `step_notes.py`: argumentos de `append` + `_FIELD_RE` do `parse`. `skill-body-length` (plugin de `.claude/skills/critique/check_docs.py`, nao de `check_skill_system.py`): implement = tier heavy, **253/500 linhas**. |
| (g) `gate.json` fechado? | nao | `feature-layout.md` declara `{schema_version, fast, full, ts}` sem dizer que e fechado; leitores ignoram chave desconhecida. Decisao pendente 2 = A (chave `build`). O `drift-report.md` do plan-000014 (Step 2 dele, ja commitado) le **arquivos separados**: `features/<slug>/runner/cucumber.json`, `gate.json` (+ `baseline_moved`, `adapter` opcionais), `drift/red-reason.json` (`{schema_version, scenarios{chave: bool}}`), `drift/coverage.json` (`{schema_version, base, touched_total, touched_uncovered}`) e espera que o `/implement` chame `drift_report.py --freeze --moment M1 --at <UTC>` no fim. Este plano grava `gate.json.build` **e** exporta esses arquivos (subcomando `export`), para a costura com o 000014 sem depender de leitura do `build`. |
| (h) baseline | medido | `run_all_checks.py`: 14 FAIL, contadores 17 undefined / 2 error(s) / 9 error(s); pytest: 12 failed / 1120 passed. `uvx ruff` 0.16.10 ok; `pyright` **nao roda** neste ambiente (node sem `libatomic.so.1`): verificacao de tipos fica "nao provado". |

Desvios de nome decididos aqui:
- Prefixo das regras proprias: **`ITF-NNN`** (instrucao do orquestrador) no lugar do `TFB-NNN` do plano; numeracao 1:1 (TFB-005 do plano = ITF-005).
- O plugin vai como `.claude/references/template/bdd/python/scenario_report.py.example` (sufixo `.example`, como o exemplo do 000010), para o pytest do harness nunca o coletar; `install-plugin` copia para `tests/scenario_report.py` tirando o sufixo. A logica pura do plugin nao importa `pytest_bdd` no topo e e testada com stdlib.
- Fixtures em `.claude/skills/scripts/tests/fixtures/build/` (nao `tests/fixtures/build/` na raiz). Os planos v1 do golden sao os de `fixtures/plan_format/` (copias do 000007), lidos por caminho e conferidos por hash, nao copiados de novo.
- Decisoes pendentes 1-7 aceitas no default (1=A, 2=A, 3=A, 4=A, 5=B, 6=A, 7=B), marcadas `[default; aceito 2026-10-06]`.

### Step 1 -- reflection-on-action | 2026-10-06 18:38 UTC | Conferir o terreno e as fontes de dado no open-seja
- happened: Li os contratos, o gate, os hooks, o /implement e os progress 000008-000012; todos os itens (a) a (h) existem; medi o baseline (14 FAIL, 17/2/9; pytest 12 failed).
- deviated: O conftest modelo nao grava a propriedade req; o gate nao aceita alvo de CRAP por linha de comando; o plan-000014 ja le arquivos separados (runner/cucumber.json, drift/red-reason.json, drift/coverage.json), entao o registro vai em gate.json.build e e exportado; prefixo ITF no lugar de TFB.
- less-sure: Se o plan-000014 vai mudar o formato de drift/*.json antes de fechar; pyright nao roda aqui.
- gate: not-installed

### Step 2 -- norma `implement-test-first.md` (2026-10-06)

- Criada `.claude/references/general/implement-test-first.md` com `ITF-001..025` (25 regras; as 22 do plano com o prefixo trocado e mais tres): ITF-023 exportacao para os arquivos que o `drift_report.py` do plan-000014 le (`runner/cucumber.json`, `drift/red-reason.json`, `drift/coverage.json`, `gate.json.baseline_moved`), ITF-024 demonstracao por cenario e mutantes recontados como perguntas (emenda do adendo, registro do citizen, M1), ITF-025 `scenario-tester` como terceiro amigo informativo antes da aprovacao (emenda do adendo). R1..R8 numeradas em ITF-005. Toda regra tem "Quem decide" e "Criterio de aceitacao". Decisoes 1-7 marcadas `[default; aceito 2026-10-06]`; tabela "Costura com o 000008"; tabela subcomando -> regra.
- Subcomandos acrescentados a lista do Step 5 (desvio): `route` (classificacao v1/v2 e golden; da dentes ao "v1 nao muda"), `green-check` (ITF-009 por ferramenta), `crap` (o gate nao aceita alvo por CLI), `export` (ITF-023), `demo` (ITF-024).
- `run_all_checks.py`: igual ao baseline (14 FAIL; 17/2/9). `check_docs.py` da avisos "Specific plan ID" na norma, como nas outras referencias do ciclo (ja FAIL no baseline).

### Step 2 -- reflection-on-action | 2026-10-06 18:41 UTC | Escrever a norma do teste-primeiro (implement-test-first.md)
- happened: Escrevi a norma com ITF-001..025, R1..R8, constantes, fluxo, decisoes no default, costura com o 000008 e tabela de ferramentas; run_all_checks ficou igual ao baseline.
- deviated: Prefixo ITF no lugar de TFB; tres regras a mais (exportacao ao plan-000014, demonstracao ao citizen, terceiro amigo) e cinco subcomandos a mais (route, green-check, crap, export, demo).
- less-sure: Se a frase-modelo da escalada e a narracao do demo passam no teste da surpresa sem um citizen real ler.
- gate: not-installed
