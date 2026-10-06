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
| (g) termos de C1 | sem lista no repositorio | conferencia por `git grep -i` de `<lista de termos de C1, mantida fora do ledger>` sobre o diff. No repo, os unicos acertos pre-existentes estao em `_output/briefs.md` e nos planos 000005 (nao tocados). |

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

## Step 6 -- formato e recusa nos SKILL.md e em plan-step.md (2026-10-06, executor)

Arquivos alterados (nenhum de portao, hook ou settings): `.claude/references/template/plan-step.md` (campo `Scenarios:` na forma final: chaves, dono do teste, `N/A (motivo)`; secao "Format version" com o cabecalho v2); `.claude/skills/plan/SKILL.md` (C3: `plan_format_version: 2` + `Feature:`/`Specify:` no modo standard depois da grill; `--light` e roadmap seguem v1 e o `plan_format_version: 1` continua na linha 9 e no C3); `.claude/skills/_internal/plan/standard/SKILL.md` (passo 2b: a linha `Specify: skipped` fica so aqui e o plano e v2; 2c remete ao 2b; passo 3 monta os steps de `index`; **novo passo 4c** roda `check_plan_scenarios.py` entre salvar (4/4b) e a revisao (5), corrige ate 3 vezes e pergunta com AskUserQuestion se persistir; validacao de metadados com a linha "Plan v2"); `.claude/skills/implement/SKILL.md` (decisao 4 = A: version check do Auto Mode aceita `2`, roda `check_plan_scenarios.py` e **para sem corrigir** se exit != 0; v1 como antes; versao ausente/outra continua caindo para manual; o Manual Mode ganhou uma frase com a mesma parada; o ramo teste-primeiro e do 000013 e nao foi implementado); `.claude/references/general/extended-cycle-contract.md` (emenda: CYC-028 plano v2 liga steps a cenarios, CYC-029 proxy do skip; a Compatibilidade, CYC-005 e CYC-020 trocam "tags `@REQ-`" por "chaves de cenario"; os dois paragrafos "Fato do estado atual" e "Estado da recusa" atualizados); `.claude/references/general/specify-phase.md` (um ponteiro no "O que este arquivo nao faz").

Verify: `grep -c "Specify: skipped" standard/SKILL.md` = 1 (linha do 2b); `grep -n "check_plan_scenarios" standard/SKILL.md` acha o 4c entre o passo 4b e o 5; `run_all_checks.py` 19 PASS / 14 FAIL, mesmo conjunto dos 14, contadores 17/2/9; `check_skill_system.py` 9 error(s) como no baseline; pytest 1073 passed / 12 failed (os 12 pre-existentes).
Desvios: o contrato recebeu mais que "so ponteiro" (CYC-028/029 e tres trocas de vocabulario `@REQ-` -> chave) para nao deixar duas regras contraditorias; cada edicao de SKILL.md e uma ou duas frases, detalhe em `plan-from-scenarios.md`.
Lacuna nova: o fluxo `--roadmap` Modo 1/2 executa o `standard/SKILL.md` por item inline (nota do cabecalho do proprio SKILL): um plano de item de roadmap passa a sair v2 como qualquer plano standard; o documento do roadmap em si segue v1 (C3). Nao ha fixture nem teste disso.

### Step 6 -- reflection-on-action | 2026-10-06 18:24 UTC | Formato e recusa nos SKILL.md
- happened: Editei plan-step.md, o C3 do plan, o standard (passo 4c e 2b/2c), o implement (aceita v2 e para se o verificador reprova) e o contrato (CYC-028, CYC-029).
- deviated: O contrato levou mais que um ponteiro, para nao deixar regras contraditorias sobre @REQ- e chave.
- less-sure: Se o roadmap inline gera plano v2 sem ter rodado a specify.
- gate: not-installed

## Step 7 -- tres execucoes de referencia e compatibilidade (2026-10-06, executor)

**SIMULADAS**: eu, como o agente, segui o texto do passo 4c sobre a feature ficticia `contas-da-semana` (a mesma do 000011), em modo descartavel; nenhuma pessoa real participou. Ficam como fixtures em `.claude/skills/scripts/tests/fixtures/plan_scenarios/ref-*/NN-*/` (plan.md + esperado.json), com raizes novas `_raizes/editada` e `_raizes/reaprovada` (a segunda saiu de `check_specify.py --approve` real: lock `rev: 2`, chave renomeada). Saidas reais do verificador (exit codes conferidos pelos testes):

(a) feature com codigo -- rascunho (exit 1): `plan.md:3: PFS-009 ... "A lista abre logo com muitas contas"` e `plan.md:36: PFS-006 ... O passo 4 muda comportamento e nao cita cenario`; uma correcao automatica (o step 4 passa a entregar o cenario de desempenho) -> final (exit 0, `0 erros, 0 informacoes; estado dos cenarios: approved`).
(b) tarefa sem codigo (README ficticio): `Specify: skipped -- tarefa sem codigo: atualizar um README`, todos `Tests: N/A`, nenhum `Scenarios:` necessario -> exit 0; variante com um step de teste -> `plan.md:22: PFS-013 erro: A tarefa muda comportamento no passo 2, mas a specify foi pulada` (exit 1).
(c) cenarios reaprovados depois do plano: `.feature` editado sem reaprovar -> `PFS-011 ... (estado: stale; feature, retraducao)` (exit 1); reaprovado com rev 2 e cenario renomeado -> `PFS-012` (rev 1 contra rev 2), `PFS-005` (chave antiga no passo 2) e `PFS-009` (a chave nova sem step) (exit 1); plano atualizado a mao (rev 2 e a chave nova) -> exit 0.

Compatibilidade: (1) o `check_specify.py` real devolve o mesmo `status` que o stub nos 29 casos com status (teste `test_real_check_specify_gives_the_status_the_stub_gives`); (2) planos v1: os 3 (`v1-real-1`, `v1-real-2`, `v1-minimo`) mais `v1-corpo-quebrado` saem 0 sem leitura do corpo; o `/plan` nao muda para v1 (o passo 4c e "plan v2 only") e o `/implement` mantem v1 e a versao ausente identicos (so o ramo `2` e novo); (3) `run_all_checks.py` sem plano v2 em `_output/plans/`: 19 PASS / 14 FAIL (o conjunto dos 14 do baseline, contadores 17/2/9; o PASS novo e `check_plan_scenarios.py` com "nada a verificar"); `check_plan_scenarios.py` sem argumentos na raiz do open-seja: exit 0.

**Calibracao** (simulada, um plano; o piloto do 000016 e que vale): correcoes automaticas antes de passar: 1 (execucao a); fracao de steps `N/A` no plano final: 2/5 = 40% (a migracao e o refactor); steps por cenario: 1,0 (dono unico); achados por rascunho: 2 (a) e 1 (b, variante). Nao medido: reacao de pessoa real a recusa; se `N/A (motivo)` vira fuga (so a fracao e o `info` PFS-006/013 medem).
Pytest: 161 testes no modulo; harness 1120 passed / 12 failed (os 12 pre-existentes). `uvx ruff check` limpo.

### Step 7 -- reflection-on-action | 2026-10-06 18:26 UTC | Execucoes de referencia
- happened: Simulei tres execucoes do /plan como fixtures (rascunho recusado e corrigido, tarefa sem codigo, cenarios reaprovados) e comparei o status real com o stub.
- deviated: A raiz reaprovada saiu de check_specify --approve real; as execucoes sao simuladas, sem pessoa.
- less-sure: Se uma recusa em plano real parece tao simples quanto na simulacao.
- gate: not-installed

## Step 8 -- contrato com os itens vizinhos (2026-10-06, executor)

**O que este plano entrega a quem**

| Item | Plano | Recebe | Regra |
|---|---|---|---|
| 7 | plan-000013 (teste-primeiro por cenario) | `Scenarios:` define o step **dono** do teste; a chave e a do `index` do lock (a mesma do relatorio do runner, CYC-027); `check_plan_scenarios.py <plano> --json` devolve, por step, `tests`, `tests_na` e `scenarios` (lista de chaves) e a `matrix` cenario -> steps; PFS-010 garante um unico ponto onde o teste fica verde; o `/implement` Auto Mode ja aceita v2 e para (sem corrigir) se o verificador reprova: o ramo teste-primeiro e do 000013 e deve estender o passo 3 do Phase 0, nao refaze-lo | PFS-008, PFS-010, PFS-011 |
| 8 | plan-000014 (relatorio de divergencia) | a coluna "step" do D1/D2: `matrix` do `--json`; plano velho (PFS-011 cenarios `stale`, PFS-012 `rev` velho) **nunca** conta como coberto (`não medido`); `Specify: skipped` = `NM-SPECIFY-PULADA` (PFS-013 garante que o plano pulado nao tem teste sem justificativa) | PFS-009, PFS-011, PFS-012, PFS-013 |
| 8 | plan-000008 (metrica, vetor D) | `check_features.py --matrix` continua lendo so `scenarios: approved` (lacuna 1 do 000011); quem calcula D1 deve ler `check_specify.py --status`, como o verificador deste plano | PFS-011 |
| 9 | plan-000015 (integracao e quickguide) | `/help` e quickguide pt-BR do `/plan`: formato do cabecalho (`Feature:`, `Specify:`), campo `Scenarios:` por chave, `N/A (motivo)`, as mensagens de recusa (PFS-006, PFS-009, PFS-011, PFS-013, em voz controlada), o passo 4c; atualizar GRL-014 ("`--specify` continua reservada"); `run_all_checks` dos projetos que adotarem v2 reprova plano v2 aberto com cenarios velhos (plano `# DONE` fica de fora) | PFS-001, PFS-011, PFS-012 |
| 10 | plan-000016 (piloto) | linha de base de friccao: correcoes automaticas por plano, fracao de steps `N/A` (40% na simulacao), achados `info` PFS-006/013 (`N/A (motivo)` em step com teste), steps por cenario (1,0) e quantas vezes a recusa chegou ao citizen (apos 3 tentativas); calibrar `N/A` usado para fugir de cenario e o dono unico (opcao B da decisao 2 se o piloto pedir) | PFS-006, PFS-007, PFS-010, PFS-013 |

Reexecutado: pytest do harness **1120 passed / 12 failed** (os 12 pre-existentes; 161 testes no modulo novo); `check_features.py --strict`, `check_specify.py` e `check_intent.py` sem argumentos: exit 0; `run_all_checks.py` **19 PASS / 14 FAIL** (o conjunto de 14 do baseline; contadores 17/2/9; PASS novo = `check_plan_scenarios.py`); `uvx ruff check` limpo nos dois .py; pyright nao medido (sem `libatomic.so.1`). Vocabulario conferido com 000007 a 000011: `CYC-NNN`, `Scenarios:`, `plan_format_version: 2`, `Specify: skipped -- <motivo>`, `Feature: <slug>`, `scenarios.lock.json` (`index`, `rev`), chave `<slug>/<arquivo>::<nome>`, `check_specify.py --status` (`approved|stale|draft|missing`), `SPC-NNN`, `GHK-NNN`, `NM-SPECIFY-PULADA`. C1: `grep -i` de `<lista de termos de C1, mantida fora do ledger>` sobre arquivos novos e alterados: zero (fora da copia literal dos planos v1 reais, que ja os tinham limpos).

**Decisoes pendentes e o default em uso** (todas `[default; aceito 2026-10-06]`): 1 = A (script novo; `critique_plan_coverage.py` nem existe aqui); 2 = A (dono unico, PFS-010); 3 = A (so a chave, nunca `@REQ-`; PFS-004); 4 = A (o `/implement` repete a parada; version check do Auto Mode e uma frase no Manual); 5 = A (uma feature por plano, PFS-002); 6 = A (infra com `N/A (motivo)` e `Tests:` tambem N/A, PFS-007/008).

**Desvios do plano (para o designer)**
1. PFS-006 e PFS-013 seguem o contrato, nao a tabela do plano: `Scenarios: N/A (motivo)` em step com `Tests:` nao-N/A **passa** (achado `info`, nao bloqueia; `--strict` o faz reprovar). A ferramenta nao julga "comportamento observavel"; so recusa o campo ausente e o N/A sem motivo que se leia.
2. Cabecalho = linhas antes da primeira secao `## `, em qualquer ordem (o plano dizia "ate a primeira linha em branco"; planos reais trazem `> **Origem**` no meio).
3. `run_all_checks.py` nao foi editado (glob); varredura sem argumentos ignora planos `# DONE | ...` (T3).
4. O contrato recebeu CYC-028 e CYC-029 e tres trocas de vocabulario (`@REQ-` -> chave em CYC-005, CYC-020 e na Compatibilidade), nao so um ponteiro; o Verify de "no maximo uma linha por arquivo de ponteiro" vale so para `specify-phase.md` (1 linha).
5. O teste do Step 4 foi escrito junto com o script, nao antes (as fixtures vieram antes).

**Lacunas (estado ao fim do plano)**
1. `Specify: approved (rev N)`: o `rev` do lock e a revisao da retradução. Se o designer reaprova mudando o corpo de um cenario sem subir o `rev` e sem renomear, o plano nao e invalidado (PFS-012 igual; PFS-005/009 nao veem). `stale` do `--status` pega a edicao **antes** da reaprovacao; depois dela o plano segue "valido". Sugestao ao 000014/000015: o lock ganhar um identificador de aprovacao (ex.: `approved_at`) e o cabecalho citar `Specify: approved (rev N, <approved_at>)`; exige emenda ao SPC-010 e ao formato do cabecalho. Nao resolvido aqui.
2. `--roadmap` Modos 1/2 executam o `standard/SKILL.md` por item inline: o plano de cada item passa a sair v2 como qualquer plano standard (o documento do roadmap segue v1). Sem fixture nem teste.
3. Nome de cenario com crase nao pode ser citado (PFS-004 no lock); `check_features.py` nao o proibe. Emenda sugerida ao GHK (nova regra) se o piloto encontrar um.
4. Campo `Tests:`/`Scenarios:` numa linha so; valor em varias linhas e ignorado alem da primeira.
5. `N/A (motivo)` com teste e um buraco medido, nao fechado (info). Se o piloto mostrar fuga, a opcao B da decisao 6 (recusar para step de codigo novo) e a reabertura.
6. O health check (`run_all_checks`) de um projeto que adotar v2 reprova plano v2 aberto com cenarios velhos; plano `# DONE` e ignorado. Plano `REVOKED`/`SUPERSEDED` tambem.
7. `check_docs` ganhou ~34 WARNING (IDs de plano nas copias dos planos v1 e no README das fixtures); nao falha nenhum check.
8. pyright nao medido; D-NNN proposta abaixo; `product-design/` nao foi editado.
9. `critique_plan_coverage.py` do upstream nao existe neste repositorio: a distincao "rastreabilidade de design" x "cobertura de cenarios" esta so em `plan-from-scenarios.md`.

**Texto sugerido ao designer** (prosa Human; NAO escrito em `product-design/`; os arquivos de referencia via `/implement --manual`):
- `plan-step.md` e contrato (Compatibilidade): ja aplicados neste plano (CYC-028, CYC-029); se o designer preferir so ponteiro, o texto equivalente e: "`Scenarios:` -- lista de chaves `<slug>/<arquivo>.feature::<nome>` entre crases, tiradas de `index` do `scenarios.lock.json` da `Feature: <slug>`, ou `N/A (<motivo>)`; a tag `@REQ-` nao vale no lugar da chave".
- Decisao **D-012** (proposta, via `apply_marker.py --marker DECISION_APPEND`, com confirmacao): "**D-012: o plano v2 liga cada step aos cenarios aprovados e e recusado por ferramenta nos dois sentidos.** Context: o D1 e o teste-primeiro precisam de uma ligacao step-cenario confiavel; a regra do 000007 so recusava step de teste sem `Scenarios:`. Decision: o plano v2 traz `Feature:` e `Specify: approved (rev N)` (ou `skipped -- <motivo>`); cada step lista as chaves de cenario que entrega (dono unico do teste) ou `N/A (<motivo>)`; `check_plan_scenarios.py` recusa step de comportamento sem cenario, cenario aprovado sem step, chave inexistente, cenarios `stale` e `rev` velho, e plano pulado com teste; plano v1 nunca e recusado. Consequences: mais um script e um campo por step; `N/A (motivo)` com teste passa com `info` e e medido no piloto; plano velho precisa de atualizacao a mao. Rejected: estender `critique_plan_coverage.py` (outro dominio); aceitar a tag `@REQ-` (esconde cenario sem step); validar so no `/implement` (o erro apareceria depois da revisao)."
- §14, linha `[intended] Grill e specify no /plan` (REQ-MC-011): com o plano a partir dos cenarios entregue, as tres fases (grill, specify, escrita do plano) tem mecanismo; um marcador `STATUS: implemented` cabe depois do 000015 (integracao) e do piloto (000016), nao agora.

### Step 8 -- reflection-on-action | 2026-10-06 18:27 UTC | Contrato com os itens vizinhos
- happened: Registrei o que vai aos itens 7-10 e ao plano 000008, os desvios, nove lacunas, as seis decisoes no default e a proposta D-012.
- deviated: O contrato levou CYC-028/029 e trocas de vocabulario, mais que um ponteiro.
- less-sure: Se o rev do lock basta para invalidar plano velho depois de reaprovar.
- gate: not-installed
