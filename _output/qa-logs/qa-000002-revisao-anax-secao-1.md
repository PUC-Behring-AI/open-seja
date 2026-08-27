# QA 000002 | 2026-08-27 00:45 UTC | Revisão para o Anax da seção 1 do SEJA as-intended

- **Brief**: o que foi decidido aqui e a informação condensada sobre os docs gerados para o anax revisar
- **Skill**: `/document` (tipo inferido: `ddr`)
- **Saída**: `docs/revisao-anax-2026-08-26.md`
- **Artefato documentado**: `product-design/seja-as-intended.md`
- **Branch**: `seja-intention-docs`

---

## Q&A log

### 1. Limpeza e commit inicial

**Usuário**: adicionei a documentacao produzida pela simone em docs/. vamos remover os arquivos
Zone.Identifier e commitar em uma nova branch: seja-intention-docs. depois vou colocar minhas
notas sobre conversa com o Anax hoje de tarde. por alto é um novo começo para o seja. e vamos
produzi-lo as-intended primeiro, documentando a intenção do que é o SEJA, começando por:
1-Principios da engenharia semiotica. 1.1 conceitos fundamentais/ 1.2 fluxos de trabalho
1.3 agentes principais

**Agente**: Removidos 189 arquivos `:Zone.Identifier` (lixo de download do WSL). Criada a branch
`seja-intention-docs` e commitadas as quatro coleções da Simone (doc-A a doc-D, 189 arquivos)
mais 5 arquivos `call-graph.*` na raiz de `docs/` -- 194 arquivos, 90.816 linhas, commit `e5aff94`.

Levantado o material semiótico já existente que alimentaria a seção 1: `docs/foundations.md`,
`docs/concepts.md`, `docs/reference/agents.md`, `docs/doc-D/foundations/*`,
`docs/doc-A/explanation/semiotic-engineering.html`.

Achado relevante: `open-seja/product-design/` só continha `conventions.md`. Não existe
`product-design-as-intended.md` neste repositório -- o SEJA nunca se documentou a si mesmo no
formato que impõe aos outros projetos.

### 2. Notas da conversa com o Anax

**Usuário**: nós desenhamos o que é ser dev atualmente, vindo de um desenho do artigo do abrahao.
temos agora os devs falando com o robo, que produz código, apoiado nas ferramentas. também temos
os User ou citzen devs, que não sabem ler código, mas tem uma intenção e esperam que a
computabilidade do robo gere algo que traduza do código que foi implementado para uma linguagem
adequada a ele. o harnerss, e seus agentes precisam se adequar ao qual dev estão assistindo. uma
hipótese é que podemos ter uma escala que vai do user/citzen dev até o power dev especialista em
tecnologia. uma outra hipotese é que o seja pode ser uma boa ferramenta para embasar a
computabilidade dos agentes a medida que eles transformam intenções em código executável. O agente
de workflow possui um orquestrados que pode chamar diversos agentes para compor o que é necessário
para o agente de IA dev assista o humano no desenvolvimento de software.

**Agente**: Escrita a seção 1 completa em `product-design/seja-as-intended.md` (commit `1480dee`),
ancorada em `docs/foundations.md` e no catálogo real de agentes do harness.

Registrados `P-001` a `P-007` como princípios, `H-001` a `H-004` como hipóteses abdutivas com
condições de refutação, e `Q-001` a `Q-006` como questões abertas.

Achado principal apresentado ao usuário: a escala citizen&#8596;power é um **terceiro eixo de
audiência**, ortogonal aos dois que o SEJA já tem (`BLD/SHP/GRD` por função, `L1-L3` por
senioridade). Ela classifica por *literacia de código*, e é o único dos três que determina em que
sistema de signos a mensagem de volta pode ser escrita. Consequência enunciada: para o citizen dev,
o código não pode ser a mensagem.

Duas decisões declaradas como reversíveis: arquivo separado em vez do formato §0-§17 do template
(`Q-006`), e pt-BR em vez de en-US (`Q-005`). Tensão registrada: `product-design-as-intended.md` é
classificado `Human (markers)` -- agentes não escrevem prosa nele.

`Q-001` deixada explicitamente em aberto: a referência bibliográfica do artigo do Abrahão não foi
inventada.

Pergunta devolvida ao usuário: `Q-003` (como o harness detecta a posição do humano na escala) foi
apresentada como a mais urgente para destravar implementação.

### 3. Decisão sobre Q-003

**Usuário**: vamos deixar como questão em aberto

**Agente**: `Q-003` marcada como **deliberadamente sustentada em aberto**, e não meramente sem
resposta (commit `8fc7a32`). Razão de dependência registrada no documento: não se decide *como
detectar* a posição de alguém numa escala cujos pontos ainda não foram definidos, e a granularidade
é justamente o que `Q-002` mantém aberto. Fixar um mecanismo de detecção agora congelaria por via
indireta uma resposta a `Q-002` que ainda não existe.

Consequência: `H-003` permanece como leitura, sem implementação. Ordem de resolução fixada:
`Q-002` antes de `Q-003`.

### 4. Incorporação dos desenhos

**Usuário**: adicionei aos docs, tambem os desenhos que fiz com o anax do design do software
project e do harnerss, que ilustram a as notas com a conversa com o anax desta sessao

**Agente**: Lidos os dois PNGs (com ampliação por região para leitura confiável), vinculados à
seção 1 e documentados no `Apêndice B` (commit `09219a0`). Convenção de leitura adotada a partir do
próprio traço: **branco = arranjo herdado, vermelho = acrescentado na sessão**.

O que os desenhos acrescentaram:

- **`P-002a` (correção)**: a Figura 1 mostra duas setas entrando no `</>` -- uma do robô, outra do
  lado humano. O robô não substituiu o time na autoria do código; somou-se a ele. O esquema linear
  `dev -> robô -> código` que eu havia escrito é o caminho novo, não o único. Levanta `Q-007`:
  quando dois prepostos escrevem no mesmo texto, de quem é a voz que o leitor está lendo?
- **Reformulação de `Q-003`**: a escala está desenhada sob a população inteira de devs, não anexada
  a um indivíduo. Talvez a pergunta certa seja "como o projeto declara a distribuição de literacia
  do seu time?".
- **O harness incide de fora**: a seta que alimenta `Convenções/Design/Intenção` atravessa a
  fronteira da caixa "Projeto".
- **`P-003` e `H-004` já estavam desenhadas** antes de serem argumentadas: o `LN` é bidirecional
  por traço, e `User Dev | Power Dev` são cabeçalho *sobre* o `Agent WF`, não conteúdo dele.
- **A pilha é `Docs -> Harness -> LLM`**, e a caixa `Docs (O que é o SEJA)` contém exatamente o
  índice da seção 1.
- **Divergência `Q-008`**: o `Agent WF` lista um ciclo reduzido (`Research -> Plan -> Implement ->
  Reflect`), sem `/critique`, que é o portão do único invariante rígido do harness (`P-005`).

Abertas `Q-007` a `Q-010`. Nenhuma resolvida pelo agente.

### 5. Geração deste pacote de revisão

**Usuário**: /document o que foi decidido aqui e a informação condensada sobre os docs gerados para
o anax revisar

**Agente**: Tipo inferido `ddr` (as decisões são a espinha), entregue como pacote único de revisão
em vez de arquivos DDR fragmentados, porque o pedido é uma coisa só para o Anax ler.

Gerado inline em vez de via agente `document-generator`: o escopo é "o que foi decidido *aqui*", e
um agente frio não teria como reconstruir as decisões desta sessão nem seus porquês.

Saída: `docs/revisao-anax-2026-08-26.md`, com (1) as dez questões abertas em ordem de quanto
destravam, (2) `D-1` a `D-5` em formato DDR com consequências e alternativas rejeitadas, (3) as
duas divergências, (4) o inventário condensado dos docs gerados, (5) o estado do repositório.
Publicado também como página para leitura remota, com os dois desenhos embutidos.

---

## Decisões registradas nesta sessão

| ID | Decisão | Status |
|---|---|---|
| `D-1` | Registrar as duas hipóteses como abdutivas, não como decisões | Aceita |
| `D-2` | Escrever em arquivo separado, não no `product-design-as-intended.md` | Aceita, reversível (`Q-006`) |
| `D-3` | Preservar notas verbatim e leitura dos desenhos em apêndices | Aceita |
| `D-4` | Sustentar `Q-003` deliberadamente em aberto | Aceita (determinação do usuário) |
| `D-5` | Escrever em pt-BR | Aceita, provisória (`Q-005`) |

## Questões que seguem abertas

`Q-001` referência do Abrahão &middot; `Q-002` granularidade e ortogonalidade da escala &middot;
`Q-003` detecção da posição (sustentada) &middot; `Q-004` forma da retradução &middot;
`Q-005` idioma &middot; `Q-006` relação com o template §0-§17 &middot;
`Q-007` autoria dupla sobre o código &middot; `Q-008` ciclo reduzido do `Agent WF` &middot;
`Q-009` duplicidade do orquestrador &middot; `Q-010` elemento não identificado na Figura 1
