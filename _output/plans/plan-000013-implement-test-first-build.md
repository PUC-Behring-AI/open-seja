# Plan 000013 | FEATURE-O | 2026-10-05 12:43 UTC | implement-test-first-build: /implement por step com teste vermelho por cenário, Coder, Cleaner (CRAP), Hardener (mutação) e loop até PASS | Review: standard

> **Origem**: movido do ledger do Doutourado em 2026-10-05 (proposal-000088; la era `plan-000082`). Os IDs roadmap-000006 e plan-000007..000016 sao deste ledger (tabela no roadmap). Referencias a research-NNNNNN, reflection-NNNNNN, communication-NNNNNN, roadmap-000062 e plan-000064..000074 apontam para o ledger do Doutourado (repositorio do pesquisador). Caminhos `open-seja/...` em Files passam a ser relativos a raiz deste repositorio.
plan_format_version: 1

> Item 7 do roadmap-000006 (Wave 3; Depends on: plan-from-scenarios = plan-000012). Repositório de execução: **open-seja** (worktree/branch por plano); o plano vive no Doutourado. C1: nenhum nome de parceiro nos artefatos que forem ao open-seja. ID alocado pelo orquestrador (não usa `reserve_id.py`). Este plano é `plan_format_version: 1` porque o v2 só existe depois que o 000012 executar. Usa o vocabulário dos planos 000007 (`CYC-NNN`, `features/<slug>/gate.json`, `--pipeline` reservado, teste vermelho pelo motivo certo), 000008 (D2, D3a, D3b, colunas derivadas `test_result`, `red_reason_ok`, `touched_uncovered`, `baseline`), 000009 (`intent.md`), 000010 (`check_features.py`, `GHK-NNN`, `conftest` modelo, propriedade `req`, Outline = um cenário), 000011 (`check_specify.py --status`, `scenarios.lock.json`, `stale`) e 000012 (`check_plan_scenarios.py`, `PFS-NNN`, `Scenarios:` com chave `<slug>/<arquivo>::<nome>`, dono único, parada de uma linha no `/implement`, ordem de edição dos `SKILL.md` 76 → 78 → 80 → 81 → **82**). Consome o gate do plano 000065 e os hooks do plano 000068; não os reconstrói. Não reabre nenhuma decisão fechada daqueles planos.

## User brief

> Item 7 do roadmap-000006: `implement-test-first-build` (Depends on: plan-from-scenarios). "/implement por step: cenário vira teste vermelho pelo motivo certo, Coder, Cleaner (CRAP), Hardener (mutação), contexto curto por papel, loop até PASS; consome o gate do roadmap-000062 (plan-000065)."

## Agent interpretation

**Problem.** O 000007 fixou o contrato do teste-primeiro só em texto ("o teste fica vermelho pelo motivo certo, por cenário, antes do código") e reservou `--pipeline` para este item. O 000012 entrega, por step, a lista de cenários que ele é dono. Falta o motor: **como** se decide, por ferramenta, que um teste está vermelho pelo motivo certo (e não por erro de import, de fixture ou de sintaxe); **quem** escreve o quê e o que cada papel enxerga; **como** o Cleaner e o Hardener entram sem desmanchar o teste congelado; **quando** o loop para e chama o humano; e **o que fica registrado** para que o 000008 (D2, D3a, D3b) e o item 8 tenham dado de entrada. Sem isso, "PASS" volta a ser uma frase do agente, e o D3a do 000008 não tem a evidência "vermelho pelo motivo certo" que ele exige.

**Approach.** Plano **técnico** (o segundo do ciclo com código, depois do 000010), no open-seja, em cinco peças:
1. **Norma** `implement-test-first.md` com regras `TFB-NNN` (aplicabilidade, vermelho pelo motivo certo, congelamento, escopo por papel, contexto por papel, limiares do Cleaner, critério do Hardener, loop e teto, escalada, registro, `--accept-baseline`).
2. **Plugin de relatório do runner** (`scenario_report`, pytest + pytest-bdd): promove o `conftest` modelo do 000010 a ferramenta. Escreve, por cenário, a chave `<slug>/<arquivo>::<nome>`, a propriedade `req`, o resultado, o tipo do step que falhou e as linhas de `Examples`, num JSON próprio e em propriedades JUnit. É a fonte do D2 e da evidência de vermelho.
3. **Verificador determinístico** `build_checks.py` (biblioteca padrão, sem LLM): `red-check` (vermelho pelo motivo certo), `freeze` (testes congelados), `scope` (o papel só tocou o que podia), `uncovered` (linhas tocadas que nenhum teste de cenário exerce), `baseline` (o baseline do gate foi movido?), `record` (grava no `gate.json`).
4. **Papéis com contexto curto**: três agentes novos (`scenario-tester`, `cleaner`, `hardener`) mais o subagente de step já existente como **Coder**; um montador de briefing (`build_brief.py`) que entrega a cada papel só o que ele precisa e recusa passar de um teto.
5. **Texto do `/implement`**: flag `--pipeline`, ramo do plano v2 (vermelho → verde → [limpar → endurecer]), loop com teto, escalada ao humano e retomada pelo progress file. Plano v1 não muda de comportamento.

O que **não** muda: o gate (`gate.py`, plano 000065), os hooks `Stop` e `PreToolUse`, o deny de `--no-verify` e `--accept-baseline` e o `settings.json` (plano 000068). O plano os chama; não os edita.

**Alternatives rejected.**
- **Skill separada `/build`** (rascunho de 2026-09-30): bifurca o ciclo de H-008; o roadmap fechou `/implement` por step com `--pipeline`.
- **O mesmo agente escreve o teste vermelho e o código**: o agente conhece o código que vai escrever e tende a escrever o teste que ele já passa. Papel separado, contexto separado, e o teste congelado por hash antes do Coder (TFB-007).
- **Decidir "vermelho pelo motivo certo" por leitura do agente ou de LLM**: contradiz "PASS is a tool result, not a sentence" (research-000050). O critério é mecânico: resultado `failed` (não `error`), exceção `AssertionError`, step que falhou do tipo `Then`, asserção não constante, código do step exercido (TFB-005).
- **Cleaner e Hardener sempre ligados**: o 000007 e o research-000050 (rec 20) pedem medir findings por step antes. Ficam atrás de `--pipeline` (Decisão pendente 1) e o Step 8 mede.
- **Papel `architect` agora**: o roadmap lista Coder, Cleaner e Hardener; o `lint-imports` já roda no `--fast` (etapa 5 do gate) e devolve a violação ao Coder. Fica para depois, registrado como lacuna.
- **Reconstruir CRAP e mutação para o pipeline**: o gate do 000065 já os calcula por função tocada (`--files`, `--full`). O pipeline lê o JSON do gate.
- **Gravar o vermelho em commit**: o `PreToolUse` em `git commit` roda o gate e recusaria a árvore vermelha. A prova é o registro com hashes e o relatório, não um commit (TFB-006).

**Selection rationale.** Sem `source:`. Fontes: roadmap-000006 (item 7, tabela "Decisões", H-009), research-000050 (§1.1 pipeline e papéis; §1.2 CRAP por função e mutação; §3 limiares e anti-gaming; §10.3 `--pipeline`; recs 17 a 20), roadmap-000062 (`--pipeline` previsto; backlog) e os planos 000065, 000068, 000007 a 000012.

### Decisões fechadas (aprovadas pelo designer; não reabrir)
1. Teste-primeiro dentro do `/implement`, por step, com a flag `--pipeline` prevista no roadmap-000062. Sem skill nova, sem preset, sem perfil.
2. Plano v2 com `Scenarios:` obrigatório; v1 válido para sempre e **não muda de comportamento**.
3. Outline = um cenário (chave única; as linhas de `Examples` ficam como detalhe no relatório).
4. `skip` e `xfail` contam como **descoberto** (000008, D2). Aqui isso vira regra de PASS: cenário `skipped`/`xfailed` não é verde (TFB-009).
5. Gate (plano 000065) e hooks (plano 000068) são consumidos, não reconstruídos.
6. Estado `stale` (000011) vale como "cenários não aprovados": o `/implement` não começa nem continua (000012, PFS-011).
7. Dono único do cenário (000012, Decisão pendente 2, default A). Com B, o ponto verde do cenário fica ambíguo; o Step 1 confere qual vigorou.
8. Este plano não escreve em `product-design/` do Doutourado, não edita roadmap nem INDEX e não muda gate, hooks ou `settings`.

### Fluxo por step (resumo; o texto normativo é o Step 2)

```
passo v2 com Scenarios (dono)
  PRÉ   status=approved? plano=000012 OK? suíte-base verde?  (ferramentas; se não: parar)
  RED   Tester escreve step definitions + teste + esqueleto neutro
        red-check: failed, AssertionError, step Then, asserção não constante, código exercido, resto da suíte verde
        registra red{...}; congela hashes (feature + testes dos cenários)      [<= 3 tentativas]
  GREEN Coder escreve o mínimo; scope-check; freeze-check;
        cenários donos = passed (não skip/xfail); gate --fast --files PASS     [<= 3 tentativas, como o 000068]
  --pipeline:
  CLEAN Cleaner só se CRAP de função tocada > alvo; só código-fonte; testes congelados;
        cenários continuam verdes; gate --fast PASS                            [<= 3]
  HARD  Hardener só se há mutante sobrevivente em função tocada; só testes novos
        (e pragma com motivo); mutação restrita às funções tocadas             [<= 3]
  REC   grava gate.json (fast, build.steps[N]); baseline_moved? status
fim do plano: full (Decisão pendente 4), touched_uncovered da feature, relatório
```

Status do step: `PASS`, `PASS_WITH_BASELINE` (o humano moveu o baseline; D3a trata como descoberto), `ESCALATED` (teto atingido; o humano decide). Step sem cenário (infraestrutura, config, `Specify: skipped`) segue o caminho de antes (Coder + gate `--fast` do 000068), sem vermelho e sem papéis novos.

### Decisões pendentes
Cada uma tem default (a recomendação). Se o designer não responder, os steps seguem o default; mudar uma altera só o Step indicado.

**Decisão pendente 1 -- `--pipeline` (Cleaner e Hardener) é opt-in ou padrão no plano v2?** (afeta Steps 7, 8)
- Opção A: opt-in. Plano v2 roda sempre vermelho → Coder → gate `--fast`; Cleaner e Hardener só com `--pipeline`.
- Opção B: padrão no v2, com `--no-pipeline` para desligar.
- Opção C: padrão no v2 só quando `GATE_FULL_CMD` está configurado.
- **Recomendação: A.** Recommended when o research-000050 (rec 20) pede medir findings por step antes de ligar os passes separados, e o piloto (item 10) vai ligar `--pipeline` no braço estendido e registrar. NOT recommended when o Step 8 mostrar que quase todo step tem CRAP acima do alvo ou sobrevivente (então B ou C: o subagente do step não dá conta sozinho). O vermelho por cenário **não** é opcional: é o contrato do v2 (000007).

**Decisão pendente 2 -- Onde moram os registros do build** (afeta Steps 2, 5, 9; lacuna com 000007/000008)
- Opção A: `features/<slug>/gate.json` ganha a chave aditiva `build` (e mantém `fast`, `full`, `ts` do 000007).
- Opção B: arquivo novo `features/<slug>/build-record.json`; `gate.json` fica só com `{fast, full, ts}` e ponteiros.
- **Recomendação: A.** Recommended when o item 8 já lê `gate.json` e um arquivo a menos reduz a junção. NOT recommended when o Step 1 achar que o 000007/000010 declararam `gate.json` como esquema fechado ou que um validador rejeita chave desconhecida (então B, sem tocar o esquema). Leitores que ignoram chaves desconhecidas não sentem a diferença.

**Decisão pendente 3 -- Tetos do loop** (afeta Steps 6, 7)
- Opção A: 3 tentativas por fase (vermelho, verde, limpar, endurecer) e no máximo 10 invocações de papel por step.
- Opção B: só o `--max-iterations` global que o `/implement` já tem.
- Opção C: 5 tentativas por fase.
- **Recomendação: A.** Recommended when o verde já tem 3 tentativas no 000068 e o mesmo número nas outras fases mantém o custo previsível e a escalada rápida. NOT recommended when o piloto mostrar que o Hardener precisa de mais (então C só para ele). B sozinho deixa uma fase consumir o orçamento das outras.

**Decisão pendente 4 -- Rodada `full` ao fim do plano v2** (afeta Steps 7, 8; lacuna com 000008)
- Opção A: sempre que o plano é v2 e `GATE_FULL_CMD` está configurado, `/implement` roda `full` uma vez no fim e grava `full` no `gate.json`.
- Opção B: só com `--pipeline`.
- Opção C: só a pedido.
- **Recomendação: A.** Recommended when o 000008 define D3a como "teste verde **e** `full` PASS sem baseline movido", e sem `full` gravado o D3a fica `não medido` mesmo com todos os testes verdes. NOT recommended when a mutação completa passa de ~30 min no projeto (então B, e declarar D3a `não medido` no ciclo sem pipeline). O custo é uma rodada por plano.

**Decisão pendente 5 -- Alvo de CRAP do Cleaner** (afeta Steps 2, 6)
- Opção A: o limiar do gate (10, `crap_max_touched`); o Cleaner nunca dispara, porque o gate já barrou antes.
- Opção B: alvo 8 em funções tocadas, configurável (`CRAP_TARGET_TOUCHED`); piso 6.
- Opção C: alvo 6.
- **Recomendação: B.** Recommended when o research-000050 §3 fixa "10 agora, 8 após o piloto, 6 depois" e o piloto no `pegasus` já foi medido (15 de 45 funções acima de 8). NOT recommended: C agora (agente fragmenta em helpers de uma linha para satisfazer o número) e A (o papel deixa de existir). O gate continua barrando em 10; o alvo do Cleaner é só o limiar do passe, nunca um novo bloqueio.

**Decisão pendente 6 -- Vermelho que já nasce verde (cenário passa antes de qualquer código)** (afeta Steps 5, 7)
- Opção A: escalada. O cenário é do step, deveria falhar; verde antes do código indica teste fraco ou cenário já entregue por outro step.
- Opção B: aceitar como `already_green`, pular o Coder, registrar.
- **Recomendação: A.** Recommended when o dono é único (000012) e o D3a usa o vermelho como evidência. NOT recommended when o step é de regressão por design (então B, com `Tests:` dizendo "regressão" e o motivo no registro). Outline: vermelho se **alguma** linha falha pelo motivo certo e nenhuma dá `error`; linhas verdes no vermelho ficam em `rows_green_in_red` (informação de teste fraco).

**Decisão pendente 7 -- `--pipeline` em plano v1** (afeta Step 7)
- Opção A: aceita e roda só Cleaner e Hardener (sem vermelho).
- Opção B: recusa com uma frase ("`--pipeline` é do plano v2").
- **Recomendação: B.** Recommended when "v1 não muda de comportamento" e o braço de controle do piloto (ciclo padrão) não pode ser contaminado. NOT recommended when o power dev quiser CRAP e mutação em projeto antigo (então A, depois do piloto).

## Files

Todos no **open-seja**, exceto onde dito. O submodule não está inicializado neste worktree; caminhos **não verificados**: o Step 1 os confere antes de qualquer escrita.

- `.claude/references/general/implement-test-first.md` (create) -- norma `TFB-NNN`
- `.claude/skills/scripts/build_checks.py` (create) -- `red-check`, `freeze`, `scope`, `uncovered`, `baseline`, `record`
- `.claude/skills/scripts/build_brief.py` (create) -- montador de briefing por papel, com teto de tamanho
- `.claude/references/template/bdd/python/scenario_report.py` (create) -- plugin pytest; copiado para `tests/` do projeto no primeiro vermelho
- `.claude/agents/scenario-tester.md`, `.claude/agents/cleaner.md`, `.claude/agents/hardener.md` (create)
- `.claude/skills/implement/SKILL.md` (modify) -- flag e ramo v2, por referência à norma (limite de tamanho: Step 1 mede)
- `.claude/references/template/feature-example/conftest.py` (modify, só se existir após o 000010: passa a importar o plugin)
- `.claude/skills/scripts/step_notes.py` (modify, mínimo) -- campos do pipeline na nota de reflexão, se o Step 1 confirmar o ponto de extensão do 000068
- `.claude/skills/scripts/tests/test_build_checks.py`, `test_scenario_report.py`, `test_build_brief.py` e `tests/fixtures/build/` (create) -- fixtures primeiro
- `.claude/references/general/extended-cycle-contract.md` (modify, só linha de ponteiro, se existir)
- `_output/plans/plan-000013-progress.md` (create no Doutourado)

## Best practices

- "PASS is a tool result, not a sentence" (research-000050): cada transição de fase é um código de saída ou um JSON, nunca "terminei" do agente.
- Agentes estreitos e descartáveis, "spawn for one job, then destroy": um subagente novo por invocação, com briefing curto montado por script. A perda de identidade de papel depois de compactações (research-000050 §1.1) é o motivo do teto e do escopo mecânico.
- Teste congelado: o Coder, o Cleaner e o Hardener não alteram o que o Tester entregou. Hash antes e depois.
- Anti-gaming (research-000050 §3): asserção não constante, todo teste afirma (já no `--fast`), mutante equivalente só com `# pragma: no mutate  # equivalent: <motivo>`, e o humano é dono do baseline.
- Fixtures primeiro (o mesmo princípio que este plano impõe): cada regra `TFB-NNN` tem um caso mínimo que a dispara e um que não.
- Funções puras (`parse`, `check_*`) separadas de CLI e I/O; biblioteca padrão; saída `--json` versionada (`schema_version`); timestamps em UTC; `ruff` e `pyright` limpos (standards.md § Backend 1, 4, 8, 19, 21).
- Voz controlada (plano 000074) nas mensagens que o citizen lê: a recusa, a escalada e o resumo de fim de step em frases curtas, termos fixos, primeira pessoa.
- Registrar o que **não** foi medido (`null`, `não medido`) em vez de omitir.

## Design decisions

- **User-visible impact:** quando você aprovar os cenários e mandar implementar, eu primeiro escrevo um teste para cada cenário e mostro que ele falha pelo motivo certo, isto é, porque o comportamento ainda não existe e não porque o teste está quebrado. Só então escrevo o código. Se eu não conseguir em três tentativas, eu paro e pergunto a você. Com `--pipeline` eu ainda deixo as funções mais simples e procuro testes que não pegam erros. Plano antigo roda como antes.
- **Trade-offs accepted:** mais invocações de agente por step (custo e tempo, medidos no Step 8 e no piloto) em troca de evidência mecânica por cenário; esqueleto neutro obrigatório no vermelho (o Tester não escreve lógica); a árvore fica vermelha entre RED e GREEN, e o `Stop` hook pode barrar uma pausa nesse intervalo (lacuna 9); só Python e pytest-bdd.
- **Metacommunication impact:** I know you may not read the tests; therefore I show you, for each scenario, the one sentence that says it failed because the behavior is missing, and I stop and ask you when I cannot make it pass, instead of telling you it is done.

## Steps

### Step 1: Conferir o terreno e as fontes de dado no open-seja
Na branch `dev` do open-seja (`git submodule update --init open-seja` se vazio), registrar no progress: (a) se os planos 000007, 000009, 000010, 000011 e 000012 já estão lá, com os identificadores reais (`CYC-NNN`, `GHK-NNN`, `SPC-NNN`, `PFS-NNN`) e a **ordem de edição** de `implement/SKILL.md` e `_internal/plan/standard/SKILL.md` (76 → 78 → 80 → 81 → este); **se o 000012 não executou, parar** (este plano depende do campo `Scenarios:`, do lock e de `check_plan_scenarios.py`); (b) a linha de parada do `/implement` do 000012 (existe? Decisão pendente 4 dele: A ou B); (c) o formato real da chave em `scenarios.lock.json` (`index`) e a função de chave de `check_features.py` (para o plugin reusar, não reescrever); (d) o `conftest` modelo do 000010 (hooks usados, nome da propriedade `req`) e a versão instalável de `pytest-bdd` com os hooks `pytest_bdd_apply_tag`, `pytest_bdd_step_error` e o atributo `step.type`; (e) do gate (`gate.py`): flags reais (`--fast`, `--full`, `--files`, `--json`, `--out-dir`, override de `crap_max_touched`), códigos de saída por categoria, como restringir a mutação às funções tocadas, o formato de `coverage.json` e `quality-baseline.json`, e se `--cov-context` é viável; (f) do `/implement`: o passo 8 do modo auto (contrato do subagente, três tentativas, `PARTIAL`, progress file), onde `--gate-json`/`--gate-attempts` vão para a nota de reflexão, o ponto de extensão de `step_notes.py`, e quantas linhas faltam até o limite do check `skill-body-length`; (g) se `features/<slug>/gate.json` foi declarado fechado (Decisão pendente 2); (h) o baseline de `run_all_checks.py` (falhas pré-existentes). Nada é escrito no open-seja.
- **Files**: open-seja/.claude/skills/implement/SKILL.md (read), open-seja/.claude/skills/_internal/plan/standard/SKILL.md (read), open-seja/.claude/references/template/quality-gate/python/gate.py (read), open-seja/.claude/references/template/feature-example/conftest.py (read, se existir), open-seja/.claude/skills/scripts/check_features.py (read, se existir), open-seja/.claude/skills/scripts/check_specify.py (read, se existir), open-seja/.claude/skills/scripts/check_plan_scenarios.py (read, se existir), open-seja/.claude/skills/scripts/step_notes.py (read)
- **References**: product-design/conventions.md, product-design/constitution.md, research-000050 §10
- **Interface**: N/A
- **Verify**: o progress lista cada item (a) a (h) como "existe", "rascunho" ou "ausente" com o caminho; a decisão de parar ou seguir está escrita; `git -C open-seja status` limpo.
- **Tests**: N/A (verificação de estado)
- [ ] Done

### Step 2: Escrever a norma do teste-primeiro (`implement-test-first.md`)
Criar o documento com as regras `TFB-001..022`, cada uma com "Quem decide" e "Critério de aceitação" (molde de `CYC-NNN` e `PFS-NNN`). Conteúdo mínimo:
- **TFB-001 Aplicabilidade.** Só plano `plan_format_version: 2` com `Specify: approved`. v1/ausente: nada deste documento roda (Decisão pendente 7: `--pipeline` em v1 é recusado com uma frase). Versão desconhecida: parar.
- **TFB-002 Pré-condições** (checadas por comando, no início do run e antes de cada step): `check_plan_scenarios.py` sai 0; `check_specify.py --status` devolve `approved`; suíte-base verde; `GATE_FAST_CMD` configurado (senão o step v2 roda sem gate, grava `gate: not-installed` e o D3a fica `não medido`, como o fallback do 000068).
- **TFB-003 Classes de step.** *Dono*: `Tests:` não-N/A e uma ou mais chaves em `Scenarios:`. *Sem cenário*: `Scenarios: N/A (...)` ou `Specify: skipped`; caminho antigo (Coder + gate `--fast`), registro `mode: no-scenario` e o motivo.
- **TFB-004 Esqueleto neutro.** No vermelho o Tester pode criar módulos e funções de **esqueleto** nos arquivos de código do step (`Files:`/`Interface:`): assinatura e corpo apenas `pass`, `...`, docstring ou `return <literal>`. Verificado por `ast`. Sem lógica.
- **TFB-005 Vermelho pelo motivo certo** (por cenário dono, lido do relatório do plugin): R1 o teste foi coletado e o resultado é `failed` (não `error`, `passed`, `skipped`, `xfailed`); R2 a exceção é `AssertionError`; R3 o tipo efetivo do step que falhou é `then` (falha em `given`/`when` = montagem quebrada); R4 o corpo do step que falhou não tem asserção constante (`assert False`, `assert 0`, `assert not True`, `raise AssertionError()` sem condição, `pytest.fail`); R5 o esqueleto cumpre TFB-004; R6 o restante da suíte (cenários não donos e testes existentes) passou como na linha de base; R7 o código do step foi exercido (cobertura da rodada vermelha cobre ao menos uma linha de corpo de função em arquivo de código de `Files:`; vale só quando o step cria ou modifica código); R8 Outline: ver Decisão pendente 6. Cada falha de R1 a R8 devolve a regra e uma dica em frase curta. Limitação declarada: a ferramenta não sabe se a asserção **diz** o que o cenário diz; isso é a auditoria humana por amostra do 000008 (Decisão pendente 1 dele).
- **TFB-006 Registro do vermelho.** `build.scenarios[<chave>].red = {ts, outcome, reason_ok, exception, failing_step_type, rows_total, rows_failed, rows_green_in_red, skeleton_files, report}`. O estado vermelho **não** é commitado (o `PreToolUse` em commit roda o gate e recusaria); a prova são o registro, os hashes e o relatório gravado em `_output/quality/`.
- **TFB-007 Congelamento.** Ao fim do vermelho, gravar SHA-256 dos `*.feature` da feature, dos arquivos de teste e de step definitions dos cenários donos. Coder, Cleaner e Hardener não os alteram; mudança = violação, o step volta ao vermelho (consome tentativa) ou escala.
- **TFB-008 Escopo por papel** (conferido por diff, por `build_checks.py scope`): Tester: só arquivos de teste, step definitions, `conftest` e esqueleto; Coder: código-fonte e testes **não congelados**, nunca `features/**`; Cleaner: só código-fonte (nenhum arquivo de teste); Hardener: só testes novos ou não congelados, mais linhas de comentário `# pragma: no mutate  # equivalent: <motivo>` no código. Nenhum papel toca `gate.py`, hooks, `settings*`, `quality-baseline.json`, `conventions.md` (linhas `GATE_*`).
- **TFB-009 Verde.** Cada cenário dono com resultado exatamente `passed` (`skipped`, `xfailed`, `error`, `missing` não são verde); `GATE_FAST_CMD --files <tocados> --json` com `status PASS`; freeze e scope limpos. Tentativas e `PARTIAL` como o 000068 define; não redefinir.
- **TFB-010 Cleaner.** Dispara só se o JSON do gate (ou o cálculo do `--fast` com o alvo) acusa função **tocada** com CRAP acima do alvo (`CRAP_TARGET_TOUCHED`, default 8, piso 6, Decisão pendente 5). Refatora sem mudar comportamento: cenários e suíte continuam verdes, testes intocados, `Interface:` do step preservada, gate `--fast` PASS. Não cria função de uma linha só para baixar o número (alvo abaixo do piso é recusado). Sem função acima do alvo: o passe é **pulado** e registrado.
- **TFB-011 Hardener.** Dispara só se a mutação restrita às funções tocadas (via o gate, `--full` com `--files` ou o que o Step 1 confirmar) deixa sobrevivente. Escreve testes que os matem ou anota equivalente com motivo. Saída: zero sobreviventes **inexplicados** nas funções tocadas; pragma sem motivo falha o gate (000065). Todo pragma novo entra no relatório de fim de step para revisão humana. Não gatear por percentual.
- **TFB-012 Contexto por papel** (montado por `build_brief.py`, teto de tamanho; ver Step 6): Tester vê o texto do step, o Gherkin dos cenários donos, `Interface:`, o índice de step definitions existentes e a convenção do plugin; **não** vê os outros steps nem o código novo. Coder vê o texto do step, o Gherkin dono, a saída do `red-check` (a mensagem da falha) e o escopo; **não** vê regras do Cleaner/Hardener. Cleaner vê só os achados de CRAP (`key`, cc, cobertura, limite), o corpo das funções tocadas acima do alvo e a regra de escopo. Hardener vê só a lista de mutantes sobreviventes (diff do mutante), as funções e os testes existentes e a regra do pragma. Nenhum vê o plano inteiro, o roadmap, nem a conversa.
- **TFB-013 Loop e teto.** Tentativas por fase e invocações por step conforme a Decisão pendente 3. Cada transição depende de código de saída de ferramenta. Um subagente novo por invocação.
- **TFB-014 Escalada.** Teto atingido, violação de congelamento persistente, vermelho sem motivo certo após o teto, ou `check_specify.py --status` ≠ `approved` a meio: status `ESCALATED`, gravação no progress file (fase, tentativa, último JSON), parada do run e `AskUserQuestion` com as opções do Step 7 (C4). O agente nunca move o baseline, nunca afrouxa limiar, nunca edita `.feature`.
- **TFB-015 Registros.** `features/<slug>/gate.json`: `fast` (último `--fast` do step), `full`, `ts` (contrato do 000007) e `build` (Decisão pendente 2) com `schema_version`, `scenarios{}`, `steps{}` e `feature{}`; campos do Step 5.
- **TFB-016 Relatório do runner.** Contrato do plugin (Step 4): por cenário `scenario_key`, `req` (lista), `feature_file`, `outcome`, `exception`, `failing_step_type`, `rows`, `reason`; propriedades JUnit `req` (repetida) e `scenario_key`; chave idêntica à de `scenarios.lock.json`.
- **TFB-017 Baseline.** `baseline_moved` é verdadeiro se `quality-baseline.json` mudou entre o início do step e o fim (diff do git). Agente não move (deny e hook do 000068). Se mudou, o status é `PASS_WITH_BASELINE`, nunca `PASS`.
- **TFB-018 Linhas tocadas não cobertas** (medida, não bloqueio): linhas adicionadas ou alteradas do step (diff `-U0` contra o início do step) executáveis e **não** exercidas por teste de cenário (rodada de cobertura só com testes que têm `req`); ramos via `missing_branches`. Por step é provisório; a medida da feature é calculada no fim do plano sobre a união.
- **TFB-019 Fim do plano.** `full` conforme a Decisão pendente 4; `build.feature{}` com `touched_uncovered`, contagens e `baseline_moved` acumulado; resumo em voz controlada.
- **TFB-020 Retomada.** O progress file guarda fase, tentativa e ponteiros; o `/implement` retoma da fase seguinte à última aprovada por ferramenta, nunca por memória do agente.
- **TFB-021 Compatibilidade.** v1 intocado; `Scenarios: N/A` e `Specify: skipped` seguem o caminho antigo; `--pipeline` em v1 recusado (default).
- **TFB-022 Não faz.** Não reconstrói nem edita gate, hooks, `settings`; não altera `.feature`; não calcula D (item 8 e 000008); não aprova baseline; não tem papel `architect`; só Python e pytest-bdd.
Incluir os defaults das Decisões pendentes 1 a 7 marcados `[default; pendente]`, a tabela estado → registro → coluna do 000008 (ver "Costura com o 000008" abaixo) e o fluxo por step.
- **Files**: open-seja/.claude/references/general/implement-test-first.md (create)
- **References**: product-design/constitution.md, product-design/standards.md § Testing, research-000050 §1, §3, §10
- **Depends on**: Step 1
- **Interface**: contratos de dado: `red` por cenário, `steps[N]`, `feature{}`, relatório do plugin; constantes `PIPELINE_MAX_TRIES = 3`, `PIPELINE_MAX_INVOCATIONS = 10`, `CRAP_TARGET_TOUCHED = 8`.
- **Verify**: o arquivo existe; toda regra `TFB-NNN` tem "Quem decide" e "Critério de aceitação"; `grep -c "TFB-"` >= 22; R1 a R8 estão numeradas; `git grep -ci` dos termos de C1 (lista do Step 1) devolve zero; `python .claude/skills/scripts/run_all_checks.py` igual ao baseline do Step 1.
- **Tests**: N/A (documento normativo; os testes são dos Steps 3 a 6)
- **Docs**: o próprio documento; o quickguide pt-BR fica para o item 9.
- [ ] Done

### Step 3: Criar fixtures golden e os testes que ainda falham (fixtures primeiro)
Criar em `tests/fixtures/build/` (todas fictícias, sem parceiro e sem dado real): (a) relatórios do plugin em JSON e JUnit para os casos do `red-check`: `red-ok` (failed, `AssertionError`, step `then`), `red-import-error` (`error` por `ModuleNotFoundError`), `red-given-failure` (falha em `given`), `red-when-failure`, `red-already-green` (passed), `red-skipped`, `red-xfail`, `red-constant-assert` (`assert False`), `red-collection-error`, `red-outline-partial` (3 linhas: 2 falham, 1 verde), `red-outline-error`, `red-suite-broken` (teste não dono vermelho); (b) pares de árvores `antes`/`depois` para `freeze` (arquivo `.feature` alterado, step definition alterado, intocado) e para `scope` (um caso por papel, com violações: Coder edita `.feature`, Cleaner edita teste, Hardener edita código além de pragma, qualquer papel edita `quality-baseline.json` ou `gate.py`); (c) um diff `-U0` e um `coverage.json` com `missing_lines` e `missing_branches` para `uncovered`; (d) um par de `quality-baseline.json` (igual / movido) para `baseline`; (e) árvores de esqueleto válidas e inválidas (corpo com lógica) para TFB-004; (f) dois planos v1 reais (cópia dos mesmos do 000007, sem dado privado) e um v2 válido, com a **sequência esperada de ações** do `/implement` em dry-run (golden). Escrever `test_build_checks.py`, `test_scenario_report.py` e `test_build_brief.py` **antes** do código: um teste por regra TFB que o código vai satisfazer. Rodar e registrar no progress que os testes falham (vermelho), por `ImportError` do módulo ainda inexistente **e** que, depois de criar um módulo vazio com as funções pendentes, passam a falhar por asserção.
- **Files**: open-seja/tests/fixtures/build/ (create; casos a até f), open-seja/.claude/skills/scripts/tests/test_build_checks.py (create), open-seja/.claude/skills/scripts/tests/test_scenario_report.py (create), open-seja/.claude/skills/scripts/tests/test_build_brief.py (create)
- **References**: product-design/standards.md § Testing, `.claude/references/general/implement-test-first.md`
- **Depends on**: Step 2
- **Interface**: esquema de entrada e saída dos subcomandos (o do Step 2); `Finding{rule, severity, scenario, file, message, hint}`; `Report{ok, findings, ...}`.
- **Verify**: `pytest` nos três arquivos mostra os testes falhando por asserção (segunda rodada) e a lista de testes cobre cada regra TFB-004 a TFB-011, TFB-016 a TFB-018 pelo menos uma vez com caso positivo e negativo; as fixtures não contêm termo de C1; os planos v1 são idênticos aos usados no 000007 (hash igual).
- **Tests**: when o relatório `red-import-error` é lido pelo `red-check`, returns um achado R1 (outcome `error`) e `ok = false`; when `red-given-failure` é lido, returns R3; when `red-constant-assert` é lido, returns R4; when `red-already-green` é lido, returns o achado da Decisão pendente 6 (default: escalada); when `red-outline-partial` é lido, returns `ok = true` e `rows_green_in_red = 1`; when o Coder altera um `.feature`, o `scope` returns violação TFB-008 com o arquivo; when `quality-baseline.json` difere entre o início e o fim, `baseline` returns `moved = true`. Estes testes são o contrato; passam nos Steps 4 e 5.
- **Docs**: um `README` de uma linha por fixture.
- [ ] Done

### Step 4: Implementar o plugin de relatório do runner (`scenario_report`)
Promover o `conftest` modelo do 000010 a plugin em `template/bdd/python/scenario_report.py` (um arquivo, só `pytest` e `pytest-bdd`; sem rede, sem LLM). Comportamento: (1) registra os markers `REQ-...` em `pytest_bdd_apply_tag` (herdado do modelo) e marca todo item de cenário com `scenario` (para a rodada de cobertura só de cenários); (2) opções `--scenario-report <path>` (JSON), `--scenario-key <chave>` (repetível; seleciona só esses cenários) e `--scenario-exclude-key`; (3) por item, grava `scenario_key` calculada **pela mesma função** de `check_features.py` (importada; se o arquivo não estiver no caminho, copia a função com um teste de igualdade), `feature_file`, `req` (lista das tags `@REQ-...`), `outcome` (`passed|failed|error|skipped|xfailed|xpassed`), `exception` (nome da classe), `failing_step_type` (de `pytest_bdd_step_error`, `step.type` efetivo), `reason` (mensagem curta), `duration`; (4) propriedades JUnit via `record_property`: `scenario_key` e uma `req` por tag; (5) Outline: um registro por chave com `rows[]` (índice, outcome, exception, failing_step_type) e `outcome` agregado (`passed` só se todas passaram; `failed` se alguma falhou; `skipped`/`xfailed` se alguma); (6) erro de coleta aparece como `error` com `exception`, não some; (7) o JSON traz `schema_version: 1`, `generated_at` UTC e `pytest_bdd_version`. Instalação: `build_checks.py install-plugin <projeto>` copia o plugin para `tests/scenario_report.py` e acrescenta `pytest_plugins = ["scenario_report"]` ao `tests/conftest.py` (cria se faltar; idempotente; registra o hash; nunca sobrescreve plugin alterado à mão sem aviso). O `conftest` do exemplo do 000010 passa a importar o plugin em vez de repetir a lógica.
- **Files**: open-seja/.claude/references/template/bdd/python/scenario_report.py (create), open-seja/.claude/skills/scripts/build_checks.py (create, só `install-plugin` neste step), open-seja/.claude/references/template/feature-example/conftest.py (modify, se existir), open-seja/.claude/skills/scripts/tests/test_scenario_report.py (modify)
- **References**: product-design/standards.md § Testing, `.claude/references/general/implement-test-first.md`
- **Depends on**: Step 3
- **Interface**: `ScenarioRecord{scenario_key, feature_file, req, outcome, exception, failing_step_type, reason, rows, duration}`; opções de linha de comando acima; arquivo JSON `schema_version: 1`.
- **Verify**: `uv run --with pytest-bdd pytest` sobre o exemplo mínimo (num diretório temporário) produz o JSON com 2 passed, 1 failed por `AssertionError` com `failing_step_type = "then"`, 1 skipped e o Outline agregado; a propriedade `req` aparece em todo teste de cenário no JUnit; `scenario_key` de cada cenário do exemplo é igual à chave de `check_features.py --matrix` e à do `scenarios.lock.json` da fixture (teste de contrato); os testes do Step 3 do arquivo `test_scenario_report.py` passam; `ruff` e `pyright` limpos. Se `pytest-bdd` não puder ser instalado no ambiente de verificação, registrar "não provado" no progress e manter a prova com relatórios fixture (Step 3).
- **Tests**: when um cenário falha em um `Then`, returns `failing_step_type = "then"` e `exception = "AssertionError"`; when falha em um `Given`, returns `"given"`; when a definição de step falta, returns `outcome = "error"` com `exception` de step não encontrado; when `--scenario-key` é passado, returns só aquele cenário coletado; when um Outline tem linhas mistas, returns `outcome` agregado `failed` e `rows` com o detalhe; when o nome do cenário tem acento, espaço ou `::`, returns a mesma chave que a do lock da fixture.
- **Docs**: seção "Relatório do runner" na norma e comentário de cabeçalho do plugin com as opções.
- [ ] Done

### Step 5: Implementar os verificadores determinísticos (`build_checks.py`)
Funções puras mais CLI: `build_checks.py <subcomando> ... [--json]`, exit 0 ok, 1 achado de erro, 2 erro de uso ou dado ausente. Subcomandos: **`red-check`** `--report <json> --owned <chaves> [--files <fonte...>] [--coverage <json>] [--baseline-passed <lista>]`: aplica R1 a R8 (TFB-005) e devolve, por cenário, `red{...}` pronto para gravar; **`skeleton`** `<arquivos>`: TFB-004 por `ast`; **`freeze`** `--snapshot <json> | --write`: grava ou confere hashes (TFB-007); **`scope`** `--role <tester|coder|cleaner|hardener> --base <rev> [--frozen <snapshot>]`: lê `git diff --name-status` e, para o Hardener, confere que o diff do código-fonte são só linhas de pragma (TFB-008); **`uncovered`** `--base <rev> --coverage <json> --report <json>`: interseção do diff `-U0` com `missing_lines`/`missing_branches` da rodada só de cenários (TFB-018), devolve `{n_touched, n_uncovered, items[{file,line,kind}], provisional}`; **`baseline`** `--base <rev> [--file quality-baseline.json]`: `moved`, `sha_before`, `sha_after` (TFB-017); **`record`** `--feature <slug> --step N --from <json>`: grava no `features/<slug>/gate.json` sem apagar chaves desconhecidas, escrita atômica (arquivo temporário + rename), `fast`/`full`/`ts` conforme o 000007 e `build{}` conforme a Decisão pendente 2; **`status`** `--feature <slug> --step N`: lê o registro e devolve a fase seguinte (suporte à retomada, TFB-020). Nada de LLM, rede ou relógio fora de `--at`; ordem de saída estável.
- **Files**: open-seja/.claude/skills/scripts/build_checks.py (modify), open-seja/.claude/skills/scripts/tests/test_build_checks.py (modify)
- **References**: product-design/standards.md § Backend 1, 4, 5, 8, 19, 21; `.claude/references/general/implement-test-first.md`
- **Depends on**: Step 4
- **Interface**: funções `red_check(report, owned, *, source_files, coverage, baseline_passed) -> RedReport`; `check_skeleton(paths) -> list[Finding]`; `freeze_write/freeze_check`; `check_scope(role, changes, frozen) -> list[Finding]`; `uncovered(diff, coverage, report) -> Uncovered`; `baseline_moved(base, path) -> BaselineState`; `record(root, slug, step, payload) -> None`.
- **Verify**: todos os testes dos Steps 3 e 4 passam; `build_checks.py red-check` sobre cada fixture devolve a regra esperada (tabela no progress); `record` sobre um `gate.json` com chave desconhecida e com o esquema `{fast, full, ts}` do 000007 mantém ambos (teste); `uncovered` sobre a fixture confere o número a mão; `ruff check` e `pyright` limpos; zero termos de C1.
- **Tests**: when `red-check` recebe `red-ok`, returns `ok = true` e `red.reason_ok = true`; when recebe cobertura que não exerce nenhuma linha de corpo de função dos arquivos do step, returns R7; when `skeleton` encontra um `if` no corpo, returns TFB-004; when `freeze --check` encontra o hash diferente, returns violação e exit 1; when `scope --role cleaner` vê um `test_*.py` no diff, returns TFB-008; when `scope --role hardener` vê uma linha de código que não é pragma, returns TFB-008; when `record` roda duas vezes com o mesmo payload, returns o mesmo arquivo (idempotente); when `status` lê um step com `red` ok e sem `green`, returns a fase `GREEN`.
- **Docs**: `--help` de cada subcomando; tabela subcomando → regra na norma.
- [ ] Done

### Step 6: Criar os papéis com contexto curto (agentes e montador de briefing)
Criar `.claude/agents/scenario-tester.md`, `cleaner.md` e `hardener.md` (frontmatter do mecanismo existente de agentes do open-seja; ferramentas mínimas por papel: o Cleaner e o Hardener não recebem busca na web nem acesso ao plano) e `build_brief.py`: `build_brief.py --role <tester|coder|cleaner|hardener> --plan <plano.md> --step N --feature <slug> [--tool-output <json>]` escreve um briefing em Markdown em `_output/tmp/` e imprime o caminho, com **manifesto** do que entrou (arquivos, trechos, tamanho em caracteres) e um **teto** por papel (default 24 000 caracteres, `PIPELINE_BRIEF_MAX`; acima do teto, corta a lista de contexto opcional, nunca a regra de escopo, e avisa). Conteúdo por papel conforme TFB-012; o briefing do Tester inclui o índice de step definitions já existentes (para reuso, evitando as duplicatas que GHK-015 acusa) e as regras de esqueleto e de asserção; o do Coder, a mensagem de falha do `red-check` e a lista de arquivos congelados; o do Cleaner, só os achados de CRAP (formato "CRAP(arquivo::função)=26.4 (CC=26, cov=0.92) > 8: dividir") e o corpo das funções; o do Hardener, os mutantes sobreviventes e o texto da regra do pragma. O prompt de cada agente fecha com: o resultado é o que a ferramenta devolver, não o que o agente escrever; qualquer arquivo fora do escopo é violação. Texto dos agentes e mensagens ao citizen em voz controlada.
- **Files**: open-seja/.claude/agents/scenario-tester.md (create), open-seja/.claude/agents/cleaner.md (create), open-seja/.claude/agents/hardener.md (create), open-seja/.claude/skills/scripts/build_brief.py (create), open-seja/.claude/skills/scripts/tests/test_build_brief.py (modify)
- **References**: product-design/standards.md § Backend 4, 19; `.claude/references/general/implement-test-first.md`
- **Depends on**: Step 5
- **Interface**: `build_brief(role, plan, step, feature, tool_output=None, *, max_chars) -> Brief{path, manifest, truncated}`.
- **Verify**: `test_build_brief.py` passa; o briefing do Cleaner de uma fixture **não contém** o texto do cenário nem outros steps (`grep` do nome de outro step devolve zero); o do Tester não contém corpo de função de código novo; o manifesto lista tamanhos; um plano grande é cortado no teto e `truncated = true`; os três agentes são aceitos pelo check de estrutura do harness (`check_skill_system.py`/`run_all_checks.py` igual ao baseline); zero termos de C1.
- **Tests**: when o papel é `cleaner`, returns um briefing sem `Scenarios`, sem outros steps e com o limite de CRAP; when o papel é `coder`, returns a mensagem da falha do `red-check` e a lista de arquivos congelados; when o conteúdo passa do teto, returns `truncated = true` e a regra de escopo continua presente; when o papel é desconhecido, returns erro de uso (exit 2).
- **Docs**: cabeçalho de cada agente (uma frase: "um trabalho, depois destruído").
- [ ] Done

### Step 7: Escrever o ramo v2, `--pipeline`, o loop e a escalada no `/implement`
Ordem obrigatória de edição de `implement/SKILL.md` (conferida no Step 1): ponteiro do 000007 → parada do 000012 → **este passo**. (1) Argumento `--pipeline` (Cleaner e Hardener; Decisões pendentes 1 e 7). (2) No início do run: ler `plan_format_version`; v1 ou ausente = caminho antigo **sem nenhuma mudança** (golden do Step 3); v2 com `Specify: approved` = executar TFB-002 (se a linha de parada do 000012 não existir, escrevê-la aqui). (3) Por step: classificar (TFB-003); step dono segue RED → GREEN [→ CLEAN → HARD] → REC conforme o fluxo da norma, com **um subagente novo por invocação**, briefing de `build_brief.py` e transição por código de saída de `build_checks.py` e do gate; step sem cenário segue o contrato do 000068 sem alteração. (4) Loop e teto (Decisão pendente 3), atualização do progress file a cada transição (fase, tentativa, ponteiro do último JSON) e retomada (TFB-020). (5) Escalada: status `ESCALATED`, parada do run e `AskUserQuestion` (C4) com: *Ajustar o cenário e refazer a specify* (Recommended when o teste não consegue passar por causa do cenário; NOT recommended when o erro é de código), *Eu assumo este step* (`/implement --manual`; Recommended when o humano quer escrever o código), *Aceitar como PARTIAL e seguir* (Recommended when o step não bloqueia os seguintes; NOT recommended when há `Depends on`), *Subir o teto uma vez* (Recommended when o último JSON mostra progresso). Mensagem de escalada em primeira pessoa, frases curtas, com a regra e a dica da ferramenta. Nunca oferecer mover o baseline (só o humano, fora do `/implement`). (6) Fim do plano: `full` (Decisão pendente 4), `build.feature{}` (TFB-019), resumo. (7) Nota de reflexão: acrescentar, no ponto de extensão que o Step 1 achou, os campos `pipeline` e `red_reason_ok` (sem mudar `--gate-json` e `--gate-attempts`). (8) Toda a prosa extensa vai para a norma; o `SKILL.md` ganha só o necessário e um ponteiro, respeitando o limite de `skill-body-length` medido no Step 1. Não alterar o Quality Gate existente, hooks, `settings` nem a fase de revisão.
- **Files**: open-seja/.claude/skills/implement/SKILL.md (modify), open-seja/.claude/skills/scripts/step_notes.py (modify, mínimo), open-seja/.claude/references/general/extended-cycle-contract.md (modify, só ponteiro, se existir), open-seja/.claude/references/general/implement-test-first.md (modify, texto da escalada)
- **References**: product-design/constitution.md, `.claude/references/general/implement-test-first.md`
- **Depends on**: Step 6
- **Interface**: texto do `/implement` com `--pipeline`, ramo por `plan_format_version`, loop e escalada.
- **Verify**: `git diff --stat` mostra só os arquivos listados; `grep -n "pipeline" .claude/skills/implement/SKILL.md` acha a flag, o ramo v2 e o ponteiro à norma; `grep -c "plan_format_version"` mostra o ramo antes de qualquer uso de `Scenarios:`; nenhum arquivo de gate, hook ou `settings` no diff; o dry-run do `/implement` sobre os dois planos v1 produz a **mesma sequência de ações** do golden (resultado igual à tag v0.10.1); `python .claude/skills/scripts/check_skill_system.py` e `run_all_checks.py` com resultado igual ao baseline; o limite de `skill-body-length` não foi excedido.
- **Tests**: when um plano v1 é lido em dry-run, returns a sequência de ações do golden (nenhum `red-check`, nenhum papel novo); when `--pipeline` é passado com plano v1 (default da Decisão pendente 7), returns a recusa em uma frase e nenhuma ação; when o plano v2 tem `check_plan_scenarios.py` ≠ 0, returns parada antes do primeiro step; when `check_specify.py --status` devolve `stale`, returns parada com a frase "os cenários estão desatualizados: refaça a specify"; when um step tem `Scenarios: N/A (...)`, returns o caminho antigo com `mode: no-scenario`. O dry-run é uma checagem de texto e de golden (o `SKILL.md` é instrução, não código); o comportamento real é provado no Step 8.
- **Docs**: SKILL-quickguide do `/implement` fica para o item 9.
- [ ] Done

### Step 8: Ensaiar o ciclo ponta a ponta em um projeto descartável e medir
Criar um projeto Python descartável (um pacote pequeno, pytest-bdd, gate instalado como no ensaio do 000068), com uma feature fictícia aprovada (3 REQs, 5 cenários, um Outline, um cenário de infraestrutura sem teste) e um plano v2 que passa em `check_plan_scenarios.py`. Executar o fluxo do Step 7 com **papéis roteirizados** (o que um subagente faria, escrito à mão ou por script, como o ensaio do 000068; declarar no progress o que foi simulado e o que rodou de verdade). Casos: (a) caminho feliz com `--pipeline`: vermelho certo, verde, Cleaner dispara em uma função com CRAP acima de 8 e a refatora, Hardener mata um sobrevivente; (b) vermelho pelo motivo errado (import) é recusado com R1 e o Tester corrige; (c) Coder edita um `.feature` e o `scope`/`freeze` o barra; (d) Coder deixa um cenário `skipped`, e o step não passa; (e) teto atingido (cenário impossível): `ESCALATED`, progress gravado, retomada depois; (f) `quality-baseline.json` movido à mão pelo humano: `PASS_WITH_BASELINE` e `baseline_moved = true`; (g) cenário já verde antes do código: escalada (Decisão pendente 6); (h) `stale` a meio: parada; (i) `Stop` hook com a árvore vermelha na pausa da escalada (documentar até 3 barras e a liberação, lacuna 9); (j) plano v1: sequência igual ao golden. Medir e registrar: invocações por step, tempo por fase, tentativas até PASS, **findings por step** do Cleaner e do Hardener (research-000050 rec 20: justificam os passes separados?), tamanho de cada briefing, e a fração de steps em que Cleaner e Hardener foram pulados. Esses números alimentam a Decisão pendente 1 e o item 10. Conferir o `gate.json` resultante contra a tabela "Costura com o 000008".
- **Files**: `_output/plans/plan-000013-progress.md` (create no Doutourado), projeto descartável fora do repositório (create/delete)
- **References**: research-000050 §2, §3, §10.3; `_output/plans/plan-000068-progress.md` (ensaio de referência)
- **Depends on**: Step 7
- **Interface**: N/A
- **Verify**: o progress registra, por caso (a) a (j), a saída das ferramentas e o resultado esperado/obtido; o `gate.json` do caso (a) tem `fast`, `full`, `ts` e `build` com `scenarios{}` (cada chave igual à do lock) e `steps{}`; no caso (f) `baseline_moved = true`; no (d) o step não é `PASS`; o progress lista o que foi simulado; a tabela de medidas existe com números brutos e `n`; nada foi escrito no repositório do Doutourado além dos arquivos de `_output/plans/`.
- **Tests**: N/A (ensaio; os testes automáticos são dos Steps 3 a 6)
- [ ] Done

### Step 9: Fechar: costura com os vizinhos, consistência, C1 e pendências
Em `implement-test-first.md`, acrescentar a seção "Quem alimenta e quem consome" e a tabela "Costura com o 000008" (abaixo). Reexecutar `pytest` dos três arquivos, `ruff`, `pyright`, `run_all_checks.py` e `/critique validate` nos arquivos novos; conferir vocabulário contra 000007 a 000012 (nomes de degrau, chaves, estados, `rev`, `stale`) e C1 (`git grep -i` dos termos do Step 1 sobre o diff). Registrar no progress: o resultado dos checks, as lacunas (seção "Lacunas e conflitos"), as decisões pendentes que ficaram no default, e os textos sugeridos ao designer via `/implement --manual`: (i) uma frase no contrato do 000007 dizendo que o registro do build mora em `gate.json.build` (ou em `build-record.json`); (ii) uma frase no `drift-metric.md` do 000008 definindo `baseline_moved` e a fonte de `red_reason_ok`; (iii) o aviso de que o ciclo sem `full` deixa o D3a `não medido`.
- **Files**: open-seja/.claude/references/general/implement-test-first.md (modify), `_output/plans/plan-000013-progress.md` (modify no Doutourado)
- **References**: product-design/constitution.md
- **Depends on**: Step 8
- **Interface**: N/A
- **Verify**: a tabela de costura cobre itens 8, 9, 10 e o plano 000008, cada linha citando uma regra `TFB-NNN`; suíte, `ruff`, `pyright` verdes; `run_all_checks.py` retorna o mesmo conjunto de falhas pré-existentes do Step 1; `git diff --stat` dos arquivos de ponteiro mostra no máximo uma linha adicionada cada; nenhum arquivo de gate, hook ou `settings` no diff total; zero termos de C1; o progress lista as 7 decisões pendentes com o default em uso.
- **Tests**: N/A (verificação final; a suíte dos Steps 3 a 6 é o teste)
- [ ] Done

## Costura com o 000008 (colunas derivadas e fontes)

| Coluna / dado do 000008 | Quem escreve | Onde | Regra |
|---|---|---|---|
| `test_result` (D2 e D3a) | plugin `scenario_report` na última rodada verde e no `full` | `build.scenarios[chave].final.test_result` (`passed`, `failed`, `skipped`, `xfailed`, `error`, `missing`) e `scenarios-<ts>.json` | TFB-009, TFB-016 |
| chave cenário → teste, `req` | plugin | relatório JSON e propriedades JUnit | TFB-016 |
| `skip`/`xfail` = descoberto (D2) | plugin registra o estado; o step não passa com ele | idem | TFB-009 |
| `red_reason_ok` (evidência exigida no D3a) | `build_checks.py red-check` | `build.scenarios[chave].red.reason_ok` (`true`, `false`, `null` = sem registro → `não medido` na evidência) | TFB-005, TFB-006 |
| gate `full` PASS (D3a) | `/implement` no fim do plano | `gate.json.full` | TFB-019, Decisão pendente 4 |
| "sem `--accept-baseline`" (D3a) | `build_checks.py baseline` | `build.steps[N].baseline_moved` e `build.feature.baseline_moved` | TFB-017 |
| `touched_uncovered` (D3b) | `build_checks.py uncovered` | `build.steps[N].touched_uncovered` (provisório) e `build.feature.touched_uncovered` (final) | TFB-018, TFB-019 |
| linhas **e** ramos | idem | `kind: line|branch` | TFB-018 |

Estado "descoberto por baseline": `status = PASS_WITH_BASELINE` (leitura do 000008: "PASS só com baseline aceito").

## Coverage (advisory)

`product-design/product-design-as-intended.md` do Doutourado não tem marcadores REQ; `critique_plan_coverage.py` não se aplica e `Traces:` fica ausente. O plano executa no open-seja.

## Lacunas e conflitos com os planos 000007 a 000012

1. **Onde grava (000007, Step 4/5).** O 000007 fixa `gate.json` como `{fast, full, ts}` + ponteiros e diz que "o resultado entra em `gate.json`". Este plano acrescenta a chave `build`. Aditivo; se o esquema foi declarado fechado, Decisão pendente 2 opção B.
2. **"Sem `--accept-baseline`" (000008, D3a).** O JSON do gate não traz indicador de baseline aceito. Este plano o **deriva** do diff de `quality-baseline.json` (TFB-017). O `drift-metric.md` do 000008 precisa citar essa fonte (texto sugerido no Step 9).
3. **`fast` vs `full` (000008, D3a).** D3a pede `full` PASS; o `/implement` por step só roda `--fast` (000068). Sem a rodada final (Decisão pendente 4) o D3a fica `não medido` mesmo com testes verdes. O 000008 não diz o que ocorre quando só `fast` rodou; este plano grava `full: null` e o item 8 deve ler como `não medido`.
4. **D3b por step vs por feature (000008).** O 000008 mede por feature. Linha tocada num step pode ser coberta por cenário de outro step. O valor por step é **provisório**; o final é o de `build.feature` calculado no fim do plano sobre a união do diff.
5. **`conftest` modelo vs plugin (000010, Step 8).** O 000010 entrega um `conftest` modelo e a propriedade `req`; este plano o promove a plugin com instalador idempotente. Evitar divergência: o exemplo passa a importar o plugin; teste de igualdade da chave contra `check_features.py` e contra o lock. A propriedade JUnit `req` repetida e o JSON `req` (lista) coexistem; o item 8 deve ler o JSON.
6. **Ordem dos `SKILL.md` e linha de parada (000012, Decisão pendente 4).** Conferida no Step 1. Se o 000012 escolheu B (sem a linha), o Step 7 a escreve; se A, herda.
7. **Dono único (000012, Decisão pendente 2).** Com B (vários donos), o ponto verde do cenário é ambíguo; este plano supõe A e escala se o plano v2 tiver cenário com dois donos.
8. **`--pipeline` do roadmap-000062 listava `architect`.** O roadmap-000006 (item 7) só lista Coder, Cleaner e Hardener. Violações do `lint-imports` voltam ao Coder pelo `--fast`. `architect` fica fora; registrar no backlog do 000062.
9. **Hooks e árvore vermelha.** O `PreToolUse` em commit recusa o estado vermelho (por isso o vermelho não é commitado) e o `Stop` hook roda `--fast` e barra até 3 vezes a pausa do agente com a árvore vermelha (escalada durante RED/GREEN). Hooks não são editados aqui; o efeito é documentado e medido no caso (i) do Step 8. Candidato a follow-up no 000068: um marcador de "vermelho em curso".
10. **Mutação por step cresce com o diff.** `diff_base` do gate é `main`: "função tocada" é cumulativa na branch, não só do step. Custo da mutação cresce ao longo do plano. Medido no Step 8; follow-up se passar de poucos minutos por step.
11. **Cleaner/Hardener sem medição prévia (000007, Decisão pendente 5; research-000050 rec 20).** O 000007 adiou os dois papéis "depois de medir findings por step". Este plano entrega os papéis atrás de `--pipeline` (Decisão pendente 1) e mede no ensaio; a medição real é a do piloto (item 10).
12. **Vermelho é verificado por forma, não por sentido.** Um `Then` com `assert result == "x"` sempre falso passa o `red-check`. R4/R7 barram os casos vazios; a adequação semântica é a auditoria humana por amostra do 000008 (Decisão pendente 1 dele).
13. **Outline = um cenário.** Uma linha de `Examples` que falha não é distinguível no plano; fica em `rows`. Custo da decisão fechada.
14. **Só Python/pytest-bdd.** C++ e JS/TS (research-000050 §5, §7) ficam fora; o plugin e `build_checks.py` assumem pytest.
15. **Instalação do plugin fora do `/seja-setup`.** O plugin é copiado por `install-plugin` no primeiro vermelho, para não editar o instalador do 000065/000068. O item 9 decide se o `/seja-setup` passa a oferecê-lo.
16. **`skill-body-length`.** O `implement/SKILL.md` pode estar perto do limite; por isso o texto vai para a norma e o `SKILL.md` leva ponteiro (Step 1 mede, Step 7 respeita).

## Metacomm Intention
- **Summary**: I tell you that, before I write any code, I write one test for each scenario you approved and I show you it fails because the behavior is missing; that I stop and ask you after three tries instead of saying it is done; and that I never move the quality baseline myself.
- **Source**: agent (technical plan; metacomm text kept for the report to the designer)

Metacomm contradiction check: nenhuma intenção existente em `product-design-as-intended.md` (D-001 a D-005) conflita; D-004 e D-005 (presets) ficam fora de escopo.

## Review log

**Review depth:** Standard (9 steps, ~20 arquivos distintos no total, no máximo 5 por step). Phase 1 inline (sem subagente; mesmo critério dos planos 000007 a 000012); sem Phase 2 (nenhum Deferred com risco de regressão não resolvido). Prefixo FEATURE-O sem linha na tabela de atalhos: usei TEST, DX, COMPAT, ARCH, SEC, PERF, UX, DATA.

### Phase 1 -- Perspective scan

| Perspective | Status | Concern |
|---|---|---|
| TEST | Adopted | Fixtures e testes primeiro (Step 3, vermelho por asserção); critério de "vermelho pelo motivo certo" é mecânico (R1 a R8); a limitação semântica é declarada (lacuna 12). Steps documentais com `Tests: N/A` justificado. |
| DX | Adopted | Contexto curto por papel com manifesto e teto; mensagens em voz controlada; escalada com opções C4; retomada pelo progress file. |
| COMPAT | Adopted | v1 intocado e provado por golden (Steps 3 e 7, caso j); gate, hooks e `settings` fora do diff (Verify dos Steps 7 e 9); `gate.json` só aditivo (Decisão pendente 2); `--pipeline` recusado em v1. |
| ARCH | Adopted | Funções puras mais CLI (standards § Backend 4, 19); plugin separado do verificador; norma separada do `SKILL.md`; sem papel `architect` (lacuna 8). |
| SEC | Adopted | C1 verificado por `git grep` nos Steps 2, 3, 5, 6, 9; escopo por papel impede edição de baseline, gate e hooks; gate roda sem rede e sem `ANTHROPIC_API_KEY` (herdado do 000065); fixtures fictícias. |
| PERF | Adopted | Mutação só em função tocada e só quando há sobrevivente; passes pulados quando nada a fazer; custo cumulativo da mutação medido (lacuna 10). |
| UX | Adopted | A escalada e o resumo de step falam com o citizen em primeira pessoa e frases curtas; nunca oferecem mover o baseline. |
| DATA | Adopted | `null`/`não medido` explícitos; escrita atômica e idempotente do `gate.json`; chaves desconhecidas preservadas; `schema_version`. |
| API, DB, I18N, A11Y, VIS, RESP, OPS, MICRO | N/A | Sem superfície. |

### Riscos e lacunas registrados
- Caminhos, flags do gate e hooks do `pytest-bdd` do open-seja não verificados (submodule vazio): o Step 1 é o portão e pára o plano se o 000012 não executou.
- O ensaio do Step 8 simula os papéis de LLM; a prova de que subagentes reais seguem o briefing curto só vem do piloto (item 10).
- Fricção do citizen (risco do roadmap): vermelho obrigatório e escalada aumentam passos; o Step 8 e o piloto medem invocações e tempo.
- Heurísticas R4/R7 podem errar para os dois lados; por isso a falha vem com regra e dica, e a escalada é humana.

### Execution Metrics
| Metric | Value |
|---|---|
| Review depth | Standard |
| Phase 1 perspectives | 8 adopted, 8 N/A |
| Phase 2 deep-dives | 0 |
| Iterations | 0 |
| Pending decisions | 7 (defaults em "Decisões pendentes") |

## Outcomes

- Norma `implement-test-first.md` (`TFB-001..022`) com fluxo por step, critério mecânico de vermelho pelo motivo certo, escopo e contexto por papel, limiares do Cleaner, critério do Hardener, loop com teto e escalada.
- Plugin `scenario_report` (relatório do runner com chave de cenário e `req`) e `build_checks.py` (`red-check`, `freeze`, `scope`, `uncovered`, `baseline`, `record`), com fixtures e testes escritos antes.
- Três agentes novos (`scenario-tester`, `cleaner`, `hardener`) e `build_brief.py` com teto de tamanho; Coder é o subagente de step existente.
- `/implement` com `--pipeline` e ramo v2; plano v1 sem mudança, provado por golden.
- `gate.json` com `fast`, `full`, `ts` e `build` (colunas derivadas pedidas pelo 000008: `test_result`, `red_reason_ok`, `touched_uncovered`, `baseline_moved`).
- Medidas do ensaio (invocações, tempo, findings por step) para decidir a Decisão pendente 1 e alimentar o item 10.

smoke: false
