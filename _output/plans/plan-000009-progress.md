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

### Step 2 -- grill-phase.md (2026-10-06, executor)
- Criado `.claude/references/general/grill-phase.md` com GRL-001..015 (15 regras; 16 "Quem decide" e "Critério de aceitação" contando o cabeçalho), bloco de constantes (`GRILL_MAX_ROUNDS=5`, `GRILL_MAX_QUESTIONS_PER_ROUND=4`, `GRILL_DIMENSIONS`, `GRILL_MAX_REQS=12`, `MAX_SENTENCE_WORDS=25`, `MAX_SENTENCES_PER_PARAGRAPH=6`), pergunta-modelo pt-BR e en-US por dimensão, 3 REQs bons e 3 ruins, glossário fixo, tabela de degradação e tabela das 5 decisões pendentes `[default; aceito 2026-10-06]`.
- Mapa dos 12 itens do plano: (1) GRL-001; (2) GRL-003; (3) GRL-004; (4) GRL-009; (5) GRL-006; (6) GRL-007; (7) GRL-008; (8) GRL-012; (9) GRL-011; (10) GRL-010; (11) GRL-013; (12) GRL-014. Regras a mais: GRL-002 (slug, decisão 5), GRL-005 (extensões do esquema e emendas 1, 2, 3 e nota C1), GRL-015 (D0 via `--d0`).
- Emendas do roadmap: índice `F<n>`/`A<n>` (GRL-005, GRL-015); "Para que" e "Modelo e termos" (GRL-005, GRL-009); `serve:` (GRL-005); "o que essa pessoa sabe fazer" (GRL-004); nota C1 (GRL-005).
- `run_all_checks.py` no baseline (15 PASS / 14 FAIL; 17 / 2 / 9). `check_docs` ganha warnings "Specific plan ID" no arquivo novo, como os outros arquivos do contrato; continua FAIL por 0 errors e warnings pré-existentes. Sem travessão tipográfico nem aspas curvas.

### Step 2 -- reflection-on-action | 2026-10-06 17:17 UTC | Protocolo normativo grill-phase.md
- happened: Escrevi grill-phase.md com GRL-001..015, constantes, perguntas-modelo bilingues, exemplos de REQ, glossario e degradacao.
- deviated: Tres regras alem dos 12 itens: slug (GRL-002), extensoes do esquema com as emendas (GRL-005) e D0 (GRL-015).
- less-sure: Se a lista VAGUE_WORDS pega o bastante sem barrar criterio legitimo; calibrar no piloto.
- gate: not-installed

### Step 3 -- modelo template/intent.md (2026-10-06, executor)
- Criado `.claude/references/template/intent.md`: o próprio arquivo é um `intent.md` válido (feature fictícia `contas-da-semana`, 3 REQs: 2 `comportamento` e 1 `restrição`; 1 premissa confirmada; 2 itens de fora do escopo, cada um citando `F<n>`; D0 vazio). Comentários HTML marcam cada extensão como "emenda 000009" (decisão 1 = B).
- `feature-layout.md`: um bloco aditivo marcado "Emenda 000009 (aditiva)" com ponteiro às extensões; nada removido ou renomeado.
- Desvios: (a) `brief` não está no frontmatter (ver Step 1); (b) o frontmatter do modelo tem `designer_description` porque o arquivo é referência do harness; o verificador ignora chaves desconhecidas; (c) a Verify com `check_intent.py` roda no Step 4, que cria o verificador.
- `run_all_checks.py` no baseline (15 PASS / 14 FAIL; 17 / 2 / 9).

### Step 3 -- reflection-on-action | 2026-10-06 17:18 UTC | Modelo de intent.md com exemplo ficticio
- happened: Criei template/intent.md como intent valido de feature ficticia e um ponteiro aditivo em feature-layout.md.
- deviated: Brief indexado na secao, nao no frontmatter; frontmatter com designer_description; checagem pelo verificador fica no Step 4.
- less-sure: Se o specify do 000011 aceita o indice F/A como origem suficiente da retraducao.
- gate: not-installed

### Step 4 -- check_intent.py (2026-10-06, executor)
- Teste primeiro: `test_check_intent.py` (40 testes) rodado contra um stub com as assinaturas da Interface; 29 vermelhos por asserção (nenhum ImportError), 11 verdes triviais (os negativos). Depois o verificador: 40 passed.
- Criado `.claude/skills/scripts/check_intent.py`: `check_intent(text, *, require_approved=False) -> list[Finding]`, `Finding(regra, linha, mensagem, severidade)`, `brief_residue(text)` (D0, GRL-015), `ressalvas()`; constantes `GRILL_*`, `VAGUE_WORDS`, `MAX_SENTENCE_WORDS`, `MAX_SENTENCES_PER_PARAGRAPH` (importadas do lint do 000074 se ele existir). CLI: `<intent.md> [--require-approved] [--strict] [--json] [--d0]`; sem argumento varre `features/*/intent.md` (intenção aprovada com error -> exit 1; `grilling` só relata). Exit 2 para arquivo ausente. Registrado em `check_plugin_registry.json` (append no fim, formato preservado).
- Regras além de P1..P6: `ESQUEMA` (error: slug, status, seção Requisitos, tipo, estado; warning: esquema mínimo sem regra de parada, falta "Modelo e termos"), `VOZ`, `TAMANHO` (> 12 REQs ativos), `SERVE` (forma dos IDs), todas warning exceto ESQUEMA estrutural.
- Escolhas: (a) modo mínimo -- arquivo sem nenhuma extensão da grill e sem `--require-approved` recebe só as regras do mínimo do 000007 (IDs, texto, critério presente) e um warning; é o que faz o exemplo de `feature-layout.md` passar; (b) P4 inclui contiguidade 001..N e "REQ com rev > 1 ou retirado tem linha em Mudanças"; (c) a ressalva `voz: não verificada` vai num campo `ressalvas`, não como Finding, para não poluir a lista; (d) `grill-phase.md` GRL-006 ganhou uma frase sobre quais seções `--require-approved` exige e sobre a varredura.
- Verify: `check_intent.py .claude/references/template/intent.md --require-approved --strict` sai 0; ruff limpo; `pyright` do PyPI não roda neste WSL (falta `libatomic.so.1` para o node que ele baixa) -- usei `uvx basedpyright --level error`: 0 errors. `run_all_checks.py`: 16 PASS / 14 FAIL (o PASS a mais é `check_intent.py` sem `features/`), contadores 17 / 2 / 9; mesmos 14 FAIL. pytest: 666 passed / 12 failed (626 + 40).

### Step 4 -- reflection-on-action | 2026-10-06 17:23 UTC | Verificador deterministico check_intent.py
- happened: Escrevi 40 testes, vi 29 vermelhos por assercao contra um stub, e implementei check_intent.py com P1-P6, voz, D0 e varredura; 40 verdes.
- deviated: Regras extras ESQUEMA, TAMANHO, SERVE; modo minimo para o esquema do 000007; ressalva de voz fora da lista de findings; pyright substituido por basedpyright.
- less-sure: Se a varredura sem argumento no run_all_checks deve falhar em intent aprovado incompleto num projeto real.
- gate: not-installed

### Step 5 -- fase grill no /plan e flag --grill (2026-10-06, executor)
- `_internal/plan/standard/SKILL.md`: novo passo `2b. Grill phase` antes do passo 3 (criação das seções), 10 linhas em en-US que apontam para `grill-phase.md` e `check_intent.py`: classificar, slug, aviso C1, índice `F`, rodadas, `intent.md` em `grilling` por rodada, `check_intent.py --json` por rodada, teto, aprovação Approve/Adjust/Discard (C4), `--require-approved --strict` antes do passo 3, `Feature: <slug>`, tarefa sem código com `## Intenção` e `Specify: skipped -- <reason>`, metacomm I/you, `--grill` só a fase. Passos de revisão (5) e `/implement` intocados.
- `plan/SKILL.md`: `--grill [<slug>]` no `argument-hint`, na tabela de argumentos e em Mode Detection (despacho ao passo 2b); `--specify` como linha "reservada" (cita CYC-006, sem ID de plano, para não gerar warning de citação privada).
- `extended-cycle-contract.md`: duas linhas de ponteiro (CYC-002 "Protocolo"; CYC-006 "Implementação": `--grill` implementada, `--specify` reservada).
- Escolha: enquanto a specify não existe, o plano depois da grill continua v1 com a linha `Feature: <slug>` sob o cabeçalho (CYC-005 pede `Feature:`; CYC-018 só pede v2 quando a specify roda).
- Verify: `git diff --stat` só nos três arquivos; nenhum arquivo de gate, hook ou settings; `grep` acha `--grill` na tabela e `Specify: skipped` no internal. `run_all_checks.py` 16 PASS / 14 FAIL, 17 / 2 / 9 (os 9 de `check_skill_system` são os mesmos: `product-design-as-coded.md` ausente). pytest 666 / 12.

### Step 5 -- reflection-on-action | 2026-10-06 17:24 UTC | Fase grill no /plan e flag --grill
- happened: Inseri o passo 2b no internal standard, --grill no wrapper e dois ponteiros no contrato; checks e pytest no baseline.
- deviated: Plano depois da grill segue v1 com Feature: slug ate a specify existir; --specify listada como reservada.
- less-sure: Se o passo 2b curto basta para um agente conduzir a entrevista sem ler grill-phase.md inteiro.
- gate: not-installed

### Step 6 -- três entrevistas de referência (2026-10-06, executor) -- SIMULADAS
- Criado `.claude/skills/scripts/tests/fixtures/grill/` (caminho do Step 1, não `tests/fixtures/grill/`): `README.md` (aviso de simulação, tabela, roteiro manual), `esperado.json` (erros esperados, D0 e calibração por versão), (a) `a-feature-com-codigo/` transcrição + `intent-rodada-1.md`, `intent-rodada-2.md`, `intent-final.md`; (b) `b-tarefa-sem-codigo/` transcrição + `plano-trecho.md` (`## Intenção` de 4 linhas e `Specify: skipped`); (c) `c-brief-detalhado/` transcrição + `intent-rodada-0.md`, `intent-final.md`.
- **As entrevistas são simuladas**: escritas pelo executor, sem pessoa real; o "citizen" é um papel. A execução real de `/plan --grill` em dry-run também é a transcrição simulada de (a), não uma sessão; "o citizen entendeu sem reformular" é **não observado**.
- Saída de `check_intent.py --require-approved --strict` (pares negativos):

| Versão | Errors | Exit | D0 (`--d0`) |
|---|---|---|---|
| (a) rodada 1 | P1 (não faz, erros e limites), P3 (pergunta aberta), P6 | 1 | F2 |
| (a) rodada 2 | P2 ("rápido" sem número em REQ-004), P3 (premissa não confirmada), P6 | 1 | -- |
| (a) final | nenhum | 0 | -- |
| (c) rodada 0 | P1 (gatilho, erros e limites), P3, P6 | 1 | F3 (só em premissa) |
| (c) final | nenhum | 0 | F3 (só em premissa) |
| (b) | sem `intent.md` (GRL-012); teste confere `## Intenção` e `Specify: skipped` | n/a | n/a |

- Calibração de (a) (roteiro simulado): 3 rodadas; perguntas 4 + 3 + 2 = 9; avisos de voz 0 nas três versões; reformulações não observadas. (b): 1 rodada, 4 perguntas. (c): 1 rodada, 3 perguntas. Nenhum caso chegou perto do teto 5x4; o dado não serve para calibrar o teto (fica para o piloto, plan-000016).
- Testes: `test_check_intent.py` ganhou 16 testes parametrizados sobre `esperado.json` (regras por versão, D0, exit code do `--strict`, forma da tarefa sem código): 56 passed.
- Plano v1: o passo 2b só atua ao escrever plano novo; nenhuma linha que lê plano existente mudou (`implement/SKILL.md` intocado; fixtures v1 de `plan_format/` intocadas). A "leitura de um plano v1 antigo no `/plan`" não foi executada como sessão; a prova é o diff (nenhum texto de leitura de plano mudou) e a varredura `check_intent.py` sem argumento na raiz sair 0.
- `run_all_checks.py` 16 PASS / 14 FAIL, 17 / 2 / 9, mesmos FAIL. pytest 682 passed / 12 failed (626 + 56). Sem travessão tipográfico nem aspas curvas; nomes fictícios genéricos (sala, lista de compras), nenhum termo de C1 (a lista de termos é do orquestrador, que roda o `git grep`).

### Step 6 -- reflection-on-action | 2026-10-06 17:27 UTC | Tres entrevistas de referencia (simuladas)
- happened: Escrevi tres entrevistas simuladas com versoes intermediarias e finais; check_intent falha nas intermediarias pela regra esperada e passa nas finais; 16 testes novos.
- deviated: Fixtures em .claude/skills/scripts/tests/fixtures/grill; dry-run do /plan --grill e a transcricao simulada, nao uma sessao; (b) nao tem intent.md.
- less-sure: Os numeros de calibracao sao do roteiro, nao de pessoa real; nao servem para o teto 5x4.
- gate: not-installed

### Step 7 -- contrato com os itens vizinhos (2026-10-06, executor)

**O que este plano entrega a quem**

| Item | Plano | Recebe | Regra |
|---|---|---|---|
| 4 | plan-000010 (formato Gherkin) | `REQ-<slug>-NNN` estáveis e contíguos em `intent.md` aprovado; seção "Modelo e termos" para o aviso de substantivo de step ausente; `Tipo: restrição` também vira cenário | GRL-005, GRL-009, GRL-011 |
| 5 | plan-000011 (specify) | portão de entrada: `check_intent.py <intent.md> --require-approved --strict` (exit 0) e recusa de `status: grilling` (CYC-008); coluna "Para que" e índice `F`/`A` como matéria da retradução; "Fora do escopo" citado por índice; `--specify` continua reservada | GRL-006, GRL-008, GRL-014 |
| 6 | plan-000012 (plano a partir de cenários) | `Feature: <slug>` sob o cabeçalho do plano depois da grill; tarefa sem código com `## Intenção` e `Specify: skipped -- <motivo>`; o plano segue v1 até a specify existir | GRL-012 |
| 8 | plan-000014 (relatório no REFLECT) e plan-000008 (métrica) | D1 conta os REQs `ativo` de `intent.md` aprovado; REQ `retirado` sai do denominador depois da reaprovação e conta como descoberto até lá; `rev` > 1 marca cenários desatualizados; **D0 sai de `NM-SEM-INDICE-BRIEF`**: `check_intent.py --d0` devolve `{"estado": "medido", "frases": n, "residuo": [...]}` ou `nao_medido` com `NM-SEM-INDICE-BRIEF`; `serve:` no frontmatter para a leitura reversa "intenção sem feature" | GRL-011, GRL-015, GRL-005 |
| 9 | plan-000015 (integração) | quickguide pt-BR e `/help` descrevem `--grill` (o que o citizen aprova: a lista e o "não faz"; o que o power dev aprova: o `intent.md` e a rastreabilidade) | GRL-014, GRL-008 |
| 10 | plan-000016 (piloto) | tempo de grill entra no tempo até a primeira feature aprovada (`approved_at` é o fim); linha de base simulada do Step 6 (a: 3 rodadas, 9 perguntas, 0 avisos de voz); calibrar `GRILL_MAX_ROUNDS` e `GRILL_MAX_QUESTIONS_PER_ROUND` com sessões reais; contar "Ajustar" na aprovação ao lado dos ajustes no specify | GRL-007, GRL-003 |

**Lacunas com os planos 000007 e 000008 (estado ao fim do plano)**

1. Esquema de `intent.md`: resolvido como superconjunto (GRL-005, decisão 1 = B); `feature-layout.md` ganhou só o ponteiro "Emenda 000009". Risco que continua: um validador do item 4 que leia só o esquema mínimo; ele deve importar `check_intent.parse`/`table` em vez de reescrever o parse.
2. `rev` no D1: `drift-metric.md` ainda não tem a linha "REQ com `rev` novo deixa os cenários desatualizados (`NM-CENARIOS-STALE`) até o specify reaprovar". Dono: plan-000014 (ou emenda do 000011, que escreve o estado dos cenários).
3. Tipo `restrição`: contado igual no D1 (sem mudança no 000008).
4. Tarefa sem código: consistente com o 000008 (`NM-SPECIFY-PULADA`, relatório não aplicável).
5. Voz controlada: o 000074 não existe no open-seja; `check_intent.py` confere só os dois limites numéricos e devolve a ressalva `voz: não verificada`. Quando o lint chegar, ele é importado (as constantes já vêm dele se existir).
6. Ordem de aprovação: o verificador agora existe e é o portão que o item 5 deve usar (CYC-002 aponta para ele).
7. `--grill` implementada; `--specify` reservada (ponteiro em CYC-006).
8. Novo: `features/` versionado com o pedido verbatim (nota C1, GRL-005). A troca por marcador depende do citizen; nenhum verificador procura nome sensível.
9. Novo: `check_intent.py` roda sem argumento no `run_all_checks.py` (varre `features/*/intent.md`): num projeto real, uma intenção aprovada que perder uma seção faz o health check falhar. É o comportamento pretendido (aprovado = completo), mas muda o resultado do `run_all_checks` dos projetos que adotarem `features/`.

**Decisões pendentes e o default em uso**: 1 = B (GRL-005), 2 = B (GRL-007), 3 = B (GRL-009), 4 = B (GRL-010), 5 = A (GRL-002), todas `[default; aceito 2026-10-06]`.

**Texto sugerido ao designer** (prosa Human; NÃO escrito em `product-design/`):
- Decisão D-009 (proposta, via `apply_marker.py --marker DECISION_APPEND` com confirmação): "**D-009: A grill indexa o pedido e as respostas, e a regra de parada é um verificador.** Context: o D0 ficava `não medido` sem índice do pedido, e a parada por impressão do agente não é verificável. Decision: o `intent.md` numera as frases do pedido (`F<n>`) e as respostas (`A<n>`); requisitos, fora do escopo e premissas citam esses índices. A regra de parada P1 a P6 é conferida por `check_intent.py`, sem LLM; só a aprovação do citizen grava `approved`. Consequences: o D0 passa a ser medido; o specify usa o verificador como portão. Rejected: parar por julgamento do agente; brief no frontmatter."
- §14, linha `[intended] Grill e specify no /plan` (REQ-MC-011): a metade grill está entregue; um marcador `STATUS` só cabe quando o specify (plan-000011) também estiver. Sugestão: não marcar agora.

### Step 7 -- reflection-on-action | 2026-10-06 17:27 UTC | Contrato com os itens vizinhos
- happened: Registrei a tabela do que o plano entrega aos itens 4, 5, 6, 8, 9 e 10, nove lacunas e o texto sugerido ao designer.
- deviated: Duas lacunas novas: brief verbatim em features/ e check_intent no run_all_checks dos projetos.
- less-sure: Se a linha de rev no drift-metric.md deve vir do 000011 ou do 000014.
- gate: not-installed

### Correções da revisão (orquestrador)
- Item 1: `check_intent.py` lê com `utf-8-sig`; o BOM não esconde mais o frontmatter.
- Item 2: `OSError` e `UnicodeDecodeError` viram erro sem traceback. Modo arquivo: exit 2. Scan: finding `LEITURA` por arquivo, varredura continua, exit 2 ao fim.
- Item 3: `_split_row` mantém `\|` e `|` dentro de crases na célula.
- Item 4: `parse` ignora `## ` dentro de bloco cercado (``` ou ~~~).
- Item 5: `--d0` sem path, ou com `--strict`/`--require-approved`, sai com 2 e mensagem.
- Item 6: docstring de exit codes reescrita (scan sai 1 quando um intent `approved` tem erro, sem `--strict`).
- Item 7: passo 2b do `/plan` standard coerente com CYC-002/CYC-004/D-005/D-008: a grill sempre roda; sem código vira uma pergunta, sem `features/`, `Specify: skipped`, plano v1; planos v1 existentes seguem como antes.
- Item 8: frase sobre `serve:` em `feature-layout.md` (Emenda 000009) e `intent.md`.
- Item 9: com `--require-approved`, "Mudanças" é cobrada também no arquivo mínimo (`extended or require`).
- Testes: 9 novos em `test_check_intent.py` (vermelhos antes, 65 verdes agora).
- drift: not-measured
