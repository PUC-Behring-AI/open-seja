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

### Step 3 -- fixtures e testes antes do codigo (2026-10-06)

- Fixtures ficticias em `.claude/skills/scripts/tests/fixtures/build/` (58 arquivos, README por pasta): mini projeto (`project/`: feature `task-list` copiada do exemplo do 000010, `src/tasks.py`, `tests/steps_defs.py` sem prefixo `test_` para nenhum runner coletar), 21 relatorios do plugin (`reports/`), Cucumber JSON + JUnit (`cucumber/`), cobertura de R7, esqueleto valido/invalido, 12 casos de escopo (`scope/cases.json`), diff + cobertura de D3b, baseline igual/movido, saidas do portao e `gate.json` com chave desconhecida, saidas de ferramenta para os briefings, `plans/v1-hashes.json` (hash dos dois planos v1 de `fixtures/plan_format/`, as copias do 000007: lidas por caminho, nao recopiadas). Gerador descartavel no scratchpad (nao versionado).
- Testes escritos antes: `test_build_checks.py` (R1..R8 incl. `already_green`, R2, R4 constante/raise/condicional, R5, R6 por cenario e por teste comum, R7, R8; Cucumber + JUnit; ITF-004; ITF-007; ITF-008 (12 casos + git real); ITF-009; ITF-010; ITF-015; ITF-017; ITF-018; ITF-020; ITF-001/003/021 `route` com golden dos v1; ITF-023 `export`; ITF-024 `demo` sem digito/PASS/%; ITF-016 `install-plugin` idempotente e recusa de copia editada), `test_scenario_report.py` (chave igual a `check_features.scenario_key` com acento, espaco e `::`; desfecho por item; Outline agregado; cabecalho do relatorio; selecao por chave) e `test_build_brief.py` (conteudo e exclusoes por papel, manifesto, teto, papel desconhecido = exit 2).
- Vermelho 1 (sem modulos): 3 erros de coleta -- `ModuleNotFoundError: build_checks`, `ModuleNotFoundError: build_brief`, `FileNotFoundError: scenario_report.py.example`.
- Vermelho 2 (modulos-esboco com as funcoes pendentes devolvendo vazio/None): **96 failed, 4 passed**; as falhas sao `assert` (ex.: `assert None is False`, `assert None == 0`) e 14 `TypeError: 'NoneType' object is not iterable` dos esbocos que devolvem `None` -- nenhuma por import. Os 4 que passam ja passam por desenho (hash dos v1, arquivo do plugin com sufixo `.example`, casos de escopo sem achado esperado sobre esboco que devolve vazio nao contam: conferido nos Steps 4-6).
- Desvio: para o commit deste step nao quebrar a suite do harness (regra "so as 12 falhas pre-existentes"), os tres arquivos de teste levam `pytestmark = pytest.mark.xfail(reason="plan-000013 step 3: contrato antes do codigo", strict=False)`, retirado no step que deixa cada modulo verde (4: plugin; 5: `build_checks`; 6: `build_brief`). Os esbocos `build_checks.py`, `build_brief.py` e `scenario_report.py.example` entram no commit e sao substituidos nos Steps 4-6.
- Verify: pytest do harness 12 failed (os pre-existentes), 96 xfailed, 4 xpassed; `run_all_checks.py` igual ao baseline; `uvx ruff check` limpo nos arquivos novos.

### Step 3 -- reflection-on-action | 2026-10-06 18:47 UTC | Criar fixtures golden e os testes que ainda falham
- happened: Gerei 58 fixtures ficticias e tres arquivos de teste antes do codigo; o primeiro vermelho foi de coleta (modulos ausentes) e o segundo, com esbocos, foi 96 falhas por assert e TypeError de esboco.
- deviated: Marquei os tres arquivos com xfail de modulo (com motivo) para nao quebrar a suite do harness entre os Steps 3 e 6; os v1 do golden sao lidos de fixtures/plan_format por hash, nao copiados.
- less-sure: Se 14 falhas por TypeError contam como vermelho pelo motivo certo no sentido do plano; elas vem de esboco que devolve None, nao de import.
- gate: not-installed

### Step 4 -- plugin de relatorio do runner (2026-10-06)

- `.claude/references/template/bdd/python/scenario_report.py.example` (sufixo `.example`, ver Step 1): funcoes puras (`scenario_key` copiada de `check_features.py` com teste de igualdade, `key_for`, `req_tags`, `item_outcome`, `aggregate`, `short_reason`, `add_row`, `build_report`, `selected`) e hooks (`pytest_addoption`, `pytest_configure` com o marker `scenario`, `pytest_bdd_apply_tag` para `REQ-*`/`nao-faz`, `pytest_collection_modifyitems` com a chave via `scenario_wrapper_template_registry` do pytest-bdd, propriedades JUnit `scenario_key` e `req`, selecao `--scenario-key`/`--scenario-exclude-key`, `pytest_bdd_step_error` e `pytest_bdd_step_func_lookup_error` para tipo efetivo, texto e local da funcao do step, `pytest_runtest_makereport` (hookwrapper), `pytest_collectreport` para erro de coleta, `pytest_sessionfinish` grava o JSON). pytest-bdd 9.0.0 nao expoe `__scenario__` no item: a chave vem do registro `scenario_wrapper_template_registry.get(item.obj)`, o mesmo que o pytest-bdd usa em `generation.py`.
- `build_checks.py install-plugin <projeto>`: copia para `tests/scenario_report.py`, grava o hash em `tests/.scenario_report.sha256`, acrescenta `pytest_plugins = ["scenario_report"]` ao `tests/conftest.py` (cria se falta), idempotente; copia editada a mao -> exit 1 sem sobrescrever. Os demais subcomandos seguem esboco ate o Step 5.
- `conftest.py.example` do exemplo do 000010: **nao** passou a importar o plugin (desvio). Motivo: o exemplo roda sozinho com as instrucoes da secao 10 de `gherkin-spec-format.md` e `test_feature_example.py` exige a pasta sem `*.py`; importar o plugin quebraria a receita documentada. A docstring agora aponta o plugin como a forma completa; o hook e o mesmo nos dois (o pytest-bdd usa o primeiro resultado).
- Prova no runner (scratchpad, `uvx --with pytest-bdd`, pytest-bdd 9.0.0 / pytest 9.1.1), exemplo copiado + um teste comum:
  - `--scenario-report --cucumberjson --junitxml`: 1 failed, 4 passed, 1 skipped. Relatorio: Outline `passed` com 2 linhas; "Acrescentar uma tarefa" `passed`; `@skip` `skipped`; "Marcar uma tarefa como feita" `failed`, `AssertionError`, `failing_step_type: then`, `step_func {file: test_task_list.py, line: 66, name: shows_done}`; teste comum em `tests`. JUnit com `scenario_key` e `req` em todo teste de cenario.
  - `--scenario-key <Marcar...>`: 1 failed, 5 deselected; so essa chave no relatorio, `tests` vazio.
  - Given quebrado: `failed`/`AssertionError`/`given` (o red-check o barra por R3); step `Entao` sem definicao: `error`, `StepDefinitionNotFoundError`, `undefined: true`, tipo `then`; Outline com uma linha vermelha: `failed` com linhas `[passed, failed]`; arquivo com erro de sintaxe: `collect_errors` no relatorio (nao some).
  - Chaves do relatorio == chaves de `check_features.py --matrix` (as 4).
  - `install-plugin` num projeto com `tests/`: `--strict-markers -W error::pytest.PytestUnknownMarkWarning` roda limpo (1 failed, 3 passed, 1 skipped).
- Lacuna: `pytest_plugins` em `tests/conftest.py` funciona quando `tests/` esta sob a raiz do pytest; em projeto com `conftest.py` na raiz e `rootdir` diferente, o pytest pode recusar `pytest_plugins` fora do conftest de topo. O `install-plugin` nao trata isso (fica para o piloto).
- Verify: `test_scenario_report.py` 20 passed (xfail retirado); `uvx ruff` limpo (plugin conferido numa copia `.py`); `pyright` nao provado (ambiente); `run_all_checks.py` igual ao baseline; pytest do harness 12 failed (pre-existentes).

### Step 4 -- reflection-on-action | 2026-10-06 18:51 UTC | Implementar o plugin de relatorio do runner (scenario_report)
- happened: Escrevi o plugin e o install-plugin; no pytest-bdd real o relatorio deu a chave igual a do check_features, failed por AssertionError no Entao, given quebrado, step indefinido, Outline agregado, erro de coleta e selecao por chave.
- deviated: A chave vem do registro interno do pytest-bdd (nao ha __scenario__); o conftest do exemplo nao passou a importar o plugin para nao quebrar a receita documentada.
- less-sure: O registro scenario_wrapper_template_registry e interno do pytest-bdd e pode mudar de nome; pytest_plugins em conftest fora do topo pode ser recusado em alguns layouts.
- gate: not-installed

### Step 5 -- verificadores deterministicos `build_checks.py` (2026-10-06)

- `build_checks.py` completo (stdlib; `check_plan_scenarios` importado para ler o plano): `route`, `install-plugin`, `skeleton`, `red-check` (relatorio do plugin **ou** Cucumber JSON + JUnit, CYC-027), `green-check`, `freeze`, `scope`, `crap`, `uncovered`, `baseline`, `record` (escrita atomica, chaves desconhecidas mantidas, idempotente), `status`, `export`, `demo`. Exit 0/1/2; erro de leitura -> 2 sem traceback; `--json` com `schema_version: 1`; tempo so de `--at`.
- `test_build_checks.py`: 70 passed (xfail retirado).
- Tabela `red-check` sobre as fixtures (dono = "Marcar uma tarefa como feita", baseline `suite-base`): red-ok -> ok; red-import-error, red-collection-error, red-undefined, red-already-green (+ `escalate`), red-skipped, red-xfail, red-missing -> R1; red-wrong-exception -> R2; red-given-failure, red-when-failure -> R3; red-constant-assert, red-raise-assert -> R4; red-conditional-raise -> ok (raise dentro de `if` nao e constante); red-suite-broken, red-suite-broken-test -> R6; red-outline-partial (donos Outline + Marcar) -> ok, `rows_green_in_red = 1`; red-outline-error -> R8. Skeleton invalido -> R5; cobertura sem corpo -> R7.
- `uncovered` sobre a fixture: 8 linhas + 2 ramos tocados = 10; 3 linhas + 1 ramo descobertos = 4 (conferido a mao: linhas 13, 24, 25 e o ramo 12->13; README.md fora por nao ser executavel).
- Precedencia no `scope`: `.feature` alterado pelo Coder e ITF-008 mesmo quando esta na lista de congelados (o achado diz o papel, nao o hash). `features/<slug>/gate.json`, `runner/**` e `drift/**` sao do `/implement` (classe `record`), nao contam para nenhum papel.
- Costura com o plan-000014 (mensagem do coordenador, `drift-report.md` DRP-001 e `drift_report.py` lidos): os formatos que `export` grava batem com o que o calculador le -- `drift/red-reason.json` `{schema_version, scenarios{chave: bool}}`, `drift/coverage.json` `{schema_version, base, touched_total, touched_uncovered}` (o calculador ignora `touched_total` sem `base`: o `export` sempre grava `base`), `gate.json` `full.category`/`full.exit_code` e `baseline_moved` no topo, `runner/cucumber.json`. Fica fora: `runner/adapter.json` e o campo `adapter` (ausente = adaptador existe, que e o caso do Python com pytest-bdd); o congelamento do M1 (`drift_report.py --feature <slug> --moment M1 --freeze --at <UTC>`) entra no fim do plano pelo `/implement` (Step 7), nao no `build_checks.py`.
- Verify: `uvx ruff` limpo; pyright nao provado (ambiente); `run_all_checks.py` igual ao baseline; pytest do harness 12 failed (pre-existentes) / 1424 passed. Uma rodada intermediaria deu 31 failed por arquivos em edicao do plan-000014 no mesmo worktree; a repeticao logo depois deu as 12 de sempre.

### Step 5 -- reflection-on-action | 2026-10-06 18:58 UTC | Implementar os verificadores deterministicos (build_checks.py)
- happened: Implementei os 14 subcomandos com funcoes puras e CLI; os 70 testes do Step 3 passaram e cada fixture red-* deu a regra esperada.
- deviated: Cinco subcomandos alem do plano (route, green-check, crap, export, demo); red-check tambem le Cucumber JSON + JUnit; os formatos do export foram alinhados ao drift_report.py do plan-000014.
- less-sure: A regra do Hardener (linha acrescentada so com pragma e codigo igual ao removido) pode recusar uma reformatacao legitima; R7 depende de o relatorio de cobertura usar caminhos relativos ou terminar no caminho do step.
- gate: not-installed

### Step 6 -- papeis com contexto curto (2026-10-06)

- `build_brief.py`: le o bloco do step do plano, as chaves de `Scenarios:`, o Gherkin bruto de cada cenario dono (via `check_features.parse_feature`), o indice de definicoes de passo (ast dos decoradores `given/when/then/step`), o corpo das funcoes por `arquivo::Classe.metodo` e a lista de testes; monta secoes obrigatorias (regras do papel, step, Gherkin, saida da ferramenta, escopo, fechamento) e opcionais (indice, corpos, testes), com manifesto (`item`, `chars`, `required`, `included`) e teto (`PIPELINE_BRIEF_MAX = 24000`); acima do teto corta so o opcional e marca `truncated`. Grava `_output/tmp/brief-<plan>-step-<N>-<papel>.md`.
- Conteudo por papel (ITF-012), conferido nos testes: Tester ve step, Gherkin dono, indice e regras do vermelho, nao ve corpo de codigo nem cenario de outro step; Coder ve step, Gherkin, a mensagem do `red-check` e os congelados, sem regra de CRAP ou pragma; Cleaner ve so `CRAP(src/tasks.py::TaskList.mark_done)=26.4 (CC=26, cov=0.92) > 8: dividir`, o corpo e o escopo (nenhum texto de cenario ou de step); Hardener ve sobreviventes com diff, corpos, testes existentes, a regra do pragma e o pedido da pergunta ao citizen (ITF-024).
- Agentes novos `.claude/agents/scenario-tester.md` (modos `red` e `review`, este o terceiro amigo informativo da ITF-025), `cleaner.md`, `hardener.md`: frontmatter `name`, `description`, `designer_description`, `tools` (Cleaner: Read, Edit, Bash; Hardener: Read, Write, Edit, Bash; nenhum com busca na web); cabecalho "One job, then destroyed"; fecho "o resultado e o que a ferramenta devolver". `check_skill_system.py` ve 19 agentes e continua com os 9 erros do baseline.
- Lacuna: `.claude/rules/harness-structure.md` diz "16 subagent prompts" e "Executor agents ... not standalone prompt files"; com os tres papeis isso ficou desatualizado. Nao editei (fora dos Files do plano); texto sugerido no Step 9.
- Verify: `test_build_brief.py` 10 passed (xfail retirado); `uvx ruff` limpo; `run_all_checks.py` igual ao baseline; pytest do harness 12 failed / 1434 passed (nenhum xfail restante deste plano).

### Step 6 -- reflection-on-action | 2026-10-06 19:01 UTC | Criar os papeis com contexto curto (agentes e montador de briefing)
- happened: Escrevi build_brief.py com manifesto e teto e os agentes scenario-tester, cleaner e hardener; os 10 testes do briefing passaram e o check de agentes nao subiu.
- deviated: O scenario-tester ganhou o modo review (terceiro amigo informativo) e o Hardener devolve perguntas ao citizen em JSON; harness-structure.md ficou com a contagem de agentes desatualizada.
- less-sure: Se 24 000 caracteres e o teto certo; nenhum subagente real leu um briefing ainda (so o piloto mostra se o contexto curto basta).
- gate: not-installed

### Step 7 -- ramo v2, `--pipeline`, loop e escalada no `/implement` (2026-10-06)

- `implement/SKILL.md` (ordem: ponteiro do 000007 -> parada do 000012 -> este): `argument-hint` e tabela de argumentos com `--pipeline`; o ponteiro do topo cita `implement-test-first.md`; paragrafo de flags; Manual Mode passo 2 (steps `test-first` seguem o Procedimento no contexto atual, sem subagentes de papel); Auto Mode Phase 0 passo 3 **estendido, nao refeito**: depois do `check_plan_scenarios.py` exit 0, `build_checks.py route [--pipeline] --json` e `check_specify.py --status` (nao-`approved` para com "os cenarios estao desatualizados: refaca a specify"); `--pipeline` em v1 -> `route` sai 1, a frase e nenhuma acao; Phase 1 passo 8 ganhou o paragrafo "Test-first steps (plan v2)" (um subagente novo por invocacao, briefing de `build_brief.py`, transicao por exit, 3 tentativas por fase, 10 invocacoes, `ESCALATED` com as 4 opcoes da ITF-014, nunca oferecer mover o baseline; `no-scenario` mantem o contrato e grava `record`); Phase 2 passo 12 roda o bloco de fim de plano (item 9 do Procedimento: `full`, `uncovered`, `record --step 0`, `export`, `demo` mostrado ao usuario, congelamento do M1 com `drift_report.py --feature <slug> --moment M1 --freeze --at <UTC>`) mesmo com `--skip-checks`. Corpo: 254/500 linhas (era 253); o aviso de citacao "plan-000013" na linha 136 sumiu.
- `implement-test-first.md`: nova secao "Procedimento do `/implement`" com os comandos exatos de cada transicao (o detalhe saiu do SKILL.md, como pedido).
- `step_notes.py` (minimo): `append --pipeline on|off --red-reason-ok true|false|null` escreve as linhas `- pipeline:` e `- red-reason-ok:` depois de `- gate:`; `parse` as le (`StepNote.pipeline`, `StepNote.red_reason_ok`); `--gate-json`/`--gate-attempts` intocados. 2 testes novos em `test_step_notes.py`. Os 2 achados de `ruff` em `step_notes.py` (RUF100 na linha do `import project_config`, UP012 no `append_record`) sao pre-existentes, em linhas que nao toquei; deixei como estavam.
- `extended-cycle-contract.md`: linha "Implementacao" no CYC-025 e regra nova **CYC-030** (motor do teste-primeiro e onde grava; com "Ruptura que pode provocar"). Desvio do "so linha de ponteiro": a instrucao pede regra CYC nova numerada a partir da maior existente.
- Dry-run (`route`, golden em `test_build_checks.py`): v1 com testes -> legacy, tdd, legacy, tdd, legacy (a rota de antes: TDD onde `Tests:` nao-N/A, ordem legada onde N/A); v1 de documentacao -> 7 x legacy; v2-completo -> no-scenario, test-first x3, no-scenario (com os motivos); `--pipeline` em v1 -> a frase e exit 1. Teste de texto: o version check aparece antes do paragrafo test-first; a frase do `stale` e o "never offer to move the baseline" estao no SKILL.md.
- Verify: nenhum arquivo de portao, hook ou `settings` no diff; `run_all_checks.py` igual ao baseline; pytest do harness 12 failed / 1437 passed.

### Step 7 -- reflection-on-action | 2026-10-06 19:04 UTC | Escrever o ramo v2, --pipeline, o loop e a escalada no /implement
- happened: Estendi o version check e o passo 8 do Auto Mode, a Phase 2 e o Manual Mode com ponteiros a norma; a norma ganhou o Procedimento com os comandos; step_notes ganhou pipeline e red-reason-ok; o contrato ganhou CYC-030.
- deviated: O roteamento do SKILL.md virou uma ferramenta (build_checks.py route) com golden, em vez de so texto; o fim do plano roda mesmo com --skip-checks para o D3a nao ficar sem full.
- less-sure: Se um orquestrador real segue nove itens de Procedimento sem se perder; isso so o piloto mostra.
- gate: not-installed

### Step 8 -- ensaio ponta a ponta (2026-10-06)

**Ensaio, nao piloto.** Projeto descartavel no scratchpad (fora do repositorio), venv descartavel (`uv venv` + pytest 9.1.1, pytest-bdd 9.0.0, pytest-cov 7.1.0, ruff 0.16.10, radon 6.0.1, mutmut 3.8.0). **Simulado**: os papeis (Tester, Coder, Cleaner, Hardener) sao arquivos escritos por um roteiro (como no ensaio do plano de hooks); as acoes humanas (baseline inicial, aceitar baseline, subir o teto uma vez) tambem; o `pyright` e um esboco que sai 0 (o pyright real nao roda neste ambiente: node sem `libatomic.so.1`). **Rodou de verdade**: pytest-bdd com o plugin instalado por `install-plugin`, `build_checks.py` (route, red-check, freeze, scope, green-check, crap, uncovered, baseline, record, status, export, demo), `build_brief.py`, `gate.py --fast/--full` (ruff, pytest+cobertura de ramos, radon/CRAP, marcadores, **mutmut real** com `--files`), `check_plan_scenarios.py`, `check_specify.py --status`, o hook `Stop` real e o `drift_report.py` do plan-000014 (congelamento do M1 e relatorio). Feature: `contas-da-semana` (a raiz aprovada das fixtures do 000012: 3 REQs, 4 cenarios, um Outline; o plano tinha 5 cenarios no texto -- desvio: 4) e o plano `v2-completo` (5 steps: 1 infra `no-scenario`, 3 `test-first`, 1 refactor `no-scenario`). `--pipeline` ligado so no step 2 (caso a).

| Caso | Esperado | Obtido |
|---|---|---|
| (a) feliz com `--pipeline` (step 2) | vermelho certo, verde, Cleaner dispara, Hardener mata sobrevivente | RED try 1 ok; GREEN try 1 (scope 0, freeze 0, green-check 0, gate fast PASS); `crap` acha `contas_da_semana` CRAP 9.0 > 8 (CC 9, coberta) -> Cleaner refatora para uma compreensao; depois, nenhuma acima do alvo; gate `--full --files` acha **4 sobreviventes** (categoria 6) -> Hardener escreve 5 testes de limite (-1, 0, 7, 8 dias; conta paga) e 2 perguntas ao citizen; gate full PASS, 0 sobreviventes; scope do Hardener 0; status PASS |
| (b) vermelho por import | R1, o Tester corrige | step 3 RED try 1: `R1` (+ `R7`, nenhum codigo do step executado); try 2 ok |
| (c) Coder edita `.feature` | scope/freeze barram | step 3 GREEN try 1: `ITF-008` (scope) e `ITF-007` (freeze) no `.feature` |
| (d) cenario `skipped` | step nao passa | GREEN try 2: `ITF-009`, `Desfazer...` = `skipped`, `Marcar...` = `passed` |
| (e) teto | `ESCALATED`, progress, retomada | try 3 falha de novo -> `ESCALATED` gravado no `gate.json` e linha `- itf: ... ESCALATED` no progress; `status` = `ESCALATED`; o humano "sobe o teto uma vez" -> `status` = `GREEN`; try 4 PASS |
| (f) baseline movido pelo humano | `PASS_WITH_BASELINE`, `baseline_moved = true` | step 3 REC: `PASS_WITH_BASELINE`, `baseline_moved: true`; no fim `full.category` nao virou PASS_WITH_BASELINE porque o `full` falhou (categoria 6, `MUTATION`) |
| (g) cenario ja verde | escalada | step 4 (Outline "A lista abre logo"): `R1`, `already_green: true`, `escalate: true` -- o cenario ja era entregue pelo codigo do step 2 (o `Quando` e o mesmo); status `ESCALATED` |
| (h) `stale` no meio | parada | `.feature` editado: `--status` = `stale` (`feature`); o run para (revertido em seguida) |
| (i) `Stop` hook com arvore vermelha | ate 3 barras e liberacao | chamadas 1-3: exit 2 ("Quality gate FAIL (exit 3)"); chamada 4: exit 0 ("released after 3 blocks; the human decides") |
| (j) plano v1 | rota igual ao golden | `route`: v1 com testes = legacy, tdd, legacy, tdd, legacy; v1 de documentacao = 7 x legacy; `--pipeline` em v1 = a frase, exit 1 |

Medidas (n = 1 ensaio, 5 steps; numeros brutos; tempos de parede das ferramentas nesta maquina):

| Step | Modo | Invocacoes de papel | Tentativas RED / GREEN | Cleaner (funcoes acima do alvo) | Hardener (sobreviventes) | Tempo por fase (s) | Status |
|---|---|---|---|---|---|---|---|
| 1 | no-scenario | 1 | -- | -- | -- | gate 0.37 | PASS |
| 2 | test-first `--pipeline` | 4 (tester, coder, cleaner, hardener) | 1 / 1 | 1 | 4 | pre 0.21, red 0.34, green 0.81, clean 0.90, hard 2.91, rec 0.27 | PASS |
| 3 | test-first | 6 (tester x2, coder x4) | 2 / 4 (teto + 1) | nao rodou | nao rodou | pre 0.22, red 0.68, green 2.18, rec 0.28 | PASS_WITH_BASELINE |
| 4 | test-first | 1 | 1 / -- | -- | -- | pre 0.21, red 0.33 | ESCALATED |
| 5 | no-scenario | 1 | -- | -- | -- | gate 0.42 | PASS |
| fim | -- | -- | -- | -- | -- | full 1.55 | full FAIL (1 sobrevivente em `pagamento.desfazer`, step sem `--pipeline`) |

- Briefings (caracteres): tester 2198, 2418, 2876, 2800; coder 1485, 1672, 1706, 1706, 1706; cleaner 1292; hardener 3291. Nenhum cortado (`truncated: false`; teto 24 000).
- Passes pulados: com `--pipeline` (1 step), Cleaner e Hardener dispararam ambos (0 de 1 pulados). Sem `--pipeline` o `full` do fim achou 1 sobrevivente no step 3: leitura a favor de rodar o Hardener (Decisao 1 fica em A ate o piloto; dado de n = 1).
- `gate.json` resultante conferido contra a costura com o 000008: `fast`, `full` (`MUTATION`, exit 6), `ts`, `baseline_moved: true`, `build.scenarios` com as 4 chaves **iguais ao `index` do lock**, `build.steps` 1-5 com modo e status, `build.feature {touched_total 10, touched_uncovered 1, base, baseline_moved}`. `export` gravou `runner/cucumber.json`, `drift/red-reason.json` (3 true, Outline false) e `drift/coverage.json`; `drift_report.py --moment M1 --freeze` gravou `drift/M1.json`; o relatorio leu tudo: D1 3/0/0, D2 4/0/0, D3a 0/4/0 (full FAIL e baseline aceito tornam o D3a todo descoberto, como o DRM-004 manda), D3b 9/1/0 (cobertos/descobertos/nao medidos).
- `demo` (registro do citizen): 3 cenarios "demonstrado", o Outline "nao demonstrado" (ja passava antes do codigo) e as 2 perguntas; nenhum numero tecnico fora do texto dos cenarios.

Achados do ensaio (corrigidos neste step):
1. **`scope` contra o comeco do step acusava os arquivos do Tester** (ITF-007 no proprio teste congelado): o vermelho nao e commitado, entao o diff do Coder incluia o trabalho do Tester. Correcao: base por fase (`git add -A && git write-tree && git reset -q`) no Procedimento; `_changes` trata o arquivo do instantaneo que voltou a ser nao rastreado (o `git diff <tree>` o mostrava como `D`).
2. **`check_skeleton` falhava com arquivo de codigo ainda inexistente** (vermelho por import, antes do esqueleto): exit 2 sem achado. Correcao: arquivo ausente e pulado (R7 cobre o caso).
3. **Baseline aceito pelo humano dentro da fase do Coder** era acusado pelo `scope` (ITF-008). Regra no Procedimento: o humano age entre fases; o REC le o baseline.
4. **`demo`** mostrava "nao medido" para cenario com registro de vermelho falso; passou a "nao demonstrado".
5. **Lint de teste do gate x pytest-bdd**: `def test_x(): pass` com `@scenario` falha o lint (todo `def test_*` precisa afirmar) e `scenarios(FEATURE)` vincula os cenarios dos outros steps (indefinidos -> R6). Padrao adotado no agente `scenario-tester`: `test_<nome> = scenario(FEATURE, "<nome>")(_vincular)`. Candidato a follow-up no gate (aceitar funcao de cenario do pytest-bdd), fora deste plano.
6. **Plugin e o `ruff` do projeto**: a configuracao de lint de cada projeto pode acusar o plugin copiado; o template ganhou `# ruff: noqa` e foi formatado com `ruff format --isolated` (o gate roda `ruff format --check .`).

### Step 8 -- reflection-on-action | 2026-10-06 19:14 UTC | Ensaiar o ciclo ponta a ponta em um projeto descartavel e medir
- happened: Rodei os casos (a) a (j) com papeis roteirizados e ferramentas reais (pytest-bdd, gate com mutmut, hook Stop, drift_report); todos deram o esperado depois de quatro correcoes; o gate.json e os arquivos do plan-000014 foram lidos pelo relatorio de divergencia.
- deviated: Achei e corrigi: scope contra o comeco do step (virou base por fase), skeleton com arquivo ausente, baseline do humano dentro da fase, estado do demo; a feature tinha 4 cenarios, nao 5; pipeline so no step 2.
- less-sure: n = 1 e papeis roteirizados: os numeros de tentativas e findings nao dizem nada sobre um subagente real; o pyright foi esbocado.
- gate: not-installed

### Step 9 -- fechamento: costura, consistencia, C1 e pendencias (2026-10-06)

- `implement-test-first.md` ganhou "Quem alimenta e quem consome" (planos 000007-000012, item 8 = 000014, item 9 = 000015, item 10 = 000016, cada linha com regra ITF); a tabela "Costura com o 000008" ja estava desde o Step 2.
- Vocabulario conferido contra 000007-000012: degraus D1/D2/D3a/D3b, estados coberto/descoberto/nao medido, chave `<slug>/<arquivo>.feature::<nome>` (igual ao `index` do lock, provado no ensaio), `stale` e `rev` (lidos de `check_specify.py --status`, nunca recalculados), `PASS_WITH_BASELINE` (DRM-004), `red_reason_ok`, `baseline_moved`, `touched_uncovered` (DRM-006). Uma divergencia corrigida: `final.test_result` passou a usar os nomes do DRM-006 (`xfail`, `absent`) em vez dos do pytest (`xfailed`, `missing`).
- Checks finais: `test_build_checks.py` 71, `test_scenario_report.py` 20, `test_build_brief.py` 10, `test_step_notes.py` 26 passed; pytest do harness 12 failed (os pre-existentes) / 1437 passed; `uvx ruff check` limpo nos arquivos novos (os 2 achados antigos de `step_notes.py` ficam); `pyright` **nao provado** (ambiente); `run_all_checks.py` 14 FAIL, contadores 17/2/9, igual ao baseline; `skill-body-length` do `/implement` 254/500. `/critique validate` como skill nao rodou dentro deste executor; o nucleo deterministico dele (`run_all_checks.py`) rodou a cada step.
- Diff total sem arquivo de portao, hook, `settings` nem `product-design/`. C1: nenhum nome de parceiro, instituicao ou pessoa nos arquivos novos (varredura do diff; sem lista de termos registrada). Ponteiros: `extended-cycle-contract.md` +9 linhas (uma linha de "Implementacao" no CYC-025 e a regra nova CYC-030 -- desvio do "no maximo uma linha", pedido pela instrucao de numerar regras CYC novas); `conftest.py.example` +6 linhas de docstring.

Decisoes pendentes (todas no default, `[default; aceito 2026-10-06]`): 1 = A (`--pipeline` opt-in; vermelho sempre no v2), 2 = A (`gate.json.build` + exportacao), 3 = A (3 por fase, 10 por step), 4 = A (`full` no fim quando `GATE_FULL_CMD` existe), 5 = B (alvo 8, piso 6), 6 = A (ja verde = escalada), 7 = B (`--pipeline` em v1 recusado).

Textos sugeridos ao designer (aplicar com `/implement --manual` ou `/design`, nao aplicados aqui):
1. **Contrato do 000007** -- ja feito como CYC-030 (o registro do build mora em `gate.json.build` e e exportado). Nada a acrescentar.
2. **`drift-metric.md` (arquivo do 000008; reservado ao plan-000014 nesta rodada)**, no DRM-006, coluna `baseline_moved`: "Fonte: `build_checks.py baseline` (hash de `quality-baseline.json` na base do step ou do plano contra o arquivo atual), gravado em `gate.json.build.steps[N].baseline_moved`, `gate.json.build.feature.baseline_moved` e `gate.json.baseline_moved` (implement-test-first.md, ITF-017)." Coluna `red_reason_ok`: "Fonte: `build_checks.py red-check` (R1 a R8), gravado em `gate.json.build.scenarios[<chave>].red.reason_ok` e exportado para `drift/red-reason.json` (ITF-005, ITF-023)."
3. **Aviso do D3a**: "Plano v2 sem `GATE_FULL_CMD` grava `full: null`; o D3a fica `nao medido` (`NM-SEM-GATE`) mesmo com todos os testes verdes (ITF-019)." -- cabe no DRM-004 ou na lacuna 4 do `drift-metric.md`.
4. **`feature-layout.md` § `gate.json`** (emenda aditiva): "Chaves aditivas: `baseline_moved` (bool) e `build` (registro do teste-primeiro, esquema em implement-test-first.md, ITF-015). Leitores ignoram chave desconhecida."
5. **`.claude/rules/harness-structure.md` § Subagent Prompts**: "19 subagent prompts" e uma linha "**Test-first role agents** (3): scenario-tester, cleaner, hardener -- one job each, fed by `build_brief.py`; the Coder stays the dynamic executor."
6. **`gherkin-spec-format.md` secao 10**: uma linha "Com o teste-primeiro, o plugin `scenario_report` (ITF-016) substitui o `conftest` modelo."

Propostas ao designer (proximo D livre: **D-014**; D-013 pode ser usada pelo plan-000014):
- **D-014 (proposta)**: "Base por fase no teste-primeiro: como o vermelho nao e commitado (o hook de commit o recusaria), o escopo de cada papel e medido contra um instantaneo da arvore no inicio da sua fase (`git write-tree`), e o humano so move baseline ou limiar entre fases." Contexto: achado 1 e 3 do ensaio. Alternativa rejeitada: commitar o vermelho com `--no-verify` (negado, S2).
- **Proposta de follow-up no gate (plano do portao, fora deste)**: o lint de teste do gate (`def test_*` sem assert) recusa a forma idiomatica `@scenario` do pytest-bdd; aceitar funcao decorada com `scenario` ou documentar o padrao `test_x = scenario(...)(_vincular)` no README do gate.

Lacunas para os proximos planos:
- **plan-000014**: (a) `runner/adapter.json` e `gate.json.adapter` nao sao escritos (ausente = adaptador existe; certo para Python/pytest-bdd); (b) o relatorio le so `runner/cucumber.json`; o relatorio do plugin (`scenario_report`) tem tambem `undefined`, local da funcao do step e `collect_errors` -- se o 000014 quiser o JUnit/plugin para o `@skip` e o step indefinido que o Cucumber JSON omite, o `export` pode copiar o relatorio do plugin para `runner/`; (c) no ensaio, full FAIL + baseline aceito deixaram o D3a todo `descoberto` (4/4) mesmo com 3 cenarios demonstrados -- e o DRM-004 aplicado como esta; o 000014/designer decide se `full` FAIL por mutante de outro step deve contar contra todos os cenarios; (d) os textos 2 e 3 acima.
- **plan-000015**: quickguide pt-BR do `--pipeline`, da escalada (4 opcoes) e da demonstracao por cenario; `/seja-setup` oferecer `install-plugin`; o `pytest_plugins` em `tests/conftest.py` falha se o projeto tiver `conftest.py` de topo com outra raiz (Step 4); textos 4, 5 e 6 acima; o modo `review` do `scenario-tester` ainda nao e chamado pelo `/plan` (SPC-009): falta uma linha no `_internal/plan/standard/SKILL.md` (nao editada aqui para nao abrir a ordem de edicao dos SKILL.md).
- **plan-000016 (piloto)**: os numeros do Step 8 sao de papeis roteirizados (n = 1): medir com subagentes reais invocacoes, tentativas, findings do Cleaner e do Hardener por step e tempo por fase para fechar a Decisao 1; medir se o teto de 24 000 caracteres corta algo; medir o custo da mutacao cumulativa (`--files` restringe a mutacao a todas as funcoes dos arquivos tocados, nao so as do step: lacuna 10 do plano).

Achados (resumo do plano):
- O motor esta inteiro e foi ensaiado de ponta a ponta com ferramentas reais; quatro defeitos so apareceram no ensaio (base por fase, esqueleto ausente, baseline do humano, estado do demo) e foram corrigidos com teste.
- O vermelho pelo motivo certo e decidido por forma (R1-R8); a adequacao semantica continua com a auditoria humana do 000008 (lacuna 12 do plano).

### Step 9 -- reflection-on-action | 2026-10-06 19:17 UTC | Fechar: costura com os vizinhos, consistencia, C1 e pendencias
- happened: Acrescentei quem alimenta e quem consome, alinhei test_result aos nomes do DRM-006, rodei os checks finais (iguais ao baseline) e registrei decisoes, textos sugeridos, a proposta D-014 e as lacunas para 000014-000016.
- deviated: O contrato recebeu uma regra nova (CYC-030) em vez de uma linha so; o modo review do scenario-tester ficou sem chamada no /plan.
- less-sure: Se o designer quer o D3a inteiro descoberto quando o full falha por mutante de um step que nao teve --pipeline.
- gate: not-installed

### Correções da revisão (orquestrador)

- Snapshot por fase: novo `build_checks.py snapshot` (`snapshot_tree`) copia o índice para um arquivo temporário e roda `git add -A` e `git write-tree` com `GIT_INDEX_FILE`; o índice real e o staging do usuário não mudam. A norma ITF (`implement-test-first.md`) passou a citar `BC snapshot` no lugar de `git add -A && git write-tree` + `git reset -q`. SKILL.md e agentes não citavam o comando. Teste: repo temporário com arquivo em staging e outro solto; a árvore tem os dois e `git diff --cached --name-only` fica igual.
- Timeouts: todo `subprocess.run` passa por `_run` (60 s); `TimeoutExpired` vira `BuildError` (exit 2, sem traceback). Teste com `subprocess.run` simulado que não termina.
- Filtro do citizen: `demo_text` descarta pergunta do Hardener com token técnico (`TECH_TOKENS` importado de `check_specify.py`, mais número de linha e `.py`). `demo` imprime essas perguntas em stderr, com a ressalva "Pergunta com termo técnico, fora do registro do citizen", e com `--out` grava `<out>.power-dev.md`. Testes positivo e negativo.
- Verificação: 130 testes verdes nos quatro arquivos; ruff limpo; `run_all_checks.py`: 14 FAIL de sempre (17 undefined, 2 error(s), 9 error(s)).
