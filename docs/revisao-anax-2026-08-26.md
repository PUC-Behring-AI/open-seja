# Revisão -- SEJA as-intended, sessão de 2026-08-26

- **Para**: Anax
- **De**: Andrey
- **Branch**: `seja-intention-docs` (4 commits, não mergeada em `main`)
- **Artefato principal**: `product-design/seja-as-intended.md` (607 linhas)
- **Escopo**: seção 1 -- Princípios da engenharia semiótica

---

## Sumário

Fechei a seção 1 do documento de intenção do SEJA a partir das notas da nossa conversa
e dos dois desenhos. Ela tem 8 princípios (`P-001` a `P-007`, mais `P-002a`), 4 hipóteses
registradas como abdutivas (`H-001` a `H-004`) e 10 questões abertas (`Q-001` a `Q-010`).

Duas coisas exigem sua atenção antes de a seção 2 começar: **`Q-002`**, porque ela trava
`Q-003` e a operacionalização inteira da escala; e **`Q-008`**, uma divergência entre o
seu desenho do `Agent WF` e o invariante rígido do harness.

---

## 1. O que precisa da sua revisão

Em ordem de quanto destravam.

| # | Questão | O que trava | O que preciso de você |
|---|---|---|---|
| `Q-002` | A escala citizen↔power é ortogonal a BLD/SHP/GRD e L1-L3, ou colapsa? Quantos pontos discretos precisa? | `Q-003` e toda a operacionalização de `H-001` | Uma posição: quantos pontos, e se o eixo é mesmo independente |
| `Q-008` | Seu `Agent WF` lista `Research → Plan → Implement → Reflect`. Faltam `/design`, `/critique`, `/document`, `/communicate` | Coerência entre o desenho e `P-005` | Foi simplificação do desenho ou proposta deliberada de ciclo curto? |
| `Q-001` | Referência exata do artigo do Abrahão | Citação de `P-002` | Autor(es), título, veículo, ano |
| `Q-010` | O círculo com figura no alto à esquerda da Figura 1 | Leitura completa do desenho | O que ele representa? Não consegui identificar |
| `Q-009` | "Orquestrador" aparece duas vezes na Figura 2 | Precisão de `H-004` | Dois níveis de orquestração, ou ênfase? |
| `Q-007` | Duas vias de autoria escrevem no mesmo `</>` | `P-002a` | O harness precisa distinguir código de autoria humana de código do preposto? |
| `Q-004` | A retradução obrigatória é novo artefato, novo modo de `/explain`, ou etapa do `post-skill`? | Implementação de `P-003` | Pode esperar a seção 2 |
| `Q-005` | Documento fica em pt-BR ou vai para en-US junto com `docs/`? | Publicação | Pode esperar |
| `Q-006` | Relação com o `product-design-as-intended.md` no formato §0-§17 | Estrutura | Ver `D-2` abaixo |
| `Q-003` | Como o harness detecta a posição do humano na escala? | -- | **Nada. Sustentada em aberto de propósito** (ver `D-4`) |

---

## 2. Decisões tomadas

Formato DDR. Todas reversíveis.

### D-1: Registrar as duas hipóteses como abdutivas, não como decisões

- **Status**: Aceita
- **Data**: 2026-08-26

**Contexto.** Suas notas trazem duas afirmações explicitamente marcadas como hipótese
(a escala; o SEJA embasando a computabilidade). O documento precisava acomodá-las sem
promovê-las a design assentado.

**Decisão.** Numerá-las `H-NNN`, mantê-las separadas dos princípios `P-NNN`, e exigir de
cada uma **o que a confirmaria e o que a refutaria**.

**Consequências.**
- `+` Coerente com a postura que o próprio SEJA declara: abdução peirciana, leitura
  provisória até evidência melhor (`docs/foundations.md`).
- `+` Impede que uma hipótese vire premissa por esquecimento.
- `-` Torna o documento mais lento de ler do que uma especificação afirmativa.

### D-2: Escrever em arquivo separado, não no `product-design-as-intended.md`

- **Status**: Aceita, reversível (`Q-006`)
- **Data**: 2026-08-26

**Contexto.** O template do harness tem esqueleto fixo (`§0 Planned Changes`,
`§1 Platform Purpose`, `§2 Entity Hierarchy`, ... `§17`), moldado para produto: hierarquia
de entidades, modelo de permissões, jornadas. A seção 1 que você pediu é fundamentação
teórica -- outro nível de abstração.

**Decisão.** Escrever em `product-design/seja-as-intended.md`, com estrutura própria.

**Consequências.**
- `+` A estrutura que você definiu (1.1 / 1.2 / 1.3) fica intacta.
- `+` Não conflita com os validadores do harness.
- `-` Existem agora dois documentos "as-intended" possíveis, e o canônico não está decidido.
- `0` Rota de fusão registrada: a seção 1 viraria base de `§1 Platform Purpose` e
  `§3 Domain-Specific Concepts`, e as hipóteses migrariam para `## Decisions`.

**Alternativa rejeitada 01.** Escrever direto no `product-design-as-intended.md`.
- `+` Um só documento canônico, validado pelo harness.
- `-` **Deformaria seu outline para caber num esqueleto de produto.**
- `-` O arquivo é classificado `Human (markers)`: agentes não escrevem prosa nele, e o
  `check_human_markers_only.py` rejeitaria o commit. Adotá-lo como canônico exige que a
  autoria da prosa passe por um humano.

### D-3: Preservar as notas e a leitura dos desenhos em apêndices

- **Status**: Aceita
- **Data**: 2026-08-26

**Contexto.** As notas da conversa são fonte primária. A seção 1 é interpretação delas.
Misturar as duas apagaria a distinção.

**Decisão.** `Apêndice A` guarda suas notas **verbatim**, sem edição. `Apêndice B` faz a
leitura elemento a elemento dos desenhos, usando a convenção do próprio traço:
**branco = arranjo herdado, vermelho = acrescentado na sessão.**

**Consequências.**
- `+` Dá para auditar a interpretação contra a fonte.
- `+` A convenção de cor separa o que veio do Abrahão do que veio da conversa.
- `-` Repete conteúdo entre corpo e apêndice.

### D-4: Sustentar `Q-003` deliberadamente em aberto

- **Status**: Aceita
- **Data**: 2026-08-26

**Contexto.** Eu havia apontado `Q-003` (como o harness detecta a posição do humano na
escala) como a mais urgente para destravar implementação. Você determinou deixá-la aberta.

**Decisão.** Registrá-la como **sustentada em aberto por decisão**, com a razão de
dependência explícita, e não como pendência esquecida.

**Razão registrada.** Não se decide *como detectar* a posição de alguém numa escala cujos
pontos ainda não foram definidos. A granularidade é justamente o que `Q-002` mantém
aberto. Fixar um mecanismo de detecção agora congelaria por via indireta uma resposta a
`Q-002` que ainda não temos.

**Consequências.**
- `+` `H-003` permanece como leitura, sem implementação -- ninguém vai codificar a
  variação do ciclo enquanto a escala não tiver pontos.
- `+` Um `/pending` futuro não vai tratar isso como omissão.
- `0` Ordem de resolução fica fixada: `Q-002` antes de `Q-003`.

### D-5: Escrever em pt-BR

- **Status**: Aceita, provisória (`Q-005`)
- **Data**: 2026-08-26

**Contexto.** `docs/` inteiro está em en-US e o SEJA é publicado publicamente. A conversa
de design, porém, corre em pt-BR.

**Decisão.** pt-BR, por ser a língua de trabalho do design.

**Consequências.**
- `-` Descasa do resto de `docs/`; uma tradução ficará pendente se o documento for público.

---

## 3. Divergências encontradas

Duas coisas em que as fontes não fecham entre si. Nenhuma foi resolvida por mim.

### 3.1 O desenho corrigiu as notas (`P-002a`)

As notas dizem: *"os devs falando com o robô, que produz código"*. Eu escrevi `P-002`
como `dev → robô → código`.

**A Figura 1 mostra duas setas entrando no `</>`**: uma vinda do robô, outra vinda do lado
humano. O robô **não substituiu** o time na autoria do código -- somou-se a ele. O esquema
linear é o caminho *novo*, não o único.

Acrescentei `P-002a` registrando isso, e a pergunta que o esquema linear escondia: quando
dois prepostos escrevem no mesmo texto, de quem é a voz que o leitor está lendo? (`Q-007`).

### 3.2 O `Agent WF` é mais curto que o ciclo canônico (`Q-008`)

O harness tem um único invariante rígido, `P-005`: **validar antes de comunicar**.
`/critique` sempre precede `/document` e `/communicate`.

O `Agent WF` da Figura 2 lista `Orquestrador`, `Research`, `Plan`, `Implement`, `Reflect`.
Faltam `/design`, `/critique`, `/document` e `/communicate`. Como `/critique` é o portão
desse invariante, a ausência não é cosmética: ou o desenho simplificou, ou está propondo
deliberadamente um ciclo mais curto -- e nesse caso colide com `P-005`.

---

## 4. Docs gerados

### 4.1 Coleções da Simone (commit `e5aff94`)

Quatro variantes editoriais da mesma documentação do SEJA. Nenhuma foi editada -- entraram
como recebidas, menos 189 arquivos `:Zone.Identifier` (lixo de download do WSL).

| Coleção | Arquivos | Título | Estrutura | Status |
|---|---|---|---|---|
| `docs/doc-A` | 50 | SEJA Documentation -- Reading Map | Diátaxis puro: `explanation/`, `how-to/`, `reference/`, `tutorials/` | published |
| `docs/doc-B` | 35 | System-Isomorphic Edition | Volumes e capítulos espelhando o próprio sistema (`vol1/`..`vol5/`) | published |
| `docs/doc-C` | 62 | Audience-Routed Collection | Núcleo comum + trilhas Practitioner / Architect / Scholar | published |
| `docs/doc-D` | 42 | (sem subtítulo) | Camadas: `foundations/`, `design-layer/`, `execution-layer/`, `onboarding/` | **draft** |

Mais 5 arquivos `docs/call-graph.*` na raiz. **Atenção**: eles **diferem** dos
`docs/concepts/call-graph.*` já versionados. Mantive os dois; falta decidir qual é o
canônico.

### 4.2 Documento de intenção (commits `1480dee`, `8fc7a32`, `09219a0`)

`product-design/seja-as-intended.md`, 607 linhas.

**1.1 Conceitos fundamentais**

| ID | Conteúdo |
|---|---|
| `P-001` | O artefato é uma mensagem, não um produto. Preposto do designer (de Souza 2005) |
| `P-002` | A relação dev↔código passou a ser mediada por um agente que produz código |
| `P-002a` | Ressalva da Figura 1: duas vias concorrentes de autoria sobre o mesmo artefato |
| `H-001` | Escala citizen↔power dev, ancorada em **literacia de código** |
| `P-003` | Metacomunicação em dois sentidos: a retradução como obrigação constitutiva |
| `P-004` | Os marcadores do SEJA como sistema de significação projetado (Eco 1976) |
| `H-002` | Computabilidade da intenção: signo fixo + rastreabilidade + deriva |

**1.2 Fluxos de trabalho**

| ID | Conteúdo |
|---|---|
| `P-005` | Ciclo canônico e o invariante "validar antes de comunicar" |
| -- | Par as-intended / as-coded; a deriva como cidadã de primeira classe |
| `H-003` | Variação da superfície de contato ao longo da escala (tabela por polo) |
| -- | Os três registros de Schön e a abdução de Peirce |

**1.3 Agentes principais**

| ID | Conteúdo |
|---|---|
| `P-006` | Skill orquestra; agente executa |
| `P-007` | Três papéis: avaliadores, geradores, executores (catálogo real do harness) |
| `H-004` | O orquestrador como lugar onde a adequação ao dev se realiza |

Mais `Apêndice A` (notas verbatim), `Apêndice B` (leitura dos desenhos), referências
e CHANGELOG.

### 4.3 Desenhos (commit `09219a0`)

| Arquivo | Figura | Onde está referenciado |
|---|---|---|
| `docs/design-software-project.png` | Figura 1 | §1.1.2, lido em `B.1` |
| `docs/designt-harnerss.png` | Figura 2 | §1.3.3, lido em `B.2` |

Três achados da leitura, além de `P-002a`:

- **A escala está desenhada sob a população inteira de devs**, não anexada a um indivíduo.
  Isso reformula `Q-003`: talvez a pergunta certa não seja "como detectar a posição deste
  usuário?", e sim "como o projeto declara a distribuição de literacia do seu time?".
- **O harness incide de fora.** A seta vermelha grossa que alimenta
  `Convenções/Design/Intenção` atravessa a fronteira da caixa "Projeto".
- **A pilha desenhada é `Docs → Harness → LLM`**, e a caixa `Docs (O que é o SEJA)` contém
  exatamente o índice da seção 1. O documento não é interpretação do desenho: é o
  preenchimento de uma caixa que o desenho já tinha reservado.

E `P-003` e `H-004` já estavam desenhadas antes de eu as argumentar: o `LN` é bidirecional
por traço, e `User Dev | Power Dev` são cabeçalho **sobre** o `Agent WF`, não conteúdo dele.

---

## 5. Estado do repositório

```
09219a0  docs(as-intended): incorpora os desenhos de origem da sessão com o Anax
8fc7a32  docs(as-intended): sustenta Q-003 deliberadamente em aberto
1480dee  docs(as-intended): §1 Princípios da engenharia semiótica
e5aff94  docs: adiciona coleções de documentação da Simone (doc-A..doc-D)
```

Branch `seja-intention-docs`, a partir de `main` em `056a6de`. Não mergeada.

**Pendências de higiene** (não tratadas, fora do escopo desta sessão):

- O repositório **não tem `.gitignore`**. `__pycache__/` e `_output/conversation-trace.jsonl`
  aparecem sujando o `git status`.
- O arquivo `designt-harnerss.png` tem dois erros de digitação no nome.
- Duplicidade `docs/call-graph.*` vs `docs/concepts/call-graph.*`.

---

> Gerado por `/document` em 2026-08-27 00:39 UTC. Fonte: sessão de trabalho de
> 2026-08-26 sobre `product-design/seja-as-intended.md`.
