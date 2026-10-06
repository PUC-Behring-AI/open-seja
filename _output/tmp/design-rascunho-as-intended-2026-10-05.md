# Rascunho para o /design do open-seja (branch dev) -- 2026-10-05

> Preparado a partir de `product-design/seja-as-intended.md` (P-001..P-007, H-001..H-008, Q-001..Q-013, D-001, D-002), do `README.md`, do `conventions.md` e dos planos movidos (roadmap-000006, plan-000007..000016). Nada aqui e novo em relacao ao que esses arquivos ja dizem, exceto o que esta marcado **[DECIDIR]** (escolha sua) ou **[intended]** (estado pretendido, nao atual). Sem nomes de parceiros nem de pessoas.
>
> Uso: rode `open-seja:design` dentro de `open-seja/`; quando o questionario pedir cada secao, cole o bloco correspondente e corrija a voz. As secoes 11, 12, 14 e 15 sao as que o harness mais le (metacomunicacao e jornadas); as secoes 2 a 10 podem ficar curtas.
>
> Resposta a Q-006 que este rascunho assume: **semear ao lado**. O `seja-as-intended.md` continua como fundamentacao teorica (P, H, Q); o `product-design-as-intended.md` e o documento operacional que o harness le, e cita a fundamentacao por ID.

---

## Parte A -- product-design-as-intended.md

### 0. Planned Changes

| Target Version | Change Summary | Motivation / Rationale |
|---|---|---|
| v0.11 | Ciclo default com fases grill e specify dentro do `/plan`, teste-primeiro por cenario no `/implement`, divergencia por degrau no `/reflect` (roadmap-000006, H-009) -- STATUS: intended | Decompor a intencao em representacoes progressivamente formais (intencao detalhada -> cenarios -> testes -> codigo) para que o as-coded divirja menos do as-intended, com a divergencia medida por degrau e nao so no fim. |
| v0.11 | Retraducao em primeira pessoa como objeto de aprovacao do citizen no specify e no REFLECT; `.feature` como contrato aprovado pelo power dev -- STATUS: intended | Features sao contratos enderecaveis, nao signos; o citizen aprova a mensagem (ver D-004 proposta abaixo). |
| v0.11 | Voz controlada (STE100) como voz padrao de `/explain`, `/communicate`, `/document`; `--html` autocontido -- STATUS: intended (plan-000074 do ledger do pesquisador) | O citizen le em frases curtas e termos fixos. |
| v0.12+ | Presets `apprentice` (iniciantes em programa de formacao) e `literature-reviewer` (revisao sistematica) gerados a partir do open-seja pinado, dependencia unidirecional preset -> open-seja -- STATUS: intended | Pontos discretos da escala H-001 (Q-002) sem bifurcar o ciclo; comparabilidade de artefatos entre instancias. |
| futuro | SEJA como servico (`seja-mcp`) -- STATUS: intended, parado | Rumo de arquitetura; o ciclo consome o harness como ele estiver. |

### 1. Platform Purpose

O open-seja e a distribuicao de acesso aberto do SEJA (Semiotic Engineering Journeys with Agents). Instalado num projeto de software, ele da ao Claude Code um ciclo curto, PLAN -> BUILD -> REFLECT, em que a intencao e escrita antes do codigo e comparada com o que foi construido, cada passo de implementacao so conta como feito quando um portao deterministico responde PASS, e cada fase termina com um espelho oferecido ao designer.

E para dois publicos. O primeiro sao desenvolvedores ao longo de uma escala continua de literacia de codigo (H-001): do citizen dev, que tem a intencao e o dominio do problema mas nao le codigo, ao power dev, que le codigo fluentemente e quer aceleracao, controle e rastreabilidade. O segundo sao pesquisadores que estudam o harness como objeto: a pergunta que ele serve e como o sistema comunica ao humano as intencoes que realizou, e se essa comunicacao e reconstruivel por quem a recebe.

O problema que resolve: desenvolvimento assistido por IA e um problema de comunicacao projetada (P-001, P-002). Quando um agente produz o codigo a partir de uma intencao dita em linguagem natural, a traducao pode estar errada sem estar quebrada, e o humano que nao le codigo nao tem como saber. O open-seja torna a intencao um signo enderecavel (H-002), mede a deriva entre o que se pretendia e o que existe, e devolve ao humano, no registro que ele decodifica, o que o preposto entendeu e construiu (P-003).

#### Design Philosophy

- **O artefato e uma mensagem, nao um produto** (P-001): cada arquivo que o harness ajuda a produzir e andaime para a comunicacao designer -> usuario.
- **O dev fala, o robo produz, as ferramentas apoiam o robo** (P-002): o preposto do designer deixou de ser estatico e compoe a fala no momento do uso.
- **O receptor nao e unico** (H-001): para o citizen dev, o codigo nao pode ser a mensagem; o harness produz os signos metalinguisticos que falam sobre ele.
- **Ha um caminho de volta** (P-003): o robo devolve ao humano o que entendeu e construiu; a retraducao e obrigatoria no polo citizen e eletiva no polo power (H-003).
- **As convencoes sao um sistema de signos projetado, nao estilo** (P-004): marcadores, classificacoes de autoria e IDs dizem de quem e a voz em cada arquivo.
- **Validar antes de comunicar** (P-005): `/critique` sempre precede `/document` e `/communicate`.
- **Skill orquestra, agente executa** (P-006, P-007, H-004): o orquestrador e o preposto; os agentes sao o vocabulario; a composicao varia com a posicao do humano na escala.
- **PASS e resultado de ferramenta, nao frase** (H-008): prosa no prompt nao e plano de controle; o limiar so se move por mao humana.
- **Tudo aqui e hipotese numerada com condicao de refutacao**: o SEJA aplica a si mesmo o raciocinio abdutivo que declara adotar.

### 2. Entity Hierarchy

Duas hierarquias paralelas: a **estrutura do harness** (o que existe) e a **escada de representacoes** (intended, roadmap-000006).

```
Projeto com o harness instalado
└── Intencao (product-design/)
    ├── product-design-as-intended.md   (voz humana; agentes marcam)
    ├── seja-as-intended.md             (fundamentacao: P, H, Q, D)
    ├── constitution.md, standards.md, conventions.md
    └── product-design-as-coded.md      (voz do agente; regenerado)
└── Ledger (_output/)
    └── Artefato com ID global (research, plan, roadmap, proposal, reflection, communication, qa-log)
        └── Plano
            └── Step (Files, Verify, Tests, Traces; Scenarios em v2 [intended])
                └── Resultado do portao (gate JSON por step)
└── Harness (.claude/)
    ├── Skill (orquestra; pre-skill e post-skill envolvem toda invocacao)
    │   └── Agente (avaliador | gerador | executor; contexto isolado)
    └── Scripts de verificacao (check_*.py, run_all_checks.py, gate)
```

```
[intended] Feature (features/<slug>/)
└── intent.md         (REQ-<slug>-NNN; "Nas suas palavras"; Fora do escopo; Premissas; Para que; Modelo e termos; serve:)
    └── *.feature     (cenario com @REQ-<slug>-NNN; contrato)
        └── teste executavel (vermelho pelo motivo certo, depois verde)
            └── codigo + gate.json (perimetro da feature)
```

#### Projeto
- **Representa**: um repositorio de software onde o open-seja foi instalado por `/seja-setup`.
- **Regra de dominio**: sem `product-design-as-intended.md` nao ha ciclo; `/design` precede o primeiro `/plan` (D-002).

#### Intencao
- **Representa**: o que o designer quer, em arquivo. Tres estados: as-conceived (na cabeca, sem artefato), as-intended (registrado), as-coded (o que existe) (H-005).
- **Regra**: as-intended e as-coded ficam separados de proposito; a distancia e a deriva, e `/explain drift` a reconcilia.

#### Artefato do ledger
- **Representa**: a saida de uma skill, com ID sequencial global reservado por `reserve_id.py`.
- **Regra**: imutavel depois de criado; correcao e por apensamento (revoked/superseded com motivo), nunca por reescrita.

#### Plano e Step
- **Representa**: compromisso de construcao; cada step declara arquivos, verificacao, testes e intencoes que atende (`Traces:`).
- **Regra**: em BUILD, step so conta como feito com PASS do portao; o `/critique` do fim mede o que escapou.

#### Skill e Agente
- **Representa**: a skill conduz a conversa e decide a composicao; o agente executa um papel sobre um tipo de artefato, em contexto isolado.
- **Regra**: o usuario nunca invoca um agente diretamente (P-006).

#### Feature [intended]
- **Representa**: a unidade de medida da divergencia por degrau; nunca apagada (git e a recuperacao).
- **Regra**: a feature e o perimetro de medicao; fora dele e `legado: nao medido`.

### 3. Domain-Specific Concepts

- **Preposto do designer**: a voz do designer atravessando o sistema no momento do uso; aqui, generativo (P-002).
- **Mensagem de metacomunicacao**: "eis meu entendimento de quem voce e, o que quer, de que modo, por que; eis o sistema que projetei e como usa-lo".
- **Retraducao (mao de volta)**: o preposto devolve ao humano o que entendeu e construiu, no registro que ele decodifica (P-003).
- **Escala citizen <-> power**: eixo de literacia de codigo, ortogonal a BLD/SHP/GRD e L1-L3 (H-001, Q-002).
- **Deriva**: distancia entre as-intended e as-coded; cidada de primeira classe (H-002).
- **Portao deterministico**: lint, tipos, testes com cobertura por ramo, CRAP nas funcoes tocadas, contratos de dependencia e, na rodada lenta, mutacao; PASS e resultado de ferramenta (H-008).
- **Ratchet e baseline**: o limiar so se move por mao humana; o agente nao aceita baseline nem pula o portao.
- **Espelhos por fase**: o plano contado a uma audiencia (PLAN) e a deriva medida (BUILD), oferecidos, nunca impostos.
- **Tres registros de Schon**: na-acao (justificativa de cada opcao), sobre-a-acao (nota por step e por skill), sobre-a-pratica (`/reflect`, palavras literais).
- **Hipotese H-NNN**: enunciado com o que a confirmaria e o que a refutaria; nao e decisao.
- **Classificacoes de autoria**: Human, Human (markers), Human/Agent, Agent; dizem de quem e a voz em cada arquivo (P-004, Q-007).
- **Escada de representacoes [intended]**: brief -> intent.md -> .feature -> teste -> codigo + gate, com divergencia por degrau (H-009).
- **Degrau zero [intended]**: residuo do brief que nao virou requisito nem fora-do-escopo; leitura fora do vetor D.
- **Contrato enderecavel [intended]**: o `.feature` e um par expressao-conteudo convencionalizado entre humano e preposto; REQ IDs e chaves de cenario sao enderecos, nao signos.
- **Preset [intended]**: perfil gerado a partir do open-seja pinado, com dependencia unidirecional preset -> open-seja; nao e fork.

### 4. Permission Model

Nao ha login. O modelo de permissao do open-seja e sobre **quem pode escrever em que arquivo** e **o que o agente nao pode fazer**.

#### System-Level Roles

| Role | Level | Capabilities |
|---|---|---|
| Designer (humano) | owner | Escreve prosa em arquivos Human e Human (markers); aprova marcadores; move o ratchet do portao; aceita ou recusa espelhos |
| Agente (skills e subagentes) | agent | Escreve em `_output/` e em arquivos Agent (as-coded, indices); aplica marcadores via `apply_marker.py` apos confirmacao; nunca edita prosa Human (markers) |
| Leitor da distribuicao | reader | Clona `main` (manifesto exclui `_output/**` e `product-design/conventions.md`), roda `/seja-setup --here` |

#### Resource-Level Access

| Access Level | Level | Capabilities |
|---|---|---|
| `main` (distribuicao) | public-org | So o que o `tools/publish-manifest.txt` inclui; sem ledger, sem conventions do proprio open-seja |
| `dev` (desenvolvimento) | restricted | Ledger `_output/`, `product-design/` completo, planos do ciclo default |
| Denies ao agente | enforced | `git commit --no-verify` e `gate --accept-baseline` negados por permissao; hooks `Stop` e `PreToolUse` rodam o portao |

> **Rationale:** a unica fronteira que importa e a da voz (P-004, Q-007) e a do ratchet (H-008): o humano e o dono das restricoes; o agente fica no laco interno.

### 5. Content Authoring & Attribution

Duas vias de autoria escrevem no mesmo codigo (P-002a, Q-007 aberta). O harness distingue a voz por classificacao de arquivo e por marcador, nao por sistema de atribuicao em app. Regras: palavras do designer sao registradas literalmente (regra do verbatim); a mensagem de metacomunicacao usa "eu" (designer) e "voce" (usuario), nunca terceira pessoa; agentes marcam `source: agent (...)` no que escrevem. O open-seja e derivado do SEJA sob CC BY-NC 4.0; a atribuicao e o uso do nome estao em `README.md` e `TRADEMARKS.md`.

### 6. Content Import & Export

#### Import Formats

| Format | Source | Features |
|---|---|---|
| Codebase existente (brownfield) | repositorio do usuario | `/seja-setup --here` instala o harness; `/design` registra a intencao a partir do que existe |
| Questionario de design | `/design` | Gera as-intended, constitution, standards, conventions |
| Spec de roadmap | `--from-spec <path>` | Roadmap com waves a partir de arquivo preenchido |
| Palavras do designer | `/reflect`, `--framing metacomm` | Registradas verbatim |

#### Export Formats

| Format | Output | Use Case |
|---|---|---|
| Markdown | `_output/**` | Todo artefato do ledger |
| HTML autocontido | `--html` em `/explain`, `/communicate`, `/document` [intended] | Leitura fora do terminal |
| Material por segmento | `/communicate` (EVL, CLT, USR, ACD) | O plano contado a uma audiencia (espelho do PLAN) |
| Release | `main` pelo manifesto; tag `vX.Y.Z`; instalador `npx` (nao publicado) | Distribuicao |

### 7. User Community & Localization

#### Target Community

Times de desenvolvimento ao longo da escala H-001, do citizen ao power dev, cruzada com as familias de papel (BLD Builders, SHP Shapers, GRD Guardians) e os niveis L1-L3. Segundo publico: pesquisadores de engenharia semiotica e de engenharia de software que estudam o harness como objeto. Instancias previstas [intended]: programa de formacao de iniciantes (`apprentice`) e revisao sistematica de literatura (`literature-reviewer`).

#### Localization Design

| Aspect | Primary | Secondary |
|---|---|---|
| Sessoes de design e `seja-as-intended.md` | pt-BR | -- |
| `docs/` e README publicos | en-US | pt-BR (Q-005 aberta) |
| Voz ao citizen | voz controlada (frases curtas, termos fixos) [intended] | -- |

> Codigo, identificadores e mensagens de log em en-US. **[DECIDIR Q-005]**: traduzir a fundamentacao para en-US junto com `docs/`, ou mante-la em pt-BR.

### 8. User Experience Patterns (Domain-Driven)

A interface e a conversa no Claude Code. Padroes proprios:

- **Decisao com justificativa**: toda `AskUserQuestion` traz, por opcao, "Recommended when" e "NOT recommended when" (reflexao-na-acao). Nenhuma opcao e pre-aceita por enquadramento.
- **Files for review** antes de qualquer pergunta que cite artefato ja gerado.
- **Espelho oferecido, nunca imposto**: `/communicate` do plano ao fim do PLAN; `/explain drift` ao fim do BUILD; o `/reflect` registra quando nao foram medidos.
- **PASS como resultado**: o portao devolve achados por funcao, nunca resumo em prosa.
- **Progress file** por plano, com nota por step.
- [intended] **Grill e specify**: entrevista em rodadas curtas, uma ideia por pergunta; aprovacao em voz controlada; o citizen aprova a mensagem, o power dev aprova o contrato.

### 9. Administrative Domain

#### Activity Logging
`_output/briefs.md` (toda invocacao de skill), `telemetry.jsonl` (um registro por skill), `conversation-trace.jsonl`, `pending.jsonl` (acoes humanas pendentes), `INDEX.md` (catalogo). Git e o log de mudancas.

#### Backup & Restore
Git. Artefatos do ledger sao imutaveis; nao ha soft-delete.

#### Terms & Conditions
CC BY-NC 4.0 (derivado do SEJA), uso nao comercial, sem garantias; nome usado com permissao do detentor da marca.

### 10. Validation Constants (Domain)

| Constant | Value | Domain Rationale |
|---|---|---|
| CRAP maximo em funcoes tocadas / teto absoluto | 10 / 30 (defaults do gate; ratchet a partir do baseline) | Funcoes minusculas e cobertas; o limiar desce por mao humana |
| `--fast` do portao | <= 90 s, sem mutacao | Portao por step tem de caber no laco interno |
| Tentativas por step no modo auto | 3, depois falha no progress file | O agente nao insiste indefinidamente |
| Pendencia vencida / escalada / auto-dismiss | 14 / 30 / 90 dias | Conforme `conventions.md` |
| [intended] Grill: rodadas x perguntas | 5 x 4 | Teto, nao alvo; depois devolve a decisao ao citizen |
| [intended] Specify: rodadas de ajuste | 3 | Ajuste repetido indica REQ vago; volta a grill |
| [intended] Voz controlada | 25 palavras por frase; 6 frases por paragrafo | Legibilidade para o citizen |

> Conferir os valores vigentes em `conventions.md` e no `gate.py` do template antes de fixar.

---

### 11. Global Metacommunication Vision

> "Eu sei que voce quer construir software com um agente que escreve mais rapido do que voce consegue revisar, e que talvez voce nao leia o codigo que ele escreve. Por isso eu peco que voce me diga o que quer antes de qualquer codigo, nas suas palavras, e eu o registro como intencao que uma maquina consegue enderecar. Eu so considero um passo feito quando uma ferramenta, e nao uma frase, diz que passou. Ao fim de cada fase eu lhe ofereco um espelho: o plano contado a quem voce escolher, e a distancia entre o que voce pediu e o que existe. E eu lhe devolvo, no registro que voce le, o que entendi, o que construi e o que nao construi, para que voce exerca autoria sem precisar ler codigo. Tudo isso e uma aposta que eu numero e me comprometo a refutar se os dados disserem o contrario."

### 12. Extended Metacommunication Template Guiding Questions

1. Analise
   1.1. **O que sei sobre voce.** Sei que voce esta em algum ponto de uma escala de literacia de codigo (H-001), e que isso decide em que sistema de signos eu posso lhe falar de volta. Aprendi isso observando que, para quem nao le codigo, entregar o codigo nao e comunicar. Nao sei ainda quantos pontos a escala tem nem como detectar o seu (Q-002, Q-003, deliberadamente abertas).
   1.2. **Sobre os outros afetados.** Sei que o seu time, os revisores e os leitores da documentacao recebem o que voce comunica; por isso nada sai do envelope sem `/critique`. Sei que pesquisadores estudam o que eu faco; por isso registro tudo com ID e proveniencia.
   1.3. **Contextos de uso.** Dentro do Claude Code, num repositorio seu, local; em `dev` para quem me desenvolve, em `main` para quem me instala.
   1.4. **Questoes eticas.** Duas vias de autoria no mesmo codigo (Q-007): de quem e a voz que o leitor le? E o risco de delegacao cega no polo citizen e de ritual no polo power (H-003).
2. Design
   2.1. **O que projetei para voce.** Um ciclo PLAN -> BUILD -> REFLECT com portao deterministico por passo, espelhos por fase e um caminho de volta.
   2.2. **Que objetivos apoio.** Dizer a intencao antes do codigo; construir com validacao por passo; saber o que escapou; refletir antes do proximo turno.
   2.3. **Em que situacoes.** Em qualquer engajamento de desenvolvimento, do primeiro `/design` ao `/reflect`; com portao quando a stack o tem, sem portao quando nao (e eu digo que nao medi).
   2.4. **Como usar.** `/seja-setup`, depois `/design` uma vez, depois `/plan`, `/implement`, `/reflect`; aceite ou recuse os espelhos.
   2.5. **Para que nao quero que use.** Para pular o portao (`--no-verify`, `--accept-baseline` pelo agente), para editar prosa humana por agente, para tratar hipotese como decisao, para publicar sem `/critique`.
   2.6. **Principios eticos.** A voz pertence a quem a emitiu; o humano e dono das restricoes; o que nao foi medido e dito como nao medido.
   2.7. **Alinhamento.** Classificacoes de autoria e marcadores (P-004); ratchet so por mao humana; estados `nao medido` sempre visiveis.
3. Prototipacao, implementacao e avaliacao formativa
   3.1. **Como construi.** Skills em Markdown que orquestram agentes em contexto isolado; scripts Python deterministas de verificacao; template de portao por stack.
   3.2. **O que construi para prevenir mau uso.** Hooks `Stop` e `PreToolUse`, denies de permissao, verificador de marcadores humanos, imutabilidade de artefatos.
   3.3. **Para identificar efeitos nao antecipados.** Deriva as-intended/as-coded, taxa de escape do `/critique`, notas por step, `/reflect` com palavras literais.
   3.4. **Cenarios eticos avaliados.** Agente aceitando baseline; agente editando intencao humana; aprovacao do citizen virando ritual ("parece bem").
4. Avaliacao continua
   4.1. **Quanto da visao se reflete no uso.** H-008 ainda nao medida; o primeiro ciclo real com portao gera a primeira medida.
   4.2. **Usos nao antecipados.** [a registrar]
   4.3. **Efeitos.** [a registrar]
   4.4. **Questoes a tratar por redesign.** Se escapes de intencao forem frequentes com PASS, o espelho deixa de ser oferta e vira passo fixo (refutacao iv de H-008).

### 13. Solution Representations

#### SS-001: O power dev roda um ciclo com portao
- **Persona**: power dev (le codigo; quer aceleracao e rastreabilidade)
- **Goals**: construir uma feature com validacao por passo e saber o que escapou
- **Setting**: repositorio Python com o portao instalado; `/design` ja feito
- **Design Rationale**: o portao ocupa o lugar da validacao dentro de BUILD (H-008); o `/critique` final mede o escape

O dev escreve o brief, o `/plan` gera e revisa o plano, o `/implement` em modo auto roda o portao `--fast` a cada step (ate 3 tentativas), o `/critique` cruza achados com steps em PASS, o `/explain drift` e oferecido com o as-coded regenerado, e o `/reflect` registra o que o episodio ensinou e o que nao foi medido.

#### SS-002 [intended]: O citizen dev aprova a mensagem, nao o codigo
- **Persona**: citizen dev (tem a intencao; nao le codigo)
- **Goals**: exercer autoria sem ler codigo; reconhecer a propria intencao no que voltou
- **Setting**: mesma escada, sem perfil; muda o objeto de aprovacao
- **Design Rationale**: para o citizen o codigo nao pode ser a mensagem (H-001); features sao contratos, a mensagem e a retraducao (D-004 proposta)

O citizen responde a grill nas proprias palavras; aprova a lista de requisitos; recebe a retraducao em primeira pessoa com exemplos narrados e a lista do que nao sera feito, e aprova a mensagem; o power dev (ou ele mesmo, em outro papel) aprova o `.feature` como contrato; ao fim, recebe a demonstracao por cenario, os mutantes sobreviventes recontados como perguntas e o que ficou `nao medido`.

#### US-001
Como designer, quero registrar a intencao antes do codigo para que a deriva tenha contra o que ser medida. Criterios: `/plan` recusa partir sem as-intended; todo step declara `Traces:`.

#### US-002
Como power dev, quero que cada passo so conte como feito com PASS para que a validacao nao dependa da minha velocidade de revisao. Criterios: portao por step; 3 tentativas; denies de `--no-verify` e `--accept-baseline`.

#### US-003 [intended]
Como citizen dev, quero aprovar o que vai ser construido num texto que eu reconheca, e saber o que nao foi construido, para nao delegar as cegas. Criterios: retraducao com "Nas suas palavras" ao lado; ausencias enumeradas; nenhum numero tecnico no meu registro.

### 14. Per-Feature Metacommunication Intentions

| Feature / Flow | Designer Intent | Priority | Source | Last Synced |
|---|---|---|---|---|
| `/seja-setup` | Eu instalo o harness no seu repositorio e lhe entrego ao `/design`, porque sem intencao registrada nao ha ciclo. | P0 | human | 2026-10-05 |
| `/design` | Eu registro, nas suas palavras, quem voce e, o que quer e por que, e os principios que nao negocio, porque tudo o que vem depois e medido contra isso. | P0 | human | 2026-10-05 |
| `/plan` | Eu transformo o seu brief num plano com passos rastreaveis a intencao, reviso-o em perspectivas e lhe ofereco conta-lo a uma audiencia antes de construir. | P0 | human | 2026-10-05 |
| `/implement` com portao por step | Eu so considero um passo feito quando o portao responde PASS, e paro na terceira falha; eu nao movo o limiar, voce move. | P0 | human | 2026-10-05 |
| `/critique` | Eu valido antes de qualquer coisa sair para um leitor, e no fim do BUILD mec o que escapou do portao. | P0 | human | 2026-10-05 |
| `/explain drift` (espelho do BUILD) | Eu lhe mostro a distancia entre o que voce pediu e o que existe, com o as-coded regenerado, e digo o que nao medi. | P1 | human | 2026-10-05 |
| `/communicate` (espelho do PLAN) | Eu conto o plano a quem voce escolher, porque plano que nao sobrevive a ser contado nao esta claro. | P1 | human | 2026-10-05 |
| `/reflect` | Eu registro as suas palavras literalmente, sem prescrever mudanca, e anoto o que nao foi medido. | P1 | human | 2026-10-05 |
| Marcadores e classificacoes de autoria | Eu digo de quem e a voz em cada arquivo e nunca escrevo prosa no lugar de voce. | P0 | human | 2026-10-05 |
| Hooks e denies | Eu nao deixo o agente pular o portao nem aceitar baseline; isso e seu. | P0 | human | 2026-10-05 |
| [intended] Grill e specify no `/plan` | Eu pergunto o que voce quer, um pouco de cada vez e nas suas palavras, escrevo de volta como requisitos e so sigo para os cenarios depois que voce aprovar. | P1 | human | 2026-10-05 |
| [intended] Retraducao como objeto de aprovacao | Eu lhe mostro o que entendi e o que vou construir em primeira pessoa, com exemplos; voce aprova a mensagem, e o contrato fica para quem le codigo. | P1 | human | 2026-10-05 |
| [intended] Divergencia por degrau | Eu mostro onde a sua intencao se perdeu, degrau a degrau, com o que nao medi ao lado, em vez de uma nota unica. | P1 | human | 2026-10-05 |
| [intended] Presets | Eu me ofereco em perfis gerados a partir de mim, sem bifurcar o ciclo, para pontos da escala que precisam de outro registro. | P2 | human | 2026-10-05 |

### 15. Designed User Journeys

#### JM-TB-001: Primeiro ciclo de um power dev com portao
- **Persona**: power dev
- **Solution Scenario**: SS-001
- **Goal**: uma feature construida com validacao por passo e deriva medida
- **Pre-conditions**: `/seja-setup --here` feito; `/design` feito; portao instalado e baseline aceito pelo humano

| # | Action | Touchpoint | User Emotion | Pain Point | Opportunity |
|---|---|---|---|---|---|
| 1 | Escreve o brief e roda `/plan` | Claude Code | focado | brief vago gera plano vago | revisao por perspectivas; espelho do PLAN |
| 2 | Aceita ou recusa contar o plano (`/communicate`) | AskUserQuestion | avaliando | friccao se o plano e trivial | espelho oferecido, nunca imposto |
| 3 | Roda `/implement` em modo auto | subagente por step | confiante | esperar o portao | `--fast` <= 90 s; nota por step |
| 4 | Le os achados do `/critique` cruzados com PASS | relatorio | surpreso ou aliviado | achado critico em step com PASS | taxa de escape de H-008 |
| 5 | Aceita ou recusa a deriva (`/explain drift`) | AskUserQuestion | curioso | relatorio longo | `nao medido` sempre visivel |
| 6 | `/reflect` | conversa | reflexivo | parecer ritual | palavras literais; o que nao foi medido |

Post-conditions: feature em PASS, achados do `/critique` registrados, deriva medida ou registrada como nao medida, reflexao gravada.

#### JM-TB-002 [intended]: O citizen dev na escada, aprovando a mensagem
- **Persona**: citizen dev
- **Solution Scenario**: SS-002
- **Goal**: reconhecer a propria intencao no que foi construido, sem ler codigo
- **Pre-conditions**: ciclo default do roadmap-000006 entregue; `features/` no projeto

| # | Action | Touchpoint | User Emotion | Pain Point | Opportunity |
|---|---|---|---|---|---|
| 1 | Responde a grill, nas proprias palavras | rodadas curtas | ouvido | perguntas demais | teto de rodadas; "Nas suas palavras" |
| 2 | Aprova a lista de requisitos e o "nao faz" | resumo em voz controlada | seguro | aprovar o que nao entendeu | criterio por requisito em uma frase |
| 3 | Aprova a retraducao com exemplos narrados | mensagem em primeira pessoa | reconhecendo | "parece bem" sem ler | exemplos narrados; teste da surpresa |
| 4 | Recebe demonstracao por cenario e mutantes recontados | superficie do produto; perguntas | surpreso | mais coisas para olhar | so sobreviventes e cenarios marcados por padrao |
| 5 | Marca "e isso / nao e isso" por requisito | REFLECT | autor | friccao | alimenta a auditoria semantica |

Post-conditions: requisitos com estado demonstrado / nao demonstrado / nao medido / fora do escopo; "nao e isso" com endereco para a maquina agir.

### 16. Conceptual Design Delta

| Section | Element | Description |
|---|---|---|
| §0, §2, §3 | Escada de representacoes, feature, degrau zero, contrato enderecavel | intended; roadmap-000006 |
| §0, §3, §14 | Presets | intended; sem roadmap |
| todas | as-coded | nao existe ainda; o primeiro `/implement` apos este `/design` o instancia |

### 17. Metacommunication Delta

| Feature / Flow | Designer Intent | Priority |
|---|---|---|
| Grill e specify | ver §14 | P1 |
| Retraducao como objeto de aprovacao | ver §14 | P1 |
| Divergencia por degrau | ver §14 | P1 |
| Voz controlada | Eu falo com voce em frases curtas e termos fixos. | P1 |
| Presets | ver §14 | P2 |

---

### Decisions (propostas para `apply_marker.py --marker DECISION_APPEND`)

> **[DECIDIR]**: D-001 e D-002 ficam no `seja-as-intended.md` (fundamentacao) ou migram para ca. Se ficarem la, este arquivo comeca em D-003 e cita D-001/D-002 por referencia. O rascunho abaixo assume que ficam la.

#### D-003: Presets sao perfis gerados a partir do open-seja pinado, nao forks nem bifurcacoes do ciclo

**Context**: Dois pontos da escala H-001 pedem outro registro de contato: iniciantes num programa de formacao (duas fases: agente-tutor com o aprendiz escrevendo o codigo, depois desenvolver com agentes) e pesquisadores conduzindo revisao sistematica de literatura (DAG com nos humanos, deterministicos e por LLM, run imutavel, proveniencia). Q-002 pergunta quantos pontos discretos a escala precisa.

**Decision**: Um preset e um perfil gerado a partir do open-seja numa tag pinada, com dependencia unidirecional preset -> open-seja, comandos e voz proprios, e artefatos no formato SEJA. O ciclo nao bifurca (H-003): muda a superficie de contato e a obrigatoriedade da retraducao. Dois presets pretendidos: `apprentice` e `literature-reviewer`. A fase do aprendiz e atribuida pelo tutor por marcador Human (markers); enforcement (settings) e separado de instrucao (CLAUDE.md).

**Consequences**: Artefatos comparaveis entre instancias; upgrade por tag; registra dois pontos concretos para Q-002 sem fecha-la. Exige que o orquestrador aceite a posicao na escala como entrada (H-004). Fica como intencao ate haver roadmap.

**Rejected Alternatives**: fork por instancia (sem canal de upgrade, dados incomparaveis); harness novo minimo; tratar o aprendiz como citizen dev com retraducao obrigatoria (a fase 1 pede o inverso: o humano escreve o codigo); ciclo bifurcado por perfil.

#### D-004: Features Gherkin sao contratos enderecaveis, nao signos; o citizen aprova a mensagem, nao o .feature

**Context**: O ciclo default pretendido (roadmap-000006, H-009) decompoe a intencao em intent.md -> .feature -> teste -> codigo e mede a divergencia por degrau. A analise da lacuna da intencao mostrou que o Gherkin representa comportamento observavel e deixa sem signo o porque, o modelo conceitual, as preferencias e as crencas sobre o usuario; que D1 mede presenca de tag, nao fidelidade; e que o ponto de aprovacao do specify mostrava o texto do .feature ao citizen, tratando contrato como mensagem.

**Decision**: O .feature e um contrato enderecavel entre o humano e o preposto (par expressao-conteudo convencionalizado, P-004), nao a mensagem de metacomunicacao. REQ IDs e chaves de cenario sao os enderecos para onde os signos apontam; os signos sao a retraducao em primeira pessoa, os exemplos narrados, os mutantes recontados e as ausencias declaradas. O objeto de aprovacao muda por receptor, sem perfil: o citizen aprova a mensagem; o .feature e derivado dela e aprovado como contrato pelo power dev. Toda emenda ao ciclo e todo signo devolvido ao citizen passam pelo teste da surpresa: deve poder provocar uma ruptura decodificavel pelo receptor; item que so confirma (PASS, percentuais) nao entra no registro do citizen. H-009 declara o proprio alcance: completa para comportamento operacionalizado, com perda declarada de racional, modelo e preferencia; o degrau zero (residuo do brief) e leitura fora do vetor D.

**Consequences**: Emenda ao ponto de aprovacao do specify (plan-000011); tabela degrau x receptor no contrato do ciclo (plan-000007); H-009 com limite declarado e tres medidores de ganho do citizen na condicao de refutacao (ajustes no specify; escapes antes vs depois do codigo; mutantes virados em requisito). A aposta "um caminho sem perfis" se mantem.

**Rejected Alternatives**: tratar o .feature como mensagem (ruptura "parece bem"; conformidade no lugar de reflexao); medir semantica com LLM dentro do D; perfil citizen com cadeia propria (contra H-003); setima dimensao na grill para porque e modelo (o lugar e uma secao nao-cenario do intent.md).

> Q-004 fecha com D-004: a retraducao e etapa do specify e do REFLECT, nao artefato novo nem modo de `/explain`. Q-012 ganha resposta parcial: a retraducao e julgada pelo receptor ("e isso / nao e isso" por requisito), logica CEM, registrada em `audit.json`.

---

## Parte B -- constitution.md

### Project Identity

open-seja: distribuicao de acesso aberto do SEJA; um harness para o Claude Code que trata desenvolvimento assistido por IA como comunicacao projetada, com ciclo PLAN -> BUILD -> REFLECT, portao deterministico por passo e caminho de volta ao humano. Usuario primario: desenvolvedores ao longo da escala citizen <-> power; secundario: pesquisadores do harness.

### Technical Principles

| # | Principle | Rationale |
|---|---|---|
| T1 | PASS e resultado de ferramenta, nao frase. Nenhum passo de BUILD conta como feito sem o portao deterministico (ou sem a declaracao explicita de que o projeto nao tem portao). | Prosa no prompt nao e plano de controle (H-008). |
| T2 | Sem as-intended nao ha ciclo. `/design` precede o primeiro `/plan`; `/plan` recusa partir sem `product-design-as-intended.md`. | A deriva precisa de referencia (D-002, H-002). |
| T3 | Artefatos em `_output/` sao imutaveis; correcao e por apensamento com motivo (revoked / superseded), nunca por reescrita. | Historia de design e evidencia de pesquisa (P-004, SigniFYIng Traces). |
| T4 | Arquivos Human (markers) recebem de agentes apenas marcadores, via `apply_marker.py`, apos confirmacao no mesmo turno. | A voz pertence a quem a emitiu (P-004, Q-007). |
| T5 | Skill orquestra, agente executa, em contexto isolado; o usuario nunca invoca agente diretamente. | P-006, P-007, H-004. |
| T6 | Fronteira agnostica de stack: o harness consome contratos (JSON do portao com codigos de saida por categoria; relatorio do runner) e nunca a ferramenta; stack sem adaptador degrada para `nao medido`, nunca para falha. | O ciclo roda em qualquer linguagem e diz o que nao mediu. |

### Quality Principles

| # | Principle | Rationale |
|---|---|---|
| Q1 | Mudanca no harness so entra com `pytest .claude/skills/scripts/tests/` verde e `run_all_checks.py` sem falha nova em relacao ao baseline. | O harness exige dos projetos o que exige de si. |
| Q2 | `/critique` sempre precede `/document` e `/communicate`. | Validar antes de comunicar (P-005). |
| Q3 | Toda hipotese registrada carrega o que a confirmaria e o que a refutaria; limiares de medida sao fixados antes de ver os dados. | Raciocinio abdutivo aplicado a si mesmo (1.2.4, H-008). |
| Q4 | O que nao foi medido e dito como `nao medido`, ao lado do que foi, nunca escondido em media ou numero unico. | Honestidade do instrumento (H-009, D-004). |

### Security Invariants

| # | Invariant | Rationale |
|---|---|---|
| S1 | O portao roda sem rede e sem chave de API no ambiente filho. | Centenas de rodadas mutadas multiplicariam qualquer vazamento. |
| S2 | O agente nao move o ratchet nem pula o portao: `--accept-baseline` e `git commit --no-verify` negados por permissao; hooks `Stop` e `PreToolUse` ativos. | O humano e o dono das restricoes (H-008). |
| S3 | Nenhum segredo em fonte ou em `_output/`; `.env` gitignored. | Chave commitada e chave comprometida. |

### Compliance Requirements

| # | Requirement | Regulation/Contract |
|---|---|---|
| C1 | Atribuicao ao SEJA original e licenca CC BY-NC 4.0 preservadas em toda distribuicao; nome usado conforme `TRADEMARKS.md`. | Licenca e marca. |
| C2 | Nenhum nome de parceiro, instituicao conveniada ou pessoa nos artefatos de `_output/` e de `product-design/`; dados de instancias ficam nos repositorios das instancias. | Confidencialidade de convenios; o open-seja e visivel a organizacao e tende ao publico. |
| C3 | `main` so recebe o que o `tools/publish-manifest.txt` inclui (sem `_output/**`, sem `conventions.md` do proprio open-seja). | Separar distribuicao de desenvolvimento. |

---

## Parte C -- standards.md (notas; o questionario preenche o resto)

- **Stack**: harness em Markdown (skills, agentes, referencias) + scripts Python 3.11+ em `.claude/skills/scripts/` usando so biblioteca padrao (tomli abaixo de 3.11); testes em `.claude/skills/scripts/tests/` com pytest; `ruff` para lint. Sem backend web, sem frontend.
- **Scripts de verificacao**: `check_*.py` registrados em `check_plugin_registry.json`; saida legivel em stdout, diagnostico em stderr, `--json` com `schema_version`; exit 0 sem erro, 1 com erro, 2 uso incorreto; deterministicos (mesma entrada, mesma saida, sem relogio); sem LLM e sem rede.
- **Template de portao**: `template/quality-gate/<stack>/` com o mesmo JSON e os mesmos codigos de saida (0 PASS; 2 lint/tipos; 3 testes; 4 CRAP; 5 arquitetura; 6 mutacao); Python e o primeiro adaptador.
- **Skills**: `SKILL.md` com frontmatter (`metadata.references`, `context_budget`), quickguide irmao, concisao em instrucoes para agente, prosa humana nao comprimida.
- **Convencoes de artefato**: cabecalho com ID, prefixo-escopo, data UTC, titulo; `source:`/`spawned:`; UTF-8 sem BOM; sem travessao tipografico nem aspas curvas; nomes de arquivo em minusculas.
- **Idioma**: codigo e identificadores em en-US; `docs/` em en-US; sessoes de design em pt-BR (Q-005).
- **Testes**: cada regra de verificador tem um caso que a dispara e um negativo; fixtures escritas antes do codigo; ferramentas externas (ruff, pyright, mutmut) stubadas nos testes do harness.

---

## O que este rascunho nao decide (fica para a sessao)

1. **Q-006**: semear ao lado (assumido aqui) ou fundir.
2. **D-001 e D-002**: ficam na fundamentacao ou migram.
3. **Q-005**: idioma da fundamentacao.
4. Se D-003 (presets) entra agora ou espera o roadmap dos presets.
5. Valores exatos da secao 10 (conferir `conventions.md` e `gate.py`).
