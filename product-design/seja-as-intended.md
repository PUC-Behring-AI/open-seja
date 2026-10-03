# SEJA -- DESIGN INTENT

<!-- maintained-by: human (designer) -->

> Documento de intenção do SEJA: o que o SEJA **é para ser**, antes e acima do que ele
> hoje **é**. Registra a fundamentação teórica, os fluxos e os agentes que a materializam.
>
> **Classificação**: `Human (markers)`. A prosa é de autoria humana. Agentes podem
> escrever marcadores `STATUS` sobre as seções e apensar linhas ao `## CHANGELOG`
> via `apply_marker.py`, após confirmação explícita no mesmo turno.
>
> **Postura epistêmica**: tudo aqui é leitura corrente e provisória, no registro
> abdutivo que o próprio SEJA adota (ver `docs/foundations.md`). Hipóteses são
> marcadas como tal (`H-NNN`) e carregam o que as confirmaria ou refutaria.
> Não confundir hipótese registrada com decisão tomada.
>
> **IDs estáveis**: princípios `P-NNN`, hipóteses `H-NNN`, questões abertas `Q-NNN`,
> decisões `D-NNN`.
>
> **Idioma**: pt-BR, língua de trabalho das sessões de design. A documentação pública
> em `docs/` é en-US; a tradução é preocupação posterior (ver `Q-005`).

---

## 1. Princípios da engenharia semiótica

O SEJA não é um gerenciador de tarefas para agentes, nem uma camada de processo sobre
o Claude Code. Ele é uma aposta teórica: a de que **desenvolvimento de software assistido
por IA é um problema de comunicação projetada**, e que os métodos da engenharia semiótica
-- construídos para a interação humano-computador -- se transferem para a interação
humano-agente-código com poder explicativo intacto.

Esta seção registra os princípios que sustentam essa aposta. Ela vem primeiro porque
todo o resto do harness (o sistema de marcadores, o ciclo de vida das skills, o catálogo
de agentes) é consequência dela, e não o contrário. Quem lê o SEJA de fora tende a ver
uma coleção de convenções arbitrárias; quem lê a partir daqui vê um sistema de signos
desenhado.

---

### 1.1 Conceitos fundamentais

#### 1.1.1 Software como comunicação projetada

<!-- P-001 -->
**P-001 -- O artefato é uma mensagem, não um produto.**

A premissa central da engenharia semiótica (de Souza 2005, cap. 1 e 3) é que interação
humano-computador é um caso particular de comunicação humana mediada por computador. A
interface não é onde o usuário opera a máquina; é onde o **designer fala com o usuário**
através de um substituto que fala em seu nome no momento do uso.

De Souza chama esse substituto de **preposto do designer** (*designer's deputy*). O
preposto não é o sistema: é a voz do designer atravessando o sistema, num momento em que
o designer não está na sala. Cada rótulo, cada mensagem de erro, cada valor-padrão é uma
fala do preposto. Quando o usuário não sabe o que fazer, o preposto tropeçou no texto --
e isso é uma **quebra de comunicação**, diagnosticável como quebras de comunicação são
diagnosticáveis.

A consequência para o SEJA é direta: cada artefato que o harness ajuda a produzir
(`product-design-as-intended.md`, os marcadores, os planos, os relatórios) é andaime
para essa comunicação. Não é sobrecarga de gestão. É um modo de ser mais deliberado
sobre a mensagem que se está entregando.

#### 1.1.2 O terceiro interlocutor: o robô entra na cena

<!-- P-002 -->
**P-002 -- A relação dev↔código passou a ser mediada por um agente que produz código.**

Partimos do desenho clássico da atividade de desenvolvimento (artigo de Abrahão --
ver `Q-001`, referência a completar), em que o desenvolvedor age sobre o código
*apoiado por ferramentas*: editor, compilador, depurador, testes. A ferramenta amplia
o alcance do dev, mas não fala por ele.

O desenho que estamos propondo desloca esse arranjo. Hoje temos:

```
  [ dev ] ──fala──> [ robô ] ──produz──> [ código ]
                        │
                        └──apoiado por──> [ ferramentas ]
```

![Design do software project](../docs/design-software-project.png)

> **Figura 1 -- Design do software project** (desenho de origem, sessão com o Anax,
> 2026-08-26). Leitura elemento a elemento no `Apêndice B`.

<!-- P-002a -->
**Ressalva que o desenho impõe (`P-002a`).** A Figura 1 mostra **duas setas entrando no
`</>`**: uma vinda do robô e outra vinda do lado humano. Isto é, o robô **não substituiu**
o time na produção de código -- ele se somou a ele. O esquema linear acima
(`dev → robô → código`) é o caminho *novo*, não o único. O arranjo real é de **duas vias
concorrentes de autoria sobre o mesmo artefato**, e isso levanta uma pergunta semiótica
que o esquema linear esconde: quando dois prepostos escrevem no mesmo texto, de quem é
a voz que o leitor está lendo? Ver `Q-007`.

Três mudanças, todas com consequência semiótica:

1. **O dev fala.** A entrada primária deixa de ser edição direta e passa a ser
   linguagem natural -- isto é, passa a ser *mensagem*, com toda a ambiguidade,
   pressuposto e implicatura que mensagens carregam.
2. **O robô produz.** O código deixa de ser autoria direta do humano e passa a ser
   um artefato *interpretado a partir de uma intenção*. Alguém traduziu, e a tradução
   pode estar errada sem estar quebrada.
3. **As ferramentas apoiam o robô, não o humano.** O compilador, os testes e o
   linter passam a ser instrumentos do preposto, não do designer.

O ponto teórico é que o preposto do designer **deixou de ser estático**. No modelo de
2005, o preposto é código escrito de antemão que repete um script fixo em tempo de uso.
Aqui o preposto *compõe a fala no momento do uso*. Isso não invalida a teoria -- amplia
a superfície em que ela morde. A extensão da engenharia semiótica ao pipeline de
desenvolvimento já havia sido feita em SigniFYI (de Souza et al. 2016, *Software
Developers as Users*); o que acrescentamos é que o desenvolvedor agora tem um preposto
próprio, generativo, entre ele e o artefato.

#### 1.1.3 O receptor não é único: a escala citizen dev ↔ power dev

<!-- H-001 -->
**H-001 (hipótese) -- Existe uma escala contínua de desenvolvedores, ancorada em
literacia de código, e o harness precisa se adequar à posição do humano que assiste.**

Se o robô produz código a partir de uma intenção, a pergunta seguinte é: **o humano
consegue ler o que voltou?** A resposta divide a população de usuários em algo que não
é uma categoria, mas um contínuo:

| Polo | Quem é | Relação com o código | O que espera do robô |
|---|---|---|---|
| **User / citizen dev** | Tem intenção e domínio do problema; não lê código | O código é opaco -- não é signo legível para ele | Que a computabilidade do robô produza algo que **traduza de volta** o código implementado para uma linguagem adequada a ele |
| ... contínuo ... | | | |
| **Power dev** | Especialista em tecnologia | O código é o sistema de signos primário; lê fluentemente | Que o robô acelere, não que traduza; quer controle, rastreabilidade e governança |

A consequência de projeto é forte e vale enunciar sozinha:

> **Para o citizen dev, o código não pode ser a mensagem.**
> Se o receptor não decodifica o sistema de signos em que o artefato está expresso,
> entregar o artefato não é comunicar. O preposto tem obrigação de emitir a mensagem
> num registro que o receptor decodifique -- e essa obrigação é *constitutiva*,
> não um recurso de conveniência.

Em vocabulário da engenharia semiótica: para o power dev, o código funciona como signo
**estático** legível diretamente; para o citizen dev, o código só chega através de signos
**metalinguísticos** que falam *sobre* ele. O harness é responsável por produzir esses
signos metalinguísticos, e essa responsabilidade cresce à medida que se desce a escala.

<!-- Q-002 -->
**Relação com os eixos que o SEJA já tem (`Q-002`, aberta).** O harness já estratifica
audiência de duas maneiras: **famílias de papel** (BLD Builders / SHP Shapers /
GRD Guardians), que classificam por *função*, e **níveis de expertise** (L1 Contributor /
L2 Expert / L3 Leader), que classificam por *senioridade dentro da função*.

A escala de H-001 **não é nenhuma das duas**. Ela classifica por *literacia de código*,
e cruza as outras: existe SHP sênior (L3) que não lê código, e existe BLD júnior (L1)
que lê. Nossa leitura corrente é que se trata de um **terceiro eixo, ortogonal**, e que
ele é o único dos três que determina *em que sistema de signos a mensagem de volta pode
ser escrita*. Isso o torna o eixo mais consequente dos três para efeito de comunicação,
ainda que o menos representado no harness hoje.

Fica aberto: (a) se o eixo é de fato ortogonal ou se colapsa parcialmente em BLD/SHP/GRD;
(b) quantos pontos discretos a escala precisa ter para ser operacional -- um contínuo não
é implementável, e dois polos provavelmente são grosseiros demais.

#### 1.1.4 A mão de volta: metacomunicação em dois sentidos

<!-- P-003 -->
**P-003 -- O SEJA tem um caminho de retorno, e ele é parte da mensagem.**

O template de metacomunicação (de Souza 2005, cap. 1 p.25 e cap. 3 p.84) é uma fala em
primeira pessoa do designer ao usuário: *"Eis meu entendimento de quem você é, eis o que
aprendi que você quer, eis o sistema que construí para você, eis como você pode ou deve
usá-lo."* Barbosa et al. (2021) o estenderam no **EMT** com quatro dimensões de ciclo de
vida e questões éticas explícitas.

Sob P-002 e H-001, esse template ganha um segundo trajeto. Não basta o humano declarar
intenção ao robô; o robô precisa **devolver ao humano uma declaração do que entendeu e
do que construiu**, no registro que o humano decodifica:

```
    intenção  ──────────────────>  código executável
   (humano)      tradução do robô      (artefato)
       ^                                   │
       └───────── retradução ──────────────┘
              (signos metalinguísticos)
```

A retradução é o que permite ao citizen dev **exercer autoria sem ler código**. Sem ela,
ele não tem como verificar se o artefato corresponde à sua intenção, e a relação vira
delegação cega -- exatamente o oposto do que a engenharia semiótica considera
comunicação bem-sucedida.

Parte dessa mão de volta já existe no harness (`/explain`, `/communicate` com seus
segmentos de audiência, `/document`), mas hoje ela é **eletiva**: o usuário precisa
pedir. A intenção registrada aqui é que, para posições baixas da escala H-001, a
retradução deixe de ser eletiva.

#### 1.1.5 Sistemas de signos e o sistema de marcadores

<!-- P-004 -->
**P-004 -- As convenções do SEJA são um sistema de significação projetado, não estilo.**

De Souza, a partir de Peirce e Eco, classifica signos de interface em três classes
(de Souza 2005, cap. 4; de Souza e Leitão 2009, pp.19-20):

- **Estáticos** -- lidos num único instante: um rótulo, um leiaute, um ícone.
- **Dinâmicos** -- emergem da interação: uma transição de estado, uma confirmação.
- **Metalinguísticos** -- explicam os outros dois: ajuda, mensagens de erro, tooltips.

E, de Eco (1976), a distinção entre **sistema de significação** -- o repertório
socialmente convencionado de pares expressão-conteúdo disponível a um grupo -- e
**processo de comunicação** -- o que alguém faz ao montar uma mensagem intencional a
partir desse repertório. O vão entre os dois é onde mora a invenção.

O sistema de marcadores do SEJA (`STATUS`, `ESTABLISHED`, `CHANGELOG_APPEND`, e os
oito `REQ-TYPE-NNN`) é lido aqui como **sistema de significação projetado** nesse
sentido exato: um vocabulário pequeno e convencionado para eventos de ciclo de vida,
com forma fixa (`apply_marker.py` a impõe) e lugar fixo (`check_human_markers_only.py`
rejeita escrita fora do padrão). Ele existe para que designer e agente possam falar
sobre movimento de intenção sem nenhum dos dois ter que reescrever prosa.

As quatro classificações de arquivo -- `Human`, `Human (markers)`, `Agent`,
`Human / Agent` -- são o mesmo mecanismo aplicado à **autoria**: elas dizem de quem é
a voz em cada arquivo do repositório, e impedem que as vozes se misturem.

#### 1.1.6 Computabilidade da intenção

<!-- H-002 -->
**H-002 (hipótese) -- O SEJA pode ser um bom instrumento para embasar a computabilidade
dos agentes na medida em que eles transformam intenções em código executável.**

A afirmação por trás da hipótese é que **intenção só é computável quando é signo**. Uma
intenção dita em prosa livre não é operável por um agente: não há como verificar se foi
atendida, nem detectar quando deixou de ser. A aposta do SEJA é que três propriedades,
juntas, tornam intenção computável:

1. **Expressão em sistema de signos fixo** -- a intenção mora em
   `product-design-as-intended.md` sob estrutura conhecida, com IDs estáveis
   (`REQ-TYPE-NNN`, `D-NNN`) que um programa consegue endereçar.
2. **Rastreabilidade até o código** -- passos de plano declaram quais requisitos
   satisfazem, e `check_plan_coverage.py` verifica que nada foi silenciosamente pulado.
   A intenção deixa de ser preâmbulo e passa a ser contrato verificável.
3. **Deriva como cidadã de primeira classe** -- o par as-intended / as-coded, com
   `/explain drift`, faz do descolamento entre intenção e implementação algo
   *detectável e reconciliável*, em vez de algo que simplesmente acontece.

Se a hipótese se sustenta, o SEJA não é apenas um harness para o dev: é o **substrato
sobre o qual um agente consegue raciocinar sobre intenção** -- e, por consequência,
consegue produzir a retradução de P-003 com fundamento, porque sabe *a que intenção*
cada trecho de código responde.

O que a confirmaria: agentes conseguindo responder "esta mudança atende a qual intenção
declarada?" e "o que na intenção ainda não tem código?" sem inspeção humana. O que a
refutaria: a rastreabilidade se degradando na prática a ponto de os marcadores virarem
ritual -- exatamente a crítica de Eraut (1994) que `docs/foundations.md` já registra
contra os andaimes de reflexão.

---

### 1.2 Fluxos de trabalho

#### 1.2.1 O caminho canônico

<!-- P-005 -->
**P-005 -- Validar antes de comunicar.**

O SEJA roda um único ciclo canônico em torno de qualquer engajamento:

```
/research (ou /explain) > /design | /plan > /implement > /critique > /document | /communicate > /reflect
```

Leia `|` como "escolha um, conforme a intenção" e `>` como "e então".

| Etapa | Skills | Propósito |
|---|---|---|
| **Investigar** | `/research` ou `/explain` | fazer uma pergunta, ou entender como algo funciona |
| **Dar forma** | `/design` ou `/plan` | mudar a intenção (design) ou comprometer-se com uma construção (plan) |
| **Construir** | `/implement` | executar um plano aprovado |
| **Validar** | `/critique` | portão de qualidade antes que qualquer coisa voltada ao leitor saia |
| **Comunicar** | `/document` ou `/communicate` | artefatos para leitor, **somente após validação** |
| **Fechar o ciclo** | `/reflect` | registrar o que o turno ensinou antes do próximo começar |

O invariante que dá nome ao princípio é o único portão rígido: `/critique` sempre precede
`/document` e `/communicate`. Nada sai do envelope sem ter sido validado. Isso é uma
posição semiótica, não de processo: uma mensagem entregue sem validação é o preposto
falando sem saber se o que diz é verdade.

A entrada natural é `/research` ou `/explain` -- investigar o que se vai mudar. A saída
dessa investigação flui para `/design` se a **intenção** precisa mudar, ou para `/plan`
se a intenção está assentada e o que falta é construir. A única exceção é a primeira
iteração de um projeto novo, em que `/seja-setup` instala o harness e entrega a
`/design`.

#### 1.2.2 O par as-intended / as-coded e a deriva

O harness mantém dois documentos em tensão deliberada:

- **`product-design-as-intended.md`** -- o que se pretende. Voz humana, agentes só
  marcam. Estados de ciclo de vida: `proposed -> implemented -> established -> superseded`.
- **`product-design-as-coded.md`** -- o que existe. Voz do agente, reconstruído após
  implementação.

A distância entre os dois é a **deriva**, e `/explain drift` é o fluxo de alinhamento
que a reconcilia. Manter os dois arquivos separados é uma escolha: fundir intenção e
implementação num documento só apaga precisamente a informação mais valiosa -- *o que
ainda não é*.

#### 1.2.3 Os fluxos precisam variar ao longo da escala H-001

<!-- H-003 -->
**H-003 (hipótese, decorrente de H-001) -- O caminho canônico é o mesmo, mas a
superfície de contato e a obrigatoriedade da retradução variam com a posição do humano
na escala citizen↔power.**

Leitura corrente de como o ciclo se apresenta em cada polo:

| | **Citizen / user dev** | **Power dev** |
|---|---|---|
| Superfície primária | `/design`, `/explain`, `/communicate` | `/plan`, `/implement`, `/critique` |
| `/plan` e `/implement` | rodam com mais autonomia; o plano é resumido em prosa de intenção, não em passos técnicos | são o objeto central; o plano é revisado passo a passo |
| Retradução (P-003) | **obrigatória** -- é como ele verifica o resultado | eletiva; o código já é legível |
| Papel do `/critique` | prova de que a intenção foi atendida | prova de qualidade técnica e conformidade |
| Papel dos marcadores | invisíveis; o valor é a rastreabilidade automática | ferramenta de governança usada diretamente |
| Risco dominante | delegação cega -- aceitar o que não se consegue verificar | ritual -- produzir a forma do processo sem o conteúdo |

O ciclo não se bifurca. O que muda é **onde o humano toca nele** e **em que registro o
preposto fala de volta**. Essa é a formulação concreta de "o harness e seus agentes
precisam se adequar ao dev que estão assistindo".

#### 1.2.4 Os três registros de reflexão

O SEJA carrega os três registros de Schön (1983) como andaimes concretos, deliberadamente
mínimos para que a encenação não compense o esforço:

- **Reflexão-na-ação** -- a justificativa curta que acompanha cada opção em toda
  `AskUserQuestion`: transforma uma bifurcação silenciosa numa deliberação visível.
- **Reflexão-sobre-a-ação** -- a nota breve ao fim de `/implement`, `/plan`, `/design`
  e `/document`: o que de fato aconteceu, o que desviou do plano, sobre o que se está
  menos seguro agora do que no início.
- **Reflexão-sobre-a-prática** -- a skill `/reflect`, que ancora numa escolha de
  artefatos, pergunta se a lente é o **produto** ou a **prática**, e registra as
  palavras do designer **literalmente**, sem prescrever mudança.

O par natural de Schön aqui é a **abdução** de Peirce: observar um fato surpreendente,
levantar a hipótese que o explicaria se verdadeira, e sustentá-la provisoriamente até
que evidência melhor chegue. É por isso que as hipóteses deste documento são numeradas
e carregam condições de refutação -- é o modo de raciocínio que o SEJA declara adotar,
aplicado a si mesmo.

---

### 1.3 Agentes principais

#### 1.3.1 Skill orquestra, agente executa

<!-- P-006 -->
**P-006 -- A skill é o orquestrador; o agente é a responsabilidade única.**

A distinção estrutural do harness:

- Uma **skill** é um `SKILL.md` sob `.claude/skills/<nome>/`, invocada por barra
  (`/plan`). Ela conduz a conversa, segura o estado do ciclo de vida, faz as perguntas
  ao humano e **decide quais agentes compor**.
- Um **agente** é um prompt sob `.claude/agents/`, que executa **um papel sobre um tipo
  de artefato**, em janela de contexto isolada, com conjunto de ferramentas definido.
  Recebe entradas da skill que o chamou e devolve artefato estruturado. O usuário
  **nunca** invoca um agente diretamente.

Duas skills internas -- `pre-skill` e `post-skill` -- envolvem toda invocação de skill
de usuário. São elas que fazem os andaimes de reflexão de 1.2.4 acontecerem de forma
consistente e auditável, em vez de dependerem de disciplina.

#### 1.3.2 Os três papéis

<!-- P-007 -->
**P-007 -- Todo agente é avaliador, gerador ou executor.**

**Avaliadores** -- revisam artefatos sob uma lente de qualidade e devolvem achados
estruturados:

| Agente | Papel |
|---|---|
| `code-reviewer` | revisa diffs contra 16 perspectivas de engenharia e design, com profundidade graduada |
| `plan-reviewer` | revisa um plano em processo de duas fases graduado por complexidade |
| `research-reviewer` | avalia decisões de design, questões abertas e trade-offs |
| `council-debate` | debate estruturado entre cinco arquétipos fixos mais 0-2 especialistas do tema |
| `semiotic-inspector` | conduz avaliação SIM da comunicabilidade nas três classes de signo |
| `harness-health-evaluator` | roda 9 checagens de autodiagnóstico do harness |
| `standards-checker` | agrega todos os scripts de validação num relatório de conformidade |
| `test-runner` | roda as suítes e classifica falhas com contexto |
| `migration-validator` | valida integridade de cadeia de migrações |

**Geradores** -- produzem artefatos autocontidos a partir de entradas bem definidas:

| Agente | Papel |
|---|---|
| `explanation-generator` | explicações de comportamento, código e modelo de dados |
| `architecture-explainer` | estrutura do sistema, fronteiras, decisões-chave |
| `evolution-explainer` | como uma funcionalidade chegou ao estado atual, a partir do histórico de planos |
| `document-generator` | documentação por tipo (readme, api-reference, ddr, changelog, ...) |
| `communication-generator` | material para um segmento de audiência (EVL, CLT, USR, ACD) |
| `onboarding-generator` | plano de integração por família de papel e nível |
| `test-plan-generator` | plano de teste manual estruturado |

**Executores** -- não estão catalogados: são construídos **dinamicamente** pelo modo
automático de `/implement`, a partir dos metadados dos passos do plano. São a ponta que
efetivamente transforma intenção em código.

Vale notar que o `council-debate` é a operacionalização explícita da abdução: vários
especialistas rodando leituras abdutivas concorrentes sobre a mesma questão, postos em
desacordo estruturado, para que a síntese entregue carregue as contra-leituras visíveis.
A intenção é não fingir que uma recomendação é a única plausível.

#### 1.3.3 O orquestrador que compõe

![Design do harness](../docs/designt-harnerss.png)

> **Figura 2 -- Design do harness** (desenho de origem, sessão com o Anax, 2026-08-26).
> Leitura elemento a elemento no `Apêndice B`.

<!-- H-004 -->
**H-004 (hipótese) -- O agente de workflow possui um orquestrador capaz de chamar
diversos agentes e compor o que for necessário para que o agente de IA-dev assista o
humano no desenvolvimento de software.**

O desenho já responde parte da hipótese antes de a discutirmos: na Figura 2, **`User Dev`
e `Power Dev` não estão dentro do `Agent WF` -- estão como cabeçalho *sobre* ele**. Os
dois polos são desenhados como *entrada* do agente de workflow, não como um caso de uso
dele. Essa é exatamente a formulação que H-004 defende, e ela chegou pelo desenho antes
de chegar pelo argumento.

A leitura: nenhum agente isolado assiste o desenvolvedor. O que assiste é a **composição**
-- e o orquestrador é quem decide a composição. Uma passagem por `/critique` pode compor
`standards-checker`, `test-runner`, `code-reviewer` e `semiotic-inspector`; uma passagem
por `/research --deep` compõe `research-reviewer` e `council-debate`.

A consequência de projeto, e a razão pela qual esta hipótese fecha a seção 1: **o
orquestrador é o lugar onde a adequação ao dev (H-001, H-003) se realiza.** Se a
composição é decidida em tempo de execução, então a posição do humano na escala
citizen↔power é uma **entrada legítima da decisão de composição** -- e não uma
bifurcação que precisaria ser costurada em cada skill separadamente.

Dito de outro modo: o orquestrador é o preposto. Os agentes são o vocabulário de que ele
dispõe. A mensagem é o que ele monta com eles, para este humano, neste turno.

O que a confirmaria: composições visivelmente diferentes para a mesma solicitação vinda
de pontos diferentes da escala, com retradução automática no polo citizen. O que a
refutaria: a adequação exigindo bifurcação dentro de cada skill, o que indicaria que o
orquestrador não é o ponto de variação certo.

---

## 2. De AI-assisted a AI-Native: a hipótese

A literatura sobre desenvolvimento assistido por IA investiga majoritariamente a
comunicação humano -> IA: como o desenvolvedor instrui, corrige e restringe o modelo.
A pergunta de pesquisa que este documento serve aponta na direção inversa: **como o
sistema comunica ao humano as intenções que realizou, e se essa comunicação é
reconstruível por quem a recebe.** É P-003 (a mão de volta) e H-001 (o receptor não é
único) ditas como pergunta -- e é o que a engenharia semiótica chama de
comunicabilidade, aplicada ao preposto generativo de P-002.

A hipótese de trabalho é que o ciclo de desenvolvimento se reorganiza em três fases --
PLAN, BUILD, REFLECT -- atravessadas por uma faixa de retorno contínua. Esta seção
lê cada elemento contra a seção 1: o que já estava lá, o que se refina, o que é novo.
Os termos *AI-assisted* e *AI-native* seguem Hassan et al. (2026), que os usam para
nomear SE 2.0 e SE 3.0.

### 2.1 Três fases como grão grosso do caminho canônico

PLAN, BUILD e REFLECT não são um ciclo novo; são o caminho canônico de P-005 em grão
mais grosso:

| Fase | Skills de P-005 | O que a fase materializa |
|---|---|---|
| **PLAN** | `/research` ou `/explain` > `/design` ou `/plan` | intenção e design. A intenção não nasce pronta: prototipar -> observar -> ajustar, antes de travar o design |
| **BUILD** | `/implement`, com `/critique` **dentro** | o incremento, a partir da intenção registrada; refinar e refatorar são parte da fase, não uma fase depois |
| **REFLECT** | `/reflect` | o que o episódio ensinou, antes do próximo começar |

Duas precisões que evitam contradição com P-005. Primeira: `/critique` não desaparece --
ele vive dentro de BUILD, e o portão "validar antes de comunicar" permanece. Segunda: o
"documentar" que acontece dentro de BUILD é a nota de reflexão-sobre-a-ação do post-skill
e a regeneração do as-coded (voz do agente); não é `/document`, que produz artefato
para leitor e continua vindo depois de `/critique`.

Isto responde Q-008: o `Agent WF` de quatro itens da Figura 2 era este grão grosso, não
uma proposta de ciclo sem validação. Registrado em D-001.

### 2.2 A faixa transversal EXPLAIN / COMMUNICATE

Atravessando as três fases corre uma faixa de retorno, e ela não é uma coisa só:

- **EXPLAIN** é o retorno IA -> humano: o que o preposto entendeu e construiu, no registro
  que o receptor decodifica (P-003). O instrumento é a deriva (H-002, item 3): a
  comparação contínua entre as-coded e as-intended. Mas a deriva é o instrumento, não o
  EXPLAIN -- o EXPLAIN é o retorno cuja *surpresa* dispara o REFLECT.
- **COMMUNICATE** é entre pessoas, mesmo quando mediado por IA: o que o time diz ao
  cliente, ao revisor, ao próximo desenvolvedor.

Duas distinções mantêm a faixa coerente com o que a seção 1 já fixou:

1. **Contínuo para EXPLAIN, gated para COMMUNICATE.** A faixa é contínua para o retorno
   IA -> humano, que não sai do envelope, e para a *preparação* de COMMUNICATE. Cada
   emissão pessoa -> pessoa continua passando por `/critique` (P-005). É uma posição
   semiótica, não de processo: uma mensagem entregue sem validação é o preposto falando
   sem saber se o que diz é verdade.
2. **EXPLAIN-deriva é agnóstico de audiência; EXPLAIN-retradução não.** A comparação
   as-coded x as-intended roda sempre e custa pouco. O registro em que o resultado é
   devolvido depende da posição do humano na escala citizen <-> power (H-003):
   obrigatório num polo, eletivo no outro.

A faixa é uma resposta *candidata* a Q-004 (etapa do post-skill que compara e devolve).
Q-004 permanece aberta até o mecanismo rodar. Abre Q-011.

### 2.3 A seta REDESIGN: deriva como detecção precoce

Quando o EXPLAIN surpreende -- o que voltou não é o que se pretendia -- a seta REDESIGN
volta da faixa ao PLAN. Isto já existe em H-002 (deriva como cidadã de primeira classe,
reconciliada por `/explain drift`). O que a seta muda é o **gatilho**: hoje a deriva é
periódica (verificação a cada 14 dias) e eletiva; detecção precoce pede que ela dispare
por evento, ao fim de cada `/implement`. Esta é a consequência verificável desta
subseção -- e é estado intencional, não atual.

### 2.4 As-conceived / as-intended / as-coded: duas lacunas

<!-- H-005 -->
**H-005 (hipótese) -- Há três estados da intenção, não dois, e só a segunda lacuna
entre eles é verificável por máquina.**

O par de 1.2.2 (as-intended / as-coded, dois arquivos em tensão) esconde um terceiro
termo. Há o que o designer **concebeu** (na cabeça, sem artefato), o que ele
**registrou** (`product-design-as-intended.md`, planos, briefs -- o as-intended, que
continua sendo o arquivo) e o que **existe** (as-coded). Isso dá duas lacunas:

| Lacuna | Entre | Verificável por máquina? | Como aparece |
|---|---|---|---|
| 1 | as-conceived -> as-intended | não | o registro não diz o que se queria; várias realizações cabem no mesmo texto (subespecificação; ver Q-007) |
| 2 | as-intended -> as-coded | sim (`/explain drift`, `check_plan_coverage`) | a implementação diverge do registro |

A lacuna 1 não é verificável, mas é **elicitável**: a surpresa no EXPLAIN (2.2) é a
lacuna 1 detectada através de artefatos da lacuna 2 -- o código voltou fiel ao registro
e ainda assim não era o que se queria. O microloop de PLAN (prototipar -> observar ->
ajustar) é a sonda humana da mesma lacuna, antes de travar o design.

O que a confirmaria: `/explain drift` produzindo, com alguma frequência, propostas de
`/design` (mudar o registro) e não só de `/plan` (mudar o código). O que a refutaria:
toda deriva tratada como bug de código e nunca como bug de expressão -- as surpresas no
EXPLAIN nunca resultando em mudança do as-intended.

Nota de nomenclatura: o termo "as-conceived" para o estado tácito é escolha deste
documento; formulações anteriores usaram outro nome para o termo do meio. O arquivo
as-intended mantém o sentido que tem em 1.2.2 e H-002.

### 2.5 Governança, proveniência, rastreabilidade

A terceira perna da hipótese -- quem altera o quê, de onde veio cada item, cada decisão
ligada à sua intenção -- não acrescenta princípio novo. É P-004 (o sistema de marcadores
e as quatro classificações de autoria dizem de quem é a voz em cada arquivo) e H-002
(IDs estáveis endereçáveis; passos de plano declarando que requisito satisfazem). O que
a hipótese faz é nomeá-la como condição: sem rastreabilidade, o EXPLAIN de 2.2 não sabe
*a que intenção* cada trecho responde, e a retradução vira opinião. Q-007 (de quem é a
voz quando duas vias de autoria escrevem no mesmo texto) continua sendo a questão
aberta desta perna.

### 2.6 Os três registros de Schön relidos nas três fases

A seção 1.2.4 localizou os três registros de Schön em andaimes concretos. A hipótese os
relê sobre o desenho das três fases:

| Registro | Onde vive no desenho | Andaime |
|---|---|---|
| **Reflexão-na-ação** | a faixa EXPLAIN / COMMUNICATE, e os microloops dentro de PLAN (prototipar -> observar -> ajustar) e BUILD (testar -> validar -> refinar -> refatorar) | a justificativa das `AskUserQuestion`; o `/critique` dentro do `/implement`; a comparação contínua da faixa |
| **Reflexão-sobre-a-ação** | o painel REFLECT, depois do episódio | a nota do post-skill; `/reflect` com lente *produto* |
| **Reflexão-sobre-a-prática** | o harness que evolui (2.7) | `/reflect` com lente *prática*, alimentando as skills |

Isto refina 1.2.4 em dois pontos: a reflexão-na-ação deixa de ser só a justificativa
da `AskUserQuestion` e passa a incluir os microloops de PLAN e BUILD; e o `/reflect`
se desdobra pelas duas lentes que a skill já oferece.

### 2.7 O harness que evolui da reflexão do time

<!-- H-006 -->
**H-006 (hipótese) -- As skills e regras do harness podem evoluir a partir dos
registros de reflexão-sobre-a-prática do time, e não apenas de traces de execução do
agente.**

Hoje nenhuma skill lê os registros de `/reflect` como entrada: `/reflect` escreve, o
post-skill indexa, e nada consome. A hipótese está, portanto, não refutada por ausência
de mecanismo -- o que é diferente de confirmada.

A referência mais próxima é o WikiSkill (Tang et al., 2026), que co-evolui
skills reutilizáveis de agente com uma base de conhecimento persistente em três camadas
de escrita: traces de execução imutáveis; um wiki de padrões que acumula e nunca reseta;
skills com atualizações reversíveis. As três camadas mapeiam sobre o SEJA: `_output/`
(imutável, por convenção de artefato), `product-design/` (acumula, `Human (markers)`)
e `.claude/skills` (reversível). O contraste é o que importa: lá, quem propõe e quem
mantém são agentes, e a fonte é a experiência do agente; aqui a fonte são palavras
humanas registradas literalmente, e a mudança de skill passa por autoria humana. É o
mesmo eixo da pergunta de pesquisa desta seção -- humano -> IA no WikiSkill, IA -> humano
aqui -- aplicado ao próprio harness.

O que a confirmaria: uma mudança de skill cujo plano cita um registro de reflexão como
origem (rastreabilidade de P-004). O que a refutaria: reflexões acumuladas sem nenhum
plano que as cite -- a crítica de Eraut (1994) a andaimes que viram ritual, já
registrada em H-002. Abre Q-013.

### 2.8 As três fases com validação por passo: o portão determinístico

D-001 leu o `Agent WF` de quatro itens como o grão grosso do caminho canônico, com o
`/critique` dentro de BUILD. Curto é a superfície que o leitor vê, não o conteúdo.
Falta dizer o que torna confiável a validação dentro de BUILD quando quem constrói é
um agente que escreve mais rápido do que o humano revisa.

<!-- H-008 -->
**H-008 (hipótese) -- PLAN -> BUILD -> REFLECT pode ser oferecido como caminho de
entrada ao agente de workflow sem perder o que P-005 protege, desde que: (a) dentro de
BUILD, cada passo do agente só conta como feito quando um portão determinístico responde
PASS -- a validação que 2.1 põe dentro de BUILD passa a acontecer passo a passo, como
resultado de ferramenta, antes do `/critique`; e (b) a reflexão atravessa as fases, e
cada fase termina com um espelho oferecido ao designer: no PLAN, o plano contado a uma
audiência; no BUILD, a deriva entre o que se pretendia e o que existe.**

A condição (a) é a frase "PASS é resultado de ferramenta, não frase": prosa no prompt
não é plano de controle. O portão reúne verificações que não negociam -- lint e tipos,
testes com cobertura por ramo, complexidade ponderada pela cobertura (CRAP) nas funções
tocadas, contratos de dependência entre módulos e, numa rodada mais lenta, testes de
mutação. O limiar só se move por mão humana (ratchet a partir do baseline): o agente fica
no laço interno, o humano no externo, dono das restrições.

P-005 continua de pé: `/critique` sempre precede `/document` e `/communicate`. O que a
H-008 muda é o papel do `/critique` no fim de BUILD: ele deixa de ser a primeira
validação e passa a ser a medida do que escapou do portão.

A condição (b) relê 2.6 no grão do passo e no grão da fase. Reflexão-na-ação: a
justificativa de cada `AskUserQuestion` e, no microloop de BUILD, o que muda na
tentativa seguinte a um FAIL. Reflexão-sobre-a-ação: a nota ao fim do `/plan` (1.2.4) e
uma nota curta por passo de BUILD -- o que aconteceu, o que desviou, sobre o que se está
menos seguro -- com o resultado do portão como evidência. Reflexão-sobre-a-prática: o
`/reflect` com lente *prática* (2.6), lendo notas e resultados do portão através de
vários planos -- a entrada de que H-006 precisa.

Os espelhos são o que a nota do agente sobre si mesmo não alcança. O espelho do PLAN é
o plano contado a um segmento (`/communicate`): a retradução de P-003 aplicada à
intenção antes de ela virar código; plano que não sobrevive a ser contado não está
claro. O espelho do BUILD é a deriva entre as-intended e as-coded (`/explain drift`,
com o as-coded regenerado): o portão responde se cada passo foi construído certo; a
deriva responde se o que se construiu era o que se pretendia, e o que se pretendia e
não entrou. Os dois são **oferecidos** ao fim da fase, nunca impostos -- a retradução é
eletiva no polo power (H-003) -- e o `/reflect` registra quando um deles não foi medido.
É assim que a Q-008 se fecha: o ciclo curto não descarta `/communicate` e `/explain`;
ele os internaliza como instrumentos de reflexão de cada fase, e P-005 segue de pé --
o `plan-reviewer` precede o comunicar do plano, e o `/critique` do fim de BUILD precede
o explicar da deriva.

O ciclo tem uma pré-condição: sem `as-intended` não há PLAN -> BUILD -> REFLECT. O
`/design` precede qualquer ciclo, como 2.1 já diz da primeira iteração; não existe modo
degradado em que a deriva não tenha contra o que ser medida.

É um caso de H-004: o orquestrador compõe, por passo, um subagente novo e o portão, e,
por fase, o espelho que o designer aceitar; a composição varia com a escala de H-003
(no polo citizen, a retradução do resultado do portão é obrigatória; no polo power, o
resultado cru basta).

| Medida | Fonte |
|---|---|
| iterações até PASS, por passo | resultado do portão por passo |
| taxa de escape: achados críticos do `/critique` final em código de passo com PASS, por passos com PASS | log do `/critique` x resultado do portão |
| escapes de intenção: itens de deriva (construído sem intenção, intenção não construída) por plano, nos ciclos em que a deriva foi medida | relatório do `/explain drift` após o BUILD |
| sobreviventes de mutação por commit, na rodada lenta | resultado do portão |
| marcadores de evasão acrescentados (skip, xfail, no cover, no mutate) sem motivo registrado | ratchet do portão |
| notas por passo com desvio cujo passo seguinte as cita (nota que age) | nota por passo x passo seguinte |
| espelhos aceitos por fase (comunicação do plano, deriva do BUILD) | registro do `/plan` e do `/implement` no progress file |

Antes do primeiro ciclo medido, o designer fixa e registra (como `D-NNN`) o número
mínimo de planos e os limiares; fixá-los depois de ver os dados invalida a medida. O
que a confirmaria: a taxa de escape abaixo do limiar, marcadores de evasão estáveis, a
maioria das notas com desvio mudando o passo seguinte e, nos ciclos com deriva medida,
escapes de intenção raros. O que a refutaria: (i) a taxa de escape acima do limiar -- o
portão não ocupa o lugar da validação; (ii) evasão ou sobreviventes de mutação crescendo
com o portão em PASS -- o agente otimiza o número, e o ratchet não segura; (iii) notas
por passo que não mudam nenhum passo seguinte -- o ritual que H-003 aponta como risco do
polo power; (iv) escapes de intenção frequentes com o portão em PASS -- o portão prova
correção, não intenção, e o ciclo curto precisa do espelho como passo fixo, não como
oferta.
Registrado em D-002 o que o release faz enquanto a hipótese está em teste.

---

## Questões abertas

| ID | Questão | Bloqueia |
|---|---|---|
| `Q-001` | Referência bibliográfica exata do artigo de Abrahão de que partiu o desenho de 1.1.2 -- autor(es), título, veículo, ano. Não foi inventada aqui de propósito. | citação de P-002 |
| `Q-002` | A escala H-001 é ortogonal a BLD/SHP/GRD e L1-L3, ou colapsa parcialmente? Quantos pontos discretos ela precisa para ser operacional? | operacionalização de H-001 |
| `Q-003` | Como o harness **detecta** a posição do humano na escala? Declaração explícita no `conventions.md`? Inferência a partir da interação? Escolha por sessão? **Sustentada em aberto por decisão de 2026-08-26 -- ver nota abaixo.** | H-003 |
| `Q-004` | A retradução obrigatória (P-003) é um novo artefato, um novo modo de `/explain`, ou uma etapa do `post-skill`? | P-003 |
| `Q-005` | Este documento fica em pt-BR ou é traduzido para en-US junto com `docs/`? O SEJA é publicado publicamente. | publicação |
| `Q-006` | Relação entre este documento e o `product-design-as-intended.md` no formato §0-§17 do template -- ver nota abaixo. | estrutura |
| `Q-007` | Duas vias de autoria escrevem no mesmo `</>` (Figura 1). De quem é a voz que o leitor do código está lendo? O harness precisa distinguir trecho de autoria humana de trecho de autoria do preposto? | `P-002a` |
| `Q-008` | O `Agent WF` da Figura 2 lista **Research → Plan → Implement → Reflect** -- um ciclo **reduzido**, sem `/design`, `/critique`, `/document` e `/communicate`. É simplificação do desenho, ou é uma proposta deliberada de ciclo mais curto para o agente de workflow? Se for deliberada, colide com `P-005` (validar antes de comunicar). **Fechada por D-001 (2026-09-18).** Reforçada por H-008 (2026-10-03): o ciclo curto internaliza `/communicate` e `/explain` como espelhos de fase. | `P-005`, `H-004` |
| `Q-009` | "Orquestrador" aparece **duas vezes** na Figura 2: dentro da lista do `Agent WF` e de novo, solto, fora da caixa. São dois níveis de orquestração (um por-workflow e um global), ou é repetição de ênfase? | `H-004` |
| `Q-010` | O círculo com figura no alto à esquerda da Figura 1, alimentado por um humano e ligado ao `</>`, não foi identificado com segurança. O que representa? | leitura da Figura 1 |
| `Q-011` | Como a faixa contínua de EXPLAIN (2.2) respeita o portão de P-005 sem virar ritual -- o que é "preparar" um COMMUNICATE sem emiti-lo? | 2.2, Q-004 |
| `Q-012` | O `semiotic-inspector` avalia signos de interface via SIM. Avaliar a retradução (se a mensagem IA -> humano é reconstruível pelo receptor) pede um modo novo. Qual método -- CEM adaptado? | pergunta de pesquisa da seção 2 |
| `Q-013` | Qual skill consome os registros de `/reflect` como entrada, e com que regra de escrita sobre `.claude/skills` (reversível? proposta + confirmação humana?) | H-006 |

> **Nota sobre `Q-003`.** Esta questão está **deliberadamente sustentada em aberto**, e
> não meramente sem resposta. A razão é de dependência: não se decide *como detectar* a
> posição de alguém numa escala cujos pontos ainda não foram definidos -- e a granularidade
> da escala é justamente o que `Q-002` mantém em aberto. Fixar um mecanismo de detecção
> agora (campo em `conventions.md`, inferência, escolha por sessão) congelaria por via
> indireta uma resposta a `Q-002` que ainda não temos. Fechar `Q-002` primeiro é o
> caminho; até lá, `H-003` permanece como leitura, sem implementação.

> **Nota sobre `Q-006`.** O esqueleto do template (`§0 Planned Changes`, `§1 Platform
> Purpose`, `§2 Entity Hierarchy`, ... `§17`) é moldado para produto: hierarquia de
> entidades, modelo de permissões, jornadas. Este documento é de outro nível -- é a
> fundamentação teórica de que o produto decorre. A leitura corrente é que ele é
> **anterior** ao as-intended no formato do template, e que este último ainda precisa ser
> semeado. Se a decisão for fundir, esta seção 1 vira a base de `§1 Platform Purpose` e
> `§3 Domain-Specific Concepts`, e as hipóteses migram para `## Decisions`.

---

## Decisions

> Decisões registradas por `apply_marker.py --marker DECISION_APPEND` (formato DDR:
> Context / Decision / Consequences / Rejected Alternatives). Uma decisão fecha ou
> reencaminha uma questão aberta; hipóteses não entram aqui até serem decididas.

### D-001: O Agent WF de três fases é o grão grosso do caminho canônico; Q-008 fechada

**Context**: A Figura 2 lista Research -> Plan -> Implement -> Reflect, mais curto que o ciclo de P-005. Q-008 perguntava se era simplificação do desenho ou proposta de ciclo sem validação.
**Decision**: PLAN / BUILD / REFLECT são o caminho canônico em grão grosso: PLAN = investigar + dar forma; BUILD = `/implement` com `/critique` dentro; REFLECT = `/reflect`. O portão "validar antes de comunicar" permanece.
**Consequences**: Q-008 fechada por testemunho do autor do desenho. `/document` e `/communicate` continuam depois de `/critique`; o "documentar" interno a BUILD é a voz do agente (nota do post-skill, as-coded), não artefato para leitor. Ver seção 2.1.
**Rejected Alternatives**: tratar o Agent WF como ciclo reduzido sem `/critique` -- colide com o único invariante rígido do harness.

### D-002: O release apresenta PLAN -> BUILD -> REFLECT como caminho de entrada, condicionado ao portão determinístico (H-008)

**Context**: D-001 leu o ciclo curto como grão grosso de P-005. O release precisa dizer sob que condição o oferece a quem instala, enquanto H-008 não foi medida.
**Decision**: O caminho de entrada documentado é PLAN -> BUILD -> REFLECT. Dentro de BUILD, o `/implement` roda o portão determinístico por passo quando o projeto o instalou; o `/critique` do fim de BUILD continua obrigatório e seus achados críticos são cruzados com os passos que tiveram PASS (taxa de escape de H-008). `/critique` antes de `/document` e `/communicate` não muda (P-005). O `/plan` oferece ao fim o `/communicate` do plano e o `/implement` oferece no wrap-up o `/explain drift` com o as-coded regenerado; nenhum dos dois é obrigatório, e o `/reflect` registra quando não foram medidos. O ciclo exige as-intended: o `/seja-setup` entrega ao `/design`, e o `/plan` recusa partir sem `product-design-as-intended.md`.
**Consequences**: Projetos sem portão instalado ficam fora da medida de H-008; neles o `/critique` dentro de BUILD continua sendo a primeira validação, como em 2.1 e D-001. O primeiro ciclo real com portão gera a primeira medida, contra limiares fixados antes dele. A medida de escapes de intenção só existe nos ciclos em que o designer aceitou a deriva; a taxa de aceitação dos espelhos é ela própria registrada.
**Rejected Alternatives**: apresentar o ciclo curto sem condição; tornar o portão obrigatório na instalação; espelhos obrigatórios (um agente gerador por plano, contra H-003); modo degradado sem as-intended (a deriva não teria referência).

## Referências

Herdadas de `docs/foundations.md`, que é o primer em prosa desta mesma fundamentação:

- de Souza, C.S. (2005). *The Semiotic Engineering of Human-Computer Interaction*.
  Cambridge, MA: MIT Press. Template de metacomunicação (cap. 1 e 3), classes de signo
  (cap. 4), preposto do designer, comunicabilidade.
- de Souza, C.S. e Leitão, C.F. (2009). *Semiotic Engineering Methods for Scientific
  Research in HCI*. Morgan & Claypool. Tratamento metodológico de SIM e CEM.
- de Souza, C.S., Cerqueira, R.F.G., Afonso, L.M., Brandão, R.R.M. e Ferreira, J.S.J.
  (2016). *Software Developers as Users: Semiotic Investigations in Human-Centered
  Software Development* (SigniFYI). Springer. **Extensão da engenharia semiótica ao
  pipeline voltado ao desenvolvedor -- a base direta de P-002.**
- Barbosa, S.D.J., Barbosa, G.D.J., de Souza, C.S. e Leitão, C.F. (2021). "A
  Semiotics-based epistemic tool to reason about ethical issues in digital technology
  design and development." *Proc. FAccT '21*, pp.363-374. O EMT.
- Schön, D.A. (1983). *The Reflective Practitioner: How Professionals Think in Action*.
  New York: Basic Books.
- Eraut, M. (1994). *Developing Professional Knowledge and Competence*. London: Falmer
  Press. Contra-leitura sobre os limites de andaimes de reflexão.
- Eco, U. (1976). *A Theory of Semiotics*. Sistema de significação vs. processo de
  comunicação.
- Hassan, A.E., Oliva, G.A., Lin, D., Chen, B. e Jiang, Z.M. (2026). "Towards AI-Native
  Software Engineering (SE 3.0): A Vision and a Challenge Roadmap." *ACM Transactions on
  Software Engineering and Methodology*. DOI 10.1145/3807901 (online em 21 ago. 2026;
  preprint arXiv:2410.06107, 2024). Origem dos termos AI-assisted (SE 2.0) e AI-native
  (SE 3.0) do título da seção 2.
- Tang, L., Rashtchian, C., Ferng, C.-S., Tomkins, A., Juan, D.-C. e Vu, T. (2026).
  "WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution."
  arXiv:2608.27454. Contraste de H-006: três camadas de escrita (traces imutáveis, wiki
  que acumula, skills reversíveis), com a experiência do agente como fonte.
- Abrahão, ... -- **`Q-001`, a completar.**

---

## Apêndice A -- Notas de origem (verbatim)

> Notas da conversa com o Anax, 2026-08-26, registradas literalmente conforme a
> disciplina do `/reflect`. Esta seção 1 é a leitura estruturada delas; o texto abaixo
> é a fonte.

Nós desenhamos o que é ser dev atualmente, vindo de um desenho do artigo do abrahao.
temos agora os devs falando com o robo, que produz código, apoiado nas ferramentas.
também temos os User ou citzen devs, que não sabem ler código, mas tem uma intenção e
esperam que a computabilidade do robo gere algo que traduza do código que foi
implementado para uma linguagem adequada a ele. o harnerss, e seus agentes precisam se
adequar ao qual dev estão assistindo. uma hipótese é que podemos ter uma escala que vai
do user/citzen dev até o power dev especialista em tecnologia. uma outra hipotese é que
o seja pode ser uma boa ferramenta para embasar a computabilidade dos agentes a medida
que eles transformam intenções em código executável. O agente de workflow possui um
orquestrados que pode chamar diversos agentes para compor o que é necessário para o
agente de IA dev assista o humano no desenvolvimento de software.

---

## Apêndice B -- Leitura dos desenhos

> Os dois desenhos (`docs/design-software-project.png`, `docs/designt-harnerss.png`) foram
> feitos na mesma sessão com o Anax que gerou as notas do `Apêndice A`. Nesta leitura,
> **branco = o arranjo herdado; vermelho = o que foi acrescentado na sessão.** Essa
> distinção é significativa: o vermelho é, literalmente, a contribuição desta sessão.

### B.1 Figura 1 -- Design do software project

Tudo está contido numa caixa rotulada **"Projeto"**. A unidade de análise é o projeto,
não a sessão nem o turno -- o que importa porque intenção, convenção e deriva só fazem
sentido no horizonte do projeto.

| Elemento | Cor | Leitura |
|---|---|---|
| **Robô** (figura de cabeça quadrada, ao centro) | circulado em **vermelho** | O terceiro interlocutor de `P-002`. Está no centro geométrico do desenho, e o círculo vermelho é a ênfase da sessão: ele é o elemento novo. |
| **`</>`** (canto superior direito) | caixa branca, **remarcada em vermelho** | O código. Recebe **duas setas**: uma do robô, outra do lado humano -- base de `P-002a`. |
| **`LN`** (caixa entre o User Dev e o robô) | **vermelho** | Linguagem natural, nomeada como artefato explícito. Tem tráfego **nos dois sentidos**: sobe para o robô e desce dele. É `P-003` desenhada. |
| **User Dev / Citzen Dev** (figura humana, canto inferior esquerdo) | branco, rótulo branco | O polo de baixa literacia de código. Sua única via para o robô é o `LN`. |
| **Time** (grupo de figuras humanas, centro-inferior) | branco | Os demais desenvolvedores. Ligados entre si e ao `</>`. |
| **Convenções / Design / Intenção** (caixa, canto inferior direito) | caixa branca, **seta vermelha grossa** | A camada de design. A seta grossa vermelha entra nela **vindo de fora e de baixo da caixa "Projeto"** -- isto é, **o harness injeta a camada de design no projeto a partir de fora**. |
| **Linha horizontal com terminações em T** (base do desenho) | **vermelho** | O eixo/escala. Corre **por baixo da população de desenvolvedores**, do `User Dev` à esquerda em direção ao time à direita. |

Três coisas que o desenho acrescenta às notas:

1. **A escala é propriedade da população, não do indivíduo em sessão.** A linha vermelha
   é desenhada sob *todos* os humanos do projeto, não anexada a um deles. Isso reforça
   a suspeita de `Q-003`: talvez a pergunta certa não seja "como detectar a posição deste
   usuário?", e sim "como o projeto declara a distribuição de literacia do seu time?".
2. **A camada de design vem de fora do projeto.** A seta vermelha grossa atravessa a
   fronteira da caixa "Projeto". O harness não é parte do projeto: é o que se aplica
   sobre ele. Isso é coerente com o padrão *workspace* que o `/seja-setup` oferece.
3. **O `LN` é bidirecional por desenho.** `P-003` foi escrita como argumento; a figura
   já a tinha como fato.

### B.2 Figura 2 -- Design do harness

Dois painéis lado a lado.

**Painel esquerdo -- o agente de workflow** (todo em vermelho, isto é, todo novo):

- Cabeçalho dividido em duas caixas: **`User Dev`** | **`Power Dev`**. Elas estão
  *sobre* o painel, não dentro -- os polos são entrada do agente, não conteúdo dele.
- Corpo: **`Agent WF`**, com os itens `Orquestrador`, `Research`, `Plan`, `Implement`,
  `Reflect`. Um traço vertical liga `Research → Plan → Implement`, sugerindo sequência
  ou laço.
- Fora da caixa, abaixo: **`Orquestrador`** de novo, solto (ver `Q-009`).

**Painel direito -- o harness:**

- Rótulo **`Harness`** no topo, em vermelho.
- Dentro, uma caixa branca: **`Docs (O que é o SEJA)`**, contendo
  `- Princípios Eng. Semiótica`, com os três itens `• Conceitos fundamentais`,
  `• Fluxos de trabalho`, `• Agentes principais`.
- Abaixo, uma caixinha com seta para baixo apontando para **`LLM`**.

Duas coisas que o desenho acrescenta:

1. **Este documento é o artefato desenhado.** A caixa `Docs (O que é o SEJA)` contém
   exatamente o índice da seção 1 deste arquivo. A seção 1 não é uma interpretação do
   desenho -- é o preenchimento de uma caixa que o desenho já reservou.
2. **O harness assenta sobre o LLM, e os Docs assentam sobre o harness.** A pilha
   desenhada é `Docs → Harness → LLM`. O harness é a camada que faz o documento chegar
   ao modelo -- o que é a leitura mais literal possível de `H-002`: a intenção vira
   computável porque existe uma camada que a entrega ao modelo em forma operável.

E uma divergência que o desenho expõe: o ciclo listado no `Agent WF` é **mais curto** que
o caminho canônico de `P-005` -- faltam `/design`, `/critique`, `/document` e
`/communicate`. Como `/critique` é o portão do único invariante rígido do harness, a
ausência não é cosmética. Registrada em `Q-008`.

---

## CHANGELOG

2026-08-26 | § 1 | added | - | Seção 1 (Princípios da engenharia semiótica) redigida a partir das notas da conversa com o Anax; P-001..P-007 registrados, H-001..H-004 registradas como hipóteses abdutivas, Q-001..Q-006 abertas
2026-08-26 | Q-003 | held-open | - | detecção da posição na escala sustentada deliberadamente em aberto: depende de Q-002 (granularidade da escala), que precede
2026-08-26 | Apêndice B | added | - | desenhos de origem (design do software project e design do harness) incorporados; P-002a acrescentado a partir da Figura 1 (duas vias de autoria sobre o código); Q-007..Q-010 abertas
2026-09-18 | § 2 | added | - | Seção 2 (De AI-assisted a AI-Native: a hipótese) redigida: três fases como grão grosso de P-005, faixa EXPLAIN/COMMUNICATE, seta REDESIGN, trio as-conceived/as-intended/as-coded, governança como condição, Schön relido nas fases, harness que evolui da reflexão do time
2026-09-18 | H-005 | added | - | três estados da intenção (as-conceived / as-intended / as-coded) e duas lacunas; só a segunda é verificável por máquina, a primeira é elicitável via P-003
2026-09-18 | H-006 | added | - | skills e regras do harness evoluindo a partir dos registros de /reflect; WikiSkill (Tang et al., 2026) como referência e contraste
2026-09-18 | Q-011..Q-013 | added | - | faixa contínua vs portão de P-005; método para avaliar a retradução; skill que consome os registros de /reflect
2026-09-18 | Q-008 | answered | plan-000005 | fechada por D-001: o Agent WF de quatro itens da Figura 2 é o grão grosso do caminho canônico, não um ciclo sem validação
2026-09-18 | Q-004 | candidate | - | a faixa de 2.2 (etapa do post-skill que compara e devolve) é resposta candidata; segue aberta até o mecanismo rodar
2026-09-18 | Q-006 | partial | - | seção ## Decisions criada neste arquivo independentemente da fusão com o template; D-NNN daqui ficam fora do decision digest e CHANGELOG_APPEND não aceita os IDs deste arquivo até o registro As-Intended/As-Coded e o regex do harness os conhecerem; Q-006 segue aberta só na fusão
2026-09-18 | 1.2.4 | refined | - | reflexão-na-ação passa a incluir os microloops de PLAN e BUILD; /reflect se desdobra pelas lentes produto (sobre-a-ação) e prática (sobre-a-prática) -- ver 2.6
2026-09-18 | H-007 | renumbered | plan-000004 | a hipótese que o plan-000004 (SEJA como serviço) propõe registrar passa a ser H-007, e a próxima questão aberta é Q-014
2026-10-03 | H-008 | added | - | PLAN -> BUILD -> REFLECT de 2.1 como entrada, com portão determinístico por passo, reflexão transversal e espelho oferecido ao fim de cada fase (comunicação do plano, deriva do BUILD); fecha Q-008 por internalização; caso de H-004, dá condição operacional a D-001
2026-10-03 | D-002 | added | - | o release apresenta as três fases como entrada, com o portão como condição, a taxa de escape do /critique final e os escapes de intenção como medidas, e /design obrigatório antes do ciclo; projetos sem portão ficam fora da medida
