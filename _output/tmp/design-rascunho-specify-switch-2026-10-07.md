# Rascunho para o /design do open-seja (branch dev) -- 2026-10-07: interruptor da specify

> Preparado pelo Step 1 do plan-000022 (`_output/plans/plan-000022-specify-switch.md`). Fontes: o adendo 2026-10-07 do roadmap-000006, a nota `inbox/2026-10-07-gherkin-opt-out-experimento-e-specify-por-plano.md` do repositório do pesquisador, a revisão deep do plan-000022 e os textos atuais de D-005, D-009, H-009, CYC-004, CYC-033 e `drift-control-protocol.md`.
>
> Uso: rode `/design` dentro de `open-seja/`. A prosa abaixo é proposta do agente. Corrija a voz, aceite, recuse ou mude cada bloco. O agente não escreve prosa no as-intended (T4). Os blocos de contrato (Parte C) entram pelo Step 3 do plano, depois que você aprovar as Partes A e B.
>
> Nada aqui vale enquanto você não registrar. Até lá, D-009, D-005, CYC-004 e CYC-033 valem como estão.

---

## O que mudou, em uma frase

Você quer poder rodar o open-seja como instrumento de experimento: um projeto com a especificação em Gherkin como padrão e outro sem, na mesma versão do harness, e cada plano podendo desviar do padrão com o motivo registrado.

Nas suas palavras (2026-10-07):

> acho que faz sentido um preset ou um parametro no plan. pode ser que o dev esteja em um estágio de prototipação e não faz sentido materializar tantos artefatos e acabar escrevendo mal os requisitos e gherking

> olha, assumindo que vamos usar o open-seja para fazer experimentos, eu fico curioso de ver se é válido ou não habilitar o gherking e fazer experimentos: um time usa o outro nao e medimos a velocidade/entendimento/qualidade do que foi construido. neste caso estou pendendo mais para um opt-out e um preset a ser decidido no setup/design. ao mesmo tempo, como usuário do seja, eu posso querer ainda sim escolher escrever a fase de especificação individualmente para cada plano

Respostas suas na grill do plan-000022 (2026-10-07):

- Quando o projeto não declara o valor: o setup e o upgrade perguntam; enquanto não há resposta, vale `on`.
- Quando a specify está desligada numa tarefa com código: a grill faz a entrevista curta (as quatro linhas de `## Intenção` no plano), sem `intent.md` nem REQ IDs.

---

## Parte A -- Decisões

### A.1 Nova D-NNN (provavelmente D-011), que substitui a D-009

**Título proposto**: O ciclo default entra por upgrade de tag e tem um interruptor por projeto (`SPECIFY_DEFAULT`); cada plano pode desviar com motivo registrado

**Context**: A D-009 fechou o ciclo default "sem chave de desligar" e pôs o braço de controle do piloto na tag anterior pinada. Duas coisas mudaram a leitura. Primeira: entre duas tags muda o Gherkin e também tudo o que entrou na release (grill, checks, matriz, correções); o controle por tag confunde a variável que H-009 quer isolar. Segunda: na prototipação, requisitos e Gherkin escritos à força são ruído no vetor D; obrigar a escada não protege a medida, piora. O designer quer usar o open-seja como instrumento de experimento (com e sem a escada) e, como usuário, escolher a fase de especificação por plano.

**Decision**: O ciclo continua entrando pela tag e agindo só onde há `features/<slug>/` ou plano v2 (o que a D-009 já dizia). Passa a existir a variável `SPECIFY_DEFAULT: on | off` em `product-design/conventions.md`. Ausente vale `on`. O `/seja-setup` pergunta o valor na instalação; o upgrade pergunta quando a variável falta e só grava com resposta explícita. Cada plano v2 novo registra o braço no próprio cabeçalho (`Specify default: on | off`). Por plano: `/plan --with-specify` liga a fase quando o default é `off`; a flag de desligar (nome em A.3) desliga quando é `on`, com motivo obrigatório. Quando a fase não roda numa tarefa com código, a grill faz a entrevista curta. O pulo passa a ter três classes: `tarefa sem código` (a de hoje), `default off` e `opt-out`. O braço de controle do piloto é a **mesma tag com `off`**.

**Consequences**:
- O upgrade passa a poder gravar `conventions.md`, mas só depois de resposta explícita; sem resposta, não grava e diz "vale `on` até você responder". O script de upgrade continua sem tocar em `conventions.md`.
- H-009 passa a ser lida de dois jeitos: por intenção de tratar (o braço do projeto) e por protocolo (o que cada plano fez). A taxa de desvio é reportada como achado.
- O braço de controle deixa de ser o ciclo de H-008 puro: com `off`, o controle tem a entrevista curta e plano v2. O contraste vira "escada x entrevista curta" (ameaça declarada no protocolo).
- Planos v1 continuam valendo para sempre (D-008). Nenhum plano existente é reescrito.
- Um preset continua sendo perfil (D-003); a chave não é preset.

**Rejected Alternatives**:
- Sem chave (D-009): o controle por tag confunde o Gherkin com o resto da release, e a prototipação produz Gherkin ruim.
- Preset por projeto: a D-003 diz que preset não bifurca o ciclo, e um preset é fixado no pin, não escolhido por plano.
- Escolha por plano sem default de projeto: não dá braço para o experimento.
- Reusar `--specify` para ligar a fase: `--specify` já quer dizer "rodar só a fase specify, avulsa" (SPC-016).

**Source**: plan-000022 Step 1; adendo 2026-10-07 do roadmap-000006.

**Marcador na D-009**: `superseded` pela nova D-NNN.

### A.2 Revisão da D-005 (grill e specify como fases do `/plan`)

A D-005 continua certa no que importa (fases do `/plan`, não skills; a grill nunca é pulada, mas pode ser curta). Duas frases dela ficam desatualizadas:

- Decision: "A specify é pulada por tipo de tarefa (DOCUMENT, CHORE, RESEARCH, steps só de config ou harness)". Passa a ser: por tipo de tarefa **ou** pelo interruptor e pela escolha do plano (nova D-NNN).
- Rejected Alternatives: "specify por escolha livre (H-009 não mede o que é opcional)". A nova D-NNN responde: a escolha não é livre, é registrada com classe e motivo, e a medida passa a ter as duas leituras.

Duas formas de registrar, à sua escolha:

1. **Só a nova D-NNN cita a D-005** ("revisa a D-005 em dois pontos"), e a D-005 fica como está, com STATUS `proposed`. Mais simples; a D-005 não perde o resto do texto.
2. **A D-005 recebe `superseded`** e uma D-NNN nova reescreve a D-005 inteira com as duas frases mudadas. Mais limpo para quem lê só as decisões, mais trabalho.

Recomendação do agente: a forma 1. A D-005 continua válida em quase tudo, e a nova D-NNN diz exatamente o que muda.

### A.3 Três decisões que só você toma

| Decisão | Opções | Recomendação do agente |
|---|---|---|
| Nome da flag de desligar | `--no-specify "<motivo>"` / `--without-specify "<motivo>"` | `--without-specify`: pela convenção de CLI, `--no-X` nega `--X`, e `--specify` já existe com outro sentido (fase avulsa, SPC-016); o par `--with-specify` / `--without-specify` é simétrico e nenhuma das duas existe ainda |
| Sequência de release | ciclo default, PKB (plan-000020) e este interruptor na v0.11.0 / interruptor na v0.11.0 e PKB na v0.12.0 / outra | o interruptor entra na v0.11.0 (a seção `[v0.11.0]` do CHANGELOG está cortada e sem tag; as notas dela dizem "needs no switch" e "does not touch conventions.md", e isso precisa mudar antes da tag). Onde o PKB entra é decisão sua; se for na v0.11.0, os Steps 3 a 11 do plan-000022 terminam antes do Step 11 do plan-000020, que cria a tag |
| `/design` como segunda porta | o `/design` também pergunta e grava `SPECIFY_DEFAULT` / só o setup e o upgrade | só o setup e o upgrade neste plano; o `/design` fica declarado fora do escopo (um plano depois, se fizer falta) |

---

## Parte B -- Hipótese

### B.1 Ajuste à H-009 (§3, 2.9)

Proposta de parágrafo a acrescentar depois de "O que a refutaria":

> Com o interruptor (D-NNN), H-009 tem duas leituras. **Por intenção de tratar**: os projetos ou planos com `Specify default: on` contra os com `off`, cada um no braço que lhe foi atribuído, desviando ou não. Diz se adotar a escada como padrão funciona. **Por protocolo**: os planos que escreveram a especificação contra os que não escreveram. Diz se a escada funciona quando é escrita, com viés de seleção (quem escreve pode ser quem tem a intenção mais clara). A leitura por protocolo da divergência por degrau só é mensurável no piloto com oráculo (O1 e D3b contra o oráculo, `drift-control-protocol.md`), porque um plano sem specify não tem vetor D. Fora do piloto, o ledger mede aderência (quantos planos seguiram o braço e por que desviaram), não desfecho. Os limiares das duas leituras são fixados antes do primeiro dado (Q3).

Proposta de condição de refutação acrescentada:

> Se, no piloto, os planos que escreveram a especificação não tiverem O1 e D3b menores que os que pularam, nas mesmas features, a escada não paga o seu custo quando é escrita. Se a taxa de desvio no braço `on` for alta, o custo percebido da escada é um achado, não uma falha a esconder.

---

## Parte C -- Contrato e protocolo (entram pelo Step 3 e pelo Step 8, depois da sua aprovação)

Listados aqui para você ver o alcance antes de decidir. O agente escreve estes blocos como emendas aditivas marcadas "emenda 000022", cada uma com a linha "Ruptura que pode provocar" (CYC-014).

- **CYC-004** (quando a specify é pulada): três classes, `tarefa sem código`, `default off` e `opt-out`. Motivo sem classe = `tarefa sem código` (os planos v2 que já existem continuam válidos). `opt-out` exige motivo.
- **CYC novo** (o interruptor): `SPECIFY_DEFAULT`, ausente = `on`; as duas flags; a linha `Specify default:` no cabeçalho; o desvio sempre registrado.
- **CYC-033** (o ciclo entra por upgrade de tag): "Não há chave de ligar ou desligar" passa a "há uma chave por projeto e uma escolha por plano, as duas registradas"; o braço de controle passa a ser a mesma tag com `off`.
- **CYC-018, CYC-029 e Compatibilidade**: com `default off` ou `opt-out`, um step pode ter `Tests:` real com `Scenarios: N/A (motivo)`.
- **GRL-012**: duas linhas novas (specify desligada numa tarefa com código: entrevista curta; specify desligada e `--with-specify`: grill completa).
- **SPC-002**: a specify também não roda por `default off` ou `opt-out`.
- **`drift-control-protocol.md`**: o braço A (controle) passa a ser a mesma tag com `off` (entrevista curta, plano v2 `default off`, `Tests:` por step); a seção 9 ganha a ameaça "o controle tem entrevista curta; o contraste deixa de ser o ciclo de H-008"; o retrofit da seção 4 vale para plano v2 `default off`; a leitura por protocolo é feita só com o oráculo.

---

## Ruptura que esta revisão pode provocar

- Ao citizen: "agora o setup me pergunta se quero especificação em Gherkin, e eu não sei o que isso é". A pergunta precisa vir em voz controlada, com o exemplo da prototipação.
- Ao pesquisador: "o braço de controle mudou de natureza; resultados de piloto com a tag anterior não são comparáveis com os novos". Fica declarado no protocolo.
- Ao power dev: "posso desligar a escada num plano sem justificar". Não pode: o motivo é obrigatório e aparece no relatório de aderência.

---

## Fora do escopo

Um preset `prototype` com outro conjunto de skills; a grill completa quando a specify está desligada; o `/design` como segunda porta do interruptor; reabrir a D-003.
