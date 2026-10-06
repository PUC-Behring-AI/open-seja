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

### Step 2 -- emendas aditivas (2026-10-06)

- `feature-layout.md` (+33, 0 remoções): árvore completa com `adoption.json`, `scenarios.lock.json`, `runner/`, `drift/` (M1.json imutável, `M2-<at>.json`, `red-reason.json`, `coverage.json`, `audit.json`, `oracle-result.json`, `retraducao-pos-codigo.md`, HTML) e quem escreve cada um; regra "nada em `drift/` é apagado"; campos `scenarios_*` e o valor `draft` gravado por `--reconcile`; chaves opcionais do `gate.json` (`baseline_moved`, `adapter`, `build`); Outline = um cenário.
- `extended-cycle-contract.md` (+59, 0 remoções): seção "Emendas do item 9" com a tabela das decisões 1-8 no default, ponteiros para CYC-028 (chave) e CYC-029 (proxy do skip), regras novas **CYC-031** (quem congela o M1), **CYC-032** (reconciliação de `scenarios:`), **CYC-033** (ciclo default por upgrade de tag, sem chave), **CYC-034** (quem escreve `adoption.json`, `retraducao-pos-codigo.md`, e quando o relatório usa `--citizen`) e a tabela da ordem de edição dos `SKILL.md`.
- `plan-step.md` (+1): exemplo do campo `Scenarios:` com chave real das fixtures e com `N/A (motivo)`.
- `drift-metric.md` (+12) e `drift-report.md` (+17): fora dos Files do plano (pedido do orquestrador). DRM: REQ retirado fora do denominador, população e ordem do D3a, fonte de `baseline_moved`/`red_reason_ok`, cadeia indeterminada, os dois códigos de leitura, Outline = um cenário, lacuna 6 fechada. DRP-020 (nova): registro `--citizen` quando `scenarios_contract_by: ninguem` ou a pedido; o agente do `/reflect` escreve `retraducao-pos-codigo.md` antes do Step B1.
- **Contradição registrada**: GRL-011 diz "o D1 conta o REQ retirado como descoberto até a reaprovação"; o `drift_report.py` o tira do denominador. Sem efeito prático (até a reaprovação o D1 já é `não medido`); a emenda ao `drift-metric.md` registra isso. GRL-011 não foi reescrito.
- **Para o orquestrador**: anexar ao plan-000007 um "Plan Amendment" dizendo que o texto do Step 3 sobre `Scenarios:` ("`@REQ-...` ou nomes de cenário") foi substituído pela chave `<slug>/<arquivo>.feature::<nome>` (CYC-028, emenda 000012; apontado no contrato pela emenda 000015).
- Verify: `git diff --numstat` só adições (122 linhas, 0 remoções); `grep -c "emenda 000015"` = 7 no contrato, 3 no layout, 1 em `plan-step.md`, 1 em cada arquivo de drift; `run_all_checks.py` 19 PASS / 14 FAIL (mesmo conjunto), 17/2/9; pytest 1440 passed / 12 failed (mesmo conjunto). `check_docs.py` foi de 633 para 639 warnings ("Specific plan ID" nas linhas novas; padrão já presente nessas referências; check_docs já falha no baseline). C1: nenhum nome de parceiro, instituição ou pessoa nas linhas novas.

### Step 2 -- reflection-on-action | 2026-10-06 19:29 UTC | Emendas aditivas ao contrato, ao layout e ao formato de plano
- happened: Acrescentei a arvore completa ao layout, CYC-031 a CYC-034 e a tabela de ordem ao contrato, um exemplo de Scenarios: e as emendas do drift-metric e do drift-report (DRP-020).
- deviated: A chave e o proxy do skip ja existiam (CYC-028/029): so apontei; drift-metric e drift-report entraram fora dos Files; 6 warnings novos de ID de plano no check_docs.
- less-sure: Se escolher o registro citizen pelo campo scenarios_contract_by e o sinal certo do polo citizen.
- gate: not-installed

### Step 3 -- `check_specify.py --reconcile` (2026-10-06)

- Teste primeiro: 12 casos novos em `test_check_specify.py` (`-k reconcile`); vermelho 12/12 por `SystemExit: 2` (argparse: opção desconhecida), o motivo certo.
- `check_specify.py --reconcile [<slug>] [--json]` (CYC-032): com o campo `scenarios: approved` e `--status` diferente de `approved`, troca só essa linha por `scenarios: draft` (`set_frontmatter` + `_atomic_write`: BOM, CRLF e permissão do arquivo mantidos; lock e campos `scenarios_*` intactos). Motivo `reopened` quando a razão inclui `intencao-reaberta`, senão `stale`. JSON: `{schema_version, slug, changed, from, to, reason, reasons}`; sem slug, varre `features/*/intent.md` (`{schema_version, features: [...]}`). Recusa (exit 2, nada escrito): slug fora do padrão (`../x`, `a/b`), pasta que é symlink para fora de `features/`, combinação com `--approve`/`--status`, `--feature` diferente do slug. Nunca exit 1. Frase ao humano: "os cenários voltaram a rascunho, porque <motivo>. Peça nova aprovação."
- Interface conferida contra o JSON real do `--status` (`status`, `reasons`, `reqs`): o `--reconcile` repete `reasons` do status antes da escrita.
- Efeito no `run_all_checks`: a varredura do `check_specify` reprova `scenarios: approved` velho; depois do `--reconcile` a varredura volta a 0 e o `--status` segue `stale` (com `sem-campo` mais as razões de antes) até a specify reaprovar (teste `test_reconcile_then_scan_passes_and_status_stays_stale`).
- Docs: `grill-phase.md` GRL-011 (+1 linha: rodar `--reconcile` ao reabrir e avisar o citizen) e GRL-001 (+1 linha: a grill escreve `features/adoption.json` uma vez, CYC-034); `specify-phase.md` tabela "Entrada e saída" (+1 linha).
- Verify: `test_check_specify.py` 101 passed (os 89 antigos sem edição); `uvx ruff check check_specify.py` limpo; no arquivo de teste há um I001 **pré-existente** (ordem de imports, já no HEAD; não mexi nos imports); pyright não medido (sem `libatomic.so.1`). `run_all_checks.py` 19/14, mesmo conjunto, 17/2/9; pytest 1452 passed / 12 failed (mesmo conjunto).

### Step 3 -- reflection-on-action | 2026-10-06 19:32 UTC | Reconciliar scenarios: no disco quando a grill reabre
- happened: Escrevi 12 testes vermelhos e o --reconcile; o campo vira draft so na feature indicada, lock e resto intactos, idempotente; GRL-011, GRL-001 e specify-phase ganharam uma linha cada.
- deviated: Sem slug o --reconcile varre todas as features; recusa tambem symlink para fora de features/; a linha da marca de adocao foi para GRL-001.
- less-sure: Se a frase ao citizen ao reabrir e o bastante para ele entender que precisa aprovar de novo.
- gate: not-installed

### Step 4 -- `scenarios_state` na matriz (2026-10-06)

- Teste primeiro: 5 casos em `test_check_features.py` e 2 de integração real em `test_drift_report.py`; vermelho por `KeyError: 'scenarios_state'`, `AttributeError` (`SPECIFY_SCRIPT`, `scenarios_state` ainda não existiam) e o texto sem "estado confiável".
- `check_features.py --matrix`: cada feature ganha `scenarios_state` (`approved|stale|draft|missing`, ou `desconhecido` quando `check_specify.py` falta, falha, ou devolve JSON fora do `schema_version: 1`), pedido por subprocesso a `check_specify.py <raiz> --feature <slug> --status --json` (acoplamento por CLI e JSON versionado; `check_specify` importa `check_features`, então o caminho inverso por import faria ciclo). `scenarios_approved` não mudou de significado (valor do campo). O estado só é pedido com `--matrix` (a varredura simples do `run_all_checks` não abre subprocesso; teste `test_plain_scan_does_not_ask_check_specify`). Texto: "estado confiável: <estado>" na linha da matriz. Chave nova no JSON, nenhuma removida; `schema_version` continua 1 (acréscimo).
- Consumidores: `git grep scenarios_approved` em `drift_report.py`, `check_plan_scenarios.py` e `build_checks.py`: **zero** ocorrências (os três já usam `--status`). Integração real (sem stub): feature `spc-013-hash-mudou` (campo `approved`, `.feature` editado) -> matriz `scenarios_approved: true`, `scenarios_state: "stale"`, e `drift_report.py --json` dá D1 `NM-CENARIOS-STALE` com 0 cobertos; `spc-013-aprovado` -> `approved` e D1 medido.
- Docs: `gherkin-spec-format.md` seção 4 (+1 linha: o campo é o valor do disco; o estado confiável é `scenarios_state`) e seção 10 (+1 linha, texto 6 do 000013: o plugin `scenario_report` substitui o `conftest` modelo no teste-primeiro).
- Verify: `test_check_features.py` 167 passed, `test_drift_report.py`, `test_check_specify.py` e `test_check_plan_scenarios.py` verdes sem edição dos testes antigos (645 nos quatro); `uvx ruff check check_features.py` e `test_check_features.py` limpos; `test_drift_report.py` tem um I001 **pré-existente** (já no HEAD). pyright não medido. `run_all_checks.py` 19/14, mesmo conjunto, 17/2/9; pytest 1459 passed / 12 failed (mesmo conjunto).

### Step 4 -- reflection-on-action | 2026-10-06 19:35 UTC | Matriz e consumidores usam --status, nao o campo
- happened: check_features --matrix ganhou scenarios_state pedido por CLI ao check_specify; a integracao real mostra campo approved com estado stale e D1 nao medido; nenhum consumidor le o campo.
- deviated: O estado so e pedido com --matrix, para a varredura do run_all_checks nao abrir subprocessos; a secao 10 do gherkin-spec-format ganhou a linha do plugin (texto 6 do 000013).
- less-sure: Se o custo de um subprocesso por feature pesa em projetos com muitas features.
- gate: not-installed

### Step 5 -- congelar o M1 (2026-10-06)

- Terreno (Step 1, achado 2): a fiação já existia no `implement/SKILL.md` (Phase 2, passo 12: "M1 freeze") e no Procedimento, item 9, de `implement-test-first.md` (plan-000013). **Desvio**: `implement/SKILL.md` **não** ganhou linha (seria a segunda menção; `git diff --numstat` do SKILL.md = 0/0, não 1/0 como o Verify do plano supunha).
- `implement-test-first.md` (+24): seção "Congelar o M1 (emenda 000015)" com quando (v2, `Feature:`, `Specify: approved`, depois de `full`/`full: null`, `export`, `demo`), o comando exato com `--plan` (o texto sugerido do 000014 traz `--plan`; o item 9 do 000013 não; com `--plan`, um plano v1 passado por engano sai "não aplicável" sem arquivo) e a tabela do que fazer com cada resultado: exit 0 registra `- m1: ...` no progress; exit 2 "já foi congelado" avisa e segue; script ausente ou outro erro avisa e segue (o `/reflect` dirá `NM-SEM-M1`). Nunca reprova o `/implement`.
- `test_default_cycle_wiring.py` (novo, 6 testes): o orquestrador roteirizado lê o comando **da própria norma** e roda o `drift_report.py` real sobre uma cópia de `fixtures/drift_report/ok-m1`. Casos: o comando da norma é o freeze; plano v2 cria `M1.json` com `momento`, `at`, `feature` e o SHA-256 de cada entrada; a segunda chamada avisa e deixa o arquivo igual byte a byte; plano v1 não cria nada em `drift/`; sem `drift_report.py`, aviso e fim sem erro; `Specify: skipped` não congela. Ordem: a seção da norma foi escrita antes do teste (o teste a lê); prova do vermelho: com a norma do HEAD, 3 dos 6 falham por `IndexError` (seção ausente) e os 3 que não dependem do comando passam.
- Verify: `grep -n "drift_report.py --feature <slug> --plan <plano> --moment M1 --freeze"` acha a seção; `test_default_cycle_wiring.py` 6 passed; os testes do 000013 sem edição; `check_docs.py --plugins skill-body-length` 0 erros (implement 254/500, sem mudança); `uvx ruff` limpo; `run_all_checks.py` 19/14, mesmo conjunto, 17/2/9; pytest 1465 passed / 12 failed (mesmo conjunto).

### Step 5 -- reflection-on-action | 2026-10-06 19:37 UTC | Fiacao do /implement para congelar o M1
- happened: A norma ganhou a secao Congelar o M1 com o comando e a tabela de resultados; um teste de costura le o comando da norma e roda o drift_report real: cria, recusa a sobrescrita, ignora v1 e degrada sem o script.
- deviated: O implement/SKILL.md nao ganhou linha: o passo 12 ja cita o freeze (000013); o comando da norma passou a levar --plan.
- less-sure: Se um orquestrador real le esta secao no fim do plano ou para no item 9 do Procedimento.
- gate: not-installed

### Step 6 -- os quatro checks no `run_all_checks` (2026-10-06)

- Terreno (Step 1, achado 3): o modo sem argumentos e as entradas do registro já existiam (planos 000009-000012). Nenhum `check_*.py`, nem o registro, nem `run_all_checks.py` foram editados. Decisão 8 = A `[default; aceito 2026-10-06]`.
- `test_default_cycle_checks.py` (novo, 8 testes): projetos descartáveis em `tmp_path` com `.claude` ligado a este harness e dois planos v1 reais (`fixtures/plan_format/`). Uma rodada **completa** de `run_all_checks.py --root <projeto>` por forma de projeto (sem `features/` e só v1; `features/` de terceiros sem `intent.md`; feature aprovada e íntegra): os quatro em PASS nas três, e o conjunto inteiro de resultados (33 checks) **idêntico** entre as três formas. Casos de falha por script, sem argumentos e com cwd na raiz (o mesmo caminho do orquestrador): `.feature` sem `@REQ-` -> `check_features` exit 1 com GHK-002; plano v2 com cenário sem step -> `check_plan_scenarios` exit 1 com PFS-009; plano v1 com corpo quebrado -> exit 0, "nada a verificar", `--json` com `plans: []`; `features/` de terceiros intacta byte a byte; os quatro no registro com `stack: any`, `critical: false`. Tempo: ~6 s.
- Teste primeiro sem vermelho: o comportamento já existia (Step 1); o teste é a prova agregada pedida pelo plano, não a especificação de código novo.
- Palavra impressa: "nada a verificar" (não "pulado"); mantida.
- Docs: não há README de scripts com lista de checks (`.claude/skills/scripts/README*` ausente); nada a atualizar.
- Verify: 8 passed; `uvx ruff` limpo; `git diff --stat` não toca `run_all_checks.py`; `run_all_checks.py` do open-seja 19/14, mesmo conjunto, 17/2/9; pytest 1473 passed / 12 failed (mesmo conjunto).

### Step 6 -- reflection-on-action | 2026-10-06 19:40 UTC | Os checks novos no run_all_checks, condicionais a features/
- happened: Escrevi o teste agregado: tres formas de projeto com run_all_checks completo dao o mesmo conjunto de resultados e os quatro em PASS; feature sem tag e plano v2 com cenario sem step falham pelo nome.
- deviated: Nenhum script nem o registro mudou: o modo sem argumentos ja existia; o teste nao teve vermelho.
- less-sure: Se um projeto real com conftest e pyproject proprios muda algum dos outros 29 checks ao ganhar features/.
- gate: not-installed
