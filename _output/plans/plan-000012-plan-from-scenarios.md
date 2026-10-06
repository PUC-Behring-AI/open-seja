# Plan 000012 | FEATURE-O | 2026-10-05 13:05 UTC | plan-from-scenarios: formato final do plano v2 (cada step cita os cenários que cobre) e recusa executável nos dois sentidos | Review: standard

> **Origem**: movido do ledger do Doutourado em 2026-10-05 (proposal-000088; la era `plan-000081`). Os IDs roadmap-000006 e plan-000007..000016 sao deste ledger (tabela no roadmap). Referencias a research-NNNNNN, reflection-NNNNNN, communication-NNNNNN, roadmap-000062 e plan-000064..000074 apontam para o ledger do Doutourado (repositorio do pesquisador). Caminhos `open-seja/...` em Files passam a ser relativos a raiz deste repositorio.
plan_format_version: 1

> Item 6 do roadmap-000006 (Wave 2; Depends on: plan-specify-phase = plan-000011). Repositório de execução: **open-seja** (worktree/branch por plano); o plano vive no Doutourado. C1: nenhum nome de parceiro nos artefatos que forem ao open-seja. ID alocado pelo orquestrador (não usa `reserve_id.py`). Este plano é `plan_format_version: 1` porque o v2 só existe depois que ele executar. Usa o vocabulário dos planos 000007 (`CYC-NNN`, campo `Scenarios:`, `plan_format_version: 2`, v1 válido para sempre, `Specify: skipped -- <motivo>`), 000008 (D1, D2), 000009 (`intent.md`, `rev`, `retirado`), 000010 (`check_features.py`, `--matrix`, `GHK-NNN`, Outline = um cenário, chave `<slug>/<arquivo>::<nome>`) e 000011 (`check_specify.py --status`, `scenarios.lock.json`, estado `stale`, `SPC-NNN`, cabeçalho provisório `Feature:` / `Specify: approved (rev N)`). Não reabre decisão fechada daqueles planos.

## User brief

> Item 6 do roadmap-000006: `plan-from-scenarios` (Depends on: plan-specify-phase). "Formato do plano: cada step lista os cenários que cobre; /plan recusa step sem cenário."

## Agent interpretation

**Problem.** O 000007 definiu o campo `Scenarios:` e a regra "v2 exige `Scenarios:` em step com `Tests:` não-N/A", mas só em texto e só num sentido. O 000011 deixou três pontas para este item: (1) o cabeçalho final (`Feature:`, `Specify:`) que ele grava provisoriamente; (2) a recusa executável; (3) o proxy do "skip por tipo de tarefa", porque `Tests:` não-N/A só existe depois que a specify rodou. Faltam também: cenário aprovado sem nenhum step (cobertura no sentido inverso), o que fazer com step de infraestrutura, e o que acontece com um plano velho quando os cenários são reaprovados (`stale`). Sem isso o item 7 (cenário vira teste vermelho por step) não tem uma ligação step↔cenário confiável e o item 8 não tem a coluna "step" da matriz.

**Approach.** Plano **técnico** com núcleo de design, no molde dos 000009 e 000011. Produz no open-seja: (a) a referência normativa `plan-from-scenarios.md` (regras `PFS-NNN`: cabeçalho v2, campo `Scenarios:`, step de infraestrutura, cobertura nos dois sentidos, estado dos cenários, skip, compatibilidade); (b) um verificador **determinístico** `check_plan_scenarios.py` (sem LLM, biblioteca padrão) que lê o plano e o `scenarios.lock.json`, chama `check_specify.py --status` e devolve achados `PFS-NNN` com exit 0/1/2 e a matriz cenário→step em `--json`; (c) o texto de escrita do plano em `_internal/plan/standard/SKILL.md` (montar os steps a partir da lista de cenários aprovados, rodar o verificador, **recusar e corrigir** antes de salvar), o cabeçalho v2 em `plan/SKILL.md` (C3) e o campo em `plan-step.md`; (d) fixtures v1 e v2, válidas e inválidas, escritas antes do código; (e) um check condicional no `run_all_checks.py` e, se aprovado (Decisão pendente 4), uma parada mínima no `/implement`. Não implementa o teste vermelho (item 7), a métrica (item 8) nem a documentação (item 9).

### Formato final do plano v2 (decisão deste plano)

Cabeçalho (linhas logo após o título, até a primeira linha em branco; a ordem entre elas é livre, `source:` do C3 continua válido):

```
# Plan 000123 | FEATURE-O | 2026-11-01 10:00 UTC | login com bloqueio | Review: standard
plan_format_version: 2
Feature: login
Specify: approved (rev 2)
```

ou, para tarefa sem código (sem `Feature:`):

```
plan_format_version: 2
Specify: skipped -- tarefa sem código: só documentação
```

Step v2 (campo novo, depois de `Tests:`; obrigatório em **todo** step v2 quando `Specify: approved`):

```
- **Scenarios**: `login/login.feature::Entrar com senha correta`, `login/login.feature::Bloquear depois de 3 tentativas`
```
ou `- **Scenarios**: N/A (<motivo>)`. Chave = `<slug>/<arquivo>::<nome>`, entre crases, exatamente a do `scenarios.lock.json` (campo `index`). A tag `@REQ-...` **não** é aceita no lugar da chave (Decisão pendente 3). Seção opcional e gerada no fim do plano: `## Cobertura de cenários` (tabela cenário → step, saída do verificador; o parser não a lê).

Semântica: **`Scenarios:` lista os cenários cujo teste nasce neste step** (o step é o "dono": é nele que o item 7 transforma o cenário em teste vermelho e o leva a verde). Consequências, todas checadas:

| Situação do step | `Tests:` | `Scenarios:` | Resultado |
|---|---|---|---|
| Entrega comportamento observável | não-N/A | 1+ chaves | válido |
| Infraestrutura, migração, config, refactor com cobertura prévia | N/A | `N/A (motivo)` | válido; o motivo diz a que cenário serve (texto livre, p.ex. "tabela usada pelo cenário de login") |
| Comportamento sem cenário aprovado | não-N/A | `N/A (...)` ou ausente | **recusado** (PFS-006): ou entra um cenário (volta à specify) ou o `Tests:` vira N/A com justificativa |
| Chaves citadas, mas sem teste | N/A | 1+ chaves | **recusado** (PFS-008): o dono precisa ter teste |
| Chave que não está no lock (renomeada, retirada, inventada) | qualquer | chave inexistente | **recusado** (PFS-005) |
| Cenário aprovado que nenhum step cita | -- | -- | **recusado** (PFS-009, cobertura inversa) |

### Alternatives rejected
- Estender `critique_plan_coverage.py`: ele confere marcadores `REQ-TYPE-NNN` do `product-design/` contra `Traces:`, é consultivo e se cala sem marcadores. Cenário↔step é outro domínio, com saída bloqueante e dependência do lock; misturar os dois confunde o nome (`REQ-ENT` vs `REQ-login-001`) e enfraquece o modo consultivo. Rejeitado como default (Decisão pendente 1); o novo script só *convive* com ele (não o altera).
- Aceitar `@REQ-...` em `Scenarios:`: a tag cobre vários cenários e esconderia cenário sem step; o 000007 listou "`@REQ-...` ou nomes", mas 000010/000011 fixaram a chave. Rejeitado (Decisão pendente 3).
- Recusar todo step sem cenário, inclusive infraestrutura: força inventar cenário para migração e config, o que gera ruído (risco do roadmap). Rejeitado (Decisão pendente 6): infraestrutura passa com `N/A (motivo)` desde que o `Tests:` também seja N/A.
- Validar só no `/implement`: o erro apareceria depois da revisão do plano. Rejeitado: a recusa é no `/plan`, antes de salvar; o `/implement` só repete a parada (Decisão pendente 4).
- Deixar a cobertura inversa para o item 8: o relatório mediria a falta, mas o plano já nasceria incompleto. Rejeitado: cobertura nos dois sentidos aqui; o item 8 só mede.

**Selection rationale.** Sem `source:`. Fontes: roadmap-000006 (item 6, riscos "fricção" e "Gherkin vira ruído"), planos 000007 a 000011, roadmap-000062 (formato de plano e gate), research-000050 ("PASS is a tool result": aceitar plano é comando que sai 0), `product-design/constitution.md` (Q2: git é a recuperação) e `conventions.md`.

### Decisões fechadas (aprovadas pelo designer; não reabrir)
1. `plan_format_version: 2` com `Scenarios:` obrigatório; v1 (ou ausente) é válido para sempre e nunca recebe bloqueio.
2. Chave de cenário `<slug>/<arquivo>::<nome>`; Outline = um cenário.
3. Specify pulada por tipo de tarefa, registrada como `Specify: skipped -- <motivo>`; a grill nunca é pulada.
4. Layout `features/<slug>/{intent.md,*.feature,gate.json}` mais `scenarios.lock.json` (000011); teste-primeiro no `/implement`.
5. Estado `stale` do 000011 vale como "cenários não aprovados" para tudo que depende deles.

### Regras (resumo; o texto normativo é o Step 2)

| Regra | Conteúdo | Gravidade |
|---|---|---|
| PFS-001 | **Versão.** v1/ausente: o verificador sai 0 com `v1: não verificado` e não lê mais nada. v2: aplica as regras abaixo. Versão desconhecida: exit 2. | -- |
| PFS-002 | **Cabeçalho v2.** `Specify:` exatamente uma vez, no formato `approved (rev N)` ou `skipped -- <motivo>` (motivo não vazio). `approved` exige `Feature: <slug>` (kebab-case, pasta existente). `skipped` proíbe `Feature:`. | erro |
| PFS-003 | **Campo presente.** Com `Specify: approved`, todo step tem `Scenarios:`. | erro |
| PFS-004 | **Chave bem formada.** `<slug>/<arquivo>.feature::<nome>`, entre crases, slug igual ao `Feature:`, sem duplicata dentro do mesmo step. `@REQ-...` no lugar da chave gera dica. | erro |
| PFS-005 | **Chave existente.** A chave está em `index` do `scenarios.lock.json`. Renomeada ou retirada: erro com a dica "o cenário mudou de nome; veja Mudanças do intent.md". | erro |
| PFS-006 | **Step sem cenário.** `Tests:` não-N/A com `Scenarios:` ausente ou `N/A`. | erro |
| PFS-007 | **N/A justificado.** `N/A (motivo)` com motivo vazio ou de enchimento (`n/a`, `-`, `tbd`, `todo`, `...`) ou menos de 3 palavras. | erro |
| PFS-008 | **Dono precisa de teste.** Chaves citadas com `Tests: N/A`. | erro |
| PFS-009 | **Cenário sem step.** Cenário de `index` que nenhum step cita. Lista cada chave faltante. | erro |
| PFS-010 | **Dono único** [default; Decisão pendente 2]. Cenário citado por mais de um step. | erro (aviso se B) |
| PFS-011 | **Estado dos cenários.** `check_specify.py --status` deve devolver `approved`; `stale`, `draft` ou `missing` recusam, com a frase "os cenários estão desatualizados: refaça a specify". Sem `check_specify.py`: exit 2 (não dá para provar). | erro |
| PFS-012 | **Revisão.** `Specify: approved (rev N)` tem N igual ao `rev` do lock. Diferente: plano velho em relação à última aprovação. | erro |
| PFS-013 | **Skip coerente.** Com `Specify: skipped`, todo step tem `Tests: N/A` e `Scenarios:` ausente ou `N/A (...)`. Step com `Tests:` não-N/A: recusa com "a tarefa muda comportamento; rode a specify ou justifique o Tests: N/A". Fecha a lacuna do proxy (000011, lacuna 6). | erro |
| PFS-014 | **Todos N/A.** `Specify: approved` e nenhum step com chave: coberto por PFS-009; a mensagem sugere trocar para `skipped` só se `features/<slug>/` nunca teve cenário. | erro |
| PFS-015 | **Não faz.** Não altera o plano nem o lock; não mede divergência; não roda teste. | -- |

### Decisões pendentes
Cada uma tem default (a recomendação). Se o designer não responder, os steps seguem o default; mudar uma altera só o Step indicado.

**Decisão pendente 1 -- Onde mora a recusa executável** (afeta Steps 4, 5)
- Opção A: script novo `check_plan_scenarios.py`, que convive com `critique_plan_coverage.py`.
- Opção B: estender `critique_plan_coverage.py` com um modo `--scenarios`.
- Opção C: validar dentro do `/plan` por instrução, sem script.
- **Recomendação: A.** Recommended when se quer saída bloqueante, lock como entrada e o modo consultivo do outro script intacto. NOT recommended when o Step 1 mostrar que o `critique_plan_coverage.py` já tem parser de steps reutilizável de forma limpa (então B, importando só o parser). C rejeitada: "PASS é resultado de ferramenta, não frase".

**Decisão pendente 2 -- Um cenário pode ter mais de um step dono?** (afeta Steps 2, 4; o item 7 depende)
- Opção A: dono único (PFS-010 erro); os demais steps usam `N/A (motivo)`.
- Opção B: vários donos permitidos, com aviso; o item 7 decide quando o teste fica verde.
- **Recomendação: A.** Recommended when o item 7 precisa de um ponto único onde o teste vira verde por step, e um cenário dividido em camadas é sinal de step grande demais. NOT recommended when o piloto (item 10) mostrar cenários que atravessam camadas de forma natural (então B).

**Decisão pendente 3 -- Aceitar a tag `@REQ-...` na lista** (afeta Steps 2, 4; emenda ao texto do 000007)
- Opção A: só chaves de cenário.
- Opção B: tag aceita e expandida para todos os cenários do REQ.
- **Recomendação: A.** Recommended when se quer cobertura por cenário (D2 do 000008 mede por chave). NOT recommended when o citizen escreve planos à mão e acha a chave longa (então B, só como açúcar no `/plan`, que expande antes de salvar).

**Decisão pendente 4 -- O `/implement` repete a parada** (afeta Step 6; colide com o item 7 no mesmo `SKILL.md`)
- Opção A: sim, uma linha: plano v2 com `check_plan_scenarios.py` ≠ 0 não começa (v1 intocado).
- Opção B: não; o item 7 faz.
- **Recomendação: A.** Recommended when o 000007 já promete que o `/implement` para (sem corrigir) e o plano pode ter ficado velho depois de uma reaprovação (PFS-011, PFS-012). NOT recommended when o item 7 vai reescrever o preâmbulo do `/implement` logo em seguida (então B, e o item 7 herda a regra deste plano).

**Decisão pendente 5 -- Mais de uma feature por plano** (afeta Steps 2, 4)
- Opção A: um plano, uma feature (`Feature: <slug>`); a grill já propõe dividir.
- Opção B: lista (`Feature: a, b`; `Specify: approved (a rev 2, b rev 1)`).
- **Recomendação: A.** Recommended when se quer cabeçalho simples e uma aprovação por feature. NOT recommended when o piloto mostrar tarefas reais que atravessam duas features (então B, em plano próprio).

**Decisão pendente 6 -- Step de infraestrutura sem cenário** (afeta Steps 2, 4)
- Opção A: permitido com `Scenarios: N/A (motivo)` quando o `Tests:` também é N/A (default).
- Opção B: recusado; infraestrutura vira parte de um step com cenário.
- Opção C: permitido sempre, mesmo com `Tests:` não-N/A.
- **Recomendação: A.** Recommended when migração, config e refactor com cobertura prévia existem em quase todo plano e inventar cenário gera ruído. NOT recommended when o piloto mostrar `N/A` usado para fugir de cenário (então B para steps de código novo, medido pela fração de steps N/A). C rejeitada: reabre o buraco que o item fecha.

## Files

Todos no **open-seja**, exceto onde dito. O submodule não está inicializado neste worktree; caminhos **não verificados**: o Step 1 os confere antes de qualquer escrita. Itens "se existir" dependem de 000007, 000009 e 000011 já executados.

- `.claude/references/general/plan-from-scenarios.md` (create) -- protocolo normativo `PFS-NNN`
- `.claude/skills/scripts/check_plan_scenarios.py` (create)
- `.claude/skills/scripts/tests/test_check_plan_scenarios.py` (create)
- `tests/fixtures/plan_scenarios/` (create; caminho conforme o Step 1) -- planos v1/v2 e locks
- `.claude/references/template/plan-step.md` (modify) -- campo `Scenarios:` na forma final
- `.claude/skills/plan/SKILL.md` (modify) -- C3: cabeçalho v2 (`Feature:`, `Specify:`)
- `.claude/skills/_internal/plan/standard/SKILL.md` (modify) -- escrita do plano a partir dos cenários e recusa
- `.claude/skills/implement/SKILL.md` (modify, só se Decisão pendente 4 = A) -- uma linha de parada
- `.claude/skills/scripts/run_all_checks.py` (modify, condicional)
- `.claude/references/general/extended-cycle-contract.md`, `.claude/references/general/specify-phase.md` (modify, só ponteiro cada, se existirem)
- `_output/plans/plan-000012-progress.md` (create no Doutourado)

## Best practices

- Contrato primeiro: citar `CYC-NNN`, `SPC-NNN`, `GHK-NNN` reais; se não existirem no open-seja, marcar "a confirmar".
- "PASS is a tool result, not a sentence" (research-000050): plano v2 só é salvo com `check_plan_scenarios.py` saindo 0.
- Teste-primeiro também aqui: fixtures antes do script.
- Acoplar pela CLI e pelo JSON versionado (`check_specify.py --status`, lock com `schema_version`), nunca pelos internos dos outros scripts.
- Determinismo: ordem de saída estável, sem relógio, UTC; achados `arquivo:linha`, regra e dica; biblioteca padrão; funções puras separadas de CLI e I/O (standards.md § Backend 1, 4, 8, 19); `ruff` e `pyright` limpos no escopo do open-seja.
- Retrocompatibilidade por construção: v1 não é lido além do cabeçalho.

## Design decisions

- **User-visible impact:** depois de aprovar os cenários, você recebe um plano em que cada passo diz quais cenários entrega; se faltar cenário num passo, se sobrar cenário sem passo, ou se os cenários mudaram depois da aprovação, eu corrijo ou volto à specify antes de te mostrar o plano. Passos de infraestrutura continuam existindo, com o motivo escrito. Tarefa sem código segue sem cenário e o plano diz por quê.
- **Trade-offs accepted:** mais um script e mais um campo por step, em troca de cobertura nos dois sentidos checada por máquina; `N/A (motivo)` é texto livre e pode ser usado para fugir de cenário (medido no piloto); dono único pode forçar a divisão de um step grande.
- **Metacommunication impact:** I know you approved a list of scenarios; therefore I only give you a plan in which every approved scenario belongs to one step, and I tell you plainly when a step has no scenario or when the scenarios changed after you approved them, instead of going on with an old plan.

## Steps

### Step 1: Conferir o terreno e as dependências no open-seja
Na branch `dev` do open-seja (`git submodule update --init open-seja` se vazio), registrar no progress: (a) se os planos 000007, 000009 e 000011 já estão lá e os identificadores reais (`CYC-NNN`, `SPC-NNN`); (b) CLI real e JSON de `check_specify.py --status` e o esquema real de `scenarios.lock.json` (`rev`, `index`, `basis`, `schema_version`); (c) o texto atual de `plan-step.md` (forma do `Scenarios:` do 000007), de `plan/SKILL.md` (C3: onde está `plan_format_version`) e de `_internal/plan/standard/SKILL.md` (onde as fases grill e specify entraram; **quem escreve a linha `Specify: skipped`**: o 000009 e o 000011 citam a linha; registrar o ponto único); (d) se existe validador de formato de plano e como o `critique_plan_coverage.py` lê steps (regex, parser) para a Decisão pendente 1; (e) onde moram scripts, testes e fixtures e como `run_all_checks.py` registra check condicional; (f) se o nome do cenário pode conter crase ou `::` (o parser de `check_features.py`), para a regra PFS-004; (g) a lista de termos de C1. Se (a) faltar, escrever os Steps 2 a 8 contra o vocabulário dos planos do Doutourado e marcar cada identificador "a confirmar". Ordem de edição dos `SKILL.md` exigida: 000007 → 000009 → 000011 → este plano; se o 000011 ainda não executou, **parar** neste ponto e avisar o designer (os Steps 6 e 7 não podem ser executados sem a fase specify no texto). Nada é escrito no open-seja.
- **Files**: open-seja/.claude/references/general/extended-cycle-contract.md (read, se existir), open-seja/.claude/references/general/specify-phase.md (read, se existir), open-seja/.claude/references/template/plan-step.md (read), open-seja/.claude/skills/scripts/check_specify.py (read, se existir), open-seja/.claude/skills/design/critique_plan_coverage.py (read), open-seja/.claude/skills/plan/SKILL.md (read), open-seja/.claude/skills/_internal/plan/standard/SKILL.md (read), `_output/plans/plan-000012-progress.md` (create no Doutourado)
- **References**: product-design/conventions.md, product-design/constitution.md
- **Interface**: N/A
- **Verify**: o progress responde (a) a (g) com "existe", "rascunho" ou "ausente" e o caminho; registra o ponto único da linha `Specify: skipped`, a decisão sobre nomes com crase e as flags reais; `git -C open-seja status` limpo.
- **Tests**: N/A (verificação de estado)
- [x] Done

### Step 2: Escrever o protocolo normativo `plan-from-scenarios.md`
Criar o documento com as regras `PFS-001..015` da tabela acima, cada uma com "Quem decide" e "Critério de aceitação" (molde de `CYC-NNN` e `SPC-NNN`). Incluir: (1) o **cabeçalho v2 exato** (os dois exemplos acima, com as expressões regulares de `Feature:` e `Specify:` e a regra "linhas até a primeira linha em branco, ordem livre"); (2) o campo `Scenarios:` (sintaxe com crases, `N/A (motivo)`, semântica de "dono do teste") e a tabela das situações de step (acima); (3) como o `/plan` monta os steps: partir da lista `index` do lock, agrupar por camada, nunca deixar cenário fora, e quando um cenário não cabe em nenhum step, criar o step ou voltar à specify; (4) a regra de skip e o proxy: a grill classifica "com código/sem código" **antes** (decide se roda a specify) e o PFS-013 confere **depois** (decide se o plano é coerente), com a frase para o citizen; (5) estado `stale`: o que o `/plan` e o `/implement` dizem, e que reaprovar os cenários invalida o plano até ele ser atualizado (PFS-012), sem migração automática; (6) a **tabela de compatibilidade** (v1/ausente, v2 aprovado, v2 skipped, versão desconhecida, projeto sem `features/`, open-seja antigo sem o script); (7) o esquema da saída `--json` (`schema_version: 1`, `findings`, `matrix: [{scenario, steps: [n]}]`, `steps: [{n, tests, scenarios}]`); (8) a emenda ao texto do 000007 (`<@REQ-... | N/A>` vira só chave) para o designer colar via `/implement --manual`; (9) o que o plano **não** faz (PFS-015). Defaults das Decisões pendentes 1 a 6 marcados `[default; pendente]`. C1: sem nome de parceiro.
- **Files**: open-seja/.claude/references/general/plan-from-scenarios.md (create)
- **References**: product-design/constitution.md, product-design/standards.md § Testing, § Backend 8
- **Depends on**: Step 1
- **Interface**: regras `PFS-001..015`; esquema de `--json`; expressões regulares do cabeçalho e da chave.
- **Verify**: o arquivo existe; todo `PFS-NNN` tem "Quem decide" e "Critério de aceitação"; `grep -c "PFS-"` >= 15; a tabela de compatibilidade cobre os 6 casos; `git grep -ci` dos termos de C1 devolve zero; `python .claude/skills/scripts/run_all_checks.py` igual ao baseline do Step 1.
- **Tests**: N/A (documento normativo; a verificação mecânica é o Step 4)
- **Docs**: o próprio arquivo; o quickguide pt-BR fica para o item 9.
- [x] Done

### Step 3: Criar as fixtures golden de plano (teste primeiro)
Antes do código, criar em `tests/fixtures/plan_scenarios/` uma árvore por caso, todas fictícias, cada uma com `plan.md`, `features/<slug>/` mínimo (`intent.md` com `scenarios: approved`, `*.feature`, `scenarios.lock.json` com `rev`) quando couber, um `status` simulado do `check_specify` (arquivo `status.txt` lido por um stub passado ao teste; o script real é chamado só no Step 7) e `esperado.json` (`findings: [{rule, severity, line}]`, `exit_code`, `matrix`). Casos **válidos**: `v1-real-1` e `v1-real-2` (cópias de dois planos v1 antigos do open-seja, sem dado privado), `v1-minimo`, `v2-completo` (4 cenários; 5 steps: 3 com chaves, 1 de migração `N/A (tabela usada pelo cenário de login)`, 1 de refactor `N/A (...)`; `Specify: approved (rev 2)`), `v2-skipped` (documentação; todos `Tests: N/A`), `v2-outline` (Outline = uma chave). **Inválidos**, um disparo e um negativo por regra: PFS-001 (versão 3), PFS-002 (sem `Specify:`; `approved` sem `Feature:`; `skipped` com `Feature:`), PFS-003 (step sem o campo), PFS-004 (sem crases; `@REQ-...`; slug diferente), PFS-005 (cenário renomeado), PFS-006 (`Tests:` não-N/A com `N/A`), PFS-007 (`N/A (n/a)`), PFS-008 (chave com `Tests: N/A`), PFS-009 (cenário sem step), PFS-010 (cenário em dois steps), PFS-011 (`status` `stale`, `draft`, `missing`), PFS-012 (`rev 1` com lock `rev 2`), PFS-013 (`skipped` com step `Tests:` não-N/A). `README.md` com uma linha por caso.
- **Files**: open-seja/tests/fixtures/plan_scenarios/ (create; árvore de casos), open-seja/tests/fixtures/plan_scenarios/README.md (create)
- **References**: `.claude/references/general/plan-from-scenarios.md`
- **Depends on**: Step 2
- **Interface**: esquema de `esperado.json` (`findings`, `exit_code`, `matrix`).
- **Verify**: existe disparo e negativo para cada regra checável (script lista as regras citadas nos `esperado.json` e compara com a tabela do Step 2); `line` de cada achado conferida à mão; os planos v1 reais passam pela leitura antiga do `/plan` sem mudança; nenhum termo de C1 no diff.
- **Tests**: N/A (dados de teste; os testes que os usam são do Step 4)
- [x] Done

### Step 4: Implementar `check_plan_scenarios.py` (recusa nos dois sentidos)
Funções puras mais CLI: `check_plan_scenarios.py <plano.md> [--root <raiz>] [--json] [--table] [--strict] [--status-cmd <cmd>]`. `parse_plan(text) -> Plan` (cabeçalho, versão, `Feature`, `Specify`, steps de `## Steps` por `### Step N:`, campos `Tests` e `Scenarios` com chaves entre crases; ignora seções fora de `## Steps`), `check_plan(plan, lock, status) -> Report` aplicando PFS-001 a PFS-014 nesta ordem; `load_lock(root, slug)`; `scenario_status(root, slug)` chama `check_specify.py --status --feature <slug> --json` por **subprocesso** (acopla à CLI, não aos internos; `schema_version` desconhecido ou comando ausente = exit 2 com a mensagem "validador de cenários não encontrado"). Versão 1 ou ausente: devolve exit 0 depois de ler só o cabeçalho. `--table` imprime a tabela `## Cobertura de cenários` (cenário → step). Exit codes iguais aos do 000010/000011: `0` sem erro, `1` com erro (ou aviso com `--strict`), `2` uso incorreto, arquivo ilegível, validador ausente. Linha por achado `plano.md:57: PFS-006 erro: o passo 3 muda comportamento e não cita cenário. Dica: ...`, em voz controlada quando a mensagem vai ao citizen (limite de palavras do 000074, se existir). Sem LLM, sem rede, biblioteca padrão, ordem estável.
- **Files**: open-seja/.claude/skills/scripts/check_plan_scenarios.py (create), open-seja/.claude/skills/scripts/tests/test_check_plan_scenarios.py (create)
- **References**: product-design/standards.md § Testing, § Backend 8, 19, 20; product-design/constitution.md
- **Depends on**: Step 3
- **Interface**: `parse_plan(text: str) -> Plan`; `check_plan(plan: Plan, lock: dict | None, status: str | None) -> Report`; `Finding(rule, severity, file, line, message, hint)`; CLI acima; saída `--json` com `schema_version: 1` e `matrix`.
- **Verify**: `pytest .claude/skills/scripts/tests/test_check_plan_scenarios.py` verde sobre as fixtures do Step 3; `ruff check` e `pyright` limpos no escopo do open-seja (ou "n/a" registrado); duas execuções seguidas produzem saída idêntica; os 3 planos v1 saem 0 sem ler o corpo.
- **Tests**: when um plano é `plan_format_version: 1` ou sem a linha, returns exit 0 e nenhum achado; when um step v2 com `Tests:` não-N/A tem `Scenarios: N/A (x)` ou não tem o campo, returns PFS-006 com o número do step; when um cenário de `index` não aparece em nenhum step, returns PFS-009 com a chave; when um step cita chave que não está no lock, returns PFS-005; when um step cita chave e tem `Tests: N/A`, returns PFS-008; when `N/A (n/a)`, returns PFS-007; when o `status` é `stale`, returns PFS-011 e exit 1; when `rev` do cabeçalho difere do lock, returns PFS-012; when `Specify: skipped` e um step tem `Tests:` não-N/A, returns PFS-013; when o plano `v2-completo` é lido, returns exit 0 e a `matrix` tem cada cenário em exatamente um step; when `check_specify.py` não existe, returns exit 2 e a mensagem "validador de cenários não encontrado" (só para v2 aprovado); when um Outline é citado, returns uma chave só.
- **Docs**: cabeçalho do script com a tabela de regras e ponteiro para `plan-from-scenarios.md`.
- [x] Done

### Step 5: Registrar o check condicional no `run_all_checks.py`
Se o Step 1 mostrou ponto de registro limpo: acrescentar o check `plan-scenarios`, condicional, que roda `check_plan_scenarios.py` sobre cada plano em `_output/plans/` com `plan_format_version: 2` e reprova só nesses; sem plano v2, imprime `plan-scenarios: pulado`. Planos v1 nunca entram. Sem ponto limpo, registrar a lacuna no progress e marcar `N/A (lacuna registrada)`.
- **Files**: open-seja/.claude/skills/scripts/run_all_checks.py (modify), open-seja/.claude/skills/scripts/tests/test_check_plan_scenarios.py (modify)
- **References**: product-design/standards.md § Testing 6
- **Depends on**: Step 4
- **Interface**: entrada nova no registro de checks (nome `plan-scenarios`, condicional).
- **Verify**: `run_all_checks.py` num projeto sem planos v2 lista `plan-scenarios: pulado` com o mesmo conjunto de falhas pré-existentes do baseline; com a fixture `v2-completo` lista `ok`; com `PFS-009` lista `falhou`; `git diff --stat` só mostra os arquivos esperados.
- **Tests**: when `_output/plans/` só tem planos v1, returns `pulado` e os outros checks ficam idênticos ao baseline; when há um v2 válido, returns `ok`; when há um v2 com cenário sem step, returns `falhou` com o nome do check. Se não houver ponto limpo: `N/A (lacuna registrada)`.
- [ ] Done

### Step 6: Escrever o formato e a recusa nos `SKILL.md` e em `plan-step.md`
Ordem obrigatória de edição dos `SKILL.md` (conferida no Step 1): 76 (ponteiro) → 78 (grill) → 80 (specify) → **este passo**. (1) Em `plan-step.md`: forma final do campo (`**Scenarios**: ...` depois de `Tests:`, sintaxe com crases, `N/A (motivo)`, "dono do teste", só chave e nunca `@REQ-`), substituindo o texto provisório do 000007; (2) em `plan/SKILL.md`, C3: para plano de modo standard gerado depois da fase grill, `plan_format_version: 2` mais `Feature:` e `Specify:` (formatos exatos do Step 2); `--light` e roadmap seguem v1; (3) em `_internal/plan/standard/SKILL.md`: no passo de criar as seções, quando `Specify: approved`, montar os steps a partir de `index` do lock, preencher `Scenarios:` em todo step, e depois de salvar o rascunho e **antes** da revisão (passo 5) rodar `check_plan_scenarios.py` (corrigir sozinho até 3 vezes; persistindo, mostrar o achado em voz controlada e perguntar com AskUserQuestion, C4: voltar à specify / ajustar o plano); a validação de metadados do passo 5 ganha uma linha "Scenarios: presente e coerente com Tests"; sem `Feature:`/`Specify:` (grill sem código) escrever a linha `Specify: skipped -- <motivo>` **uma vez**, no ponto único definido no Step 1, e remover a duplicata do texto provisório do 000009/000011, se houver; plano `Specify: skipped` roda o verificador só para PFS-013; (4) se Decisão pendente 4 = A, em `implement/SKILL.md`, uma linha: plano v2 com `check_plan_scenarios.py` ≠ 0 não começa, sem corrigir (v1 intocado); (5) uma linha de ponteiro em `extended-cycle-contract.md` e `specify-phase.md`, se existirem. Não alterar a fase de revisão, o gate, hooks ou `settings`.
- **Files**: open-seja/.claude/references/template/plan-step.md (modify), open-seja/.claude/skills/plan/SKILL.md (modify), open-seja/.claude/skills/_internal/plan/standard/SKILL.md (modify), open-seja/.claude/skills/implement/SKILL.md (modify, condicional), open-seja/.claude/references/general/extended-cycle-contract.md (modify, só ponteiro)
- **References**: product-design/constitution.md, `.claude/references/general/plan-from-scenarios.md`
- **Depends on**: Step 4
- **Interface**: texto do C3 com o cabeçalho v2; passo "verificar cenários" entre salvar e revisar o plano.
- **Verify**: `git diff --stat` mostra só os arquivos listados; `grep -n "plan_format_version: 2" .claude/skills/plan/SKILL.md` acha o C3 novo e `plan_format_version: 1` continua nos modos `--light` e roadmap; `grep -n "check_plan_scenarios" .claude/skills/_internal/plan/standard/SKILL.md` acha a chamada entre salvar e revisar; `grep -c "Specify: skipped" ` no `standard/SKILL.md` = 1; `python .claude/skills/scripts/check_skill_system.py` e `run_all_checks.py` com resultado igual ao baseline; nenhum arquivo de gate, hook ou `settings` no diff.
- **Tests**: N/A (instruções de skill; a prova de comportamento é o Step 7)
- **Docs**: SKILL-quickguide do `/plan` fica para o item 9.
- [ ] Done

### Step 7: Provar o ciclo em três execuções de referência e a compatibilidade
Sobre as fixtures de feature do 000011 (lock real, gerado por `check_specify.py --approve`), executar `/plan` em modo descartável e registrar no progress, com a saída do verificador: (a) **feature com código**: o agente monta 5 steps, o primeiro rascunho tem um defeito proposital (um cenário sem step e um step de comportamento sem cenário), o verificador recusa com PFS-009 e PFS-006, o agente corrige e o plano final sai 0; (b) **tarefa sem código** (atualizar um README fictício): `Specify: skipped -- <motivo>`, nenhum `Scenarios:` necessário, PFS-013 passa; variante com um step `Tests:` não-N/A **recusada** pelo PFS-013; (c) **cenários reaprovados depois do plano**: a specify muda o `rev`/renomeia um cenário, o verificador devolve PFS-011 ou PFS-012 e PFS-005, e a atualização do plano volta a sair 0. Provar a compatibilidade: os 3 planos v1 das fixtures são lidos pelo `/plan` e pelo `/implement` como antes (comparar com o baseline do Step 1); `run_all_checks.py` sem `features/` e sem plano v2 devolve o conjunto do baseline; com o stub removido, a chamada real a `check_specify.py --status` funciona nas fixtures. Medir como calibração: número de correções automáticas antes de o plano passar, fração de steps `N/A` por plano, steps por cenário.
- **Files**: `_output/plans/plan-000012-progress.md` (modify no Doutourado), open-seja/tests/fixtures/plan_scenarios/ (modify), open-seja/.claude/skills/scripts/tests/test_check_plan_scenarios.py (modify)
- **References**: product-design/constitution.md, `.claude/references/general/plan-from-scenarios.md`
- **Depends on**: Step 5, Step 6
- **Interface**: N/A
- **Verify**: (a) e (c) terminam com exit 0 depois de falhar com a regra esperada; (b) sai 0 e a variante sai 1 com PFS-013; o progress traz correções automáticas, fração de `N/A` e steps por cenário; os planos v1 têm resultado igual ao baseline; nenhum termo de C1 no diff.
- **Tests**: when `check_plan_scenarios.py` roda sobre cada versão intermediária das execuções, returns o achado esperado (PFS-005, 006, 009, 011, 012 ou 013); sobre cada versão final, returns lista sem achados e `matrix` completa; com o `check_specify.py` real nas fixtures, returns o mesmo `status` que o stub. Reusa os testes do Step 4 com as execuções como entrada.
- [ ] Done

### Step 8: Fechar o contrato com os itens vizinhos
Registrar no progress a tabela "o que este plano entrega a quem": item 7 (o campo `Scenarios:` define o step dono; chave = a do lock; `check_plan_scenarios.py --json` dá a lista de cenários por step e o `Tests:` do step; PFS-010 garante um ponto verde por cenário), item 8 e plano 000008 (a `matrix` cenário→step fecha a coluna "step" do D1/D2; plano velho = PFS-011/012, nunca contado como coberto), item 9 (quickguide e `/help`: formato do cabeçalho, mensagens de recusa), item 10 (fração de steps `N/A` e correções automáticas como linha de base de fricção). Reexecutar `pytest`, `check_features.py --strict` e `run_all_checks.py`; conferir vocabulário contra 000007 a 000011 e C1 (`git grep -i` dos termos do Step 1 sobre o diff). Registrar as lacunas abaixo, as decisões pendentes que ficaram no default e os textos sugeridos ao designer via `/implement --manual`: (i) emenda ao `plan-step.md`/contrato do 000007 (chave no lugar de `@REQ-...`); (ii) esclarecimento do contrato (proxy do skip = classificação da grill, conferido por PFS-013).
- **Files**: `_output/plans/plan-000012-progress.md` (modify no Doutourado)
- **References**: product-design/constitution.md
- **Depends on**: Step 7
- **Interface**: N/A
- **Verify**: a tabela cobre os itens 7, 8, 9, 10 e o plano 000008, cada linha citando uma regra `PFS-NNN`; suíte verde; `run_all_checks.py` com o mesmo conjunto de falhas pré-existentes do baseline; `git diff --stat` dos arquivos de ponteiro mostra no máximo uma linha adicionada cada; zero termos de C1; o progress lista as 6 decisões pendentes com o default em uso.
- **Tests**: N/A (verificação final; a suíte dos Steps 4 a 7 é o teste)
- [ ] Done

## Coverage (advisory)

`product-design/product-design-as-intended.md` do Doutourado não tem marcadores REQ; `critique_plan_coverage.py` não se aplica e `Traces:` fica ausente. O plano executa no open-seja.

## Lacunas e conflitos com os planos 000007 a 000011

1. **Cabeçalho provisório do 000011.** O 000011 (Step 5) grava `Feature:` e `Specify: approved (rev N)` em plano v1, "o item 6 define o cabeçalho final". Este plano fixa o formato (regex no Step 2) e o torna v2; planos escritos antes (v1 com essas linhas) continuam v1 e não são verificados. Divergência é cosmética.
2. **Quem escreve `Specify: skipped`.** Os planos 000009 (Step 5, Verify procura "skipped") e 000011 (Step 5) citam a linha. Risco de duplicata no `standard/SKILL.md`; o Step 1 acha o ponto único e o Step 6 remove a duplicata (Verify: contagem = 1).
3. **Texto do 000007 sobre `Scenarios:`.** O 000007 diz "`@REQ-...` ou nomes de cenário"; os planos 000010/000011 fixaram a chave `<slug>/<arquivo>::<nome>`. Este plano aceita **só** a chave (Decisão pendente 3). Exige emenda ao `plan-step.md` e ao contrato (Step 6/8).
4. **Regra do 000007 era unidirecional.** "Tests não-N/A exige `Scenarios:`" não pega cenário sem step, chave inexistente, `N/A` sem motivo, nem chave com `Tests: N/A`. PFS-005 a PFS-010 completam; é extensão, não conflito.
5. **Proxy do skip (000011, lacuna 6).** Resolvida em duas pontas: a classificação da grill decide *antes*; o PFS-013 confere *depois*. Falta o 000007 dizer isso explicitamente (emenda de texto no Step 8). Caso borda: tarefa classificada "sem código" cujo plano acaba com `Tests:` não-N/A é recusada, não promovida automaticamente; o agente volta à grill/specify.
6. **Estado `stale` e `scenarios: approved` (000011, lacunas 1 e 4).** O plano usa `check_specify.py --status`, não o campo. O `check_features.py --matrix` (000010) continua lendo só o campo; o item 8 precisa fazer o mesmo. Registrado, não resolvido aqui.
7. **Reaprovação invalida o plano.** Se a specify é refeita (rename com linha em "Mudanças"), o plano fica com PFS-005/012 até ser atualizado à mão; não há migração automática de chaves. Aceito: a alternativa (reescrever planos) viola a regra de que o plano é artefato aprovado.
8. **`critique_plan_coverage.py`.** Seu "coverage" é de REQ do `product-design/` contra `Traces:`; o deste item é de cenário. Dois conceitos com o mesmo nome. Decisão pendente 1; a documentação deve distinguir ("rastreabilidade de design" vs "cobertura de cenários").
9. **`implement/SKILL.md` compartilhado com o item 7.** O 000007 só põe ponteiro lá; o item 7 reescreve o preâmbulo. A linha de parada (Decisão pendente 4) deve ser feita antes do item 7 ou herdada por ele.
10. **Chave com crase ou `::` no nome.** Se o parser do 000010 aceitar nomes assim, a lista com crases quebra. Step 1 verifica; se aceitar, emenda ao `check_features.py` (nova regra GHK) ou escape em PFS-004.
11. **Outline.** Uma chave por Outline: uma linha de `Examples` que falha não é distinguível no plano. É o custo da decisão fechada "Outline = um cenário".
12. **Fricção do citizen (risco do roadmap).** A recusa é invisível quando o agente corrige sozinho; só chega ao citizen se persistir após 3 tentativas. A fração de `N/A` e as correções automáticas (Step 7) calibram no piloto.
13. **Escrita concorrente nos mesmos `SKILL.md`.** Quatro planos tocam `plan/SKILL.md` e `standard/SKILL.md`; a ordem 76 → 78 → 80 → 81 é pré-condição (Step 1 pára se 80 não executou).

## Metacomm Intention
- **Summary**: I tell you that every step of the plan says which approved scenarios it delivers, that I refuse a plan in which a step has no scenario or a scenario has no step, and that I tell you when the scenarios changed after you approved them.
- **Source**: agent (technical plan; metacomm text kept for the report to the designer)

Metacomm contradiction check: nenhuma intenção existente em `product-design-as-intended.md` (D-001 a D-005) conflita; D-004 e D-005 (presets) ficam fora de escopo.

## Review log

**Review depth:** Standard (8 steps, ~14 arquivos distintos). Phase 1 inline (sem subagente; mesmo critério dos planos 000007 a 000011); sem Phase 2 (nenhum Deferred com risco de regressão não resolvido). Prefixo FEATURE-O sem linha na tabela de atalhos: usei DX, TEST, COMPAT, ARCH, SEC, UX.

### Step metadata validation
- Todo step tem Files, References, Interface, Verify, Tests, checkbox; `Depends on` só aponta para trás; nenhum step toca mais de 5 arquivos (Step 6 toca 5 com um condicional).
- `Tests:` não-N/A (Steps 4, 5, 7) expressam comportamento observável ("when X, returns Y").
- Caminhos do open-seja **não verificados** (submodule vazio): o Step 1 é o portão e pára se o 000011 não executou.
- `critique_plan_coverage.py` não existe neste repositório (vive no open-seja); sua leitura é do Step 1.

### Phase 1 -- Perspective scan

| Perspective | Status | Concern |
|---|---|---|
| DX | Adopted | Regras PFS com mensagem `arquivo:linha`, regra e dica; tabela de situações de step; `--table` para colar a cobertura. |
| TEST | Adopted | Fixtures antes do código (Step 3); disparo e negativo por regra; v1 reais como regressão; Steps 1, 2, 6, 8 documentais com `Tests: N/A` justificado. |
| COMPAT | Adopted | v1 válido para sempre e nunca lido além do cabeçalho; `--light` e roadmap seguem v1; check condicional "pulado"; versão desconhecida sai 2, não 1. |
| ARCH | Adopted | Acopla a `check_specify.py` pela CLI e pelo lock versionado; script novo separado do consultivo; sem LLM no verificador; gate e hooks intocados. |
| SEC | Adopted | C1 por `git grep` nos Steps 2, 3, 7, 8; fixtures fictícias; o verificador não escreve nada (PFS-015). |
| UX | Adopted | Correção automática antes de qualquer pergunta; mensagem em voz controlada só quando persiste; motivo de skip visível no plano. |
| PERF, DB, API, I18N, A11Y, VIS, RESP, DATA, OPS, MICRO | N/A | Sem superfície. |

### Riscos e lacunas registrados
- Caminhos, CLI de `check_specify.py` e esquema do lock não verificados (submodule vazio); Step 1 é o portão, com rota "a confirmar".
- `N/A (motivo)` é texto livre e pode virar fuga; medido no Step 7 e no piloto (item 10).
- Dono único (PFS-010) é palpite a calibrar.
- Lacunas 3, 5 e 6 exigem emendas ao 000007, ao 000010 e ao item 8; registradas, não resolvidas aqui.

### Execution Metrics
| Metric | Value |
|---|---|
| Review depth | Standard |
| Phase 1 perspectives | 6 adopted, 10 N/A |
| Phase 2 deep-dives | 0 |
| Iterations | 0 |
| Pending decisions | 6 (defaults A, A, A, A, A, A) |

## Outcomes

- `plan-from-scenarios.md`: formato final do plano v2 (cabeçalho `Feature:` / `Specify:`, campo `Scenarios:` com chaves de cenário, dono do teste, step de infraestrutura com `N/A (motivo)`), regras `PFS-001..015` e tabela de compatibilidade.
- `check_plan_scenarios.py`: recusa executável nos dois sentidos (step sem cenário e cenário sem step), estado `stale` e `rev` do 000011, coerência do skip, `matrix` cenário→step em `--json` para os itens 7 e 8.
- Texto do `/plan` (C3, escrita a partir dos cenários, verificação antes da revisão), `plan-step.md` e, se aprovado, parada mínima no `/implement`.
- Fixtures v1 e v2 válidas e inválidas, check condicional no `run_all_checks.py` e três execuções de referência.
- Planos v1 e projetos sem `features/` inalterados.
