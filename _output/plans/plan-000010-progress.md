# Progress -- Plan 000010

Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

## Codebase Patterns
<!-- Subagents consolidate reusable patterns here -->

- Terreno herdado do plan-000007 (ler `_output/plans/plan-000007-progress.md`, secoes "Codebase Patterns", "Step 1" e "Step 7"): repositorio de execucao e este (sem prefixo `open-seja/`); `seja-as-intended.md` -> `product-design/product-design-as-intended.md` (§3); numeracao D-NNN do Doutourado nao vale aqui (D-004 = contrato Gherkin; D-005..D-008 = plan-000007; proximo livre D-009); "D-006 do Doutourado" citada nos planos = D-004 aqui.
- O contrato existe: `.claude/references/general/extended-cycle-contract.md` (CYC-001..026); esquema `features/<slug>/` em `.claude/references/template/feature-layout.md`; formato v2 em `.claude/references/template/plan-step.md`.
- Fixtures do harness ficam em `.claude/skills/scripts/tests/fixtures/<tema>/` (logo `<fixtures>/drift/` = `.claude/skills/scripts/tests/fixtures/drift/`).
- `python3` (nao `python`); pytest via `uvx --with pyyaml pytest ... --ignore=.claude/skills/scripts/tests/test_generate_spo.py --ignore=.claude/skills/scripts/tests/test_generate_spo_design_system.py`.
- Baseline (Q1): `run_all_checks.py` 16 PASS / 14 FAIL (o PASS extra e check_intent.py, plan-000009) com contadores 17 undefined (check_conventions), 2 error(s) (check_i18n_keys), 9 error(s) (check_skill_system); pytest 682 passed / 12 failed (apos plan-000009). Rodar `run_all_checks.py` com `timeout 200`, saida em arquivo, nunca dois ao mesmo tempo, nunca checks isolados, nunca `pkill -f`.
- Arquivos do harness: UTF-8, sem travessao tipografico nem aspas curvas; nada de nome de pessoa, parceiro, instituicao ou empresa.
- Portao nao instalado no open-seja: notas com `--gate not-installed`.
- Commits: `git -c user.name=arodrigues-puc-rio -c user.email=arodrigues-puc-rio@users.noreply.github.com commit ...`; nunca `--no-verify`.
- Decisoes pendentes do plano: o designer aceitou todas as recomendacoes em 2026-10-06; marcar como `[default; aceito 2026-10-06]`.
- `run_all_checks.py` deve rodar com `< /dev/null` (sem isso `check_skill_system` pode travar 120 s e dar ERROR; com isso leva ~3,5 s).

- Planos ja entregues neste roadmap: ver a coluna Status da Wave Summary em `_output/roadmaps/roadmap-000006-*.md` e os `## Implementation summary` dos planos DONE; os progress files deles listam lacunas que este plano deve absorver no Step 1.

## Iteration Log

## Step 1 -- terreno e pontos de integracao (2026-10-06)

Decisoes pendentes 1 a 7 aceitas nos defaults (1=C, 2=A, 3=A, 4=B, 5=A, 6=A, 7=B) `[default; aceito 2026-10-06]`.

| item | resultado |
|---|---|
| (a) contrato e medida | existem: `extended-cycle-contract.md` (CYC-001..026; proximo livre CYC-027), `feature-layout.md`, `drift-metric.md` (DRM-001..014; lacuna 5 = formato do relatorio do runner e do 000010), `grill-phase.md`, `template/intent.md`, `check_intent.py` |
| (b) `run_all_checks.py` | descobre `check_*.py` por glob (scripts/ e subpastas de skill) e roda `python <script>` com `cwd=raiz`, sem argumentos, timeout 120 s; PASS = exit 0. Nao ha "pulado": o check condicional e o proprio script (sem `features/<slug>/intent.md` imprime "nada a verificar" e sai 0, como `check_intent.py`). Registro em `check_plugin_registry.json` (so filtro por stack). Python 3.12.3 local; sem requisito minimo declarado |
| (c) testes e fixtures | `.claude/skills/scripts/tests/test_<modulo>.py`; fixtures em `.claude/skills/scripts/tests/fixtures/<tema>/` (a pasta nova e `fixtures/features/`); testes importam `from check_intent import ...` (scripts/ no sys.path) |
| (d) colisao de regex | `critique_plan_coverage.py` nao existe neste repo; `REQ-TYPE-NNN` aparece em `human_markers_registry.py` como `REQ-[A-Z0-9]+-\d{3}` em maiusculas, dentro de comentario HTML. A tag `@REQ-<slug>-NNN` (slug minusculo) e o prefixo reservado em GHK-016 nao colidem |
| (e) spike pytest-bdd | pytest-bdd **9.0.0** (pytest 9.1.1), via `uvx --with pytest-bdd`. Le `# language: pt` (Funcionalidade/Cenario/Dado/Quando/Entao). `--cucumberjson=<arquivo>` **existe** e emite Cucumber JSON. Tag `REQ-demo-001` com `--strict-markers` falha na coleta ate o `conftest` tratar `pytest_bdd_apply_tag`; com o hook retornando `True` coleta limpo. No JSON: `tags` ja vem por feature e por cenario (nome **sem** `@`), `uri` e relativo a rootdir, `elements[].id` e o nome da funcao de teste, `steps[].result.status` (passed/failed/...) e `error_message` e o traceback |

Fecha: decisao 1 (C viavel: pytest-bdd le `# language: pt`), decisao 3 (A: harness sem dependencia opcional; parser proprio), decisao 7 (B: rede e instalacao funcionam).

Desvio registrado (emenda do adendo): o runner contract e **Cucumber JSON** (CYC-012), nao JUnit XML. O plano fala em "propriedade `req` no relatorio JUnit/JSON"; como o Cucumber JSON ja traz `tags` por cenario, nao ha propriedade extra: a ligacao cenario -> REQ e a lista `tags`, e a chave de cenario `<slug>/<arquivo>::<nome>` e derivada de `uri` + `name`. O Step 8 prova isto.

Baseline confirmado: `run_all_checks.py` 16 PASS / 14 FAIL; `git status` limpo.

### Step 1 -- reflection-on-action | 2026-10-06 17:31 UTC | Terreno e pontos de integracao
- happened: Confirmei contrato, esquema e metrica no repositorio, o mecanismo de descoberta do run_all_checks e o spike do pytest-bdd 9.0.0 (le language pt, tem --cucumberjson).
- deviated: Runner contract e Cucumber JSON, nao JUnit; as tags ja vem no JSON, sem propriedade req.
- less-sure: Se o formato de falha do Cucumber JSON do pytest-bdd distingue assercao de erro (vai para o Step 8).
- gate: not-installed

### Step 2 -- reflection-on-action | 2026-10-06 17:32 UTC | Convencao normativa gherkin-spec-format.md
- happened: Escrevi a convencao com GHK-001..019 (as 16 do plano mais termos, Rule como jornada e @nao-faz), a tabela de mapeamento Cucumber JSON para os estados do DRM-003 e a chave de cenario.
- deviated: Tres regras acrescentadas pelas emendas do adendo (GHK-017..019); runner contract em Cucumber JSON em vez de JUnit.
- less-sure: A heuristica de GHK-017 (aspas e maiuscula) pode gerar ruido; fica como aviso.
- gate: not-installed

## Step 3 -- fixtures golden (2026-10-06)

36 casos em `.claude/skills/scripts/tests/fixtures/features/` (README com uma linha por caso): `ok-minimo`, `ok-completo`, tres negativos (`neg-*`), um caso de disparo para cada GHK-001..019 (varios com mais de um achado), tres de `--steps` alem do ok, e `sem-features`, `features-de-terceiros`, `pasta-sem-intent`. `esperado.json` por caso: `args`, `exit_code`, `findings` exatos `[regra, severidade, arquivo, linha]` e, nos validos, `matrix`.
- As linhas esperadas foram escolhidas a partir do texto do fixture (a linha que a regra deve apontar), nao copiadas da saida do validador (que ainda nao existe). Conferencia fina fica para o Step 4.
- Cascatas assumidas e escritas nos esperados: `ghk-016-sem-req` espera tambem GHK-004 (o REQ da tag nao existe porque a tabela nao tem REQ valido).
- Contagem do plano 000008: `ghk-002-sem-tag` tem 1 achado GHK-002; `ghk-004-orfa` tem 1 achado GHK-004.
- O gerador dos fixtures ficou no scratchpad (nao entra no repo); os arquivos sao estaticos.

### Step 3 -- reflection-on-action | 2026-10-06 17:35 UTC | Fixtures golden
- happened: Criei 36 casos com esperado.json (achados exatos, exit code e matriz), cobrindo GHK-001..019, negativos e retrocompatibilidade.
- deviated: Casos extras para as tres emendas (GHK-017..019) e para --steps.
- less-sure: As linhas esperadas dependem da minha leitura das regras; o Step 4 pode revelar divergencia de interpretacao.
- gate: not-installed

## Step 4 -- parser e regras de estrutura (2026-10-06)

`check_features.py` criado (stdlib so; importa `parse`/`table`/`_norm` de `check_intent.py`, nao reescreve o parser de intent.md). Entregue neste step: `parse_feature` (en/pt, tags com linha, Rule, Background, Outline/Examples, doc strings e tabelas, tipos efetivos de And/But), `load_intent`, `validate_structure` (GHK-001, 002, 003, 004, 005, 009, 010, 011, 014, 016, 018, 019), `build_matrix`, `discover`, registro em `check_plugin_registry.json` (scope `features`). Testes: `.claude/skills/scripts/tests/test_check_features.py` (53 passam; golden por caso restrito as regras de estrutura).
- Decisao de design: arquivo que nao parseia suprime GHK-005 da pasta (cobertura desconhecida, nao zero).
- GHK-018 e GHK-019 (emendas do adendo) entraram aqui por serem estruturais; `@nao-faz` e proibida em Feature/Rule/Examples e o info de cobertura so aparece se "Fora do escopo" tem itens.
- Achado do Step 3: arquivos `test_*.py` dentro de fixtures sao coletados pelo pytest do harness; os steps de exemplo dos fixtures de `--steps` foram renomeados para `steps/definitions.py`. Mesma ressalva vale para o `conftest`/`test_*.py` do Step 8 (ver la).
- ruff limpo nos dois .py novos. pyright indisponivel neste ambiente (`libatomic.so.1` ausente no node do pyright): registrado como nao medido; o open-seja nao tem pyproject nem config de pyright.
- Verificacao: `run_all_checks.py` 17 PASS / 14 FAIL (o PASS novo e `check_features.py`, que sem `features/` imprime "nada a verificar" e sai 0), contadores 17 undefined / 2 error(s) / 9 error(s); pytest do harness 744 passed / 12 failed (os mesmos 12 do baseline).

### Step 4 -- reflection-on-action | 2026-10-06 17:38 UTC | Parser e regras de estrutura
- happened: Implementei o parser Gherkin en/pt, load_intent reutilizando check_intent, as regras estruturais e a matriz; os 36 casos golden passaram na primeira rodada.
- deviated: Rule como jornada (GHK-018) e @nao-faz (GHK-019) entraram aqui; fixtures de steps renomeadas para nao serem coletadas pelo pytest.
- less-sure: O parser e minimo: construcoes raras do Gherkin (comentarios no meio de tabelas, Rule com Background proprio) nao foram exercitadas.
- gate: not-installed
