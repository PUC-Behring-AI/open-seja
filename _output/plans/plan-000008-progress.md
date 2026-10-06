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
