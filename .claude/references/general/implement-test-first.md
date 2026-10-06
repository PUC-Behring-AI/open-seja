---
designer_description: "When you approve the scenarios and ask me to build, I'm the rule book /implement follows per step: I first write one test per scenario and a tool shows it fails because the behavior is missing, then a fresh agent writes the code, and with --pipeline two more agents simplify the code and look for tests that miss errors. Every move is decided by a tool's exit code, I stop and ask you after three tries, and I never move the quality baseline."
---

# GENERAL - IMPLEMENT TEST-FIRST

> Norma do teste-primeiro por cenário dentro do `/implement` (roadmap-000006, item 7; plan-000013). Detalha CYC-017 e CYC-020 a CYC-025 de `.claude/references/general/extended-cycle-contract.md` e implementa a interface reservada `--pipeline` (CYC-025). Consome, sem mudar: o portão (`.claude/references/template/quality-gate/python/gate.py`), os hooks `Stop` e `PreToolUse` (`.claude/hooks/`), os denies de `--no-verify` e `--accept-baseline` e o `settings` (CYC-024, S2).
>
> Depende de: plano v2 com `Scenarios:` (`plan-from-scenarios.md`, PFS-001..015; verificador `check_plan_scenarios.py`); cenários aprovados e `stale` (`specify-phase.md`, SPC-013; `check_specify.py --status`); chave de cenário e estados do runner (`gherkin-spec-format.md` seção 8; CYC-027); medida (`drift-metric.md`, DRM-003 a DRM-006, DRM-011).
>
> Ferramentas desta norma: `.claude/skills/scripts/build_checks.py` (verificadores, registro, exportação), `.claude/skills/scripts/build_brief.py` (briefing por papel), o plugin de relatório `.claude/references/template/bdd/python/scenario_report.py.example` e os agentes `.claude/agents/scenario-tester.md`, `cleaner.md`, `hardener.md`. O Coder é o subagente de step que o `/implement` já usa.
>
> Idioma: pt-BR (norma), identificadores en-US. Marcação: `[default; aceito 2026-10-06]` indica uma decisão pendente do plan-000013 que o designer aceitou no default. Cada regra tem identificador estável `ITF-NNN`, campo **Quem decide** e campo **Critério de aceitação** (o plano chamava as regras de `TFB-NNN`; a numeração é a mesma).

## Constantes

```
PIPELINE_MAX_TRIES        = 3       # tentativas por fase (RED, GREEN, CLEAN, HARD)
PIPELINE_MAX_INVOCATIONS  = 10      # invocações de papel por step
CRAP_TARGET_TOUCHED       = 8       # alvo do Cleaner em função tocada (o gate continua barrando em 10)
CRAP_TARGET_FLOOR         = 6       # alvo abaixo disto é recusado
PIPELINE_BRIEF_MAX        = 24000   # caracteres por briefing
BUILD_SCHEMA_VERSION      = 1       # gate.json.build e o relatório do plugin
```

## Fluxo por step

```
step v2 com Scenarios (dono)
  PRÉ   check_plan_scenarios = 0; check_specify --status = approved; suíte-base verde
  RED   Tester (scenario-tester): step definitions + teste + esqueleto neutro
        build_checks red-check (R1..R8); build_checks freeze --write          [<= 3 tentativas]
  GREEN Coder: o mínimo; build_checks scope + freeze --check;
        cenários donos = passed; GATE_FAST_CMD --files PASS                    [<= 3]
  --pipeline:
  CLEAN Cleaner só se build_checks crap acha função tocada acima do alvo        [<= 3]
  HARD  Hardener só se GATE_FULL_CMD --files deixa sobrevivente                 [<= 3]
  REC   build_checks record (gate.json: fast, ts, build.steps[N], build.scenarios)
fim do plano: GATE_FULL_CMD; build_checks uncovered (feature); record --full; export; demo
```

Status do step: `PASS`, `PASS_WITH_BASELINE` (o humano moveu o baseline durante o step; o D3a o lê como `descoberto`), `ESCALATED` (teto ou violação persistente; o humano decide). Step sem cenário segue o caminho de antes (ITF-003).

---

## Regras

### ITF-001 -- Aplicabilidade

Esta norma vale só para plano `plan_format_version: 2` com `Specify: approved (rev N)`. Plano v1 ou sem versão, e plano v2 com `Specify: skipped`, seguem o `/implement` como antes (CYC-018, CYC-020, D-008). Versão desconhecida: o `/implement` para (regra existente do Phase 0). `--pipeline` em plano v1 é recusado com uma frase: "`--pipeline` é do plano v2; este plano roda como antes." `[default; aceito 2026-10-06]` (decisão pendente 7 = B). O roteamento é calculado por ferramenta: `build_checks.py route <plano> [--pipeline]`.

- **Quem decide**: o cabeçalho do plano; `build_checks.py route` aplica.
- **Critério de aceitação**: `route` sobre os planos v1 de `fixtures/plan_format/` devolve só modos `legacy`/`tdd` e nenhuma fase desta norma; `route --pipeline` sobre plano v1 sai 1 com a frase de recusa e nenhuma ação.

### ITF-002 -- Pré-condições

Checadas por comando no início do run e antes de cada step dono: `check_plan_scenarios.py <plano>` sai 0; `check_specify.py <raiz> --feature <slug> --status --json` devolve `approved`; a suíte-base (comando de teste do projeto) está verde antes do RED. `stale`, `draft` ou `missing` param o run com a frase "os cenários estão desatualizados: refaça a specify" (PFS-011, SPC-013). `GATE_FAST_CMD` vazio: o step dono roda RED e GREEN sem portão, grava `fast: null`, a nota leva `--gate not-installed` e o D3a fica `não medido` (`NM-SEM-GATE`, CYC-012).

- **Quem decide**: as ferramentas (exit e JSON); o agente não interpreta.
- **Critério de aceitação**: com `--status` = `stale` o run para antes do primeiro step e nada é escrito; com suíte-base vermelha o step não começa e a falha é relatada.

### ITF-003 -- Classes de step

*Dono*: `Tests:` não-N/A e uma ou mais chaves em `Scenarios:` (PFS-008). *Sem cenário*: `Scenarios: N/A (motivo)`, ou plano com `Specify: skipped`. O step sem cenário segue o contrato atual do subagente de step (TDD por `Tests:` quando não-N/A, ordem legada quando N/A, portão `--fast` por step) e é registrado com `mode: no-scenario` e o motivo.

- **Quem decide**: o plano (campo `Scenarios:`); `route` classifica.
- **Critério de aceitação**: `route` devolve `test-first` só para step com chaves; `no-scenario` com o motivo para `N/A (motivo)`.

### ITF-004 -- Esqueleto neutro

No RED o Tester pode criar, nos arquivos de código do step (`Files:`, `Interface:`), módulos, classes e funções de **esqueleto**: assinatura e corpo só com `pass`, `...`, docstring, `return <literal>` (constante, `None`, lista ou dicionário vazio) ou `raise NotImplementedError`. Verificado por `ast` (`build_checks.py skeleton`). Sem lógica: nenhum `if`, laço, chamada, atribuição ou expressão composta no corpo.

- **Quem decide**: `build_checks.py skeleton`.
- **Critério de aceitação**: corpo `pass` ou `return None` passa; corpo com `if` ou chamada dispara ITF-004 com arquivo e linha.

### ITF-005 -- Vermelho pelo motivo certo

Por cenário dono, lido do relatório do plugin (ITF-016) ou, sem ele, do Cucumber JSON mais o JUnit do mesmo run (CYC-027):

- **R1** o teste foi coletado e o resultado é `failed`; `error`, `undefined`, `passed`, `skipped`, `xfailed`, `xpassed` e `missing` não contam.
- **R2** a exceção é `AssertionError` (CYC-022: `failed` só com asserção; o resto é `error`).
- **R3** o tipo efetivo do step que falhou é `then` (falha em `given`/`when` = montagem quebrada).
- **R4** o corpo da função do step que falhou não tem asserção constante (`assert False`, `assert 0`, `assert not True`, `raise AssertionError(...)` fora de condição, `pytest.fail(...)` fora de condição). Sem a localização da função (só Cucumber JSON), R4 fica `não verificado` (info).
- **R5** os arquivos de esqueleto cumprem ITF-004.
- **R6** o resto da suíte (cenários não donos e testes comuns) ficou como na linha de base: o que passava continua `passed`.
- **R7** quando o step cria ou muda código, a cobertura da rodada vermelha executou ao menos uma linha de corpo de função em arquivo de código de `Files:`.
- **R8** `Scenario Outline`: vermelho se **alguma** linha cumpre R1 a R4 e **nenhuma** dá `error`; linhas verdes no vermelho ficam em `rows_green_in_red` (informação de teste fraco).

Cenário dono já verde antes do código: achado R1 `already_green` e **escalada** (ITF-014) `[default; aceito 2026-10-06]` (decisão pendente 6 = A). Cada achado traz a regra e uma dica em frase curta. Limite declarado: a ferramenta não sabe se a asserção **diz** o que o cenário diz; isso é a auditoria humana por amostra do plan-000008.

- **Quem decide**: `build_checks.py red-check` (exit 0 vermelho certo; 1 achado; 2 uso ou dado ausente).
- **Critério de aceitação**: as fixtures `red-*` de `fixtures/build/` devolvem a regra esperada (tabela no progress do plan-000013); `red-ok` e `red-outline-partial` saem 0.

### ITF-006 -- Registro do vermelho

`build.scenarios[<chave>].red = {ts, outcome, reason_ok, exception, failing_step_type, rows_total, rows_failed, rows_green_in_red, skeleton_files, report}`. O estado vermelho **não** é commitado: o `PreToolUse` em `git commit` roda o portão e recusaria a árvore vermelha. A prova é o registro, os hashes (ITF-007) e o relatório gravado em `QUALITY_DIR`.

- **Quem decide**: `red-check` produz o objeto; `record` grava.
- **Critério de aceitação**: depois de um RED aprovado, `gate.json` tem `build.scenarios[<chave>].red.reason_ok = true` para cada cenário dono, e `report` aponta para um arquivo existente.

### ITF-007 -- Congelamento

Ao fim do RED, `build_checks.py freeze --write` grava SHA-256 dos `*.feature` da feature e dos arquivos de teste e de step definitions dos cenários donos em `QUALITY_DIR/plan-<id>-step-<N>-freeze.json`. Coder, Cleaner e Hardener não os alteram. `freeze --check` com hash diferente sai 1: o step volta ao RED (consome tentativa) ou escala.

- **Quem decide**: `build_checks.py freeze`.
- **Critério de aceitação**: alterar um byte de um arquivo congelado faz `freeze --check` sair 1 com o arquivo; arquivo intocado sai 0.

### ITF-008 -- Escopo por papel

Conferido por diff (`build_checks.py scope --role <papel> --base <rev>`): **Tester** só testes, step definitions, `conftest` e esqueleto (ITF-004); **Coder** código-fonte e testes **não congelados**, nunca `features/**`; **Cleaner** só código-fonte, nenhum teste; **Hardener** só testes novos ou não congelados, mais linhas de comentário `# pragma: no mutate  # equivalent: <motivo>` no código. Nenhum papel toca `gate.py`, `.claude/hooks/**`, `.claude/settings*`, `quality-baseline.json` nem `product-design/conventions.md` (linhas `GATE_*`).

- **Quem decide**: `build_checks.py scope`.
- **Critério de aceitação**: Coder com `.feature` no diff, Cleaner com `test_*.py`, Hardener com linha de código que não é pragma, e qualquer papel com `quality-baseline.json` ou `gate.py` saem 1 com ITF-008 e o arquivo.

### ITF-009 -- Verde

Cada cenário dono com resultado **exatamente** `passed` (`skipped`, `xfailed`, `xpassed`, `error`, `undefined` e `missing` não são verde: DRM-003, decisão fechada 4 do plano); `GATE_FAST_CMD --files <tocados> --json` com `status` PASS; `freeze --check` e `scope --role coder` limpos. Tentativas e `PARTIAL` como o Auto Mode do `/implement` já define (3 rodadas do portão); esta norma não as redefine.

- **Quem decide**: o relatório do plugin (`build_checks.py green-check`) e o portão.
- **Critério de aceitação**: cenário `skipped` com o resto verde faz `green-check` sair 1; todos `passed` sai 0.

### ITF-010 -- Cleaner

Só com `--pipeline`. Dispara se `build_checks.py crap --radon <json> --coverage <json> --files <tocados> --target 8` acha função **tocada** com CRAP acima do alvo (`CRAP_TARGET_TOUCHED`, default 8, piso 6) `[default; aceito 2026-10-06]` (decisão pendente 5 = B). O gate não aceita alvo por linha de comando (o limiar dele é do humano, em `[tool.seja-gate]`); por isso o cálculo do alvo do Cleaner é do `build_checks.py`, com a mesma fórmula do gate (`CRAP = cc^2 * (1 - cov)^3 + cc`). O Cleaner refatora sem mudar comportamento: cenários e suíte verdes, testes intocados (`scope --role cleaner`, `freeze --check`), `Interface:` preservada, portão `--fast` PASS. Alvo abaixo de 6 é recusado (exit 2): o agente fragmentaria o código em funções de uma linha. Sem função acima do alvo, o passe é **pulado** e registrado (`clean: {skipped: true}`).

- **Quem decide**: `build_checks.py crap` (dispara) e o portão (aceita).
- **Critério de aceitação**: função com CRAP 26 e alvo 8 aparece no achado; alvo 5 sai 2; nenhuma função acima dá `[]` e o passe pulado.

### ITF-011 -- Hardener

Só com `--pipeline`. Dispara se `GATE_FULL_CMD --files <tocados> --json` deixa achado de categoria 6 (sobrevivente em função dos arquivos tocados). Escreve testes que matem o mutante ou anota o equivalente com `# pragma: no mutate  # equivalent: <motivo>`. Saída: zero sobreviventes **inexplicados** nas funções tocadas; pragma sem motivo falha o portão (etapa de marcadores). Todo pragma novo entra no resumo de fim de step para revisão humana. Não se gateia por percentual. Para cada sobrevivente o Hardener também escreve uma **pergunta** ao citizen (ITF-024).

- **Quem decide**: o portão (`--full`).
- **Critério de aceitação**: sem achado de categoria 6 o passe é pulado e registrado; com achado, o step só passa quando o `--full` sai sem categoria 6.

### ITF-012 -- Contexto por papel

Montado por `build_brief.py` (ITF-013 para o teto). **Tester**: texto do step, Gherkin dos cenários donos, `Interface:`, índice das step definitions existentes (para reuso; GHK-015 acusa duplicata), regras de esqueleto e de asserção. **Coder**: texto do step, Gherkin dono, saída do `red-check` e lista de arquivos congelados, regra de escopo. **Cleaner**: só os achados de CRAP (`CRAP(arquivo::função)=26.4 (CC=26, cov=0.92) > 8: dividir`), o corpo das funções acima do alvo e a regra de escopo. **Hardener**: só a lista de sobreviventes (nome e diff do mutante), o corpo das funções, a lista de testes existentes e a regra do pragma. Nenhum papel vê o plano inteiro, o roadmap, a conversa nem as regras de outro papel.

- **Quem decide**: `build_brief.py`.
- **Critério de aceitação**: o briefing do Cleaner não contém o texto de cenário nem de outro step; o do Tester não contém corpo de função de código novo; todo briefing tem manifesto (o que entrou, tamanho em caracteres).

### ITF-013 -- Loop e teto

3 tentativas por fase (RED, GREEN, CLEAN, HARD) e no máximo 10 invocações de papel por step `[default; aceito 2026-10-06]` (decisão pendente 3 = A). Cada transição depende de código de saída de ferramenta. Um subagente **novo** por invocação ("um trabalho, depois destruído"). O briefing tem teto de 24 000 caracteres: acima dele `build_brief.py` corta o contexto opcional, nunca a regra de escopo, e marca `truncated: true`.

- **Quem decide**: o `/implement` conta; as ferramentas decidem cada transição.
- **Critério de aceitação**: a quarta tentativa de uma fase nunca é lançada sem escolha humana; o progress file mostra fase, tentativa e o último JSON a cada transição.

### ITF-014 -- Escalada

Teto atingido, violação de congelamento ou de escopo persistente, vermelho sem motivo certo depois do teto, cenário já verde antes do código (ITF-005), cenário com dois donos, ou `--status` diferente de `approved` no meio do run: status `ESCALATED`, gravação no progress file (fase, tentativa, último JSON), parada do run e `AskUserQuestion` com:

- **Ajustar o cenário e refazer a specify** -- Recommended when o teste não passa por causa do cenário (o cenário pede o impossível ou o ambíguo). NOT recommended when o erro é de código.
- **Eu assumo este step** (`/implement --manual`) -- Recommended when você quer escrever o código. NOT recommended when você não lê código.
- **Aceitar como PARTIAL e seguir** -- Recommended when o step não bloqueia os seguintes. NOT recommended when outro step tem `Depends on` neste.
- **Subir o teto uma vez** -- Recommended when o último JSON mostra progresso entre as tentativas. NOT recommended when as tentativas repetem o mesmo achado.

Mensagem de escalada em primeira pessoa, frases curtas, com a regra e a dica da ferramenta. Modelo: "Eu parei no step <N>. Tentei <k> vezes e o teste ainda falha. A ferramenta diz: <dica>. Eu não mudo o cenário nem o limite do portão. Escolha como seguir." O agente nunca move o baseline, nunca afrouxa limiar, nunca edita `.feature` e nunca oferece mover o baseline (só o humano, fora do `/implement`).

- **Quem decide**: o humano escolhe; as ferramentas disparam.
- **Critério de aceitação**: no ensaio, o caso de teto atingido termina em `ESCALATED` com o progress gravado, e a mensagem não tem número técnico.

### ITF-015 -- Registros (`gate.json.build`)

`features/<slug>/gate.json` mantém `schema_version`, `fast`, `full` e `ts` do contrato (CYC-024, `feature-layout.md`) e ganha a chave aditiva `build` `[default; aceito 2026-10-06]` (decisão pendente 2 = A):

```json
{
  "schema_version": 1,
  "fast": {"exit_code": 0, "category": "PASS", "ref": "_output/quality/plan-000123-step-2-green-try-1.json"},
  "full": {"exit_code": 0, "category": "PASS", "ref": "_output/quality/plan-000123-full.json"},
  "ts": "2026-10-06T18:00:00Z",
  "baseline_moved": false,
  "build": {
    "schema_version": 1,
    "plan": "plan-000123",
    "scenarios": {"<chave>": {"step": 2, "red": {"...": "ITF-006"}, "final": {"test_result": "passed"}}},
    "steps": {"2": {"mode": "test-first", "status": "PASS", "pipeline": true,
                    "phases": {"red": {"ok": true, "tries": 1}, "green": {"ok": true, "tries": 2},
                               "clean": {"skipped": true}, "hard": {"ok": true, "tries": 1, "survivors": 1}},
                    "baseline_moved": false, "touched_uncovered": {"n_touched": 12, "n_uncovered": 1, "provisional": true}}},
    "feature": {"touched_total": 30, "touched_uncovered": 2, "base": "<sha>", "baseline_moved": false}
  }
}
```

`category` é o nome da categoria do exit do portão (`PASS`, `CONFIG`, `STATIC`, `TESTS`, `CRAP`, `ARCH`, `MUTATION`, `MARKERS`); com baseline movido e exit 0 a categoria é `PASS_WITH_BASELINE`. `record` escreve atômico (temporário + rename), preserva chaves desconhecidas e é idempotente; o tempo vem de `--at`.

- **Quem decide**: `build_checks.py record`.
- **Critério de aceitação**: `record` sobre um `gate.json` com chave desconhecida a mantém; repetir o mesmo payload dá bytes iguais.

### ITF-016 -- Relatório do runner (plugin `scenario_report`)

Plugin pytest + pytest-bdd, copiado para `tests/scenario_report.py` por `build_checks.py install-plugin <projeto>` (idempotente; recusa sobrescrever cópia editada à mão). Opções: `--scenario-report <json>`, `--scenario-key <chave>` (repetível; seleciona só esses cenários), `--scenario-exclude-key <chave>`. Marca todo item de cenário com o marker `scenario` (rodada de cobertura só de cenários: `-m scenario`). Por cenário: `scenario_key` (mesma função de `check_features.py`), `feature_file`, `req` (lista das tags `@REQ-`), `outcome` (`passed|failed|error|skipped|xfailed|xpassed`), `exception` (classe), `failing_step_type` (`step.type` efetivo), `failing_step` (texto), `step_func` (`{file, line, name}`), `reason` (frase curta), `duration`, `rows` (Outline: uma linha por exemplo; `outcome` agregado pelo pior). Erro de coleta aparece como `error`; step indefinido como `error` com `exception: StepDefinitionNotFoundError` e `undefined: true`. Testes comuns ficam em `tests{nodeid: outcome}`. Cabeçalho `schema_version: 1`, `generated_at` (UTC), `pytest_bdd_version`. Propriedades JUnit: `scenario_key` e uma `req` por tag. O `/implement` roda o runner com `--scenario-report`, `--cucumberjson` e `--junitxml` juntos: o contrato do ciclo continua sendo o Cucumber JSON (CYC-012, CYC-027), e o JUnit cobre o que o Cucumber JSON do pytest-bdd omite (`@skip`, primeiro step indefinido).

- **Quem decide**: o plugin escreve; `red-check` e `green-check` leem.
- **Critério de aceitação**: no exemplo do plan-000010 o relatório traz 2 cenários `passed` (o Outline agregado), 1 `failed` por `AssertionError` com `failing_step_type: then` e 1 `skipped`; a chave de cada cenário é igual à de `check_features.py --matrix`.

### ITF-017 -- Baseline

`baseline_moved` é verdadeiro se `quality-baseline.json` mudou entre o início do step e o fim (`build_checks.py baseline --base <rev>`: hash do arquivo na revisão base contra o arquivo atual). O agente não move o baseline (deny e hook do plano de portão). Se mudou, o status do step é `PASS_WITH_BASELINE`, nunca `PASS`, e `full.category` é `PASS_WITH_BASELINE`. Sem git ou sem base: `null` (o D3a lê como não medido).

- **Quem decide**: `build_checks.py baseline`.
- **Critério de aceitação**: arquivo igual dá `moved: false`; arquivo diferente dá `moved: true` com os dois hashes.

### ITF-018 -- Linhas tocadas não cobertas (medida, não bloqueio)

`build_checks.py uncovered --base <rev> --coverage <json>`: linhas adicionadas ou alteradas (diff `-U0` contra a base) que são executáveis e **não** foram exercidas na rodada de cobertura **só de cenários** (`pytest -m scenario --cov --cov-branch --cov-report=json:<arq>`); ramos via `missing_branches`. Devolve `{n_touched, n_uncovered, items[{file, line, kind}], provisional}`. Por step é provisório (`provisional: true`): uma linha tocada no step 2 pode ser coberta por um cenário do step 4. A medida da feature é calculada no fim do plano sobre a união do diff (base = início do plano).

- **Quem decide**: `build_checks.py uncovered`.
- **Critério de aceitação**: a fixture de diff e cobertura dá o número conferido à mão; nada aqui bloqueia o step.

### ITF-019 -- Fim do plano

Plano v2 com `GATE_FULL_CMD` configurado: o `/implement` roda `full` uma vez no fim e grava `full` no `gate.json` `[default; aceito 2026-10-06]` (decisão pendente 4 = A). Sem `GATE_FULL_CMD`: `full: null` e o D3a fica `não medido` (`NM-SEM-GATE`) mesmo com todos os testes verdes; a nota diz isso. Depois: `uncovered` da feature, `record --feature-end`, `export` (ITF-023), a demonstração ao citizen (ITF-024) e, quando existir `drift_report.py`, o congelamento do M1 (`drift_report.py --feature <slug> --freeze --moment M1 --at <UTC>`).

- **Quem decide**: o `/implement`; o portão dá o resultado.
- **Critério de aceitação**: depois do fim do plano, `gate.json.full` existe (ou é `null` com a razão na nota) e `build.feature` tem `touched_total`, `touched_uncovered`, `base` e `baseline_moved`.

### ITF-020 -- Retomada

O progress file guarda, a cada transição, a linha `- itf: step <N> phase <fase> try <k> ok <true|false> ref <json>`. `build_checks.py status --feature <slug> --step N` lê `gate.json.build` e devolve a fase seguinte (`RED`, `GREEN`, `CLEAN`, `HARD`, `REC`, `DONE`). O `/implement` retoma da fase seguinte à última aprovada por ferramenta, nunca por memória do agente.

- **Quem decide**: `build_checks.py status`.
- **Critério de aceitação**: step com `red` ok e sem `green` devolve `GREEN`; step `PASS` devolve `DONE`.

### ITF-021 -- Compatibilidade

Plano v1 intocado (mesma sequência de ações da v0.10.1); `Scenarios: N/A (motivo)` e `Specify: skipped` seguem o caminho de antes; `--pipeline` em v1 recusado (ITF-001). Nenhum arquivo de portão, hook ou `settings` muda.

- **Quem decide**: designer (D-008).
- **Critério de aceitação**: o golden de `route` dos dois planos v1 não muda; nenhum diff deste plano toca portão, hook ou `settings`.

### ITF-022 -- O que esta norma não faz

Não reconstrói nem edita o portão, os hooks nem o `settings`; não altera `.feature`; não calcula D (plan-000008, plan-000014); não aprova baseline; não tem papel `architect` (violação de `lint-imports` volta ao Coder pelo `--fast`); só Python e pytest-bdd.

- **Quem decide**: designer.
- **Critério de aceitação**: nenhum texto desta norma traz fórmula de D; nenhuma ferramenta desta norma escreve em `quality-baseline.json`, `.feature` ou `conventions.md`.

### ITF-023 -- Exportação para o relatório de divergência

`build_checks.py export --feature <slug> [--cucumber <json>]` escreve os arquivos que o `drift_report.py` (plan-000014, `drift-report.md` DRP-001) lê, a partir de `gate.json.build`: `features/<slug>/runner/cucumber.json` (o Cucumber JSON da última rodada verde ou do `full`), `features/<slug>/drift/red-reason.json` (`{schema_version: 1, scenarios: {<chave>: true|false}}`, só cenários com registro), `features/<slug>/drift/coverage.json` (`{schema_version: 1, base, touched_total, touched_uncovered}`) e `baseline_moved` no topo do `gate.json`. Cenário sem registro de vermelho fica fora de `red-reason.json` (o calculador o lê como `NM-SEM-REGISTRO-VERMELHO`).

- **Quem decide**: `build_checks.py export`.
- **Critério de aceitação**: depois do `export`, os três arquivos existem com `schema_version: 1`; repetir dá bytes iguais.

### ITF-024 -- Demonstração por cenário e mutantes como perguntas (registro do citizen)

No fim do plano (M1), `build_checks.py demo --feature <slug>` escreve, em pt-BR e voz controlada, uma linha por cenário com a narração dos seus passos em primeira pessoa e um de três estados em palavras: **demonstrado** (vermelho pelo motivo certo, depois verde), **não demonstrado** (o teste não ficou verde), **não medido** (sem registro). Depois, cada mutante sobrevivente recontado como **pergunta** (o texto que o Hardener escreveu: "Se <o código fizesse outra coisa>, nenhum cenário perceberia. Isso importa para você?"). Nenhum número técnico, PASS ou percentual entra nesse texto (CYC-013, CYC-014, D-004). **Ruptura que pode provocar**: o citizen lê a narração de um cenário e diz "não é isso", ou responde "importa" a uma pergunta e o mutante vira requisito novo.

- **Quem decide**: designer (o texto); `demo` só monta.
- **Critério de aceitação**: a saída de `demo` não contém dígito fora do texto do cenário, nem `PASS`, nem `%`; todo cenário dono aparece com um dos três estados.

### ITF-025 -- O `scenario-tester` como terceiro amigo (informativo)

Antes da aprovação dos cenários (specify, SPC-009), o `/plan` pode chamar o `scenario-tester` em modo `review`: ele lê o `.feature` e o índice de step definitions e devolve, por cenário, se consegue escrevê-lo como teste vermelho pelo motivo certo (Then observável, dado montável, sem detalhe de implementação). O resultado é **informativo**: não bloqueia, não muda o `.feature` e entra na apresentação ao power dev como nota.

- **Quem decide**: designer (aprova os cenários); o agente só informa.
- **Critério de aceitação**: o agente em modo `review` não escreve arquivo; a nota lista cenários com risco e o motivo em uma frase.

---

## Procedimento do `/implement` (o que o orquestrador executa)

Variáveis: `Q` = `QUALITY_DIR` do projeto (padrão `_output/quality`); `BC` = `python3 .claude/skills/scripts/build_checks.py`; `BB` = `python3 .claude/skills/scripts/build_brief.py`; `<pfx>` = `Q/plan-<id>-step-<N>`; `<run>` = o comando de teste do projeto com `--scenario-report <json> --cucumberjson <json> --junitxml <xml>` (e, no RED, `--cov=<pacote> --cov-branch --cov-report=json:<json>`). Cada linha abaixo é uma transição; ela só acontece com o exit indicado. `<fase-base>` = o instantâneo da árvore no começo da fase de cada papel (`git add -A && git write-tree`, depois `git reset -q`): o vermelho nunca é commitado (ITF-006), então o `scope` de cada papel compara com o instantâneo da sua fase, não com o começo do step (achado do ensaio do plan-000013).

1. **Início do run.** `BC route <plano> [--pipeline] --json`. Exit 1 com a frase de ITF-001: diga a frase e pare sem nenhuma ação. Exit 2: pare com a mensagem. Plano v2 com `Specify: approved`: `check_specify.py <raiz> --feature <slug> --status --json`; estado diferente de `approved` = pare com "os cenários estão desatualizados: refaça a specify". `BC install-plugin <raiz>` (exit 1: pare e mostre a mensagem; o humano decide sobre a cópia editada).
2. **Step `no-scenario`.** O contrato atual do subagente de step, sem mudança. Depois: `BC record --feature <slug> --step N --from <payload> --at <UTC>` com `{"step": {"mode": "no-scenario", "reason": "<motivo>", "status": "<SUCCESS|PARTIAL>"}}`.
3. **PRÉ (step `test-first`).** `git rev-parse HEAD` = `<base>`; `<run>` com saída `<pfx>-base-*` (suíte-base). Algum `failed` ou `error` = pare: a suíte-base não está verde (ITF-002). `BC status --feature <slug> --step N [--pipeline]` diz de que fase retomar (ITF-020).
4. **RED** (até 3 tentativas). `BB --role tester ...` -> subagente `scenario-tester` novo com o briefing. `<run>` com saída `<pfx>-red-try-<k>-*`. `BC red-check --report <pfx>-red-try-<k>-scenarios.json --owned <chaves> --root <raiz> --files <código do step> --coverage <cov> --baseline <pfx>-base-scenarios.json --skeleton <arquivos de código> --at <UTC> --json > <pfx>-red-try-<k>-check.json`. Exit 0: `BC freeze --root <raiz> --write <pfx>-freeze.json <.feature da feature> <arquivos de teste do step>`; `BC record` com `scenarios[<chave>].red` e `step.phases.red`. Exit 1 com `escalate: true` (já verde): escalada (ITF-014). Exit 1: nova tentativa com os achados no briefing.
5. **GREEN** (até 3 tentativas, as mesmas 3 rodadas do portão do Auto Mode). `BB --role coder --tool-output <pfx>-red-try-<k>-check.json` (com `frozen` = os arquivos congelados) -> subagente de step novo (o Coder). `BC scope --role coder --base <fase-base> --frozen <pfx>-freeze.json`; `BC freeze --check <pfx>-freeze.json`; `<run>`; `BC green-check --report <...> --owned <chaves>`; `GATE_FAST_CMD --files <tocados> > <pfx>-green-try-<k>.json`. Todos 0 e `status` PASS: `BC record` com `fast`, `scenarios[<chave>].final` e `step.phases.green`.
6. **CLEAN** (só `--pipeline`; até 3). `radon cc -j <pacote>` e o `coverage.json` do GREEN; `BC crap --radon ... --coverage ... --files <tocados> --json`. Lista vazia: `phases.clean = {skipped: true}`. Senão: `BB --role cleaner --tool-output <crap.json>` -> subagente `cleaner` novo; `BC scope --role cleaner --base <fase-base>`, `BC freeze --check`, `<run>`, `BC green-check`, `GATE_FAST_CMD --files`.
7. **HARD** (só `--pipeline`; até 3). `GATE_FULL_CMD --files <tocados> > <pfx>-hard-try-<k>.json`. Sem achado de categoria 6: `phases.hard = {skipped: true}`. Senão: o orquestrador monta `{"survivors": [{"key", "mutant", "diff"}]}` (o `diff` de `mutmut show <mutante>`), `BB --role hardener` -> subagente `hardener` novo; `BC scope --role hardener --base <fase-base>`, `BC freeze --check`, `<run>`, `GATE_FULL_CMD --files`. As perguntas que o Hardener devolve vão para `Q/plan-<id>-questions.json` (lista).
8. **REC.** `BC baseline --base <base> --json` (um baseline que o humano aceitou durante o step aparece aqui, não no `scope`: o humano age entre as fases, nunca dentro da fase de um papel); `BC uncovered --base <base> --coverage <cobertura só de cenários: pytest -m scenario --cov ...> --json`; `BC record` com `step.status` (`PASS`, ou `PASS_WITH_BASELINE` se `moved`), `step.pipeline`, `step.baseline_moved`, `step.touched_uncovered`. Nota do step com `step_notes.py append ... --pipeline <on|off> --red-reason-ok <true|false|null>`; uma linha `- itf: step <N> phase <fase> try <k> ok <...> ref <json>` no progress a cada transição.
9. **Fim do plano** (ITF-019). `GATE_FULL_CMD --json > Q/plan-<id>-full.json` (sem `GATE_FULL_CMD`: `full: null` e a nota diz `não medido`); `<run>` final; `BC uncovered --base <base do plano> --final`; `BC baseline --base <base do plano>`; `BC record --step 0` com `full`, `baseline_moved` e `feature {touched_total, touched_uncovered, base, baseline_moved}`; `BC export --feature <slug> --cucumber <Cucumber JSON final>`; `BC demo --feature <slug> --questions Q/plan-<id>-questions.json` (mostre o texto ao usuário: é o registro do citizen); se `drift_report.py` existir: `drift_report.py --feature <slug> --moment M1 --freeze --at <UTC>`.

Teto de invocações: no máximo 10 subagentes por step (ITF-013). A escalada (ITF-014) é a saída de qualquer teto.

## Decisões pendentes do plan-000013 e o default adotado

| # | Decisão | Default adotado | Regra |
|---|---|---|---|
| 1 | `--pipeline` opt-in ou padrão no v2 | A: opt-in; o vermelho por cenário é sempre ligado no v2 `[default; aceito 2026-10-06]` | ITF-010, ITF-011 |
| 2 | Onde moram os registros do build | A: `gate.json.build` (e exportação para os arquivos do plan-000014) `[default; aceito 2026-10-06]` | ITF-015, ITF-023 |
| 3 | Tetos do loop | A: 3 por fase, 10 invocações por step `[default; aceito 2026-10-06]` | ITF-013 |
| 4 | Rodada `full` ao fim do plano v2 | A: sempre que `GATE_FULL_CMD` está configurado `[default; aceito 2026-10-06]` | ITF-019 |
| 5 | Alvo de CRAP do Cleaner | B: 8, configurável, piso 6 `[default; aceito 2026-10-06]` | ITF-010 |
| 6 | Vermelho que já nasce verde | A: escalada `[default; aceito 2026-10-06]` | ITF-005, ITF-014 |
| 7 | `--pipeline` em plano v1 | B: recusa em uma frase `[default; aceito 2026-10-06]` | ITF-001 |

## Costura com o plan-000008 (colunas derivadas e fontes)

| Coluna / dado do 000008 | Quem escreve | Onde | Regra |
|---|---|---|---|
| `test_result` (D2 e D3a) | plugin `scenario_report` na última rodada verde e no `full` | `build.scenarios[chave].final.test_result` e `runner/cucumber.json` | ITF-009, ITF-016, ITF-023 |
| chave cenário -> teste, `req` | plugin | relatório JSON e propriedades JUnit | ITF-016 |
| `skip`/`xfail` = descoberto (D2) | plugin registra; o step não passa com ele | idem | ITF-009 |
| `red_reason_ok` (D3a) | `build_checks.py red-check` | `build.scenarios[chave].red.reason_ok` e `drift/red-reason.json` (`null` = sem registro = `NM-SEM-REGISTRO-VERMELHO`) | ITF-005, ITF-006, ITF-023 |
| gate `full` PASS (D3a) | `/implement` no fim do plano | `gate.json.full` | ITF-019 |
| "sem `--accept-baseline`" (D3a) | `build_checks.py baseline` | `build.steps[N].baseline_moved`, `build.feature.baseline_moved`, `gate.json.baseline_moved` | ITF-017 |
| `touched_uncovered` (D3b) | `build_checks.py uncovered` | `build.steps[N].touched_uncovered` (provisório), `build.feature` e `drift/coverage.json` (final) | ITF-018, ITF-019 |
| linhas **e** ramos | idem | `kind: line\|branch` | ITF-018 |

Estado "descoberto por baseline": `status = PASS_WITH_BASELINE` (leitura do 000008: "PASS só com baseline aceito").

## Ferramentas: subcomando e regra

| Subcomando de `build_checks.py` | Regra |
|---|---|
| `route` | ITF-001, ITF-003, ITF-021 |
| `install-plugin` | ITF-016 |
| `skeleton` | ITF-004 |
| `red-check` | ITF-005, ITF-006 |
| `green-check` | ITF-009 |
| `freeze` | ITF-007 |
| `scope` | ITF-008 |
| `crap` | ITF-010 |
| `uncovered` | ITF-018 |
| `baseline` | ITF-017 |
| `record` | ITF-015, ITF-019 |
| `status` | ITF-020 |
| `export` | ITF-023 |
| `demo` | ITF-024 |

Saída de todos: legível em stdout, `--json` com `schema_version: 1`; exit 0 ok, 1 achado, 2 uso, leitura ou dado ausente (sem traceback). Nada de LLM, rede ou relógio fora de `--at`.
