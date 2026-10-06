# Progress -- Plan 000007

Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

## Codebase Patterns
<!-- Subagents consolidate reusable patterns here -->

- Repositorio de execucao e este (open-seja, branch `dev`); nao ha submodule `open-seja/` a inicializar. Todo caminho `open-seja/X` do plano = `X` na raiz deste repo.
- O as-intended e `product-design/product-design-as-intended.md` (classificacao Human (markers)). `product-design/seja-as-intended.md` NAO existe: foi fundido no §3 (Q-006, 2026-10-05). Toda referencia do plano a `seja-as-intended.md` le-se como `product-design-as-intended.md`.
- Use `python3` (nao ha `python` no PATH). pytest nao esta instalado no sistema: `uvx --with pyyaml pytest .claude/skills/scripts/tests/ -q`.
- Arquivos do harness: UTF-8, sem travessao tipografico nem aspas curvas (`--` e aspas retas) -- standards.md § Backend > 17.
- Nenhum nome de parceiro, instituicao conveniada ou pessoa em `_output/`, `product-design/` ou `.claude/` (constituicao C2). A lista de termos de C1 fica com o orquestrador e NAO e escrita no ledger; o orquestrador roda o `git grep` sobre o diff.

## Iteration Log

### Step 1 -- conferencia do terreno (2026-10-06 15:20 UTC, orquestrador, inline)

Executado no contexto do orquestrador (os dados ja tinham sido levantados na sessao de status do roadmap). Nada escrito fora do ledger.

**Identificadores**
- Ultimo D-NNN usado: **D-004** (contrato Gherkin; era a D-006 do Doutourado). D-003 = preset `apprentice`. Proximos livres: **D-005, D-006, D-007, D-008** para D-A..D-D do Step 6.
- H-009: **ja registrada** pelo `/design` de 2026-10-05 no §3, subsecao 2.9 ("A escada de representacoes (proposta)"), com o alcance declarado (D-004) e a refutacao pelos tres medidores de ganho do citizen. O Step 6 nao cria H-009: no maximo acrescenta (com prosa do designer) a medida por degrau com estados coberto/descoberto/nao medido, o tempo ate a primeira feature aprovada e a refutacao por comparacao com o ciclo de controle. Proximo H livre: H-010.
- Numeracao do Doutourado citada nos planos 000009..000015 ("D-004 apprentice", "D-005 literature-reviewer", "D-006 contrato") NAO vale aqui. Mapa: D-004(Dout.)->D-003; D-005(Dout.) nao existe aqui (fora do escopo); D-006(Dout.)->D-004.

**Caminhos de "Files"**
| Caminho do plano | Estado |
|---|---|
| `.claude/references/general/extended-cycle-contract.md` | nao existe (create no Step 2) |
| `.claude/references/template/plan-step.md` | existe (43 linhas; ja tem `Traces:`) |
| `.claude/references/template/feature-layout.md` | nao existe (create no Step 4) |
| `.claude/skills/_internal/plan/standard/SKILL.md` | existe |
| `.claude/skills/implement/SKILL.md` | existe (auto mode faz version check: `plan_format_version` != 1 -> cai para manual; ver Step 3) |
| `product-design/seja-as-intended.md` | **corrigido** -> `product-design/product-design-as-intended.md` |
| fixtures de plano v1/v2 | caminho definido: `.claude/skills/scripts/tests/fixtures/plan_format/` |

**Validador de formato de plano**: nenhum script `.py` le `plan_format_version`. Logo o Step 3 NAO cria validador (fica para o plan-000012) e seu `Tests:` e `N/A (sem validador; fixtures documentadas)`. Unico leitor e o texto do `implement/SKILL.md` (Auto Mode Phase 0 step 3).

**Pre-requisitos consumidos** (roadmap-000062 no ledger do pesquisador): `.claude/references/template/quality-gate/python/gate.py`, `.claude/hooks/quality_gate_pretool.py`, `.claude/hooks/quality_gate_stop.py`, `.claude/skills/scripts/check_quality_gate.py` existem. No proprio open-seja `GATE_FAST_CMD` esta vazio em `conventions.md`: o portao NAO esta instalado aqui -> notas com `--gate not-installed` (T1: declaracao explicita).

**Baseline (Q1) em 2026-10-06, HEAD 6c3e41f, antes de qualquer escrita do plano**
- `python3 .claude/skills/scripts/run_all_checks.py`: 15 PASS, 14 FAIL. FAIL: check_docs, check_plan_coverage, check_api_auth_decorators, check_backend_test_coverage, check_conventions (17 undefined vars), check_frontend_test_coverage, check_i18n_keys (2 errors), check_migration_chain, check_po_parity, check_skill_system (9 errors), check_validation_constants_sync, check_version_changelog_sync (VERSION 0.7.1 vs CHANGELOG 0.9.1), check_vuln_patterns, check_worktree_health (1 orphan).
- pytest `.claude/skills/scripts/tests/`: 2 erros de coleta (test_generate_spo.py, test_generate_spo_design_system.py: falta `scripts/priv/generate_spo.py`); ignorando esses dois: **626 passed, 12 failed** (inclui 3 de test_summarize_artifacts).
- Criterio de "sem falha nova": o conjunto de FAIL acima nao cresce, e os contadores de erro de check_skill_system (9) e check_conventions (17) nao sobem.

**Decisoes pendentes do plano**: o designer aceitou os defaults em 2026-10-06 ("pode seguir com os defaults"): 1=B (fases internas, `--grill`/`--specify` reservadas), 2=A (specify pulada por tipo de tarefa), 3=A (`features/<slug>/`), 4=C (composta por degrau), 5=A (teste-primeiro no `/implement`), 6=B (`plan_format_version: 2`, v1 valido para sempre). Marcar no contrato como `[default; aceito 2026-10-06]` em vez de `[default; pendente]`.

**Emendas do adendo do roadmap a absorver** (research-000087, ledger do pesquisador): regra do perimetro (a feature e a unidade de medida; fora dela `legado: nao medido`); fronteira agnostica de stack nomeada (gate contract: JSON + codigos de saida + `GATE_*_CMD`; runner contract: Cucumber JSON + chave de cenario; stack sem adaptador degrada para `nao medido`, constituicao T6); tabela degrau x receptor (o citizen aprova a mensagem -- retraducao em primeira pessoa e exemplos narrados --; o power dev aprova o `.feature` como contrato; D-004); teste da surpresa como criterio de aceitacao de emendas (todo signo devolvido ao citizen deve poder provocar uma ruptura decodificavel; item que so confirma -- PASS, percentuais -- nao entra no registro do citizen); D-004 deste repo como fonte.

**Dependencias do auto mode**: o plano e v1; Steps 2-5 e 7 podem ir a subagentes. Step 6 escreve em arquivo Human (markers) e exige confirmacao do designer no mesmo turno: fica com o orquestrador.

### Step 1 -- reflection-on-action | 2026-10-06 15:18 UTC | Conferir o terreno no open-seja e fixar os identificadores
- happened: O terreno foi conferido no proprio contexto do orquestrador: ultimo D-NNN e D-004, H-009 ja existe no §2.9, seja-as-intended.md foi fundido no product-design-as-intended.md, nenhum validador le plan_format_version, o portao nao esta instalado no open-seja e o baseline tem 14 checks e 12 testes falhando.
- deviated: O step rodou inline e nao em subagente, porque os dados ja estavam levantados. O Step 6 perdeu metade do escopo: H-009 ja tinha sido registrada pelo /design.
- less-sure: Se a refutacao por comparacao com o controle, rascunhada no plano, ainda cabe no §2.9 depois do ajuste do /design; e se o baseline de testes e estavel ou varia por ambiente.
- gate: not-installed

### Step 2 -- reflection-on-action | 2026-10-06 15:20 UTC | Escrever o contrato normativo do ciclo estendido
- happened: Criei extended-cycle-contract.md com 19 regras CYC-001..019, cada uma com Quem decide e Criterio de aceitacao, a tabela das decisoes pendentes 1 a 6 no default aceito e as secoes Compatibilidade e IMPLEMENT como cabecalhos vazios. run_all_checks ficou em 15 PASS e 14 FAIL, igual ao baseline.
- deviated: Acrescentei regras alem do minimo (perimetro, fronteira de stack, degrau x receptor, teste da surpresa, decisoes 3 a 6 como regras proprias) e cobri tambem a decisao 6, que o texto do passo nao listava (1 a 5).
- less-sure: Se o teto de 5 rodadas x 4 perguntas da grill e 3 ajustes da specify, citados do §10 como intended, devem ficar no contrato; e se o criterio de CYC-008 (recusa) e verificavel antes de existir validador.
- gate: not-installed

### Step 2 -- contrato normativo (2026-10-06, subagente)

Arquivo criado: `.claude/references/general/extended-cycle-contract.md` (frontmatter `designer_description`, como shared-definitions.md). 19 regras `CYC-001..019`, todas com "Quem decide" e "Critério de aceitação". Run_all_checks: 15 PASS / 14 FAIL (iguais ao baseline); check_skill_system=9, check_conventions=17.

Mapa de regras:
- CYC-001 ciclo; 002 grill; 003 specify; 004 pular specify (dec. 2); 005 escrita do plano; 006 flags avulsas reservadas (dec. 1); 007 tabela le/escreve/aprova; 008 ordem e portoes; 009 tres degraus + D0; 010 estados coberto/descoberto/nao medido; 011 perimetro; 012 fronteira agnostica (gate contract, runner contract, T6); 013 degrau x receptor; 014 teste da surpresa; 015 layout features/<slug>/ (dec. 3); 016 divergencia composta (dec. 4); 017 teste-primeiro no /implement (dec. 5); 018 versao do formato v2 (dec. 6); 019 o que o contrato nao faz.
- Secoes `## Compatibilidade` (Step 3: campo `Scenarios:`, v1 valido para sempre, v2 invalido) e `## IMPLEMENT` (Step 5: vermelho pelo motivo certo, gate, gate.json, `--pipeline` reservado, runner pendente) estao no fim do arquivo, com a linha "preenchida pelos Steps 3 e 5". Novas regras desses steps devem continuar a numeracao a partir de CYC-020.
- CYC-002 cita o esquema de intent.md (REQ-<slug>-NNN, "Nas suas palavras", "Fora do escopo", "Premissas"); o Step 4 deve manter coerencia com CYC-015.
- Referencias a planos 000008 (formula), 000010 (validador Gherkin), 000013 (Cleaner/Hardener) no CYC-019 seguem a numeracao deste ledger.

### Step 3 -- formato de plano v2 (2026-10-06, subagente)

- `plan-step.md` ganhou o campo `Scenarios:` e a secao "Format version"; `## Compatibilidade` do contrato preenchida (regra v1/v2, comportamento do /implement, fato do Auto Mode caindo para manual com version != 1, recusa executavel e do plan-000012). `implement/SKILL.md` nao foi tocado.
- Fixtures em `.claude/skills/scripts/tests/fixtures/plan_format/`: v1 = plan-000001 e plan-000004 (NAO o 000005: ele cita literalmente a lista de termos do grep de C1 no corpo); v2 valida, v2 invalida, README.
- Para Step 5: a secao `## IMPLEMENT` do contrato continua vazia. Para plan-000012/13: o version check do implement/SKILL.md (Auto Mode Phase 0 passo 3) precisa aceitar `2`.
- Cuidado: rodar `check_skill_system.py` ou `check_conventions.py` isolado, sem `</dev/null` e timeout, pode travar; use `run_all_checks.py`.
- Run_all_checks igual ao baseline (15 PASS / 14 FAIL); pytest 626 passed / 12 failed.

### Step 3 -- reflection-on-action | 2026-10-06 15:24 UTC | Definir o formato de plano com steps ligados a cenarios e a retrocompatibilidade
- happened: Acrescentei o campo Scenarios e a regra de versao ao plan-step.md, preenchi a secao Compatibilidade do contrato e criei 4 fixtures (2 planos v1 reais, 1 v2 valida, 1 v2 invalida) com README. run_all_checks e pytest ficaram iguais ao baseline.
- deviated: Usei o plano 000004 no lugar do 000005 como fixture v1, porque o 000005 traz no corpo a lista de termos do grep de C1.
- less-sure: Se a recusa do v2 invalido, so descrita, sera verificavel ate o plan-000012 criar o validador; e se o Auto Mode em manual para v2 vira surpresa antes do plan-000013.
- gate: not-installed

### Step 4 -- reflection-on-action | 2026-10-06 15:27 UTC | Definir o layout por feature
- happened: Criado template/feature-layout.md: estrutura features/<slug>/, esquema de intent.md (frontmatter slug/status, secoes, tabela de REQ), convencao de tags @REQ- nos .feature, esquema de gate.json, esquema da tabela de rastreabilidade (estados de CYC-010, perimetro de CYC-011) e exemplo task-list com 2 REQs e 3 cenarios. CYC-015 aponta para o arquivo como esquema normativo.
- deviated: gate.json ganhou schema_version e campos exit_code/category/ref por rodada, alem de {fast, full, ts}; QUALITY_DIR escrito sem ${} para nao subir o check_conventions.
- less-sure: Forma exata de fast/full em gate.json (exit_code/category/ref) pode precisar de ajuste quando o gate real for integrado no Step 5 e no plan-000010.
- gate: not-installed

### Step 4 -- layout por feature (2026-10-06)
- Esquema normativo em `.claude/references/template/feature-layout.md`; CYC-015 aponta para ele.
- Para o Step 5: `gate.json` tem `{schema_version, fast, full, ts}`, com `fast`/`full` = `{exit_code, category, ref}` ou `null` (null = `nao medido`). O IMPLEMENT escreve esse arquivo (CYC-007); `ref` aponta para o JSON do gate em QUALITY_DIR (escrito sem `${}`).
- `run_all_checks.py` demora mais de 120 s no foreground; rode em background gravando em arquivo. Nao use `pkill -f run_all_checks` (mata o proprio shell).

### Step 5 -- reflection-on-action | 2026-10-06 15:33 UTC | Definir o contrato do teste-primeiro no /implement consumindo gate e hooks
- happened: Preenchi a secao IMPLEMENT do contrato com CYC-020..026 (escopo por Scenarios, cenario vira teste, vermelho pelo motivo certo, codigo minimo, portao e gate.json, --pipeline reservado, runner pendente do plan-000010) e acrescentei uma linha de ponteiro em implement/SKILL.md e em plan/standard/SKILL.md. run_all_checks ficou em 15 PASS e 14 FAIL com 17 undefined, 2 e 9 errors.
- deviated: Cada SKILL.md ganhou 2 linhas no diff (a linha de ponteiro mais uma linha em branco antes dela). Uma primeira rodada do run_all_checks concorrente com outra deu 1 timeout e foi descartada; a rodada isolada bateu com o baseline.
- less-sure: Se a regra CYC-022 e verificavel antes de existir runner (plan-000010), e se a ordem Coder, Cleaner, Hardener antes do portao em CYC-025 sera mantida pelo plan-000013.
- gate: not-installed

### Step 5 -- contrato do teste-primeiro (2026-10-06, subagente)
- Regras novas na secao `## IMPLEMENT`: CYC-020 (escopo: so step com `Scenarios:` de tags), 021 (cenario vira teste, chave de cenario), 022 (vermelho = `failed` com asserção; `ERROR`/`ImportError`/`undefined` nao contam), 023 (codigo minimo), 024 (portao `--fast` + 3 tentativas + `gate.json`; portao/hooks/deny nao mudam), 025 (`--pipeline` reservado, plan-000013), 026 (runner pendente do plan-000010; pytest-bdd so recomendacao).
- Para o Step 7: tabela item->CYC: plan-000010 consome CYC-012, 021, 022, 026; plan-000013 consome CYC-020, 023, 024, 025; plan-000012 consome CYC-018 e o version check do Auto Mode.
- Para plan-000010: o runner precisa expor estado `failed` distinto de `ERROR`/`undefined` por chave de cenario (CYC-022).
- Para plan-000013: `--pipeline` entra entre CYC-023 e CYC-024; o Auto Mode do implement/SKILL.md (Phase 1 passo 8) ja tem a cadeia red-green-gate que CYC-020..024 reutilizam sem mudar.
- Cuidado: nao rode dois run_all_checks ao mesmo tempo (um deu timeout em check_skill_system). Rodado isolado: ~1,4 s.

### Step 6 -- reflection-on-action | 2026-10-06 16:39 UTC | Registrar H-009 e as D-NNN no as-intended do open-seja
- happened: D-005 a D-008 foram aplicadas no product-design-as-intended.md via apply_marker.py DECISION_APPEND, cada uma com STATUS proposed acima, depois da confirmacao do designer no turno.
- deviated: H-009 nao foi criada: ja estava no §2.9 pelo /design de 2026-10-05; a refutacao por comparacao com o controle ficou para o designer colar no §2.9, porque e prosa Human. O CHANGELOG nao ganhou linhas: o regex do CHANGELOG_APPEND recusa IDs D-NNN.
- less-sure: Se a ausencia de linhas no CHANGELOG para D-NNN quebra alguma leitura posterior (decision digest, /explain drift).
- gate: not-installed
- human: "sim, aplique o oerquestre"

### Step 7 -- prova de retrocompatibilidade e fechamento (2026-10-06, orquestrador, inline)

- `run_all_checks.py`: 15 PASS / 14 FAIL, os mesmos 14 do baseline; contadores 17 undefined (check_conventions), 2 error(s) (check_i18n_keys), 9 error(s) (check_skill_system). Nenhum FAIL novo.
- pytest (sem os 2 modulos com erro de coleta pre-existente): 626 passed / 12 failed, igual ao baseline.
- Fixtures: `v1-plan-with-tests.md` e `v1-plan-doc-only.md` declaram `plan_format_version: 1` -> o Auto Mode do `/implement` (Phase 0 step 3) os aceita como antes; `v2-valid.md` e `v2-invalid-missing-scenarios.md` declaram 2 -> hoje caem para manual (documentado na secao Compatibilidade do contrato; adaptar e do 000012/000013).
- C1: `git grep` dos termos (lista fora do ledger) sobre `pre-plan-000007..HEAD`: zero linhas acrescentadas (o unico acerto e linha de contexto pre-existente de briefs.md).
- Contrato: 26 regras `CYC-001..026`.
- Decisoes pendentes: as 6 com default aceito pelo designer em 2026-10-06; nenhuma segue pendente.

**Tabela item do roadmap -> regras do contrato que consome**

| Item | Plano | Consome |
|---|---|---|
| 2 drift-metric | plan-000008 | CYC-009, 010, 011, 012, 016 (+ D-007) |
| 3 plan-grill-phase | plan-000009 | CYC-002, 006, 007, 008, 013, 014, 015 |
| 4 gherkin-spec-format | plan-000010 | CYC-003, 012, 015, 021, 022, 026 |
| 5 plan-specify-phase | plan-000011 | CYC-003, 004, 006, 007, 008, 013, 014 (+ D-004) |
| 6 plan-from-scenarios | plan-000012 | CYC-005, 008, 018, secao Compatibilidade (+ D-008) |
| 7 implement-test-first-build | plan-000013 | CYC-017, 020, 021, 022, 023, 024, 025, secao IMPLEMENT |
| 8 reflect-drift-report | plan-000014 | CYC-009, 010, 011, 013, 014, 016 |
| 9 default-cycle-wiring | plan-000015 | todas (quickguide pt-BR; /help; run_all_checks), CYC-019 |
| 10 default-cycle-pilot | plan-000016 | CYC-009..016 (medida), CYC-013 (quem aprova o que) |

**Para os planos seguintes (terreno)**: `seja-as-intended.md` -> `product-design/product-design-as-intended.md` (§3); numeracao D-NNN do Doutourado nao vale (D-004 aqui = contrato Gherkin; D-005..D-008 = este plano; proximo livre D-009); `CHANGELOG_APPEND` recusa IDs D-NNN (lacuna do regex, registrada desde 2026-09-18).

### Step 7 -- reflection-on-action | 2026-10-06 16:40 UTC | Provar a retrocompatibilidade e fechar o contrato
- happened: Checks e testes repetiram o baseline sem falha nova; as fixtures v1 declaram versao 1 e seguem aceitas pelo Auto Mode; a tabela item x CYC foi escrita no progress.
- deviated: Rodou inline no orquestrador; o dry-run do /implement sobre as fixtures foi substituido pela leitura da regra de versao do Auto Mode, porque nao ha validador executavel.
- less-sure: Se o /critique review encontraria inconsistencia entre CYC-018 e a secao Compatibilidade, que foram escritas por executores diferentes.
- gate: not-installed
- drift: not-measured
