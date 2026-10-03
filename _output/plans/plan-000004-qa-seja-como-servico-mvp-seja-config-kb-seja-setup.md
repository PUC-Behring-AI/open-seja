# QA Log | Plan 000004 | 2026-09-04 20:15 UTC | seja como serviço MVP: seja-config, KB e o papel do seja-setup

## Brief

explorar e documentar: intenção seja como um serviço mvp utilizado por uma harnerss. o que seria o seja-setup ? teriamos que ter um seja-config antes para acoplar uma llm. seja-setup cria o necessario para instanciar uma KB no repositorio, que será usado para o design e outras interaçòes seja-like

## Q&A Log

## Q1

explorar e documentar: intenção seja como um serviço mvp utilizado por uma harnerss. o que seria o seja-setup ? teriamos que ter um seja-config antes para acoplar uma llm. seja-setup cria o necessario para instanciar uma KB no repositorio, que será usado para o design e outras interaçòes seja-like

## A1

Antes de planejar, levantei o estado real das quatro peças do brief no repositório:

- **`seja-config` não existe.** Não há nenhuma camada de acoplamento de LLM em lugar nenhum do harness. O SEJA hoje pressupõe estar rodando dentro do Claude Code; `resolve_seja_version.py` e `detect_setup_state.py` têm `simonedjb/seja` hardcoded, e `conventions.md` não tem nenhuma linha de provedor ou modelo.
- **`/seja-setup` hoje scaffolda arquivos, não conhecimento.** Cinco modalidades (install / `--here` / `--workspace` / `--demo` / `--upgrade`), despachadas por estado via `detect_setup_state.py`. Escreve `CLAUDE.md`, `.claude/rules/`, `conventions.md`, `.seja-version`. Nenhum índice, nenhum embedding, nenhuma recuperação.
- **Não há conceito de KB no SEJA.** A maquinaria RAG referida no brief (ChromaDB + sentence-transformers + MCP `query_knowledge`) vive no repositório-pai Doutourado como Pegasus, inteiramente fora deste harness.
- **A intenção já tem o gancho.** `H-004` diz que o orquestrador compõe agentes e *é* o preposto; `Q-003` (como o harness detecta a posição na escala citizen<->power) está explicitamente sustentada em aberto. Um `seja-config` é uma resposta plausível a `Q-003` que o documento deliberadamente não tomou.

## Q2

(AskUserQuestion) O brief cobre três coisas inexistentes (seja-config, KB no repo, SEJA-como-serviço) mais a redefinição do seja-setup. Qual artefato você quer? / O brief está escrito em registro de intenção, não de construção. Como enquadrar?

## A2

**Plano único exploratório** e **enquadramento metacomm (voz eu/você)**.

A pontuação da detecção automática de modo tinha empatado (3 entidades distintas e múltiplas camadas apontavam para roadmap; verbo único "explorar e documentar" e referência a componente específico apontavam para plano único), então a escolha foi levada ao designer em vez de arbitrada. A escolha de plano único descartou o roadmap com a razão certa: um roadmap agenda construção e pressupõe o WHAT assentado, e três das quatro peças não existem sequer como especificação.

## Q3

Como o plano ficou?

## A3

Sete passos, três arquivos, revisão em profundidade Standard.

O plano não constrói: ele produz `docs/seja-as-a-service.md` (o documento de exploração, em cinco seções encadeadas), registra na intenção do projeto o que a exploração assentou, e entrega `_output/roadmaps/roadmap-spec-seja-service-mvp.md` preenchido para que a construção possa ser agendada depois com `/plan --roadmap --from-spec`.

Achados que estruturaram o plano:

- **Por que `seja-config` precede `seja-setup`, com razão técnica e não estética.** Hoje o acoplamento da LLM é inteiramente da harness -- `/seja-setup` roda dentro de uma sessão Claude Code já ativa e usa `AskUserQuestion`, logo o modelo já está acoplado quando o setup começa, e um `seja-config` seria supérfluo. Ele passa a ser necessário no instante exato em que o SEJA precisa **indexar** um corpus, porque indexar exige um modelo de embedding que a harness não fornece. Essa é a dependência que força a ordem que o brief intuiu.
- **Por que uma KB e não carga eager.** O argumento mais forte já está visível no harness: `pre-skill` tem `context_budget` em três níveis, os briefs são janelados por recência em 50 entradas com um resumo explícito de "N earlier entries ... not loaded", e `/plan` usa protocolo demand-pull de referências. Os três são contornos da mesma ausência.
- **Duas tensões reais com a intenção registrada**, que o documento deve expor em vez de resolver em silêncio: o Apêndice B.1 nota 2 afirma que a camada de design vem **de fora** do projeto, enquanto o brief pede uma KB **no repositório** (resolve-se se a localização seguir o eixo embedded/companion-workspace); e o Apêndice B.2 desenha `Docs -> Harness -> LLM` com o SEJA *sendo* a harness, enquanto o brief propõe `Harness -> SEJA -> LLM` com o SEJA sendo serviço consumido -- reordenação da figura, não leitura dela.
- **`Q-003` fica fechada como estava.** Está sustentada em aberto por decisão de 2026-08-26 porque depende de `Q-002` (granularidade da escala). Fixar um campo de escala no `seja-config` fecharia `Q-002` por via indireta. O plano registra o `seja-config` como hospedeiro natural futuro desse campo, em forma de questão.
- **Restrição de escrita verificada.** `product-design/seja-as-intended.md` é `Human (markers)`. `apply_marker.py` só aplica `STATUS`, `CHANGELOG_APPEND`, `DECISION_APPEND`, `ESTABLISHED`, `INCORPORATED`, `REQ_TRACED_BY` -- e `DECISION_APPEND` levanta erro sem uma seção `## Decisions`, que aquele arquivo não tem. Só `CHANGELOG_APPEND` é aplicável; prosa nova é autoria humana, entregue pronta para colar.

## Q4

O que a revisão mudou?

## A4

Profundidade Standard (7 passos, piso `light`, sem flag). Shortlist por prefixo `DOCUMENT-O` -> DX, OPS, COMPAT, mais ARCH (o núcleo é uma reordenação de fronteira) e SEC (a KB ingere o repositório para cópia local pesquisável). As duas fases foram conduzidas em linha, sem despachar o subagente `plan-reviewer`, por restrição desta sessão a subagentes só mediante pedido explícito.

Quatro deep-dives, cinco emendas, convergência na iteração 1:

1. **DX** -- o documento citava `H-002`, `Q-003`, Apêndices por ID sem glosa, o que o tornaria legível só com o arquivo de intenção aberto ao lado. Passou a exigir glosa em linha na primeira ocorrência, seguindo a disciplina de `docs/o-que-e-o-seja.md`.
2. **ARCH** -- dizer que o SEJA passa a ser serviço consumido é uma afirmação sobre direção de dependência, e o plano a fazia sem enunciar o que ela **proíbe**. Passou a exigir o enunciado: nada do lado SEJA importando API específica de Claude Code, fronteira nomeada como protocolo e não biblioteca. Sem isso, a construção pode "implementar o serviço" preservando o acoplamento sem que nada detecte.
3. **ARCH** -- verificado em `apply_marker.py` que o mecanismo de registro de decisão do harness não alcança o arquivo onde as decisões sobre o harness moram. Passou a ser achado registrado, ligado a `Q-006`, em vez de proposta unilateral de criar a seção.
4. **SEC** -- o plano tratava exclusão de **ingestão** como se fosse a superfície inteira. A recuperação é uma segunda travessia: `query_knowledge` devolve passagens a quem chamar, e o ponto do plano é justamente que quem chama deixa de ser só o Claude Code. Passou a exigir enunciado próprio de fronteira de confiança (quem chama / o que volta / o que nunca sai), com os dois casos concretos.
5. **COMPAT** -- nenhum passo tratava de projetos já instalados em `v0.9.1` sem `seja-config` nem KB, nem classificava a mudança sob SemVer. Como `.seja-version` e o modelo de release A2 dependem dessa classificação, deixá-la implícita é como o modelo de release quebra em silêncio. Passou a exigir o caso e a classificação, com recomendação a registrar (KB aditiva e opcional no MVP, degradando para o comportamento atual quando ausente).

Um conflito checado, entre SEC e DX (mais texto de fronteira vs. mais texto de glosa): incidem em seções diferentes e nenhuma restringe a outra, então não houve trade-off a arbitrar.

## Observações

- `product-design/constitution.md`, `product-design-as-coded.md` e `product-design-as-intended.md` não existem neste repositório -- a intenção mora em `product-design/seja-as-intended.md`, com IDs `P`/`H`/`Q`/`D` em vez do formato §0-§17 do template. `Q-006` já rastreia esse descompasso. `product-design/security-checklists.md`, referenciado pelo `CLAUDE.md` da raiz, também está ausente; a regra de credencial por referência se apoia em `check_secrets.py`.
- `product-design/seja-as-intended.md` não tem marcadores `<!-- REQ-*-NNN -->`, então a checagem de cobertura (passo 4b) foi pulada em silêncio.
- plan-000001 (`npx open-seja`) segue pendente há 23 dias e é o hospedeiro natural do passo de configuração não-interativo. Anotado como dependência externa no Step 7.
