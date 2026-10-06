# O que é o SEJA

> Apresentação do estado atual da fundamentação (parte 1) em `product-design/product-design-as-intended.md` § 3.
> Este documento **não decide nada**: ele expõe o que já está codificado como
> intenção, e mantém visível a diferença entre o que é princípio, o que é
> hipótese e o que ainda é pergunta.
>
> Última sincronização com a fonte: 2026-08-27.

---

## A tese

O SEJA não é um gerenciador de tarefas para agentes, nem uma camada de processo sobre o
Claude Code. Ele é uma **aposta teórica**: a de que desenvolvimento de software assistido
por IA é um problema de **comunicação projetada**, e que os métodos da engenharia
semiótica -- construídos para a interação humano-computador -- se transferem para a
interação humano-agente-código com poder explicativo intacto.

Quem lê o SEJA de fora tende a ver uma coleção de convenções arbitrárias. Quem lê a
partir da tese vê um sistema de signos desenhado. Tudo o mais no harness -- o sistema de
marcadores, o ciclo de vida das skills, o catálogo de agentes -- é consequência dela, e
não o contrário.

---

## Como ler este documento

O artefato distingue três estados epistêmicos, e a distinção é substantiva, não
decorativa. Confundi-los é o principal risco de leitura.

| Estado | Marca | O que significa |
|---|---|---|
| **Princípio** | `P-NNN` | Leitura assentada. Sustenta decisões de projeto hoje. |
| **Hipótese** | `H-NNN` | Leitura provisória, no registro abdutivo. Carrega o que a confirmaria e o que a refutaria. **Não é decisão tomada.** |
| **Questão** | `Q-NNN` | Em aberto. Algumas estão abertas por dependência, não por omissão. |

Estado atual: **8 princípios, 4 hipóteses, 10 questões abertas.**

A postura é a que o próprio SEJA declara em `docs/foundations.md`: abdução peirciana --
observar um fato surpreendente, levantar a hipótese que o explicaria se verdadeira, e
sustentá-la provisoriamente até que evidência melhor chegue. As hipóteses aqui são
numeradas e carregam condições de refutação porque esse é o modo de raciocínio que o
harness declara adotar, aplicado a si mesmo.

---

# 1. Princípios da engenharia semiótica

## 1.1 Conceitos fundamentais

### P-001 -- O artefato é uma mensagem, não um produto

A premissa central da engenharia semiótica (de Souza 2005) é que interação
humano-computador é um caso particular de **comunicação humana mediada por computador**.
A interface não é onde o usuário opera a máquina; é onde o designer fala com o usuário
através de um substituto que fala em seu nome no momento do uso.

De Souza chama esse substituto de **preposto do designer** (*designer's deputy*). O
preposto não é o sistema: é a voz do designer atravessando o sistema, num momento em que
o designer não está na sala. Cada rótulo, cada mensagem de erro, cada valor-padrão é uma
fala do preposto.

Quando o usuário não sabe o que fazer, o preposto tropeçou no texto. Isso é uma **quebra
de comunicação** -- e é diagnosticável como quebras de comunicação são diagnosticáveis.

> Consequência para o SEJA: cada artefato que o harness ajuda a produzir é andaime para
> essa comunicação. Não é sobrecarga de gestão. É um modo de ser mais deliberado sobre a
> mensagem que se está entregando.

### P-002 -- A relação dev↔código passou a ser mediada por um agente que produz código

No desenho clássico da atividade de desenvolvimento, o desenvolvedor age sobre o código
*apoiado por ferramentas*: editor, compilador, depurador, testes. A ferramenta amplia o
alcance do dev, mas não fala por ele.

O arranjo atual desloca isso:

```
  [ dev ] ──fala──> [ robô ] ──produz──> [ código ]
                        │
                        └──apoiado por──> [ ferramentas ]
```

Três mudanças, todas com consequência semiótica:

1. **O dev fala.** A entrada primária deixa de ser edição direta e passa a ser linguagem
   natural -- isto é, passa a ser *mensagem*, com toda a ambiguidade, pressuposto e
   implicatura que mensagens carregam.
2. **O robô produz.** O código deixa de ser autoria direta do humano e passa a ser um
   artefato *interpretado a partir de uma intenção*. Alguém traduziu, e **a tradução pode
   estar errada sem estar quebrada**.
3. **As ferramentas apoiam o robô, não o humano.** O compilador, os testes e o linter
   passam a ser instrumentos do preposto, não do designer.

O ponto teórico: o preposto **deixou de ser estático**. No modelo de 2005 ele é código
escrito de antemão que repete um script fixo em tempo de uso. Aqui ele *compõe a fala no
momento do uso*. Isso não invalida a teoria -- amplia a superfície em que ela morde.

A extensão da engenharia semiótica ao pipeline de desenvolvimento já havia sido feita em
SigniFYI (de Souza et al. 2016, *Software Developers as Users*). O acréscimo é que o
desenvolvedor agora tem um **preposto próprio, generativo**, entre ele e o artefato.

### P-002a -- Duas vias de autoria escrevem no mesmo artefato

O esquema linear acima é o caminho *novo*, não o único. O robô **não substituiu** o time
na produção de código: somou-se a ele. O arranjo real é de duas vias concorrentes de
autoria sobre o mesmo artefato.

Isso levanta uma pergunta semiótica que o esquema linear esconde: **quando dois prepostos
escrevem no mesmo texto, de quem é a voz que o leitor está lendo?**

### H-001 -- A escala citizen dev ↔ power dev

> **Hipótese.** Existe uma escala contínua de desenvolvedores, ancorada em literacia de
> código, e o harness precisa se adequar à posição do humano que assiste.

Se o robô produz código a partir de uma intenção, a pergunta seguinte é: **o humano
consegue ler o que voltou?** A resposta divide a população de usuários em algo que não é
uma categoria, mas um contínuo.

| Polo | Quem é | Relação com o código | O que espera do robô |
|---|---|---|---|
| **User / citizen dev** | Tem intenção e domínio do problema; não lê código | O código é opaco -- não é signo legível para ele | Que a computabilidade do robô **traduza de volta** o código implementado para uma linguagem adequada a ele |
| *...contínuo...* | | | |
| **Power dev** | Especialista em tecnologia | O código é o sistema de signos primário; lê fluentemente | Que o robô acelere, não que traduza; quer controle, rastreabilidade e governança |

A consequência de projeto vale enunciar sozinha:

> **Para o citizen dev, o código não pode ser a mensagem.**
> Se o receptor não decodifica o sistema de signos em que o artefato está expresso,
> entregar o artefato não é comunicar. O preposto tem obrigação de emitir a mensagem num
> registro que o receptor decodifique -- e essa obrigação é *constitutiva*, não um
> recurso de conveniência.

Em vocabulário da engenharia semiótica: para o power dev, o código funciona como signo
**estático**, legível diretamente; para o citizen dev, o código só chega através de signos
**metalinguísticos**, que falam *sobre* ele. A responsabilidade do harness por produzir
esses signos cresce à medida que se desce a escala.

**Um terceiro eixo.** O harness já estratifica audiência de duas maneiras: **famílias de
papel** (BLD Builders / SHP Shapers / GRD Guardians), por *função*; e **níveis de
expertise** (L1 / L2 / L3), por *senioridade dentro da função*.

A escala de `H-001` não é nenhuma das duas. Ela classifica por **literacia de código**, e
cruza as outras: existe SHP sênior que não lê código, e existe BLD júnior que lê. A
leitura corrente é que se trata de um terceiro eixo, ortogonal -- e que ele é o único dos
três que determina *em que sistema de signos a mensagem de volta pode ser escrita*. Isso
o torna o mais consequente dos três para efeito de comunicação, ainda que o menos
representado no harness hoje.

*Em aberto (`Q-002`)*: se o eixo é de fato ortogonal ou colapsa parcialmente nos outros;
e quantos pontos discretos precisa para ser operacional -- um contínuo não é
implementável, e dois polos provavelmente são grosseiros demais.

### P-003 -- O SEJA tem um caminho de retorno, e ele é parte da mensagem

O template de metacomunicação (de Souza 2005) é uma fala em primeira pessoa do designer
ao usuário: *"Eis meu entendimento de quem você é, eis o que aprendi que você quer, eis o
sistema que construí para você, eis como você pode ou deve usá-lo."* Barbosa et al. (2021)
o estenderam no **EMT**, com quatro dimensões de ciclo de vida e questões éticas
explícitas.

Sob `P-002` e `H-001`, esse template ganha um segundo trajeto. Não basta o humano
declarar intenção ao robô; o robô precisa **devolver ao humano uma declaração do que
entendeu e do que construiu**, no registro que o humano decodifica:

```
    intenção  ──────────────────>  código executável
   (humano)      tradução do robô      (artefato)
       ^                                   │
       └───────── retradução ──────────────┘
              (signos metalinguísticos)
```

A retradução é o que permite ao citizen dev **exercer autoria sem ler código**. Sem ela,
ele não tem como verificar se o artefato corresponde à sua intenção, e a relação vira
**delegação cega** -- exatamente o oposto do que a engenharia semiótica considera
comunicação bem-sucedida.

Parte dessa mão de volta já existe no harness (`/explain`, `/communicate`, `/document`),
mas hoje ela é **eletiva**: o usuário precisa pedir. A intenção registrada é que, para
posições baixas da escala, a retradução deixe de ser eletiva.

### P-004 -- As convenções do SEJA são um sistema de significação projetado, não estilo

De Souza, a partir de Peirce e Eco, classifica signos de interface em três classes:

- **Estáticos** -- lidos num único instante: um rótulo, um leiaute, um ícone.
- **Dinâmicos** -- emergem da interação: uma transição de estado, uma confirmação.
- **Metalinguísticos** -- explicam os outros dois: ajuda, mensagens de erro, tooltips.

E, de Eco (1976), a distinção entre **sistema de significação** -- o repertório
socialmente convencionado de pares expressão-conteúdo disponível a um grupo -- e
**processo de comunicação** -- o que alguém faz ao montar uma mensagem intencional a
partir desse repertório. O vão entre os dois é onde mora a invenção.

O sistema de marcadores do SEJA (`STATUS`, `ESTABLISHED`, `CHANGELOG_APPEND`, e os oito
`REQ-TYPE-NNN`) é um sistema de significação nesse sentido exato: um vocabulário pequeno
e convencionado para eventos de ciclo de vida, com **forma fixa** (`apply_marker.py` a
impõe) e **lugar fixo** (`check_human_markers_only.py` rejeita escrita fora do padrão).
Ele existe para que designer e agente possam falar sobre movimento de intenção sem
nenhum dos dois ter que reescrever prosa.

As quatro classificações de arquivo -- `Human`, `Human (markers)`, `Agent`,
`Human / Agent` -- são o mesmo mecanismo aplicado à **autoria**: dizem de quem é a voz em
cada arquivo do repositório, e impedem que as vozes se misturem.

### H-002 -- Computabilidade da intenção

> **Hipótese.** O SEJA pode ser um bom instrumento para embasar a computabilidade dos
> agentes na medida em que eles transformam intenções em código executável.

A afirmação por trás: **intenção só é computável quando é signo.** Uma intenção dita em
prosa livre não é operável por um agente -- não há como verificar se foi atendida, nem
detectar quando deixou de ser.

A aposta é que três propriedades, juntas, tornam intenção computável:

1. **Expressão em sistema de signos fixo** -- a intenção mora num documento de estrutura
   conhecida, com IDs estáveis que um programa consegue endereçar.
2. **Rastreabilidade até o código** -- passos de plano declaram quais requisitos
   satisfazem, e `check_plan_coverage.py` verifica que nada foi silenciosamente pulado.
   A intenção deixa de ser preâmbulo e passa a ser **contrato verificável**.
3. **Deriva como cidadã de primeira classe** -- o par as-intended / as-coded, com
   `/explain drift`, faz do descolamento entre intenção e implementação algo *detectável
   e reconciliável*, em vez de algo que simplesmente acontece.

Se a hipótese se sustenta, o SEJA não é apenas um harness para o dev: é o **substrato
sobre o qual um agente consegue raciocinar sobre intenção** -- e, por consequência,
consegue produzir a retradução de `P-003` com fundamento, porque sabe *a que intenção*
cada trecho de código responde.

**O que a confirmaria**: agentes respondendo "esta mudança atende a qual intenção
declarada?" e "o que na intenção ainda não tem código?" sem inspeção humana.
**O que a refutaria**: a rastreabilidade se degradando a ponto de os marcadores virarem
ritual -- a crítica de Eraut (1994) que `docs/foundations.md` já registra contra os
andaimes de reflexão.

---

## 1.2 Fluxos de trabalho

### P-005 -- Validar antes de comunicar

O SEJA roda um único ciclo canônico em torno de qualquer engajamento:

```
/research (ou /explain) > /design | /plan > /implement > /critique > /document | /communicate > /reflect
```

Leia `|` como "escolha um, conforme a intenção" e `>` como "e então".

| Etapa | Skills | Propósito |
|---|---|---|
| **Investigar** | `/research` ou `/explain` | fazer uma pergunta, ou entender como algo funciona |
| **Dar forma** | `/design` ou `/plan` | mudar a intenção, ou comprometer-se com uma construção |
| **Construir** | `/implement` | executar um plano aprovado |
| **Validar** | `/critique` | portão de qualidade antes que qualquer coisa voltada ao leitor saia |
| **Comunicar** | `/document` ou `/communicate` | artefatos para leitor, **somente após validação** |
| **Fechar o ciclo** | `/reflect` | registrar o que o turno ensinou antes do próximo começar |

O invariante que dá nome ao princípio é o **único portão rígido** do harness: `/critique`
sempre precede `/document` e `/communicate`. Nada sai do envelope sem ter sido validado.

Isso é uma posição semiótica, não de processo: **uma mensagem entregue sem validação é o
preposto falando sem saber se o que diz é verdade.**

A entrada natural é `/research` ou `/explain`. A saída dessa investigação flui para
`/design` se a *intenção* precisa mudar, ou para `/plan` se a intenção está assentada e o
que falta é construir. A única exceção é a primeira iteração de um projeto novo, em que
`/seja-setup` instala o harness e entrega a `/design`.

### O par as-intended / as-coded

O harness mantém dois documentos em tensão deliberada:

| Documento | O que registra | Voz |
|---|---|---|
| `product-design-as-intended.md` | o que se **pretende** | humana; agentes só marcam |
| `product-design-as-coded.md` | o que **existe** | do agente; reconstruído após implementação |

Estados de ciclo de vida: `proposed -> implemented -> established -> superseded`.

A distância entre os dois é a **deriva**, e `/explain drift` é o fluxo que a reconcilia.
Manter os arquivos separados é uma escolha: fundir intenção e implementação num documento
só apaga precisamente a informação mais valiosa -- **o que ainda não é**.

### H-003 -- Os fluxos variam ao longo da escala

> **Hipótese**, decorrente de `H-001`. O caminho canônico é o mesmo, mas a superfície de
> contato e a obrigatoriedade da retradução variam com a posição do humano na escala.

| | **Citizen / user dev** | **Power dev** |
|---|---|---|
| Superfície primária | `/design`, `/explain`, `/communicate` | `/plan`, `/implement`, `/critique` |
| `/plan` e `/implement` | rodam com mais autonomia; o plano é resumido em prosa de intenção, não em passos técnicos | são o objeto central; o plano é revisado passo a passo |
| Retradução (`P-003`) | **obrigatória** -- é como ele verifica o resultado | eletiva; o código já é legível |
| Papel do `/critique` | prova de que a intenção foi atendida | prova de qualidade técnica e conformidade |
| Papel dos marcadores | invisíveis; o valor é a rastreabilidade automática | ferramenta de governança usada diretamente |
| Risco dominante | **delegação cega** -- aceitar o que não se consegue verificar | **ritual** -- produzir a forma do processo sem o conteúdo |

O ciclo não se bifurca. O que muda é **onde o humano toca nele** e **em que registro o
preposto fala de volta**. Essa é a formulação concreta de "o harness e seus agentes
precisam se adequar ao dev que estão assistindo".

*Em aberto (`Q-003`)*: como o harness detecta a posição do humano na escala. A questão
está **sustentada em aberto por decisão**, não por omissão -- ela depende de `Q-002`, a
granularidade da escala, que precede. Enquanto `Q-002` não fechar, `H-003` permanece como
leitura, sem implementação.

### Os três registros de reflexão

O SEJA carrega os três registros de Schön (1983) como andaimes concretos, deliberadamente
mínimos para que a encenação não compense o esforço:

- **Reflexão-na-ação** -- a justificativa curta que acompanha cada opção em toda
  `AskUserQuestion`. Transforma uma bifurcação silenciosa numa deliberação visível.
- **Reflexão-sobre-a-ação** -- a nota breve ao fim de `/implement`, `/plan`, `/design` e
  `/document`: o que de fato aconteceu, o que desviou do plano, sobre o que se está menos
  seguro agora do que no início.
- **Reflexão-sobre-a-prática** -- a skill `/reflect`, que ancora numa escolha de
  artefatos, pergunta se a lente é o **produto** ou a **prática**, e registra as palavras
  do designer **literalmente**, sem prescrever mudança.

O par natural de Schön aqui é a **abdução** de Peirce, e é por isso que as hipóteses
deste documento carregam condições de refutação: é o modo de raciocínio que o SEJA
declara adotar, aplicado a si mesmo.

---

## 1.3 Agentes principais

### P-006 -- A skill é o orquestrador; o agente é a responsabilidade única

| | **Skill** | **Agente** |
|---|---|---|
| Onde vive | `.claude/skills/<nome>/SKILL.md` | `.claude/agents/<nome>.md` |
| Como é chamado | por barra, pelo usuário (`/plan`) | pela skill; **nunca** diretamente |
| O que faz | conduz a conversa, segura o estado do ciclo de vida, faz as perguntas, **decide quais agentes compor** | executa **um papel sobre um tipo de artefato** |
| Contexto | o da conversa | janela isolada, ferramentas definidas |
| Devolve | a interação | artefato estruturado |

Duas skills internas -- `pre-skill` e `post-skill` -- envolvem toda invocação de skill de
usuário. São elas que fazem os andaimes de reflexão acontecerem de forma consistente e
auditável, em vez de dependerem de disciplina.

### P-007 -- Todo agente é avaliador, gerador ou executor

**Avaliadores** revisam artefatos sob uma lente de qualidade e devolvem achados
estruturados:

| Agente | Papel |
|---|---|
| `code-reviewer` | revisa diffs contra 16 perspectivas de engenharia e design, com profundidade graduada |
| `plan-reviewer` | revisa um plano em processo de duas fases graduado por complexidade |
| `research-reviewer` | avalia decisões de design, questões abertas e trade-offs |
| `council-debate` | debate estruturado entre cinco arquétipos fixos mais 0-2 especialistas do tema |
| `semiotic-inspector` | avaliação SIM da comunicabilidade nas três classes de signo |
| `harness-health-evaluator` | 9 checagens de autodiagnóstico do harness |
| `standards-checker` | agrega os scripts de validação num relatório de conformidade |
| `test-runner` | roda as suítes e classifica falhas com contexto |
| `migration-validator` | valida integridade de cadeia de migrações |

**Geradores** produzem artefatos autocontidos a partir de entradas bem definidas:

| Agente | Papel |
|---|---|
| `explanation-generator` | explicações de comportamento, código e modelo de dados |
| `architecture-explainer` | estrutura do sistema, fronteiras, decisões-chave |
| `evolution-explainer` | como uma funcionalidade chegou ao estado atual |
| `document-generator` | documentação por tipo (readme, api-reference, ddr, changelog, ...) |
| `communication-generator` | material para um segmento de audiência (EVL, CLT, USR, ACD) |
| `onboarding-generator` | plano de integração por família de papel e nível |
| `test-plan-generator` | plano de teste manual estruturado |

**Executores** não estão catalogados: são construídos **dinamicamente** pelo modo
automático de `/implement`, a partir dos metadados dos passos do plano. São a ponta que
efetivamente transforma intenção em código.

O `council-debate` merece nota: ele é a operacionalização explícita da abdução. Vários
especialistas rodam leituras abdutivas concorrentes sobre a mesma questão, postos em
desacordo estruturado, para que a síntese entregue carregue as **contra-leituras
visíveis**. A intenção é não fingir que uma recomendação é a única plausível.

### H-004 -- O orquestrador que compõe

> **Hipótese.** O agente de workflow possui um orquestrador capaz de chamar diversos
> agentes e compor o que for necessário para que o agente de IA-dev assista o humano no
> desenvolvimento de software.

Nenhum agente isolado assiste o desenvolvedor. O que assiste é a **composição** -- e o
orquestrador é quem a decide. Uma passagem por `/critique` pode compor
`standards-checker`, `test-runner`, `code-reviewer` e `semiotic-inspector`; uma passagem
por `/research --deep` compõe `research-reviewer` e `council-debate`.

A consequência de projeto, e a razão pela qual esta hipótese fecha a seção: **o
orquestrador é o lugar onde a adequação ao dev se realiza.** Se a composição é decidida
em tempo de execução, então a posição do humano na escala `H-001` é uma **entrada legítima
da decisão de composição** -- e não uma bifurcação que precisaria ser costurada em cada
skill separadamente.

> O orquestrador é o preposto. Os agentes são o vocabulário de que ele dispõe. A mensagem
> é o que ele monta com eles, para este humano, neste turno.

**O que a confirmaria**: composições visivelmente diferentes para a mesma solicitação
vinda de pontos diferentes da escala, com retradução automática no polo citizen.
**O que a refutaria**: a adequação exigindo bifurcação dentro de cada skill, o que
indicaria que o orquestrador não é o ponto de variação certo.

---

## Os desenhos de origem

A seção 1 é o preenchimento de uma caixa que o desenho já tinha reservado: o painel
`Harness` da Figura 2 contém `Docs (O que é o SEJA)`, com exatamente estes três itens --
conceitos fundamentais, fluxos de trabalho, agentes principais.

Convenção de leitura, tirada do próprio traço: **branco = arranjo herdado, vermelho =
acrescentado na sessão de 2026-08-26.**

### Figura 1 -- Design do software project

`docs/design-software-project.png`

Tudo contido numa caixa rotulada **"Projeto"**: a unidade de análise é o projeto, não a
sessão nem o turno. O robô ao centro, circulado em vermelho. Duas setas entrando no
`</>`. O `LN` (linguagem natural) como artefato nomeado entre o citizen dev e o robô,
com tráfego nos dois sentidos. A caixa `Convenções / Design / Intenção` alimentada por
uma seta vermelha grossa que **atravessa a fronteira da caixa "Projeto"** -- o harness
incide de fora. E uma linha vermelha horizontal na base, correndo **sob a população
inteira de desenvolvedores**: a escala não está anexada a um indivíduo.

### Figura 2 -- Design do harness

`docs/designt-harnerss.png`

Dois painéis. À esquerda, `User Dev | Power Dev` como **cabeçalho sobre** o `Agent WF`,
não conteúdo dele -- os polos são *entrada* do agente de workflow. À direita, o painel
`Harness` com a caixa `Docs (O que é o SEJA)`, e abaixo uma seta apontando para `LLM`.

A pilha desenhada é **`Docs → Harness → LLM`**: o harness é a camada que faz o documento
chegar ao modelo. É a leitura mais literal possível de `H-002` -- a intenção vira
computável porque existe uma camada que a entrega ao modelo em forma operável.

---

## O que ainda não está resolvido

Dez questões seguem abertas. Duas travam trabalho real.

| ID | Questão | Estado |
|---|---|---|
| `Q-002` | A escala é ortogonal a BLD/SHP/GRD e L1-L3? Quantos pontos discretos precisa? | **Bloqueia** a operacionalização de `H-001` e `H-003` |
| `Q-008` | O `Agent WF` desenhado lista um ciclo reduzido, sem `/critique` -- o portão de `P-005` | **Bloqueia**; divergência entre desenho e princípio |
| `Q-001` | Referência bibliográfica exata do artigo de Abrahão | Citação de `P-002` pendente |
| `Q-007` | Duas vias de autoria no mesmo `</>`: o harness precisa distinguir as vozes? | Decorre de `P-002a` |
| `Q-009` | "Orquestrador" aparece duas vezes na Figura 2 -- dois níveis, ou ênfase? | Precisão de `H-004` |
| `Q-010` | Elemento não identificado no alto à esquerda da Figura 1 | Leitura do desenho |
| `Q-004` | A retradução obrigatória é novo artefato, novo modo de `/explain`, ou etapa do `post-skill`? | Implementação de `P-003` |
| `Q-005` | Idioma do documento: pt-BR ou en-US junto com `docs/` | Publicação |
| `Q-006` | Relação com o `product-design-as-intended.md` no formato §0-§17 | Estrutura |
| `Q-003` | Como o harness detecta a posição do humano na escala? | **Sustentada em aberto por decisão** -- depende de `Q-002` |

---

## Referências

- **de Souza, C.S.** (2005). *The Semiotic Engineering of Human-Computer Interaction*.
  MIT Press. Template de metacomunicação, classes de signo, preposto do designer,
  comunicabilidade.
- **de Souza, C.S. e Leitão, C.F.** (2009). *Semiotic Engineering Methods for Scientific
  Research in HCI*. Morgan & Claypool. Tratamento metodológico de SIM e CEM.
- **de Souza, C.S. et al.** (2016). *Software Developers as Users: Semiotic Investigations
  in Human-Centered Software Development* (SigniFYI). Springer. Extensão ao pipeline
  voltado ao desenvolvedor -- base direta de `P-002`.
- **Barbosa, S.D.J. et al.** (2021). "A Semiotics-based epistemic tool to reason about
  ethical issues in digital technology design and development." *Proc. FAccT '21*. O EMT.
- **Schön, D.A.** (1983). *The Reflective Practitioner*. Basic Books.
- **Eraut, M.** (1994). *Developing Professional Knowledge and Competence*. Falmer Press.
  Contra-leitura sobre os limites de andaimes de reflexão.
- **Eco, U.** (1976). *A Theory of Semiotics*. Sistema de significação vs. processo de
  comunicação.
- **Abrahão, ...** -- `Q-001`, a completar.

---

> Fonte: `product-design/product-design-as-intended.md` § 3, Fundamentação, parte 1. Este documento é derivado e deve ser
> regerado quando a fonte mudar. As notas de origem estão preservadas verbatim no
> `Apêndice A` da fonte; a leitura elemento a elemento dos desenhos, no `Apêndice B`.
