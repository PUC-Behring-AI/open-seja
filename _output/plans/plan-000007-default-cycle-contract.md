# DONE | 2026-10-06 16:59 UTC |
# Plan 000007 | FEATURE-O | METACOMM | 2026-10-05 02:00 UTC | default-cycle-contract: contrato do ciclo estendido (grill e specify no /plan, teste-primeiro no /implement, H-009) | Review: standard

> **Origem**: movido do ledger do Doutourado em 2026-10-05 (proposal-000088; la era `plan-000076`). Os IDs roadmap-000006 e plan-000007..000016 sao deste ledger (tabela no roadmap). Referencias a research-NNNNNN, reflection-NNNNNN, communication-NNNNNN, roadmap-000062 e plan-000064..000074 apontam para o ledger do Doutourado (repositorio do pesquisador). Caminhos `open-seja/...` em Files passam a ser relativos a raiz deste repositorio.
plan_format_version: 1

> Item 1 do roadmap-000006 (Wave 0, sem dependências). Repositório de execução: **open-seja** (worktree/branch por plano). O plano vive no Doutourado. C1: nenhum nome de parceiro nos artefatos que forem ao open-seja.

## Designer's metacommunication message (verbatim)

> Item 1 do roadmap-000006: `default-cycle-contract` (Depends on: nenhum). Título: "Contrato do ciclo estendido: fases grill e specify dentro do /plan, plano com steps ligados a cenários, teste-primeiro no /implement, layout por feature, D-NNN e H-009 (filha de H-008) com condição de refutação; retrocompatibilidade com planos antigos".
>
> Hipótese H-009: decompor a intenção em representações progressivamente mais formais (intenção detalhada com REQ IDs → Gherkin → testes → código) reduz a divergência as-coded vs as-intended, medida por degrau. Ciclo continua PLAN → IMPLEMENT → REFLECT; grill e specify são FASES do /plan (não skills antes dele); gate (plan-000065) e hooks (plan-000068) já existem e devem ser consumidos, não reconstruídos.

## Agent interpretation

**Problem.** O roadmap-000006 quer que o ciclo default do SEJA quebre a intenção em linguagem natural em sub-representações (intenção detalhada, Gherkin, testes) antes do código. Os itens 2 a 10 só podem andar se houver um **contrato único** que diga o que cada fase lê e escreve, onde os artefatos moram, como o plano os referencia, como o `/implement` os consome e como a hipótese pode ser refutada. Hoje não há esse contrato, e o formato de plano v1 não tem ligação step-cenário.

**Approach.** Um plano de **design** (nada de código de validador, runner ou fase executável: isso é dos itens 3 a 8). Este plano produz, no open-seja: (a) uma referência normativa do ciclo estendido; (b) o formato de plano com campo `Scenarios:` e a regra de retrocompatibilidade; (c) o layout `features/<slug>/`; (d) o contrato do teste-primeiro no `/implement`, consumindo o gate e os hooks existentes; (e) H-009 filha de H-008 e as D-NNN no `seja-as-intended.md`, com condição de refutação e a medida por degrau. O ciclo continua PLAN → IMPLEMENT → REFLECT; `grill` e `specify` são fases do `/plan`; não há skill nova, nem preset, nem perfil.

**Alternatives rejected.**
- Skills `/grill`, `/specify`, `/build` separadas antes do `/plan` (rascunho de 2026-09-30): bifurca o ciclo de H-008 e exige "ativação".
- Já implementar as fases neste plano: mistura contrato com execução; os itens 3 a 6 dependem de o contrato estar fechado e revisto.
- Reconstruir gate e hooks para o teste-primeiro: o plan-000065 e o plan-000068 já entregam `--fast` por step, hooks `Stop`/`PreToolUse` e deny de `--no-verify`/`--accept-baseline`; o contrato os **consome**.

**Selection rationale.** Sem `source:`; o roadmap-000006 é a fonte (tabela "Decisões"): as recomendações dele são o default de cada decisão pendente abaixo.

### Decisões fechadas (não reabrir neste plano)
1. Ciclo = PLAN → IMPLEMENT → REFLECT. PLAN contém as fases grill → specify → escrever o plano. IMPLEMENT = teste vermelho por cenário → código → gate. REFLECT lê divergência por degrau.
2. Sem preset e sem perfil: comportamento default do SEJA, igual para citizen e power dev (muda quem olha cada degrau).
3. Gate (plan-000065) e hooks (plan-000068) são pré-requisitos já entregues e são consumidos.
4. H-009 é filha de H-008 (registrada pelo plan-000064 no `seja-as-intended.md`, subseção 2.8). Numeração de D-NNN: continuar a sequência existente no open-seja (D-002 refina D-001; conferir o próximo número livre no Step 1).
5. A hipótese não depende do item 9 do roadmap-000062 (primeiro ciclo real).
6. Tarefas sem código (docs, pesquisa) pulam specify **por tipo de tarefa** (ver Decisão pendente 2 para a regra exata).
7. Este plano não escreve em `product-design/` do Doutourado e não edita roadmap nem INDEX.

### Decisões pendentes
Cada uma tem default (a recomendação da tabela "Decisões" do roadmap-000006). Se o designer não responder, os steps seguem o default; mudar uma delas altera só o Step indicado.

**Decisão pendente 1 -- Forma das fases grill e specify** (afeta Steps 2, 3)
- Opção A: fases internas do `/plan`, sem entrada avulsa.
- Opção B: fases internas do `/plan`, cada uma também invocável avulsa (`/plan --grill`, `/plan --specify`).
- Opção C: skills separadas `/grill` e `/specify`.
- **Recomendação: B.** Recommended when o citizen precisa repetir só a entrevista ou só o Gherkin depois de uma mudança de intenção. NOT recommended (A/B) when o ciclo precisa de vocabulário próprio por fase. C rejeitada: bifurca o ciclo de H-008. O contrato define as flags como interface reservada; o item 3/5 decide se as implementa.

**Decisão pendente 2 -- Quando a fase specify é pulada** (afeta Steps 2, 4)
- Opção A: por tipo de tarefa; o `/plan` decide e registra o motivo no plano.
- Opção B: nunca.
- Opção C: por escolha livre do designer a cada plano.
- **Recomendação: A.** Regra proposta: specify roda quando algum step tem `Tests:` não-N/A (cria ou muda código com comportamento observável). Pula, com a linha `Specify: skipped -- <motivo>` no plano, para prefixos DOCUMENT/CHORE/RESEARCH e para steps só de config ou harness. A fase grill nunca é pulada, mas pode ser curta (uma pergunta) quando o brief já traz intenção detalhada. NOT recommended: B (obriga Gherkin para um README) e C (vira opcional, que H-009 não mede).

**Decisão pendente 3 -- Layout por feature** (afeta Steps 1, 2, 3)
- Opção A: `features/<slug>/{intent.md, *.feature, gate.json}` na raiz do projeto, rastreável por tag `@REQ-NNN`.
- Opção B: arquivos soltos em `_output/`.
- **Recomendação: A.** Recommended when a feature precisa sobreviver ao plano que a criou e ser lida por `/reflect` e `/explain drift`. NOT recommended when o projeto é só de documentos. B perde a ligação com o código versionado (`_output/` é local por fork em vários projetos). O plano referencia a pasta pelo slug; plano de pesquisa ou docs não cria pasta.

**Decisão pendente 4 -- Definição de "divergência"** (afeta Steps 5, 6; detalhada no item 2 do roadmap)
- Opção A: só cenários verdes.
- Opção B: rastreabilidade completa (todo REQ tem cenário, teste, código).
- Opção C: composta, reportada **por degrau**: intenção→cenário, cenário→teste, teste→código (e gate), sem número único.
- **Recomendação: C.** Recommended when a hipótese diz "medida por degrau". NOT recommended: A (esconde cenário que não cobre o REQ) e um número único (esconde em que degrau a intenção se perde). Este plano só fixa o **vocabulário e a unidade de medida** (degrau, pares de artefatos, estados "coberto/descoberto/não medido"); a operação (fórmulas, controle) é do item 2.

**Decisão pendente 5 -- Onde roda o teste-primeiro (e Coder/Cleaner/Hardener)** (afeta Step 5)
- Opção A: dentro do `/implement`, por step (`--pipeline`, previsto no roadmap-000062).
- Opção B: skill separada `/build`.
- **Recomendação: A.** Recommended when o gate por step e o progress file do `/implement` já existem. NOT recommended when o loop precisaria de estado que o `/implement` não guarda (hoje não é o caso). Neste plano só o **primeiro passo da escada em código** entra no contrato (teste vermelho pelo motivo certo, por cenário, antes do código); Cleaner e Hardener ficam para o item 7, depois de medir findings por step (research-000050 rec 20).

**Decisão pendente 6 -- Versão do formato de plano** (afeta Step 3)
- Opção A: manter `plan_format_version: 1` e acrescentar `Scenarios:` como campo **opcional**.
- Opção B: `plan_format_version: 2`, com `Scenarios:` obrigatório quando a fase specify rodou; planos v1 continuam válidos para sempre.
- **Recomendação: B.** Recommended when o `/plan` precisa recusar step sem cenário (item 6) sem recusar planos antigos: a recusa vale só para v2. NOT recommended when nenhum validador distinguir versões (A basta, mas o item 6 não consegue impor a regra).

## Files

Todos no **open-seja** (repositório de execução), exceto onde dito. Caminhos do open-seja **não foram verificados nesta sessão** (o submodule não está inicializado no worktree): o Step 1 os confere antes de qualquer escrita.

- `.claude/references/general/extended-cycle-contract.md` (create) -- contrato normativo
- `.claude/references/template/plan-step.md` (modify) -- campo `Scenarios:`
- `.claude/references/template/feature-layout.md` (create) -- layout `features/<slug>/`
- `.claude/skills/_internal/plan/standard/SKILL.md` (modify, só a referência ao contrato; a implementação das fases é dos itens 3, 5, 6)
- `.claude/skills/implement/SKILL.md` (modify, só a referência ao contrato; implementação é do item 7)
- `product-design/seja-as-intended.md` (modify via `apply_marker.py`: H-009, D-NNN, CHANGELOG)
- `tests/` ou fixtures de planos antigos do open-seja (create: fixtures v1)

## Best practices

- Contrato primeiro, execução depois: cada regra tem um identificador estável (`CYC-NNN`) para os itens 3 a 8 citarem em `Traces:`.
- Marcadores Human (markers) só via `apply_marker.py` com confirmação; prosa de H-009 e das D-NNN colada pelo designer (`/implement --manual`), como no plan-000064.
- Voz controlada (item 11 do roadmap-000062, plan-000074): frases curtas, termos fixos, no texto que o citizen lê (perguntas do grill, resumo do Gherkin).
- "PASS is a tool result, not a sentence" (research-000050): todo critério deste plano é verificável por comando ou por leitura de arquivo.

## Design decisions

- **User-visible impact:** você escreve a intenção em linguagem natural e o `/plan` pergunta até ela ficar detalhada (grill); depois eu a escrevo como cenários Gherkin e peço a sua aprovação antes de planejar; só então o `/implement` escreve um teste vermelho por cenário e o código. Planos antigos continuam rodando como estão.
- **Trade-offs accepted:** mais passos antes do código (risco de fricção para o citizen, medido no piloto, item 10) em troca de divergência medida por degrau; um campo novo no formato do plano (v2), com custo de dois formatos em convivência.
- **Metacommunication impact:** I know you may not program by trade; therefore I ask you about what you want in your own words, I show you the scenarios in near-natural language so that you approve *what* will be built, and I keep the lower steps (tests, contracts) for the machine and for the developer who wants to look. If I skip the scenarios, I tell you why in the plan.

## Steps

### Step 1: Conferir o terreno no open-seja e fixar os identificadores
Na tag/branch `dev` do open-seja (submodule `open-seja`; `git submodule update --init open-seja` se vazio), confirmar que existem os arquivos listados em "Files", ler o texto atual de `/plan` standard, `/implement` (Quality Gate, modo auto, `--fast` por step do plan-000068) e a subseção 2.8 (H-008) do `seja-as-intended.md`. Registrar no progress do plano: último D-NNN usado, próximo H-NNN livre (esperado H-009; se já ocupado, usar o próximo livre e atualizar o roadmap pelo orquestrador), caminhos reais que diferirem dos de "Files", e o validador de formato de plano existente (se houver) para o Step 3. Nada é escrito no open-seja neste step.
- **Files**: open-seja/.claude/skills/_internal/plan/standard/SKILL.md (read), open-seja/.claude/skills/implement/SKILL.md (read), open-seja/product-design/seja-as-intended.md (read), open-seja/.claude/references/template/plan-step.md (read)
- **References**: product-design/conventions.md, product-design/constitution.md
- **Interface**: N/A
- **Verify**: o progress lista D-NNN e H-NNN livres e todos os caminhos de "Files" marcados como "existe" ou corrigidos; `git -C open-seja status` limpo.
- **Tests**: N/A (verificação de estado, sem código)
- [x] Done

### Step 2: Escrever o contrato normativo do ciclo estendido
Criar `extended-cycle-contract.md` com regras `CYC-NNN` cobrindo: (1) fases do `/plan` -- grill (entrada: brief; saída: `features/<slug>/intent.md` com REQ IDs `REQ-<slug>-NNN`, em linguagem que o citizen valida; nunca pulada), specify (entrada: `intent.md`; saída: `*.feature` com tag `@REQ-...` por cenário; ponto de aprovação humana antes de escrever o plano; pulada por tipo de tarefa com a linha `Specify: skipped -- <motivo>`), escrita do plano; (2) invocação avulsa `--grill`/`--specify` como interface **reservada**; (3) o que cada fase lê e escreve e quem aprova; (4) ordem e portões: sem `intent.md` aprovado não há specify, sem `.feature` aprovado não há plano v2; (5) os três degraus e os artefatos de cada par (intenção→cenário, cenário→teste, teste→código+gate); (6) o que o contrato **não** faz: não define validador de Gherkin (item 4), fórmula de divergência (item 2), nem Cleaner/Hardener (item 7). Cada regra com campo "Quem decide" e "Critério de aceitação". Incluir, para as decisões pendentes 1 a 5, o default adotado marcado `[default; pendente]`.
- **Files**: open-seja/.claude/references/general/extended-cycle-contract.md (create)
- **References**: product-design/product-design-as-intended.md, product-design/constitution.md
- **Depends on**: Step 1
- **Interface**: N/A
- **Verify**: o arquivo existe; todo `CYC-NNN` tem "Critério de aceitação"; `grep -c "CYC-" ` >= 12; nenhuma menção a nome de parceiro (`git grep -i` dos termos de C1 devolve zero); `python .claude/skills/scripts/run_all_checks.py` passa no open-seja.
- **Tests**: N/A (documento normativo)
- **Docs**: o próprio contrato; o quickguide pt-BR fica para o item 9.
- **Traces**: (sem REQ no as-intended; ver Coverage)
- [x] Done

### Step 3: Definir o formato de plano com steps ligados a cenários e a retrocompatibilidade
Em `plan-step.md`, acrescentar o campo `Scenarios:` (lista de `@REQ-...` ou nomes de cenário que o step cobre; `N/A (motivo)` permitido só para steps sem comportamento observável) e a regra de versão: `plan_format_version: 2` exige `Scenarios:` em todo step com `Tests:` não-N/A; `plan_format_version: 1` (ou ausente) permanece **válido para sempre** e o `/plan` e o `/implement` os leem como antes, sem warning de bloqueio (no máximo advisory). Documentar a regra no contrato (secção "Compatibilidade") e o que `/implement` faz com `Scenarios:` ausente em v2 (para a execução, não corrige). Criar fixtures de plano v1 reais (copiar 2 planos antigos do open-seja, sem dado privado) e 1 fixture v2 e 1 v2 inválido (step sem cenário). Se o Step 1 achou um validador de formato, estendê-lo só para distinguir versões; se não achou, **não criar validador** (item 6).
- **Files**: open-seja/.claude/references/template/plan-step.md (modify), open-seja/.claude/references/general/extended-cycle-contract.md (modify), fixtures de plano v1/v2 (create, caminho definido no Step 1)
- **References**: product-design/standards.md § Testing
- **Depends on**: Step 2
- **Interface**: campo `**Scenarios**: <@REQ-... | N/A (motivo)>` por step; cabeçalho `plan_format_version: 2`.
- **Verify**: os 2 planos v1 reais passam pela checagem existente (ou pela leitura do `/implement`) sem mudança de resultado em relação ao v0.10.1; o v2 válido passa; o v2 inválido é descrito no contrato como recusado (a recusa executável é do item 6); `run_all_checks.py` com o mesmo resultado de antes do plano.
- **Tests**: when um plano `plan_format_version: 1` é lido pelo validador existente, returns o mesmo resultado que na tag v0.10.1; when um plano v2 tem step com `Tests:` não-N/A e sem `Scenarios:`, o contrato o classifica como inválido (fixture marcada). Só roda como teste se o Step 1 achou validador; senão, `N/A (sem validador; fixtures documentadas)`.
- **Docs**: `plan-step.md` e seção "Compatibilidade" do contrato.
- [x] Done

### Step 4: Definir o layout por feature
Criar `feature-layout.md`: `features/<slug>/intent.md` (frontmatter `slug`, `status: grilling|approved`, tabela de `REQ-<slug>-NNN` com texto em linguagem natural e critério), `features/<slug>/*.feature` (tag `@REQ-<slug>-NNN` em cada `Scenario`; Gherkin Uncle Bob: critério de aceitação em Given/When/Then, sem detalhe de implementação), `features/<slug>/gate.json` (resultado do gate por feature: `{fast, full, ts}` + ponteiros para os JSONs do gate em `_output/quality/`). Regras: slug em kebab-case, uma pasta por feature, nunca apagada (Q2: git é a recuperação); tarefas sem código não criam pasta; o plano referencia `features/<slug>/` no cabeçalho (`Feature: <slug>`); `features/` entra na lista de diretórios que `/critique` e `/explain drift` leem (a leitura é dos itens 8 e 9). Definir a tabela de rastreabilidade (colunas: REQ, cenário, teste, código, gate) que o item 8 vai ler, **só como esquema**.
- **Files**: open-seja/.claude/references/template/feature-layout.md (create), open-seja/.claude/references/general/extended-cycle-contract.md (modify)
- **References**: product-design/constitution.md
- **Depends on**: Step 2
- **Interface**: esquema de `intent.md`, convenção `@REQ-<slug>-NNN`, esquema de `gate.json`.
- **Verify**: o esquema tem exemplo completo de uma feature fictícia (sem parceiro, sem dado real) com 2 REQs e 3 cenários; todo cenário do exemplo tem tag `@REQ-`; `run_all_checks.py` igual ao baseline.
- **Tests**: N/A (esquema documental; o validador é do item 4)
- **Docs**: o próprio arquivo de layout.
- [x] Done

### Step 5: Definir o contrato do teste-primeiro no `/implement` consumindo gate e hooks
No contrato, seção "IMPLEMENT": para cada step com `Scenarios:`, (a) o cenário vira teste executável; (b) o teste precisa ficar **vermelho pelo motivo certo** (falha por comportamento ausente, não por erro de import, sintaxe ou fixture) antes de qualquer código -- critério verificável: o relatório do runner mostra a asserção do cenário falhando e não `ERROR`/`ImportError`; (c) o Coder escreve o mínimo para ficar verde; (d) o gate `--fast` por step do plan-000068 roda, com as 3 tentativas e a falha no progress file já existentes; (e) o resultado entra em `features/<slug>/gate.json`. Declarar que o gate e os hooks (`Stop`, `PreToolUse` em commit, deny de `--no-verify` e `--accept-baseline`) **não mudam**: o contrato só os cita. Reservar `--pipeline` (Cleaner, Hardener) como interface do item 7, sem texto executável. Declarar o runner de Gherkin como **pendente do item 4** (recomendação do roadmap: pytest-bdd), sem acoplar o contrato a ele. Em `implement/SKILL.md` e `_internal/plan/standard/SKILL.md`, acrescentar **apenas** uma linha que aponta para o contrato (`See extended-cycle-contract.md`), sem mudar comportamento.
- **Files**: open-seja/.claude/references/general/extended-cycle-contract.md (modify), open-seja/.claude/skills/implement/SKILL.md (modify), open-seja/.claude/skills/_internal/plan/standard/SKILL.md (modify)
- **References**: product-design/constitution.md, research-000050 §10
- **Depends on**: Step 2, Step 3
- **Interface**: N/A
- **Verify**: `git diff --stat` mostra só a linha de ponteiro nos dois SKILL.md; nenhum arquivo de gate, hook ou `settings` aparece no diff; `run_all_checks.py` (inclui o check de estrutura dos SKILL.md) com resultado igual ao baseline.
- **Tests**: N/A (contrato e ponteiros; comportamento é do item 7)
- [x] Done

### Step 6: Registrar H-009 e as D-NNN no as-intended do open-seja
Redigir (prosa do designer, `/implement --manual`, como no plan-000064) e aplicar via `apply_marker.py` após confirmação: **H-009** filha de H-008 (subseção ao lado da 2.8): enunciado do roadmap; medida **por degrau** (intenção→cenário, cenário→teste, teste→código) com os estados coberto/descoberto/não medido; medida complementar: tempo até a primeira feature aprovada; **condição de refutação (rascunho para o designer ajustar)**: H-009 é refutada se, no piloto do item 10, a mesma feature construída no ciclo estendido e no ciclo padrão mostrar divergência composta igual ou maior no ciclo estendido em ao menos dois dos três degraus, **ou** se a divergência no degrau teste→código só cair por o gate ter sido o único filtro (os cenários aprovados não mudarem o que o código faz), **ou** se o tempo até a primeira feature aprovada aumentar sem queda em qualquer degrau. Com poucas features é estudo de caso, não teste estatístico (declarar). Mais as D-NNN (número livre do Step 1): D-A "grill e specify são fases do `/plan`, não skills"; D-B "layout por feature `features/<slug>/`"; D-C "divergência composta por degrau, não número único"; D-D "retrocompatibilidade: planos v1 válidos para sempre". Cada D em forma DDR (Context, Decision, Consequences, Rejected Alternatives), citando H-008 e H-004. Usar o nome do projeto, nunca nome de parceiro (C1).
- **Files**: open-seja/product-design/seja-as-intended.md (modify via apply_marker.py), open-seja/product-design/ (CHANGELOG append)
- **References**: product-design/product-design-as-intended.md
- **Depends on**: Step 1, Step 4, Step 5
- **Interface**: N/A
- **Verify**: `grep -n "H-009" open-seja/product-design/seja-as-intended.md` acha a hipótese com subseção "Condição de refutação" e a medida por degrau; existem 4 entradas `### D-NNN` novas com os quatro campos DDR e linha `STATUS` acima; CHANGELOG ganhou 5 linhas; `python .claude/skills/scripts/run_all_checks.py` passa; nenhum termo de C1 (`git grep -i` com a lista do Step 1) no diff.
- **Tests**: N/A (documento de design; escrita Human (markers))
- **Docs**: `seja-as-intended.md`.
- [x] Done

### Step 7: Provar a retrocompatibilidade e fechar o contrato
Rodar, no open-seja com as mudanças dos Steps 2 a 6: `run_all_checks.py`; a leitura do `/implement` em dry-run sobre as fixtures v1 (não executa step: confirma que o plano é aceito e que os campos lidos são os mesmos da v0.10.1); `/critique validate` nos arquivos novos. Registrar no progress o resultado e uma tabela "item do roadmap consome qual CYC-NNN" para os itens 2 a 10, para o orquestrador atualizar o roadmap. Listar as decisões pendentes que ainda estão no default.
- **Files**: open-seja/.claude/references/general/extended-cycle-contract.md (read), `_output/plans/plan-000007-progress.md` (create no Doutourado)
- **References**: product-design/constitution.md
- **Depends on**: Step 3, Step 5, Step 6
- **Interface**: N/A
- **Verify**: `run_all_checks.py` retorna o mesmo conjunto de falhas pré-existentes que a v0.10.1 (nenhuma nova); fixtures v1 aceitas; a tabela cobre os itens 2 a 10; o contrato não cita nenhum nome de parceiro.
- **Tests**: N/A (verificação; fixtures do Step 3 são o teste)
- [x] Done

## Coverage (advisory)

`product-design/product-design-as-intended.md` do Doutourado não tem marcadores REQ; `critique_plan_coverage.py` não se aplica e `Traces:` fica ausente. O plano executa no open-seja.

## Metacomm Intention
- **Summary**: I tell you that, by default, before I write any code I will first ask you what you want in your own words, then show you the scenarios for you to approve, and that old plans keep working; and I make this a hypothesis (H-009) that you can refute, measured step by step.
- **Source**: agent (metacomm)

Metacomm contradiction check: nenhuma intenção existente em `product-design-as-intended.md` (D-001 a D-005) conflita; D-004 (`apprentice`) e D-005 (`literature-reviewer`) tratam de presets e ficam fora do escopo, como no roadmap.

## Review log

**Review depth:** Standard (7 steps, ~9 arquivos distintos). Phase 1 inline; sem Phase 2 (nenhum Deferred com risco de regressão não resolvido). Prefixo FEATURE-O sem linha na tabela de atalhos: usei DX, COMPAT, TEST, ARCH, SEC.

### Phase 1 -- Perspective scan

| Perspective | Status | Concern |
|---|---|---|
| DX | Adopted | Contrato com `CYC-NNN` e critério por regra; cada step tem Verify por comando ou `grep`. |
| COMPAT | Adopted | Step 3 e 7: planos v1 válidos para sempre; prova por fixtures reais; só v2 exige `Scenarios:`. |
| TEST | Adopted | Teste-primeiro com "vermelho pelo motivo certo" tem critério observável (asserção, não `ERROR`). Steps 2 a 7 são documentais: `Tests: N/A` justificado; o único teste real é a regressão do Step 3. |
| ARCH | Adopted | Contrato não reimplementa gate nem hooks; só aponta (diff de Step 5 limitado a ponteiros). |
| SEC | Adopted | C1 verificado por `git grep` nos Steps 2, 6, 7; S1/S2: nenhuma chave nem `.env` envolvidos. |
| PERF, DB, API, I18N, UX, A11Y, VIS, RESP, DATA, OPS, MICRO | N/A | Sem superfície (plano de contrato). |

### Riscos e lacunas registrados
- Caminhos do open-seja não verificados (submodule vazio no worktree): o Step 1 é o portão.
- Condição de refutação é rascunho; o designer ajusta no Step 6 (prosa Human).
- Gherkin runner, validador de `.feature`, fórmula de divergência e Cleaner/Hardener ficam deliberadamente fora (itens 4, 2, 7).
- Fricção para o citizen (risco do roadmap) só é medida no item 10.

### Execution Metrics
| Metric | Value |
|---|---|
| Review depth | Standard |
| Phase 1 perspectives | 5 adopted, 11 N/A |
| Phase 2 deep-dives | 0 |
| Iterations | 0 |
| Pending decisions | 6 (defaults da tabela do roadmap-000006) |

## Outcomes

- Contrato `extended-cycle-contract.md` com regras `CYC-NNN` e critérios de aceitação.
- Formato de plano v2 (`Scenarios:`) coexistindo com v1, provado por fixtures.
- Esquema `features/<slug>/` e tabela de rastreabilidade (só esquema).
- H-009 (filha de H-008) com medida por degrau e condição de refutação, mais quatro D-NNN, no `seja-as-intended.md` do open-seja.
- Tabela item-do-roadmap x regra do contrato, para os itens 2 a 10.

smoke: false

## Implementation summary (2026-10-06)

- Steps: 7/7 concluidos; 4 por subagente Sonnet (2, 3, 4, 5), 3 pelo orquestrador Opus (1 terreno, 6 marcadores Human com confirmacao do designer, 7 verificacao). Iteracoes: 7 de 20; nenhum PARTIAL/FAILED.
- Arquivos: `.claude/references/general/extended-cycle-contract.md` (create; CYC-001..026, secoes Compatibilidade e IMPLEMENT); `.claude/references/template/plan-step.md` (campo `Scenarios:`, regra de versao); `.claude/references/template/feature-layout.md` (create); fixtures `.claude/skills/scripts/tests/fixtures/plan_format/` (2 v1 reais, v2 valida, v2 invalida, README); uma linha de ponteiro em `.claude/skills/implement/SKILL.md` e `.claude/skills/_internal/plan/standard/SKILL.md`; D-005..D-008 (`STATUS: proposed`) em `product-design/product-design-as-intended.md`.
- Desvios: `seja-as-intended.md` nao existe mais (fundido no as-intended §3); H-009 ja estava registrada (§2.9) e nao foi recriada; a refutacao por comparacao com o controle ficou para o designer colar no §2.9; o CHANGELOG nao ganhou linhas porque o regex do `CHANGELOG_APPEND` recusa IDs D-NNN; o portao nao esta instalado no open-seja (`--gate not-installed` em todas as notas).
- Quality gate: `run_all_checks.py` e pytest iguais ao baseline (14 FAIL pre-existentes; 626 passed / 12 failed). `/critique review` (code-reviewer, light) achou 4 critical e 8 advisory no contrato; os 4 critical e os advisory 5-8 foram corrigidos no contexto do orquestrador (1 rodada de 2); advisory 9-11 (criterios prospectivos sem comando) e 12 (CHANGELOG) ficam como deferidos.

### Generator-Critic Iterations
- Iteration count: 1/2
- Findings per iteration: [4 critical, 8 advisory]
- Resolution status: all resolved (critical); 4 advisory deferred

## Reflection

- 2026-10-06: O Step 6 encolheu porque o /design ja tinha registrado H-009, e o Step 1 absorveu a fusao do as-intended; a revisao achou contradicoes entre regras escritas por executores diferentes (CYC-018 x Compatibilidade, CYC-012 x CYC-026), corrigidas no fechamento. (notes 7, with deviation 7, with gate 0)
