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

## Step 5 -- regras de step e `--steps` (2026-10-06)

`check_features.py` ganhou `normalize_step`, `light_key`, `validate_steps` (GHK-006, 007, 008, 012, 013, 017) e `validate_step_defs` (GHK-015, decisao pendente 4 = B: leitura com `ast`, nunca executa; literal e `parsers.parse` verificados; `parsers.re`, `cfparse` e decoradores dinamicos viram info "nao verificado"). `main` ja aceita `--steps`. Testes: 101 passam em `test_check_features.py` (golden de todas as regras com `args` e `--steps`, mais os testes unitarios do plano).
- Refinamento de GHK-008: a normalizacao agressiva troca valores (numeros e texto entre aspas) por `<v>`, mas so e quase-duplicata quando os **valores** tambem sao iguais; senao todo step parametrizado ("tem 1 conta" / "tem 2 conta") seria acusado. Texto do plano seguia a regra sem essa ressalva.
- GHK-017 pula o step que ja gerou GHK-013 (SQL em maiuscula virava "substantivo"). GHK-017 so emite a info "sem Modelo e termos" quando existe candidato a medir.
- Heuristicas GHK-012/013/017 sao aviso, nunca erro; documentadas em `gherkin-spec-format.md`.
- Verificacao: `run_all_checks.py` 17 PASS / 14 FAIL (contadores 17/2/9); pytest do harness 792 passed / 12 failed; ruff limpo.

### Step 5 -- reflection-on-action | 2026-10-06 17:40 UTC | Regras de step e --steps
- happened: Implementei duplicata, ambiguidade, quase-duplicata, tamanho, estilo, vocabulario e a leitura de definicoes por ast; os 36 casos golden e os testes unitarios passam.
- deviated: GHK-008 ignora steps que diferem em valor; GHK-017 pula steps ja acusados por GHK-013.
- less-sure: As heuristicas de aviso (012, 013, 017) podem errar nos dois sentidos com texto real.
- gate: not-installed

## Step 6 -- CLI, saida, `--json`, `--matrix`, exit codes (2026-10-06)

`main` completo: `check_features.py [raiz] [--feature] [--steps] [--json] [--matrix] [--strict] [--quiet]`; relatorio legivel agrupado por feature com `arquivo:linha`, regra, severidade em pt e `Dica:`; resumo `N erros, N avisos, N informacoes; N REQs, N cenarios, N REQ sem cenario`; JSON com `schema_version: 1` (`summary`, `findings`, `features`, `matrix` opcional); exit 0/1/2 como o plano (falha interna vira exit 2 com mensagem curta, nunca traceback; `--feature` sem pasta tambem e 2). Secao "Saida" e "Codigos de saida" escritas em `gherkin-spec-format.md` (secao 11).
- A convencao de exit code dos `check_*.py` existentes: `check_intent.py` sai 0 sempre (1 so com `--strict`); aqui erro falha por padrao porque o check roda no `run_all_checks.py` e "erro reprova" e o contrato do plano (Step 7). Documentado.
- Verificacao: 145 testes de `test_check_features.py` passam; pytest do harness 836 passed / 12 failed; `run_all_checks.py` 17 PASS / 14 FAIL (17/2/9); ruff limpo.

### Step 6 -- reflection-on-action | 2026-10-06 17:41 UTC | CLI e saida do validador
- happened: Escrevi o CLI com saida legivel, JSON versionado, matriz, --strict e --quiet, e documentei a saida e os codigos de saida na convencao.
- deviated: Erro falha por padrao (exit 1), diferente do check_intent.py que so falha com --strict.
- less-sure: O JSON e a matriz sao a entrada do plan-000014; o formato pode precisar de ajuste quando ele consumir.
- gate: not-installed

## Step 7 -- integracao com run_all_checks e retrocompatibilidade (2026-10-06)

`run_all_checks.py` **nao foi modificado**: ele descobre `check_*.py` por glob e so conhece PASS/FAIL/ERROR (sem estado "pulado"); a condicionalidade esta no proprio script (sem `features/<slug>/intent.md` imprime "nada a verificar" e sai 0), como `check_intent.py`. Isto cumpre o Verify do plano na substancia (o conjunto de falhas pre-existentes nao muda; a lista ganha uma linha `check_features.py PASS`), mas nao ha rotulos `features: pulado/ok/falhou`: desvio registrado. Erro GHK (exit 1) reprova o check; aviso nao.
- Testes (7 novos, 152 em `test_check_features.py`): check descoberto e registrado; `sem-features`, `features-de-terceiros` e `pasta-sem-intent` rodam como check (`run_script` do proprio `run_all_checks`) com PASS e exit 0; o repositorio atual (sem `features/`) passa dizendo "nada a verificar"; `ok-completo` PASS, `ghk-002-sem-tag` FAIL com o nome `check_features.py`; so aviso (`ghk-013-detalhe`) continua PASS.
- Retrocompatibilidade: `run_all_checks.py` real 17 PASS / 14 FAIL (os mesmos 14 FAIL do baseline; +1 PASS = este check), contadores 17 undefined / 2 error(s) / 9 error(s); nenhum SKILL.md, gate, hook ou settings alterado; `git diff` do step so mexe no teste.
- Nota: `run_all_checks.py --root <fixture>` nao serve para provar o check por raiz (nao imprime nada util fora de um repo com `.claude`); por isso os testes usam `run_script`.
- pytest do harness: 843 passed / 12 failed (os mesmos 12).

### Step 7 -- reflection-on-action | 2026-10-06 17:42 UTC | Integracao com run_all_checks
- happened: Provei por testes que o check e descoberto, nao afeta projetos sem features/ e reprova so com erro; nao foi preciso editar o run_all_checks.
- deviated: Nao existe estado pulado no run_all_checks; a condicional e interna ao script, e o arquivo run_all_checks.py ficou intacto.
- less-sure: Um projeto real que adotar features/ com intent aprovado vera o health check falhar por erro GHK; e o comportamento pretendido, mas muda o resultado dele.
- gate: not-installed

## Step 8 -- prova no runner (pytest-bdd) (2026-10-06)

Decisao pendente 7 = B executada. Versoes: **pytest-bdd 9.0.0**, pytest 9.1.1, Python 3.14 do `uvx` (rede e instalacao funcionaram; nenhuma dependencia entrou no harness; `uvx --with pytest-bdd`). pytest-bdd **tem `--cucumberjson`** e le `# language: pt`.
Exemplo em `.claude/references/template/feature-example/` (README, `features/task-list/{intent.md,manage-tasks.feature}`, `conftest.py.example`, `test_task_list.py.example`, `cucumber_states.py.example`). Os `.py` levam sufixo `.example` (desvio do plano, que pedia `conftest.py` e `test_login.py`): um `test_*.py` ou `conftest.py` real na pasta seria coletado por um `pytest` rodado na raiz do repo e falharia sem pytest-bdd; `test_feature_example.py` garante que a pasta nao tem `*.py`.
Saida do pytest (copiando a pasta e tirando o sufixo, `--strict-markers --cucumberjson --junitxml`): `1 failed, 3 passed, 1 skipped`. Falha: `assert False is True` / `AssertionError` do cenario REQ-task-list-002 (nao `ERROR` de coleta). Coleta limpa tambem com `-W error::pytest.PytestUnknownMarkWarning`. `check_features.py <pasta copiada> --steps <pasta>` sem achado GHK-015. `check_features.py` sobre o exemplo no repo: exit 0 (1 aviso GHK-014 do `@skip` e 1 info GHK-019, esperados).

Descobertas do runner (todas em `gherkin-spec-format.md` secoes 8 e 10; fixture real em `.claude/skills/scripts/tests/fixtures/runner/pytest-bdd-cucumber.json`):
1. Tags vem no Cucumber JSON por cenario, **sem `@`**; nao ha propriedade `req` a gravar (o plano falava de JUnit/propriedade).
2. `uri` e relativo a pasta `features/` (ou a raiz): a chave de cenario usa os **dois ultimos componentes** do `uri`.
3. `Scenario Outline`: um elemento por linha de `Examples`, mesmo `name` e mesma chave; agregar pelo pior estado.
4. `@skip` **nao aparece** no Cucumber JSON (so no JUnit e no resumo do pytest). Tambem **nao aparece** o cenario cujo primeiro step e indefinido, e o step indefinido de um cenario que falha no meio fica fora (so os steps anteriores, `passed`). `--junitxml` do mesmo pytest traz todos (`skipped`, `failure` com `StepDefinitionNotFoundError`).
5. `@xfail` e uma tag no relatorio: o step que falha vem `skipped`; xpass vem todo `passed`. `xfail` nao e nativo: sai da tag.
6. Falha de asserção: `error_message` termina em `AssertionError`; excecao de fixture ou de step (`RuntimeError`) tambem vem `failed`, sem `AssertionError` -> `error`. Nao ha `ambiguous` nem `pending` no pytest-bdd.
7. `pytest_bdd_apply_tag` devolvendo `True` para `REQ-*` e `nao-faz` basta para `--strict-markers`; `skip` e `xfail` ficam nativos.

Tabela de mapeamento Cucumber JSON -> estados do DRM-003 escrita (secao 8) e executavel (`cucumber_states.py.example`, testada em `test_feature_example.py`, 18 testes, inclusive sobre o relatorio real). Nova regra **CYC-027** (estados e chave do runner contract) em `extended-cycle-contract.md`, mais uma linha "Implementacao" em CYC-026. Verificacao: pytest do harness 861 passed / 12 failed; `run_all_checks.py` 17 PASS / 14 FAIL (17/2/9); ruff limpo.

### Step 8 -- reflection-on-action | 2026-10-06 17:46 UTC | Prova no runner pytest-bdd
- happened: Provei o exemplo no pytest-bdd 9.0.0 (3 passed, 1 failed por AssertionError, 1 skipped), com Cucumber JSON real e a tabela de mapeamento de estados executavel e testada; criei CYC-027.
- deviated: Os .py do exemplo levam sufixo .example para o pytest do harness nao os coletar; o JSON nao precisa de propriedade req; o JSON do pytest-bdd omite o cenario @skip e o primeiro step indefinido.
- less-sure: Se o complemento com --junitxml sera aceito pelo plan-000013 ou se ele prefere outro runner; o relatorio Cucumber do pytest-bdd e incompleto.
- gate: not-installed

## Step 9 -- fechamento (2026-10-06)

Reexecutados: `test_check_features.py` (155) e `test_feature_example.py` (17) verdes; os exemplos pt e en de `gherkin-spec-format.md` passam no validador (teste `test_spec_examples_pass_the_validator`, extrai os blocos `gherkin` do proprio documento; os exemplos foram trocados para `"tarefa de compras"` / `"shopping task"` para ficarem cobertos por "Modelo e termos"); `check_features.py` sobre `feature-example` sai 0; pytest do harness 863 passed / 12 failed (os mesmos 12); `run_all_checks.py` 17 PASS / 14 FAIL (os mesmos 14; contadores 17 undefined / 2 error(s) / 9 error(s)); ruff limpo. Vocabulario conferido com `extended-cycle-contract.md`, `feature-layout.md` e `drift-metric.md`: `REQ-<slug>-NNN`, `status: grilling|approved`, estados do DRM-003, chave de cenario (CYC-012). C1: grep de nomes de parceiro, instituicao e pessoa sobre os arquivos novos e alterados do `.claude/`: zero (um teste que listava esses nomes foi removido por isso). Nenhum SKILL.md, gate, hook, `settings` ou esquema de `feature-layout.md` alterado.
Ponteiros: uma linha em `feature-layout.md` (secao `*.feature`) e uma linha "Implementacao" em CYC-019 do contrato. Alem do ponteiro, o plano deste executor acrescentou CYC-027 e uma linha de implementacao em CYC-026 (instrucao do designer: regras CYC novas a partir de CYC-027) e fechou a lacuna 5 da tabela de `drift-metric.md` (formato do relatorio do runner) com uma frase.

### Tabela GHK -> leituras do plan-000008

| Regra | Alimenta |
|---|---|
| GHK-002 | D1 / leitura "cenario sem tag" (`ghk-002-sem-tag`: 1 achado) |
| GHK-003, GHK-004 | D1 / leitura "tag sem REQ" (tag orfa, `ghk-004-orfa`: 1 achado) |
| GHK-005 | D1: REQ aprovado sem cenario = descoberto (erro); em `grilling` = nao medido (info) |
| `scenarios_approved` da matriz | D1 `NM-CENARIOS-STALE` (nao aprovado/ausente) |
| GHK-010 e a chave `<slug>/<arquivo>::<nome>` | D2 (liga cenario ao teste) |
| GHK-014 e `disabled` da matriz | D2: `skip`/`xfail` = descoberto, avisado antes do runner |
| `rows` da matriz e o pior estado das linhas | D2: Outline e um cenario (decisao 6 = A) |
| GHK-006..008, 012, 013, 017 | ruido do Gherkin (risco do roadmap); nao entram no D |
| GHK-018 e `journey` da matriz | leitura da jornada ordenada (JM-TB-NNN), fora do vetor D |
| GHK-019 e `nao_faz` da matriz | leitura "nao faz" (opt-in), fora do vetor D |
| GHK-015 | duplicata de definicao de step (item 7) |

### Decisoes pendentes e o default em uso

1 = C (en e pt; `# language: pt` exigido), 2 = A (tag nao herdada), 3 = A (parser proprio stdlib), 4 = B (`--steps` por `ast`; ambiguidade por casamento fica para o 000013), 5 = A (`scenarios: approved` lido, nao escrito), 6 = A (Outline = um cenario), 7 = B (prova no runner feita), todas `[default; aceito 2026-10-06]`. Emendas do adendo: aviso de substantivo fora de "Modelo e termos" (GHK-017), `Rule:` como jornada com `JM-TB-NNN` (GHK-018), `@nao-faz` opt-in (GHK-019).

### Desvios do plano

- Runner contract em **Cucumber JSON**, nao JUnit XML (o JUnit entra so como complemento, achado 4 do Step 8). Sem propriedade `req`.
- `.py` do exemplo com sufixo `.example` (nao coletados pelo pytest do harness); exemplo em pt com `task-list`, nao `login`.
- `run_all_checks.py` nao foi modificado (descoberta por glob; condicional interna; sem estado "pulado").
- Regras GHK-017..019 (3 alem das 16) e CYC-027.
- GHK-008 ignora steps que diferem em valor; GHK-017 pula step ja acusado por GHK-013.
- pyright nao rodou (node do pyright sem `libatomic.so.1`); o open-seja nao tem config de pyright. Nao medido.
- Fixtures em `.claude/skills/scripts/tests/fixtures/features/` (nao `tests/fixtures/features/`).

### Lacunas para os planos 000011 a 000016

| Plano | Lacuna |
|---|---|
| 000011 (specify) | escrever `scenarios: approved` em `intent.md` na aprovacao do `.feature`; usar `check_features.py <raiz> --feature <slug>` como portao de saida da specify (exit 0; avisos sao do power dev); ponto de aprovacao do citizen mostra a retradução, nao o `.feature`; `@nao-faz` e `Rule` com `JM-TB-NNN` sao opt-in a oferecer; `--specify` segue reservada; cenario `@REQ` de REQ `retirado` nao e erro |
| 000012 (plano v2) | conferir as tags de `Scenarios:` contra `check_features.py --json --matrix` (a tag existe, o REQ esta ativo); chave de cenario `<slug>/<arquivo>::<nome>` como unica referencia por nome |
| 000013 (teste-primeiro) | produzir o Cucumber JSON (`--cucumberjson`) e, para nao perder `@skip` e step indefinido no primeiro passo, tambem `--junitxml` (achado 4 do Step 8); classificar `failed` so com `AssertionError` (CYC-022, CYC-027); `conftest` modelo (`pytest_bdd_apply_tag`); ambiguidade de definicoes por casamento (decisao 4 = B so cobre duplicata exata); `check_features.py --steps` como parte do passo; `baseline_moved`, rodada `full` (lacunas do 000008) |
| 000014 (relatorio) | consumir `check_features.py --json --matrix` (`schema_version: 1`) e `cucumber_states.py.example` como referencia do mapeamento; agregar linhas de Outline pelo pior estado; `scenarios_approved` -> `NM-CENARIOS-STALE`; `rev` > 1 do REQ x cenarios (lacuna 2 do 000009); `disabled` -> D2 descoberto |
| 000015 (integracao) | quickguide pt-BR e `/help` sobre `check_features.py` e a convencao; `features/` entra nas leituras de `/critique` e `/explain drift`; avisar que `check_features.py` no `run_all_checks` dos projetos que adotarem `features/` reprova com erro GHK (aprovado = conferido) |
| 000016 (piloto) | contar achados por regra GHK nas features reais (calibrar GHK-012, 013, 017, que sao heuristicas); testar o aviso de GHK-017 com texto real (aspas e maiuscula); registrar relatorio real do runner do piloto |

### Texto sugerido ao designer (prosa Human; NAO escrito em `product-design/`)

- `feature-layout.md` (via `/implement --manual`), secao `intent.md`, frontmatter: campo opcional `scenarios: approved` (escrito quando o contrato `.feature` for aprovado; ausente = D1 `NM-CENARIOS-STALE`). Secao `*.feature`: "O `Scenario Outline` e **um** cenario; coberto so se todas as linhas de `Examples` rodaram e nenhuma foi `skip` ou `xfail`."
- `drift-metric.md` DRM-003: "A unidade do D2 e o `Scenario` com tag; um `Scenario Outline` e uma unidade e vale o pior estado das suas linhas (`gherkin-spec-format.md` secao 8)."
- Decisao D-010 (proposta, via `apply_marker.py --marker DECISION_APPEND`, com confirmacao): "**D-010: o `.feature` e conferido por um validador deterministico antes da aprovacao, e o relatorio do runner e Cucumber JSON.** Context: o Gherkin vira ruido sem checagem mecanica, e o D1 e o D2 precisam de uma fonte legivel por maquina. Decision: `check_features.py` aplica GHK-001..019 (rastreabilidade REQ-cenario, steps sem duplicata ou ambiguidade, vocabulario do citizen); o runner contract e Cucumber JSON com chave `<slug>/<arquivo>::<nome>`; `xfail`, `error` e `undefined` sao mapeados por regra (CYC-027). Consequences: o D1 e o D2 leem a matriz sem reinterpretar o `.feature`; projetos com `features/` passam a reprovar no `run_all_checks` por erro GHK. Rejected: depender de parser externo (dependencia no harness); validar semantica com LLM; JUnit como contrato (nao traz tags nem steps)."
- §14, linha `[intended] Grill e specify no /plan`: a metade grill ja esta entregue; com o validador a metade specify tem o portao de saida, mas a aprovacao (000011) ainda falta; marcador `STATUS` so quando o specify existir.

## Implementation summary

Entregue: convencao `gherkin-spec-format.md` (GHK-001..019, saida, mapeamento Cucumber JSON -> DRM-003, rodando no pytest-bdd), validador `check_features.py` (parser en/pt, regras de estrutura, rastreabilidade e steps, `--steps` por `ast`, `--json`, `--matrix`, exit 0/1/2, registrado no plugin registry, sem alterar `run_all_checks.py`), 36 fixtures golden + `esperado.json`, exemplo executavel em `template/feature-example/`, CYC-027. Medidas: 155 + 17 testes novos passam; baseline do harness mantido (14 FAIL, 12 testes falhando, contadores 17/2/9). Nao medido: pyright.

### Step 9 -- reflection-on-action | 2026-10-06 17:48 UTC | Fechamento
- happened: Reexecutei suites, exemplos da convencao (pt e en, via teste), run_all_checks e C1; acrescentei ponteiros e a tabela GHK para 000008, as lacunas para 000011-000016 e o texto sugerido ao designer.
- deviated: Alem do ponteiro, fechei a lacuna 5 do drift-metric com uma frase e criei CYC-027 (instrucao do designer); removi um teste que listava nomes de parceiro (C1).
- less-sure: Se o designer quer D-010 como proposto; e se o complemento JUnit do runner e aceitavel para o plan-000013.
- gate: not-installed
