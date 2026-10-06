# Progress -- Plan 000011

Append-only cross-iteration learnings. Each subagent reads this file at the start and appends findings at the end.

## Codebase Patterns
<!-- Subagents consolidate reusable patterns here -->

- Terreno herdado do plan-000007 (ler `_output/plans/plan-000007-progress.md`, secoes "Codebase Patterns", "Step 1" e "Step 7"): repositorio de execucao e este (sem prefixo `open-seja/`); `seja-as-intended.md` -> `product-design/product-design-as-intended.md` (§3); numeracao D-NNN do Doutourado nao vale aqui (D-004 = contrato Gherkin; D-005..D-008 = plan-000007; proximo livre D-009); "D-006 do Doutourado" citada nos planos = D-004 aqui.
- O contrato existe: `.claude/references/general/extended-cycle-contract.md` (CYC-001..026); esquema `features/<slug>/` em `.claude/references/template/feature-layout.md`; formato v2 em `.claude/references/template/plan-step.md`.
- Fixtures do harness ficam em `.claude/skills/scripts/tests/fixtures/<tema>/` (logo `<fixtures>/drift/` = `.claude/skills/scripts/tests/fixtures/drift/`).
- `python3` (nao `python`); pytest via `uvx --with pyyaml pytest ... --ignore=.claude/skills/scripts/tests/test_generate_spo.py --ignore=.claude/skills/scripts/tests/test_generate_spo_design_system.py`.
- Baseline (Q1): `run_all_checks.py` 17 PASS / 14 FAIL (PASS extras: check_intent.py e check_features.py) com contadores 17 undefined (check_conventions), 2 error(s) (check_i18n_keys), 9 error(s) (check_skill_system); pytest 863 passed / 12 failed (apos plans 000009-000010). Rodar `run_all_checks.py` com `timeout 200`, saida em arquivo, nunca dois ao mesmo tempo, nunca checks isolados, nunca `pkill -f`.
- Arquivos do harness: UTF-8, sem travessao tipografico nem aspas curvas; nada de nome de pessoa, parceiro, instituicao ou empresa.
- Portao nao instalado no open-seja: notas com `--gate not-installed`.
- Commits: `git -c user.name=arodrigues-puc-rio -c user.email=arodrigues-puc-rio@users.noreply.github.com commit ...`; nunca `--no-verify`.
- Decisoes pendentes do plano: o designer aceitou todas as recomendacoes em 2026-10-06; marcar como `[default; aceito 2026-10-06]`.
- `run_all_checks.py` deve rodar com `< /dev/null` (sem isso `check_skill_system` pode travar 120 s e dar ERROR; com isso leva ~3,5 s).

- Planos ja entregues neste roadmap: ver a coluna Status da Wave Summary em `_output/roadmaps/roadmap-000006-*.md` e os `## Implementation summary` dos planos DONE; os progress files deles listam lacunas que este plano deve absorver no Step 1.

## Iteration Log

## Step 1 -- terreno e dependencias (2026-10-06, executor)

Decisoes pendentes 1 a 6 aceitas nos defaults (1=A, 2=B, 3=A, 4=A, 5=A, 6=A) `[default; aceito 2026-10-06]`.

| item | resultado |
|---|---|
| (a) planos 000007, 000009, 000010 | existem. `extended-cycle-contract.md` CYC-001..027 (proximo livre **CYC-028**); specify = CYC-003, CYC-004, CYC-006 (`--specify` "reservada"), CYC-007, CYC-008, CYC-013 (degrau x receptor), CYC-014 (teste da surpresa). `grill-phase.md` GRL-001..015 (GRL-014 ainda diz "`--specify` continua reservada"). `gherkin-spec-format.md` GHK-001..019 (3 alem das 16 do plano). `drift-metric.md` ja cita `check_specify.py --status` (DRM-006 `scenario_status` = approved/stale/draft/missing) e `NM-CENARIOS-STALE` (inclusive "REQ editado (`rev` novo)", DRM-013). |
| (b) CLI `check_features.py` | `[root] [--feature <slug>] [--steps <dir>] [--json] [--matrix] [--strict] [--quiet]`; exit 0 sem erro, 1 com erro (ou aviso sob `--strict`), 2 uso/raiz ilegivel/`--feature` sem pasta/falha interna; JSON `schema_version: 1` (`summary`, `findings[{rule,severity,file,line,scenario,message,hint}]`, `features`, `matrix`). Funcoes publicas importaveis: `discover`, `validate`, `build_matrix`, `cited_reqs`, `scenario_key`, `parse_feature`, `load_intent`. |
| (b) CLI `check_intent.py` | `<path> [--require-approved] [--strict] [--json] [--d0]`; sem path varre `features/*/intent.md`. **`--strict` so sai 1 com `error`** (avisos VOZ/TAMANHO/SERVE nao falham). Funcoes publicas: `check_intent(text, require_approved=)`, `parse`, `table`, `ressalvas`, `MAX_SENTENCE_WORDS`, `MAX_SENTENCES_PER_PARAGRAPH`, `VOICE_LINTER`. Le com `utf-8-sig`. |
| (c) chaves extras no frontmatter | **sim, toleradas**: `_parse_frontmatter` le `chave: valor` sem lista fechada; `check_features.load_intent` le so `slug`, `status`, `scenarios`, `serve`. Secao nova `## Retradução` tambem e tolerada (secoes desconhecidas sao ignoradas; so "requisitos" e lida como tabela de REQ). Decisao pendente 1 fica em A. |
| (d) `/plan` | `_internal/plan/standard/SKILL.md` tem o passo **2b Grill phase** (antes do passo 3, criacao do plano); a specify entra como 2c. `plan/SKILL.md`: `--grill [<slug>]` na tabela e na Mode Detection; `--specify` na tabela como "Reserved ... not implemented". |
| (e) voz controlada | `lint_controlled_language.py` **ausente**. Constantes vem de `check_intent` (`MAX_SENTENCE_WORDS = 25`, `MAX_SENTENCES_PER_PARAGRAPH = 6`, ja com o try-import do 000074) e a ressalva `voz: nao verificada` (`check_intent.ressalvas()`). |
| (f) onde moram | scripts `.claude/skills/scripts/`; testes `.claude/skills/scripts/tests/test_<mod>.py` (importam `from check_x import ...`); fixtures `.claude/skills/scripts/tests/fixtures/specify/` (nao `tests/fixtures/specify/`). |
| (g) `run_all_checks.py` | descobre `check_*.py` por glob e roda `python <script>` sem argumentos, `cwd=raiz`, timeout 120 s; nao ha "pulado". O check condicional e o proprio script: `check_specify.py` sem argumentos varre `features/*/` e so reprova `stale` em feature com `scenarios: approved`; sem `features/` imprime "nada a verificar" e sai 0. Logo o registro do Step 7 e automatico (glob) mais a linha em `check_plugin_registry.json`; `run_all_checks.py` nao precisa ser editado. |

Termos de C1 usados nos Steps seguintes: a lista de nomes de parceiro, instituicao e pessoa do designer (grep case-insensitive sobre os arquivos novos e alterados). A lista nao e copiada aqui (C2). O repositorio ja tem o nome da organizacao em URLs de remote e na identidade git, pre-existente e fora do escopo.

Baseline confirmado: `run_all_checks.py` 17 PASS / 14 FAIL, contadores 17 undefined / 2 error(s) / 9 error(s); pytest 863 passed / 12 failed (`test_html_report` x8, `test_summarize_artifacts` x4). `git status` limpo.

Emenda central aplicada a todos os Steps (D-004 do as-intended; "D-006 do Doutourado" no plano): o citizen aprova a **retradução** em primeira pessoa e os exemplos narrados (a mensagem); o `.feature` e derivado e aprovado como **contrato** por quem le codigo; secao `## Retradução` com `rev` no `intent.md`; "Fora do escopo" sem cenario (SPC-006) mas presente na mensagem; teste da surpresa (CYC-014). Onde o plano mostra o `.feature` ao citizen ("Fluxo da fase", itens 3; Step 2 item 4; Step 5 item 6), vale a emenda; desvio registrado em cada Step.

Conflito de lacuna registrado: o progress do 000010 sugere usar `check_features.py --feature <slug>` sem `--strict` ("avisos sao do power dev"); o plano (SPC-007/SPC-008) usa `--strict`. Sigo o plano: aviso GHK bloqueia a aprovacao (vira SPC-008 aviso); quem resolve e quem le codigo, ao aprovar o contrato. O 000010 tambem diz "cenario `@REQ` de REQ `retirado` nao e erro" (no validador); aqui SPC-003 acusa como erro na **aprovacao** (a specify e mais estrita que o validador; o cenario de REQ retirado sai com linha em "Mudancas").

### Step 1 -- reflection-on-action | 2026-10-06 17:53 UTC | Terreno e dependencias
- happened: Conferi contrato, grill, convencao Gherkin, CLIs de check_intent e check_features, o passo 2b do /plan e o run_all_checks; baseline 17/14 e 863/12.
- deviated: Fixtures em .claude/skills/scripts/tests/fixtures/specify; run_all_checks nao precisa de edicao (glob); emenda D-004 muda o objeto de aprovacao do citizen.
- less-sure: Se o aviso GHK deve bloquear a aprovacao (plano) ou ficar so com quem le codigo (lacuna do 000010).
- gate: not-installed

## Step 2 -- protocolo `specify-phase.md` (2026-10-06, executor)

Criado `.claude/references/general/specify-phase.md`: SPC-001..018 (16 do plano + SPC-017 retradução e SPC-018 registro do citizen / teste da surpresa, ambos da emenda D-004), cada uma com "Quem decide" e "Critério de aceitação"; constantes (`SPECIFY_MAX_ROUNDS = 3`, `SPECIFY_MAX_AUTOFIX = 3`, voz importada de `check_intent`, `LOCK_SCHEMA_VERSION = 1`); tabela "de onde vem cada step"; 3 exemplos bons (pt e en) e 3 ruins; texto exato das duas aprovações; esquema dos campos `scenarios_*` e do lock; tabela de degradação (com a linha nova "Ninguém lê código"); voz; o que não faz; decisões 1-6 `[default; aceito 2026-10-06]`.

Desvios (emenda D-004):
- SPC-009 tem **dois** objetos de aprovação: o citizen aprova a retradução e o "não faz" (Aprovar / Ajustar / Voltar à entrevista / Descartar); quem lê código aprova o `.feature` (Aprovar o contrato / Pedir mudança / Ninguém aqui lê código). O plano mostrava o `.feature` ao citizen ("Fluxo da fase" item 3; Step 2 item 4).
- Campos do frontmatter: 5, nao 4 (acrescido `scenarios_contract_by`, com valor `ninguem` honesto quando ninguem le codigo). `scenarios_rev` = `rev` da retradução (a rodada de ajuste muda a mensagem e o contrato juntos).
- Lock acrescenta `retraducao` (sha256 da secao), `approved_at`, `approved_by`, `contract_by`; editar a retradução depois da aprovação torna o estado `stale` (razao `retraducao`).
- SPC-008 em modo estrito (aviso GHK bloqueia) e SPC-003 acusando cenario de REQ retirado: ver o conflito registrado no Step 1.
- `scenarios: draft` nao e escrito por ninguem: `draft` e estado calculado (sem lock e sem `scenarios: approved`).

Verify: 48 ocorrencias de `SPC-`; 18 regras com "Quem decide" e "Critério de aceitação"; C1 zero; sem travessao nem aspas curvas. `run_all_checks.py` = baseline (17 PASS / 14 FAIL, 17/2/9). `check_docs.py` (ja FAIL no baseline) sobe de 542 para 553 **avisos** "Specific plan ID" (11 citacoes de `plan-0000NN` no arquivo novo; mesmo padrao de `grill-phase.md` e `gherkin-spec-format.md`); 0 erros. Os exemplos bons sao reexecutados contra `check_features.py --strict` por teste no Step 4/8.

### Step 2 -- reflection-on-action | 2026-10-06 17:56 UTC | Protocolo specify-phase.md
- happened: Escrevi SPC-001..018 com quem decide e criterio, exemplos bons e ruins pt/en, os dois textos de aprovacao, o esquema do lock e a degradacao.
- deviated: Emenda D-004: dois objetos de aprovacao (mensagem ao citizen, contrato a quem le codigo); SPC-017/018 novas; quinto campo scenarios_contract_by; lock com hash da retraducao.
- less-sure: Se o formato da secao Retraducao e simples o bastante para o agente escrever sem tropecar no verificador.
- gate: not-installed

## Step 3 -- fixtures golden (2026-10-06, executor)

41 casos em `.claude/skills/scripts/tests/fixtures/specify/` (cada pasta e uma raiz de projeto; README com uma linha por caso), todos ficticios e **simulados** (nenhuma pessoa real aprovou nada; "usuario" e um papel):
- validos: `ok-completo` (3 REQs: 2 `comportamento`, 1 `restrição` com `Esquema do Cenário`; erro "desfazer" com cenario proprio; pt), `ok-minimo`, `ok-en` (en, "What I will not do");
- disparo e negativo por regra checavel: SPC-001 (`grilling`, `sem-intent`, `intent-com-erro`; negativo `ok-*`), SPC-003 (`sem-cenario`, `retirado-com-cenario`; negativo `retirado-sem-cenario`), SPC-004 (`sem-numero`; negativo `numero-no-entao` e o Outline de `ok-completo`), SPC-007 (26 / 25 palavras), SPC-008 (`ghk013`, `skip`), SPC-010 (`aprovar`, `contrato-ninguem`, `falha-nao-grava`), SPC-011 (`rev-sem-mudanca` / `rev-com-mudanca`, `teto` = info), SPC-012 (sem / com linha em Mudancas), SPC-013 (`aprovado`, `rev-subiu`, `hash-mudou`, `retraducao-mudou`, `intencao-reaberta`, `sem-lock`, `missing`), SPC-017 (sem secao, REQ sem exemplo, REQ fora, "nao faz" faltando, sem primeira pessoa), SPC-018 (PASS/percentual, frase de 26 palavras);
- retrocompatibilidade: `sem-features`, `features-de-terceiros`, `pasta-sem-intent`, `check-features-ausente`, e varredura sem argumentos (`varredura-aprovado-ok`, `varredura-aprovado-stale`, `varredura-draft`) para o check do `run_all_checks` (Step 7).

`esperado.json`: `args`, `exit_code`, `status`, `reasons`/`reqs` (stale), `findings` exatos `[regra, severidade, arquivo, linha]`, e `intent_final`/`lock_final` ou `unchanged` nos casos de `--approve`. As linhas foram tiradas do texto do fixture (a linha que a regra deve apontar) e conferidas a mao em `spc-008-*` (linha 8 = URL, linha 19 = tag `@skip`), `spc-003-sem-cenario` (linha 34 = linha do REQ 002) e `spc-003-retirado-com-cenario` (linha 26 = `Esquema do Cenário`). As linhas SPC-008 sao as que `check_features.py` ja devolve (o verificador embrulha, nao recalcula). Lock e frontmatter finais de `spc-010-*` foram calculados por uma implementacao independente da regra de `specify-phase.md` (gerador no scratchpad, nao versionado), nao pelo verificador.

Conferencia: todos os `intent.md` validos passam em `check_intent.py --require-approved` (so os casos `grilling` dao P6 e `intent-com-erro` da P2, como esperado); todos os `.feature` passam em `check_features.py --strict` exceto os disparos de GHK previstos (`spc-003-sem-cenario` GHK-005, `spc-008-*`, `spc-013-missing` sem `.feature`). C1 zero; sem travessao nem aspas curvas.

Desvio: as tres execucoes de referencia (`ref-a-ajuste`, `ref-b-sem-codigo`, `ref-c-stale`) ficam para o Step 6, que as escreve com as versoes intermediarias e a saida do verificador; o README ja as anuncia.

### Step 3 -- reflection-on-action | 2026-10-06 18:00 UTC | Fixtures golden
- happened: Escrevi 41 casos com esperado.json: ok pt/en/minimo, disparo e negativo por regra checavel, aprovacao com bytes finais, estados stale e retrocompatibilidade.
- deviated: Execucoes de referencia movidas para o Step 6; casos novos para SPC-017/018 (emenda D-004) e para a varredura do run_all_checks.
- less-sure: Se a contagem de palavras do step deve excluir a palavra-chave (decidi que sim).
- gate: not-installed

## Step 4 -- `check_specify.py` (2026-10-06, executor)

Teste primeiro: `test_check_specify.py` escrito antes do script e vermelho pelo motivo certo (coleta falhou: modulo ausente). Depois `check_specify.py` (stdlib, `main()` argparse, exit 0/1/2, bloco `# designer:`, docstring com `Invocation`/`Lifecycle` e tabela de regras, manifesto) e a entrada no fim de `check_plugin_registry.json` ("Specify Approval", scope `features`).

Interface real (difere do plano onde a emenda D-004 pediu):
- `check_specify(root, slug) -> Report(slug, findings, status)`; `approve(root, slug, *, at, by, contract_by) -> Report`; `compute_status(root, slug) -> Status(status, reasons, reqs)` (o plano previa `status() -> Literal`; aqui volta tambem as razoes e os REQs afetados, para a fase reescrever so os cenarios deles); `Finding(rule, severity, file, line, message, hint)`.
- CLI: `check_specify.py [raiz] [--feature <slug>] [--status] [--approve --at <UTC> --by <nome> --contract-by <nome|ninguem>] [--json]`. Sem `--feature`: varredura de `features/*/intent.md` que so reprova `scenarios: approved` com estado `stale` (e o check condicional do `run_all_checks`, Step 7).
- Reuso por **importacao** (nao subprocesso, como o plano dizia): `check_intent.check_intent/parse/table/_norm/ressalvas/MAX_SENTENCE_WORDS/MAX_SENTENCES_PER_PARAGRAPH` e `check_features.discover/validate/cited_reqs/scenario_key`. Sem validador (`ImportError` ou `_cf = None`): exit 2 "validador de cenarios nao encontrado", nada escrito; `--status` e a varredura funcionam sem ele (so hash e tabela). `check_intent.py` e `check_features.py` nao foram editados.
- Leitura com `utf-8-sig`; arquivo ilegivel, slug invalido (`../x`), pasta ausente, `--at` fora do formato, lock com `schema_version` desconhecido: exit 2 com uma frase em stderr, sem traceback. `--approve` preserva BOM e `\r\n` do `intent.md` e so troca/insere as 5 linhas do frontmatter.

Verify: `pytest test_check_specify.py` 74 passed (44 casos golden + 30 unitarios: idempotencia, so o frontmatter muda, CRLF/BOM, argumentos obrigatorios, aviso nao grava, validador ausente, stale apos edicao, `rev` nomeia o REQ, lock desconhecido, sem `features/`, slug ruim, ilegivel sem traceback, determinismo, linha `arquivo:linha: regra erro: ... Dica:`, ressalva de voz, constantes vindas de `check_intent`, exemplos de `specify-phase.md` passam em `check_features.py --strict` (pt em 3 arquivos, en), 18 regras com "Quem decide"/"Critério", cabecalho e registro). `uvx ruff check` limpo. pyright: **nao medido** (node do pyright sem `libatomic.so.1`, como no 000010). `run_all_checks.py`: **18 PASS** / 14 FAIL (o mesmo conjunto de 14; PASS novo = `check_specify.py`), contadores 17/2/9. pytest do harness: **944 passed / 12 failed** (os mesmos 12).

Correcao de contagem: o Step 3 tem **44** casos (nao 41).

Ajustes em `specify-phase.md`: o hash da retradução apaga comentarios HTML e linhas vazias de borda (como o parser de `check_intent`); SPC-007 conta palavras depois da palavra-chave.

### Step 4 -- reflection-on-action | 2026-10-06 18:05 UTC | check_specify.py
- happened: Escrevi os testes antes, depois o verificador com status, approve atomico e varredura; 74 testes passam, ruff limpo, 18 PASS no run_all_checks.
- deviated: Reuso por importacao em vez de subprocesso; compute_status devolve razoes e REQs; quinto campo contract_by e hash da retraducao no lock (D-004).
- less-sure: Se a varredura do run_all_checks deve reprovar projetos reais com aprovacao velha (e o pretendido, mas muda o health check deles).
- gate: not-installed

## Step 5 -- fase specify no `/plan` e flag `--specify` (2026-10-06, executor)

- `_internal/plan/standard/SKILL.md`: passo **2c Specify phase** logo depois da grill (2b) e antes da criacao das secoes do plano (3), em 7 itens curtos que apontam para `specify-phase.md` (portao SPC-001 e `--status`; escrever `.feature` e retradução; ate 3 autocorrecoes com `check_specify.py`; a mensagem ao citizen; o contrato a quem le codigo; `--approve` so com exit 0 e `Specify: approved (rev N)` no cabecalho; `--specify` avulsa e validador ausente). Em 2b sai a frase "`--specify` stays reserved". Tarefas sem codigo, planos v1 e projetos sem `features/` seguem como antes (D-008), dito na abertura do 2c.
- `plan/SKILL.md`: `--specify [<slug>]` no `argument-hint`, na tabela (substitui "Reserved ... not implemented") e na Mode Detection ("step 2c only").
- `extended-cycle-contract.md` CYC-006: a linha "Implementação" passa a dizer "`--specify` implementada pelo plan-000011 (`specify-phase.md`, SPC-016)" (troca de meia linha; o criterio de CYC-006 "nenhum texto executavel das flags existe em SKILL.md ate a implementacao" fica satisfeito pela propria implementacao).

Desvios: (1) emenda D-004 -- o item 6 do plano ("resumo por requisito ... Aprovar/Ajustar/...") virou duas perguntas: a mensagem (retradução) ao citizen e o contrato (`.feature`) a quem le codigo, com a opcao "Nobody here reads code" (`--contract-by ninguem`); (2) a opcao "Voltar a entrevista" foi mantida e "Descartar" segue a grill; (3) o `Feature: <slug>` ja era escrito pelo 2b, o 2c so acrescenta `Specify: approved (rev N)`.

Verify: `git diff --stat` so os 3 arquivos; `grep --specify plan/SKILL.md` acha a flag na tabela (linha 51), no hint e na Mode Detection; `Specify: skipped` continua no 2b e e citado no 2c; a fase aparece depois da grill e antes do passo 3. `check_skill_system.py` 9 erros (os mesmos do baseline: `product-design-as-coded.md` inexistente, `step_notes.py` etc.); `run_all_checks.py` 18 PASS / 14 FAIL, 17/2/9. Nenhum arquivo de gate, hook ou `settings` no diff. Lacuna: `grill-phase.md` GRL-014 ainda diz "`--specify` continua reservada para o plan-000011" (fora dos Files deste plano; para o plan-000015).

### Step 5 -- reflection-on-action | 2026-10-06 18:06 UTC | Fase specify no /plan e --specify
- happened: Inseri o passo 2c depois da grill, a flag --specify no wrapper e o ponteiro em CYC-006; check_skill_system e run_all_checks iguais ao baseline.
- deviated: Duas perguntas de aprovacao (mensagem e contrato) em vez de um resumo com o .feature, pela emenda D-004.
- less-sure: Se o agente vai separar bem a pergunta do contrato quando a mesma pessoa e citizen e power dev.
- gate: not-installed

## Step 6 -- execucoes de referencia (2026-10-06, executor)

**Simuladas**: roteiros escritos pelo executor; nenhuma pessoa real respondeu; "usuario" e um papel (citizen e, em outro papel, quem le codigo). Pastas em `.claude/skills/scripts/tests/fixtures/specify/`, cada versao com `esperado.json` e `saida.txt` (saida real do verificador):

- `ref-a-ajuste/` (feature com codigo, 3 REQs, um `restrição`): `v1-proposta` (step com URL e REQ 002 sem cenario nem item) -> exit 1 com SPC-003, SPC-008 (GHK-013) e SPC-017; `v2-mostrada` (uma autocorrecao) -> exit 0, `draft`, e o que o citizen ve (a retradução); `v3-sem-mudanca` (ajuste sem a linha em Mudancas) -> exit 1, SPC-011; `v3-ajustada` (retradução `rev: 2` + linha) -> `--approve` exit 0, grava lock e frontmatter identicos aos calculados a parte.
- `ref-b-sem-codigo/`: plano com `## Intenção` e `Specify: skipped -- tarefa sem código (só documentação)`; nenhuma pasta `features/`; a varredura sai 0 com "nada a verificar".
- `ref-c-stale/`: `v1-aprovado` (`approved`); `v2-intencao-mudou` (REQ 002 `rev` 2, intencao reaprovada) -> `--status`/checagem completa `stale (req-rev)` com o REQ 002 nomeado, exit 0; a **varredura** sai 1 ("aprovacao velha"); `v3-reescrito` (so os cenarios e o item do REQ 002 reescritos, nomes mantidos, retradução `rev: 2`) -> `--approve` exit 0, lock regravado com o REQ 002 em `rev` 2.

Testes: `test_golden_case` passou a descobrir tambem `ref-*/*/esperado.json`; 3 testes novos (cobertura das tres execucoes, varredura de `ref-c` sai 1, `ref-b` sem `features/`). `pytest test_check_specify.py` 85 passed; ruff limpo.

Desvios:
- O ajuste do roteiro do plano ("o limite é 3 segundos, não 2") muda **o que** se quer (o criterio do REQ 003) e, pela SPC-011, volta a grill. Troquei por um ajuste de forma (o exemplo do REQ 001 contava a semana a partir de segunda-feira). Isto e um achado sobre o proprio plano: o exemplo dele violava a regra que ele escreveu.
- Ajuste de UX no verificador: o GHK-005 (requisito sem cenario) deixou de virar SPC-008, porque repetia na mesma linha o que a SPC-003 ja diz com o ID do REQ (o leitor via dois achados para um fato). `specify-phase.md` (SPC-008) diz isso; `spc-003-sem-cenario/esperado.json` atualizado.

Dados de calibracao (do roteiro, nao de sessao observada; nao servem para calibrar o teto): (a) 1 rodada de ajuste; 1 autocorrecao antes do resumo; 1 aviso de estilo na proposta (GHK-013) e 0 avisos de voz na versao mostrada; entendimento do citizen sem pedir reformulacao: **nao medido**. (c) 1 REQ afetado; 2 cenarios reescritos de 4; 0 nomes de cenario mudados.

### Step 6 -- reflection-on-action | 2026-10-06 18:08 UTC | Execucoes de referencia
- happened: Escrevi as tres execucoes simuladas com versoes intermediarias, esperado.json e a saida real do verificador; 85 testes passam.
- deviated: Troquei o ajuste '3 segundos, nao 2' (que volta a grill pela SPC-011) por um ajuste de forma; GHK-005 deixou de duplicar a SPC-003.
- less-sure: Os numeros de calibracao sao do roteiro; nada aqui mede se um citizen real entende a retradução.
- gate: not-installed

## Step 7 -- dry-run da fase e retrocompatibilidade (2026-10-06, executor)

**Dry-run (simulado, descartavel, no scratchpad; nada versionado):** eu, como o agente, segui o texto do passo 2c sobre o `intent.md` aprovado da grill (fixture `grill/a-feature-com-codigo/intent-final.md`, `reserva-de-sala`, 4 REQs, um `restrição`), que nao e o dos fixtures da specify.
1. Portao: `check_intent.py --require-approved --strict` exit 0; `check_specify.py --status` = `missing`.
2. Escrevi `reserva-de-sala.feature` e a retradução. Rodada 1 do verificador: **2 erros, 4 avisos** -- SPC-004 (a restrição "em até 3 segundos" virou "Então eu vejo a confirmação rapidamente": palavra vaga, sem numero), SPC-017 (o item do REQ 003 sem `Exemplo:`), 4 x SPC-008/GHK-017 ("Azul", nome proprio com maiuscula, fora de "Modelo e termos").
3. Autocorrecao 1: numero no `Então`, exemplo no item, "a sala Azul" -> "a primeira sala da lista" no `.feature` (a specify **nao** pode acrescentar termo ao "Modelo e termos": SPC-015). Rodada 2: 0 achados, `draft`.
4. Aprovacao simulada (mensagem: Aprovar; contrato: Aprovar) e `--approve --at 2026-10-06T18:30Z --by usuario --contract-by usuario`: exit 0, lock gravado, 5 campos no frontmatter; `check_intent --require-approved --strict` e `check_features --strict` continuam limpos; varredura `approved`.

O que o agente errou (para calibrar a SKILL): numero da restrição trocado por palavra vaga (o mesmo erro que P2 pega na grill); exemplo esquecido num item; nome proprio no step. Uma autocorrecao bastou. Observacao: a retradução ficou com "sala Azul" (o registro do citizen nao passa pelo GHK-017) e o contrato com "a primeira sala da lista": mensagem e contrato contam o mesmo comportamento com valores diferentes; nada mecanico confere essa equivalencia (lacuna para a auditoria semantica do plan-000014).

**Retrocompatibilidade:**
1. `run_all_checks.py` no open-seja: 18 PASS / 14 FAIL (os 14 do baseline; contadores 17/2/9). Num projeto ficticio (pasta temporaria com `.claude` ligado ao harness) em tres estados: sem `features/` -> 18/14, `check_specify` PASS; com a feature do dry-run aprovada -> 18/14, PASS; com o `.feature` editado depois da aprovacao -> 17/15, **so** `check_specify.py` FAIL ("aprovação velha: peça nova aprovação"); todos os outros checks com o mesmo resultado nos tres estados.
2. Fixtures `sem-features`, `features-de-terceiros`, `pasta-sem-intent`: exit 0, nenhum achado (testes golden).
3. Plano v1: o 2c abre dizendo que planos v1 e projetos sem `features/` seguem como antes; `implement/SKILL.md`, hooks, `settings` e portao sem diff desde o inicio do plano.
4. `--specify` sem `features/<slug>/`: `check_specify.py --feature x` sai 2 com uma frase ("não há features/x/. A entrevista vem antes: rode /plan --grill.") e nao escreve nada (teste `test_feature_without_folder_refuses`).

Registro do check: **sem edicao de `run_all_checks.py`** -- ele descobre `check_*.py` por glob; o check condicional e o proprio script (varredura sem argumentos: sem `features/*/intent.md` sai 0; reprova so `scenarios: approved` em `stale`). Entrada no `check_plugin_registry.json` feita no Step 4. Nao ha estado "pulado" no orquestrador: "pulado" aparece como PASS com a linha "nada a verificar" (mesmo padrao de `check_intent.py` e `check_features.py`).

### Step 7 -- reflection-on-action | 2026-10-06 18:10 UTC | Dry-run e retrocompatibilidade
- happened: Segui o passo 2c sobre a intencao da grill: rodada 1 com 2 erros e 4 avisos, uma autocorrecao, aprovacao gravada; run_all_checks num projeto ficticio so muda o check_specify quando a aprovacao fica velha.
- deviated: run_all_checks.py nao foi editado: o glob registra o check; dry-run feito por mim, no scratchpad, sem pessoa.
- less-sure: Se mensagem e contrato com valores diferentes no exemplo confundem quem aprova os dois.
- gate: not-installed

## Step 8 -- contrato com os itens vizinhos (2026-10-06, executor)

**O que este plano entrega a quem**

| Item | Plano | Recebe | Regra |
|---|---|---|---|
| 6 | plan-000012 (plano a partir de cenarios) | cabecalho com `Feature: <slug>` (grill) e `Specify: approved (rev N)` (2c); as chaves de cenario `<slug>/<arquivo>::<nome>` no `index` do `scenarios.lock.json` (e as tags `@REQ-` na matriz de `check_features.py --matrix`) como fonte de `Scenarios:`; plano v2 so parte com `check_specify.py --status` = `approved`; `Specify: skipped` + step com `Tests:` nao-N/A e invalido em v2 (o proxy e a classificacao da grill) | SPC-002, SPC-010, SPC-013 |
| 7 | plan-000013 (teste-primeiro) | cenario -> teste pela chave do lock; `skip`/`xfail` ja barrados antes da aprovacao (GHK-014 -> SPC-008); o IMPLEMENT deve recusar step cujo `.feature` esta `stale` (a aprovacao nao vale mais) | SPC-008, SPC-012, SPC-013 |
| 8 | plan-000014 e plan-000008 (D1, relatorio) | `check_specify.py --feature <slug> --status --json` (`schema_version: 1`; `status`, `reasons`, `reqs`): `approved` e o unico estado que conta como cenario aprovado; `stale`/`draft`/`missing` = `não medido` (`NM-CENARIOS-STALE`), nunca `coberto`; `reqs` diz quais REQs; `scenarios_contract_by: ninguem` vira "contrato: não lido" ao lado do resultado (Q4); a retradução e o objeto da auditoria semantica (mensagem x contrato, ver observacao do Step 7) | SPC-009, SPC-013, SPC-017 |
| 9 | plan-000015 (integracao) | quickguide pt-BR e `/help` descrevem `/plan --specify` e as **duas** aprovacoes (mensagem ao citizen, contrato a quem le codigo, opcao "ninguem le codigo"); `check_specify.py` no `run_all_checks` dos projetos reprova aprovacao velha; atualizar GRL-014 ("`--specify` continua reservada") | SPC-009, SPC-016 |
| 10 | plan-000016 (piloto) | tempo de specify = de `approved_at` (grill) a `scenarios_approved_at`; linha de base simulada (ref-a: 1 ajuste, 1 autocorrecao; dry-run: 1 autocorrecao, 6 achados na rodada 1); contar Ajustar x Voltar a entrevista; calibrar `SPECIFY_MAX_ROUNDS` e `SPECIFY_MAX_AUTOFIX`; medir se o citizen reconhece a retradução (teste da surpresa) -- hoje **nao medido** | SPC-011, SPC-018 |

Reexecutado: `pytest` de `test_check_specify.py` + `test_check_features.py` + `test_check_intent.py` 312 passed; os exemplos de `specify-phase.md` passam em `check_features.py --strict` (teste `test_spec_good_examples_pass_check_features_strict`, pt e en); pytest do harness **955 passed / 12 failed** (os mesmos 12); `run_all_checks.py` **18 PASS / 14 FAIL** (o conjunto de 14 do baseline; contadores 17/2/9); `uvx ruff check` limpo nos dois .py novos (a partir da raiz). Vocabulario conferido com 000007-000010: `REQ-<slug>-NNN`, `status: grilling|approved`, `scenarios: approved`, chave `<slug>/<arquivo>::<nome>`, `NM-CENARIOS-STALE`, `scenario_status` (DRM-006: approved/stale/draft/missing). C1: grep dos termos sobre os arquivos novos e alterados -> zero (uma linha deste progress que listava os termos foi reescrita sem eles, por C2).

Ponteiros (uma linha cada, nenhum esquema mudado): CYC-003 ganhou "**Protocolo**: ... `specify-phase.md` ... `check_specify.py`" (a meia linha de CYC-006 foi no Step 5); `feature-layout.md` (secao `*.feature`); `gherkin-spec-format.md` (secao 4, depois de `scenarios: approved`). Nenhum arquivo de gate, hook, `settings` ou de esquema.

**Decisoes pendentes e o default em uso**: 1 = A (lock + campo; SPC-010, SPC-013), 2 = B (3 ajustes; SPC-011), 3 = A (idioma do pedido; Derivacao), 4 = A (o LLM escreve, as maquinas conferem; SPC-008), 5 = A (restricao com numero ou volta a grill; SPC-004), 6 = A (um `<slug>.feature`; Derivacao), todas `[default; aceito 2026-10-06]`.

**Lacunas (estado ao fim do plano)**
1. `check_features.py --matrix` ainda expoe `scenarios_approved` lendo so o campo; quem consome (plan-000014) deve ler `check_specify.py --status`. Nao editei `check_features.py` (instrucao).
2. Layout (000007): `scenarios.lock.json` e a secao `## Retradução` sao aditivos; `check_features` e `check_intent` os toleram (Step 1). Falta a emenda no esquema de `feature-layout.md` (texto sugerido abaixo).
3. Grill reaberta (lacuna 4 do plano): o campo `scenarios: approved` continua no frontmatter quando a grill reabre; `--status` devolve `stale (intencao-reaberta)` e a varredura do `run_all_checks` reprova. Alternativa para o 000015: a grill reaberta reescrever `scenarios: stale`. Decisao do designer.
4. `restrição` nao observavel volta a grill (decisao 5 = A); restricao que so um gate externo mede continua sem solucao (emenda a 000008/000010 se o piloto pedir).
5. Voz: sem `lint_controlled_language.py`; `check_specify` confere so tamanho de frase e paragrafo e a lista fixa de termos tecnicos; "uma ideia por frase", termos fixos e primeira pessoa (alem da palavra "eu"/"I") sao `voz: não verificada`.
6. Equivalencia mensagem x contrato nao e mecanica: no dry-run o exemplo da retradução ("sala Azul") e o cenario ("a primeira sala da lista") contam o mesmo comportamento com valores diferentes. Para a auditoria semantica do 000014.
7. GRL-014 em `grill-phase.md` ainda diz "`--specify` continua reservada para o plan-000011" (fora dos Files deste plano).
8. `run_all_checks` dos projetos que adotarem `features/` passa a reprovar aprovacao velha (`check_specify.py` sem argumentos). E o pretendido (como 000009/000010 fizeram), mas muda o health check deles.
9. Severidade: SPC-008 bloqueia por aviso GHK (estrito, como o plano), contra a sugestao do progress do 000010 ("avisos sao do power dev"). Se o piloto mostrar GHK-017 ruidoso (o dry-run teve 4 em 6 achados), reabrir: aviso GHK fica so no registro do contrato.

**Texto sugerido ao designer** (prosa Human; NAO escrito em `product-design/`; os arquivos de referencia via `/implement --manual`):
- `feature-layout.md`, secao `intent.md`: "Frontmatter opcional escrito so por `check_specify.py --approve` (SPC-010): `scenarios: approved`, `scenarios_approved_at`, `scenarios_approved_by`, `scenarios_contract_by` (`ninguem` quando ninguem le codigo), `scenarios_rev`. Secao opcional `## Retradução` (SPC-017): a mensagem ao citizen, com `rev`." Estrutura de pastas: acrescentar `scenarios.lock.json (specify; prova da aprovacao: versao de cada REQ, chaves de cenario, hash dos .feature e da retradução)`.
- `drift-metric.md` DRM-002 / DRM-013: "`stale`, `draft` e `missing` de `check_specify.py --status` contam como `não medido` (`NM-CENARIOS-STALE`), nunca como `coberto`; `scenarios_contract_by: ninguem` aparece como 'contrato: não lido'."
- Decisao **D-011** (proposta, via `apply_marker.py --marker DECISION_APPEND`, com confirmacao): "**D-011: a aprovacao da specify e um comando com prova, em dois objetos.** Context: o D1 precisa distinguir cenario aprovado de rascunho ou desatualizado, e D-004 separou a mensagem do contrato. Decision: o citizen aprova a retradução em primeira pessoa com exemplos narrados e o 'não faz'; quem le codigo aprova o `.feature` (ou o registro diz `ninguem`); so `check_specify.py --approve`, com tudo verde, grava os campos `scenarios_*` e o `scenarios.lock.json` (versao de cada REQ, hashes dos `.feature` e da retradução); qualquer mudanca depois torna o estado `stale`, que o D1 le como `não medido`. Consequences: aprovacao nao fica velha sem ninguem notar; mais um arquivo por feature; projetos com `features/` reprovam no `run_all_checks` com aprovacao velha. Rejected: so o campo no frontmatter (sem prova); tabela no `intent.md` (colide com o parser de REQ); mostrar o `.feature` ao citizen (D-004)."
- §14, linha `[intended] Grill e specify no /plan` (REQ-MC-011): as duas metades estao entregues (grill no 000009, specify aqui). Um marcador `STATUS: implemented` cabe agora, se o designer confirmar; `[intended] Retradução como objeto de aprovação` (REQ-MC-012) tambem tem o mecanismo entregue (SPC-009, SPC-017), mas a medida de que o citizen reconhece a mensagem e do piloto (000016): sugestao, marcar so a REQ-MC-011.

## Implementation summary

Entregue: protocolo `specify-phase.md` (SPC-001..018, com a emenda D-004: mensagem ao citizen e contrato a quem le codigo; teste da surpresa), verificador `check_specify.py` (SPC-001/003/004/007/008/011/012/017/018, `--status` missing/draft/approved/stale com razoes e REQs, `--approve` atomico com lock e 5 campos, varredura para o `run_all_checks`, exit 0/1/2, registrado no plugin registry), 44 fixtures golden + 3 execucoes de referencia simuladas (com versoes intermediarias e a saida real), passo 2c no `/plan` e flag `--specify`, ponteiros em CYC-003/CYC-006, `feature-layout.md` e `gherkin-spec-format.md`. Medidas: 85 testes novos passam; harness 955 passed / 12 failed (os 12 pre-existentes); `run_all_checks` 18 PASS / 14 FAIL (o mesmo conjunto; PASS novo = `check_specify.py`), contadores 17/2/9. Nao medido: pyright (sem `libatomic.so.1`); entendimento real do citizen (nenhuma sessao com pessoa).

### Step 8 -- reflection-on-action | 2026-10-06 18:12 UTC | Contrato com os itens vizinhos
- happened: Registrei o que vai a 000012-000016, as nove lacunas, as seis decisoes no default, o texto sugerido (feature-layout, drift-metric, D-011, marcador de REQ-MC-011) e uma linha de ponteiro em CYC-003, feature-layout e gherkin-spec-format.
- deviated: Reescrevi uma linha deste progress que listava os termos de C1 (C2 proibe nomes em _output).
- less-sure: Se o designer quer o aviso GHK bloqueando a aprovacao, ou so no registro do contrato.
- gate: not-installed

### Correções da revisão (orquestrador)
- Item 3: o hash do `.feature` agora vem de `_normalized` (BOM fora, CRLF para LF), em `_current`, logo em `build_lock` e no status. Os locks das fixtures não mudaram de hash (todas LF, sem BOM), então nenhuma foi regenerada. Teste novo: aprovar, regravar o `.feature` com BOM e CRLF, status segue `approved`.
- Item 5: `_atomic_write` aplica `shutil.copymode` do original, quando existe, antes do `os.replace`. Teste novo confere 0640 no `intent.md` e 0600 no lock.
- Item 8: `- Exemplo:` na coluna 0 logo depois do item conta como exemplo; a forma indentada continua valendo. O ramo antigo, inalcançável para coluna 0, foi fundido num só `elif`. Teste novo.
- Item 9: `SPECIFY_MAX_AUTOFIX` removida (sem consumidor). O SPC-008 diz que o limite de 3 tentativas vive só no SPC e no SKILL do `/plan`.
- Docs: GRL-014 (`--specify` implementada, não reservada); SPC-013 (o que `stale` observa e por que, mais a normalização do hash); SPC-010 e docstring (atomicidade por arquivo, falha entre as duas escritas cai em `sem-campo`, recuperável); SPC-016 (sem `features/`: varredura 0, `--feature` sai 2).
- drift: not-measured
