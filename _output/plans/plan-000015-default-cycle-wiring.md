# Plan 000015 | FEATURE-O | METACOMM | 2026-10-05 12:55 UTC | default-cycle-wiring: integração do ciclo default (freeze do M1, reconciliação da grill, checks, /help e guias pt-BR, upgrade por tag) | Review: deep

> **Origem**: movido do ledger do Doutourado em 2026-10-05 (proposal-000088; la era `plan-000084`). Os IDs roadmap-000006 e plan-000007..000016 sao deste ledger (tabela no roadmap). Referencias a research-NNNNNN, reflection-NNNNNN, communication-NNNNNN, roadmap-000062 e plan-000064..000074 apontam para o ledger do Doutourado (repositorio do pesquisador). Caminhos `open-seja/...` em Files passam a ser relativos a raiz deste repositorio.
plan_format_version: 1

> Item 9 do roadmap-000006 (Wave 4; Depends on: implement-test-first-build = plan-000013, reflect-drift-report = plan-000014). Repositório de execução: **open-seja** (worktree/branch por plano); o plano vive no Doutourado. C1: nenhum nome de parceiro nos artefatos que forem ao open-seja. Este plano não edita o roadmap nem `_output/INDEX.md`, não publica, não faz push e não edita hooks já entregues.

## Designer's metacommunication message (verbatim)

> Item 9 do roadmap-000006: `default-cycle-wiring` (Depends on: implement-test-first-build, reflect-drift-report). "/help e quickguides pt-BR, upgrade por tag sem quebrar projetos existentes, run_all_checks."
>
> DECISÕES APROVADAS (fechadas, incluindo recomendadas de 76-83): fases internas ao /plan e invocáveis avulsas; plan_format_version 2 com v1 válido para sempre; layout features/<slug>/; sem preset, modo default; --pipeline opt-in; divergência composta por degrau.
>
> Este item é a INTEGRAÇÃO e deve absorver o que os planos anteriores deixaram "para o item 9" (leia as seções de Lacunas): (a) congelar M1: fiação do `/implement` chamando `--freeze` do 83 ao fim e emenda aditiva ao feature-layout.md para a pasta `features/<slug>/drift/` e o scenarios.lock.json; (b) reconciliar `scenarios: approved` no disco quando a grill reabre (sem depender só do --status); (c) `check_features --matrix` e consumidores usando `check_specify.py --status`; (d) consolidar a ordem de edição dos SKILL.md (76→78→80→81→82→83→84) e o limite skill-body-length; (e) emenda ao texto do 76 sobre `Scenarios:` (chave `<slug>/<arquivo>::<nome>`) e ao proxy do skip; (f) `/help` e quickguides pt-BR (voz controlada, diagrama da escada intenção→cenário→teste→código), upgrade por tag (retrocompatibilidade provada em projetos existentes e v1), registro de todos os novos checks no `run_all_checks` (condicionais a features/), D-NNN/H-009 coerentes; (g) o follow-up dos hooks do 68 (Stop hook com árvore vermelha em escalada) se couber, sem editar hooks já entregues sem decisão pendente.

## Agent interpretation

**Problem.** Os planos 000007 a 000014 definem cada peça do ciclo default (contrato, métrica, grill, validador de Gherkin, specify, plano por cenário, teste-primeiro, relatório de divergência), mas cada um deixou de fora a **costura**: quem congela o M1 e onde, o campo `scenarios: approved` que fica mentindo quando a grill reabre, os consumidores da matriz que ainda leem só o campo, a ordem em que seis planos editam os mesmos `SKILL.md`, o texto do 000007 que diverge da chave de cenário fixada depois, e o fato de nenhuma peça ter sido provada num **projeto que já existe** ao receber a nova tag. Sem esta integração, o ciclo é um conjunto de arquivos corretos que não formam um modo default, e o roadmap-000006 lista "mudança no core" como risco.

**Approach.** Plano técnico com núcleo de integração, no molde dos 000009 a 000014. Produz no open-seja: (a) emendas **aditivas** ao contrato, ao layout e ao formato de plano (Steps 2); (b) dois ajustes pequenos e testados nos validadores já entregues, `check_specify.py --reconcile` e `scenarios_state` na matriz (Steps 3 e 4); (c) a fiação `/implement` -> `--freeze` do M1 (Step 5); (d) o registro condicional dos checks novos no `run_all_checks` e um teste agregado (Step 6); (e) a ordem consolidada de edição dos `SKILL.md`, a medição final do `skill-body-length` e o ajuste do que estourar (Step 7); (f) `/help`, guia pt-BR em voz controlada com o diagrama da escada, e ponteiros nos quickguides (Step 8); (g) a prova de upgrade por tag em projetos existentes e v1, mais versão e CHANGELOG preparados **sem publicar** (Step 9); (h) H-009 e as D-NNN coerentes entre os oito planos (Step 10); (i) a decisão sobre o follow-up dos hooks e o ensaio de ponta a ponta que fecha o item e alimenta o piloto (Step 11). Nada aqui reimplementa uma peça: cada step chama o que os itens 1 a 8 entregaram.

**Alternatives rejected.**
- Um preset ou chave de ativação (`EXTENDED_CYCLE=on`) para proteger projetos existentes: contradiz a decisão fechada "sem preset, modo default"; a proteção vem de a nova tag **só agir quando há `features/` ou plano v2** e de `--light`/tipo de tarefa continuarem como saída (Step 9 prova isso).
- Reescrever planos v1 ou `scenarios: approved` antigo no upgrade (migração automática): viola "v1 válido para sempre" e a regra de que o plano é artefato aprovado.
- Editar o Stop hook agora para o "vermelho em curso" (000013, lacuna 9): os hooks do 000068 estão entregues e não há medição ainda; vira decisão pendente 7 com gatilho de medição.
- Um agregador `check_default_cycle.py` que chama os quatro validadores: o `run_all_checks` descobre `check_*.py` por glob e os quatro já seriam executados sozinhos (ver lacuna 5); o agregador duplicaria a execução (decisão pendente 8).
- Traduzir os `SKILL-quickguide.md` no lugar: os quickguides do harness público são em inglês e o carregador (`load_quickguide.py`) lê um único arquivo por skill; traduzir mudaria o contrato do carregador (decisão pendente 4).

**Selection rationale.** Sem `source:`. Fontes: roadmap-000006 (item 9, riscos "fricção do citizen" e "mudança no core", H-009), roadmap-000062 (H-008, item 11 / plan-000074), research-000050 (§10, encaixe no open-seja), planos 000007 a 000014 (seções "Lacunas e conflitos" e Steps que citam "item 9"), constitution.md (T2, T3, Q1, Q2, S1, C1) e conventions.md. Toda lacuna que os planos anteriores deixaram "para o item 9" entra como step; as que pedem decisão do designer entram como "Decisão pendente".

### Decisões fechadas (não reabrir neste plano)
1. Fases grill e specify são internas ao `/plan` e também invocáveis avulsas (`--grill`, `--specify`).
2. `plan_format_version: 2` exige `Scenarios:` por step com `Tests:` não-N/A; v1 (ou ausente) é válido para sempre e nunca é migrado.
3. Layout `features/<slug>/` (`intent.md`, `*.feature`, `gate.json`, `scenarios.lock.json`, e agora `drift/`).
4. Sem preset e sem perfil: modo default do SEJA, igual para citizen e power dev. `apprentice` (D-004) e `literature-reviewer` (D-005) ficam fora.
5. `--pipeline` (Cleaner, Hardener) é opt-in no `/implement`.
6. Divergência composta, reportada por degrau (D1, D2, D3a, D3b), sem número único.
7. Gate (plan-000065) e hooks (plan-000068) são consumidos, não reconstruídos; nenhum hook é editado aqui.
8. Este plano não escreve em `product-design/` do Doutourado, não edita roadmap nem INDEX e não publica release.

### Decisões pendentes
Cada uma tem default (a recomendação). Se o designer não responder, os steps seguem o default; mudar uma decisão altera só os Steps indicados.

**Decisão pendente 1 -- Quem congela o M1 e quando** (afeta Steps 2, 5, 11; lacuna 2 do 000014)
- Opção A: o `/implement` chama `drift_report.py --freeze` **uma vez, ao fim do plano v2**, depois da rodada `full` do 000013 (ou com `full: null` se ela foi pulada), e só quando o plano tem `Feature: <slug>`.
- Opção B: o `/reflect` congela na primeira execução depois do IMPLEMENT.
- Opção C: o designer roda `--freeze` à mão.
- **Recomendação: A.** Recommended when o M1 precisa ser o estado "fim do IMPLEMENT" e o agente que implementou ainda tem o contexto (000008: "M1 = matriz congelada com o gate"). NOT recommended (B) when o `/reflect` roda dias depois, com a árvore já mudada: o M1 deixaria de ser M1. NOT recommended (C) when o piloto precisa de dados comparáveis: depende de memória humana. Falha de `--freeze` (por exemplo, M1 já existe, regra de recusa do 000014) **não** reprova o `/implement`: avisa e segue.

**Decisão pendente 2 -- Grill reaberta: o que acontece com `scenarios: approved` no disco** (afeta Steps 2, 3, 4; lacunas 1 e 4 do 000011, lacuna 3 do 000014)
- Opção A: `check_specify.py --reconcile` (chamado pela grill ao reabrir, e por quem detectar `stale`) reescreve `scenarios: approved` para `scenarios: draft` e **mantém** o lock; `--status` continua a dizer `stale` com o motivo. Consumidores seguem consultando `--status` (cinto e suspensório).
- Opção B: a reconciliação grava um valor novo, `scenarios: stale` (exige que os leitores do 000010 e do 000011 aceitem o valor).
- Opção C: não gravar nada; só consumidores consultam `--status`.
- **Recomendação: A.** Recommended when o campo precisa dizer a verdade para quem lê o arquivo sem rodar script (revisão no GitHub, Obsidian) e `draft` já é valor aceito pelos leitores. NOT recommended (B) when isso obriga emenda aos esquemas dos 000009/000010/000011 só para um valor a mais. NOT recommended (C) when o designer pediu explicitamente "sem depender só do --status". Escrita só no `intent.md` da feature indicada, atômica, idempotente.

**Decisão pendente 3 -- Saída do ciclo para quem não quer a escada** (afeta Steps 8, 9; risco "fricção do citizen")
- Opção A: nenhuma chave nova. A saída é a que já existe: `--light`, prefixos DOCUMENT/CHORE/RESEARCH e steps só de config (`Specify: skipped -- <motivo>`), e `--roadmap` (planos v1) para o item de roadmap que não tem comportamento observável.
- Opção B: variável em `conventions.md` (`CYCLE_MODE: extended|standard`) lida pelo `/plan`.
- Opção C: flag `--no-grill` por invocação.
- **Recomendação: A.** Recommended when a decisão fechada é "modo default, sem preset": uma chave global vira preset por outro nome e o piloto (item 10) perderia o controle limpo. NOT recommended (B/C) when o objetivo é medir H-009: um desvio sem registro contamina a medida. O braço de controle do piloto usa a **tag anterior pinada**, não uma chave.

**Decisão pendente 4 -- Forma do guia e dos quickguides em pt-BR** (afeta Step 8)
- Opção A: arquivos irmãos `SKILL-quickguide.pt-BR.md` por skill e parâmetro opcional `locale` em `load_quickguide.py`.
- Opção B: **um guia** `docs/how-to/ciclo-default.pt-BR.md` (voz controlada, com o diagrama da escada) mais **uma linha de ponteiro** em cada quickguide afetado (`plan`, `implement`, `reflect`, `explain`, `help`) e uma entrada "Ciclo default" no `/help`.
- Opção C: seção "Em português" dentro de cada `SKILL-quickguide.md`.
- **Recomendação: B.** Recommended when o harness é público e em inglês, o carregador lê um arquivo por skill e o diagrama da escada precisa de um lugar só. NOT recommended when o designer quer `/help <skill>` inteiramente em pt-BR por skill (então A, com custo de carregador, `check_docs` e cinco arquivos a manter). C engorda o corpo lido por `pre-skill`.

**Decisão pendente 5 -- Número da versão** (afeta Step 9)
- Opção A: bump **minor** (próxima minor após a tag corrente do open-seja, lida no Step 1).
- Opção B: patch.
- Opção C: major.
- **Recomendação: A.** Recommended when muda o comportamento default de `/plan`, `/implement` e `/reflect` sem quebrar planos nem estrutura (v1 válido, estruturas só lidas quando existem). NOT recommended (B) when o texto do CHANGELOG precisa avisar o usuário do novo default. NOT recommended (C) when nada é removido nem incompatível. A **publicação** (`/publish`, tag, npm) fica com o designer, fora deste plano.

**Decisão pendente 6 -- Plugin pytest do 000013 no `/seja-setup`** (afeta Step 9; lacuna 15 do 000013)
- Opção A: continua sob demanda (`install-plugin` no primeiro vermelho); o upgrade **não** instala nada novo.
- Opção B: install e upgrade oferecem o plugin em projeto Python com `features/`.
- Opção C: A, mais: o upgrade **atualiza** o plugin e o `conftest` se já estiverem instalados (idempotente, sem tocar em arquivos alterados à mão: mostra diff e pergunta).
- **Recomendação: C.** Recommended when o upgrade não pode criar arquivo em projeto que não pediu o ciclo, mas também não pode deixar o plugin velho contra um validador novo. NOT recommended (B) when o projeto não é Python. NOT recommended (A) when o plugin instalado já divergiu do `check_features.py` (a chave do cenário é calculada nos dois lados).

**Decisão pendente 7 -- Follow-up do Stop hook com árvore vermelha em escalada** (afeta Step 11; lacuna 9 do 000013)
- Opção A: sem mudança de hook agora. Documentar o efeito (o `Stop` pode barrar até 3 vezes a pausa entre RED e GREEN) no guia e medir no ensaio e no piloto.
- Opção B: abrir plano de follow-up no 000068 para um marcador "vermelho em curso" (por exemplo, arquivo de estado escrito pelo `/implement` entre RED e GREEN, lido pelo hook), com os mesmos limites de segurança (o hook não é sandbox).
- Opção C: ignorar.
- **Recomendação: A, com gatilho para B.** Recommended when não há medição real ainda e os hooks estão entregues e testados (72 testes). O Step 11 registra a medição do caso (i) do 000013 e escreve o **rascunho de brief** do follow-up B no progress; vira plano só se houver barramento medido em mais de um step por feature. NOT recommended (C) when o citizen pode ver "bloqueado" no meio do vermelho sem entender: é o risco de fricção do roadmap.

**Decisão pendente 8 -- Como os checks novos entram no `run_all_checks`** (afeta Step 6; lacuna 5)
- Opção A: cada `check_*.py` (`check_intent`, `check_features`, `check_specify`, `check_plan_scenarios`) trata a **invocação sem argumentos** como "varrer o projeto" e imprime `pulado` com exit 0 quando não há `features/` nem plano v2; sem agregador. Entradas no `check_plugin_registry.json` com `stack: any`.
- Opção B: um agregador `check_default_cycle.py`, e os quatro scripts passam a recusar invocação sem argumentos com exit 0 e mensagem de uso.
- **Recomendação: A.** Recommended when o orquestrador já descobre `check_*.py` por glob e roda cada um **sem argumentos** (o exit code é tudo que ele lê): A não muda o orquestrador. NOT recommended (B) when isso exige reabrir quatro validadores entregues só para criar um quinto arquivo.

## Ordem de execução e de edição dos `SKILL.md`

Seis planos editam os mesmos arquivos. A ordem abaixo é pré-condição e o Step 1 **para** se um plano anterior não tiver executado; o Step 7 mede o resultado.

| Ordem | Plano | `SKILL.md` de corpo que ele toca | Natureza |
|---|---|---|---|
| 1 | 000007 | `_internal/plan/standard`, `implement` | uma linha de ponteiro para o contrato cada |
| 2 | 000009 | `_internal/plan/standard`, `plan` | fase grill, flag `--grill` |
| 3 | 000011 | `_internal/plan/standard`, `plan` | fase specify, flag `--specify`, `Specify: skipped` |
| 4 | 000012 | `plan`, `_internal/plan/standard`, `implement` (condicional) | `plan_format_version: 2`, recusa de step sem cenário, linha de parada |
| 5 | 000013 | `implement` | `--pipeline`, ramo v2 (teste-primeiro) |
| 6 | 000014 | `reflect`, `explain`, `_internal/explain/drift` | relatório por degrau (alvo <= 40 linhas somadas) |
| 7 | **000015** | `implement` (uma linha: congelar M1) | fiação; **nenhum** corpo novo em `plan`, `reflect`, `explain` |

Os planos 000008 e 000010 não tocam corpo de `SKILL.md`. Os quickguides (`SKILL-quickguide.md`) e `help/SKILL.md` não entram na tabela: o 000015 só acrescenta ponteiro em quickguide (Step 8).

**Orçamento de `skill-body-length`** (limites do tier em `check_docs_skill_body_length_baseline.md`; os números abaixo são da v0.9.1 e o Step 1 os remede na `dev` atual): `plan` heavy 423/500 (folga 77 para 78, 80, 81); `implement` heavy 199/500; `explain` standard 259/300 (folga 41); `reflect` standard 136/300; `help` light 71/150. Regra: quem estourar move o texto para a referência normativa e deixa ponteiro (como o 000013 já faz).

## Files

Todos no **open-seja** (repositório de execução), exceto onde dito. Caminhos **não verificados nesta sessão** (submodule vazio no worktree): o Step 1 os confere antes de qualquer escrita.

- `.claude/references/general/extended-cycle-contract.md` (modify, emendas aditivas e tabela de ordem)
- `.claude/references/template/feature-layout.md` (modify, `drift/` e `scenarios.lock.json`)
- `.claude/references/template/plan-step.md` (modify, texto de `Scenarios:`)
- `.claude/skills/scripts/check_specify.py` e `tests/test_check_specify.py` (modify, `--reconcile`)
- `.claude/skills/scripts/check_features.py` e `tests/test_check_features.py` (modify, `scenarios_state`)
- `.claude/references/general/grill-phase.md` e `implement-test-first.md` (modify, ponteiros)
- `.claude/skills/implement/SKILL.md` (modify, uma linha)
- `.claude/skills/scripts/run_all_checks.py` (read; modify só se o Step 1 mostrar necessidade), `check_plugin_registry.json` (modify), `tests/test_default_cycle_checks.py` (create)
- `.claude/skills/scripts/check_docs_skill_body_length_baseline.md` (modify)
- `docs/how-to/ciclo-default.pt-BR.md` (create) e ponteiros nos `SKILL-quickguide.md` de `plan`, `implement`, `reflect`, `explain`, `help`; `.claude/skills/help/SKILL.md` ou o manifesto que o gera (modify, entrada "Ciclo default")
- `tests/compat/` (create: fixtures de projetos existentes e script de prova de upgrade), `VERSION`/`CHANGELOG.md` (modify, nomes reais pelo Step 1)
- `product-design/seja-as-intended.md` (modify via `apply_marker.py`: H-009, D-NNN, CHANGELOG)
- `_output/plans/plan-000015-progress.md` (create no Doutourado)

## Best practices

- Integração não reimplementa: cada step chama o CLI ou o contrato que o item anterior entregou e testa a **costura** (entrada de um, saída do outro).
- Teste primeiro nos steps com código (3, 4, 6, 9); steps documentais declaram `Tests: N/A` com motivo.
- Emenda aditiva: nenhuma regra `CYC/GRL/GHK/SPC/PFS/TFB` é removida ou renumerada; o que muda ganha uma regra nova ou uma nota "emenda 000015".
- "PASS is a tool result, not a sentence" (research-000050): todo critério vira comando ou `grep`.
- Voz controlada (plan-000074): o guia pt-BR passa em `lint_controlled_language.py` se existir; senão, frases até 25 palavras por contagem própria, e o progress registra `voz: não verificada`.
- Marcadores Human (markers) só via `apply_marker.py` com confirmação; prosa de H-009 e das D-NNN colada pelo designer (`/implement --manual`), como no 000064.
- Retrocompatibilidade como teste, não como promessa: a prova do Step 9 roda antes e depois e compara.

## Design decisions

- **User-visible impact:** quando você atualizar o SEJA para a nova tag, nada muda no que já existe: seus planos antigos, seus testes e seu `run_all_checks` continuam como estavam. A partir daí, um `/plan` para uma tarefa com código começa perguntando o que você quer (grill), mostra os cenários para você aprovar (specify) e só então escreve o plano; o `/implement` escreve um teste vermelho por cenário e, ao fim, guarda o retrato do que foi entregue; o `/reflect` mostra onde a intenção se perdeu, degrau por degrau. Se você reabrir a conversa sobre uma intenção, os cenários aprovados passam a rascunho sozinhos. O `/help` explica tudo isso em português, com um desenho da escada.
- **Trade-offs accepted:** pequenas escritas aditivas em validadores já entregues (`--reconcile`, `scenarios_state`) em troca de um campo que não mente; o M1 é congelado pelo `/implement` (acopla `/implement` a `drift_report.py` por uma linha) em troca de um M1 comparável; o guia pt-BR fica separado dos quickguides (um arquivo a mais) para não mexer no carregador; o upgrade só atualiza o plugin do teste-primeiro se ele já estiver instalado; o follow-up do Stop hook fica como medição, não como mudança.
- **Metacommunication impact:** I know you may have projects that already use the SEJA; therefore I do not change them when you upgrade: old plans stay valid and nothing new is asked until you ask for code with a new feature. I tell you in Portuguese, with short sentences and one picture, how your intent becomes scenarios, tests and code, and where I could not measure. If I stop you between a red test and green code, I tell you why in the message.

## Steps

### Step 1: Conferir o terreno e fixar o baseline antes de qualquer escrita
Na `dev` do open-seja (`git submodule update --init open-seja` se vazio), registrar no progress `_output/plans/plan-000015-progress.md`: (a) que os planos 000007 a 000014 já executaram, com os identificadores reais (`CYC/GRL/GHK/SPC/PFS/TFB-NNN`, `NM-*`) e os CLIs reais de `check_intent.py`, `check_features.py` (`--matrix`), `check_specify.py` (`--status`, `--approve`), `check_plan_scenarios.py` e `drift_report.py` (`--freeze`, `--compare`); **parar** se algum item anterior não executou (a ordem da tabela é pré-condição); (b) o que cada `check_*.py` faz **sem argumentos** num projeto sem `features/` (o `run_all_checks` os executa assim: glob `check_*.py`, sem argumentos, lê só o exit code; script fora do registro entra por padrão); (c) a conformidade de `scenarios: draft|approved` nos leitores do 000010/000011 (valores aceitos); (d) o estado do `skill-body-length` por skill (`python .claude/skills/critique/check_docs.py --plugins skill-body-length --verbose`) e a folga contra o orçamento da tabela; (e) a tag corrente, o arquivo de versão e o CHANGELOG reais, e se `check_version_changelog_sync.py` os cobre; (f) se `lint_controlled_language.py`, `select_diagram.py` e o `--html` do 000074 existem; (g) o baseline de `python .claude/skills/scripts/run_all_checks.py` (conjunto de falhas pré-existentes) e a medição do caso (i) do 000013 (Stop hook entre RED e GREEN), se o progress do 000013 a tiver. Nada é escrito no open-seja neste step.
- **Files**: open-seja/.claude/references/general/extended-cycle-contract.md (read), open-seja/.claude/skills/scripts/run_all_checks.py (read), open-seja/.claude/skills/scripts/check_plugin_registry.json (read), open-seja/.claude/skills/scripts/check_specify.py (read), `_output/plans/plan-000015-progress.md` (create no Doutourado)
- **References**: product-design/conventions.md, product-design/constitution.md, planos 000007 a 000014
- **Interface**: N/A
- **Verify**: o progress responde (a) a (g) com caminho e "existe/ausente"; contém o baseline de `run_all_checks` (lista de checks e status); `git -C open-seja status` limpo; se um plano anterior não executou, o progress diz "PARADO: plano 0000NN" e nenhum step seguinte começa.
- **Tests**: N/A (verificação de estado, sem código)
- [x] Done

### Step 2: Emendas aditivas ao contrato, ao layout e ao formato de plano
Três arquivos, só acréscimos com a marca "emenda 000015": (1) `feature-layout.md`: acrescentar `features/<slug>/scenarios.lock.json` (do 000011) e `features/<slug>/drift/` (do 000014: `m1.json` imutável, `m2-<data>.json`, saída de `--compare`), a chave `build` de `gate.json` (do 000013) e a regra "nada em `drift/` é apagado" (Q2); (2) `extended-cycle-contract.md`: nova seção "Emendas do item 9" com (a) **`Scenarios:` usa a chave `<slug>/<arquivo>::<nome>`**, substituindo o texto "`@REQ-...` ou nomes de cenário" do 000007 (a tag `@REQ-` continua sendo a tag do cenário e a ligação REQ-cenário; não é a chave de step), (b) **proxy do skip**: a classificação da grill ("com código" / "sem código") decide *antes*; `PFS-013` confere *depois* (000011 lacuna 6; 000012 lacuna 5), (c) quem congela o M1 e quando (Decisão pendente 1), (d) quem reconcilia `scenarios:` e com qual valor (Decisão pendente 2), (e) a tabela "ordem de edição dos `SKILL.md`" acima; (3) `plan-step.md`: o texto do campo `Scenarios:` ganha a chave e um exemplo, mantendo `N/A (motivo)`. As emendas ao **texto do plano 000007** (arquivo do Doutourado) não são feitas aqui: vão como nota no progress para o orquestrador anexar como "Plan Amendment" ao 000007, porque plano aprovado só recebe adendo.
- **Files**: open-seja/.claude/references/template/feature-layout.md (modify), open-seja/.claude/references/general/extended-cycle-contract.md (modify), open-seja/.claude/references/template/plan-step.md (modify)
- **References**: product-design/constitution.md, planos 000007, 000010, 000011, 000012, 000013, 000014
- **Depends on**: Step 1
- **Interface**: chave de cenário `<slug>/<arquivo>::<nome>`; árvore `features/<slug>/{intent.md,*.feature,gate.json,scenarios.lock.json,drift/}`.
- **Verify**: `git diff` dos três arquivos mostra só linhas adicionadas (`git diff --numstat` com 0 remoções, exceto o trecho do `Scenarios:` em `plan-step.md`, que o diff mostra como substituição do exemplo); `grep -c "emenda 000015"` >= 5; `grep -n "drift/" feature-layout.md` e `grep -n "scenarios.lock.json" feature-layout.md` acham as linhas; os checks do 000010 (`check_features.py`) e do 000012 (`check_plan_scenarios.py`) sobre os exemplos do layout continuam com o mesmo resultado; `git grep -i` dos termos de C1 sobre o diff devolve zero; `run_all_checks.py` igual ao baseline.
- **Tests**: N/A (documento normativo; os validadores têm os testes)
- **Docs**: as três referências.
- [x] Done

### Step 3: Reconciliar `scenarios:` no disco quando a grill reabre
Teste primeiro. Em `check_specify.py`, acrescentar `--reconcile <slug|--all> [--json]` (Decisão pendente 2, default A): para cada feature em que `--status` calcula `stale` (lock não bate com os `.feature` ou com os `rev` dos REQs) **ou** em que o `intent.md` voltou a `status: grilling`, reescrever `scenarios: approved` para `scenarios: draft` **só** no `intent.md` daquela feature, preservando o resto byte a byte e o `scenarios.lock.json`; escrita atômica; caminho resolvido sob `features/<slug>/` sem seguir `..`; idempotente (segunda execução não muda nada, exit 0); saída lista o que mudou e o motivo em frase curta. Em `grill-phase.md`, acrescentar ao passo "reabrir a intenção" uma linha: depois de voltar `status` a `grilling`, rodar `check_specify.py --reconcile <slug>`. Não alterar `--status`, `--approve` nem o formato do lock.
- **Files**: open-seja/.claude/skills/scripts/check_specify.py (modify), open-seja/.claude/skills/scripts/tests/test_check_specify.py (modify), open-seja/.claude/references/general/grill-phase.md (modify, uma linha)
- **References**: product-design/standards.md § Backend 19, 20; § Testing; plano 000011 (SPC-013), plano 000009 (Degradação)
- **Depends on**: Step 2
- **Interface**: `check_specify.py --reconcile <slug> [--json]` -> exit 0 se nada a fazer ou reconciliou, 2 em erro de uso; `--json` devolve `{"slug", "changed": bool, "from": "approved", "to": "draft", "reason": "stale|reopened"}` (campos conferidos contra o JSON real do `--status` no Step 1).
- **Verify**: `pytest .claude/skills/scripts/tests/test_check_specify.py` verde, incluindo os casos novos; `ruff check` e `pyright` limpos nos dois arquivos; `git diff --stat` mostra só os três arquivos; os testes antigos do `--status`/`--approve` passam sem edição.
- **Tests**: when a feature tem `scenarios: approved` e um `.feature` foi editado depois do lock, `--reconcile` returns exit 0 e o `intent.md` passa a `scenarios: draft`, com o restante do arquivo e o lock byte a byte iguais; when a feature está `approved` e íntegra, returns "nada a fazer" e o arquivo não muda (mtime e hash iguais); when roda duas vezes, a segunda não altera nada; when o `intent.md` tem `status: grilling` e `scenarios: approved`, returns `draft` com motivo `reopened`; when o slug aponta para fora de `features/` (`../x`), returns exit 2 e não escreve.
- **Docs**: a seção de CLI no `specify-phase.md` (acrescentar `--reconcile` à tabela de comandos, uma linha) e `grill-phase.md`.
- [x] Done

### Step 4: Matriz e consumidores usam `--status`, não o campo
Teste primeiro. Em `check_features.py --matrix`, acrescentar a cada feature o campo `scenarios_state` (`approved|stale|draft|missing`), obtido de `check_specify.py --status --json` pela CLI (acoplamento por JSON versionado, não pelos internos), **sem mudar** o significado de `scenarios_approved` (continua o valor do campo no disco). Quando `check_specify.py` não existe (open-seja velho) ou falha, `scenarios_state` sai `desconhecido` e o `--matrix` não falha. Conferir `drift_report.py` (000014): ele já consulta `--status`; o step só prova, por teste, que `scenarios_state != approved` torna o D1 `não medido` e que `scenarios_approved: true` com `stale` **não** conta como aprovado. Conferir também `check_plan_scenarios.py` (000012), que usa `--status`. Nenhum consumidor novo lê só o campo.
- **Files**: open-seja/.claude/skills/scripts/check_features.py (modify), open-seja/.claude/skills/scripts/tests/test_check_features.py (modify), open-seja/.claude/skills/scripts/tests/test_drift_report.py (modify, só caso novo, se o 000014 não o tiver)
- **References**: product-design/standards.md § Backend 4, 19; plano 000010 (`--matrix`), plano 000011 (`--status`), plano 000014 (decisão fechada 3)
- **Depends on**: Step 3
- **Interface**: chave `scenarios_state` na saída `--matrix --json` (versão do esquema do `--json` acrescenta a chave sem remover nenhuma).
- **Verify**: `pytest` dos três arquivos verde; `ruff` e `pyright` limpos; `check_features.py --matrix --json` numa fixture com feature `stale` mostra `scenarios_approved: true` e `scenarios_state: "stale"`; `git grep -n "scenarios_approved"` em `drift_report.py` e `check_plan_scenarios.py` não aparece como fonte de decisão (só o `scenarios_state` ou `--status`); os testes antigos do `--matrix` passam sem edição.
- **Tests**: when a feature tem `scenarios: approved` e lock desatualizado, `--matrix --json` returns `scenarios_state: "stale"` e mantém `scenarios_approved: true`; when `check_specify.py` está ausente, returns `scenarios_state: "desconhecido"` e exit 0; when `drift_report.py` calcula D1 sobre a feature `stale`, returns D1 `não medido` com a razão; when a feature está `approved` e íntegra, returns `scenarios_state: "approved"` e D1 medido.
- **Docs**: `gherkin-spec-format.md` (uma linha: o campo `scenarios_approved` é o valor do disco; o estado confiável é `scenarios_state`).
- [x] Done

### Step 5: Fiação do `/implement` para congelar o M1
Em `implement-test-first.md` (norma do 000013), acrescentar a seção "Congelar o M1 (emenda 000015)": ao fim do plano com `plan_format_version: 2` e `Feature: <slug>`, depois da rodada `full` (ou registrando `full: null` quando foi pulada), o `/implement` roda `python .claude/skills/scripts/drift_report.py --freeze <slug>`; se o M1 já existe, a regra de recusa do 000014 vale e o `/implement` só avisa (Decisão pendente 1, default A); se `drift_report.py` não existir ou falhar por outro motivo, avisa e segue (nunca reprova o `/implement`). Em `implement/SKILL.md`, **uma** linha no ramo v2 ("ao fim, congelar o M1; ver `implement-test-first.md`"), na posição conferida no Step 1 (depois do ponteiro do 000007, da parada do 000012 e do ramo do 000013). Plano v1, plano sem `Feature:` e `Specify: skipped` não congelam nada. Teste de integração com papéis roteirizados (reuso do projeto descartável do 000013).
- **Files**: open-seja/.claude/references/general/implement-test-first.md (modify), open-seja/.claude/skills/implement/SKILL.md (modify, uma linha), open-seja/.claude/skills/scripts/tests/test_default_cycle_wiring.py (create)
- **References**: plano 000013 (Step 7, Step 8), plano 000014 (`--freeze`, recusa de sobrescrita), plano 000008 (M1)
- **Depends on**: Step 2, Step 4
- **Interface**: N/A (texto normativo e uma chamada de CLI existente)
- **Verify**: `git diff --stat` mostra só os três arquivos e **uma** linha adicionada em `implement/SKILL.md` (`git diff --numstat` = 1 adição, 0 remoções); `grep -n "drift_report.py --freeze" implement-test-first.md` acha a seção; `pytest .../test_default_cycle_wiring.py` verde; `python .claude/skills/critique/check_docs.py --plugins skill-body-length` não reprova `implement`; os testes do 000013 passam sem edição.
- **Tests**: when um plano v2 com `Feature: demo` termina com a rodada `full` verde, o fluxo roteirizado returns `features/demo/drift/m1.json` criado e o hash das entradas registrado; when o `m1.json` já existe, returns aviso "M1 já congelado" e exit 0 do fluxo, sem sobrescrever; when o plano é v1, returns nenhum arquivo em `drift/`; when `drift_report.py` não está instalado, returns aviso e o fluxo termina OK.
- **Docs**: `implement-test-first.md` e o guia pt-BR (Step 8).
- [x] Done

### Step 6: Registrar os checks novos no `run_all_checks` (condicionais a `features/`)
Teste primeiro. Decisão pendente 8, default A: garantir que `check_intent.py`, `check_features.py`, `check_specify.py` e `check_plan_scenarios.py`, **chamados sem argumentos na raiz do projeto**, (a) imprimem `pulado` e saem 0 quando não há `features/` com `intent.md` nem plano v2 em `_output/plans/`; (b) varrem o projeto e saem 1 (com o nome do check) quando há feature ou plano v2 inválido; (c) ignoram `features/` de terceiros sem `intent.md` (`pulado`); (d) nunca tocam planos v1. Acrescentar as quatro entradas ao `check_plugin_registry.json` (`stack: any`, `critical: false`, `scope` próprio). Só editar `run_all_checks.py` se o Step 1 mostrar que o glob não os pega (esperado: não é preciso). O teste agregado `test_default_cycle_checks.py` cria quatro projetos temporários e roda `run_all_checks.py` em cada um, comparando com o baseline do Step 1.
- **Files**: open-seja/.claude/skills/scripts/check_plugin_registry.json (modify), open-seja/.claude/skills/scripts/tests/test_default_cycle_checks.py (create), open-seja/.claude/skills/scripts/check_intent.py (modify, só o ramo sem argumentos, se o Step 1 mostrar necessidade), open-seja/.claude/skills/scripts/check_specify.py (modify, idem), open-seja/.claude/skills/scripts/check_plan_scenarios.py (modify, idem)
- **References**: product-design/standards.md § Testing 4; plano 000011 (Step 7), plano 000012 (Step 5)
- **Depends on**: Step 4
- **Interface**: `run_all_checks.py` lista os quatro checks com `PASS` e saída `pulado` quando não há ciclo; `FAIL` com o nome do check quando há violação.
- **Verify**: `pytest .claude/skills/scripts/tests/test_default_cycle_checks.py` verde; num projeto sem `features/` e só com planos v1, `run_all_checks.py` devolve o **mesmo conjunto de falhas pré-existentes** do baseline do Step 1 e os quatro checks `PASS` (`pulado`); `ruff` e `pyright` limpos; `git diff --stat` não toca `run_all_checks.py` se não for necessário.
- **Tests**: when o projeto não tem `features/` nem plano v2, returns `pulado` nos quatro e o resto do `run_all_checks` idêntico ao baseline; when há `features/foo/` sem `intent.md` (terceiros), returns `pulado`; when há feature válida e aprovada, returns `PASS`; when há `.feature` sem tag `@REQ-`, returns `FAIL` do `check_features`; when há plano v2 com cenário sem step, returns `FAIL` do `check_plan_scenarios`; when só há plano v1, returns `pulado` e nenhum v1 é lido além do cabeçalho.
- **Docs**: `README` de scripts, se houver lista de checks (uma linha por check).
- [x] Done

### Step 7: Consolidar a ordem de edição dos `SKILL.md` e o limite `skill-body-length`
Com os planos 000007 a 000014 e os Steps 2 a 6 aplicados, medir: `python .claude/skills/critique/check_docs.py --plugins skill-body-length --verbose`, `check_skill_system.py` e `check_skill_spec.py`. Comparar cada skill com o orçamento da tabela. Para qualquer skill acima do limite do tier ou com 90% do limite: mover o texto executável para a referência normativa da fase (`grill-phase.md`, `specify-phase.md`, `plan-from-scenarios.md`, `implement-test-first.md`, `drift-report.md`) e deixar ponteiro; **não** aumentar o limite (a calibração é do mundo, não do lint: baseline do plan-000458). Verificar também o **conteúdo** da ordem: cada flag (`--grill`, `--specify`, `--pipeline`) aparece uma vez na tabela de argumentos, a linha `Specify: skipped` aparece uma vez no `standard/SKILL.md` (lacuna 2 do 000012), `plan_format_version: 2` só no C3 do modo standard e `1` em `--light` e roadmap. Atualizar `check_docs_skill_body_length_baseline.md` com os números finais.
- **Files**: open-seja/.claude/skills/scripts/check_docs_skill_body_length_baseline.md (modify), open-seja/.claude/skills/plan/SKILL.md (modify, só se precisar mover texto), open-seja/.claude/skills/_internal/plan/standard/SKILL.md (modify, idem), open-seja/.claude/skills/implement/SKILL.md (modify, idem), open-seja/.claude/references/general/extended-cycle-contract.md (modify, tabela com números finais)
- **References**: `check_docs_skill_body_length_baseline.md` (plan-000458), plano 000013 (lacuna 16)
- **Depends on**: Step 5, Step 6
- **Interface**: N/A
- **Verify**: `check_docs.py --plugins skill-body-length` sai 0 sem novo WAIVER; `grep -c "Specify: skipped" .claude/skills/_internal/plan/standard/SKILL.md` = 1; `grep -c -- "--grill" .claude/skills/plan/SKILL.md` e `--specify`, `--pipeline` em `implement` = 1 cada na tabela de argumentos; `grep -n "plan_format_version" .claude/skills/plan/SKILL.md` mostra `2` só no modo standard; o baseline atualizado lista `plan`, `implement`, `explain`, `reflect`, `help` com os números medidos; `check_skill_system.py` e `run_all_checks.py` com o mesmo conjunto de falhas do baseline.
- **Tests**: N/A (medição e documento; os lints existentes são o teste)
- **Docs**: a tabela de ordem no contrato e o baseline.
- [x] Done

### Step 8: `/help` e guia pt-BR em voz controlada, com o diagrama da escada
Decisão pendente 4, default B. Criar `docs/how-to/ciclo-default.pt-BR.md` com: o que mudou e por que (uma tela), a **escada** (intenção -> cenário -> teste -> código) em Mermaid, com os quatro degraus (D1 intenção->cenário, D2 cenário->teste, D3a/D3b teste->código e gate) e, por degrau, **quem olha** (você, que descreve a intenção e aprova os cenários; a máquina; quem programa, se quiser) e o artefato; os comandos (`/plan`, `/plan --grill`, `/plan --specify`, `/implement`, `--pipeline`, `/reflect`, `/explain drift --scope ladder`); como pular com motivo (`--light`, tarefa sem código); o que fazer quando algo bloqueia (a grill reaberta, `stale`, o Stop hook entre vermelho e verde); como atualizar (`/seja-setup --upgrade`) e o que não muda. Escolher o tipo de diagrama com `select_diagram.py` se existir (Step 1(f)); senão, `flowchart LR`. Frases até 25 palavras, uma ideia por frase, termos fixos do glossário (`grill`, `specify`, `cenário`, `degrau`). Acrescentar **uma linha de ponteiro** em cada `SKILL-quickguide.md` afetado (`plan`, `implement`, `reflect`, `explain`, `help`) e a entrada "Ciclo default" na saída do `/help` (no manifesto que o gera, conforme Step 1). Se o `--html` do 000074 existir, gerar a página em `_output/html/` para conferência; não commitar.
- **Files**: open-seja/docs/how-to/ciclo-default.pt-BR.md (create), open-seja/.claude/skills/help/SKILL.md (modify, entrada "Ciclo default"), open-seja/.claude/skills/plan/SKILL-quickguide.md (modify, ponteiro), open-seja/.claude/skills/implement/SKILL-quickguide.md (modify, ponteiro), open-seja/.claude/skills/reflect/SKILL-quickguide.md (modify, ponteiro)
- **References**: plano 000074 (voz controlada, diagramas), `designer-copy-voice.md`, plano 000008 (nomes dos degraus), `general/constraints.md`
- **Depends on**: Step 5, Step 7
- **Interface**: N/A
- **Verify**: `python .claude/skills/scripts/lint_controlled_language.py docs/how-to/ciclo-default.pt-BR.md` sem aviso (ou, sem o lint, um `awk` de contagem de palavras por frase com máximo 25, registrado no progress com `voz: não verificada`); o bloco Mermaid renderiza (conferência por `md_to_html.py` ou `--html`, sem erro) e cita D1, D2, D3a, D3b; `git grep -c "ciclo-default.pt-BR"` mostra 1 ponteiro em cada um dos cinco quickguides (os de `explain` e `help` entram no próximo commit do mesmo step se o limite de 5 arquivos por step estourar: dividir em 8a e 8b); `/help` (dry-run por `generate_skill_map.py` ou leitura do `help/SKILL.md`) lista "Ciclo default"; `check_docs.py` (harness-integrity, path-liveness) sem erro novo; `git grep -i` dos termos de C1 devolve zero.
- **Tests**: N/A (documentação; o lint de voz e o `check_docs` são o critério). Se o `lint_controlled_language.py` não existir: `N/A (lint ausente; contagem manual registrada)`.
- **Docs**: o próprio guia; os cinco ponteiros.
- [ ] Done

### Step 9: Provar o upgrade por tag em projetos existentes e preparar a versão
Teste primeiro. Criar `tests/compat/` com quatro projetos de fixture **gerados pela tag anterior** (instalar a tag pinada anterior num diretório temporário a partir de um clone local do open-seja, passando o clone como `--remote` ao `resolve_seja_version.py`; sem rede, sem push): (i) projeto novo sem `features/` e com planos v1; (ii) projeto com `features/` de terceiros sem `intent.md` e planos v1; (iii) projeto no meio do ciclo: `features/<slug>/` aprovado, plano v2 e M1 (retrato congelado) -- gerado depois, com a tag nova, para provar idempotência de uma segunda atualização; (iv) cópia do estado do próprio Doutourado (`.seja-version v0.9.1`, `conventions.md` e `settings` próprios). Para cada um: guardar o instantâneo de `run_all_checks.py` e a leitura em dry-run do `/implement` sobre um plano v1; rodar `/seja-setup --upgrade --dry-run` e depois `--upgrade` até a tag nova; comparar. Passa quando: nenhum arquivo do projeto (`conventions.md`, `settings`, `_output/`, `product-design/`, `features/`, planos) muda; o conjunto de falhas do `run_all_checks` é o mesmo mais os quatro checks `pulado`; o plano v1 é aceito como antes; o plugin do 000013 só é atualizado se já estava instalado (Decisão pendente 6, default C); rodar o upgrade duas vezes não muda nada na segunda. Preparar (sem publicar) a versão: bump conforme a Decisão pendente 5 (default minor) no arquivo de versão real, entrada no CHANGELOG (en-US, sem parceiro) descrevendo o novo default, `--grill`, `--specify`, `--pipeline`, `scenarios: draft`, e a frase "plans in v1 stay valid", e `check_version_changelog_sync.py` verde. A tag, o `/publish` e o `npm publish` ficam com o designer.
- **Files**: open-seja/tests/compat/run_upgrade_compat.py (create), open-seja/tests/compat/fixtures/ (create), open-seja/CHANGELOG.md (modify), open-seja/VERSION (modify; nome real conforme Step 1), open-seja/.claude/skills/seja-setup/SKILL.md (modify, só se a Decisão pendente 6 = C exigir uma linha de texto no fluxo de upgrade)
- **References**: product-design/constitution.md (T2, Q2), `resolve_seja_version.py`, `check_version_changelog_sync.py`, plano 000013 (lacuna 15)
- **Depends on**: Step 6, Step 7
- **Interface**: `python tests/compat/run_upgrade_compat.py --from <tag-anterior> --to <tag-nova> --remote <clone-local>` -> exit 0 se os quatro projetos passam; relatório por projeto com os arquivos comparados.
- **Verify**: o script devolve exit 0 nos quatro projetos; o relatório mostra 0 arquivos de projeto alterados e o conjunto de falhas pré-existentes igual; a segunda atualização devolve "already up to date" ou diff vazio; `python .claude/skills/scripts/check_version_changelog_sync.py` verde; `git tag` não ganhou nenhuma tag e nada foi enviado (`git status` e `git log origin..HEAD` só mostram commits locais); `git grep -i` dos termos de C1 sobre o diff devolve zero.
- **Tests**: when o projeto (i) é atualizado para a tag nova, returns nenhum arquivo de projeto alterado e `run_all_checks` com os quatro checks `pulado`; when o projeto (ii) tem `features/` de terceiros, returns `pulado` e `features/` intacta byte a byte; when o projeto (iii) é atualizado de novo, returns diff vazio e o `m1.json` com o mesmo hash; when o projeto (iv) é atualizado, returns `conventions.md` e `settings` iguais e `.seja-version` com a tag nova; when o plugin do teste-primeiro não estava instalado, returns que o upgrade não o criou.
- **Docs**: `CHANGELOG.md`; o guia pt-BR (seção "Como atualizar").
- [ ] Done

### Step 10: H-009 e as D-NNN coerentes entre os oito planos
Conferir no `seja-as-intended.md` do open-seja (escrito pelo 000007, Step 6) que H-009 e as quatro D-NNN existem e que **batem** com o que os planos 000008 a 000014 e este plano fixaram: nomes dos degraus (D1, D2, D3a, D3b), estados (`coberto/descoberto/não medido`, `approved/stale/draft/missing`), a chave do cenário, `rev` do REQ, `Specify: skipped`, `--pipeline` opt-in. Redigir (prosa do designer, `/implement --manual`, via `apply_marker.py`) apenas o que falta: (a) a **ressalva** do 000008 (lacuna 2) na condição de refutação: no ciclo padrão não há REQ nem cenário, então D1 e D2 do braço A existem por retrofit e a comparação segue a regra do `drift-control-protocol.md`; (b) uma nota sob H-009 dizendo que a medida é feita pelo `drift_report.py` sobre o M1 congelado pelo `/implement` e o M2 pós-entrega; (c) **uma D-NNN nova**: "o ciclo default entra por upgrade de tag e age só onde há `features/` ou plano v2; v1 é válido para sempre; sem chave de desligar" (Decisão pendente 3 deste plano) em forma DDR, citando H-008 e as D-NNN anteriores do ciclo. Registrar no progress a tabela "afirmação de H-009 -> plano que a sustenta". Sem nome de parceiro (C1).
- **Files**: open-seja/product-design/seja-as-intended.md (modify via apply_marker.py), open-seja/product-design/ (CHANGELOG append), `_output/plans/plan-000015-progress.md` (modify)
- **References**: product-design/product-design-as-intended.md (D-004, D-005), plano 000007 (Step 6), plano 000008 (Step 7 e lacuna 2)
- **Depends on**: Step 5, Step 9
- **Interface**: N/A
- **Verify**: `grep -n "H-009" seja-as-intended.md` acha a hipótese com "Condição de refutação", a ressalva do braço A e a menção a `drift_report.py`; `grep -c "^### D-"` aumentou em 1 em relação ao Step 1, com os quatro campos DDR e linha `STATUS` acima; `python .claude/skills/scripts/check_human_markers_only.py` e `run_all_checks.py` verdes; `git grep -n "D3a"` aparece de forma consistente em `drift-metric.md`, `drift-report.md`, `seja-as-intended.md` e no guia pt-BR; `git grep -i` dos termos de C1 sobre o diff devolve zero.
- **Tests**: N/A (documento de design; escrita Human (markers))
- **Docs**: `seja-as-intended.md`.
- [ ] Done

### Step 11: Follow-up dos hooks, ensaio de ponta a ponta e entrega ao piloto
(1) **Hooks** (Decisão pendente 7, default A): ler no progress do 000013 a medição do caso (i) (quantas vezes o `Stop` barrou entre RED e GREEN no ensaio) e registrar no progress; documentar o efeito no guia pt-BR (seção "Se o Stop hook bloquear no vermelho") **sem editar** `quality_gate_stop.py`, `quality_gate_pretool.py`, `_gate_hook_common.py` nem `settings.fragment.json`; escrever, no progress, o **rascunho de brief** do follow-up B (marcador "vermelho em curso" escrito pelo `/implement`, lido pelo hook, com os limites do 000068) e o gatilho para virar plano (barramento medido em mais de um step por feature). (2) **Ensaio** numa feature fictícia descartável (sem parceiro), com papéis roteirizados como no 000013: grill (aprovado) -> specify (aprovado) -> `/plan` v2 (`check_plan_scenarios.py` ok) -> `/implement` (vermelho, verde, `full`, **freeze do M1**) -> reabrir a grill (`--reconcile` muda o campo) -> editar um `.feature` -> M2 e `--compare` -> `/reflect` e `/explain drift --scope ladder` lendo a saída; registrar tempos e o que o agente fez de errado. (3) Fechar: `run_all_checks.py`, `/critique validate` nos arquivos novos, C1 por `git grep -i`, e escrever a tabela "o que este plano entrega ao item 10" (piloto): comando do braço novo, comando do braço de controle (tag anterior pinada), onde ficam M1/M2, como medir tempo até a primeira feature aprovada, e as pendências que ainda estão no default.
- **Files**: `_output/plans/plan-000015-progress.md` (modify), open-seja/docs/how-to/ciclo-default.pt-BR.md (modify, seção do Stop hook), open-seja/tests/compat/fixtures/ (read), open-seja/.claude/skills/scripts/run_all_checks.py (read)
- **References**: plano 000068 (progress, limites dos hooks), plano 000013 (lacuna 9, Step 8), plano 000014 (Step 9), roadmap-000006 (item 10)
- **Depends on**: Step 8, Step 10
- **Interface**: N/A
- **Verify**: `git diff --stat` não lista nenhum arquivo em `.claude/hooks/` nem `settings.fragment.json`; o progress contém o ensaio com os sete momentos e os tempos, o rascunho de brief do follow-up e a tabela para o item 10; `run_all_checks.py` com o mesmo conjunto de falhas do baseline; `/critique validate` sem erro novo; `git grep -i` dos termos de C1 devolve zero; o guia pt-BR passa de novo no lint de voz (ou na contagem).
- **Tests**: N/A (ensaio e documento; as asserções estão nos Steps 3 a 6 e 9)
- **Docs**: o guia pt-BR (Stop hook) e o progress.
- [ ] Done

## Lacunas e conflitos com os planos 000007 a 000014

1. **`Scenarios:` no 000007 x chave dos 000010/000011/000012.** O 000007 (Step 3) diz "lista de `@REQ-...` ou nomes de cenário"; os três planos seguintes fixaram a chave `<slug>/<arquivo>::<nome>` e o 000012 aceita **só** a chave. Resolvido por emenda aditiva no contrato e em `plan-step.md` (Step 2). O texto do próprio plano 000007 (arquivo do Doutourado) continua dizendo a versão antiga: recomendo ao orquestrador anexar um "Plan Amendment" ao 000007; não editei o 000007 aqui.
2. **Proxy do skip.** O 000007 dá a regra "algum step tem `Tests:` não-N/A", mas os steps nascem depois da specify; 000011 e 000012 usam a classificação da grill e conferem depois com `PFS-013`. Emenda no contrato (Step 2). Caso borda mantido do 000012: tarefa "sem código" que termina com `Tests:` não-N/A é recusada, não promovida.
3. **Esquema fechado do layout.** O 000007 fixa `{intent.md, *.feature, gate.json}` e `gate.json = {fast, full, ts}`; os planos seguintes acrescentaram `scenarios.lock.json` (80), a chave `build` (82) e `drift/` (83). Todos aditivos; a emenda do Step 2 lista as quatro. Risco: um validador de layout fechado do open-seja rejeitar arquivos extras; o Step 1(b) e o Step 6 provam que não.
4. **`scenarios: approved` mentindo.** Lacuna 4 do 000011 e 3 do 000014: nenhuma peça reescrevia o campo. Fechada pelo `--reconcile` (Step 3) e pelo `scenarios_state` (Step 4), com o `--status` como fonte de verdade para os consumidores. Decisão pendente 2 escolhe o valor gravado.
5. **Descoberta por glob do `run_all_checks` (achado novo, v0.9.1).** O orquestrador executa **todo** `check_*.py` por glob, **sem argumentos**, e lê só o exit code; script fora do `check_plugin_registry.json` entra por padrão. Os planos 000011 e 000012 trataram o registro como "opcional/condicional", mas na prática `check_intent.py`, `check_features.py`, `check_specify.py` e `check_plan_scenarios.py` **já seriam executados sem argumentos** em todo projeto assim que a tag nova chegasse; se algum sair com exit 2 por falta de argumento, `run_all_checks` passa a falhar em **todos** os projetos existentes. É o risco de compatibilidade mais concreto do item; o Step 1(b) confirma e o Step 6 o fecha. Conferido só na cópia local v0.9.1; a `dev` atual pode diferir.
6. **Quem congela o M1.** Lacuna 2 do 000014 e "item 7 ou 9" do 000008: nenhum plano chamava `--freeze`. Fechada pelo Step 5 (Decisão pendente 1).
7. **Escrita concorrente nos mesmos `SKILL.md`.** Lacunas do 000011 (8), 000012 (13), 000013 (6), 000014 (7). A tabela de ordem é a resposta; o Step 1 para se a ordem não foi seguida; o Step 7 mede e corrige.
8. **`skill-body-length`.** `plan` (heavy, 423/500 na v0.9.1) recebe três planos; se a soma passar de 77 linhas o limite estoura. Os planos 000009, 000011 e 000012 não declaram orçamento de linhas; o 000014 declara <= 40 linhas somadas. O Step 7 mede, move texto para as referências e não sobe o limite.
9. **Matriz com número de linha variável.** O `--matrix` (000010) devolve `scenarios_approved` e o `drift_report.py` (000014) já consulta `--status`: dois caminhos para a mesma informação até o Step 4. Não há conflito de resultado, só risco de um consumidor futuro ler o campo.
10. **Plugin pytest fora do `/seja-setup`.** Lacuna 15 do 000013: decidido na Decisão pendente 6 (default C) e provado no Step 9.
11. **Stop hook e árvore vermelha.** Lacuna 9 do 000013: tratada como medição com gatilho (Decisão pendente 7); nenhum hook é editado.
12. **Voz controlada e HTML (000074).** Se `lint_controlled_language.py`, `select_diagram.py` ou `--html` não estiverem entregues, o Step 8 degrada para contagem de palavras e `flowchart LR` e registra `voz: não verificada`; não há bloqueio.
13. **Condição de refutação do 000007 x protocolo do 000008.** O braço A (ciclo padrão) não tem REQ nem cenário; a comparação é por retrofit. Ressalva proposta no Step 10(a); prosa Human, não escrita sem o designer.
14. **Fricção do citizen.** O risco do roadmap permanece: a grill e a specify acrescentam passos. A defesa deste plano é não acrescentar um quinto (nenhuma chave nova, Decisão pendente 3), explicar em pt-BR e deixar `--light`/tipo de tarefa como saída; a medição é do piloto (item 10).
15. **Doutourado fora do escopo de escrita.** Este plano não toca `product-design/` do Doutourado; a coerência de D-NNN/H-009 vale para o `seja-as-intended.md` do open-seja. Se o designer quiser um espelho no Doutourado (D-006), é plano à parte.

## Coverage (advisory)

`product-design/product-design-as-intended.md` do Doutourado não tem marcadores REQ; `critique_plan_coverage.py` não se aplica e `Traces:` fica ausente. O plano executa no open-seja. Cobertura de cenário (conceito do 000012) não se aplica: este plano é v1 e não tem `Scenarios:`.

## Metacomm Intention
- **Summary**: I tell you that when you upgrade to the new tag, your existing projects and old plans keep working and nothing new is asked until you start a feature with code; that after that I ask first, show you the scenarios, build with a red test per scenario, freeze a snapshot of what I delivered and tell you in Portuguese, with one picture, where your intent got lost; and that if you reopen the conversation about an intent, I turn your approved scenarios back into drafts myself.
- **Source**: agent (metacomm)

Metacomm contradiction check: nenhuma intenção existente em `product-design-as-intended.md` (D-001 a D-005) conflita; D-004 (`apprentice`) e D-005 (`literature-reviewer`) tratam de presets e ficam fora de escopo, como no roadmap-000006.

## Review log

**Review depth:** Deep. Gate: 11 steps (<= 12) mas ~25 arquivos distintos (> 8), e o item mexe no comportamento default de todos os projetos que usam o SEJA. Override: auto=deep, floor=light, flag=none, effective=deep. Phase 1 inline e Phase 2 inline nos três Deferred com risco; o agente `plan-reviewer` não foi lançado (plano gerado em subagente isolado, mesmo critério dos 000007 a 000014). Prefixo FEATURE-O sem linha na tabela de atalhos: usei DX, TEST, COMPAT, ARCH, SEC, UX, OPS, DATA.

### Step metadata validation
- Todo step tem Files, References, Interface, Verify, Tests, checkbox; `Depends on` só aponta para trás (1 -> 2 -> 3 -> 4 -> 5/6 -> 7 -> 8/9 -> 10 -> 11); `Interface:` presente (N/A onde não há contrato novo).
- Nenhum step toca mais de 5 arquivos (Steps 6 e 8 e 9 tocam 5; o Step 8 prevê divisão em 8a/8b se os ponteiros dos cinco quickguides estourarem o limite).
- `Tests:` não-N/A (Steps 3, 4, 5, 6, 9) expressam comportamento observável ("when X, returns Y"); `Tests: N/A` só em Steps 1, 2, 7, 8, 10, 11 (estado, documento, medição, ensaio) com motivo.
- Caminhos do open-seja **não verificados** (submodule vazio): o Step 1 é o portão e para se um plano anterior não executou.

### Phase 1 -- Perspective scan

| Perspective | Status | Concern |
|---|---|---|
| DX | Adopted | `--reconcile` em frase curta com motivo; guia pt-BR em uma tela; cada step com Verify por comando. |
| TEST | Adopted | Teste primeiro nos steps com código; integração por papéis roteirizados; fixtures de projeto existente no Step 9; Steps documentais declaram `Tests: N/A`. |
| COMPAT | Adopted | v1 válido; `run_all_checks` condicional; upgrade em quatro projetos, duas vezes, comparando byte a byte; `scenarios_approved` sem mudar de significado. |
| ARCH | Adopted | Acoplamento por CLI/JSON versionado; `/implement` -> `drift_report.py` por uma linha, falha não reprova; gate e hooks intocados. |
| SEC | Adopted | `--reconcile` só escreve sob `features/<slug>/` sem seguir `..`; upgrade não executa conteúdo de projeto; C1 por `git grep` nos Steps 2, 8, 9, 10, 11; fixtures fictícias; sem chaves nem `.env`. |
| UX | Adopted | Mensagens em pt-BR e voz controlada; sem chave nova; explicação de bloqueio do Stop hook; aprovação humana mantida. |
| OPS | Adopted | Versão e CHANGELOG preparados, publicação fora; sem push; sem tag. |
| DATA | Adopted | M1 imutável e hash das entradas; reconciliação preserva lock e restante do arquivo byte a byte. |
| PERF, DB, API, I18N, A11Y, VIS, RESP, MICRO | N/A | Sem superfície relevante (I18N: só a Decisão pendente 4, forma do guia pt-BR). |

### Phase 2 -- Deep-dives

| Concern deferred | Resultado |
|---|---|
| COMPAT: o upgrade rodar os `check_*.py` novos sem argumentos em todo projeto (lacuna 5) | Mudança no plano: Step 6 vira pré-requisito do Step 9 e testa o modo sem argumentos em quatro projetos; Decisão pendente 8 registra a escolha. |
| OPS: bump de versão sem publicar pode ser confundido com release | Mudança no plano: Step 9 proíbe tag e push e verifica por `git tag`/`git log origin..HEAD`; publicação é do designer. |
| UX: reconciliação escrever em `intent.md` sem o citizen ver | Sem mudança: a saída do `--reconcile` lista o que mudou em frase curta, a grill mostra o aviso ao reabrir (texto em `grill-phase.md`, Step 3) e o campo `draft` é valor já aceito. |

**Conflict check:** COMPAT (nenhuma chave) x DX (atalho para pular a escada): resolvido a favor de COMPAT e da decisão fechada "sem preset"; a saída é `--light`/tipo de tarefa (Decisão pendente 3). Iterações: 1 (Phase 2 acima); nenhuma amendment adicional.

### Riscos e lacunas registrados
- Caminhos e CLIs do open-seja não verificados; o Step 1 é o portão. Em particular, o achado do `run_all_checks` (lacuna 5) vem da cópia v0.9.1 local.
- Fricção do citizen só é medida no piloto; este plano não acrescenta passo ao ciclo.
- Prova de upgrade usa clone local como `--remote`; não prova o comportamento contra o remoto público (isso é do `/publish` e do designer).
- Duas decisões deixadas ao designer podem mudar o escopo dos Steps 3 (valor gravado) e 8 (forma do guia).

### Execution Metrics
| Metric | Value |
|---|---|
| Review depth | Deep |
| Phase 1 perspectives | 8 adopted, 8 N/A |
| Phase 2 deep-dives | 3 (2 com mudança no plano) |
| Iterations | 1 |
| Pending decisions | 8 (defaults = recomendações) |

## Outcomes

- Emendas aditivas ao contrato, ao layout (`scenarios.lock.json`, `drift/`, `gate.json.build`) e ao formato de plano (chave de cenário e proxy do skip).
- `check_specify.py --reconcile` e `scenarios_state` na matriz: o campo `scenarios:` deixa de mentir e nenhum consumidor decide só por ele.
- `/implement` congela o M1 ao fim do plano v2; falha do freeze nunca reprova o `/implement`.
- Quatro checks novos no `run_all_checks`, condicionais (`pulado` sem `features/`), com teste em quatro projetos.
- Ordem de edição dos `SKILL.md` consolidada, `skill-body-length` medido e dentro do tier.
- `/help` e guia pt-BR em voz controlada com o diagrama da escada, ponteiros nos quickguides.
- Prova de upgrade por tag em quatro projetos existentes (inclusive v1), versão e CHANGELOG prontos para o designer publicar.
- H-009 e D-NNN coerentes entre os oito planos; follow-up do Stop hook como medição com gatilho; tabela de entrega ao item 10 (piloto).

smoke: false
