# Plan 000022 | FEATURE-O | 2026-10-07 15:37 UTC | specify-switch: interruptor da specify por projeto e escolha por plano | Review: deep
plan_format_version: 2
Specify: skipped -- tarefa sem código: plano de harness (contrato, skills, verificadores e guias do próprio open-seja); os testes estão no Verify de cada step

> Item 11 do roadmap-000006 (adendo 2026-10-07, Wave 4b; Depends on: default-cycle-wiring = plan-000015). O item 10 (plan-000016) passa a depender deste. **Este plano reabre duas decisões fechadas, a D-009 e o CYC-004.** Por isso os Steps 1 e 2 vêm antes de qualquer mudança, e o Step 3 em diante só anda se o designer registrou a revisão no `/design`. Até lá, D-009 e CYC-004 valem como estão. Tudo precisa sair **antes da tag v0.11.0**.

## User brief

> sim, registre no inbox e vamos trabalhar em adicionar a um plano e adendo ao roadmap 6

Contexto da mesma conversa (2026-10-07), nas palavras do designer:

> acho que faz sentido um preset ou um parametro no plan. pode ser que o dev esteja em um estágio de prototipação e não faz sentido materializar tantos artefatos e acabar escrevendo mal os requisitos e gherking

> olha, assumindo que vamos usar o open-seja para fazer experimentos, eu fico curioso de ver se é válido ou não habilitar o gherking e fazer experimentos: um time usa o outro nao e medimos a velocidade/entendimento/qualidade do que foi construido. neste caso estou pendendo mais para um opt-out e um preset a ser decidido no setup/design. ao mesmo tempo, como usuário do seja, eu posso querer ainda sim escolher escrever a fase de especificação individualmente para cada plano

Respostas do designer na grill (2026-10-07):

- Valor quando o projeto não declara: **perguntar no setup e no upgrade**; enquanto não há resposta, vale `on`.
- Grill com a specify desligada, em tarefa com código: **entrevista curta** (as quatro linhas de `## Intenção` no plano, sem `intent.md` nem REQ IDs).

## Intenção
- Objetivo: cada projeto escolhe se a especificação em Gherkin é o padrão, e cada plano pode ligar ou desligar a fase com o motivo registrado.
- O que você vê no fim: `SPECIFY_DEFAULT` no `conventions.md`, perguntado no setup e no upgrade; `/plan --with-specify` e `/plan --no-specify "<motivo>"`; um relatório de aderência que separa a leitura por intenção de tratar e por protocolo.
- Não faz: não cria preset, não muda a escada quando a specify está ligada, não reescreve planos v1 nem v2 existentes.
- Pronto quando: o designer registrou a revisão da D-009 e do CYC-004, os testes do harness passam e o `run_all_checks.py` não tem falha nova.

## Agent interpretation

**Problema.** A D-009 e o CYC-004 tornam a escada obrigatória em toda tarefa com código: só se pula a specify por tipo de tarefa, e a "escolha livre" foi rejeitada. Isso deixa sem saída quem está prototipando, a não ser o `--light`, que tira o plano inteiro do ciclo. E o braço de controle do piloto (tag anterior pinada) confunde o Gherkin com tudo o que mudou entre as tags.

**Abordagem.** Dois níveis, uma gramática:

- **Projeto:** variável `SPECIFY_DEFAULT: on | off` em `conventions.md`. Ausente = `on`. `/seja-setup` (install e upgrade) pergunta e grava.
- **Plano:** `/plan --with-specify` liga a fase quando o default é `off`; `/plan --no-specify "<motivo>"` desliga quando é `on`. Quando a fase não roda numa tarefa com código, a grill faz a entrevista curta.
- **Gramática do pulo:** `Specify: skipped -- <classe>: <motivo>`, com três classes: `tarefa sem código` (a de hoje; PFS-013 continua exigindo `Tests: N/A`), `default off` e `opt-out` (as duas novas; aceitam `Tests:` não-N/A). Um motivo sem classe é lido como `tarefa sem código`, para os planos v2 que já existem.
- **Medida:** `cycle_adherence.py` lista os planos v2 com o braço do projeto e a classe de cada plano, e reporta as duas leituras (por intenção de tratar e por protocolo) e a taxa de desvio. O `drift-control-protocol.md` passa a usar a mesma tag com `off` como braço de controle.

**Alternativas rejeitadas.**
- Preset: a D-003 diz que preset não bifurca o ciclo, e um preset é escolhido por projeto e fixado no pin, não por plano.
- Reusar `--specify` para ligar a fase: hoje a flag quer dizer "rodar só a fase specify, avulsa" (SPC-016). Mudar o sentido quebraria quem já a usa. Por isso a flag nova é `--with-specify`.
- Grill completa com a specify desligada: escolha do designer (entrevista curta).
- Medir só por intenção de tratar: esconde se a escada funciona quando é escrita (Q4: o que não foi medido aparece como `não medido`).

## Files

| File | Steps |
|---|---|
| `_output/tmp/design-rascunho-specify-switch-2026-10-07.md` (create) | 1 |
| `product-design/product-design-as-intended.md` (designer, via `/design`) | 2 |
| `.claude/references/general/extended-cycle-contract.md` | 3 |
| `.claude/references/general/grill-phase.md` | 3 |
| `.claude/references/general/specify-phase.md` | 3 |
| `.claude/references/general/plan-from-scenarios.md` | 3 |
| `.claude/references/template/conventions.md` | 4 |
| `product-design/conventions.md` | 4 |
| `.claude/skills/scripts/project_config.py` | 4 |
| `.claude/skills/scripts/check_plan_scenarios.py` | 5 |
| `.claude/skills/scripts/tests/test_check_plan_scenarios.py` and `tests/fixtures/plan_scenarios/` | 5 |
| `.claude/skills/plan/SKILL.md` | 6 |
| `.claude/skills/_internal/plan/standard/SKILL.md` | 6 |
| `.claude/skills/_internal/seja-setup/install/SKILL.md` | 7 |
| `.claude/skills/_internal/seja-setup/upgrade/SKILL.md` | 7 |
| `.claude/skills/scripts/cycle_adherence.py` (create) and `tests/test_cycle_adherence.py` (create) | 8 |
| `.claude/references/general/drift-control-protocol.md` | 8 |
| `.claude/skills/scripts/drift_report.py` and its test | 9 |
| `docs/how-to/ciclo-default.pt-BR.md`, `.claude/skills/plan/SKILL-quickguide.md`, `.claude/skills/help/SKILL.md` | 10 |
| `.claude/skills/scripts/tests/test_default_cycle_wiring.py`, `CHANGELOG.md` | 11 |

## Best practices

- Mudanças aditivas no contrato, marcadas "emenda 000022", como o 000015 fez com "emenda 000015".
- Nenhum plano existente é reescrito (T3). Os planos v2 com motivo sem classe continuam válidos.
- A prosa no as-intended é do designer (T4). O agente escreve só o rascunho em `_output/tmp/`.
- C4 em toda AskUserQuestion nova (setup e upgrade).
- Q1: `pytest .claude/skills/scripts/tests/` verde e `run_all_checks.py` sem falha nova. A linha de base pós-merge é 18/15, e a falha conhecida de `check_human_markers_only` é a do bug que o plan-000019 Step 4 corrige.

## Design decisions

- **User-visible impact:** quem instala ou atualiza o SEJA responde a uma pergunta a mais ("a especificação em Gherkin é o padrão neste projeto?"). Quem planeja ganha duas flags. Quem tem `on` e não usa flag não vê diferença.
- **Trade-offs accepted:** a escada deixa de ser obrigatória, e H-009 passa a ser medida em duas leituras com viés de seleção na leitura por protocolo. Em troca, o controle fica na mesma tag e a prototipação deixa de produzir Gherkin ruim.
- **Metacommunication impact:** eu passo a te dizer "você escolheu pular a especificação neste plano porque <motivo>" e "neste projeto a especificação está desligada; para ligá-la neste plano, use `--with-specify`". O relatório de aderência te mostra quantas vezes o default foi seguido, sem esconder o desvio.

## Steps

### Step 1: **[AGENTE]** Rascunho da revisão para o `/design`
Escrever `_output/tmp/design-rascunho-specify-switch-2026-10-07.md` com: a nova D-NNN que substitui a D-009 (contexto, decisão, consequências, alternativas rejeitadas, incluindo "sem chave" com o motivo de agora: o controle por tag confunde a variável; e a consequência nova: o upgrade grava `SPECIFY_DEFAULT` em `conventions.md` só depois de resposta explícita); a revisão da D-005 (a Decision "pulada por tipo de tarefa" e a alternativa rejeitada "specify por escolha livre"); as emendas ao CYC-004 (três classes de pulo) e ao CYC-033 ("sem chave" e "tag anterior pinada"); o ajuste à refutação de H-009 (leitura por protocolo ao lado da intenção de tratar), dizendo que a leitura por protocolo da divergência por degrau só é mensurável no piloto com oráculo (O1, D3b), porque plano sem specify não tem vetor D, e que os limiares são fixados antes do primeiro dado (Q3); o braço A do `drift-control-protocol.md` passa a ter a entrevista curta e plano v2 `default off` (ameaça à validade declarada). Também as respostas da grill desta data (perguntar no setup e no upgrade, ausente = `on`; entrevista curta). Pedir ao designer três decisões: o nome da flag de desligar (`--no-specify` ou `--without-specify`; recomendação: `--without-specify`, porque `--no-specify` lê como negação de `--specify`, SPC-016); a sequência de release com o plan-000020 (os dois miram a v0.11.0, já cortada no CHANGELOG e sem tag); e o `/design` como segunda porta da escolha (fora do escopo deste plano). Citar o adendo 2026-10-07 do roadmap-000006 e a nota do inbox do Doutourado como fonte. Sem nomes de pessoa (C2).
- **Files**: `_output/tmp/design-rascunho-specify-switch-2026-10-07.md` (create)
- **References**: `product-design/product-design-as-intended.md` (D-003, D-005, D-008, D-009, H-009), `.claude/references/general/extended-cycle-contract.md` (CYC-004, CYC-033), `.claude/references/general/drift-control-protocol.md`, roadmap-000006 (adendo 2026-10-07)
- **Interface**: N/A
- **Verify**: o arquivo existe; `grep -c` acha D-009 (>= 2), D-005, CYC-004, CYC-033 e H-009 (>= 1 cada); `git status --porcelain product-design/` vazio; nenhum nome de pessoa (C2).
- **Tests**: N/A (rascunho de prosa para o designer)
- **Scenarios**: N/A (plano de harness, Specify skipped)
- [x] Done

### Step 2: **[DESIGNER]** Registrar a revisão no `/design`
O designer roda `/design` no open-seja a partir do rascunho do Step 1 e decide. **Aprova:** a nova D-NNN fica registrada com STATUS, a D-009 recebe o marcador `superseded`, a D-005 é revisada como o designer decidir (marcador ou D-NNN nova) e o CYC-004 passa a ter as três classes. O designer decide também o nome da flag de desligar e a sequência de release com o plan-000020; se a sequência for "os dois na v0.11.0", os Steps 3 a 11 terminam antes do Step 11 do plan-000020 (tag v0.11.0). **Recusa ou muda:** o plano para aqui e volta para `/plan`. O agente não escreve prosa no as-intended (T4).
- **Files**: `product-design/product-design-as-intended.md` (designer)
- **References**: rascunho do Step 1
- **Depends on**: Step 1
- **Interface**: o número da nova D-NNN (provavelmente D-011), citado nos Steps 3, 10 e 11; o nome final da flag de desligar (Steps 3, 6, 10, 11); a versão-alvo (Step 11).
- **Verify**: `grep -n "^### D-0" product-design/product-design-as-intended.md` mostra a nova D-NNN; a D-009 tem marcador `superseded` acima do heading; `check_human_markers_only.py` não acusa prosa de agente.
- **Tests**: N/A (decisão humana)
- **Scenarios**: N/A (plano de harness, Specify skipped)
- [x] Done

### Step 3: Emendas ao contrato, à grill, à specify e ao formato de plano
Cinco referências, só acréscimos marcados "emenda 000022", cada emenda ao contrato com a linha "Ruptura que pode provocar" (CYC-014). (1) `extended-cycle-contract.md`: emenda ao CYC-004 (classes `tarefa sem código`, `default off`, `opt-out`; motivo sem classe = `tarefa sem código`); um CYC novo para o interruptor (`SPECIFY_DEFAULT`, ausente = `on`, flags `--with-specify` e a flag de desligar decidida no Step 2; desvio sempre registrado; linha `Specify default:` no cabeçalho); emendas ao CYC-018, ao CYC-029, à seção Compatibilidade (tabela "Regra de versão": com `default off` ou `opt-out`, `Tests:` não-N/A é permitido com `Scenarios: N/A (motivo)`), à linha 2 de "Decisões pendentes" e ao CYC-033 (a chave existe; o braço de controle é a mesma tag com `off`), citando a nova D-NNN. Sem regex no contrato (CYC-019). (2) `grill-phase.md`: duas linhas novas na tabela da GRL-012 ("tarefa com código e specify desligada: entrevista curta, `## Intenção` no plano, sem pasta"; "specify desligada e `--with-specify`: rodadas até P1 a P6, como feature com código"). (3) `specify-phase.md`: emenda ao SPC-002 (a specify também não roda por `default off` ou `opt-out`; roda com `--with-specify`). (4) `plan-from-scenarios.md`: a gramática (`skipped -- tarefa sem código[: <motivo>]`, `skipped -- default off[: <motivo>]`, `skipped -- opt-out: <motivo>` com motivo que passa no PFS-007; qualquer outro motivo = `tarefa sem código`), a linha `Specify default: on|off` (ausente = `on`), o alcance da PFS-013 (só `tarefa sem código`), a PFS-016 e as chaves novas do `--json`. (5) `template/plan-step.md`: a frase "With `Specify: skipped`, no step has non-N/A `Tests:`" ganha a ressalva das duas classes novas. Nenhuma referência escreve `${SPECIFY_DEFAULT}`; o nome aparece só entre crases (o `check_conventions.py` não pode falhar em projeto antigo).
- **Files**: `.claude/references/general/extended-cycle-contract.md`, `.claude/references/general/grill-phase.md`, `.claude/references/general/specify-phase.md`, `.claude/references/general/plan-from-scenarios.md`, `.claude/references/template/plan-step.md`
- **References**: nova D-NNN (Step 2)
- **Depends on**: Step 2
- **Interface**: a gramática fica em `plan-from-scenarios.md` (não no contrato, CYC-019): `opt-out` exige motivo; `default off` e `tarefa sem código` aceitam motivo opcional; o que não casa com uma classe e casa com o `SKIPPED_RE` atual é `tarefa sem código`. Cabeçalho: `Specify default: on|off`.
- **Verify**: `git diff --numstat` dos cinco arquivos com 0 remoções; `grep -c "emenda 000022"` >= 1 em cada um dos cinco; no contrato, cada bloco "emenda 000022" tem uma linha "Ruptura que pode provocar"; `grep -rn '${SPECIFY_DEFAULT}' .claude/` vazio; `check_features.py`, `check_intent.py`, `check_specify.py` e `check_conventions.py` continuam passando no `run_all_checks.py`.
- **Tests**: N/A (documento normativo; os validadores dos Steps 4, 5, 8 e 9 têm os testes)
- **Scenarios**: N/A (plano de harness, Specify skipped)
- [ ] Done

### Step 4: `SPECIFY_DEFAULT` nas convenções e um leitor
Acrescentar a linha `SPECIFY_DEFAULT` (valores `on`/`off`; vazio = `on`) ao template `.claude/references/template/conventions.md` (placeholder `{{SPECIFY_DEFAULT}}`) e ao `product-design/conventions.md` do open-seja (`on`). Em `project_config.py`, função `specify_default(root: Path | None = None) -> str` que devolve `"on"` ou `"off"`. Ela lê `<root>/product-design/conventions.md` (e a pasta legada `project-design/`) diretamente, sem o cache de módulo e sem cair no template (`root` ausente = `REPO_ROOT`). Ela aceita o valor com ou sem crases, por um regex próprio da linha `SPECIFY_DEFAULT`, para que um `off` sem crases não vire `on` em silêncio. Arquivo ausente, linha ausente, valor vazio ou placeholder `{{...}}` = `"on"`. Outro valor levanta `ValueError` em pt-BR com o valor lido.
- **Files**: `.claude/references/template/conventions.md`, `product-design/conventions.md`, `.claude/skills/scripts/project_config.py`, `.claude/skills/scripts/tests/test_project_config.py`
- **References**: `upgrade_harness.py` (`diff_conventions` já avisa variável ausente)
- **Depends on**: Step 3
- **Interface**: `project_config.specify_default(root=None) -> "on" | "off"`
- **Verify**: `pytest .claude/skills/scripts/tests/test_project_config.py` verde; `check_conventions.py` sem falha nova.
- **Tests**: `.claude/skills/scripts/tests/test_project_config.py`: casos `specify_default` para arquivo ausente, linha ausente, vazio, placeholder `{{SPECIFY_DEFAULT}}`, `on`, `off`, `off` sem crases, inválido (`ValueError`), e `root` de fixture diferente do `REPO_ROOT`
- **Scenarios**: N/A (plano de harness, Specify skipped)
- [ ] Done

### Step 5: `check_plan_scenarios.py` lê a classe do pulo
Função pública `skip_class(value) -> (classe | None, motivo)`, o parser único da classe, importado por `build_checks.py`, `drift_report.py` e `cycle_adherence.py`. PFS-002 aceita as três classes e o motivo sem classe (legado = `tarefa sem código`); `opt-out` sem motivo, ou com motivo que não passa no `reason_ok`, é erro. Nova leitura do cabeçalho `Specify default: on|off` (ausente = `on`; outro valor = PFS-002). PFS-013 passa a valer só para `tarefa sem código`; com `default off` ou `opt-out`, step com `Tests:` não-N/A precisa de `Scenarios: N/A (motivo)` e não pode ter chave. Nova PFS-016 (info), sem ler `conventions.md`: dispara quando a classe contraria a linha `Specify default:` do próprio plano (`opt-out` com `on`; `approved` com `off`), dizendo "leitura por protocolo: este plano conta como desvio do default"; `default off` com `Specify default: on` é erro (incoerência do cabeçalho). `--json` ganha `skip_class`, `skip_reason` e `specify_default` (aditivo; `schema_version` igual, documentado em "Esquema de `--json`"). Atualizar a tabela PFS no docstring.
- **Files**: `.claude/skills/scripts/check_plan_scenarios.py`, `.claude/skills/scripts/tests/test_check_plan_scenarios.py`, `.claude/skills/scripts/tests/fixtures/plan_scenarios/` (pastas novas `pfs-016-opt-out-com-testes`, `pfs-016-default-off-com-testes`, `pfs-002-opt-out-sem-motivo`, `pfs-002-default-off-com-cabecalho-on`, `pfs-013-sem-classe-legado`, e as linhas novas na tabela do `README.md`)
- **References**: `plan-from-scenarios.md` (Step 3)
- **Depends on**: Steps 3, 4
- **Interface**: `check_plan_scenarios.skip_class(value)`; `--json` -> `{"skip_class": ..., "skip_reason": ..., "specify_default": "on" | "off", ...}`
- **Verify**: `pytest .claude/skills/scripts/tests/test_check_plan_scenarios.py .claude/skills/scripts/tests/test_build_checks.py` verde; todas as fixtures existentes de `plan_scenarios/` (inclusive `pfs-002-skipped-*`, `pfs-013-*`, `v2-skipped`, `ref-b-sem-codigo`) com o `esperado.json` igual; `python3 .claude/skills/scripts/check_plan_scenarios.py _output/plans/plan-000022-specify-switch.md` sai 0; `python3 .claude/skills/scripts/check_plan_scenarios.py` (scan) sai 0.
- **Tests**: `test_check_plan_scenarios.py`: `skip_class` para as três classes, o legado (com e sem acento, com parênteses) e o vazio; uma fixture por PFS novo ou alterado (lista em Files); `--json` com `skip_class`, `skip_reason`, `specify_default`
- **Scenarios**: N/A (plano de harness, Specify skipped)
- [ ] Done

### Step 6: As flags no `/plan`
`plan/SKILL.md`: `--with-specify` e a flag de desligar no `argument-hint`, na tabela de flags e no Mode Detection (não são overrides de modo; seguem para o standard). `_internal/plan/standard/SKILL.md`, passos 2b e 2c: ler `SPECIFY_DEFAULT` (via `project_config.specify_default`) e gravar `Specify default: on|off` sob o cabeçalho de todo plano v2 novo. A classificação "sem código" tem precedência e dá `tarefa sem código` em qualquer default. Com `off` e sem `--with-specify`, ou com `on` e a flag de desligar, a tarefa com código recebe a entrevista curta e a linha `Specify: skipped -- default off` ou `Specify: skipped -- opt-out: <motivo>`; os steps de código podem ter `Tests:` reais com `Scenarios: N/A (specify desligada neste plano)` (trocar a frase "every step has `Tests: N/A`" do passo 2b). Com `off` e `--with-specify`, a grill completa e a specify rodam como hoje. O motivo vira uma linha (quebra de linha vira espaço) e precisa passar no `reason_ok`; motivo ausente ou fraco é recusado em uma frase. As duas flags juntas, ou uma delas com `--light`, `--grill`, `--specify` ou `--roadmap`, são recusadas em uma frase; os planos gerados por um roadmap herdam o default do projeto. `--with-specify` com `on` e a flag de desligar com `off` não fazem nada e não avisam. `--specify` (fase avulsa, SPC-016) não muda. Acrescentar a linha 8 (000022) à tabela "Ordem de edição dos `SKILL.md`" do contrato.
- **Files**: `.claude/skills/plan/SKILL.md`, `.claude/skills/_internal/plan/standard/SKILL.md`, `.claude/references/general/extended-cycle-contract.md` (só a linha da tabela "Ordem de edição")
- **References**: CYC novo (Step 3), GRL-012 emendada
- **Depends on**: Steps 3, 4, 5
- **Interface**: `/plan <brief> [--with-specify | --no-specify "<motivo>"]` (o nome da segunda flag é o decidido no Step 2); cabeçalho `Specify default: on|off`
- **Verify**: `check_skill_spec.py` e `check_skill_system.py` sem falha nova; `grep -n "with-specify\|no-specify"` (ou o nome decidido) acha as duas flags nos dois `SKILL.md`; `grep -c "every step has \`Tests: N/A\`"` no standard = 0; `python3 .claude/skills/scripts/check_docs.py --plugins skill-body-length --verbose` com `plan` abaixo de 90% do tier (hoje 72/500); a tabela "Ordem de edição" tem a linha 000022.
- **Tests**: N/A (instrução de skill; a fiação é testada no Step 11)
- **Scenarios**: N/A (plano de harness, Specify skipped)
- [ ] Done

### Step 7: O setup e o upgrade perguntam
`install/SKILL.md`: uma AskUserQuestion (C4) depois de preencher as convenções: "A especificação em Gherkin é o padrão neste projeto?", com opções `on` (Recommended when o projeto vai medir a escada ou já tem requisitos estáveis) e `off` (Recommended when o projeto está em prototipação); gravar em `conventions.md`. `upgrade/SKILL.md`, passo 8 ("New convention variables"): se `SPECIFY_DEFAULT` está ausente depois do `diff_conventions`, fazer a mesma pergunta (C4); gravar a linha em `product-design/conventions.md` **só** com resposta explícita, com o valor entre crases; em modo não interativo, em `--dry-run` ou sem resposta, não gravar e dizer "vale `on` até você responder". O `upgrade_harness.py` não muda (continua sem tocar em `conventions.md`).
- **Files**: `.claude/skills/_internal/seja-setup/install/SKILL.md`, `.claude/skills/_internal/seja-setup/upgrade/SKILL.md`
- **References**: `.claude/references/general/constraints.md` (C4)
- **Depends on**: Step 4
- **Interface**: N/A
- **Verify**: `grep -n "SPECIFY_DEFAULT"` acha a pergunta nos dois arquivos; `check_skill_system.py` sem falha nova; `pytest tests/compat/test_upgrade_compat.py` verde (prova que o script de upgrade não grava em `conventions.md` e que o conjunto de falhas do `run_all_checks.py` não muda num projeto antigo sem a linha); a regra "não grava sem resposta" no texto da skill é testada no Step 11.
- **Tests**: N/A (instrução de skill; compat no Verify, texto testado no Step 11)
- **Scenarios**: N/A (plano de harness, Specify skipped)
- [ ] Done

### Step 8: Relatório de aderência e o braço de controle
Criar `cycle_adherence.py`, instrumento de **aderência**, não de desfecho. Ele faz a própria varredura de `PLANS_DIR` (via `project_config`, ou `--root`): todos os `plan-*.md`, inclusive DONE, sem `-progress` e `-qa-`, nos dois formatos de nome (6 dígitos e ULID, D-010). A classe vem de `check_plan_scenarios.skip_class` (import, como o `build_checks.py`). Definições: elegível = v2 com `approved`, `default off` ou `opt-out`; braço atribuído (ITT) = linha `Specify default:` do plano (ausente = `on`); tratamento recebido (por protocolo) = escada se `approved`, sem escada se `default off` ou `opt-out`; desvio = braço `on` com `opt-out`, ou braço `off` com `approved`. Não elegível = `tarefa sem código` (contagem própria); v1 = `não medido` (Q4); REVOKED e SUPERSEDED listados à parte; proposals de `${PROPOSALS_DIR}` contadas como `fora do ciclo` (a rota `--light`). Identidade: elegíveis + não elegíveis + v1 + revogados ou substituídos = total de planos. Desfecho por plano: o vetor por degrau só quando existe `features/<slug>/drift/M1.json`; nos outros, `não medido` com a razão; nenhum número agregado (D-007). Saída em tabela pt-BR e `--json`: `{"planos": [...], "itt": {"on": {...}, "off": {...}}, "por_protocolo": {"escada": {...}, "sem_escada": {...}}, "desvio": {"n": N, "elegiveis": M, "motivos": [...]}, "nao_elegiveis": N, "nao_medido": N, "fora_do_ciclo": N, "revogados": N}`. `--since YYYY-MM-DD` filtra pela data do cabeçalho do plano (não pelo `features/adoption.json`, que um projeto `off` nunca escreve). Emendar `drift-control-protocol.md`: braço A = mesma tag com `off` (entrevista curta, plano v2 `default off`, `Tests:` por step); seção 9 com a ameaça "o controle tem entrevista curta, o contraste deixa de ser H-008"; o retrofit da seção 4 vale para plano v2 `default off`; a leitura por protocolo da divergência é feita só com o oráculo (O1, D3b), e os limiares são fixados antes da primeira execução (Q3).
- **Files**: `.claude/skills/scripts/cycle_adherence.py` (create), `.claude/skills/scripts/tests/test_cycle_adherence.py` (create), `.claude/references/general/drift-control-protocol.md`
- **References**: `check_plan_scenarios.skip_class` (Step 5), `project_config`
- **Depends on**: Step 5
- **Interface**: `python3 .claude/skills/scripts/cycle_adherence.py [--json] [--since YYYY-MM-DD] [--root PATH]`
- **Verify**: `pytest .claude/skills/scripts/tests/test_cycle_adherence.py` verde; na fixture, elegíveis + não elegíveis + v1 + revogados = total de arquivos de plano, e ITT (on + off) = por protocolo (escada + sem escada) = elegíveis; v1 aparece como `não medido` e o DONE é contado; `python3 .claude/skills/scripts/cycle_adherence.py --json` roda no próprio open-seja e sai 0; `git diff --numstat .claude/references/general/drift-control-protocol.md` com 0 remoções.
- **Tests**: `.claude/skills/scripts/tests/test_cycle_adherence.py`: ledger de fixture com um plano de cada classe nos dois braços, um com desvio em cada braço, um DONE, um REVOKED, um v1, um nome ULID, uma proposal e um plano sem `Specify default:` (lido como `on`); identidade de contagem; `--since`; desfecho `não medido` sem `drift/M1.json`
- **Scenarios**: N/A (plano de harness, Specify skipped)
- [ ] Done

### Step 9: `drift_report.py` diz por que não há escada
Hoje `--plan` com `Specify: skipped` reporta "não aplicável" com a razão `NM-SPECIFY-PULADA`. Passar a ler a classe por `check_plan_scenarios.skip_class` (sem regex próprio) e a dizer a classe e o motivo, em voz controlada (DRP-013): "Você escolheu não escrever a especificação neste plano: <motivo>." ou "A especificação está desligada neste projeto.", com as razões novas `NM-SPECIFY-OPT-OUT` e `NM-SPECIFY-DEFAULT-OFF` no JSON, documentadas em `drift-report.md`. `tarefa sem código` continua com `NM-SPECIFY-PULADA` e a mesma saída.
- **Files**: `.claude/skills/scripts/drift_report.py`, `.claude/skills/scripts/tests/test_drift_report.py`, `.claude/references/general/drift-report.md`
- **References**: `skip_class` (Step 5)
- **Depends on**: Step 5
- **Interface**: razões `NM-SPECIFY-OPT-OUT`, `NM-SPECIFY-DEFAULT-OFF`
- **Verify**: `pytest .claude/skills/scripts/tests/test_drift_report.py` verde; a fixture `tests/fixtures/drift_report/specify-pulado/esperado.json` não muda (a saída de `tarefa sem código` é igual byte a byte); `grep -n "NM-SPECIFY-OPT-OUT\|NM-SPECIFY-DEFAULT-OFF" .claude/references/general/drift-report.md` acha as duas.
- **Tests**: `test_drift_report.py`: um caso por classe (`opt-out` com motivo, `default off`, `tarefa sem código`), checando a frase e a razão NM no JSON
- **Scenarios**: N/A (plano de harness, Specify skipped)
- [ ] Done

### Step 10: Guias e ajuda
`docs/how-to/ciclo-default.pt-BR.md`: substituir a frase "Não existe chave para desligar o ciclo. Uma chave escondida mudaria a medida da escada sem deixar registro." por uma que aponte para a seção nova; seção "Ligar e desligar a especificação" (o interruptor, as duas flags, quando usar cada uma, a linha `Specify default:`, como o desvio aparece no relatório; prototipação como exemplo). `plan/SKILL-quickguide.md`: as duas flags. `help/SKILL.md`: uma linha.
- **Files**: `docs/how-to/ciclo-default.pt-BR.md`, `.claude/skills/plan/SKILL-quickguide.md`, `.claude/skills/help/SKILL.md`
- **References**: nova D-NNN, Steps 6 e 8
- **Depends on**: Steps 6, 7, 8, 9
- **Interface**: N/A
- **Verify**: `grep -n "with-specify"` acha a flag nos três; `grep -c "Não existe chave para desligar o ciclo" docs/how-to/ciclo-default.pt-BR.md` = 0; `check_docs.py` e `check_skill_system.py` sem falha nova.
- **Tests**: N/A (documentação)
- **Docs**: os três arquivos.
- **Scenarios**: N/A (plano de harness, Specify skipped)
- [ ] Done

### Step 11: Fiação, CHANGELOG e portão final
`test_default_cycle_wiring.py`: casos novos: o template tem `SPECIFY_DEFAULT`; `plan/SKILL.md` e o standard citam as duas flags; o standard grava `Specify default:`; o `upgrade/SKILL.md` diz que não grava sem resposta; `cycle_adherence.py` existe e roda; `build_checks.py route` sobre um plano `opt-out` com `Tests:` real dá steps `no-scenario` com as ações TDD e preâmbulo sem `check-specify-status` (o `/implement` trata o plano sem mudança, CYC-020). `CHANGELOG.md`: se `git tag -l v0.11.0` estiver vazio, acrescentar a entrada à seção `## [v0.11.0]` já cortada (sem bump), citando a nova D-NNN e dizendo que a D-009 foi substituída, e corrigir as frases "needs no switch" e "does not touch [...] `conventions.md`" dessa seção; se a tag existir ou o Step 2 tiver escolhido outra versão, parar e perguntar ao designer (C4) antes de escrever. Rodar o portão de Q1.
- **Files**: `.claude/skills/scripts/tests/test_default_cycle_wiring.py`, `CHANGELOG.md`
- **References**: constitution Q1, `tools/release-process.md`
- **Depends on**: Steps 1 a 10
- **Interface**: N/A
- **Verify**: `pytest .claude/skills/scripts/tests/` e `pytest tests/compat/test_upgrade_compat.py` verdes; `python3 .claude/skills/scripts/run_all_checks.py` com no máximo as 15 falhas da linha de base pós-merge e nenhuma nova; `check_version_changelog_sync.py` no mesmo estado ou melhor; `git tag -l v0.11.0` ainda vazio no fim deste plano (a tag é do Step 11 do plan-000020).
- **Tests**: `.claude/skills/scripts/tests/test_default_cycle_wiring.py`: os casos novos listados acima
- **Scenarios**: N/A (plano de harness, Specify skipped)
- [ ] Done

## Riscos

- **A escolha livre esvazia o ciclo.** Mitigação: o motivo é obrigatório e a taxa de desvio é reportada como achado.
- **Viés de seleção na leitura por protocolo.** Mitigação: a leitura por intenção de tratar ao lado e o crossover do plan-000016.
- **O próprio plano mostra a lacuna.** Ele é um plano de harness com código e testes, mas o PFS-013 de hoje exige `Tests: N/A` com `Specify: skipped`. Os testes estão no Verify. Depois do Step 5, um plano assim poderia usar `opt-out` e declarar `Tests:` de verdade.
- **Colisão de versão.** D-009, plan-000020 e este plano miram a v0.11.0. A sequência é decisão do designer (adendo 2026-10-07).

## Outcomes

- Um projeto declara se a escada é o padrão, e um plano declara quando desvia e por quê.
- O piloto (plan-000016) compara os braços na mesma tag e lê H-009 de dois jeitos.
- Nenhum plano existente muda de validade.

smoke: false

## Metacomm Intention
- **Summary**: Eu deixo você escolher, no projeto e em cada plano, se a sua intenção vira especificação em Gherkin, e te mostro quando e por que você desviou do padrão.
- **Source**: agent

## Review log

**Review depth:** Deep (pedida pelo chamador; o cabeçalho do plano já diz deep)
**Deep-dive budget:** 6/6 used

### Phase 1 -- Perspective Scan (2026-10-07 UTC)

O prefixo FEATURE-O não tem linha na tabela de atalhos de `review-perspectives.md`. Base: a linha CHORE-O/DOCUMENT-O (DX, OPS, COMPAT) mais TEST, que está em toda linha FEATURE. Acréscimos justificados (2):
- **ARCH**, porque o mesmo cabeçalho passa a ser lido por quatro scripts (`check_plan_scenarios.py`, `build_checks.py`, `drift_report.py`, `cycle_adherence.py`) e porque `project_config.py` é o leitor das convenções.
- **DATA**, porque o plano cria um instrumento de medida (ITT, por protocolo, desvio). A integridade e a honestidade do dado são o risco central (Q3, Q4).

| Perspective | Status | Concern |
|-------------|--------|---------|
| TEST | Deferred | Steps 4, 5, 8, 9 e 11 têm testes reais, mas declaram `Tests: N/A` por uma premissa falsa sobre o PFS-013; dispara Phase 2 |
| COMPAT | Deferred | gramática nova do pulo sobre planos v2 e fixtures existentes; várias regras normativas que dizem "sem chave" ou "todo step Tests: N/A" ficam fora da lista de arquivos; dispara Phase 2 |
| ARCH | Deferred | `specify_default(root)` contra o leitor global e com cache do `project_config`; três parsers do mesmo cabeçalho; PFS-016 dependendo das convenções; dispara Phase 2 |
| DATA | Deferred | definições de ITT e por protocolo, elegibilidade, braço por plano, planos DONE, rota `--light`, marca `--since`; dispara Phase 2 |
| OPS | Deferred | v0.11.0 já cortada no CHANGELOG; Step 11 em `[Unreleased]` com `bump: minor`; upgrade que passa a gravar em `conventions.md`; dispara Phase 2 |
| DX | Deferred | nome `--no-specify` ao lado de `--specify` (SPC-016) com outro sentido; combinações de flags não definidas; tabela "Ordem de edição dos SKILL.md"; dispara Phase 2 (iteração 2) |
| SEC | N/A | sem segredo, rede ou superfície nova. O motivo do `--no-specify` vai para o cabeçalho; uma quebra de linha poderia injetar uma segunda linha `Specify:` ou `Feature:` (PFS-002 pega a duplicata). A sanitização de uma linha fica no DX/Step 6 |
| PERF | N/A | o `cycle_adherence.py` faz uma varredura linear dos planos; sem custo relevante |
| DB | N/A | sem banco; os arquivos de `features/` não mudam de esquema |
| API | N/A | sem API HTTP; o `--json` ganha chaves aditivas (tratado em COMPAT) |
| I18N | N/A | mensagens em pt-BR, como os verificadores atuais |
| UX | N/A | sem UI; as mensagens de metacomunicação ficam no DX e no CYC-014 |
| A11Y | N/A | sem UI |
| VIS | N/A | sem UI |
| RESP | N/A | sem UI |
| MICRO | N/A | sem UI |

### Phase 2 -- Deep-dive: TEST (iteration 1, deep-dive 1/6)

**Concern:** todos os steps declaram `Tests: N/A`, "porque o PFS-013 de hoje exige". Os testes ficam só no Verify.
**Step ref:** Steps 4, 5, 8, 9 e 11; seção Riscos, item 3.
**Files read:** `.claude/skills/scripts/check_plan_scenarios.py` (linhas 338-362: `_check_step_common`, `_pfs_no_scenario`), `.claude/references/general/plan-from-scenarios.md` (PFS-013), `.claude/skills/scripts/build_checks.py` (linhas 828-866: `route`), `.claude/references/general/extended-cycle-contract.md` (CYC-020, CYC-029).
**Finding:**
- Com `Specify: skipped`, um step com `Tests:` não-N/A **e** `Scenarios: N/A (motivo)` com motivo válido recebe PFS-013 com gravidade **info**, não erro. Prova: copiei o plano para o scratchpad, troquei o `Tests:` do Step 4 por um teste real e rodei `check_plan_scenarios.py`. Resultado: "0 erros, 1 informação", exit 0. Só com `--strict` o exit é 1. O erro só existe quando falta `Scenarios: N/A (motivo)`.
- Nem o `/implement` nem o `/plan` (passo 4c) usam `--strict`.
- Com `Tests: N/A`, o `build_checks.py route` marca o step como `legacy` (`_LEGACY`), não como `_TDD`. O `/implement` perde o vermelho-verde nos steps de código do próprio plano. O Q1 vira só o portão final.
- O próprio plano é um exemplo do problema que ele resolve: harness com código, classificado como "sem código".
**Recommendation:** declarar `Tests:` reais nos Steps 4, 5, 8, 9 e 11. Manter `Scenarios: N/A (plano de harness, Specify skipped)`, que satisfaz o PFS-013 como info. Os Steps 1, 2, 3, 6, 7 e 10 continuam `Tests: N/A` (prosa, decisão humana ou instrução de skill; a fiação deles é testada no Step 11). O cabeçalho `Specify: skipped -- tarefa sem código: ...` continua válido, mas o item 3 dos Riscos está errado. Isso fica registrado na emenda, já que só a seção Steps muda in place.
**Resolution:** Plan amended -- see Plan Amendment (iteration 1), A1.

### Phase 2 -- Deep-dive: COMPAT (iteration 1, deep-dive 2/6)

**Concern:** a gramática nova do pulo precisa conviver com os planos v2 e as fixtures que já existem. O plano edita só 4 referências e algumas regras com "sem chave" ou "Tests: N/A" ficam de fora.
**Step ref:** Steps 3, 5, 9 e 10.
**Files read:**
- `extended-cycle-contract.md` (CYC-004, CYC-014, CYC-018, CYC-019, CYC-020, CYC-029, CYC-033, Compatibilidade, "Decisões pendentes", "Ordem de edição dos SKILL.md")
- `grill-phase.md` (GRL-012), `specify-phase.md` (SPC-002, linha 382), `plan-from-scenarios.md` (PFS-002, PFS-013)
- `.claude/references/template/plan-step.md:45-50`, `.claude/skills/_internal/plan/standard/SKILL.md:35`
- `drift_report.py:520-537, 720-733`, a lista de fixtures em `tests/fixtures/plan_scenarios/` e o README dela
- `check_conventions.py`, `tests/compat/run_upgrade_compat.py:256-265`
- `grep` das linhas `Specify:` em `_output/plans/` e nas fixtures
**Finding:**
- **Linhas atuais:** `skipped -- tarefa sem código: ...` (7 ocorrências), `tarefa sem código (só documentação)`, `tarefa sem codigo: so documentacao` (sem acento), `tarefa de documentação (DOCUMENT), ...`, `só documentação`, e `skipped --` vazio (a fixture `pfs-002-skipped-sem-motivo`). Com o fallback "sem classe = tarefa sem código", todas mantêm o resultado de hoje. O fallback está correto.
- **Defeito no regex proposto:** `^skipped -- (tarefa sem código|default off|opt-out)(: (\S.*))?$` torna o motivo opcional para todas as classes. Assim `Specify: skipped -- opt-out`, sem motivo, passaria, e isso contradiz "motivo obrigatório" (Riscos, item 1).
- **CYC-019:** "nenhum texto deste arquivo traz [...] regex de validador". O Interface do Step 3 põe o regex no contrato. O regex deve morar em `plan-from-scenarios.md` e no script.
- **CYC-014:** toda emenda ao contrato registra "Ruptura que pode provocar". O Step 3 não pede isso.
- **Textos normativos que contradizem a mudança e ficam fora do plano:**
  - CYC-018 e a seção Compatibilidade, incluindo a tabela "Regra de versão": "em v2 com `Specify: skipped`, nenhum step tem `Tests:` não-N/A".
  - CYC-029: "plano pulado com step de teste e sem N/A justificado sai 1".
  - CYC-033: "Não há chave de ligar ou desligar (`CYCLE_MODE`, `--no-grill`)" e "O braço de controle do piloto usa a tag anterior pinada".
  - A linha 2 da tabela "Decisões pendentes".
  - SPC-002 ("Quando roda").
  - `template/plan-step.md:50`.
  - `_internal/plan/standard/SKILL.md:35` ("every step has `Tests: N/A`"; o Step 6 toca o arquivo, mas não diz que essa frase muda).
  - O guia `docs/how-to/ciclo-default.pt-BR.md:85` ("Não existe chave para desligar o ciclo"; o Step 10 só acrescenta uma seção).
- **GRL-012:** falta a linha "specify desligada, mas `--with-specify`", em que a grill completa precisa rodar, porque a specify exige `intent.md` aprovado.
- **`drift_report.py`:** devolve a razão `NM-SPECIFY-PULADA` para todo pulo. A razão está documentada em `drift-metric.md` e `drift-report.md` e tem fixture `drift_report/specify-pulado/esperado.json`. Sem códigos novos de máquina, o JSON não distingue as classes. Só a frase muda.
- **Variável nova no template:** se alguma referência usar `${SPECIFY_DEFAULT}`, o `check_conventions.py` falha nos projetos antigos que ainda não têm a linha. O `tests/compat` exige o mesmo conjunto de falhas antes e depois do upgrade (`check_set`) e quebraria.
**Recommendation:**
- (a) No Step 3, além das quatro referências: emendas aditivas a CYC-018, CYC-029, CYC-033, Compatibilidade e à linha 2 de "Decisões pendentes", todas marcadas "emenda 000022" e cada uma com "Ruptura que pode provocar". Acrescentar `.claude/references/template/plan-step.md` como quinto arquivo. O regex fica fora do contrato.
- (b) A gramática em `plan-from-scenarios.md`:
  - `opt-out` exige motivo com `reason_ok`, como no PFS-007;
  - `default off` não exige motivo;
  - linha sem classe = `tarefa sem código` (legado).
- (c) GRL-012 com duas linhas novas (off e código: entrevista curta; off e `--with-specify`: grill completa) e SPC-002 emendado.
- (d) No Step 9, códigos `NM-SPECIFY-DEFAULT-OFF` e `NM-SPECIFY-OPT-OUT`, documentados em `drift-report.md`. A saída de `tarefa sem código` fica igual byte a byte, o que a fixture `specify-pulado` prova.
- (e) No Step 10, a frase da linha 85 do guia é substituída.
- (f) Nenhuma referência usa `${SPECIFY_DEFAULT}`: o nome aparece só entre crases.
**Resolution:** Plan amended -- see Plan Amendment (iteration 1), A2.

### Phase 2 -- Deep-dive: ARCH (iteration 1, deep-dive 3/6)

**Concern:** o lugar da função `specify_default`, a forma de leitura e a duplicação do parser do cabeçalho.
**Step ref:** Steps 4, 5, 8 e 9.
**Files read:** `.claude/skills/scripts/project_config.py` (linhas 33-41, 66-150, 193-230), `.claude/references/template/conventions.md:17-19, 102`, `.claude/skills/scripts/upgrade_harness.py:669-700`, `check_plan_scenarios.py:155-181, 560-644`, `build_checks.py:832-866` (já importa `check_plan_scenarios as cps`), `drift_report.py:520-537`.
**Finding:**
- **(1) O lugar está certo.** `project_config.py` é o leitor central das convenções, e o `diff_conventions` do upgrade já usa o mesmo `_ROW_RE`.
- **(2) `_ROW_RE` exige o valor entre crases.** Com `| \`SPECIFY_DEFAULT\` | off | ...`, sem crases, a linha não casa, o valor fica "ausente" e vira `on` em silêncio: o "Looks fine to me" do DX.
- **(3) A falha de leitura do template devolve o placeholder.** Sem `product-design/conventions.md`, `_parse_config` lê o template. O template usa placeholder entre crases (como `MINIMUM_REVIEW_DEPTH`, linha 102), então o valor lido seria `{{SPECIFY_DEFAULT}}` e a função proposta levantaria `ValueError` em todo projeto sem convenções.
- **(4) `get()` lê do `REPO_ROOT` do script, com cache de módulo.** Um verificador chamado com `--root <fixture>` leria as convenções do open-seja. A assinatura `specify_default(root)` do plano está certa, desde que a função leia `root/product-design/conventions.md` (com a pasta legada) diretamente, sem `_ensure_config`.
- **(5) O cabeçalho passaria a ter quatro leitores** (`cps.parse_header`, `drift_report._plan_header` com regex próprio, `build_checks` via cps, `cycle_adherence`). A classe do pulo deve ter uma função só, `cps.skip_class(value) -> (classe, motivo)`, importada pelos outros. É o precedente do `build_checks`.
- **(6) PFS-016 lendo as convenções acopla o verificador ao estado atual do projeto.** Um plano escrito com `off` e lido depois de o projeto voltar para `on` seria acusado de desvio que não houve. A solução: o `/plan` grava `Specify default: on|off` no cabeçalho de todo plano v2 novo. Ausente = `on`, porque antes do 000022 só existia o `on`, então é verdade por construção. O PFS-016 compara classe e linha do próprio plano, e o verificador continua puro. O `SPECIFY_RE` (`^Specify:`) e o regex do `drift_report` não casam `Specify default:`, então a linha nova não colide.
**Recommendation:**
- Step 4: `specify_default(root: Path | None = None) -> Literal["on","off"]`.
  - Lê o arquivo de `root`, sem cache e sem cair no template.
  - Aceita o valor com ou sem crases, por um regex próprio da linha `SPECIFY_DEFAULT`.
  - Ausente, vazio ou placeholder `{{...}}` -> `"on"`.
  - Outro valor -> `ValueError` em pt-BR com o valor lido.
- Step 5: `skip_class` público em cps; linha `Specify default:` definida em `plan-from-scenarios.md` (Step 3) e lida pelo cps; PFS-016 sem leitura das convenções.
- Steps 8 e 9 importam `skip_class`.
**Resolution:** Plan amended -- see Plan Amendment (iteration 1), A3.

### Phase 2 -- Deep-dive: DATA (iteration 1, deep-dive 4/6)

**Concern:** se o instrumento de aderência mede o que diz medir (Q3, Q4), sem perder linhas nem misturar braços.
**Step ref:** Steps 1, 8; Outcomes; Design decisions.
**Files read:** `check_plan_scenarios.py:620-644` (`_is_open_plan`, `_scan`), `.claude/references/general/drift-control-protocol.md` (seções 1, 2, 4, 8, 9, 10), `extended-cycle-contract.md` (CYC-034, adoption.json), `product-design/product-design-as-intended.md` (H-009, linhas 810-815; D-010), roadmap-000006 (Adendo 2026-10-07).
**Finding:**
- **(1) O scan exclui o ledger concluído.** `_is_open_plan` exclui planos com título `DONE|REVOKED|SUPERSEDED` e só aceita `plan-\d{6}-`. Se o `cycle_adherence.py` reusar o scan do cps, perde os planos concluídos, que são o dado principal. E os nomes ULID da D-010 (`plan-20261006-q8zrj4-*`) sumiriam quando o plan-000019 entrar.
- **(2) O braço lido do `conventions.md` atual reclassifica planos antigos** quando o projeto troca o default. Resolvido pela linha `Specify default:` (ARCH).
- **(3) A rota `--light` fica invisível.** O `--light` gera proposal v1 em `${PROPOSALS_DIR}` e é a outra rota para pular a escada (CYC-033). Fora da contagem, a taxa de desvio fica subestimada.
- **(4) Elegibilidade:** `tarefa sem código` não é desvio nem tratamento. Se entrar nos denominadores de ITT ou por protocolo, dilui a taxa.
- **(5) A marca `--since` não é o `adoption.json`.** O plano usa `features/adoption.json` (CYC-034, DRP-014), mas a grill só o escreve ao criar a primeira `features/<slug>/`. Num projeto `off` ele nunca existe. A marca do `--since` deve ser a data do cabeçalho do plano, informada explicitamente.
- **(6) Desfecho (o ponto mais sério).**
  - A leitura por protocolo de H-009 no adendo ("entre os que escreveram, a divergência por degrau não é menor que entre os que pularam") não pode ser medida no ledger. Plano sem specify não tem `features/<slug>/` nem vetor D.
  - Só o piloto com oráculo (O1 e D3b contra o oráculo, `drift-control-protocol.md` seção 4) compara os dois grupos.
  - O `cycle_adherence.py` é instrumento de aderência, não de desfecho. Se o rascunho do Step 1 não disser isso, a condição de refutação fica imensurável fora do piloto (Q3), e o relatório "itt/por_protocolo" sugere um resultado que não mede (Q4).
- **(7) O braço A muda de natureza.** No protocolo de controle, o braço A é "sem grill nem specify; plano v1; v0.10.x". Com `off` na mesma tag, ele passa a ter a entrevista curta e plano v2 `default off`. O contraste deixa de ser "escada x H-008" e vira "escada x entrevista curta". É uma ameaça à validade que precisa ser declarada. O retrofit (seção 4) também precisa valer para plano v2 `default off`.
- **(8) "A soma de ITT e a de por protocolo batem com o total" é ambíguo.**
**Recommendation:**
- **Definições no Step 8 (e no rascunho do Step 1):**
  - elegível = plano v2 com classe `approved`, `default off` ou `opt-out`;
  - braço atribuído (ITT) = `Specify default:` do plano (ausente = `on`);
  - tratamento recebido (por protocolo) = escada se `approved`, sem escada se `default off` ou `opt-out`;
  - desvio = braço `on` com `opt-out`, ou braço `off` com `approved`;
  - não elegível = `tarefa sem código`, listada com contagem própria;
  - v1 = `não medido`;
  - proposals (`--light`) = `fora do ciclo`;
  - REVOKED/SUPERSEDED = listados à parte.
- **Identidade de contagem:** elegíveis + não elegíveis + v1 + revogados/substituídos = total de arquivos de plano; as proposals ficam numa linha à parte.
- **Desfecho:** a coluna mostra o vetor por degrau só onde existe `features/<slug>/drift/M1.json`; nos outros, `não medido` com a razão. Nenhum número agregado (D-007).
- **Varredura própria:** inclui DONE e aceita os dois formatos de nome (D-010).
- **`--since`:** data do cabeçalho.
- **`drift-control-protocol.md`:** braço A redefinido, a ameaça "entrevista curta no braço de controle" na seção 9, o retrofit para v2 `default off` e a regra "limiares da leitura por protocolo fixados antes do primeiro dado" (Q3).
**Resolution:** Plan amended -- see Plan Amendment (iteration 1), A4.

### Phase 2 -- Deep-dive: OPS (iteration 1, deep-dive 5/6)

**Concern:** a sequência da release e o upgrade que passa a gravar em `conventions.md`.
**Step ref:** Steps 7 e 11; Riscos (colisão de versão); cabeçalho do plano ("antes da tag v0.11.0").
**Files read:** `CHANGELOG.md` (linhas 1-40 e a seção `[v0.11.0]`), `.seja-version`, `git tag`, `git log -S"## [v0.11.0]"`, `tools/release-process.md:18-33`, `_output/plans/plan-000020-*.md` (Step 11), `.claude/skills/_internal/seja-setup/upgrade/SKILL.md` (passos 5-8), `tests/compat/run_upgrade_compat.py`.
**Finding:**
- **(1) A v0.11.0 já está cortada.** `CHANGELOG.md` tem `## [v0.11.0] - 2026-10-06` (commit 230955c, "v0.11.0 preparada") e `.seja-version` = `v0.11.0`. A tag `v0.11.0` ainda não existe (`git tag -l 'v0.1*'` lista só v0.10.0 e v0.10.1). O Step 11 grava em `[Unreleased]` com `<!-- bump: minor -->`: pelo `release-process.md`, isso vira a próxima release (v0.12.0), não a v0.11.0. É o contrário do que o cabeçalho do plano exige.
- **(2) As notas da v0.11.0 contradizem o plano.** Dizem "Upgrading [...] needs no switch" e "`/seja-setup --upgrade` does not touch [...] `conventions.md`". A D-009 (Consequences) e o CYC-033 também dizem que o upgrade não toca `conventions.md`. O Step 7 muda isso. A nova D-NNN precisa dizer que o upgrade grava `conventions.md` só depois de resposta explícita.
- **(3) O Step 11 do plan-000020 cria a tag `v0.11.0`.** Os Steps 3-11 deste plano precisam terminar antes dele. Nenhum dos dois planos registra essa dependência.
- **(4) O `tests/compat` não prova a regra do Step 7.** Ele roda o `upgrade_harness.py`, não a skill. A pergunta mora no `SKILL.md`, então a frase do Verify do Step 7 ("o upgrade não grava em `conventions.md` sem resposta") não é provada pelo compat. O compat só prova que o script não grava, o que continua verdadeiro. Falta um teste de texto da skill.
- **(5) O comando do compat fica em outro lugar.** O compat roda em `tests/compat/test_upgrade_compat.py`, fora de `.claude/skills/scripts/tests/`. O Verify precisa nomear o comando.
**Recommendation:**
- Step 11: se `git tag -l v0.11.0` estiver vazio, acrescentar à seção `## [v0.11.0]` existente, sem bump, e corrigir as duas frases citadas. Se a tag existir, parar e perguntar ao designer (C4).
- Step 2: o designer decide também a sequência de release com o plan-000020 (já pedida no adendo).
- Step 7: dizer quando a pergunta acontece (passo 8 do upgrade, em "New convention variables"); gravar só com resposta explícita; não gravar em `--dry-run` nem sem interação. Verify: `pytest tests/compat/test_upgrade_compat.py`.
- Step 11: um teste de texto que acha a regra "não grava sem resposta" no `upgrade/SKILL.md`.
**Resolution:** Plan amended -- see Plan Amendment (iteration 1), A5.

### Conflict Check (iteration 1)

- **ARCH x COMPAT (linha nova `Specify default:` no cabeçalho x "não reescreve planos"):** não há conflito. A linha só entra em planos novos; ausente = `on` é verdade histórica.
- **DATA x COMPAT (varredura própria que inclui DONE x scan do cps só com abertos):** não há conflito. São consumidores diferentes e o cps não muda de semântica.
- **OPS x DX (entrar na v0.11.0 x notas já escritas):** resolvido a favor de OPS. As notas são editáveis enquanto a tag não existe; depois da tag, decide o designer.
- **Inversão de uma resolução anterior:** o review do plan-000015 resolveu "COMPAT (nenhuma chave) x DX (atalho para pular)" a favor de COMPAT. Este plano inverte isso por decisão do designer (adendo 2026-10-07). Fica registrado que a inversão depende do Step 2. Sem aprovação, a resolução anterior continua valendo.

No inter-perspective conflicts remain open after iteration 1.

### Phase 2 -- Deep-dive: DX (iteration 2, deep-dive 6/6)

**Concern:** reavaliar o Step 6 depois das emendas A1-A5: nomes das flags, combinações e a mensagem ao usuário.
**Step ref:** Steps 2, 6 e 10.
**Files read:** `.claude/skills/plan/SKILL.md` (argument-hint, tabela de flags, Mode Detection, C3), `.claude/skills/_internal/plan/standard/SKILL.md` (passos 2b, 2c, 4c), `extended-cycle-contract.md` (CYC-006, "Ordem de edição dos SKILL.md" e medida 72/500), `specify-phase.md` (SPC-016), `grill-phase.md` (GRL-014).
**Finding:**
- **(1) `--no-specify` lê como a negação de `--specify`.** Pela convenção de CLI, `--no-X` nega `--X`. Aqui `--specify` (SPC-016) significa "rodar só a fase specify, avulsa", então `--no-specify` sugere "não rodar a fase avulsa". O par simétrico `--with-specify` / `--without-specify` evita a leitura errada e não tem custo de compatibilidade, porque nenhuma das duas existe ainda. O roadmap diz `--no-specify`, e a decisão do nome é do designer.
- **(2) Combinações não definidas:**
  - as duas flags juntas;
  - uma delas com `--light` (gera proposal v1, fora do ciclo);
  - com `--grill` ou `--specify` (fases avulsas);
  - com `--roadmap` (os planos gerados herdam o default do projeto?);
  - `--no-specify` num projeto `off` (não faz nada? o motivo é descartado?);
  - tarefa sem código num projeto `off` (a classe deve ser `tarefa sem código`, não `default off`, senão polui a elegibilidade).
- **(3) Motivo:** precisa ser de uma linha (a quebra de linha vira espaço; ver SEC na Phase 1) e passar no `reason_ok`. A recusa é uma frase em voz controlada.
- **(4) A regra do contrato ("Ordem de edição dos SKILL.md") pede que o próximo plano que tocar esses arquivos acrescente a sua linha.** O Step 6 não pede isso.
- **(5) O Verify do Step 6 cita "medir `skill-body-length`" sem comando nem limiar.**
- **(6) O roadmap pede a escolha "no `/seja-setup` ou no `/design`".** O plano só cobre o setup. Um caminho pelo `/design` (`/design update stack` grava convenções) fica fora do escopo e deve ser declarado como fora, não omitido.
**Recommendation:**
- Step 2 inclui a decisão do nome (recomendação: `--without-specify`).
- Step 6:
  - define as combinações (as duas flags juntas: recusa; com `--light`, `--grill`, `--specify` ou `--roadmap`: recusa em uma frase; os planos de um roadmap herdam o default);
  - com `off`, `--no-specify` não faz nada e não avisa, como o `--with-specify` com `on`; a classe `tarefa sem código` tem precedência;
  - grava `Specify default:`;
  - acrescenta a linha 8 à tabela "Ordem de edição";
  - Verify com `python3 .claude/skills/scripts/check_docs.py --plugins skill-body-length --verbose`, com `plan` abaixo de 90% do tier.
- O `/design` como segunda porta fica declarado fora do escopo no rascunho do Step 1.
**Resolution:** Plan amended -- see Plan Amendment (iteration 2), A6.

### Conflict Check (iteration 2)

- **DX (`--without-specify`) x roadmap e brief (`--no-specify`):** não é conflito de perspectiva. É uma decisão de nome, devolvida ao designer no Step 2; o plano usa um marcador até lá.
- **DX (recusar combinações) x DATA (registrar todo desvio):** compatíveis. A recusa acontece antes de existir plano, então não há desvio a registrar.

No inter-perspective conflicts detected.

### Execution Metrics

| Metric | Value |
|--------|-------|
| Deep-dives used | 6/6 |
| Iterations completed | 2/3 |
| Perspectives shortlisted | 6 (DX, OPS, COMPAT, TEST + ARCH, DATA) |
| Perspectives Adopted | 6 (depois das emendas A1-A6) |
| Perspectives Deferred (with rationale) | 0 |
| Convergence reason | deep-dive budget (6/6); todos os achados viraram emenda e nenhum Deferred ficou aberto |

Observação: não conferi a linha de base "18/15" do `run_all_checks.py` citada nas Best practices.

### Plan Amendment (iteration 1)

- **A1 (TEST).** Os Steps 4, 5, 8, 9 e 11 passam a declarar `Tests:` reais, mantendo `Scenarios: N/A (plano de harness, Specify skipped)`. O item 3 dos Riscos ("o PFS-013 de hoje exige `Tests: N/A`") está errado: o PFS-013 aceita `Tests:` não-N/A com `Scenarios: N/A (motivo)` como info, com exit 0. Como só a seção Steps muda in place, a correção fica registrada aqui. Motivo: Q1 e o vermelho-verde do `/implement` (`build_checks.py route`: `_TDD` em vez de `_LEGACY`).
- **A2 (COMPAT).**
  - O Step 3 acrescenta emendas aditivas ("emenda 000022") a CYC-018, CYC-029, CYC-033, Compatibilidade, à linha 2 de "Decisões pendentes" e ao SPC-002, cada uma com "Ruptura que pode provocar" (CYC-014). Inclui `template/plan-step.md`. O regex fica fora do contrato (CYC-019).
  - Gramática: `opt-out` exige motivo (`reason_ok`); `default off` não exige; sem classe = `tarefa sem código`.
  - GRL-012 ganha duas linhas.
  - Os códigos `NM-SPECIFY-DEFAULT-OFF` e `NM-SPECIFY-OPT-OUT` entram no `drift_report.py`.
  - A frase "Não existe chave para desligar o ciclo" do guia é substituída.
  - Nenhum `${SPECIFY_DEFAULT}` nas referências.
- **A3 (ARCH).**
  - `specify_default(root=None)` lê o arquivo de `root` sem cache, aceita valor com ou sem crases e trata ausente, vazio ou `{{...}}` como `on`.
  - `cps.skip_class()` é o parser único da classe.
  - Linha nova `Specify default: on|off` no cabeçalho de plano v2 novo (ausente = `on`).
  - PFS-016 compara a classe com essa linha, sem ler as convenções.
- **A4 (DATA).**
  - Definições de elegível, braço atribuído, tratamento recebido e desvio, e a identidade de contagem.
  - Varredura própria que inclui DONE e os nomes ULID (D-010).
  - Proposals como `fora do ciclo`.
  - `--since` pela data do cabeçalho, não pelo `adoption.json`.
  - Desfecho só onde há `drift/M1.json`, nos outros `não medido`.
  - O rascunho do Step 1 diz que a leitura por protocolo de H-009 só é mensurável no piloto com oráculo.
  - `drift-control-protocol.md` redefine o braço A e declara a ameaça "entrevista curta no controle".
- **A5 (OPS).**
  - O Step 11 escreve na seção `[v0.11.0]` existente, sem bump, enquanto a tag não existe, e corrige as notas "needs no switch" e "does not touch conventions.md". Se a tag existir, para e pergunta.
  - O Step 2 inclui a decisão da sequência com o plan-000020. Os Steps 3-11 terminam antes do Step 11 do plan-000020.
  - O Step 7 grava só com resposta explícita; Verify com `pytest tests/compat/test_upgrade_compat.py` e teste de texto no Step 11.
  - O rascunho do Step 1 também revisa a D-005 (Decision e Rejected Alternatives) e o CYC-033, não só a D-009 e o CYC-004.

### Plan Amendment (iteration 2)

- **A6 (DX).**
  - O Step 2 inclui a decisão do nome da flag de desligar (recomendação: `--without-specify`, simétrico a `--with-specify`; `--no-specify` lê como negação de `--specify`, SPC-016). Até a decisão, o plano usa `--no-specify` como marcador.
  - O Step 6 define as combinações:
    - as duas flags juntas: recusa;
    - com `--light`, `--grill`, `--specify` ou `--roadmap`: recusa em uma frase; os planos de um roadmap herdam o default;
    - `--no-specify` com `off` e `--with-specify` com `on`: não fazem nada e não avisam;
    - a classe `tarefa sem código` tem precedência.
  - Motivo de uma linha e `reason_ok`.
  - O Step 6 grava `Specify default:` e acrescenta a linha 8 à tabela "Ordem de edição dos SKILL.md".
  - Verify com o comando do `skill-body-length`.
  - O `/design` como segunda porta da escolha fica fora do escopo, declarado no rascunho.

### Registros fora da seção Steps (iteration 1)

- Riscos, item 3: a premissa sobre o PFS-013 está errada (A1). O PFS-013 aceita `Tests:` não-N/A com `Scenarios: N/A (motivo)` como informação.
- Files: ganham `template/plan-step.md` (Step 3), `extended-cycle-contract.md` (Step 6), `drift-report.md` (Step 9), `test_build_checks.py` (Verify do Step 5) e `tests/compat/test_upgrade_compat.py` (Verify dos Steps 7 e 11).
- Outcomes, item 2: "lê H-009 de dois jeitos" vale só no piloto com oráculo (A4); fora dele, o `cycle_adherence.py` mede aderência, não desfecho.
- Cabeçalho do plano: "antes da tag v0.11.0" continua valendo; a seção `[v0.11.0]` do CHANGELOG já foi cortada sem tag (A5).
