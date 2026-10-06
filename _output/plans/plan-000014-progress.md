# Progress -- Plan 000014

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

## Step 1 -- terreno, CLIs reais e skills atuais (2026-10-06)

Repositorio de execucao: este (sem prefixo `open-seja/`); fixtures em `.claude/skills/scripts/tests/fixtures/<tema>/`; o progress "no Doutourado" e este arquivo. Nada foi escrito fora do progress neste step.

**(a) Planos e identificadores reais.** 000007 a 000012 estao aqui. IDs: `CYC-001..029` (contrato), `GRL-NNN` (`grill-phase.md`), `GHK-001..019` (`gherkin-spec-format.md`), `SPC-NNN` (`specify-phase.md`), `PFS-001..015` (`plan-from-scenarios.md`), `DRM-001..014` (`drift-metric.md`). Colunas derivadas (DRM-006): `scenario_status`, `test_result`, `red_reason_ok`, `touched_uncovered` (+ `touched_total`), `baseline_moved`. Razoes `NM-*` (DRM-009): as 9 do plano mais `NM-SEM-ADAPTADOR-RUNNER`, `NM-SEM-ADAPTADOR-GATE`, `NM-SEM-INDICE-BRIEF`. Esquema do relatorio: `{schema_version, feature, momento, degraus{D1,D2,D3a,D3b: n,cobertos,descobertos,nao_medidos,D,razao_nm}, leituras{cadeia_completa,cenarios_orfaos,cenarios_sem_tag,escada_fechou_sem_capturar,o1,d0}, ressalvas}` (nao existe `entradas`/`auditoria`/`delta` no DRM-007; o plano os acrescenta: vao ao lado, ver DRP).

**(b) `casos.json`.** `.claude/skills/scripts/tests/fixtures/drift/casos.json`: `{schema_version, descricao, casos{<nome>: {entrada, esperado}}}`; 6 casos (`normal`, `nada-medido`, `specify-pulado`, `orfao-e-sem-tag`, `escada-fechada`, `amostra-pequena`). `entrada`: `feature, momento, intent{status}, scenarios_status, runner{adaptador,relatorio}, gate{full,baseline_moved}|null, reqs[str], scenarios[{id,tags,test_result,red_reason_ok}], touched{total,uncovered}|null, oraculo{n,falham}|null, auditoria[]`. `esperado` = DRM-007. Observacoes que o calculador tem de respeitar: `cadeia_completa` do `nada-medido` e **0** (D3a nao medido), D3b `nada-medido` tem `nao_medidos = touched.total` com `["NM-SEM-GATE","NM-SEM-COBERTURA"]`, `specify-pulado` e `{nao_aplicavel, razao_nm}`, `amostra-pequena` = menos de 8 REQs.

**(c) CLIs reais (todas existem, `schema_version: 1`).**
- `check_features.py [raiz] [--feature s] --json --matrix`: exit 0/1 (1 = achados GHK; o JSON sai igual)/2; `features[]{slug,status,scenarios_approved}`; `matrix{slug{status,scenarios_approved,reqs{REQ{state: ativo|retirado, scenarios[{key,file,name,line,rows,disabled,nao_faz,journey}]}}}}`. Nao traz o texto do REQ nem as tags de cenario alem da chave: o calculador junta pelo `reqs` da matriz (tag = REQ dono).
- `check_specify.py [raiz] --feature <slug> --status [--json]`: **exige `--feature`** (sem ele exit 2); sem `--json` a saida e so a palavra; `--json`: `{status: approved|stale|draft|missing, reasons[], reqs[], ressalvas[]}`, sempre exit 0.
- `check_plan_scenarios.py <plano> [--root r] --json`: `{version, feature, specify, status, steps[{n,scenarios[],scenarios_na,tests_na}], findings, matrix?}`; plano v1 sai com `version: 1`, `unverified: true`, sem ler o corpo.
- `check_intent.py <intent.md> --d0` (caminho obrigatorio; sem `--strict`): `{d0: {estado: medido, frases, residuo[{frase,nota}]} | {estado: nao_medido, razao_nm}}`.

**(d) Relatorio do runner e gate.** O contrato e **Cucumber JSON** (CYC-027, `gherkin-spec-format.md` secao 8), nao JUnit como o plano diz: desvio ja registrado pelo 000010. Chave `<slug>/<arquivo>::<nome>` dos dois ultimos componentes do `uri`; tags no proprio relatorio; mapeamento de estados executavel em `.claude/references/template/feature-example/cucumber_states.py.example` (copiado, nao importado: e `.example`). `gate.json`: `{schema_version, fast{exit_code,category,ref}|null, full|null, ts}`; **nao tem** `baseline_moved`. **Nao existem** em nenhum plano: o registro "vermelho pelo motivo certo", a cobertura so dos testes de cenario, a base do diff, o caminho do relatorio do runner dentro de `features/<slug>/` (o 000013, mesma Wave, os produz). Este plano fixa caminhos aditivos em `drift-report.md` (DRP-001) e trata ausencia como `nao medido`.

**(e) Skills.** `reflect/SKILL.md` v2.0.0 (fluxo conversacional A a D, Step B ja menciona "drift report recorded by /plan and /implement"; regra nao prescritiva testada em `test_generate_reflection_report.py`); `explain/SKILL.md` v1.1.0 (`drift [scope]`; despacho para `_internal/explain/drift/SKILL.md`, Step A.1 a A.7); drift internal v1.0.0. Nenhum dos tres foi tocado pelos planos 000007 a 000012.

**(f) Plano 000074.** Nao entregou `lint_controlled_language.py` nem `controlled-language.md`. Existem `html_report.py` e `md_to_html.py` (anteriores, de outro uso). Decisao 3 = B: o HTML aqui e proprio, autocontido, escapado; limite de voz por contagem propria (25 palavras por frase, 6 frases por paragrafo).

**(g) Baseline.** `run_all_checks.py` (timeout 200, `< /dev/null`): 19 PASS / 14 FAIL, contadores 17 undefined / 2 error(s) / 9 error(s). pytest (comando acima): 1120 passed / 12 failed (os 12 pre-existentes).

**(h) C1.** A lista de termos de C1 e do orquestrador; nao a escrevo. Faco so `git grep` por termos fornecidos fora do ledger quando houver; nenhum nome de pessoa/parceiro/instituicao nos arquivos novos.

**Fontes da matriz: estado.**

| Fonte | Estado | Caminho / observacao |
|---|---|---|
| `intent.md` (REQ, status, rev, serve, Retradução, Fora do escopo, F/A) | existe | via `check_features --matrix` e leitura propria das secoes |
| `*.feature` + chave | existe | `check_features --matrix` |
| `scenario_status` | existe | `check_specify --feature s --status --json` (nunca o campo `scenarios_approved`) |
| plano v2 (cenario -> step) | existe | `check_plan_scenarios --json` (informativo, fora do vetor) |
| relatorio do runner | rascunho | Cucumber JSON; caminho nao fixado pelos planos -> `features/<slug>/runner/cucumber.json` (DRP-001) |
| `gate.json` | existe (esquema) | sem `baseline_moved` e sem `adapter`; campos aditivos opcionais (DRP-001) |
| registro de vermelho | ausente | `features/<slug>/drift/red-reason.json` (DRP-001), produzir e do 000013 |
| cobertura por cenario e base do diff | ausente | `features/<slug>/drift/coverage.json` (DRP-001) |
| `audit.json`, `oracle-result.json`, retradução pos-codigo | ausente | humano / `/reflect`; `features/<slug>/drift/` |
| indice do brief (D0) | existe | `check_intent --d0` |
| marca de adocao (leitura reversa) | ausente | `features/adoption.json` proposto (DRP-014) |

**Lacunas encontradas contra "Lacunas e conflitos" do plano.**
1. (plano 1) Confirmada e maior: faltam tambem o caminho do relatorio do runner, `baseline_moved` e o sinal de "sem adaptador" (a distincao `NM-SEM-ADAPTADOR-*` x `NM-SEM-*` do DRM-009 nao tem fonte de dado). Solucao aditiva: arquivos `runner/adapter` e `gate.json.adapter` opcionais em DRP-001; texto para o 000013 ao fim.
2. (plano 4) `casos.json` existe e o calculador o adota sem adaptador; o plano fala de JUnit, o contrato e Cucumber JSON: segue o contrato.
3. Plano diz "`check_features --matrix` -> `scenarios_approved`": segue-se `--status` (decisao fechada 3). `check_specify --status` exige `--feature` e a palavra so sai sem `--json`: uso `--json`.
4. `cadeia_completa` x D3a nao medido: o golden `nada-medido` exige `0`; a instrucao do orquestrador exige tratar como nao medido. Solucao: `compute_report` devolve o golden (0) e o relatorio acrescenta `cadeia_indeterminada` (e o texto diz "nao medida"). Proposta de emenda ao `drift-metric.md` (reservado): ver achados ao fim.
5. A matriz de `check_features` nao traz as tags de cada cenario, so a chave sob o REQ; tag = REQ dono (cenario com varias tags aparece sob varios REQs com a mesma chave: o calculador junta por chave).

### Step 1 -- reflection-on-action | 2026-10-06 18:32 UTC | Terreno e CLIs reais
- happened: Li as CLIs reais, o casos.json e as skills; registrei a tabela de fontes e cinco lacunas.
- deviated: O runner e Cucumber JSON, nao JUnit como o plano diz.
- less-sure: Os caminhos aditivos de runner, vermelho e cobertura sao minha proposta, nao contrato.
- gate: not-installed

### Step 2 -- reflection-on-action | 2026-10-06 18:36 UTC | Referencia normativa drift-report.md
- happened: Escrevi DRP-001..019 com fontes, estado x efeito do --status, frases NM, auditoria, retradução lado a lado e leitura reversa.
- deviated: Acrescentei dois codigos de leitura e caminhos aditivos de runner, vermelho e cobertura; runner e Cucumber JSON.
- less-sure: A marca de adocao e o formato de red-reason.json e coverage.json sao propostas minhas.
- gate: not-installed

## Step 3 -- fixtures e testes que falham (2026-10-06)
- 26 arvores em `.claude/skills/scripts/tests/fixtures/drift_report/<caso>/` (todas fictícias, feature `contas-da-semana`; `README.md` com uma linha por caso) + `test_drift_report.py` (6 golden de `casos.json`, determinismo, consistencia de cada `esperado.json`, um teste por arvore, stale com spy, skip/xfail, gate corrompido). `esperado.json` por caso foi escrito a mao, nao gerado pelo calculador.
- Falha esperada: `pytest test_drift_report.py` -> `ModuleNotFoundError: No module named 'drift_report'` (1 error na coleta).
- Recontagem independente (script solto, sem o calculador): os 26 `esperado.json` fecham `n = cobertos + descobertos + nao_medidos`, `D = descobertos/(cobertos+descobertos)` (4 casas) ou `n/a`, e todo `nao_medido` traz razao: 0 divergencias. Recontagem do D2 dos golden a partir de `entrada` (cenarios com tag valida e `absent/skipped/xfail`): `normal` 12/2, os demais 0, igual ao `esperado`.
- Desvio: `esperado.json` e parcial (degraus completos + as leituras e ressalvas que o caso exercita), nao o relatorio inteiro; o plano previa o inteiro. Fixtures em `.claude/skills/scripts/tests/fixtures/` (nao `tests/fixtures/`).

### Step 3 -- reflection-on-action | 2026-10-06 18:39 UTC | Fixtures e testes que falham
- happened: Criei 26 arvores de projeto e o modulo de testes; falha por ModuleNotFoundError.
- deviated: esperado.json e parcial por caso, nao o relatorio inteiro.
- less-sure: O formato de delta e das leituras novas nos testes fixa a API que o Step 4-6 vai seguir.
- gate: not-installed

### Step 4 -- reflection-on-action | 2026-10-06 18:40 UTC | Calculador puro compute_report
- happened: Implementei analyze e compute_report; os 6 golden e os casos de calculo passam.
- deviated: compute_report devolve so o DRM-007; cadeia indeterminada e as leituras novas ficam em analyze/build_report.
- less-sure: Populacao do D3a com D2 nao medido e minha leitura do DRM-004; esta nas propostas.
- gate: not-installed

## Step 5 -- carregador `load_matrix` (2026-10-06)
- `load_matrix` junta `check_features --matrix --json` (por subprocesso, lista de argumentos, sem shell), `check_specify --status --json` (sempre; `status_fn` injetavel; ausente -> ressalva "aprovação não verificada"), runner Cucumber JSON (mapeamento copiado de `cucumber_states.py.example`; contagem de steps do `.feature` para o "step indefinido omitido"), `gate.json`, `drift/*.json`, `check_intent --d0`, `check_plan_scenarios --json` (coluna `step_dono`, fora do vetor), hashes SHA-256 das entradas e a leitura reversa. `DriftInputError(arquivo, motivo)` para JSON invalido; fonte ausente e `nao medido`.
- Achados: (1) a matriz do `check_features` nao lista cenario sem tag nem com tag orfa; vem dos achados `GHK-002` e `GHK-004` do mesmo JSON. (2) `check_features.py` importa `check_intent.py`: copiar um sem o outro quebra. (3) Plano v1 e `Specify: skipped` sao lidos so pelo cabecalho, antes de qualquer fonte.
- Testes: 81 passam; os 2 que falham (`ok-m2-deriva`, `denominador-muda`) esperam o delta do Step 6. Integracao com os tres scripts reais sobre `plan_scenarios/_raizes/aprovada`: verde.

### Step 5 -- reflection-on-action | 2026-10-06 18:43 UTC | Carregador load_matrix
- happened: Liguei os tres checks por subprocesso, o runner Cucumber, gate, registros e a leitura reversa; testes de ausencia e de arquivo corrompido.
- deviated: Cenario sem tag e orfao vem dos achados GHK-002/004, nao da matriz.
- less-sure: Os formatos de red-reason.json e coverage.json sao propostos; ninguem os produz ainda.
- gate: not-installed

## Step 6 -- instantaneos, delta, auditoria e CLI (2026-10-06)
- `freeze` (escrita atomica; `M1.json` nunca sobrescrito: `FileExistsError` -> exit 2, arquivo intacto), `compare` (numerador e denominador dos dois lados, `denominador` por escrito, `mudou` por hash, `NM-SEM-M1`), `read_audit` (valor fora de sim/parcial/nao -> erro com o REQ), `audit_sample` (sha1, `ceil(30%)`, ordem independente da entrada) e a CLI (`--feature --plan --moment --freeze --compare --audit-sample --json --md --citizen --html --as-coded --out --at`). Sem `--feature`: todas as pastas de `features/` em ordem alfabetica; sem `features/`: uma linha, exit 0.
- Decisao 2 (quem congela o M1): so a CLI `--freeze` e a degradacao `NM-SEM-M1`; a fiacao no `/implement` e do 000013/000015 (texto sugerido ao fim).
- `--md`, `--citizen` e `--html` ainda respondem exit 2 com aviso "chegam no Step 7"; so `--json` (padrao) funciona neste commit.
- 96 testes passam; `run_all_checks` igual ao baseline.

### Step 6 -- reflection-on-action | 2026-10-06 18:45 UTC | Instantaneos, delta, auditoria e CLI
- happened: Escrevi freeze, compare, audit_sample e a CLI; M1 existente e recusado e o arquivo fica intacto.
- deviated: Os renderizadores ainda nao existem; --md/--citizen/--html saem com aviso neste commit.
- less-sure: Se o delta deve aparecer sempre no M2 ou so com --compare; segui o plano (--compare).
- gate: not-installed
