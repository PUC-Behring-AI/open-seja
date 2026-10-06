# Progress -- Plan 000012

Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

## Codebase Patterns
<!-- Subagents consolidate reusable patterns here -->

- Terreno herdado do plan-000007 (ler `_output/plans/plan-000007-progress.md`, secoes "Codebase Patterns", "Step 1" e "Step 7"): repositorio de execucao e este (sem prefixo `open-seja/`); `seja-as-intended.md` -> `product-design/product-design-as-intended.md` (§3); numeracao D-NNN do Doutourado nao vale aqui (D-004 = contrato Gherkin; D-005..D-008 = plan-000007; proximo livre D-009); "D-006 do Doutourado" citada nos planos = D-004 aqui.
- O contrato existe: `.claude/references/general/extended-cycle-contract.md` (CYC-001..026); esquema `features/<slug>/` em `.claude/references/template/feature-layout.md`; formato v2 em `.claude/references/template/plan-step.md`.
- Fixtures do harness ficam em `.claude/skills/scripts/tests/fixtures/<tema>/` (logo `<fixtures>/drift/` = `.claude/skills/scripts/tests/fixtures/drift/`).
- `python3` (nao `python`); pytest via `uvx --with pyyaml pytest ... --ignore=.claude/skills/scripts/tests/test_generate_spo.py --ignore=.claude/skills/scripts/tests/test_generate_spo_design_system.py`.
- Baseline (Q1): `run_all_checks.py` 18 PASS / 14 FAIL (PASS extras: check_intent, check_features, check_specify) com contadores 17 undefined (check_conventions), 2 error(s) (check_i18n_keys), 9 error(s) (check_skill_system); pytest 955+ passed / 12 failed (os 12 pre-existentes; apos plans 000009-000011). Rodar `run_all_checks.py` com `timeout 200`, saida em arquivo, nunca dois ao mesmo tempo, nunca checks isolados, nunca `pkill -f`.
- Arquivos do harness: UTF-8, sem travessao tipografico nem aspas curvas; nada de nome de pessoa, parceiro, instituicao ou empresa.
- Portao nao instalado no open-seja: notas com `--gate not-installed`.
- Commits: `git -c user.name=arodrigues-puc-rio -c user.email=arodrigues-puc-rio@users.noreply.github.com commit ...`; nunca `--no-verify`.
- Decisoes pendentes do plano: o designer aceitou todas as recomendacoes em 2026-10-06; marcar como `[default; aceito 2026-10-06]`.
- `run_all_checks.py` deve rodar com `< /dev/null` (sem isso `check_skill_system` pode travar 120 s e dar ERROR; com isso leva ~3,5 s).

- Planos ja entregues neste roadmap: ver a coluna Status da Wave Summary em `_output/roadmaps/roadmap-000006-*.md` e os `## Implementation summary` dos planos DONE; os progress files deles listam lacunas que este plano deve absorver no Step 1.

## Iteration Log

## Step 1 -- terreno e dependencias no open-seja (2026-10-06, executor)

Decisoes pendentes 1-6: o designer aceitou todas as recomendacoes (A); todas `[default; aceito 2026-10-06]`. Decisao 3 = so a chave `<slug>/<arquivo>::<nome>` na lista de `Scenarios:`.

Este repositorio e o open-seja (branch `dev`); caminhos `open-seja/X` do plano valem como `X`; fixtures em `.claude/skills/scripts/tests/fixtures/plan_scenarios/`.

| Item | Estado | Onde / fato |
|---|---|---|
| (a) 000007, 000009, 000011 | existem (executados) | CYC-001..027 em `.claude/references/general/extended-cycle-contract.md` (maior = CYC-027; as regras novas deste plano: CYC-028, CYC-029); GRL-001..015 em `grill-phase.md`; SPC-001..018 em `specify-phase.md`; GHK-001..019 em `gherkin-spec-format.md`; DRM em `drift-metric.md`. Ordem de edicao dos SKILL.md 000007 -> 000009 -> 000011 -> este plano: cumprida, nao ha o que esperar. |
| (b) `check_specify.py --status` | existe | `python3 .claude/skills/scripts/check_specify.py <root> --feature <slug> --status [--json]`; exit 0 sempre (exit 2 so para uso, pasta ausente, schema desconhecido). JSON: `schema_version: 1`, `slug`, `status` (`missing\|draft\|approved\|stale`), `reasons`, `reqs`, `findings`, `ressalvas`. Sem `--feature` e a varredura (nao serve ao plano). |
| (b) `scenarios.lock.json` | existe, `schema_version: 1` | chaves ordenadas: `approved_at`, `approved_by`, `basis` (REQ -> rev), `contract_by`, `files` (sha256), `index` (chaves de cenario ordenadas), `retraducao` (sha256), `rev` (int, rev da retradução), `schema_version`, `slug`. O `rev` NAO entra no calculo de `stale` (so `basis`, `files`, `retraducao`): PFS-012 compara so o numero do cabecalho com o `rev` do lock. |
| (c) `plan-step.md` | existe | campo `**Scenarios**: @REQ-<slug>-NNN, <scenario name> \| N/A (<reason>)` + secao "Format version" (texto provisorio do 000007). Substituido no Step 6. |
| (c) `plan/SKILL.md` | C3, linha 90 | "follow with `plan_format_version: 1` on the next line". O C3 e o ponto do cabecalho; ganha o ramo v2 no Step 6. |
| (c) `_internal/plan/standard/SKILL.md` | passos 2b (grill) e 2c (specify) existem | **Ponto unico da linha `Specify: skipped`**: o passo 2b, ponto "Without code" (linha 35). O passo 2c cita a mesma frase so como lembrete ("tasks without code keep `Specify: skipped -- <reason>`"); para o `grep -c` do Step 6 dar 1, o 2c passa a remeter ao 2b sem repetir a linha literal. O 2b hoje diz "the plan stays v1": o Step 6 troca por v2. O 2c termina com "Linking steps to scenarios is plan-000012." |
| (d) validador de formato de plano | ausente | nenhum `.py` le `plan_format_version` (000007 progress, linha 36). `critique_plan_coverage.py` **nao existe neste repositorio** (so no upstream); nao ha parser de steps a reaproveitar. Decisao 1 = A, sem condicao a verificar. |
| (e) scripts, testes, fixtures | `.claude/skills/scripts/`, `.claude/skills/scripts/tests/`, `.claude/skills/scripts/tests/fixtures/<tema>/` | `run_all_checks.py` executa cada `check_*.py` com `cwd=<raiz>` e **sem argumentos**, le so o exit code; registro em `check_plugin_registry.json` (lista; acrescentar no fim). Check condicional = o proprio script (varredura de `_output/plans/` sem argumentos). |
| (f) nome de cenario com crase ou `::` | `check_features.py` NAO proibe | GHK-010 so exige nome unico por arquivo. Nome com crase quebra a lista entre crases; nome com `::` e inofensivo (a chave se corta no primeiro `::` depois de `.feature`). Decisao: PFS-004 recusa, com dica de renomear na specify, quando o `index` do lock tem chave com crase (nao da para cita-la). Registrado como lacuna. |
| (g) termos de C1 | sem lista no repositorio | conferencia por `git grep -i` de `tecgraf\|petrobras\|puc-rio\|behring` sobre o diff. No repo, os unicos acertos pre-existentes estao em `_output/briefs.md` e nos planos 000005 (nao tocados). |

Baseline (Q1, medido agora): `run_all_checks.py` 18 PASS / 14 FAIL (contadores 17/2/9 inalterados); apos o Step 4 o esperado e 19 PASS / 14 FAIL (PASS novo = `check_plan_scenarios.py`).

Decisoes de implementacao tomadas aqui (para os Steps 2-6):
1. Cabecalho = linhas antes da primeira secao `## ` (nao "ate a primeira linha em branco"): os planos reais trazem um bloco `> **Origem**` e `source:` antes ou entre as linhas de versao. A ordem das tres linhas segue livre.
2. Contrato (Compatibilidade) permite `Scenarios: N/A (motivo)` em step com `Tests:` nao-N/A quando o step nao tem comportamento observavel. Logo PFS-006 recusa so o campo **ausente** (ou o `N/A` sem motivo, PFS-007); `N/A (motivo)` com `Tests:` nao-N/A passa, com achado `info` (nao bloqueia) para o piloto contar. Isto muda a tabela do plano ("N/A (...)" recusado) para seguir o contrato.
3. Pela mesma razao, PFS-013 (skip coerente) recusa step com `Tests:` nao-N/A que nao traga `Scenarios: N/A (motivo)` justificado; com o motivo, passa com `info`.
4. Varredura sem argumentos ignora plano cujo titulo comeca com `# DONE |` (historia imutavel, T3; um plano concluido nao pode reprovar o health check porque os cenarios foram reaprovados depois).

### Step 1 -- reflection-on-action | 2026-10-06 18:15 UTC | Terreno e dependencias
- happened: Confirmei que 000007-000011 existem, a CLI de check_specify --status e o lock, e que critique_plan_coverage.py nao existe neste repo.
- deviated: O cabecalho passa a ser as linhas antes da primeira secao; PFS-006 e PFS-013 aceitam N/A com motivo, como o contrato.
- less-sure: Se N/A com motivo vira fuga; fica medido como info.
- gate: not-installed

### Step 2 -- reflection-on-action | 2026-10-06 18:16 UTC | Protocolo plan-from-scenarios
- happened: Escrevi plan-from-scenarios.md com PFS-001..015, cabecalho v2, campo Scenarios, tabela de compatibilidade e esquema JSON.
- deviated: N/A com motivo vale tambem com Tests nao-N/A (contrato); PFS-006 recusa so o campo ausente; PFS-014 e info.
- less-sure: Se o contrato aceita N/A com motivo em step com teste sem virar fuga.
- gate: not-installed

## Step 3 -- fixtures golden de plano (2026-10-06, executor)

38 casos em `.claude/skills/scripts/tests/fixtures/plan_scenarios/` (README lista um por um): 6 v1/v2 validos de base (`v1-real-1`, `v1-real-2` = copias literais das fixtures de `plan_format/`, `v1-minimo`, `v1-corpo-quebrado`, `v2-completo`, `v2-outline`, `v2-skipped`, `v2-cabecalho-livre`) e um disparo por regra PFS-001 a PFS-014 (PFS-015 e "nao faz": o teste checa que o diff e vazio, nao ha achado). Raizes de projeto compartilhadas em `_raizes/` (`aprovada`, `rev2`, `stale`, `draft`, `missing`: copias das fixtures de `specify/`). Fixtures SIMULADAS: escritas por mim a partir do projeto ficticio `contas-da-semana`, sem pessoa real.

Convencao de linha dos achados fixada no README (campo quando o achado e do campo; titulo do step quando o campo falta; `Feature:` para PFS-009; `Specify:` para PFS-011/012/014). As linhas de `esperado.json` foram calculadas na geracao (o gerador conhece o layout) e conferidas a mao em `pfs-006-sem-campo-com-testes` (linha 36 = `### Step 4:`).
Desvio: o plano pedia um `status.txt` por caso lido por stub; usei o campo `status` do `esperado.json` (o teste injeta o stub) e raizes reais em `_raizes/` para o Step 7 chamar o `check_specify.py` de verdade.

### Step 3 -- reflection-on-action | 2026-10-06 18:18 UTC | Fixtures golden de plano
- happened: Criei 38 casos com plan.md e esperado.json sobre 5 raizes compartilhadas, um disparo por regra.
- deviated: O status simulado vai no esperado.json e nao em status.txt por caso.
- less-sure: Se as linhas esperadas sobrevivem ao primeiro teste real do script.
- gate: not-installed

## Step 4 -- check_plan_scenarios.py (2026-10-06, executor)

Entregue: `.claude/skills/scripts/check_plan_scenarios.py` (PFS-001..014, `--json`, `--table`, `--strict`, `--status-cmd`, varredura sem argumentos; exit 0/1/2), `tests/test_check_plan_scenarios.py` (113 testes; goldens sobre as 38 fixtures, CLI com o `check_specify.py` real, stub por `--status-cmd`, BOM, erro de leitura, varredura, "nunca escreve", registro). Registrado no fim de `check_plugin_registry.json`. `uvx ruff check` limpo nos dois .py; pyright nao medido (sem `libatomic.so.1`, como nos planos 000010/000011).
Medidas: pytest do harness 1072 passed / 12 failed (os 12 pre-existentes); `run_all_checks.py` 19 PASS / 14 FAIL (o mesmo conjunto de 14; PASS novo = `check_plan_scenarios.py`), contadores 17/2/9. Os WARNING de `check_docs` subiram (618 -> 652) por IDs de plano nas fixtures v1 reais e no README; sao avisos, nao falha (as fixtures `plan_format/` ja os geram).

Decisoes de implementacao:
- Teste primeiro: as fixtures (Step 3) vieram antes; escrevi o script e o arquivo de teste na mesma rodada e rodei o teste so depois (a ordem teste-antes-do-codigo nao foi estrita; a prova de vermelho nao existe). Registrado.
- A tabela de linhas por regra esta no README das fixtures; `PFS-006`/`PFS-013` com `N/A (motivo)` em step com `Tests:` nao-N/A sao `info` (nao bloqueiam); `--strict` faz o `info` reprovar.
- Chave que falha PFS-004 (sem crases, slug trocado, duplicata) NAO conta como citacao: o cenario fica sem step (PFS-009 junto). Chave bem formada fora do lock: PFS-005, tambem sem contar na matriz (a matriz e por `index`).
- Cabecalho com erro que torna o modo indeterminavel (sem `Specify:`, formato, `Feature:` ausente, slug ruim, pasta inexistente) para ali (so PFS-002); `Specify:`/`Feature:` duplicados e `Feature:` em plano pulado continuam a checagem.
- `check_specify.py --status` so e chamado em plano v2 `approved` com cabecalho valido (v1 e `skipped` nunca precisam do validador).
- Chave de `index` com crase no nome: PFS-004 na linha de `Feature:`.
- Nao tocei `check_specify.py`, `check_features.py`, `check_intent.py` nem os testes deles.

### Step 4 -- reflection-on-action | 2026-10-06 18:22 UTC | check_plan_scenarios.py
- happened: Implementei o verificador com PFS-001..014, matriz em --json e 113 testes sobre as fixtures; 1072 passed e 12 failed pre-existentes.
- deviated: Escrevi script e teste na mesma rodada; N/A com motivo em step com teste vale como info.
- less-sure: Se as linhas esperadas e o N/A com motivo sobrevivem a planos reais.
- gate: not-installed

## Step 5 -- check condicional no run_all_checks (2026-10-06, executor)

Sem edicao de `run_all_checks.py` (desvio previsto): ele descobre `check_*.py` por glob, roda cada um com `cwd=<raiz>` e sem argumentos e le so o exit code. A condicionalidade esta no proprio script (varredura de `_output/plans/`): sem plano v2 ele imprime "nenhum plano v2 em _output/plans/; nada a verificar." e sai 0 (e o "pulado" do plano: o orquestrador mostra PASS, como `check_intent.py`, `check_features.py` e `check_specify.py`); com v2 valido sai 0 ("ok"); com v2 reprovado sai 1 e o nome da regra aparece na saida ("falhou"). Plano v1, `*-progress.md`, `*-qa-*` e plano `# DONE |` nunca entram. Nao ha estado "pulado" no orquestrador (lacuna ja registrada no 000011).
Teste novo: `test_orchestrator_style_run_is_skipped_ok_or_failed` (roda o script como o orquestrador roda: sem argumentos, cwd = raiz); 114 testes no modulo. `run_all_checks.py` real: 19 PASS / 14 FAIL, conjunto dos 14 igual ao baseline, contadores 17/2/9.

### Step 5 -- reflection-on-action | 2026-10-06 18:22 UTC | Check condicional no run_all_checks
- happened: Nao editei o run_all_checks: o glob ja registra o script e a varredura sem argumentos e a condicionalidade.
- deviated: Sem estado 'pulado' no orquestrador: aparece como PASS com 'nada a verificar'.
- less-sure: Se o health check dos projetos que adotarem v2 fica ruidoso com plano velho.
- gate: not-installed
