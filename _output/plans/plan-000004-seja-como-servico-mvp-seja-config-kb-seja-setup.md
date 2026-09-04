# Plan 000004 | DOCUMENT-O | METACOMM | 2026-09-04 20:10 | seja como serviço MVP: seja-config, KB e o papel do seja-setup | Review: standard
plan_format_version: 1

## Designer's metacommunication message

> explorar e documentar: intenção seja como um serviço mvp utilizado por uma harnerss. o que seria o seja-setup ? teriamos que ter um seja-config antes para acoplar uma llm. seja-setup cria o necessario para instanciar uma KB no repositorio, que será usado para o design e outras interaçòes seja-like

## Agent interpretation

**Problem**: o SEJA não tem hoje fronteira própria. Ele é markdown e Python inertes que o Claude Code anima ao ler `.claude/`; não existe nenhum ponto em que outra harness (OpenCode, Cursor, um agente próprio) possa *chamá-lo*. Enquanto isso, `H-002` afirma que o SEJA é "o substrato sobre o qual um agente consegue raciocinar sobre intenção" -- uma afirmação que nenhum agente pode exercer hoje, porque a intenção não é recuperável: ela é carregada por arquivo inteiro, com orçamento de contexto e janela de recência como paliativos. Este plano explora e documenta o que muda quando o SEJA passa a ser um **serviço** com fronteira, configuração e base de conhecimento próprias, e o que isso faz com o `/seja-setup`.

**Approach**: produzir um documento de exploração (`docs/seja-as-a-service.md`) que atravessa quatro perguntas na ordem em que o brief as coloca -- o que é o serviço, o que é o `seja-config`, o que é a KB, e o que o `/seja-setup` passa a ser -- e fecha registrando na intenção do projeto apenas o que a exploração de fato assentou (uma hipótese nova e as questões que ela abre), sem fingir decisão onde há leitura. O plano não constrói nada: ele termina entregando um `roadmap-spec` preenchido, para que a construção seja agendada depois, com as dependências já visíveis. Escolhi documento único com seções em vez de arquivos separados por tema porque as quatro perguntas do brief só se sustentam encadeadas: o `seja-config` não tem razão de existir sem a KB, e a KB não tem onde morar sem a redefinição do `/seja-setup`.

**Alternatives rejected**:

- **Escrever direto na `product-design/seja-as-intended.md`** -- rejeitada por classificação de manutenção. O arquivo é `Human (markers)`; `check_human_markers_only.py` rejeita escrita de agente fora do padrão de marcador, e `apply_marker.py` só sabe aplicar `STATUS`, `CHANGELOG_APPEND`, `DECISION_APPEND`, `ESTABLISHED`, `INCORPORATED` e `REQ_TRACED_BY`. Prosa nova (uma hipótese `H-NNN`, questões `Q-NNN`) é autoria humana. O plano entrega o bloco redigido, pronto para colar, e aplica pelo script só o que o script sabe aplicar.
- **Gerar um roadmap agora** -- rejeitada em conversa (decisão do designer, ver Q&A). Um roadmap agenda construção e pressupõe que o WHAT está assentado; três das quatro peças do brief não existem sequer como especificação.
- **Tratar `seja-config` como resposta a `Q-003`** (detecção da posição na escala citizen<->power) -- rejeitada. `Q-003` está **deliberadamente sustentada em aberto** por decisão de 2026-08-26, porque depende de `Q-002` (granularidade da escala). Fixar um campo de escala no `seja-config` fecharia `Q-002` por via indireta. O plano registra o `seja-config` como *hospedeiro natural futuro* desse campo, em forma de questão, e não o implementa.
- **Reimplementar a KB do zero sem olhar o Pegasus** -- rejeitada. O repositório-pai (Doutourado) já roda o Pegasus em produção pessoal com exatamente a forma discutida aqui (ChromaDB, sentence-transformers, `sources.txt`, ignore-list, `--rebuild` build-new-then-swap, servidor MCP expondo `query_knowledge`, e o aviso de segurança sobre o texto ingerido virar cópia local pesquisável). É precedente testado; a exploração deve partir dele e registrar onde diverge, não redescobri-lo.

## Files

Lidos / analisados:

- `product-design/seja-as-intended.md` -- fonte da intenção. `H-002` (computabilidade da intenção) é a hipótese de que este plano é a forma operacional; `P-003` (retradução) é o que a KB passa a fundamentar; `Q-003` está sustentada em aberto e **não pode** ser fechada aqui; o Apêndice B.2 desenha a pilha `Docs -> Harness -> LLM`, que o brief reordena; o Apêndice B.1 nota 2 afirma que a camada de design vem **de fora** do projeto, o que está em tensão direta com "instanciar uma KB no repositório".
- `.claude/skills/seja-setup/SKILL.md` e `.claude/skills/_internal/seja-setup/{install,here,upgrade,demo}/SKILL.md` -- as cinco modalidades atuais scaffoldam **arquivos** (`CLAUDE.md`, `.claude/rules/`, `conventions.md`, `.seja-version`). Nenhuma cria índice, embeddings ou recuperação. O fluxo é conduzido por agente com `AskUserQuestion`, isto é, **já pressupõe uma LLM acoplada pela harness** -- o que é precisamente por que `seja-config` não faz sentido hoje e passa a fazer quando existe KB.
- `.claude/skills/seja-setup/detect_setup_state.py` -- os quatro estados (`no-harness`, `fresh-download`, `partial-init`, `finalised`) descrevem presença de *arquivos*. Uma KB acrescenta um eixo de estado ortogonal (ausente / obsoleta / atual) que o detector não modela.
- `.claude/skills/pre-skill/SKILL.md` -- `context_budget` em três níveis, janelamento de recência dos briefs em 50 entradas com resumo "N earlier entries ... not loaded", e protocolo demand-pull de referências. São três contornos para a mesma ausência: não há recuperação, só carga de arquivo inteiro.
- `.claude/skills/scripts/apply_marker.py` -- confirma que `DECISION_APPEND` exige uma seção `## Decisions`, **inexistente** em `seja-as-intended.md` (que tem `## Questões abertas` e `## CHANGELOG`). Só `CHANGELOG_APPEND` é aplicável ao arquivo hoje.
- `product-design/conventions.md` -- `PROJECT_DESCRIPTION` já declara a compatibilidade com OpenCode como objetivo; `BACKEND_FRAMEWORK`/`FRONTEND_FRAMEWORK` = `none`; o padrão de implantação é **embedded** (`CODEBASE_DIR` = `.`), com o padrão companion-workspace disponível. A localização da KB tem de seguir esse eixo, não ser fixada na raiz do repo.
- `_output/plans/plan-000001-npx-open-seja-installer-wrapper.md` -- o wrapper `npx open-seja` é bootstrap + handoff para uma sessão interativa do `claude`; ele é o lugar natural onde um passo de configuração não-interativo caberia, e o plano registra explicitamente que "fonte configurável" foi deixada de fora dele. Pendente de execução há 23 dias.
- `CLAUDE.md` do repositório-pai (Doutourado) -- descreve o Pegasus: `pegasus/knowledge/` mais `sources.txt`, ignore-list por nome, vectorstore gitignored e regenerável, `ingest`/`status`/`ask`/`serve`, servidor MCP registrado em `.mcp.json`, e o aviso de não apontar fontes para material sob sigilo porque o texto ingerido vira cópia local pesquisável.

A criar:

- `docs/seja-as-a-service.md` (create)
- `_output/roadmaps/roadmap-spec-seja-service-mvp.md` (create)

A modificar:

- `product-design/seja-as-intended.md` (modify, **somente via `apply_marker.py`**)

## Best practices

- **Documento de exploração separado do documento de intenção.** `docs/` aceita autoria de agente; `product-design/seja-as-intended.md` não. O padrão já existe no repositório: `docs/o-que-e-o-seja.md` apresenta a § 1 da intenção sem ser a intenção, e declara no cabeçalho que "não decide nada". Este documento segue a mesma disciplina.
- **Hipótese com condição de refutação.** A intenção do projeto registra hipóteses no registro abdutivo de Peirce, numeradas e carregando o que as confirmaria ou refutaria. Toda hipótese nova proposta aqui tem de vir nessa forma, ou não entra.
- **Credenciais por referência, nunca por valor.** `check_secrets.py` já varre `api_key`/`apikey`/`api_secret` atribuídos a literais. Um `seja-config` que aceitasse chave inline seria detectado pelo próprio harness como vazamento. O campo aponta para nome de variável de ambiente.
- **Artefato regenerável, não migrável.** A convenção do repositório-pai diz que índices ChromaDB não devem ser deletados sem plano de migração; a saída do Pegasus contorna isso mantendo o vectorstore gitignored e reconstruível (`--rebuild`, build-new-then-swap). A KB do SEJA deve ser regenerável por construção, o que dispensa migração.
- **pt-BR com diacríticos corretos, sem substituição tipográfica.** Língua de trabalho do design; `docs/` já tem material em pt-BR ao lado do en-US, e `Q-005` mantém a tradução em aberto.

## Design decisions

**User-visible impact**: ao final deste plano você não tem código novo -- você tem um documento que responde, com o repositório na mão e não por analogia, às quatro perguntas que você fez. Eu lhe mostro por que o `seja-config` não tinha razão de existir até agora e passa a ter no instante em que a KB entra; por que a ordem que você intuiu (config antes de setup) é forçada por uma dependência técnica concreta, e não por gosto; o que exatamente a KB indexa e o que ela nunca pode indexar; e o que sobra do `/seja-setup` quando ele deixa de ser "copiador de arquivos" e passa a ser "provisionador de um serviço". Fecho lhe entregando um `roadmap-spec` preenchido: quando você quiser construir, `/plan --roadmap --from-spec` lê aquele arquivo e a construção já sai com as dependências certas.

**Trade-offs accepted**: ganha-se uma leitura assentada e rastreável antes de qualquer linha de código, e o registro na intenção do projeto de que a exploração aconteceu. Perde-se tempo de calendário: nada fica executável ao fim deste plano, e a pergunta "qual é o custo real de manter embeddings atualizados em um repositório que muda a cada skill" continua sem resposta empírica, porque este plano não mede nada -- ele documenta. Aceita-se também que três das quatro peças (`seja-config`, KB, serviço) ficam especificadas mas não validadas contra um usuário; a validação é o que o roadmap seguinte tem de agendar.

**Metacommunication impact**: o documento gerado fala na voz do preposto ao designer. Onde ele descreve o `seja-config`, escreve "eu preciso saber com que modelo indexar antes de conseguir instanciar sua base"; onde descreve a KB, escreve "eu passo a lhe responder a partir do que seu projeto já decidiu, em vez de reler tudo a cada turno". Isso não é ornamento: `P-001` diz que o artefato é mensagem, e um documento que especifica o preposto tem de estar escrito no registro do preposto. O `roadmap-spec` de saída, por ser insumo de máquina, fica em prosa técnica neutra.

**Metacomm contradiction check**: nenhuma contradição dura encontrada, mas **duas tensões reais** com a intenção registrada, que o documento tem de expor em vez de resolver silenciosamente:

1. **Apêndice B.1, nota 2** -- "A camada de design vem de fora do projeto. O harness não é parte do projeto: é o que se aplica sobre ele." O brief pede uma KB **no repositório**. A tensão se resolve se a localização da KB seguir o eixo embedded/companion-workspace que o `/seja-setup` já oferece, em vez de ser fixada na raiz. O documento tem de dizer isso explicitamente.
2. **Apêndice B.2** -- a pilha desenhada é `Docs -> Harness -> LLM`, com o SEJA *sendo* a harness. O brief propõe `Harness -> SEJA -> LLM`, com o SEJA sendo serviço que a harness consome. É uma reordenação da figura de origem, não uma leitura dela. E `conventions.md` hoje declara literalmente "este projeto é o próprio harness de agentes SEJA". O documento tem de marcar isso como reenquadramento proposto, com a Figura 2 citada, para que a diferença fique auditável.

## Steps

### Step 1: Criar o documento e assentar o modelo de serviço

Criar `docs/seja-as-a-service.md` com cabeçalho no padrão de `docs/o-que-e-o-seja.md` (declarando explicitamente que o documento **propõe e explora**, e que decisão só existe onde marcada) e escrever a primeira seção, "O SEJA como serviço".

Conteúdo da seção: (a) constatar que o SEJA hoje não tem runtime próprio -- é markdown e Python que o Claude Code anima ao ler `.claude/`, sem nenhum ponto de chamada para outra harness; (b) contrastar a pilha do Apêndice B.2 (`Docs -> Harness -> LLM`, SEJA *sendo* a harness) com a pilha do brief (`Harness -> SEJA -> LLM`, SEJA sendo serviço consumido), citando a Figura 2 e marcando isto como reenquadramento proposto, não leitura do desenho; (c) enumerar as três fronteiras candidatas já meio-presentes no repositório -- **servidor MCP** (precedente direto: o Pegasus do repositório-pai já expõe `query_knowledge` e está registrado em `.mcp.json`), **CLI** (`npx open-seja`, plan-000001, hoje só bootstrap + handoff) e **arquivos-como-contrato** (o status quo, em que a harness lê `SKILL.md`); (d) argumentar qual é o MVP: os scripts de marcador, id e cobertura **já são** Python agnóstico de harness -- o que falta é recuperação sobre o corpus de intenção e um jeito de chamar isso de fora do Claude Code, logo o MVP mínimo é **MCP + KB**, não uma reescrita das skills; (e) **enunciar a direção de dependência** do arranjo proposto e o que ela proíbe -- se o SEJA fica abaixo da harness, então nada do lado SEJA pode importar API específica de Claude Code, e a fronteira tem de ser nomeada (protocolo, não biblioteca); sem esse enunciado o reenquadramento é slogan, não arquitetura; (f) fechar amarrando em `H-002`: o serviço é a forma operacional da hipótese de que o SEJA é substrato para o agente raciocinar sobre intenção.

**Glosa obrigatória**: toda referência a um ID da intenção (`P-NNN`, `H-NNN`, `Q-NNN`, Apêndice) tem de vir glosada em linha na primeira ocorrência -- uma oração dizendo o que aquele ID afirma. `docs/o-que-e-o-seja.md` já usa essa disciplina. Sem ela o documento só é legível com `seja-as-intended.md` aberto ao lado, o que o torna inútil para quem chega depois.

- **Files**: `docs/seja-as-a-service.md` (create)
- **References**: `product-design/seja-as-intended.md` (H-002, P-001, Apêndice B.2), `product-design/conventions.md` (PROJECT_DESCRIPTION, meta OpenCode)
- **Interface**: N/A
- **Verify**: o documento existe, o cabeçalho declara o estatuto proposto/exploratório, a seção cita `H-002` e a Figura 2 nominalmente, enuncia a direção de dependência e o que ela proíbe, e todo ID citado tem glosa em linha na primeira ocorrência
- **Tests**: N/A (documento; nenhum código produzido)
- **Docs**: este passo *é* a documentação
- [ ] Done

### Step 2: Especificar o `seja-config` e a razão da ordem

Acrescentar a seção "seja-config" ao documento. O argumento central, que a seção tem de sustentar e não apenas afirmar: **hoje o acoplamento da LLM é inteiramente da harness** -- o `/seja-setup` roda dentro de uma sessão do Claude Code já ativa e usa `AskUserQuestion`, isto é, o modelo já está acoplado quando o setup começa. Por isso um `seja-config` seria supérfluo hoje. Ele passa a ser necessário no instante exato em que o SEJA precisa **ingerir e indexar** um corpus: indexar exige um modelo de embedding que a harness não fornece. Essa é a dependência concreta que força a ordem `seja-config -> seja-setup` que o brief intuiu.

Especificar os campos do MVP: `harness` (qual runtime: `claude-code` | `opencode` | outro -- alimenta a meta de compatibilidade OpenCode já declarada em `conventions.md`); `embedding` (modelo e provedor, obrigatório -- é o que a KB consome); `generation` (modelo e provedor, opcional, necessário só se o serviço responder perguntas por conta própria em vez de devolver passagens); `credentials` (**referência a nome de variável de ambiente, nunca valor** -- `check_secrets.py` detectaria uma chave inline como vazamento no próprio repositório); `kb` (localização, fontes, ignore-list -- detalhado no Step 3). Registrar formato e lugar propostos, e por que não é linha nova em `conventions.md` (aquele arquivo é definição de projeto versionada; binding de modelo e credencial são ambientais).

Registrar explicitamente o que fica **fora** do MVP: o campo de posição na escala `H-001`. `Q-003` está sustentada em aberto por decisão de 2026-08-26 porque depende de `Q-002`; o `seja-config` é o hospedeiro natural futuro desse campo e a seção deve dizê-lo nessa forma -- como questão a abrir no Step 6, não como campo a implementar.

- **Files**: `docs/seja-as-a-service.md` (modify)
- **References**: `product-design/seja-as-intended.md` (Q-002, Q-003 e a nota que a sustenta em aberto), `product-design/conventions.md`, `.claude/skills/design/check_secrets.py`
- **Depends on**: Step 1
- **Interface**: N/A
- **Verify**: a seção enuncia a dependência técnica que força a ordem config->setup (embedding não vem da harness) e marca a posição na escala como fora do MVP, citando `Q-003` e a razão da sustentação
- **Tests**: N/A (documento)
- [ ] Done

### Step 3: Especificar a KB -- corpus, exclusões, localização, regenerabilidade

Acrescentar a seção "A base de conhecimento". Quatro blocos.

**O que indexar**: tabela do corpus que o repositório já tem e hoje não é recuperável -- `product-design/seja-as-intended.md` (a intenção, que `H-002` diz precisar ser endereçável), `_output/plans/` (como a intenção virou construção), `_output/qa-logs/` e `_output/research-logs/` (por que as decisões foram como foram), `_output/briefs.md` e `decision-digest.jsonl` e `conversation-trace.jsonl` (a trilha), `.claude/references/` (o vocabulário do próprio harness), e o código sob `CODEBASE_DIR` (o as-coded, insumo de `/explain drift`). Cada linha diz *por que* pertence.

**O que nunca indexar**: segredos, `.env`, material sob sigilo. O aviso do repositório-pai é transferível literalmente -- o texto ingerido vira **cópia local pesquisável**, então apontar uma fonte para material institucional é o mesmo que copiá-lo. Registrar também o precedente da regra do `_` (pasta com prefixo `_` não é lida nem indexada), e a limitação que ela expõe: uma ignore-list por nome não conhece prefixos, então a exclusão vira disciplina na lista de fontes.

**Onde mora**: a localização tem de seguir o eixo embedded/companion-workspace que o `/seja-setup` já oferece, e não ser fixada na raiz do repositório. Esta é a resolução da tensão com o Apêndice B.1 nota 2 ("a camada de design vem de fora do projeto"), e a seção tem de expor a tensão antes de resolvê-la. Gitignored em qualquer caso.

**Fronteira de confiança na recuperação**: as exclusões acima protegem a **ingestão**; a **recuperação** é uma segunda fronteira e precisa de enunciado próprio. Uma superfície tipo `query_knowledge` devolve passagens a quem a chamar -- e "quem a chamar" passa a incluir harnesses que não são o Claude Code. Dois casos concretos que a ignore-list por nome de arquivo não modela: `conversation-trace.jsonl`, cujo conteúdo é mascarado na escrita por `conversation_trace.py` (o caminho de exit code 2) mas ficaria indexado já mascarado ou não conforme o momento da ingestão; e trechos de código que atravessam contexto ao serem devolvidos fora do arquivo de origem. A seção tem de dizer quem pode chamar, o que a chamada pode devolver, e o que nunca sai do processo -- não apenas o que entra.

**Por que KB e não carga eager**: o argumento mais forte já está visível no harness. `pre-skill` tem `context_budget` em três níveis; os briefs são janelados por recência em 50 entradas com um resumo explícito de "N earlier entries ... not loaded"; `/plan` usa protocolo demand-pull de referências. Os três são contornos da mesma ausência. Uma KB troca "carregue os 50 briefs mais recentes" por "recupere os briefs relevantes" -- que é exatamente o que `/design` e `/explain drift` precisam e não têm. Registrar o Pegasus como precedente testado (ChromaDB, sentence-transformers, `sources.txt`, `--rebuild` build-new-then-swap, MCP) e onde o SEJA divergiria dele.

- **Files**: `docs/seja-as-a-service.md` (modify)
- **References**: `product-design/conventions.md` (CODEBASE_DIR, padrão embedded/companion), `product-design/seja-as-intended.md` (H-002, Apêndice B.1 nota 2), `.claude/skills/pre-skill/SKILL.md` (context_budget, janelamento)
- **Depends on**: Step 1
- **Interface**: N/A
- **Verify**: a seção contém a tabela de corpus com justificativa por linha, a lista de exclusões com o aviso de cópia pesquisável, a regra de localização por padrão de implantação, o enunciado de fronteira de confiança da recuperação (quem chama / o que volta / o que nunca sai), e o argumento contra carga eager ancorado nos três contornos existentes
- **Tests**: N/A (documento)
- [ ] Done

### Step 4: Redefinir o que o `/seja-setup` passa a ser

Acrescentar a seção "O que sobra do seja-setup". Hoje as cinco modalidades scaffoldam arquivos; sob o brief, `/seja-setup` passa a ser o ato de **provisionar o serviço em um projeto**. Mapear modalidade por modalidade: `install` / `--here` / `--workspace` ganham inicialização da KB e primeira ingestão; `--upgrade` reingere as referências de harness alteradas (e como a KB é regenerável por construção, derrubar e reconstruir é seguro -- é a razão pela qual regenerabilidade foi escolhida no Step 3, e não uma coincidência); `--demo` ingere o corpus TaskFlow ou embarca uma KB pré-construída.

Registrar dois problemas concretos que a redefinição cria e que a especificação tem de encarar:

1. **Estado.** `detect_setup_state.py` modela quatro estados de presença de *arquivos*. Uma KB acrescenta um eixo ortogonal -- ausente / obsoleta / atual -- que o detector não representa. Descrever o eixo; não decidir o desenho do detector aqui.
2. **Compatibilidade com projetos já instalados.** Existem projetos instalados em `v0.9.1`, sem `seja-config` e sem KB. `--upgrade` neles tem de ter caminho definido: a KB é opcional e o harness segue funcionando sem ela (degradação graciosa), ou o upgrade passa a exigir configuração e portanto é quebra? Registrar a classificação SemVer correspondente (MINOR se a KB for aditiva e opcional; MAJOR se `seja-config` virar pré-requisito de `/seja-setup`), porque `.seja-version` e o modelo de release A2 dependem dessa classificação estar certa. Recomendação a registrar no documento, não a decidir aqui: KB aditiva e opcional no MVP, com o serviço degradando para o comportamento atual quando ausente.
3. **Ordem e interatividade.** Se `seja-config` precede `seja-setup` e a KB tem de existir antes de `/design`, a sequência vira `seja-config` (não-interativo) -> `seja-setup` (interativo, `AskUserQuestion`) -> primeira ingestão -> `/design`. O wrapper `npx open-seja` do plan-000001 é o lugar natural para o passo não-interativo, e aquele plano registra explicitamente que deixou "fonte configurável" de fora. Anotar a conexão e a pendência (plan-000001 não executado).

- **Files**: `docs/seja-as-a-service.md` (modify)
- **References**: `.claude/skills/seja-setup/SKILL.md` (secção Version Pinning, modelo de release A2), `.claude/skills/seja-setup/detect_setup_state.py`, `_output/plans/plan-000001-npx-open-seja-installer-wrapper.md`
- **Depends on**: Step 2, Step 3
- **Interface**: N/A
- **Verify**: a seção cobre as cinco modalidades individualmente e nomeia os três problemas (eixo de estado da KB; compatibilidade de projetos pré-KB com classificação SemVer; ordem config->setup->ingest->design com a interatividade do setup)
- **Tests**: N/A (documento)
- [ ] Done

### Step 5: Mapear o consumo -- quem passa a usar a KB e o que isso muda

Acrescentar a seção "Quem consome". Percorrer os pontos do ciclo canônico que mudam quando existe recuperação: `/design` (deixa de partir do zero a cada iteração e passa a poder perguntar o que o projeto já decidiu), `/research` (recuperação em vez de varredura), `/explain drift` (a comparação as-intended / as-coded passa a ter os dois lados indexados), `pre-skill` (o `context_budget` deixa de ser tamanho de arquivo e passa a ser relevância), `/plan` (o protocolo demand-pull de referências vira recuperação de fato).

Fechar com o efeito sobre `P-003`, que é o mais consequente e o menos óbvio: a retradução ao citizen dev hoje é eletiva porque o agente não sabe *a que intenção* cada trecho de código responde. Com o corpus de intenção recuperável, ele passa a saber -- que é exatamente a condição que `H-002` enuncia como o que a confirmaria ("agentes conseguindo responder 'esta mudança atende a qual intenção declarada?'"). Registrar isso como a ligação entre a KB e a hipótese, e portanto como o critério pelo qual o serviço deve ser julgado.

- **Files**: `docs/seja-as-a-service.md` (modify)
- **References**: `product-design/seja-as-intended.md` (P-003, P-005, H-002), `.claude/skills/pre-skill/SKILL.md`
- **Depends on**: Step 3
- **Interface**: N/A
- **Verify**: a seção nomeia ao menos cinco consumidores com o que muda em cada um, e amarra a KB à condição de confirmação de `H-002`
- **Tests**: N/A (documento)
- [ ] Done

### Step 6: Registrar na intenção do projeto o que a exploração assentou

Redigir, ao fim de `docs/seja-as-a-service.md`, uma seção "Para registrar na intenção" contendo o bloco de prosa **pronto para colar** em `product-design/seja-as-intended.md`, e aplicar pelo script apenas o que o script sabe aplicar.

O bloco propõe: uma hipótese nova (o SEJA como serviço com fronteira própria, no registro abdutivo, com o que a confirmaria e o que a refutaria enunciados -- sem isso ela não entra) e as questões que a exploração abriu, entre elas a relação entre a pilha proposta e a Figura 2, a localização da KB frente ao Apêndice B.1 nota 2, e o `seja-config` como hospedeiro futuro do campo de escala que `Q-003` mantém em suspenso. Numerar continuando a sequência existente (a última hipótese é `H-004`, a última questão `Q-010`).

Registrar também, como achado do próprio passo, que o mecanismo de registro de decisão do SEJA **não está disponível neste arquivo**: `DECISION_APPEND` exige uma seção `## Decisions` que `seja-as-intended.md` não tem, de modo que decisões arquiteturais tomadas sobre o SEJA não têm hoje onde ser registradas em forma endereçável. Isso é matéria de `Q-006` (a relação entre este documento e o formato §0-§17 do template, que prevê `## Decisions`), e a questão nova deve apontar para ela em vez de propor a seção unilateralmente.

Não escrever a prosa no arquivo de intenção: ele é `Human (markers)`, e `check_human_markers_only.py` rejeita escrita de agente fora do padrão. `DECISION_APPEND` também não serve -- ele exige uma seção `## Decisions`, que `seja-as-intended.md` não tem. O que é aplicável é `CHANGELOG_APPEND`, e só após confirmação explícita do designer no mesmo turno:

```
python .claude/skills/scripts/apply_marker.py \
  --file product-design/seja-as-intended.md \
  --id <id-da-entrada> --marker CHANGELOG_APPEND --value added \
  --plan plan-000004 --note "<nota>" --dry-run
```

Rodar sempre `--dry-run` primeiro e mostrar o diff antes de aplicar.

- **Files**: `docs/seja-as-a-service.md` (modify), `product-design/seja-as-intended.md` (modify, somente via `apply_marker.py`)
- **References**: `.claude/references/general/shared-definitions.md` (classificação de manutenção), `.claude/skills/scripts/apply_marker.py`
- **Depends on**: Step 1, Step 2, Step 3, Step 4, Step 5
- **Interface**: N/A
- **Verify**: `apply_marker.py --dry-run` roda limpo e mostra o diff esperado; a hipótese proposta carrega condições de confirmação e refutação; a numeração continua de `H-004` e `Q-010`; a ausência da seção `## Decisions` está registrada e ligada a `Q-006`; nenhuma escrita direta em `seja-as-intended.md` fora do script
- **Tests**: N/A (documento e marcador)
- [ ] Done

### Step 7: Entregar o recorte de construção como roadmap-spec preenchido

Criar `_output/roadmaps/roadmap-spec-seja-service-mvp.md` no formato de `.claude/references/template/roadmap-spec.md`, preenchido a partir do documento, para que a construção possa ser agendada depois com `/plan --roadmap --from-spec _output/roadmaps/roadmap-spec-seja-service-mvp.md`.

Preencher visão, horizonte e temas, e listar os work items com `depends_on` explícito -- no mínimo: `seja-config` (o binding, e o passo não-interativo que o wrapper npx pode hospedar), inicialização e ingestão da KB, o eixo de estado da KB no `detect_setup_state.py`, a superfície de recuperação (MCP), e a adaptação do primeiro consumidor. Não sequenciar em ondas: `depends_on` expressa a ordem; o agendamento é do roadmap, não deste plano.

Anotar no arquivo a dependência externa: plan-000001 (`npx open-seja`) está pendente há 23 dias e é o hospedeiro natural do passo de configuração não-interativo -- ou ele é executado antes, ou o item de `seja-config` tem de carregar seu próprio ponto de entrada.

- **Files**: `_output/roadmaps/roadmap-spec-seja-service-mvp.md` (create)
- **References**: `.claude/references/template/roadmap-spec.md`, `_output/plans/plan-000001-npx-open-seja-installer-wrapper.md`
- **Depends on**: Step 4, Step 5
- **Interface**: arquivo consumível por `/plan --roadmap --from-spec`
- **Verify**: o arquivo segue os campos do template (`id`, `title`, `scope`, `size`, `depends_on`, `type`, `description`), todo `depends_on` referencia um `id` presente no próprio arquivo, e nenhum item fica sem `description`
- **Tests**: N/A (arquivo de especificação)
- [ ] Done

## Outcomes

- `docs/seja-as-a-service.md` responde, ancorado no repositório e não em analogia, às quatro perguntas do brief: o que é o serviço, o que é o `seja-config` e por que ele precede o setup, o que a KB indexa e onde mora, e o que o `/seja-setup` passa a ser.
- As duas tensões com a intenção registrada (a pilha da Figura 2; a camada de design vinda de fora do projeto) ficam expostas e nomeadas, em vez de resolvidas em silêncio.
- `Q-003` permanece sustentada em aberto; o `seja-config` fica registrado como seu hospedeiro futuro, não como sua resposta.
- A intenção do projeto ganha uma hipótese nova em forma abdutiva e as questões que a exploração abriu, com o CHANGELOG aplicado por script.
- `_output/roadmaps/roadmap-spec-seja-service-mvp.md` deixa a construção pronta para ser agendada, com dependências explícitas e a pendência do plan-000001 anotada.

## Smoke

false

## Metacomm Intention

- **Summary**: eu lhe digo o que passo a ser quando deixo de ser os arquivos que sua harness lê e viro um serviço que ela chama -- o que preciso saber antes (o modelo com que indexo), o que instalo no seu projeto (uma base do que ele já decidiu), e o que o `/seja-setup` passa a significar quando provisiona isso em vez de copiar arquivos.
- **Source**: agent (metacomm)

## Review Log

**Review depth:** Standard (auto=standard, floor=light, flag=none -> effective=standard)
**Deep-dive budget:** 4/6 used

> Execução: as duas fases foram conduzidas em linha, sem despachar o subagente `plan-reviewer`, por restrição desta sessão (subagentes só mediante pedido explícito). O trabalho equivalente -- triagem, leitura das perspectivas selecionadas, deep-dives e emendas -- foi feito nesta janela e está registrado abaixo.

### Phase 1 -- Perspective Scan (2026-09-04 20:14 UTC)

Shortlist por prefixo `DOCUMENT-O` -> DX, OPS, COMPAT. Acrescentadas 2, com justificativa:
- **ARCH**: o núcleo do plano é uma reordenação de fronteira (`Docs -> Harness -> LLM` vira `Harness -> SEJA -> LLM`), que é matéria de arquitetura mesmo quando o entregável é documento.
- **SEC**: a KB do Step 3 ingere o repositório para uma cópia local pesquisável e o Step 2 especifica manuseio de credencial -- superfície de segredo, ainda que só especificada.

| Perspective | Status | Concern |
|-------------|--------|---------|
| DX | Deferred | Documento cita `P-002a`, `H-002`, `Q-003`, Apêndices por ID sem glosa; ilegível sem o arquivo de intenção aberto ao lado -- dispara Phase 2 |
| OPS | Adopted | Credencial por referência a variável de ambiente (Step 2) atende o P0 de não embutir segredo; artefato gitignored e regenerável (Step 3) dispensa procedimento de recuperação |
| COMPAT | Deferred | Nenhum passo trata de projetos já instalados em `v0.9.1` sem `seja-config` nem KB; classificação SemVer da mudança no `/seja-setup` ausente -- dispara Phase 2 |
| ARCH | Deferred | O reenquadramento de fronteira é afirmado mas a direção de dependência resultante não é enunciada; e o mecanismo de registro de decisão do harness não está disponível no arquivo alvo -- dispara Phase 2 |
| SEC | Deferred | Step 3 cobre exclusões de **ingestão**; a superfície de **recuperação** não tem fronteira de confiança enunciada -- dispara Phase 2 |
| PERF, DB, API, I18N, TEST, DATA | N/A | Fora do shortlist; plano não produz código, schema, rota nem string de interface |
| UX, A11Y, VIS, RESP, MICRO | N/A | Fora do shortlist; sem superfície visual ou de interação |

### Phase 2 -- Deep-dive: DX (iteração 1, deep-dive 1/6)

**Concern:** o documento gerado cita IDs da intenção sem glosa.
**Step ref:** Step 1 (criação do documento).
**Files read:** `docs/o-que-e-o-seja.md`, `product-design/seja-as-intended.md`, `.claude/references/general/review-perspectives/dx.md`.
**Finding:** `dx.md` P0 -- "Will a new contributor understand this without tribal knowledge?" e o padrão de quebra `Ia` ("I give up"). O documento planejado referencia `H-002`, `P-003`, `Q-002`, `Q-003`, `Q-006`, Apêndice B.1 nota 2 e Apêndice B.2 como se o leitor os tivesse. `docs/o-que-e-o-seja.md`, o único precedente no repositório de documento que apresenta a intenção sem ser a intenção, resolve isso glosando cada item ao apresentá-lo. Sem a glosa, o público efetivo do documento é uma pessoa só.
**Recommendation:** exigir glosa em linha na primeira ocorrência de cada ID citado.
**Resolution:** Plano emendado -- ver Plan Amendment (iteração 1), item 1. Status -> Adopted.

### Phase 2 -- Deep-dive: ARCH (iteração 1, deep-dive 2/6)

**Concern:** direção de dependência não enunciada; registro de decisão indisponível.
**Step ref:** Step 1 (modelo de serviço), Step 6 (registro na intenção).
**Files read:** `product-design/seja-as-intended.md` (Apêndice B.2, `Q-006`), `.claude/skills/scripts/apply_marker.py`, `.claude/references/general/review-perspectives/arch.md`.
**Finding:** dois achados distintos.
(a) `arch.md` P0 -- "layer boundaries ... dependency direction". Dizer que o SEJA passa a ser serviço consumido pela harness é uma afirmação sobre direção de dependência, e o plano a fazia sem enunciar o que ela **proíbe**. A consequência operacional é concreta e verificável: se o SEJA fica abaixo, nada do lado SEJA pode depender de API específica do Claude Code, e a fronteira tem de ser protocolo (MCP), não biblioteca. Sem esse enunciado, a construção subsequente pode "implementar o serviço" mantendo o acoplamento, e ninguém detecta.
(b) `arch.md` P2 -- ADRs com contexto, alternativas, consequências e status. Verificado em `apply_marker.py` linhas 192-217: `DECISION_APPEND` levanta `ValueError("no '## Decisions' section found in file")`. `seja-as-intended.md` tem `## Questões abertas` e `## CHANGELOG`, não `## Decisions`. Logo o mecanismo de registro de decisão do próprio harness não alcança o arquivo onde as decisões sobre o harness moram. Isso já é território de `Q-006`, que discute a relação entre este documento e o formato §0-§17 (o qual prevê `## Decisions`), então a saída correta é apontar para `Q-006`, não propor a seção por conta própria.
**Recommendation:** (a) Step 1 enuncia direção de dependência e o que ela proíbe; (b) Step 6 registra a indisponibilidade do mecanismo e a liga a `Q-006`.
**Resolution:** Plano emendado -- ver Plan Amendment (iteração 1), itens 2 e 3. Status -> Adopted.

### Phase 2 -- Deep-dive: SEC (iteração 1, deep-dive 3/6)

**Concern:** fronteira de confiança da recuperação ausente.
**Step ref:** Step 3 (especificação da KB).
**Files read:** `.claude/references/general/review-perspectives/sec.md`, `CLAUDE.md` do repositório-pai (aviso do Pegasus), `.claude/skills/scripts/conversation_trace.py` (caminho de mascaramento, exit code 2), `.claude/skills/design/check_secrets.py`.
**Finding:** `sec.md` P1 -- "Is there a current artifact ... that shows data flows across trust boundaries, and has it been reviewed to enumerate new threats introduced by this change?" O Step 3 tratava exclusão de **ingestão** (o que entra no índice) como se fosse a superfície inteira. Não é. A recuperação é uma segunda travessia: uma superfície tipo `query_knowledge` devolve passagens a **quem chamar**, e o ponto do plano é justamente que quem chama deixa de ser só o Claude Code. Uma ignore-list por nome de arquivo -- que é o que o Pegasus tem, e que o próprio `CLAUDE.md` do repositório-pai admite não conhecer o prefixo `_` -- não modela isso. O caso mais nítido é o `conversation-trace.jsonl`: `conversation_trace.py` mascara na escrita, mas o que foi indexado depende do estado no momento da ingestão, e a devolução por recuperação atravessa a fronteira sem passar pelo mascarador de novo.
**Recommendation:** o documento tem de enunciar a fronteira de confiança da recuperação separadamente: quem pode chamar, o que a chamada pode devolver, o que nunca sai do processo.
**Resolution:** Plano emendado -- ver Plan Amendment (iteração 1), item 4. Status -> Adopted.

### Phase 2 -- Deep-dive: COMPAT (iteração 1, deep-dive 4/6)

**Concern:** projetos instalados antes da KB; classificação SemVer.
**Step ref:** Step 4 (redefinição do `/seja-setup`).
**Files read:** `.claude/skills/seja-setup/SKILL.md` (Version Pinning, modelo A2), `.claude/skills/_internal/seja-setup/upgrade/SKILL.md`, `.claude/references/general/review-perspectives/compat.md`.
**Finding:** `compat.md` P0 -- "Is backward compatibility preserved, or is a migration path provided?" e P1 -- classificação MAJOR/MINOR/PATCH batendo com o manifesto. `/seja-setup` grava `.seja-version` como linha de base do upgrade, e o modelo A2 despacha upgrades por tag SemVer. Se `/seja-setup` passa a instanciar uma KB e `seja-config` passa a precedê-lo, um projeto em `v0.9.1` sem nenhum dos dois tem de ter comportamento definido sob `--upgrade`. As duas saídas têm classificação diferente -- KB aditiva e opcional é MINOR; `seja-config` como pré-requisito é MAJOR -- e o plano não escolhia nem registrava a escolha. Deixar isso implícito é como o modelo de release quebra em silêncio.
**Recommendation:** o documento registra o caso, a classificação SemVer correspondente e uma recomendação (KB aditiva e opcional no MVP, degradando para o comportamento atual quando ausente) -- a decisão fica com o designer, não com o documento.
**Resolution:** Plano emendado -- ver Plan Amendment (iteração 1), item 5. Status -> Adopted.

### Conflict Check (iteração 1)

Uma tensão real, entre SEC e DX, resolvida sem trade-off. A emenda SEC exige que o documento enuncie o que a recuperação **nunca** devolve; a emenda DX exige glosa em linha de tudo que é citado, o que aumenta o texto. As duas incidem em seções diferentes (Step 3 e Step 1) e nenhuma restringe a outra: glosar IDs não amplia superfície de segredo, e enunciar fronteira de confiança não exige jargão novo sem glosa. Nenhuma aplicação da regra "SEC ganha por padrão" foi necessária. Nenhum outro conflito inter-perspectiva detectado.

### Execution Metrics

| Metric | Value |
|--------|-------|
| Deep-dives used | 4/6 |
| Iterations completed | 1/3 |
| Perspectives shortlisted | 5 (DX, OPS, COMPAT + ARCH, SEC acrescentadas) |
| Perspectives Adopted | 5 |
| Perspectives Deferred (with rationale) | 0 |
| Convergence reason | all resolved -- todas as concerns da Phase 1 viraram emenda ou já estavam cobertas; iteração 2 não produziria mudança |

### Plan Amendment (iteração 1)

Cinco emendas, todas aditivas. A seção `## Steps` foi atualizada no lugar (única seção que pode mudar, por ser checklist viva); nenhum texto anterior foi removido.

1. **DX -> Step 1.** Acrescentada a exigência de **glosa obrigatória**: todo ID da intenção citado (`P-NNN`, `H-NNN`, `Q-NNN`, Apêndice) vem glosado em linha na primeira ocorrência, seguindo a disciplina de `docs/o-que-e-o-seja.md`. *Rationale*: sem isso o documento só é legível com `seja-as-intended.md` aberto ao lado, e o público efetivo cai para uma pessoa.

2. **ARCH -> Step 1.** Acrescentado o item (e): enunciar a **direção de dependência** do arranjo proposto e o que ela proíbe -- nada do lado SEJA importando API específica de Claude Code, fronteira nomeada como protocolo e não biblioteca. O antigo item (e) virou (f). *Rationale*: sem o enunciado, o reenquadramento é slogan e a construção pode "implementar o serviço" preservando o acoplamento sem que nada detecte.

3. **ARCH -> Step 6.** Acrescentado o registro de que `DECISION_APPEND` não se aplica a `seja-as-intended.md` (não há seção `## Decisions`), com a questão nova apontando para `Q-006` em vez de propor a seção unilateralmente. *Rationale*: o mecanismo de registro de decisão do harness não alcança o arquivo onde as decisões sobre o harness moram -- é achado, e é matéria já aberta em `Q-006`.

4. **SEC -> Step 3.** Acrescentado o bloco **fronteira de confiança na recuperação**: quem pode chamar, o que a chamada devolve, o que nunca sai do processo -- com os dois casos concretos (`conversation-trace.jsonl` e o mascaramento na escrita; trechos devolvidos fora do arquivo de origem). *Rationale*: as exclusões de ingestão não cobrem a segunda travessia, e o ponto do plano é justamente que quem chama deixa de ser só o Claude Code.

5. **COMPAT -> Step 4.** Acrescentado o problema 2 (compatibilidade de projetos pré-KB e classificação SemVer da mudança), com recomendação a registrar -- KB aditiva e opcional no MVP, degradando para o comportamento atual quando ausente. O antigo problema 2 virou 3. *Rationale*: `.seja-version` e o modelo de release A2 dependem da classificação estar certa; deixá-la implícita é como o modelo de release quebra em silêncio.
