# Plan 000020 | FEATURE-X | 2026-10-07 00:05 UTC | PKB inbox automatico, as-expressed em H-005, release e upgrade do Doutourado | Review: deep
plan_format_version: 1
source: inbox (Doutourado) 2026-10-06-ideia-open-seja-chat-para-inbox-e-live-communicate.md -- captura da ideia e da lacuna, mesma conversa

## User brief

"vamos gerar um plano? para executar tudo de uma vez"

Brief passado ao /plan (resumo das tres mensagens anteriores, nota do inbox como fonte):

> Executar de uma vez a ideia capturada em ../inbox/2026-10-06-ideia-open-seja-chat-para-inbox-e-live-communicate.md: (1) o open-seja produz automaticamente o inbox da PKB: toda fala do humano que alimenta um artefato SEJA (brief de /plan, pergunta de /research, palavras do /reflect) vira nota Markdown de captura em inbox/, derivada do conversation-trace/briefs (nao uma quarta fonte de verdade), com o mascaramento de segredos valendo para a nota; o /seja-setup passa a poder instanciar a camada PKB (inbox/, logs/, Templates/, Objetivos.md, index.md e as 5 skills de manutencao, molde do plan-000072 do Doutourado a partir do bootstrap personal_knowledge_base_bootstrap); e um live communicate no inbox a partir dos itens ligados a um /communicate; decidir no plano a forma (post-skill, /communicate --live ou preset pkb). (2) Registrar a lacuna na fundamentacao: as-expressed como quarto estado de H-005, e limiar + gatilho que levem deriva grande ao /design em vez do /plan (marcadores/apensamento ao as-intended so apos confirmacao). (3) Publicar a tag v0.10.1 do open-seja e fazer o upgrade do harness do Doutourado (hoje .seja-version v0.9.1 do upstream) para o open-seja via /seja-setup --upgrade com --dry-run antes, preservando as 5 skills PKB locais, conventions.md e os sources.txt do pegasus.

Palavras do designer na conversa de origem (verbatim, 2026-10-06): "ok, parece plausivel. o open-seja produz automaticamente o inbox da pkb. depois vamos ter que atualizar o seja no doutourado [...] temos que fazer o upgrade para o open-seja"; "esta faltando o /design no ciclo quando o as-expressed, as-intended e as-coded divergem muito".

## Agent interpretation

**Problem.** O humano fala com o harness em linguagem natural e essas palavras (as-expressed) so sobrevivem no `conversation-trace.jsonl` e no `briefs.md`, dois registros de maquina que ninguem percorre historicamente. O metodo PKB (GTD: capturar antes de classificar) pede que elas virem notas de inbox legiveis por data; o open-seja nao tem camada PKB nem a instancia; e nenhum ponto do ciclo compara as-expressed com as-intended nem leva deriva grande ao `/design`. Em paralelo, o Doutourado continua pinado no SEJA upstream v0.9.1 e nao recebe nada disso ate migrar para o open-seja.

**Approach.** Tres frentes num plano so, nesta ordem de dependencia:

1. **Camada PKB como template + script deterministico, acionado pelo post-skill.** Template `.claude/references/template/pkb/` (inbox/, logs/, Templates/, Objetivos.md, index.md e as 5 skills de manutencao, portadas do Doutourado). Script `pkb_inbox.py` com `init` (instancia a camada, idempotente), `capture` (gera a nota de inbox a partir do trace + brief da invocacao, re-aplicando o mascaramento de `check_secrets.SECRET_PATTERNS`) e `digest` (regenera `inbox/_live.md`, o "live communicate": indice vivo das capturas com os artefatos e as comunicacoes ligadas). O post-skill ganha a etapa 7f `pkb-capture`, que roda capture + digest **sempre que `inbox/` existir no projeto**: a existencia da pasta e o interruptor; nao ha flag nem perfil. O `/seja-setup` ganha `--pkb` (e a pergunta no fluxo interativo de install/here/demo) e passa a preservar a camada no upgrade.
2. **Lacuna na fundamentacao, preparada para o /design.** O agente nao escreve prosa no as-intended (T4). O plano produz um rascunho em `_output/tmp/` com: emenda a H-005 (as-expressed como quarto estado; lacuna 1 dividida em 1a nao capturavel e 1b comparavel), Q-014 (limiar e gatilho do /design), e uma proposta de D-NNN fixando o limiar **antes** de ver os dados (Q3). O sinal deterministico que o plano entrega e o **residuo do degrau zero**: `capture` compara a fala capturada com o `## User brief` do plano gerado e marca `as_expressed_igual_ao_brief: false` quando o agente parafraseou; o post-skill, na etapa 2c (design-intent reminder), recomenda `/design` em vez de `/plan` quando o limiar de `conventions.md` (`DESIGN_TRIGGER_DRIFT_ITEMS`, vazio = desligado) e cruzado pelo relatorio de deriva do `/implement`.
3. **Release e upgrade.** O release segue `tools/release-process.md` (build_dist_branch, tag, push so com confirmacao). O upgrade do Doutourado roda do repositorio pai com `--dry-run` antes, seguido de `pkb_inbox.py init` (que encontra a camada ja existente e so acrescenta o que falta) e `run_all_checks.py`.

**Alternatives rejected.**
- *Preset `pkb` (molde de D-003)*: preset e um ponto da escala H-001, com voz e comandos proprios; o inbox e saida do ciclo para qualquer posicao da escala. Um preset tambem nao chegaria ao Doutourado pelo `--upgrade`.
- *`/communicate --live`*: comunicacoes sao snapshots imutaveis em `_output/` (T3) e saem do envelope so depois do `/critique` (P-005). Um "live" dentro de `_output/` violaria a imutabilidade; fora dele, e exatamente o `inbox/_live.md`, que e preparacao, nao emissao.
- *Inbox como quarta fonte de verdade* (o agente escrevendo direto a nota durante a skill): duplicaria trace e briefs e perderia o mascaramento feito na escrita do trace. A nota e sempre derivada.
- *Aplicar a emenda a H-005 e Q-014 por marcador*: `apply_marker.py` nao tem marcador para hipotese nem para questao aberta, e `CHANGELOG_APPEND` rejeita ids `H-NNN`/`Q-NNN`. Criar um marcador novo so para isso e decisao de design, nao detalhe deste plano.
- *Publicar v0.10.1 sem este plano e fazer dois upgrades*: dobra o custo do upgrade cross-repo. Ver decisao de versao abaixo.
- *Camada PKB em `_output/`*: o inbox e do humano e deve ficar na raiz do projeto, legivel pelo Obsidian; `_output/` e ledger do agente.

## Files

open-seja (este repositorio):
- `.claude/references/template/pkb/` (create): `inbox/README.md`, `logs/README.md`, `logs/log.md`, `Objetivos.md`, `index.md`, `Templates/{Diario,Paper,Projeto,Resumo semanal,Resumo mensal,Resumo trimestral}.md`, `skills/{daily-log,weekly-review,compress,next-action,process-inbox}/SKILL.md` (+ `SKILL-quickguide.md` quando existir na origem)
- `.claude/skills/scripts/pkb_inbox.py` (create); `.claude/skills/scripts/tests/test_pkb_inbox.py` (create); `.claude/skills/scripts/tests/test_conversation_trace.py` (create)
- `.claude/skills/scripts/conversation_trace.py` (modify: subcomando `list --led-to-skill`)
- `.claude/skills/post-skill/SKILL.md` (modify: etapas 2c e 7f, tabela `--deferred`, checkpoint)
- `.claude/skills/seja-setup/SKILL.md`, `.claude/skills/_internal/seja-setup/{install,here,demo,upgrade}/SKILL.md`, `.claude/skills/seja-setup/detect_setup_state.py`, `.claude/skills/scripts/upgrade_harness.py`, `.claude/skills/scripts/tests/test_upgrade_harness.py` (modify)
- `.claude/references/template/conventions.md`, `product-design/conventions.md` (modify: linhas `PKB_DIR`, `DESIGN_TRIGGER_DRIFT_ITEMS`)
- `_output/tmp/design-rascunho-as-expressed-2026-10-06.md` (create)
- `CHANGELOG.md`, `CHEATSHEET.md`, `.claude/rules/harness-structure.md`, `docs/pkb-layer.md` (create/modify); `.seja-version`
- `inbox/` do proprio open-seja (create, via `init`, dogfooding)

Doutourado (repositorio pai, `..`): `.seja-version`, `.claude/**` (via `--upgrade`), `inbox/README.md`, `inbox/_live.md`, `logs/log.md` (linha de registro). Nada em `pegasus/`, `product-design/` ou submodules.

## Best practices

- Scripts do harness so com stdlib; deterministicos; saida `--json` com `schema_version`; exit codes 0/1/2 (standards.md § Backend > 5, 8, 12).
- Teste-primeiro com `tmp_path` e o padrao `_runner` de `tests/test_pending.py` para scripts que passam por `project_config` (standards.md § Testing).
- Mascaramento na fonte **e** na derivacao: a nota re-aplica `SECRET_PATTERNS`; se algo for mascarado na derivacao, a nota recebe `mascarado: true` e o post-skill avisa (checklist K, M).
- Frontmatter PKB das notas novas: `origem`, `tipo`, `tags`, `data` (convencao do plan-000072 do Doutourado), mais `fonte` (evt_ids e brief), `skill`, `artefato`.
- Nenhum nome de pessoa ou instituicao conveniada no template nem nos docs (C2); a origem das skills e citada como "Doutourado, plan-000072" e o bootstrap pela URL publica.
- UTF-8, sem travessao tipografico, nomes de arquivo em minusculas no ledger; os templates de nota mantem os nomes com espaco do bootstrap (`Resumo semanal.md`) porque o Obsidian e os links existentes dependem deles.
- Release: nunca `push` sem confirmacao explicita; `build_dist_branch.py --dry-run` antes do real; `--check` depois (release-process.md).

## Design decisions

**User-visible impact.** Depois de cada skill, aparece uma nota nova em `inbox/` com as palavras que o humano digitou, a data, a skill e o artefato que nasceu delas, e `inbox/_live.md` se atualiza com o indice cronologico e os links para comunicacoes que citam o mesmo artefato. `/seja-setup` passa a oferecer a camada PKB; o upgrade nao a apaga. Quando o relatorio de deriva cruza o limiar fixado pelo humano, o post-skill recomenda `/design`. Nada disso acontece em projetos sem `inbox/`.

**Trade-offs accepted.**
- Interruptor por existencia de pasta (sem flag): simples e visivel no filesystem; em troca, apagar `inbox/` desliga a captura silenciosamente (o post-skill imprime uma linha quando pula a etapa).
- A nota e derivada do trace: se a sessao nao registrou o trace (`session_id` null), a captura usa so o brief e marca `fonte: briefs`; perde a fala literal, declara a perda.
- Limiar `DESIGN_TRIGGER_DRIFT_ITEMS` nasce vazio: o gatilho so funciona depois que o designer fixar o valor (Q3 da constituicao). O plano entrega o mecanismo e o rascunho da decisao, nao a decisao.
- **Versao do release.** O brief diz "publicar v0.10.1", que e o valor atual de `.seja-version` ainda nao taggeado. Este plano adiciona funcionalidade (etapa de post-skill, flag de setup, script novo): pelo release-process e MINOR, logo o release que contem este plano e **v0.11.0**, e o Doutourado faz um upgrade so. Se o designer preferir publicar v0.10.1 antes, sem a camada PKB, o Step 11 roda duas vezes (v0.10.1 e depois v0.11.0) e o Step 12 tambem.
- Copiar as 5 skills PKB para o template: elas passam a ser distribuidas pelo open-seja e refrescadas no upgrade (sao `.md`); a versao do Doutourado sera sobrescrita pela do template no upgrade. Por isso o Step 2 porta **a partir** do Doutourado, para que a primeira copia seja identica e o upgrade seja no-op.

**Metacommunication impact.** Eu passo a lhe devolver, em nota legivel por data, as palavras que voce me disse antes de qualquer artefato, para que voce percorra o que pediu e compare com o que registrei e construi. Quando o que eu registrei se afasta demais do que voce pediu, eu lhe digo que e hora de mudar a intencao, nao so o codigo. E eu digo quando nao capturei (sem trace) e quando mascarei algo.

## Steps

### Step 1: Template da camada PKB: notas-raiz e templates de nota
Criar `.claude/references/template/pkb/` com os arquivos que `pkb_inbox.py init` copiara para a raiz de um projeto. Conteudo: `inbox/README.md` (o que e o inbox, regra "tudo entra aqui antes de ser classificado", frontmatter esperado, aviso de que `_live.md` e gerado), `logs/README.md` e `logs/log.md` (cabecalho e formato `## [YYYY-MM-DD] skill | descricao`), `Objetivos.md` e `index.md` (esqueletos com uma secao e instrucao de uso), e `Templates/` com os seis templates de nota copiados de `../projetos/personal_knowledge_base_bootstrap/Templates/` (Diario, Paper, Projeto, Resumo semanal, Resumo mensal, Resumo trimestral), com a URL do bootstrap citada no `inbox/README.md` como origem. Texto em pt-BR, voz do harness em primeira pessoa onde couber, sem nomes de pessoa ou instituicao (C2). Todos `.md` para que o upgrade os refresque.
- **Files**: `.claude/references/template/pkb/inbox/README.md` (create), `.claude/references/template/pkb/logs/README.md` (create), `.claude/references/template/pkb/logs/log.md` (create), `.claude/references/template/pkb/Objetivos.md` (create), `.claude/references/template/pkb/index.md` (create), `.claude/references/template/pkb/Templates/*.md` (create, 6 arquivos copiados)
- **References**: `product-design/standards.md § i18n`, `product-design/constitution.md` (C2)
- **Interface**: N/A
- **Verify**: `ls .claude/references/template/pkb/Templates | wc -l` = 6; `grep -L '^---' .claude/references/template/pkb/Templates/*.md` vazio (todos tem frontmatter); `python3 .claude/skills/design/check_secrets.py` limpo
- **Tests**: N/A (templates Markdown; cobertos pelo teste de `init` no Step 3)
- [x] Done

### Step 2: Template da camada PKB: as 5 skills de manutencao
Portar para `.claude/references/template/pkb/skills/<nome>/` as skills `daily-log`, `weekly-review`, `compress`, `next-action` e `process-inbox` a partir de `../.claude/skills/<nome>/` (Doutourado, plan-000072), copiando `SKILL.md` e `SKILL-quickguide.md`. Reescrever so o que for especifico do Doutourado: referencias a `Objetivos.md`, `index.md`, `logs/`, `inbox/` e `Templates/` continuam relativas a raiz (sao as mesmas); remover mencoes a pastas que so existem la (`projetos/`, `Proposta/`, `2026.x/`, pegasus) trocando por "a estrutura real do seu arquivo"; manter o frontmatter (`context_budget`, `references: []`). Nao copiar para `.claude/skills/` do open-seja em nenhum step deste plano (nem pelo `init` do Step 8, que roda sem `--with-skills`): as skills so entram num projeto via `init --with-skills` ou `/seja-setup --pkb`, e o upgrade nunca as copia nem as apaga (ver A1/A2 em Plan Amendment).
- **Files**: `.claude/references/template/pkb/skills/daily-log/` (create), `.claude/references/template/pkb/skills/weekly-review/` (create), `.claude/references/template/pkb/skills/compress/` (create), `.claude/references/template/pkb/skills/next-action/` (create), `.claude/references/template/pkb/skills/process-inbox/` (create)
- **References**: `product-design/standards.md § Backend > 25` (SKILL.md com frontmatter e quickguide irmao), `product-design/constitution.md` (C2, T5)
- **Depends on**: Step 1
- **Interface**: N/A
- **Verify**: `grep -rn 'projetos/\|Proposta/\|pegasus\|2026\.' .claude/references/template/pkb/skills/` vazio; cada pasta tem `SKILL.md` com frontmatter `name:` igual ao nome da pasta
- **Tests**: N/A (Markdown; a copia e testada no Step 3)
- [x] Done

### Step 3: `pkb_inbox.py init`: instanciar a camada PKB, idempotente
Criar `.claude/skills/scripts/pkb_inbox.py` (stdlib, argparse, bloco `# designer:` e docstring com Invocation/Lifecycle/exit codes). Subcomando `init [--target <dir>] [--with-skills] [--dry-run] [--json]`: copia `template/pkb/` (exceto `skills/`) para a raiz do alvo e, so com `--with-skills`, `template/pkb/skills/*` para `<alvo>/.claude/skills/`, **sem sobrescrever** nada que ja exista (relata `created`/`skipped` por arquivo), cria `inbox/.gitkeep` e `logs/<ano>/.gitkeep`. Le `PKB_DIR` de `conventions.md` via `project_config.get_path` (default `inbox`). Exit 0 ok, 1 erro, 2 uso. Saida `--json` com `schema_version: 1`. Ao fim, imprime em stderr a sugestao de registrar a camada no `CLAUDE.md` do projeto (nao edita `CLAUDE.md`: e preservado e e do humano).
- **Files**: `.claude/skills/scripts/pkb_inbox.py` (create), `.claude/skills/scripts/tests/test_pkb_inbox.py` (create), `.claude/references/template/conventions.md` (modify: linha `PKB_DIR` | `inbox` na tabela Directory Structure), `product-design/conventions.md` (modify: mesma linha)
- **References**: `product-design/standards.md § Backend > 1, 5, 8, 19, 22, 24`, `product-design/standards.md § Testing`
- **Depends on**: Step 1, Step 2
- **Interface**: `pkb_inbox.py init` imprime JSON `{"schema_version":1,"created":[...],"skipped":[...]}`; funcao `init_layer(target: Path, template_root: Path, with_skills: bool, dry_run: bool) -> dict`
- **Verify**: `pytest .claude/skills/scripts/tests/test_pkb_inbox.py -k init` verde; `python3 .claude/skills/scripts/pkb_inbox.py init --dry-run --json` no open-seja lista os arquivos sem criar nada
- **Tests**: quando `init --with-skills` roda num `tmp_path` vazio, cria `inbox/README.md`, `Templates/` com 6 arquivos e `.claude/skills/daily-log/SKILL.md`; quando roda sem `--with-skills`, nada e criado em `.claude/skills/`; quando roda de novo, retorna tudo em `skipped` e nenhum arquivo muda (hash igual); quando `inbox/README.md` ja existe com conteudo proprio, o conteudo e preservado
- **Docs**: entrada no `docs/pkb-layer.md` (Step 10)
- [x] Done

### Step 4: `conversation_trace.py list` e `pkb_inbox.py capture`: a nota de inbox derivada
(a) Em `conversation_trace.py`, adicionar o subcomando `list --session-id <id> [--led-to-skill <skill-id>] [--since-evt <evt_id>] --json` que devolve as entradas da sessao (ja mascaradas na escrita) sem reescrever o arquivo. (b) Em `pkb_inbox.py`, uma unica funcao `pkb_layer_present(repo_root) -> bool`: verdadeira se `PKB_DIR` (via `project_config.get`) resolve para valor nao vazio **e** `<PKB_DIR>/README.md` existe (o arquivo que `init` cria). Linha `PKB_DIR` vazia = camada desligada, mesmo que exista uma pasta `inbox/` de outro uso. Todo subcomando que escreve (`capture`, `digest`) e o post-skill usam esse predicado, e so ele. (c) Subcomando `capture --skill <nome> --artifact <path|id> --session-id <id> [--brief <texto>] [--json]`: reune as falas do humano (`emitter == user`) da sessao ligadas a esta invocacao (`led_to_skill` igual ao skill-id, ou as entradas desde o ultimo `backfill`), mais o brief do `briefs.md`; re-aplica `SECRET_PATTERNS` importado de `design/check_secrets.py` pelo mesmo `sys.path` que `conversation_trace.py` usa (nao copiar a lista) ao texto reunido; se mascarar algo novo, `mascarado: true`; escreve `<PKB_DIR>/YYYY-MM-DD-<skill>-<id>-<slug>.md` com frontmatter `origem: usuario`, `tipo: transitoria`, `tags: [seja, <skill>]`, `data`, `skill`, `artefato` (caminho relativo), `fonte` (lista de evt_ids, ou `briefs` quando o trace nao tem a sessao), `as_expressed_igual_ao_brief: true|false` quando o artefato e um plano: comparacao do texto reunido com o `## User brief` do plano apos normalizar (casefold, espacos colapsados, marcadores de blockquote `> ` e pontuacao final removidos); corpo = as falas em blockquote, em ordem, com hora. Nunca sobrescreve: se o arquivo existe, acrescenta uma secao datada. Se `pkb_layer_present` e falso, nao escreve nada (exit 0, `{"skipped":"no-pkb-layer"}`).
- **Files**: `.claude/skills/scripts/conversation_trace.py` (modify), `.claude/skills/scripts/pkb_inbox.py` (modify), `.claude/skills/scripts/tests/test_conversation_trace.py` (create), `.claude/skills/scripts/tests/test_pkb_inbox.py` (modify)
- **References**: `product-design/standards.md § Backend > 5, 8, 12, 19`, `product-design/security-checklists.md` (K, M)
- **Depends on**: Step 3
- **Interface**: `conversation_trace.list_entries(session_id, led_to_skill=None, since_evt=None) -> list[dict]`; `pkb_inbox.pkb_layer_present(repo_root) -> bool`; `pkb_inbox.capture(skill, artifact, session_id, brief, repo_root) -> dict` com `path`, `fonte`, `mascarado`, `as_expressed_igual_ao_brief`
- **Verify**: `pytest .claude/skills/scripts/tests/test_conversation_trace.py .claude/skills/scripts/tests/test_pkb_inbox.py` verde; `ruff check .claude/skills/scripts/pkb_inbox.py` limpo
- **Tests**: quando o trace tem duas falas de usuario com `led_to_skill = "plan X"` e uma de outra skill, `list --led-to-skill "plan X"` devolve so as duas, em ordem; quando `capture` roda com essas falas e um plano cujo `## User brief` difere so em caixa, espacos e `> `, a nota nasce com `as_expressed_igual_ao_brief: true` e dois blockquotes; quando o brief troca ou acrescenta palavras, `false`; quando o texto reunido contem `ANTHROPIC_API_KEY=sk-...`, a nota contem `[MASKED:` e `mascarado: true`; quando `inbox/` existe mas sem `README.md`, nada e escrito e o JSON diz `skipped`; quando `PKB_DIR` esta vazio em `conventions.md` e `inbox/README.md` existe, nada e escrito; quando o trace nao tem a sessao, a nota nasce com `fonte: briefs`
- **Traces**: REQ-MC-008
- [x] Done

### Step 5: `pkb_inbox.py digest`: o indice vivo (`inbox/_live.md`)
Subcomando `digest [--json]`: regenera `<PKB_DIR>/_live.md` do zero a partir das notas de captura (frontmatter `skill`, `artefato`, `data`): cabecalho fixo (`<!-- gerado por pkb_inbox.py digest -->`) dizendo que o arquivo e gerado, e preparacao e nao emissao (P-005, "nada daqui saiu pelo /critique"), e que o original de cada fala esta na nota; tabela cronologica (data, skill, resumo da primeira linha da fala, link para a nota, link para o artefato); para cada artefato citado por uma comunicacao em `COMMUNICATION_DIR` (busca por `--source`/caminho no cabecalho das `communication-*.md`), coluna "comunicado em" com o link. Determinismo: mesma entrada, mesma saida; ordenacao por nome de arquivo. `_live.md` e o unico arquivo do inbox que o script sobrescreve. Antes de sobrescrever, `digest` confere que o `_live.md` existente comeca pelo cabecalho gerado; se o arquivo existe sem esse cabecalho, sai com exit 1 e a mensagem "inbox/_live.md existe e nao foi gerado por mim; renomeie-o ou remova-o" -- nunca apaga conteudo de outra origem. So roda se `pkb_layer_present`.
- **Files**: `.claude/skills/scripts/pkb_inbox.py` (modify), `.claude/skills/scripts/tests/test_pkb_inbox.py` (modify)
- **References**: `product-design/standards.md § Backend > 8, 19`, `product-design/design-standards.md` (voz, "nao medido" visivel)
- **Depends on**: Step 4
- **Interface**: `pkb_inbox.digest(repo_root) -> dict` com `path`, `count`, `linked_communications`
- **Verify**: `pytest .claude/skills/scripts/tests/test_pkb_inbox.py -k digest` verde; rodar duas vezes seguidas produz bytes identicos
- **Tests**: quando ha tres notas de captura e uma `communication-000007-ACD.md` cujo cabecalho cita o artefato da segunda, `_live.md` lista as tres em ordem de data e so a segunda tem link na coluna "comunicado em"; quando nao ha notas, `_live.md` existe com o cabecalho e a frase "nenhuma captura ainda"; quando `_live.md` existe com conteudo proprio sem o cabecalho, `digest` sai 1 e o arquivo fica identico (hash igual)
- **Traces**: REQ-MC-007, REQ-UX-003
- [x] Done

### Step 6: post-skill: etapa 7f `pkb-capture`, escopo do commit e gatilho de `/design` na 2c
(a) `verify_commit_scope.py`: nova fonte (d) em `build_expected`: se `pkb_inbox.pkb_layer_present(REPO_ROOT)` e verdadeiro, acrescentar `<PKB_DIR>/` como prefixo esperado (import de `pkb_inbox` pelo mesmo `sys.path.insert` ja usado para `project_config`). Corrigir `_normalize` para preservar a barra final (hoje `Path("inbox/").as_posix()` devolve `inbox`, o que impede prefixos via `--always-include`). (b) Em `.claude/skills/post-skill/SKILL.md`, nova etapa **7f pkb-capture**, depois de 7e e antes do commit (8): se `python .claude/skills/scripts/pkb_inbox.py capture --skill <skill> --artifact <id/path> --session-id $CLAUDE_SESSION_ID --json` devolver `skipped`, seguir em silencio (sem linha de saida: a camada e opcional e a maioria dos projetos nao a tem); senao rodar `pkb_inbox.py digest`; se `mascarado: true`, imprimir uma linha de aviso com o caminho da nota. Acrescentar a linha na tabela `--deferred` (skip: o orquestrador de waves nao captura) e o token de checkpoint `7f` (resume de `7e` passa por `7f`, que e idempotente: `capture` acrescenta secao datada em vez de duplicar a nota). (c) Na etapa **2c**: ampliar o gate, hoje "parent `implement` com header DONE", para tambem rodar quando o parent e `plan` e a etapa 7f produziu `as_expressed_igual_ao_brief: false`. Ler `DESIGN_TRIGGER_DRIFT_ITEMS` de `conventions.md`; se nao vazio e, no progress file do plano, a linha gravada por `step_notes.py record --kind drift` disser `<n> itens` com `n >= limiar`, ou se a captura desta invocacao veio com `as_expressed_igual_ao_brief: false` e a skill e `plan`, imprimir "deriva de intencao: <n> itens de deriva (limiar <limiar>) | as-expressed difere do brief -- considere `/design` antes de um novo `/plan`"; se a linha for `drift: not-measured`, imprimir "deriva: nao medida" ao lado; nunca bloquear. (d) Adicionar `DESIGN_TRIGGER_DRIFT_ITEMS` (valor vazio, descricao: "itens de deriva a partir dos quais o post-skill recomenda /design; vazio = desligado; fixar antes de medir (Q3)") nas duas `conventions.md`.
- **Files**: `.claude/skills/scripts/verify_commit_scope.py` (modify), `.claude/skills/scripts/tests/test_verify_commit_scope.py` (create ou modify, conforme exista), `.claude/skills/post-skill/SKILL.md` (modify), `.claude/references/template/conventions.md` (modify), `product-design/conventions.md` (modify)
- **References**: `product-design/standards.md § Backend > 1, 19` (skill orquestra, script executa), `product-design/design-standards.md § 2` ("nao medido" visivel, espelho oferecido), `product-design/constitution.md` (Q3, Q4)
- **Depends on**: Step 5
- **Interface**: `verify_commit_scope.build_expected(...)` passa a incluir `<PKB_DIR>/` quando a camada existe; JSON de saida inalterado
- **Verify**: `pytest .claude/skills/scripts/tests/test_verify_commit_scope.py` verde; `python3 .claude/skills/scripts/run_all_checks.py` sem falha nova; no open-seja apos o Step 8, rodar `pkb_inbox.py capture` + `digest` e `verify_commit_scope.py --skill-type plan --artifact-id 000020` com `inbox/*.md` staged -> `pass: true`; num `tmp_path` sem `inbox/README.md`, a etapa 7f nao imprime nada
- **Tests**: quando `inbox/README.md` existe e `inbox/2026-10-06-plan-000020-x.md` e `inbox/_live.md` estao staged, `check_scope` nao os lista em `unexpected`; quando `inbox/README.md` nao existe, os mesmos arquivos aparecem em `unexpected`; quando `--always-include docs/` e passado, `docs/a.md` staged casa por prefixo (regressao da barra final)
- **Docs**: `docs/pkb-layer.md` e `.claude/CHEATSHEET.md` (Step 10)
- **Traces**: REQ-MC-006
- [ ] Done

### Step 7a: `/seja-setup --pkb` e sinal `has_pkb_layer`
(a) `seja-setup/SKILL.md`: flag `--pkb` na tabela de argumentos. Nos internos `install`, `here` e `demo`, um passo final "camada PKB": se `--pkb`, rodar `pkb_inbox.py init --target <alvo> --with-skills`; senao, AskUserQuestion com opcoes "Instanciar camada PKB" (Recommended when voce quer percorrer historicamente o que pediu ao harness e manter diarios e inbox no proprio repositorio; NOT recommended when o repositorio e compartilhado por um time que nao quer notas pessoais nele) e "Agora nao" (Recommended when voce vai decidir depois; `pkb_inbox.py init --with-skills` roda a qualquer momento). (b) `detect_setup_state.py --json`: sinal `has_pkb_layer`, calculado com o mesmo predicado de `pkb_inbox.pkb_layer_present` (importar, nao reimplementar); nao altera a classificacao de estado.
- **Files**: `.claude/skills/seja-setup/SKILL.md` (modify), `.claude/skills/_internal/seja-setup/install/SKILL.md`, `.claude/skills/_internal/seja-setup/here/SKILL.md`, `.claude/skills/_internal/seja-setup/demo/SKILL.md` (modify), `.claude/skills/seja-setup/detect_setup_state.py` (modify), `.claude/skills/seja-setup/test_detect_setup_state.py` (modify, conforme exista)
- **References**: `product-design/standards.md § Backend > 19, 20`, `.claude/references/general/constraints.md` (decision-point rationale)
- **Depends on**: Step 4
- **Interface**: `detect_setup_state` JSON ganha `signals.has_pkb_layer: bool`
- **Verify**: `pytest .claude/skills/seja-setup/test_*.py` verde; `python3 .claude/skills/seja-setup/detect_setup_state.py --json` no open-seja (antes do Step 8) devolve `has_pkb_layer: false`
- **Tests**: quando o alvo tem `inbox/README.md` e `PKB_DIR` nao vazio, `detect_setup_state` devolve `has_pkb_layer: true`; quando tem `inbox/` sem `README.md`, `false`; o `state` e identico nos dois casos
- **Docs**: `seja-setup/SKILL-quickguide.md` (flag `--pkb`)
- [ ] Done

### Step 7b: upgrade: preservacao defensiva da camada PKB e tabela de classificacao
(a) `upgrade_harness.py`: `is_preserved(rel_path)` (assinatura atual, um argumento) passa a devolver True para caminhos cujo primeiro componente e `inbox`, `logs` ou `Templates`, e para `Objetivos.md` e `index.md` na raiz. Registrar no docstring que e guarda defensiva: `collect_source_files` so le `.claude/` da fonte, logo esses caminhos nunca chegam ao laco de copia hoje. (b) Depois da copia, se `pkb_layer_present(target)`, imprimir "camada PKB detectada: rode `pkb_inbox.py init` para acrescentar templates novos sem sobrescrever". (c) Tabela File Classification do interno `upgrade/SKILL.md`: linha Rules passa a "Yes -- auto-overwritten by `upgrade_harness.py`; review with `git diff` afterwards" (alinhar ao codigo, que sobrescreve `rules/*.md` sem excecao; os dois arquivos de regra sao inventario do harness, nao convencao de projeto); nova linha "PKB layer (`inbox/`, `logs/`, `Templates/`, `Objetivos.md`, `index.md`, `.claude/skills/{daily-log,...}`) | Never (not in source) | Skip; `init` adds missing files only". O passo 8 ("Offer follow-up actions") ganha a oferta de `pkb_inbox.py init` quando `has_pkb_layer`.
- **Files**: `.claude/skills/scripts/upgrade_harness.py` (modify), `.claude/skills/scripts/tests/test_upgrade_harness.py` (modify), `.claude/skills/_internal/seja-setup/upgrade/SKILL.md` (modify)
- **References**: `product-design/standards.md § Backend > 19`, `.claude/skills/scripts/upgrade_harness-rationale.md`
- **Depends on**: Step 4
- **Interface**: `upgrade_harness.is_preserved("inbox/x.md") is True`; demais retornos inalterados
- **Verify**: `pytest .claude/skills/scripts/tests/test_upgrade_harness.py` verde; `python3 .claude/skills/scripts/upgrade_harness.py --from . --target <tmp com inbox/README.md> --new-version vX --dry-run` nao lista nada sob `inbox/`, `logs/`, `Templates/` e imprime a linha "camada PKB detectada"
- **Tests**: `is_preserved` devolve True para `inbox/a.md`, `logs/2026/x.md`, `Templates/Diario.md`, `Objetivos.md`, `index.md` e False para `.claude/skills/plan/SKILL.md` e `docs/a.md`; quando o alvo tem `inbox/README.md`, a saida do upgrade em `--dry-run` contem "camada PKB detectada", senao nao contem
- [ ] Done

### Step 8: Dogfooding: instanciar a camada PKB no proprio open-seja (sem as skills) e capturar esta conversa
Rodar `python3 .claude/skills/scripts/pkb_inbox.py init` (sem `--with-skills`) na raiz do open-seja: cria `inbox/README.md`, `logs/`, `Templates/`, `Objetivos.md`, `index.md`; **nao** cria nada em `.claude/skills/` (as skills PKB nao entram no proprio open-seja nem, por consequencia, em `main` ou nos upgrades). Depois `pkb_inbox.py capture --skill plan --artifact _output/plans/plan-000020-... --session-id <id da sessao de origem, ou "null">` para que a primeira nota do inbox do open-seja seja a conversa que gerou este plano (falas qa-000015..qa-000020 no trace), e `pkb_inbox.py digest`. Conferir que `tools/publish-manifest.txt` **nao** inclui `inbox/`, `logs/`, `Templates/`, `Objetivos.md`, `index.md` (allowlist; confirmar com `build_dist_branch.py --dry-run`) para que as notas pessoais nao vao para `main` (C3). Antes do commit, conferir a nota gerada contra C2 (`grep -i` por nomes de pessoa e instituicoes conveniadas; `dev` e visivel a organizacao) e rodar `check_secrets.py`. `_live.md` e as notas sao versionados em `dev` (sao a navegacao); so o manifesto decide o que sai.
- **Files**: `inbox/` (create, raiz do open-seja), `logs/`, `Templates/`, `Objetivos.md`, `index.md` (create)
- **References**: `product-design/constitution.md` (C2, C3)
- **Depends on**: Step 5, Step 7a
- **Interface**: N/A
- **Verify**: `ls inbox/` mostra a nota `2026-10-06-plan-000020-*.md`, `README.md` e `_live.md`; `ls .claude/skills/ | grep -c 'daily-log\|weekly-review\|compress\|next-action\|process-inbox'` = 0; `python3 tools/build_dist_branch.py --dry-run` nao lista nenhum caminho da camada; `python3 .claude/skills/design/check_secrets.py` limpo; `grep -il 'puc\|tecgraf\|behring' inbox/*.md` vazio
- **Tests**: N/A (execucao de ferramenta; comportamento coberto nos Steps 3-5)
- [ ] Done

### Step 9: Rascunho para o /design: as-expressed em H-005, Q-014 e limiar (decisao do humano)
Escrever `_output/tmp/design-rascunho-as-expressed-2026-10-06.md` com o texto **proposto** para o designer colar via `/design` (o agente nao escreve prosa no as-intended, T4): (1) emenda a H-005 (§3, 2.4): quarto estado **as-expressed** (a fala registrada no trace e na nota de inbox); a lacuna 1 se divide em 1a (as-conceived -> as-expressed, nao capturavel) e 1b (as-expressed -> as-intended, comparavel por texto); condicao de confirmacao e refutacao atualizadas (1b produzindo ajustes de registro vs. toda diferenca tratada como paráfrase inocente); (2) nova linha **Q-014** na tabela de questoes abertas: "a partir de que medida de deriva (itens do relatorio do /explain drift; residuo de 1b) o ciclo volta ao /design em vez de abrir outro /plan, e em que ponto (post-skill 2c, REFLECT)?"; (3) proposta de **D-NNN** fixando o limiar inicial de `DESIGN_TRIGGER_DRIFT_ITEMS` e o numero minimo de planos antes da primeira leitura, redigida para ser decidida antes de ver dados (Q3), com Rejected Alternatives (gatilho so por evento no /implement; so por periodo de 14 dias; LLM julgando a divergencia); (4) linhas de CHANGELOG correspondentes (H-005 revised, Q-014 added, D-NNN added) para o humano apensar a mao, ja que `CHANGELOG_APPEND` nao aceita ids H/Q; (5) nota de que a nota do inbox do Doutourado de 2026-10-06 e a fonte verbatim. Registrar a pendencia humana: `python3 .claude/skills/scripts/pending.py add --type design-intent --source plan-000020 --description "Aplicar rascunho as-expressed/Q-014/D-NNN via /design" --if-absent`.
- **Files**: `_output/tmp/design-rascunho-as-expressed-2026-10-06.md` (create), `_output/pending.jsonl` (modify, via script)
- **References**: `product-design/product-design-as-intended.md` (§3 2.4 H-005, Questoes abertas, ## Decisions), `product-design/constitution.md` (T4, Q3)
- **Depends on**: Step 4 (o rascunho cita o campo `as_expressed_igual_ao_brief` como medida de 1b)
- **Interface**: N/A
- **Verify**: arquivo existe, sem travessao tipografico (`grep -P '[\x{2013}\x{2014}\x{201C}\x{201D}]'` vazio), cita H-005, Q-014 e D-NNN; `pending.py status` lista a pendencia; `check_human_markers_only.py` nao e acionado (nada em `product-design/` muda)
- **Tests**: N/A (rascunho de prosa)
- [ ] Done

### Step 10: Documentacao e inventario do harness
Criar `docs/pkb-layer.md` (en-US, para a distribuicao): o que e a camada PKB, como `init`/`capture`/`digest` funcionam, o interruptor por pasta, o que e e o que nao e o `_live.md` (preparacao, nao emissao), o gatilho de `/design` e a linha `DESIGN_TRIGGER_DRIFT_ITEMS`, e a origem do metodo (bootstrap, URL publica). Atualizar `.claude/CHEATSHEET.md` (`--pkb`, `pkb_inbox.py`; criar se nao existir), `.claude/rules/harness-structure.md` (novo script, novo template, etapa 7f), `seja-setup/SKILL-quickguide.md` e `post-skill` quickguide se existir, e `CHANGELOG.md` em `[Unreleased]` com as entradas Added (camada PKB, `--pkb`, `pkb_inbox.py`, `conversation_trace.py list`, etapa 7f) e Changed (preservacao no upgrade; gatilho de /design na 2c). Conferir que `docs/pkb-layer.md` entra no manifesto (`docs/**` ja esta).
- **Files**: `docs/pkb-layer.md` (create), `.claude/CHEATSHEET.md` (modify), `.claude/rules/harness-structure.md` (modify), `CHANGELOG.md` (modify), `.claude/skills/seja-setup/SKILL-quickguide.md` (modify)
- **References**: `product-design/standards.md § i18n`, `product-design/standards.md § Backend > 24, 25`
- **Depends on**: Step 6, Step 7a, Step 7b
- **Interface**: N/A
- **Verify**: `python3 .claude/skills/scripts/run_all_checks.py` sem falha nova; links relativos do `docs/pkb-layer.md` resolvem (`ls` de cada alvo)
- **Tests**: N/A (documentacao)
- **Docs**: este step e a documentacao
- [ ] Done

### Step 11: Release do open-seja (v0.11.0; ver decisao de versao)
Seguir `tools/release-process.md` a partir de `dev` limpo: mover `[Unreleased]` do CHANGELOG para `[v0.11.0] - <data UTC>`, com uma linha de nota no topo da secao: "v0.10.0 e v0.10.1 constam acima com data mas nunca receberam tag; v0.11.0 e a primeira tag depois de v0.9.1 e contem as tres secoes"; gravar `v0.11.0` em `.seja-version`; **nao** alterar `.claude/skills/VERSION` (e a versao interna do harness, `version: 0.7.1`, lida por `read_version`, fora do processo de release; alinhar os dois numeros e decisao separada); commitar em `dev`. Rodar `python3 tools/build_dist_branch.py --dry-run`, depois sem flag, depois `--check` (exit 0). Verificar com `git clone --branch main <repo> /tmp/x && python3 /tmp/x/.claude/skills/seja-setup/detect_setup_state.py` esperando `fresh-download`, e que `inbox/`, `_output/`, `product-design/`, `.seja-version` e `tools/` nao estao no clone, e que `.claude/references/template/pkb/` esta. `git tag -a v0.11.0 main -m "open-seja v0.11.0"`. **Parar e pedir confirmacao** antes de `git push origin dev main v0.11.0`; sem confirmacao, deixar tag e main locais e registrar no progress file que o push ficou pendente (o Step 12 tem caminho local para esse caso). Se o designer tiver optado por publicar v0.10.1 antes (sem este plano), rodar este step primeiro para v0.10.1 a partir do commit anterior ao plano, e depois para v0.11.0.
- **Files**: `CHANGELOG.md` (modify), `.seja-version` (modify)
- **References**: `product-design/constitution.md` (C1, C3), `product-design/security-checklists.md` (P), `tools/release-process.md`
- **Depends on**: Step 8, Step 9, Step 10
- **Interface**: N/A
- **Verify**: `git tag --list v0.11.0` existe; `git log main -1` e o commit de distribuicao; `build_dist_branch.py --check` exit 0; `git diff dev~1 dev -- .claude/skills/VERSION` vazio; apos o push confirmado, `git ls-remote --tags origin v0.11.0` responde
- **Tests**: N/A (processo de release; `build_dist_branch.py` ja tem testes)
- **Deploy**: nenhum servidor; a "implantacao" e a tag no remoto GitHub `PUC-Behring-AI/open-seja` (identico em Linux/Windows)
- [ ] Done

### Step 12: Upgrade do Doutourado para o open-seja e ativacao da camada PKB
No repositorio pai (`cd ..`, branch `main`, arvore limpa exceto a nota do inbox). (0) Fonte: se o push do Step 11 foi confirmado, `SEJA_REMOTE=git@github.com:PUC-Behring-AI/open-seja.git` e `python3 .claude/skills/seja-setup/resolve_seja_version.py --version v0.11.0`; senao, clone local da tag a partir do submodule **sem tocar o checkout dele**: `git clone --depth 1 --branch v0.11.0 ./open-seja /tmp/open-seja-v0.11.0` (nao rodar `git checkout` dentro de `open-seja/`: mover o ponteiro do submodule e parte do commit do designer). (1) Rodar `python3 .claude/skills/scripts/upgrade_harness.py --from <fonte> --target . --new-version v0.11.0 --dry-run`. Nota: e o script **do alvo** (versao v0.9.1 do Doutourado) que roda, como manda o interno `upgrade/SKILL.md` passo 5; as alteracoes do Step 7b nao valem nesta primeira rodada, e a camada PKB da raiz fica intacta de qualquer modo porque nenhuma das duas versoes le fora de `.claude/` da fonte. Ler a lista: deve conter so `.claude/**` do harness (inclui `mob/`, `rules/harness-structure.md` -- inventario do harness, sobrescrito, sem perda de convencao local -- e `references/template/pkb/**`); **nao** pode conter `inbox/`, `logs/`, `Templates/`, `Objetivos.md`, `index.md`, `product-design/`, `pegasus/`, `CLAUDE.md`, nem `.claude/skills/{daily-log,weekly-review,compress,next-action,process-inbox}/` (nao estao na fonte; as versoes locais do Doutourado permanecem); nenhuma skill local e apagada (`_RETIRED_SKILLS` = quickstart, seed, ausentes). Esperar e aceitar o WARN "Variables in template missing from product-design/conventions.md" (`MOB_SESSIONS_DIR`, `GATE_FAST_CMD`, `GATE_FULL_CMD`, `GATE_COMMIT_CMD`, `QUALITY_DIR`, `PKB_DIR`, `DESIGN_TRIGGER_DRIFT_ITEMS`): nada em `product-design/` e alterado por este step; `PKB_DIR` ausente vale `inbox` e o gatilho ausente fica desligado; a adicao das linhas fica para o designer (oferta do passo 8 do interno). (2) Rodar sem `--dry-run`; conferir `.seja-version` = `v0.11.0`. (3) `python3 .claude/skills/scripts/pkb_inbox.py init` (sem `--with-skills`: as skills ja existem; acrescenta `inbox/README.md`, `logs/README.md` se faltarem; tudo o mais `skipped`), depois `pkb_inbox.py capture --skill plan --artifact open-seja/_output/plans/plan-000020-... --session-id null --brief "<primeira linha da nota do inbox de 2026-10-06>"` como verificacao direta (nao invocar uma skill: o post-skill faria o fluxo de commit no repositorio pai), e `digest` (cria `inbox/_live.md` listando as notas existentes e a nova). (4) `python3 .claude/skills/scripts/run_all_checks.py` e `git diff --stat` para revisao. (5) Acrescentar em `logs/log.md`: `## [<data>] skill | seja-setup --upgrade: v0.9.1 (upstream) -> open-seja v0.11.0; camada PKB ativada (inbox automatico)`. (6) Atualizar a secao "SEJA Harness" do `CLAUDE.md` do Doutourado (pin e origem) **so se o designer confirmar**, porque `CLAUDE.md` e humano. O commit no Doutourado e do designer (repositorio pai, remoto institucional); o step termina com `git status --short` para ele revisar, sem `git add` nem `git commit`.
- **Files**: `../.seja-version` (modify), `../.claude/**` (modify, via upgrade), `../inbox/README.md` (create), `../inbox/_live.md` (create), `../inbox/<data>-plan-000020-*.md` (create), `../logs/log.md` (modify), `../CLAUDE.md` (modify, so com confirmacao)
- **References**: `product-design/constitution.md` do Doutourado (T3: nao tocar ChromaDB; S1/S2; C1), `product-design/standards.md § Backend > 22`, `.claude/skills/_internal/seja-setup/upgrade/SKILL.md` (passos 2, 5, 7, 8)
- **Depends on**: Step 11
- **Interface**: N/A
- **Verify**: `cat ../.seja-version` = `v0.11.0`; `git -C .. diff --stat -- .claude/skills/daily-log .claude/skills/weekly-review .claude/skills/compress .claude/skills/next-action .claude/skills/process-inbox` vazio; `git -C .. status --short` nao lista `pegasus/sources.txt`, nada em `product-design/`, nem `open-seja` (ponteiro do submodule inalterado); `ls ../inbox/_live.md ../inbox/README.md`; `run_all_checks.py` no Doutourado sem falha nova; `git -C .. log -1 --format=%H` identico ao valor antes do step (nenhum commit feito pelo agente)
- **Tests**: N/A (operacao cross-repo; os scripts envolvidos foram testados nos Steps 3-7b)
- **Docs**: `../CLAUDE.md` secao "SEJA Harness" (com confirmacao)
- [ ] Done

## Coverage check (advisory)

`check_plan_coverage.py --mode advisory` (2026-10-06): 4/40 requisitos do as-intended rastreados por algum plano (10%). Este plano traca REQ-MC-006, REQ-MC-007, REQ-MC-008 e REQ-UX-003 (Steps 4-6). Os demais avisos (REQ-ENT-*, REQ-UX-001/002/004/005/006, REQ-DELTA-*, REQ-I18N-001) sao anteriores a este plano e ficam para os planos do ciclo default (roadmap-000006).

## Outcomes

- Todo projeto com `inbox/` recebe, ao fim de cada skill, a nota com as palavras do humano, ligada ao artefato, com mascaramento conferido, e um `_live.md` que liga capturas a comunicacoes. Projetos sem `inbox/` nao mudam.
- `/seja-setup` instancia a camada PKB sob demanda (`--pkb` ou pergunta), e o upgrade a preserva.
- O as-expressed passa a existir como registro comparavel; o rascunho para o `/design` (H-005, Q-014, D-NNN com limiar) fica pronto para o designer, com a pendencia registrada.
- open-seja v0.11.0 publicado (push so com confirmacao) e Doutourado migrado do upstream v0.9.1 para o open-seja, com a camada PKB ativa e o inbox automatico funcionando la.
- Nao medido neste plano: a utilidade do inbox (se e processado ou acumula) e o valor do limiar; ambos sao objeto do piloto que o D-NNN do Step 9 fixar.

## Smoke

smoke: false

## Review Log

**Review depth:** Deep (auto=deep: 12 steps, >8 files; floor=light)
**Deep-dive budget:** 6/6 used
**Reviewer:** plan-reviewer agent (depth=deep), 2026-10-06

### Phase 1 -- Perspective Scan (2026-10-06 UTC)

Default shortlist for `FEATURE-X` is SEC, DB, API, ARCH, UX, A11Y, I18N, TEST. The project is a Claude Code harness (Markdown skills + stdlib Python, no web surface), so DB, API and A11Y are N/A. Added with justification: **DX** (new script, new post-skill stage, new `/seja-setup` flag), **COMPAT/OPS** (cross-version upgrade v0.9.1 -> v0.11.0 of a downstream repo; template skill overwrite; release process), **DATA** (verbatim chat text persisted as personal notes). This exceeds the "+2" guideline by one; recorded as an explicit override by the caller.

| Perspective | Status | Concern |
|-------------|--------|---------|
| SEC | Adopted (after deep-dive 1) | Masking re-applied at derivation (`SECRET_PATTERNS`); `briefs.md` is written unmasked so the re-mask is load-bearing; publish manifest is an allowlist so `inbox/`, `logs/`, `Templates/`, `Objetivos.md`, `index.md` never reach `main`. No change needed. |
| DB | N/A | No database; ChromaDB belongs to the downstream project and is untouched. |
| API | N/A | No API surface; CLI contracts covered under DX/TEST. |
| ARCH | Deferred -> amended (deep-dive 2) | Two distribution channels for the 5 PKB skills (template+`init` AND `.claude/skills/**` via dogfooding) collide; `is_preserved()` additions are dead code; `rules/*.md` table/code mismatch. |
| UX | Adopted (with remark) | AskUserQuestion in Step 7 has Recommended/NOT recommended per option; `fonte: briefs`, `mascarado: true` and the `_live.md` header make "nao medido" visible. Remark folded into A5: the "sem inbox/, pulado" line would print on every skill run in every non-PKB project (noise). |
| A11Y | N/A | No UI. |
| I18N | Deferred (rationale, no deep-dive) | `standards.md § i18n` lists SKILL.md under en-US; the 5 PKB SKILL.md are pt-BR and ship on `main` under `template/pkb/skills/`. Declared standards tension, not a regression risk. Exception line added to Best practices (A1) for the designer to accept or reject. |
| TEST | Deferred -> amended (deep-dive 3) | Step 6 `Tests: N/A` hides a required `verify_commit_scope.py` change; Step 7 upgrade test is vacuous; Step 4 "paraphrase" test lacks a normalization rule. |
| DX | Deferred -> amended (deep-dive 6) | `verify_commit_scope.py` cannot allow `inbox/` today; `.claude/skills/VERSION` write in Step 11 is outside the documented release process; Step 6(b) names a "relatorio de deriva" without saying where the number comes from. |
| COMPAT / OPS | Deferred -> amended (deep-dive 4) | Downstream upgrade runs the target's old `upgrade_harness.py`; Doutourado's 5 skills would be overwritten by generalized copies; `rules/harness-structure.md` differs downstream and is overwritten; conventions WARN expected; version decision and `VERSION` file; Step 12 `/help` invocation triggers a post-skill commit in the parent repo. |
| DATA | Deferred -> amended (deep-dive 5) | "existence of `inbox/` is the switch" writes captures into any unrelated `inbox/` and overwrites `inbox/_live.md` there; three different predicates across Steps 4/6/7; privacy of verbatim notes on the org-visible `dev` branch (C2). |
| PERF | N/A | Stdlib scripts over a few Markdown files per invocation. |
| VIS / RESP / MICRO | N/A | No visual surface. |

### Phase 2 -- Deep-dive: SEC (iteration 1, deep-dive 1/6)

**Concern:** Chat text flows from `conversation-trace.jsonl` and `briefs.md` into committed `inbox/*.md`; personal notes must not reach the public `main`.
**Step ref:** Steps 4, 8, 11
**Files read:** `.claude/skills/scripts/conversation_trace.py` (`_mask_message` l.100-113; `_cmd_append` exit 2 on unconfirmed masking), `.claude/skills/design/check_secrets.py` (`SECRET_PATTERNS` l.116; `get_files_to_scan` l.209-237 scans `git ls-files`, so committed inbox notes are scanned), `tools/publish-manifest.txt`, `tools/build_dist_branch.py` (`EXTRA_PATHSPECS`), `product-design/security-checklists.md` (K, M, P).
**Finding:** (1) Trace entries are masked at write time and `message_masked` is recorded, so `list` returns already-masked text; (2) pre-skill's brief logging has no masking path, so Step 4's re-application of `SECRET_PATTERNS` to the brief is the only guard on that half and must stay; (3) `_mask_message` ignores `FALSE_POSITIVE_PATTERNS`, so the derivation may over-mask (conservative; surfaced by `mascarado: true`); (4) the manifest is an allowlist (`.claude/**`, `docs/**`, six root files, `npm/**`), so root-level PKB paths are excluded without any manifest edit; (5) `.seja-version` is excluded from `main`, so the pin never leaks.
**Recommendation:** No change to the plan. Step 4 must import `SECRET_PATTERNS` via the same `sys.path` trick `conversation_trace.py` uses, not a copy of the list (folded into A3).
**Resolution:** No change needed -- status changed to Adopted.

### Phase 2 -- Deep-dive: ARCH (iteration 1, deep-dive 2/6)

**Concern:** Boundary between template, `init`, dogfooding and upgrade for the 5 PKB skills; `is_preserved` semantics; `rules/*.md` classification.
**Step ref:** Steps 2, 7(c), 8, Design decisions (trade-off on copying the 5 skills)
**Files read:** `.claude/skills/scripts/upgrade_harness.py` (`collect_source_files` l.177-251; `is_preserved(rel_path)` l.253-276, single argument, applies only to collected source paths; copy loop l.576-596; `_RETIRED_SKILLS` l.598), `.claude/skills/_internal/seja-setup/upgrade/SKILL.md` (File Classification table l.23-35: Rules "No -- Show diff, manual merge"), `product-design/standards.md § Backend > 1`, `product-design/constitution.md` (T5).
**Finding:** (a) Step 2 says the skills "so entram num projeto via `init`", but Step 8 runs `init` in open-seja itself, which copies them into open-seja's `.claude/skills/`; from then on `collect_source_files` ships them to every upgraded project and `main` carries them. (b) Step 2 rewrites Doutourado-specific references (`projetos/`, `pegasus/`, `Proposta/References/`, `2026.1/`, `AEWSOME_LINKS.md` -- confirmed in `weekly-review/SKILL.md:39`, `process-inbox/SKILL.md:23-25`, `daily-log/SKILL.md:37`, `next-action/SKILL.md:21`), so the copies are **not** identical; the trade-off paragraph's "upgrade seja no-op" is false under (a). (c) `is_preserved` receives only `rel_path` of a *source* file; source never contains root PKB paths, so adding them is defensive dead code; the plan's `is_preserved(path, target)` signature does not match the real one. (d) Code overwrites `rules/*.md` unconditionally while the table says manual merge; Doutourado's `rules/harness-structure.md` differs from open-seja's (harness inventory only), so the overwrite there is safe.
**Recommendation:** Keep the 5 skills **template-only** and make `init` copy them only with `--with-skills` (default on for `/seja-setup --pkb`, off for open-seja's own dogfooding). Keep the `is_preserved` additions but test them as a unit predicate. Align the Rules row to the code.
**Resolution:** Plan amended -- see A1/A2/A6/A7.

### Phase 2 -- Deep-dive: TEST (iteration 1, deep-dive 3/6)

**Concern:** Are `Tests:` entries observable behaviors, and are required test changes hidden behind `N/A`?
**Step ref:** Steps 4, 6, 7
**Files read:** `.claude/skills/scripts/verify_commit_scope.py`, `.claude/skills/scripts/tests/test_upgrade_harness.py` (no `is_preserved` tests exist today), `product-design/standards.md § Testing`.
**Finding:** Steps 3, 4, 5 tests are observable. Step 4's "quando o brief parafraseia, `false`" is not deterministic until the normalization is stated. Step 6 marks `Tests: N/A` but necessarily changes `verify_commit_scope.py` (see DX) and that change needs a positive and a negative test. Step 7's upgrade test ("nao os toca") passes even without the code change because the source never contains those paths.
**Recommendation:** State the normalization in Step 4; give Step 6 explicit tests; rewrite Step 7's test as a unit test on `is_preserved()` plus the `detect_setup_state` signal.
**Resolution:** Plan amended -- see A3, A5, A6.

### Phase 2 -- Deep-dive: COMPAT / OPS (iteration 1, deep-dive 4/6)

**Concern:** Upgrade of Doutourado (pinned upstream v0.9.1) to open-seja v0.11.0; release and version decision; cross-repo commit ownership.
**Step ref:** Steps 11, 12; Design decisions (version)
**Files read:** `tools/release-process.md`, `CHANGELOG.md` (`[Unreleased]` empty; `[v0.10.1]` and `[v0.10.0]` dated 2026-10-04), `git tag --list` (ends at v0.9.1), `.seja-version` (v0.10.1), `.claude/skills/VERSION` (`version: 0.7.1`, frozen since v0.8.0), `upgrade_harness.py` (`read_version`, `write_seja_version`), `_internal/seja-setup/upgrade/SKILL.md` steps 2-8, `resolve_seja_version.py`, Doutourado: `.seja-version` (v0.9.1), `.claude/skills/` (has `publish`, lacks `mob`, has the 5 PKB skills), `.claude/rules/` (`harness-structure.md` differs), `product-design/conventions.md` (lacks `MOB_SESSIONS_DIR`, `GATE_*`, `QUALITY_DIR`), `git submodule status` (open-seja is a submodule at `open-seja/`).
**Finding:** (1) **Version**: v0.10.0 and v0.10.1 were never tagged; this plan adds features, so one MINOR release v0.11.0 containing both untagged sections plus this plan is consistent with `release-process.md` and SemVer, and is the cheaper path downstream (one upgrade). The CHANGELOG should say so. (2) **`VERSION`**: Step 11 writes v0.11.0 into `.claude/skills/VERSION`; that file holds the *internal* harness version, is not mentioned by `release-process.md`, and has been frozen since v0.8.0; writing the public tag there conflates two namespaces. (3) **Which script runs**: the upgrade skill step 5 runs `upgrade_harness.py` from the **target** (Doutourado's v0.9.1 copy); Step 7's changes do not apply to Step 12, though the root PKB layer is safe anyway (old script never walks outside `.claude/`). (4) **Skill overwrite**: with the original plan the 5 Doutourado skills would be replaced by generalized copies; with A2 they are untouched. (5) **Rules**: `harness-structure.md` is overwritten (harness inventory only; safe). (6) **Conventions**: WARN about template variables missing from Doutourado's `conventions.md` must be declared expected. (7) **Source availability**: if the push is not confirmed, `resolve_seja_version.py` cannot see the tag; a local clone of the submodule repo at the tag works and must not check out anything inside the `open-seja/` submodule working tree. (8) **Commit ownership**: Step 12's Verify "invocar `/help` no Doutourado" runs a full post-skill in the parent repo, whose step 8 commits. Verify by calling `pkb_inbox.py capture` directly.
**Recommendation:** Keep v0.11.0; add the CHANGELOG note; drop the `VERSION` write; in Step 12 state which script runs, the expected WARN, the local-clone fallback, and replace the `/help` verification.
**Resolution:** Plan amended -- see A8, A9.

### Phase 2 -- Deep-dive: DATA (iteration 1, deep-dive 5/6)

**Concern:** Switch semantics ("existence of `inbox/`") and privacy of verbatim personal notes.
**Step ref:** Steps 4, 6, 7(b), 8; Design decisions (trade-offs)
**Files read:** `.claude/skills/seja-setup/detect_setup_state.py` (`_collect_signals` l.173-209), `product-design/conventions.md`, Doutourado `inbox/` (two notes, no `README.md`), `product-design/constitution.md` (C2; `dev` is org-visible).
**Finding:** (a) Three different predicates across Steps 4/6/7. A project with an unrelated `inbox/` would receive capture notes and have an existing `inbox/_live.md` **overwritten** by `digest`. (b) Doutourado's `inbox/` has no `README.md` today, so under the README predicate capture starts only after Step 12's `init`, which is the intended order. (c) Verbatim chat text will live on open-seja's `dev` (org-visible) after Step 8; the dogfooded note should get the same C2 names check before commit.
**Recommendation:** One predicate, implemented once in `pkb_inbox.py` and reused by `detect_setup_state.py`: layer present iff `PKB_DIR` is non-empty **and** `<PKB_DIR>/README.md` exists. `digest` refuses to overwrite a `_live.md` that lacks its generated-file header. Step 8 adds a names check.
**Resolution:** Plan amended -- see A3, A4, A5, A6, A7.

### Phase 2 -- Deep-dive: DX (iteration 1, deep-dive 6/6)

**Concern:** Post-skill stage vs script boundary; commit-scope tooling; concreteness of the `/design` trigger.
**Step ref:** Step 6
**Files read:** `.claude/skills/post-skill/SKILL.md` (step 6 l.154; 7e l.170-193; 8 l.195; 2c gate l.114), `.claude/skills/scripts/verify_commit_scope.py` (`_ALWAYS_ALLOWED_PREFIXES = ("_loom/", ".claude/")`; `_normalize` drops a trailing `/`, so `--always-include inbox/` becomes exact-match `inbox`), `.claude/skills/implement/SKILL.md` l.120/180 (`step_notes.py record --kind drift --detail "<n> itens"` or `--declined`), `product-design/standards.md § Backend > 1, 19`.
**Finding:** (1) `verify_commit_scope.py` **must** change: without it every `inbox/*.md` staged by step 8 is reported `unexpected` and the post-skill falls back to "output the commit message for manual use" on every invocation in a PKB project. Fix: a fourth expected-source `(d)` in `build_expected` when the PKB predicate holds, plus fixing `_normalize` to preserve a trailing slash. (2) Step 6(b) refers to "o relatorio de deriva da invocacao" without a source; the implement skill already records `- drift: <path> (<n> itens)` / `- drift: not-measured` in the progress file, so 2c can read the count from there. (3) 2c's current gate is parent `implement` + DONE header; the `plan`-parent branch must be added explicitly. (4) The skip line on every non-PKB invocation is noise.
**Recommendation:** Rewrite Step 6 with the `verify_commit_scope.py` change as a first-class file with tests, the progress-file source for the drift count, the amended 2c gate, and a silent skip.
**Resolution:** Plan amended -- see A5.

### Conflict Check (iteration 1)

- ARCH (template-only skills, `--with-skills`) vs DX ("one channel is simpler"): aligned; A2 removes the second channel.
- DATA (README predicate; `digest` refuses foreign `_live.md`) vs UX (filesystem switch "simple and visible"): the README file is created by `init` and is itself visible; the switch stays a file, only a more specific one.
- I18N (pt-BR SKILL.md on `main`) vs ARCH: A2 keeps the skills out of open-seja's `.claude/skills/`; they remain on `main` only under `template/pkb/skills/`. Reduced to the exception line for the designer.
No inter-perspective conflicts requiring the SEC/A11Y priority rules.

### Iteration 2 (re-evaluation, no new deep-dives)

Re-scanned ARCH, TEST, COMPAT, DATA, DX against the amended Steps 2, 6, 7a/7b, 8, 11, 12: all five move to Adopted. SEC re-checked against A2/A7: still Adopted. I18N remains Deferred by rationale. Budget exhausted; convergence reached because no amended step produced a new Deferred.

### Execution Metrics

| Metric | Value |
|--------|-------|
| Deep-dives used | 6/6 |
| Iterations completed | 2/3 |
| Perspectives shortlisted | 9 (SEC, ARCH, UX, I18N, TEST, DX, COMPAT/OPS, DATA; DB/API/A11Y/PERF/VIS/RESP/MICRO N/A) |
| Perspectives Adopted | 8 |
| Perspectives Deferred (with rationale) | 1 (I18N -- pt-BR SKILL.md exception for the designer) |
| Convergence reason | deep-dive budget exhausted; iteration-2 re-scan produced no new Deferred |

### Plan Amendment (iteration 1)

Steps 4, 6, 7 (split into 7a/7b), 8, 11 and 12 were replaced in place in `## Steps`; Steps 2, 3, 5 and 10 received the edits below. Text outside `## Steps` is not rewritten (artifact immutability); the entries here supersede the corresponding original passages.

**A1 -- Design decisions, trade-off on the 5 skills (supersedes the bullet "Copiar as 5 skills PKB para o template").** Rationale: ARCH deep-dive 2 showed the "identical copy / no-op upgrade" claim is false once Step 8 dogfoods the skills into open-seja's `.claude/skills/`.

> As 5 skills PKB ficam so no template (`template/pkb/skills/`), nunca em `.claude/skills/` do open-seja. `pkb_inbox.py init` as copia para `<alvo>/.claude/skills/` so com `--with-skills` (ligado por padrao em `/seja-setup --pkb`; desligado no dogfooding do Step 8). Consequencias: o upgrade **nao toca** as skills PKB locais de um projeto (`collect_source_files` so le `.claude/` da fonte, e a fonte nao as tem); o Doutourado mantem as suas versoes com referencias a `projetos/`, `pegasus/` e `Proposta/`; `init` re-rodado acrescenta apenas skills que faltem. O texto generalizado do template (Step 2) serve a projetos novos.

**A1-i18n -- Best practices (addition, designer to confirm):** as SKILL.md PKB sao pt-BR porque o metodo, os templates e o publico sao pt-BR; `docs/pkb-layer.md` e a superficie en-US da distribuicao (`standards.md § i18n` lista SKILL.md em en-US; excecao declarada).

**A2 -- Step 2:** last sentence replaced: the skills never enter open-seja's `.claude/skills/` in any step (Step 8 runs `init` without `--with-skills`); they enter a project only via `init --with-skills` or `/seja-setup --pkb`, and the upgrade never copies nor deletes them.

**A3 -- Step 4:** full replacement (single predicate `pkb_layer_present`; normalization rule for the brief comparison; `SECRET_PATTERNS` imported, not copied; tests for `PKB_DIR` empty and `inbox/` without README).

**A4 -- Step 5:** `digest` refuses to overwrite a `_live.md` without the generated-file header (`<!-- gerado por pkb_inbox.py digest -->`), exit 1; test added.

**A5 -- Step 6:** full replacement (`verify_commit_scope.py` source (d) + trailing-slash fix with tests; post-skill 7f with silent skip and checkpoint; 2c gate widened to `plan` parent; drift count read from the progress file `- drift:` line).

**A6 -- Step 7 split into 7a (`--pkb`, AskUserQuestion, `has_pkb_layer` via the shared predicate) and 7b (defensive `is_preserved(rel_path)`, "camada PKB detectada" hint, Rules row aligned to the code, PKB row added to the classification table).**

**A7 -- Step 8:** dogfooding runs `init` without `--with-skills`; C2 names check and `check_secrets.py` before commit; verifies no PKB skill landed in `.claude/skills/`.

**A8 -- Step 11:** CHANGELOG note that v0.10.0/v0.10.1 were never tagged and v0.11.0 is the first tag after v0.9.1; no write to `.claude/skills/VERSION`.

**A9 -- Step 12:** states that the target's old `upgrade_harness.py` runs; declares the expected conventions WARN; local-clone fallback that does not touch the `open-seja/` submodule checkout; direct `capture` verification instead of invoking a skill; no `git add`/`git commit` by the agent.

**A10 -- Files and dependencies (supersedes the corresponding lines in `## Files`):** add `.claude/skills/scripts/verify_commit_scope.py` (modify) and `.claude/skills/scripts/tests/test_verify_commit_scope.py` (create/modify); drop `.claude/skills/VERSION`; drop "`.claude/skills/{daily-log,...}` (create, via init)" from the open-seja side; Step 3 gains `--with-skills`; Step 10 depends on 6, 7a, 7b; `harness-structure.md` skill count stays 17, add `pkb_inbox.py`, `template/pkb/` and post-skill 7f.
