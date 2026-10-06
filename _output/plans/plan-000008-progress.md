# Progress -- Plan 000008

Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

## Codebase Patterns
<!-- Subagents consolidate reusable patterns here -->

- Terreno herdado do plan-000007 (ler `_output/plans/plan-000007-progress.md`, secoes "Codebase Patterns", "Step 1" e "Step 7"): repositorio de execucao e este (sem prefixo `open-seja/`); `seja-as-intended.md` -> `product-design/product-design-as-intended.md` (§3); numeracao D-NNN do Doutourado nao vale aqui (D-004 = contrato Gherkin; D-005..D-008 = plan-000007; proximo livre D-009); "D-006 do Doutourado" citada nos planos = D-004 aqui.
- O contrato existe: `.claude/references/general/extended-cycle-contract.md` (CYC-001..026); esquema `features/<slug>/` em `.claude/references/template/feature-layout.md`; formato v2 em `.claude/references/template/plan-step.md`.
- Fixtures do harness ficam em `.claude/skills/scripts/tests/fixtures/<tema>/` (logo `<fixtures>/drift/` = `.claude/skills/scripts/tests/fixtures/drift/`).
- `python3` (nao `python`); pytest via `uvx --with pyyaml pytest ... --ignore=.claude/skills/scripts/tests/test_generate_spo.py --ignore=.claude/skills/scripts/tests/test_generate_spo_design_system.py`.
- Baseline (Q1): `run_all_checks.py` 15 PASS / 14 FAIL com contadores 17 undefined (check_conventions), 2 error(s) (check_i18n_keys), 9 error(s) (check_skill_system); pytest 626 passed / 12 failed. Rodar `run_all_checks.py` com `timeout 200`, saida em arquivo, nunca dois ao mesmo tempo, nunca checks isolados, nunca `pkill -f`.
- Arquivos do harness: UTF-8, sem travessao tipografico nem aspas curvas; nada de nome de pessoa, parceiro, instituicao ou empresa.
- Portao nao instalado no open-seja: notas com `--gate not-installed`.
- Commits: `git -c user.name=arodrigues-puc-rio -c user.email=arodrigues-puc-rio@users.noreply.github.com commit ...`; nunca `--no-verify`.
- Decisoes pendentes do plano: o designer aceitou todas as recomendacoes em 2026-10-06; marcar como `[default; aceito 2026-10-06]`.
- `run_all_checks.py` deve rodar com `< /dev/null` (sem isso `check_skill_system` pode travar 120 s e dar ERROR; com isso leva ~3,5 s).

## Iteration Log

### Step 1 -- conferencia do terreno (2026-10-06, executor, inline)

Nada escrito fora do ledger. `git status` limpo no inicio.

**Fontes da matriz**
| Fonte | Estado | Caminho / nota |
|---|---|---|
| contrato do ciclo | existe | `.claude/references/general/extended-cycle-contract.md`; CYC-009 (degraus D1..D3 e D0), CYC-010 (estados), CYC-011 (perimetro), CYC-012 (gate contract e runner contract), CYC-016 (composta por degrau), CYC-019 (formula e controle sao do 000008), CYC-021/022 (teste por cenario, vermelho = `failed`), CYC-026 (runner pendente do 000010) |
| `intent.md` | definido (esquema) | `.claude/references/template/feature-layout.md`; `status: grilling\|approved`; tabela REQ/Texto/Criterio; conteudo detalhado e do 000009 |
| `*.feature` | definido (esquema) | tag `@REQ-<slug>-NNN` acima de cada `Scenario`; validador e do 000010 |
| relatorio do runner | rascunho | contrato diz Cucumber JSON com chave de cenario (CYC-012); os planos 000010/000014 ja falam de JUnit XML com chave `<slug>/<arquivo>::<nome>`; o `drift-metric.md` fixa so os estados e deixa o formato ao adaptador |
| `gate.json` | definido (esquema) | `schema_version`, `fast`, `full` (null = nao medido), `ts`; NAO traz indicador de baseline aceito (o 000013 o deriva do diff de `quality-baseline.json`) |
| cobertura por cenario | ausente | `gate.py` junta radon e `coverage.json` por funcao (`join_metrics`); cobertura SO dos testes de cenario nao existe; fica `NM-SEM-COBERTURA` ate haver (000013/000014) |
| registro "vermelho pelo motivo certo" | ausente | e do 000013 (campo derivado `red_reason_ok`) |
| diff da feature | ausente | base do diff e do 000014 (`NM-SEM-BASE-DIFF`) |
| H-009 | existe | `product-design-as-intended.md` §3 2.9; refutacao em prosa Human (nao editada aqui) |
| D-NNN | existe | D-004 contrato Gherkin; D-005..D-008 do 000007; proximo livre D-009 |

**Fontes de tempo**: `_output/briefs.md` (linhas STARTED/DONE com minuto UTC), `_output/telemetry.jsonl` (um registro por skill: `timestamp`, `skill`, `duration_seconds`, `plan_id`), `_output/conversation-trace.jsonl` (existe neste repo; `timestamp` com microssegundos, `emitter` user|claude, `session_id` frequentemente "null"), `gate.json`.ts. Nao existe fonte para `t_aprovada`: vira campo manual do registro.

**Termos C1**: lista fica com o orquestrador; nao escrita no ledger. Os arquivos novos evitam nome de pessoa, parceiro, instituicao ou empresa; fixtures fictícias.

**Decisoes pendentes** 1=B, 2=B, 3=A, 4=B `[default; aceito 2026-10-06]`.

**Emendas do adendo do roadmap absorvidas (Steps 2, 4, 7)**: D0 como leitura fora do D com `NM-SEM-INDICE-BRIEF`; subsecao "O que o D nao ve"; tres medidores de ganho do citizen; codigos `NM-SEM-ADAPTADOR-*`. Codigos `NM-*` ja usados pelo plano 000014: `NM-INTENCAO-NAO-APROVADA`, `NM-SPECIFY-PULADA`, `NM-CENARIOS-STALE`, `NM-SEM-RUNNER`, `NM-SEM-GATE`, `NM-SEM-REGISTRO-VERMELHO`, `NM-SEM-COBERTURA`, `NM-SEM-BASE-DIFF`, `NM-SEM-M1`; o `drift-metric.md` e o dono do catalogo e os usa com esses nomes.

### Step 1 -- reflection-on-action | 2026-10-06 17:00 UTC | Conferir o terreno e as fontes de dado
- happened: Li contrato, feature-layout, gate.py e fontes de tempo; listei o estado de cada fonte da matriz no progress.
- deviated: Nenhum arquivo do open-seja foi escrito; caminhos open-seja/X lidos como X.
- less-sure: Formato do relatorio do runner: contrato diz Cucumber JSON e planos 000010/000014 falam de JUnit XML.
- gate: not-installed

### Step 2 -- drift-metric.md (2026-10-06, executor)
- Criado `.claude/references/general/drift-metric.md` com regras `DRM-001..014`. Os 4 degraus tem as 6 linhas (mede, fonte, coberto, descoberto, nao medido, escrito por); formula e denominador zero em DRM-001; colunas derivadas em DRM-006; relatorio em DRM-007; leituras fora do D em DRM-008; catalogo `NM-*` em DRM-009; "O que o D nao ve", D0, auditoria semantica e tres medidores do citizen em DRM-010; anti-gaming DRM-011; M1/M2 DRM-012; casos limite DRM-013.
- Escolhas de interpretacao: (a) populacao do D3a = cenarios com D2 coberto (nao conta duas vezes); (b) sem registro de vermelho, D3a do cenario e `nao medido` (`NM-SEM-REGISTRO-VERMELHO`) com ressalva; o plano 000014 fala de "D3a com ressalva" e "estado NM": lido como as duas coisas; (c) teste `error`/`undefined` e `coberto` em D2 e `descoberto` em D3a.
- `run_all_checks.py` no baseline (15 PASS / 14 FAIL; 17 undefined; 2 e 9 errors). Uma rodada isolada deu `check_skill_system` ERROR por timeout de 120 s (flake; a repeticao deu 3,5 s). Nao rodar duas ao mesmo tempo.

### Step 2 -- reflection-on-action | 2026-10-06 17:04 UTC | Definicao normativa por degrau
- happened: Escrevi drift-metric.md com DRM-001..014: unidade, estados, formula, quatro degraus, colunas derivadas, relatorio, codigos NM, D0, anti-gaming e M1/M2.
- deviated: Acrescentei regras alem das listadas (catalogo NM, casos limite) para dar IDs estaveis; populacao do D3a definida como D2 coberto.
- less-sure: Se ausencia de registro de vermelho e nao medido ou ressalva em D3a; li como os dois.
- gate: not-installed

### Step 3 -- fixtures golden (2026-10-06, executor)
- Criados `.claude/skills/scripts/tests/fixtures/drift/casos.json` (6 casos: entrada + esperado) e `README.md`.
- Recontagem independente (script descartavel que le so a `entrada` e conta estados; resultado = esperado calculado a mao): 0 divergencias.

| Caso | D1 (c/d/nm) | D2 | D3a | D3b | Leituras |
|---|---|---|---|---|---|
| normal | 8/2/0 D=0.2 | 10/2/0 D=0.1667 | 8/2/0 D=0.2 | 43/7/0 D=0.14 | cadeia 6 |
| nada-medido | 8/0/0 D=0 | 8/0/0 D=0 | 0/0/8 n/a | 0/0/30 n/a | -- |
| specify-pulado | nao aplicavel (NM-SPECIFY-PULADA) | | | | |
| orfao-e-sem-tag | 8/0/0 | 8/0/0 | 8/0/0 | 18/2/0 D=0.1 | orfao 1, sem_tag 1 |
| escada-fechada | 8/0/0 | 8/0/0 | 8/0/0 | 20/0/0 | O1=0.4; alerta true |
| amostra-pequena | 4/1/0 D=0.2 | 4/0/0 | 4/0/0 | 9/3/0 D=0.25 | ressalva amostra pequena |

- Decisoes tomadas ao desenhar os casos e refletidas em `drift-metric.md`: D2 so conta cenario com tag para REQ existente; `razao_nm` lista todas as razoes (D3b do caso nada-medido: `NM-SEM-GATE`, `NM-SEM-COBERTURA`); `cadeia_completa` = REQ cujos cenarios estao todos coberto em D2 e D3a; `D` arredondado a 4 casas; forma curta `nao_aplicavel`.
- Esquema da entrada: `intent.status`, `scenarios_status`, `runner`, `gate{full,baseline_moved}`, `reqs`, `scenarios[{id,tags,test_result,red_reason_ok}]`, `touched{total,uncovered}`, `oraculo{n,falham}`, `auditoria`. O 000014 pode adotar ou mapear.

### Step 3 -- reflection-on-action | 2026-10-06 17:05 UTC | Fixtures golden da matriz e do relatorio
- happened: Gerei seis casos com entrada e esperado, calculados a mao, e recontei por script independente: zero divergencias.
- deviated: Esclareci em drift-metric.md arredondamento, populacao do D2, cadeia_completa e forma nao_aplicavel, que o desenho dos casos exigiu.
- less-sure: O esquema de entrada e meu; o plano 000014 le JUnit XML e pode precisar mapear.
- gate: not-installed

### Step 4 -- drift-control-protocol.md (2026-10-06, executor)
- Criado `.claude/references/general/drift-control-protocol.md` com as 10 secoes numeradas; regra de comparacao `D_B >= D_A` com empate < 1 item; condicao de refutacao "em dois ou mais dos degraus comparaveis"; tabela de resultados com uma linha por degrau mais O1, tempo, `t_verde`, auditoria e medidores do citizen.
- A secao 6 (tempo) ja traz as fontes de cada timestamp; o Step 5 acrescenta o template e o exemplo.
- Padrao: `run_all_checks.py` trava 120 s em `check_skill_system` quando roda sem stdin redirecionado dentro de script; usar `< /dev/null` (3,5 s). Promovido para Codebase Patterns.

### Step 4 -- reflection-on-action | 2026-10-06 17:08 UTC | Desenho do controle
- happened: Escrevi drift-control-protocol.md com as dez secoes: bracos, oraculo, O1, retrofit, replicas, tempo, regra de comparacao, covariaveis, ameacas e parada.
- deviated: A secao de tempo ja saiu com as fontes de timestamp, que o Step 5 previa acrescentar.
- less-sure: A condicao de refutacao por dois ou mais degraus comparaveis e minha leitura do texto do 000007.
- gate: not-installed

### Step 5 -- pilot-run-record.md e tempo (2026-10-06, executor)
- Criado `.claude/references/template/pilot-run-record.md` (campos com fonte, modelo, exemplo fictício). A secao 6 do protocolo ja aponta a fonte de cada timestamp (`conversation-trace.jsonl`/`briefs.md` para `t0`; `gate.json` `ts` para `t_verde`; campo manual para `t_aprovada`).
- Conta do exemplo, a mao: eventos 10:00, 10:04, 10:09, 10:30, 10:34, 10:41, 11:20 -> intervalos 4, 5, 21, 4, 7, 39 min; entram so os < 10 min: 4+5+4+7 = 20 min atendido; parede 80 min. Registro do exemplo traz 20 e 80.
- Achado: `conversation-trace.jsonl` existe no open-seja, mas `session_id` e quase sempre "null": delimitar a execucao pelo registro, nao por sessao.

### Step 5 -- reflection-on-action | 2026-10-06 17:08 UTC | Template de registro de execucao
- happened: Criei pilot-run-record.md com campos, fonte de cada timestamp, modelo e exemplo fictício com tempo atendido de 20 min recontado a mao.
- deviated: A ligacao timestamp-fonte ja estava no protocolo (Step 4); nao editei o protocolo de novo.
- less-sure: Onde o piloto guarda o registro (features/<slug>/pilot/) e sugestao, nao decisao.
- gate: not-installed

### Step 6 -- costura e lacunas (2026-10-06, executor)
- `drift-metric.md` ganhou as tabelas "Quem alimenta e quem consome" (itens 3 a 10) e "Lacunas contra o plan-000007" (8 lacunas, cada uma com item dono).
- `extended-cycle-contract.md`: uma linha de ponteiro (`Medida: ver drift-metric.md e drift-control-protocol.md`) no fim de CYC-016. Nao toca gate, hooks, settings nem `feature-layout.md`.
- Lacunas relevantes para os planos 000009-000016: (000013) `baseline_moved` e rodada `full` ao fim do plano; (000010/000014) formato do relatorio do runner (Cucumber JSON vs JUnit XML); (000014) colunas derivadas, cadeia completa, populacao do D3a, `--freeze` de M1; (000009) indice de frases do brief para sair de `NM-SEM-INDICE-BRIEF`.

### Step 6 -- reflection-on-action | 2026-10-06 17:09 UTC | Costura com os itens vizinhos e lacunas
- happened: Acrescentei as tabelas de quem alimenta e consome e as oito lacunas com dono; uma linha de ponteiro em CYC-016.
- deviated: Nenhum.
- less-sure: Se o plano 000014 aceita as definicoes de cadeia completa e populacao do D3a sem emenda.
- gate: not-installed

### Step 7 -- fechamento (2026-10-06, executor)
- `run_all_checks.py` (com `< /dev/null`): 15 PASS / 14 FAIL, contadores 17 undefined / 2 / 9 = baseline. pytest: 626 passed / 12 failed = baseline. Nenhum arquivo novo reclamado por check algum.
- Vocabulario: `D3a` aparece em `drift-metric.md`, `drift-control-protocol.md`, `pilot-run-record.md` e nas fixtures (`casos.json`, `README.md`); nomes de degrau, estados e codigos `NM-*` batem com CYC-009/010/016 e com o que o plan-000014 cita. Sem travessao tipografico nem aspas curvas. Sem nome de pessoa/parceiro/instituicao nos arquivos novos (a lista de termos de C1 e do orquestrador, que roda o `git grep`).
- Recontagem do Step 3: tabela no Step 3 (0 divergencias, reconferida no fechamento).
- Decisoes pendentes: 1=B, 2=B, 3=A, 4=B, todas `[default; aceito 2026-10-06]`; nenhuma no default sem aceite.
- Itens abertos para o designer: D-NNN do oraculo independente (lacuna 8); texto de H-009 abaixo.

**Texto sugerido ao designer (prosa Human; NAO escrito em `product-design/`), para colar em H-009 §3 2.9 via `/implement --manual`:**

1. Na medida de H-009: "A divergencia e medida por degrau, nao em numero unico: intencao->cenario (D1), cenario->teste (D2) e teste->codigo em duas leituras, verdade (D3a) e excesso (D3b), cada uma com os estados coberto, descoberto e nao medido; a definicao esta em `.claude/references/general/drift-metric.md`. O tempo ate a primeira feature aprovada pelo designer e medida complementar."
2. Na regra de comparacao e na refutacao: "O ciclo padrao nao tem REQ nem cenario; por isso D1 e D2 do ciclo padrao so existem por retrofit contra o oraculo do designer, e a comparacao direta e feita em D3a, D3b e O1 (cenarios do oraculo que falham no codigo final). Divergencia igual ou maior no estendido em um degrau significa `D_B >= D_A`, com empate quando a diferenca e menor que um item do denominador."
3. Em "O que o D nao ve" (acrescentar ao fim de 2.9): "O vetor D mede presenca de tag, de teste e de verde sobre o que ja virou requisito; nao ve omissao (o resíduo do brief, D0, lido fora do D, `NM-SEM-INDICE-BRIEF` quando as frases do brief nao foram indexadas) nem distorcao (julgada pela auditoria semantica e pela retraducao do citizen)."
4. Na condicao de refutacao: "Se, no piloto, ajustes e recusas no specify, escapes de intencao antes do codigo e mutantes virados em requisito forem todos zero, a aprovacao virou ritual, H-009 cai e H-001 volta a pedir adequacao por posicao na escala."

**Lacunas que afetam os planos 000009-000016**: ver Step 6 e a tabela de lacunas em `drift-metric.md` (formato do relatorio do runner; `baseline_moved`; rodada `full`; colunas derivadas; `--freeze` de M1; indice de frases do brief).

### Step 7 -- reflection-on-action | 2026-10-06 17:09 UTC | Fechar consistencia, C1 e decisoes pendentes
- happened: Rodei checks e pytest (baseline mantido), conferi vocabulario entre os arquivos e registrei o texto sugerido a H-009.
- deviated: Nenhum.
- less-sure: A lista de termos de C1 nao esta comigo; a varredura e do orquestrador.
- gate: not-installed
- drift: not-measured
