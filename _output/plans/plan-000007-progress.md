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
