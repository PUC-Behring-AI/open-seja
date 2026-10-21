# DONE | 2026-10-21 10:42 UTC |
# Plan 20261020-688kjs | REFACTOR-O | 2026-10-20 20:45 UTC | Linhagem sem Gherkin: base anterior, multi-dev portado e a escada dentro do plano com o jogo de linguagem | Review: deep
uid: 01M5DGKNMZVEZ3PNFZ15688KJS
plan_format_version: 2
Specify default: on
Specify: skipped -- opt-out: o plano remove a própria fase specify e os artefatos .feature

> Terceira forma deste plano (2026-10-20). A primeira removia o Gherkin arquivo a arquivo (cerca de 24 steps depois da revisão). A segunda voltava à base e portava o multi-dev e a camada PKB. Esta é a escolha do designer: base anterior ao Gherkin, **só o multi-dev portado**, sem a camada PKB, e a escada (intenção, requisitos, casos de uso, testes) **dentro do plano**, com o **jogo de linguagem** no lugar da grill. As formas anteriores estão resumidas em "Rumo anterior" e não são executadas.

## User brief

> quero planejar mudanças no open seja, a partir da minha reflexão recente sobre o gherking. quero remove-lo

Respostas do designer na conversa (2026-10-20):

- Motivo: "Contrato não é mensagem".
- Substituto do degrau cenário: "o proprio artefato do plano seja pode ser usado para colocar o conteúdo do intend.md + casos de uso + testes".
- Histórico: "Também reescrever H-009 e decisões" (override explícito de T3 e T4).
- Upgrade: "Aviso no upgrade".
- "AO INVÉS de seguir desta forma, porque não voltamos no tempo: olhamos as tags e continuamos de algum lugar de antes do gherking ? precisamos manter o multi dev".
- "eu gostei do experimento do jogo de linguagem. quero trocar o grill também. será que não é melhor somente pegar o multidev + escada requisito + use cases + testes no artefato gerado pelo plan ? acho que fica mais simples."
- Camada PKB: "eu instalei por fora no doutourado e já fiz algumas modificações. podemos remover do open-seja para simplificar".
- Entrega: "Um plano só".

## Intenção
- Objetivo: uma linhagem nova do open-seja, a partir de `2b17d27` (base anterior ao Gherkin, já com o design do multi-dev), com o ULID portado e um `/plan` que joga um jogo de linguagem com você e escreve no próprio plano a intenção, os requisitos, os casos de uso e os testes de cada requisito.
- O que você vê no fim: a branch `dev-sem-gherkin` com os testes verdes; o `/plan` abre com cenas, você aceita, recusa ou corrige, e o plano sai com `## Intenção`, `## Requisitos`, `## Casos de uso` e steps com `Covers:`; o `/implement` escreve um teste vermelho por requisito antes do código; nenhum `.feature`, `features/`, `intent.md`, `--specify` nem `SPECIFY_DEFAULT`; um upgrade que tira do cliente o que o v0.11.0 instalou do Gherkin e avisa sobre `features/` e sobre a camada PKB.
- Não faz: não reescreve nem apaga `dev`, `main`, a tag `v0.11.0` nem `origin` (só apensa a `dev` os commits de registro deste plano; o push é decisão sua); não porta a camada PKB nem o sinal as-expressed; não mede divergência por degrau (fica `não medido`); não mexe no Doutourado.
- Pronto quando: `pytest .claude/skills/scripts/tests/ tests/compat/` e `run_all_checks.py` passam na branch nova sem falha nova em relação à base; a busca de resíduos do Step 14 volta vazia; a decisão nova (D-006) está registrada por você; o que existia fica na tag `archive/gherkin-ladder-v0.11.0`.

## Agent interpretation

**Problema.** O Gherkin entrou como degrau da escada nos planos 7 a 15 e 22 (112 commits sem merge, 857 arquivos tocados) e a sua reflexão concluiu que ele trata um contrato como mensagem. A grill, que nasceu junto, pergunta onde você prefere reconhecer cenas. Remover para a frente custa cerca de 24 steps; portar tudo arrasta código escrito em cima do ladder.

**Abordagem.**

- **Base `2b17d27`.** É a ponta da branch do multi-dev antes do merge `8f8a601`; o `merge-base` dela com a linha do ladder é `6c3e41f` (`pre-plan-000007`). Fora de `_output/`, ela difere de `6c3e41f` só pela D-005 (ULID) no as-intended, e já traz reflection-000017, research-000018, a comunicação 21 e os textos dos planos 19 e 20. Nada de ladder em código.
- **ULID portado** (plano 19, steps 1 a 13 e correções). Fica de fora o step 14 (`04ecf9f`, parsers do ciclo default) e, à mão, a parte do step 11 (`d34c8ab`) que cita grill e specify. A decisão de ULID é a **D-005** na base; os textos portados citam "D-010" (renumeração do merge `a417a36`) e voltam a dizer D-005.
- **Sem PKB.** Nada do plano 20 é portado. No Doutourado, `pkb_inbox.py` e o post-skill têm o mesmo hash do v0.11.0: o upgrade não pode aposentar o `pkb_inbox.py`, e avisa que a etapa 7f do post-skill sai e precisa ficar como desvio local.
- **A escada no plano** (plano formato v3, para não colidir com o v2 do ladder que clientes ainda têm em `_output/`): o jogo de linguagem (hoje desvio local do Doutourado, `language-game-phase.md`, regras JDL) vira a entrevista do `/plan` e passa a ser dono da saída, da regra de parada e da aprovação; a saída vai para o plano, não para `intent.md`. Um verificador novo, `check_plan_intent.py`, confere o plano v3; planos v1 e v2 recebem "nada a verificar".
- **Upgrade.** `retired-files.json` com os arquivos do ladder que o v0.11.0 instalou, removidos só quando o hash é o do v0.11.0; aviso de `features/` e da PKB.
- **Execução.** O plano é v2 com ID ULID: o harness da base não o lê (o `/implement` da base cai para manual fora do v1, `implement/SKILL.md:134` em `6c3e41f`). Por isso o `/implement` roda **daqui**, em modo manual, com `dev` em checkout; o código, os testes e os scripts rodam com cwd no worktree; o progress é commitado em `dev`; no fim, o Step 15 leva o plano para a branch nova.

**Alternativas rejeitadas.** Remover para a frente (cerca de 24 steps); portar ULID e PKB (PKB arrasta 9 arquivos com conflito e você a mantém por fora); base `6c3e41f` (exige portar a pesquisa e reservar números de decisão); manter a grill com o jogo como desvio (você quer trocar); reusar `plan_format_version: 2` (colide com os planos v2 do ladder nos clientes).

## Design decisions

- **Impacto visível**: o `/plan` deixa de perguntar e passa a contar cenas; o plano carrega o que antes ia para `features/<slug>/`; o `/implement` cita o requisito no teste; os IDs são ULID.
- **Trade-offs aceitos**: perde-se, na linhagem nova, a história dos planos 7 a 15 e 22, a camada PKB, o as-expressed e a medida de divergência por degrau (ficam na tag); perde-se a granularidade por cenário. Ganha-se um harness pequeno e um único artefato por mudança.
- **Metacomunicação**: eu não lhe peço mais que aprove um contrato nem que formule requisitos de cabeça; eu lhe conto cenas, você reconhece ou recusa, e eu lhe devolvo em primeira pessoa o que entendi, dentro do plano. Quem lê código vê os testes.
- **Riscos**: (1) cerca de 15 arquivos de código com conflito ao portar o ULID; (2) o jogo de linguagem foi testado só no Doutourado, e a primeira versão das regras foi escrita pelo assistente; (3) dois clientes estão em v0.11.0 (um terceiro está em v0.9.1); num deles, o upgrade tira a etapa 7f do post-skill e o desvio do jogo de linguagem vira nativo; (4) override de T3 e T4 limitado ao Step 5; (5) os Steps 2 a 4 são lotes de `cherry-pick`: o campo Files lista só os arquivos resolvidos à mão.

## Best practices

Worktree estável fora do Doutourado (`~/worktrees/open-seja-sem-gherkin`); `cherry-pick -n -x` e, antes de commitar, restaurar do HEAD os arquivos append-only de `_output/` (`INDEX.md`, `briefs.md`, `briefs-index.md`, `pending.jsonl`, `telemetry.jsonl`, `conversation-trace.jsonl`); em conflito, ficar com a base e reaplicar só a mudança de ID; teste antes do código nos steps com `Tests:`; `pytest` e `run_all_checks.py` ao fim de cada step; nunca `push --force`, nunca `--no-verify`.

## Steps

> **Como rodar.** Antes do `/implement`, `dev` em checkout aqui. Rodar `/implement plan-20261020-688kjs --manual --skip-checks`: o harness daqui (v0.11.0) lê o plano, mas o código, os testes, o `apply_marker.py` e o `run_all_checks.py` rodam com cwd no worktree `~/worktrees/open-seja-sem-gherkin`, e os commits de código são feitos lá. O progress é commitado em `dev`, à parte. Recusar o `/explain drift` e o as-coded do post-skill em `dev` (mediriam a árvore errada). O `/critique review` roda no worktree, no Step 13. **Todo "pytest" abaixo** é `python3 -m pytest .claude/skills/scripts/tests/ --continue-on-collection-errors -q`, sem falha nem erro novo em relação ao baseline do Step 1 (na base: 2 erros de coleta de `generate_spo`, 8 falhas de `test_html_report` sem `markdown`, 4 de `test_summarize_artifacts`).

### Step 1: Preservar o ladder e abrir a linhagem nova
Criar a tag local `archive/gherkin-ladder-v0.11.0` em `bfac21f`. Criar o worktree `~/worktrees/open-seja-sem-gherkin` com a branch `dev-sem-gherkin` a partir de `2b17d27` (`git worktree add` grava em `.git/modules/open-seja`; `check_worktree_health.py` o marcará até a integração). No worktree, registrar no progress (em `dev`) o baseline: o pytest acima e `run_all_checks.py`, com as falhas próprias da base.
- **Files**: _output/plans/plan-20261020-688kjs-progress.md (modify)
- **References**: product-design/constitution.md (T3, Q1)
- **Interface**: N/A
- **Verify**: `git rev-parse archive/gherkin-ladder-v0.11.0` começa com `bfac21f`; `git -C ~/worktrees/open-seja-sem-gherkin rev-parse --abbrev-ref HEAD` é `dev-sem-gherkin`; o baseline está no progress.
- **Tests**: N/A (operação de git e registro de baseline)
- **Scenarios**: N/A (operação de git sem comportamento novo)
- [x] Done

### Step 2: Portar o núcleo do ULID (plano 19, steps 1 a 9)
No worktree, `cherry-pick -n -x` de `8dc3eb3` a `763bfb0` (9 commits, intervalo linear), restaurando do HEAD os append-only de `_output/` antes de cada commit. Conflitos reais (simulados na revisão): `tests/test_step_notes.py` (ficar só com o bloco do plano 19, step 7, sem os `test_pipeline_*` do ladder), `check_plugin_registry.json` (só a entrada de `check_ledger_ids.py`) e `CHANGELOG.md` (a entrada `[Unreleased]` do `763bfb0`, escrita já com **D-005**). Ao fim, no worktree: `pending.py done --source plan-000019 --type implement` (fecha a pa-000008) e `pending.py dismiss` da pa-000007 com o motivo "camada PKB não portada nesta linhagem".
- **Files**: .claude/skills/scripts/tests/test_step_notes.py (modify), .claude/skills/scripts/check_plugin_registry.json (modify), CHANGELOG.md (modify), .claude/skills/scripts/artifact_id.py (create), _output/pending.jsonl (modify)
- **References**: product-design/standards.md § Backend, § Testing
- **Depends on**: Step 1
- **Interface**: `artifact_id.new_uid()`; `reserve_id.py --type --title [--json]` devolve `{uid, id}`; `check_ledger_ids.py` sai 0 sem duplicata.
- **Verify**: pytest sem falha nova; `python3 .claude/skills/scripts/check_ledger_ids.py` sem erro; `pending.py status` sem pa-000007 nem pa-000008 abertas.
- **Tests**: when `reserve_id.py` roda duas vezes sem coordenação, devolve dois ULIDs diferentes e o nome de arquivo leva a data e seis caracteres; when dois artefatos têm o mesmo `uid`, `check_ledger_ids.py` sai 1 e cita os dois.
- **Traces**: D-005
- **Scenarios**: N/A (testes portados do plano 19, sem Gherkin)
- [x] Done

### Step 3: Portar as skills do ULID (plano 19, steps 10 a 13 e correções)
`cherry-pick -n -x` de `f720db0`, `e415c95`, `d9a47c4` e `2f44bbb`. `d34c8ab` entra à mão: só a troca da reserva de ID. Excluir `04ecf9f`. Conflitos reais: `plan/SKILL.md` e `_internal/explain/drift/SKILL.md` (os outros SKILL.md aplicam limpos). O `skills-manifest.json` não é editado: é regenerado por `generate_skills_manifest.py`, para não trazer `--grill`, `--specify`, `--with-specify` e `--pipeline`.
- **Files**: .claude/skills/plan/SKILL.md (modify), .claude/skills/_internal/explain/drift/SKILL.md (modify), .claude/skills/skills-manifest.json (modify)
- **References**: product-design/standards.md § Backend
- **Depends on**: Step 2
- **Interface**: N/A
- **Verify**: pytest sem falha nova; `python3 .claude/skills/scripts/check_skill_spec.py` sem achado novo; `grep -rnE -e "--grill|--specify|--with-specify|--pipeline|plan_format_version: 2|Scenarios:|(^|[^-])intent\.md|check_(intent|specify|features|plan_scenarios)|build_(brief|checks)|cycle_adherence|drift_report\.py|SPECIFY_DEFAULT" .claude/ docs/reference --exclude=CHANGELOG.md` não acha nada.
- **Tests**: N/A (skills em Markdown; cobertas pela suíte do Step 2 e por `check_skill_spec.py`)
- **Traces**: D-005
- **Scenarios**: N/A (skills em Markdown sem comportamento novo)
- [x] Done

### Step 4: Portar os textos do plano 19 em `_output/`
`cherry-pick -n -x` de `594a65b`, `2f3cffb` e `b630b6c` sem os append-only e **sem** o hunk de `product-design-as-intended.md` (ele põe um STATUS acima de `### D-010`, que na base é `### D-005`). `plan-000019-progress.md` conflita em todo commit desde `f720db0` (porque o `04ecf9f` pulado mexeu nele): apensar só as linhas novas. Nos hunks do `plan-000019-upgrade-…md`, manter D-005, como a base já diz. Apensar ao plano 19 a nota "Step 14 não portado nesta linhagem" e ao `plan-000019-qa-…md` (que cita D-010) a nota "nesta linhagem a decisão é a D-005". O STATUS da D-005 entra por `apply_marker.py --marker STATUS` (proposed, plan-000019), com cwd no worktree, depois da sua confirmação.
- **Files**: _output/plans/plan-000019-progress.md (modify), _output/plans/plan-000019-upgrade-multi-dev-identidade-por-ulid.md (modify), _output/plans/plan-000019-qa-upgrade-multi-dev-identidade-por-ulid.md (create), product-design/product-design-as-intended.md (modify)
- **References**: product-design/constitution.md (T3, T4)
- **Depends on**: Step 3
- **Interface**: N/A
- **Verify**: `python3 .claude/skills/scripts/check_ledger_ids.py` sem erro; `grep -n "STATUS" product-design/product-design-as-intended.md` mostra o marcador acima de `### D-005`; `check_human_markers_only.py --staged` sem prosa alterada.
- **Tests**: N/A (textos do ledger e um marcador)
- **Traces**: D-005
- **Scenarios**: N/A (textos do ledger sem comportamento)
- [x] Done

### Step 5: Fazer os scripts portados citarem a D-005
Trocar "D-010" por "D-005" onde a decisão de ULID é citada: `artifact_id.py:16`, `reserve_id.py:14`, `check_ledger_ids.py:14`, `generate_macro_index.py:21`, `human_markers_registry.py:74`. (`upgrade/SKILL.md:55` fica para o Step 12, que já o modifica.) Não tocar em `tests/test_explain_promote_phase3a_phase3b.py`: o "D-010" de lá é um exemplo de PostgreSQL, já na base.
- **Files**: .claude/skills/scripts/artifact_id.py (modify), .claude/skills/scripts/reserve_id.py (modify), .claude/skills/scripts/check_ledger_ids.py (modify), .claude/skills/scripts/generate_macro_index.py (modify), .claude/skills/scripts/human_markers_registry.py (modify)
- **References**: product-design/constitution.md (T3)
- **Depends on**: Step 4
- **Interface**: N/A
- **Verify**: `git grep -n "D-010" -- . ':(exclude)_output' ':(exclude).claude/skills/scripts/tests/test_explain_promote_phase3a_phase3b.py' ':(exclude).claude/skills/_internal/seja-setup/upgrade/SKILL.md'` não acha nada; pytest sem falha nova.
- **Tests**: N/A (troca de citação; a suíte é a verificação)
- **Traces**: D-005
- **Scenarios**: N/A (troca de citação sem comportamento)
- [x] Done

### Step 6: Registrar a D-006 e tirar o Gherkin do as-intended (designer, ponto de parada)
Ponto de parada: o texto é seu. O agente propõe em `_output/tmp/design-rascunho-d006-2026-10-20.md` e só grava com a sua confirmação no mesmo turno, cwd no worktree. Conteúdo: a D-006, "A escada vive no plano: jogo de linguagem, intenção, requisitos, casos de uso e testes por requisito; sem Gherkin, sem grill", que diz o que fica da D-004 (o citizen aprova a mensagem, não o contrato) e traz "não confundir com a D-006 da linhagem arquivada (uma pasta por feature)"; a D-004 recebe `STATUS: superseded` (a máquina de estados não tem "em parte"); H-009 reescrita para a escada no plano; as menções de Gherkin, grill e specify em §0, §2 (diagrama `*.feature`), glossário ("Escada de representações", "Degrau zero", "Contrato endereçável"), §8, §10, §14, §16, §17, SS-002, JM-TB-002, US-003, REQ-MC-011 a 013, Q-004 e Q-012. A REQ-MC-014 (preset `apprentice`) fica. Também `design-standards.md:24`. O override de T3 e T4 vai ao CHANGELOG.
- **Files**: product-design/product-design-as-intended.md (modify), product-design/design-standards.md (modify), _output/tmp/design-rascunho-d006-2026-10-20.md (create)
- **References**: product-design/constitution.md
- **Depends on**: Step 5
- **Interface**: N/A
- **Verify**: a decisão nova sai como D-006; `check_human_markers_only.py --staged` acusa só as linhas da reescrita autorizada, que você lista e aceita no mesmo turno; `grep -n -i -E "gherkin|\.feature|grill|specify|degrau zero|contrato endereç" product-design/*.md` só acha a D-006, a D-004 superseded e o CHANGELOG.
- **Tests**: N/A (documento de design)
- **Traces**: D-004, D-006
- **Scenarios**: N/A (decisão de design sem comportamento observável)
- [x] Done

### Step 7: Escrever a referência do jogo de linguagem como entrevista do `/plan`
Criar `general/plan-language-game.md` a partir da versão do jogo que hoje é desvio local de um cliente, autossuficiente: os lances (cena, contra-cena, e se, nomear, sua vez); as três respostas (aceito, recuso, corrijo); de onde vêm as cenas; rodada e cobertura **com as seis dimensões dentro** (antes na grill); o teste da surpresa; o jogo curto; e, trazidos da grill, o bom requisito, a voz e as três saídas no teto de 5 rodadas (continuar, aceitar como premissa, arquivar). Saem a regra "voltar à grill", a de registro do experimento, a menção a `Specify: skipped` e os links `[[…]]`. A citação "D-006" da fonte (numeração de outro repositório) vira D-004/D-006 daqui. Destino das respostas: aceito vira requisito ou caso de uso; recusado vai para "Não faz"; corrigido é citado em "Nas suas palavras". A referência declara que cada opção leva a justificativa curta da convenção (`constraints.md`), sem o rótulo `(Recommended)`. Exemplo genérico, sem nome de pessoa nem de instância (C2).
- **Files**: .claude/references/general/plan-language-game.md (create)
- **References**: product-design/constitution.md (C2), .claude/references/general/constraints.md
- **Depends on**: Step 6
- **Interface**: regras `JDL-001..JDL-0NN`; constantes `JOGO_MAX_LANCES_POR_RODADA = 3`, `JOGO_MAX_RODADAS = 5`.
- **Verify**: `grep -c -i -E "grill|GRL-|intent\.md|check_intent|specify|\[\[|doutourado" .claude/references/general/plan-language-game.md` é 0; inspeção de nomes de pessoas registrada no progress, sem escrever os nomes.
- **Tests**: N/A (referência; o Step 9 exercita a saída)
- **Docs**: a própria referência.
- **Traces**: D-006
- **Scenarios**: N/A (referência sem comportamento)
- [x] Done

### Step 8: Definir o plano v3 (intenção, requisitos, casos de uso, testes)
Criar `general/plan-intent-and-cases.md` com as regras PIC: header `plan_format_version: 3`; uma vez por plano, antes dos steps, `## Intenção` (4 linhas), `## Requisitos` (`REQ-<slug>-NNN` com slug **em minúsculas**, para não colidir com `REQ-[A-Z0-9]+-\d{3}` de `check_plan_coverage.py:214`; uma frase; "Para que"; origem `A<n>` do lance), `## Casos de uso` (um ou mais por requisito, em prosa e voz controlada), `## Retradução` (primeira pessoa, com "O que eu não vou fazer") e `## Nas suas palavras` (as respostas verbatim); por step, `Covers: REQ-…` só nos steps com `Tests:` diferente de N/A, e nunca dentro de `Traces:`. Atualizar `template/plan-step.md` e `general/report-conventions.md` (seções do plano).
- **Files**: .claude/references/general/plan-intent-and-cases.md (create), .claude/references/template/plan-step.md (modify), .claude/references/general/report-conventions.md (modify)
- **References**: product-design/standards.md § Backend
- **Depends on**: Step 7
- **Interface**: regras `PIC-001..PIC-0NN`.
- **Verify**: `grep -c "Covers:" .claude/references/template/plan-step.md` maior que 0.
- **Tests**: N/A (referência; o Step 9 a exercita)
- **Docs**: a própria referência.
- **Traces**: D-006
- **Scenarios**: N/A (referência sem comportamento)
- [x] Done

### Step 9: Criar `check_plan_intent.py`
Verificador do plano v3, só biblioteca padrão, `--json` com `schema_version`, saída 0/1/2. Interface `check_plan_intent.py [<plano>] [--json]`: **sem argumento** varre `_output/plans/` (o `run_all_checks.py` chama todo `check_*.py` sem argumentos) e sai 0 quando não há v3 com achado. Confere: as cinco seções presentes e não vazias; todo requisito tem caso de uso; todo requisito coberto por ao menos um step com `Covers:`; todo `Covers:` cita requisito existente; `Covers:` só com `Tests:` não-N/A; plano v1 ou v2 (ou sem versão) sai 0 com "nada a verificar". Registrar no `check_plugin_registry.json`.
- **Files**: .claude/skills/scripts/check_plan_intent.py (create), .claude/skills/scripts/tests/test_check_plan_intent.py (create), .claude/skills/scripts/tests/fixtures/plan_intent/ (create), .claude/skills/scripts/check_plugin_registry.json (modify)
- **References**: product-design/standards.md § Backend > 19
- **Depends on**: Step 8
- **Interface**: `check_plan_intent.py [<plano>] [--json]`; 0 sem achado, 1 com achado, 2 erro de uso.
- **Verify**: `python3 -m pytest .claude/skills/scripts/tests/test_check_plan_intent.py -q` verde; `run_all_checks.py` sem falha nova.
- **Tests**: when um plano v3 tem um requisito sem caso de uso, sai 1 e cita o requisito; when um step cita `Covers: REQ-x-009` que não existe, sai 1; when `## Casos de uso` está vazia, sai 1; when o plano é v1 ou v2, sai 0 com "nada a verificar"; when chamado sem argumento num diretório só com planos v1 e v2, sai 0; when tudo está coberto, sai 0 e o `--json` traz `schema_version`.
- **Traces**: D-006
- **Scenarios**: N/A (testes diretos do verificador, sem Gherkin)
- [x] Done

### Step 10: Pôr o jogo de linguagem e o plano v3 no `/plan`
No worker padrão (`_internal/plan/standard/SKILL.md`): passo novo antes da escrita do plano, que joga o jogo (`plan-language-game.md`) em rodadas, roda `check_plan_intent.py` depois de cada rodada até não haver `error`, mostra a Retradução e pede Aprovar / Ajustar / Descartar; o plano sai v3; na validação de metadata (step 5 do worker), `Covers:` só com `Tests:` não-N/A. Tarefa sem código: jogo curto (só `## Intenção`). `--light` continua v1 (proposal). Itens gerados por `--roadmap` usam o jogo curto, e o worker de roadmap diz isso. Atualizar o wrapper (C3 com v3), o quickguide e o `help`.
- **Files**: .claude/skills/_internal/plan/standard/SKILL.md (modify), .claude/skills/plan/SKILL.md (modify), .claude/skills/_internal/plan/roadmap/SKILL.md (modify), .claude/skills/plan/SKILL-quickguide.md (modify), .claude/skills/help/SKILL.md (modify)
- **References**: .claude/references/general/plan-language-game.md, .claude/references/general/plan-intent-and-cases.md
- **Depends on**: Step 9
- **Interface**: N/A
- **Verify**: `python3 .claude/skills/scripts/check_skill_spec.py` sem achado novo; `check_plan_intent.py .claude/skills/scripts/tests/fixtures/plan_intent/v3_completo.md` sai 0.
- **Tests**: N/A (skill em Markdown; a saída é coberta pelo verificador do Step 9)
- **Docs**: quickguide do `/plan`.
- **Traces**: D-006
- **Scenarios**: N/A (skill em Markdown)
- [x] Done

### Step 11: Fazer o `/implement` ler o plano v3 e testar por requisito
O `/implement` da base cai para manual fora do v1 (`implement/SKILL.md:134`). Novo comportamento: v1 como hoje; v3 com teste por requisito **nos dois modos, auto e manual** (para cada step com `Covers:`, o executor escreve primeiro um teste por requisito, que cita o ID no nome ou na docstring e fica vermelho pelo motivo certo, e só então o código até o verde). No modo manual, o v3 inverte a regra da base "manual mode retains test-after ordering by design" (passo 7 do modo manual): ela continua valendo só para v1; v2 avisa numa frase ("plano do ciclo com Gherkin: rodo em manual e ignoro Scenarios") e cai para manual; outro valor para. Atualizar `metadata.plan_format_version` do `/plan` e do `/implement`, e o quickguide.
- **Files**: .claude/skills/implement/SKILL.md (modify), .claude/skills/implement/SKILL-quickguide.md (modify)
- **References**: .claude/references/general/plan-intent-and-cases.md
- **Depends on**: Step 10
- **Interface**: N/A
- **Verify**: `python3 .claude/skills/scripts/check_skill_spec.py` sem achado novo; `grep -n "plan_format_version" .claude/skills/implement/SKILL.md` cita 1, 2 e 3. O passo 7 do modo manual diz que, em plano v3, o teste por requisito vem antes do código.
- **Tests**: N/A (skill em Markdown)
- **Traces**: D-006
- **Scenarios**: N/A (skill em Markdown)
- [x] Done

### Step 12: Fazer o upgrade limpar o que o v0.11.0 instalou e avisar
`retired-files.json` no padrão de `_RETIRED_SKILLS` de `upgrade_harness.py`, com os arquivos do ladder que o v0.11.0 instalou (nenhum existia em v0.10.1): scripts `check_intent.py`, `check_specify.py`, `check_features.py`, `check_plan_scenarios.py`, `build_brief.py`, `build_checks.py`, `cycle_adherence.py`, `drift_report.py`; referências `gherkin-spec-format`, `specify-phase`, `plan-from-scenarios`, `grill-phase`, `extended-cycle-contract`, `drift-metric`, `drift-control-protocol`, `drift-report`, `implement-test-first`; templates `feature-layout.md`, `intent.md`, `pilot-run-record.md`, `feature-example/`, `bdd/python/scenario_report.py.example`; agentes `scenario-tester`, `hardener`, `cleaner`; e, na raiz do cliente, `tests/scenario_report.py`. Remove só se existir e o hash for o de `git show v0.11.0:<path>` (árvore de distribuição); se não, mantém e diz `mantido (editado)`. **Não** aposentar `pkb_inbox.py`, `template/pkb/` nem `check_retired_tokens.py`. Avisos de uma frase: com `features/`, "O ciclo não lê mais features/ nem .feature; nada foi apagado no seu projeto."; com `PKB_DIR` preenchido, "A camada PKB saiu do harness: o post-skill não captura mais no inbox; guarde a etapa 7f como desvio local se quiser mantê-la." Em `upgrade/SKILL.md`, também trocar "D-010" por "D-005" (linha 55).
- **Files**: .claude/skills/scripts/upgrade_harness.py (modify), .claude/skills/scripts/retired-files.json (create), .claude/skills/scripts/tests/test_upgrade_harness.py (modify), .claude/skills/_internal/seja-setup/upgrade/SKILL.md (modify)
- **References**: product-design/standards.md § Testing
- **Depends on**: Step 5
- **Interface**: `retired-files.json`: lista de `{path, sha256_v0_11_0}`; o upgrade imprime `removido`, `mantido (editado)` e os avisos.
- **Verify**: `python3 -m pytest .claude/skills/scripts/tests/test_upgrade_harness.py -q` verde; `git grep -n "D-010" -- .claude/skills/_internal/seja-setup/upgrade/SKILL.md` vazio.
- **Tests**: when um cliente v0.11.0 tem `check_specify.py` idêntico ao do v0.11.0, o upgrade o remove e diz `removido`; when o cliente o editou, mantém e diz `mantido (editado)`; when o projeto tem `features/contas/`, a pasta fica byte a byte igual e a saída traz o aviso; when `PKB_DIR` está preenchido, `pkb_inbox.py` fica e a saída traz o aviso da PKB; when a lista é comparada com as adições de `.claude/` em `git diff v0.10.1 v0.11.0`, todo arquivo do ladder está nela.
- **Traces**: D-006
- **Scenarios**: N/A (testes diretos do upgrade, sem Gherkin)
- [x] Done

### Step 13: Criar `tests/compat` com um cliente v0.11.0 e um v0.10.1
`tests/compat/` não existe na base. Criar o runner e duas fixtures mínimas: um cliente v0.11.0 (com arquivos do ladder, `features/`, `PKB_DIR` e um arquivo do ladder editado) e um cliente v0.10.1. O teste roda o upgrade nos dois e confere o relatório.
- **Files**: tests/compat/run_upgrade_compat.py (create), tests/compat/test_upgrade_compat.py (create), tests/compat/fixtures/ (create)
- **References**: product-design/standards.md § Testing
- **Depends on**: Step 12
- **Interface**: `run_upgrade_compat.py <fixture>` devolve os arquivos removidos, mantidos e copiados.
- **Verify**: `python3 -m pytest tests/compat/ -q` verde.
- **Tests**: when o upgrade roda sobre o cliente v0.10.1, nenhum aviso aparece e nada é removido; when roda sobre o cliente v0.11.0, os arquivos do ladder idênticos saem, o editado fica, `features/` fica e os dois avisos aparecem.
- **Traces**: D-006
- **Scenarios**: N/A (testes diretos do upgrade, sem Gherkin)
- [x] Done

### Step 14: Fechamento: inventário, revisão, busca de resíduos e CHANGELOG
No worktree: atualizar `rules/harness-structure.md` e `docs/reference/harness-reference.md`; regenerar o `skills-manifest.json` (`generate_skills_manifest.py`); remedir `check_docs_skill_body_length_baseline.md` se os SKILL.md mudados estourarem. Rodar o pytest, `python3 -m pytest tests/compat/ -q`, `ruff check .claude/skills/`, `run_all_checks.py` e `/critique review` sobre `2b17d27..dev-sem-gherkin`; comparar com o baseline do Step 1. Busca de resíduos `gherkin|\.feature\b|scenarios\.lock|--specify|--grill|SPECIFY_DEFAULT|grill-phase|specify-phase|(^|[^-])intent\.md|check_(intent|specify|features|plan_scenarios)`, excluindo `_output/`, `CHANGELOG.md`, `.claude/CHANGELOG.md`, `retired-files.json`, `upgrade_harness.py`, `tests/test_upgrade_harness.py`, `_internal/seja-setup/upgrade/SKILL.md`, `tests/compat/fixtures/` e `product-design/product-design-as-intended.md` (conferido no Step 6). Entrada `v0.12.0` no `CHANGELOG.md` (Removed: Gherkin, grill, specify, camada PKB; Added: jogo de linguagem no `/plan`, plano v3, `check_plan_intent.py`, limpeza no upgrade; Changed: ULID como D-005). Os docs públicos de `docs/doc-*` que dizem "`plan_format_version` must be 1" ficam como pendência declarada. Propor a você nome, push e tag; não cortar tag nem dar push.
- **Files**: CHANGELOG.md (modify), .claude/rules/harness-structure.md (modify), .claude/skills/skills-manifest.json (modify), docs/reference/harness-reference.md (modify), .claude/skills/scripts/check_docs_skill_body_length_baseline.md (modify)
- **References**: product-design/constitution.md (Q1, Q4)
- **Depends on**: Step 11, Step 13
- **Interface**: N/A
- **Verify**: pytest e `run_all_checks.py` sem falha nova; `/critique review` sem achado crítico aberto; a busca de resíduos vazia.
- **Tests**: N/A (verificação final)
- **Traces**: D-006
- **Scenarios**: N/A (verificação final sem comportamento novo)
- [x] Done

### Step 15: Levar para a linhagem nova o plano que a criou
Copiar para o worktree e commitar em `dev-sem-gherkin`: este plano, o progress, o QA log e `_output/ids/01M5DGKNMZVEZ3PNFZ15688KJS.json`, para a D-006 e os commits "plan-20261020-688kjs step N" apontarem para um plano que existe na branch.
- **Files**: _output/plans/plan-20261020-688kjs-remover-gherkin.md (create), _output/plans/plan-20261020-688kjs-progress.md (create), _output/plans/plan-20261020-688kjs-qa-remover-gherkin.md (create), _output/ids/01M5DGKNMZVEZ3PNFZ15688KJS.json (create)
- **References**: product-design/constitution.md (T3)
- **Depends on**: Step 14
- **Interface**: N/A
- **Verify**: `git -C ~/worktrees/open-seja-sem-gherkin ls-files _output/plans | grep 688kjs` lista os três arquivos; `check_ledger_ids.py` no worktree sem erro.
- **Tests**: N/A (cópia de artefatos do ledger)
- **Traces**: D-006
- **Scenarios**: N/A (cópia de artefatos sem comportamento)
- [x] Done

## Outcomes
- Branch `dev-sem-gherkin`: base anterior ao Gherkin, ULID como D-005, `/plan` com jogo de linguagem e plano v3, `/implement` com teste por requisito, upgrade que limpa clientes v0.11.0.
- Tag `archive/gherkin-ladder-v0.11.0` preserva o ladder e a camada PKB; `dev`, `main` e `origin` não são reescritos.
- Os planos 7 a 16 e o roadmap-000006 que a base já traz em `_output/` ficam como estão (T3).
- Pendências declaradas: medida de divergência por requisito no `/reflect` (hoje `não medido`); a correção da base em que o upgrade copia só `.md` e `.json` de `template/` (`230955c` no ladder); o upgrade dos dois clientes em v0.11.0 depois da tag; os docs públicos de `docs/doc-*` que dizem "`plan_format_version` must be 1"; para outra rodada (decisão do designer, 2026-10-20): o portão com CRAP e mutação escrito explicitamente no ciclo v3, e a volta do `cleaner` (CRAP) e do `hardener` (mutação) sem Gherkin. O portão da base continua rodando como hoje.

## Rumo anterior (não executado)

1. **Remoção arquivo a arquivo** (15 steps): a revisão Deep achou o limite de 5 arquivos violado (o Step 10 com 16 itens), `build_checks.py` e `build_brief.py` importando módulos apagados, o plano v3 quebrando `check_plan_scenarios.py` antes da hora e uma busca final que nunca fechava; corrigido, ia a cerca de 24 steps. O desenho do plano v3 e do `check_plan_intent.py` volta aqui nos Steps 7 e 8.
2. **Voltar e portar ULID e PKB** (9 steps, base `6c3e41f`): a revisão Deep achou quatro bloqueantes (planos 7 a 16 já na base; numeração D-013 que sairia D-011; lista de aposentados incompleta; `tests/compat` inexistente). A segunda revisão do agente que escreve o plano achou uma base melhor (`2b17d27`), o problema de executar um plano v2 com ID ULID no harness da base, os clientes errados (dois em v0.11.0, um em v0.9.1) e o fim do experimento do jogo de linguagem no upgrade. Deste rumo valeram: a tag de arquivo, o `cherry-pick -n` com restauração dos append-only, a lista completa de aposentados com hash e o `tests/compat` mínimo.

## Smoke
smoke: false

## Review Log (terceira forma)

**Review depth:** Deep (`plan-reviewer`, 2026-10-20). Deep-dives 6/6; iteração 1 de 3; convergência por orçamento. O revisor fez o porte de verdade num clone no scratchpad (`cherry-pick -n -x` dos Steps 2 a 4 sobre `2b17d27`): 805 testes passaram contra 626 na base, com as mesmas 12 falhas e 2 erros de coleta; nenhum check novo falhou no `run_all_checks.py`; `check_ledger_ids.py` passa. O `/implement` do ladder aceita este plano (`check_plan_scenarios` 0 erros; `build_checks.py route` dá `no-scenario`/TDD v1). Perspectivas: COMPAT, TEST, OPS, ARCH, DX, UX e DATA, todas resolvidas por emenda; SEC, PERF, DB, API, I18N, A11Y, VIS, RESP e MICRO N/A.

| Emenda | O que mudou |
|---|---|
| A1 | Step 2: conflitos reais são `test_step_notes.py`, `check_plugin_registry.json` e `CHANGELOG.md` (não `step_notes.py`); CHANGELOG já com D-005; fecha pa-000008 e dispensa pa-000007 |
| A2 | Step 3 dividido em 3 (skills) e 4 (textos do plano 19); manifesto regenerado; STATUS da D-005 por `apply_marker.py` (o `b630b6c` o punha sobre um `### D-010` inexistente) |
| A3 | Step 5: lista de D-010 confirmada (5 scripts; `upgrade/SKILL.md` vai ao Step 12); só o QA log novo do plano 19 cita D-010, o resto da base já diz D-005 |
| A4 | Verify executáveis: pytest com `--continue-on-collection-errors` contra o baseline (a coleta da base quebra em `generate_spo`); `check_plan_intent.py` sem argumento varre `_output/plans/`; Verify do `/plan` por fixture; exclusões da busca final |
| A5 | v3 completo: slug minúsculo; `Covers:` fora de `Traces:`; `--light` v1; roadmap com jogo curto; v2 avisa e cai para manual no `/implement` |
| A6 | Execução em modo manual, cwd no worktree, `/critique review` no worktree; Step 15 leva o plano para a branch nova |
| A7 | C2 (sem nomes de pessoas nem de parceiro); D-006 com desambiguação; D-004 `superseded`; REQ-MC-014 (apprentice) fica |
| A8 | Referência do jogo autossuficiente: seis dimensões, bom requisito, voz e saídas do teto trazidos da grill; regras de instância removidas |

### Execution Metrics

| Metric | Value |
|--------|-------|
| Deep-dives used | 6/6 |
| Iterations completed | 1/3 |
| Perspectives shortlisted | 7 |
| Perspectives Adopted | 0 |
| Perspectives Deferred (with rationale) | 7, resolvidas por emenda |
| Convergence reason | deep-dive budget |

## Implementation summary (2026-10-21)

- Modo manual, rodado daqui (dev) com código, testes e commits no worktree `~/worktrees/open-seja-sem-gherkin`, branch `dev-sem-gherkin` (base `2b17d27`). Steps: 15/15. Tag local `archive/gherkin-ladder-v0.11.0` em `bfac21f`.
- Portado: núcleo e skills do ULID (plano 19, steps 1 a 13 e correções, sem o step 14), com D-005 em scripts, CHANGELOG e textos; STATUS da D-005 por apply_marker; pa-000008 fechada e pa-000007 dispensada no worktree.
- Design (Step 6, com override de T3/T4 aceito pelo designer): D-006 registrada, D-004 superseded, H-009 reescrita e seções derivadas.
- Novo: `general/plan-language-game.md` (JDL-001..011), `general/plan-intent-and-cases.md` (PIC-001..009), `check_plan_intent.py` (com `--phase game`), passo 2b do `/plan`, `/implement` com plano v3 e teste por requisito nos dois modos, `retired-files.json` e a limpeza no upgrade (inclui desligar o plugin do conftest), `tests/compat/`.
- Verificação final no worktree: pytest 852 passando, com as mesmas 12 falhas e 2 erros da base; `tests/compat/` 8 passando; `run_all_checks.py` sem check novo falhando; ruff limpo nos arquivos novos (achados novos só nos arquivos do ULID portados, de estilo).
- `/critique review` (standard): 3 críticos corrigidos (C1 lista de aposentados lida da release e upgrade roda o script da release; C2 fase do jogo no verificador e Retradução curta no jogo curto; C3 plugin sai do conftest), advisórios A1, A3, A4 e A5 corrigidos; A2, A6, A7 e A8 diferidos.
- Diferidos e pendências: A2 (linha `nenhum (` desliga as regras de requisito em qualquer plano); A6 (plano sem versão: manual no `/implement`, "nada a verificar" no verificador); docs públicos `docs/doc-*` que dizem `plan_format_version` must be 1; medida de divergência por requisito no `/reflect`; portão com CRAP e mutação no v3 e volta do cleaner e do hardener; upgrade dos clientes depois da tag; remover o worktree auxiliar da base criado no scratchpad. Nome, push e tag da linhagem: decisão do designer.

## Reflection

- 2026-10-21: Os Steps 2 a 4 conflitaram onde a revisão do plano previa; o Step 6 parou para o designer e acusou 86 linhas aceitas; o Step 9 e o Step 13 tiveram testes depois de olhar a saída real; a revisão do Step 14 achou três críticos (upgrade lendo a lista errada, verificador incompatível com o jogo, plugin no conftest) que os testes não pegavam. (notes 17, with deviation 17, with gate 0)
