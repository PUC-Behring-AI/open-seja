# Progress -- Plan 000009

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

- Planos ja entregues neste roadmap: ver a coluna Status da Wave Summary em `_output/roadmaps/roadmap-000006-*.md` e os `## Implementation summary` dos planos DONE; os progress files deles listam lacunas que este plano deve absorver no Step 1.

## Iteration Log

### Step 1 -- conferencia do terreno (2026-10-06, executor)

Nada escrito fora do ledger. `git status` limpo no inicio (branch `dev`, HEAD 6cc1bd7).

| Item | Estado | Caminho / nota |
|---|---|---|
| (a) plano 000007 | existe | `.claude/references/general/extended-cycle-contract.md` (CYC-001..026). Regras reais da grill: CYC-002 (fase grill: entrada brief, saida `intent.md`, nunca pulada, teto 5x4, aprovacao), CYC-006 (flags `--grill`/`--specify` reservadas), CYC-007 (le/escreve/aprova), CYC-008 (sem `intent.md` aprovado nao ha specify), CYC-013 (degrau x receptor: D0/D1 o citizen aprova a lista e o "nao faz"), CYC-014 (teste da surpresa), CYC-015 (layout). `feature-layout.md` existe: frontmatter `slug`, `status: grilling\|approved`; secoes "Nas suas palavras" (pedido verbatim), "Requisitos" (REQ / Texto / Criterio), "Fora do escopo", "Premissas". `plan-step.md` tem `Scenarios:` (v2). Nenhum CYC "a confirmar". |
| (b) plano 000074 (voz controlada) | ausente | sem `controlled-language.md`, sem `lint_controlled_language.py`, sem constantes `MAX_SENTENCE_WORDS`/`MAX_SENTENCES_PER_PARAGRAPH` no harness. Decisao pendente 4 = B: limites minimos embutidos (25 palavras por frase, 6 frases por paragrafo, termos fixos), mesmos valores do §10 do as-intended; ressalva `voz: nao verificada`. |
| (c) `/plan` | existe | `_internal/plan/standard/SKILL.md` (119 linhas): a fase entra antes do passo 3 (criar as secoes do plano); ja tem ponteiro ao contrato na linha 13. `plan/SKILL.md` (122 linhas): tabela `## Arguments` sem `--grill`/`--specify`. |
| (d) scripts e testes | existe | scripts em `.claude/skills/scripts/`, testes em `.claude/skills/scripts/tests/`, fixtures em `.claude/skills/scripts/tests/fixtures/<tema>/` (logo `tests/fixtures/grill/` do plano = `.claude/skills/scripts/tests/fixtures/grill/`). `run_all_checks.py` descobre todo `check_*.py` de `scripts/` e o roda **sem argumentos** a partir da raiz: `check_intent.py` sem argumento precisa sair 0 quando nao ha `features/` (contara como PASS a mais, 16 PASS / 14 FAIL). Registro em `check_plugin_registry.json` (lista; `script`, `name`, `stack`, `scope`, `critical`). |
| (e) glossario | ausente | sem `product-design/glossary.md`; o glossario fixo de termos da fase fica em `grill-phase.md`. |

**Baseline confirmado**: `run_all_checks.py` 15 PASS / 14 FAIL (17 undefined; 2 error(s); 9 error(s)); pytest 626 passed / 12 failed.

**Decisoes pendentes** `[default; aceito 2026-10-06]`: 1=B (extensoes do `intent.md` definidas em `grill-phase.md` e no modelo; `feature-layout.md` so ganha um ponteiro marcado "emenda 000009"), 2=B (5 rodadas x 4 perguntas; devolve a decisao), 3=B (`comportamento` e `restricao`), 4=B (limites numericos embutidos, ressalva `voz: nao verificada`), 5=A (o agente propoe o slug, o citizen confirma).

**Emendas do adendo do roadmap absorvidas** (linha plan-000009 da tabela "Emendas por plano"), com o lugar onde entram:
1. Frases do brief indexadas (`F1..Fn`) na secao "Nas suas palavras"; respostas da entrevista indexadas (`A1..An`); REQ, "Fora do escopo" e "Premissas" citam esses indices. Isso tira o D0 de `NM-SEM-INDICE-BRIEF`: `check_intent.py --d0` lista as frases sem REQ ativo e sem fora-do-escopo (DRM-010). Steps 2, 3, 4.
2. Coluna "Para que" na tabela de REQ e secao "Modelo e termos" no `intent.md` (o plan-000010 avisa sobre substantivo de step ausente dela). Steps 2, 3.
3. Campo `serve:` no frontmatter, lista de `REQ-MC-NNN` / `JM-TB-NNN` / `D-NNN` do as-intended (leitura reversa "intencao sem feature" do plan-000014). Steps 2, 3, 4 (formato conferido; existencia do ID no as-intended nao e conferida pelo verificador, que le so o arquivo).
4. Sub-pergunta "o que essa pessoa sabe fazer" na dimensao `quem`. Step 2 (pergunta-modelo) e Step 3 (exemplo).
5. Nota C1: o pedido verbatim vai para `features/`, versionado com o codigo do projeto; a grill avisa e oferece trocar nomes por marcadores antes de gravar. Step 2.

**Desvio de esquema registrado**: o plano pedia `brief` verbatim no frontmatter; ele fica na secao "Nas suas palavras" (lugar que o esquema do 000007 ja da ao pedido), indexado por frase. YAML multilinha no frontmatter seria fragil e duplicaria o texto.

### Step 1 -- reflection-on-action | 2026-10-06 17:15 UTC | Conferir o terreno e as dependencias
- happened: Conferi contrato, layout, plan-step, SKILL.md do /plan, scripts e baseline; listei (a)-(e) no progress.
- deviated: O 000074 nao existe no open-seja; brief fica indexado na secao Nas suas palavras, nao no frontmatter.
- less-sure: Se check_intent.py rodado sem argumento pelo run_all_checks deve falhar em intent aprovado incompleto.
- gate: not-installed
