---
designer_description: "Before /plan writes any plan for code, I'm the protocol it follows to interview you: a few short questions at a time, your words recorded as they are, each requirement written back with one sentence that says how you will see it working, and a stop rule a tool checks -- so I only go on after you approve a list you can read."
---

# GENERAL - GRILL PHASE

> Protocolo normativo da fase grill do `/plan` (plan-000009; item 3 do roadmap-000006). Detalha CYC-002, CYC-006, CYC-007, CYC-008 e CYC-013 de `.claude/references/general/extended-cycle-contract.md`. Esquema do `intent.md`: `.claude/references/template/feature-layout.md` (mínimo do plan-000007) mais as extensões deste arquivo (GRL-005); modelo completo em `.claude/references/template/intent.md`. Verificador: `.claude/skills/scripts/check_intent.py`.
>
> Idioma: pt-BR (protocolo), identificadores em en-US. Marcação: `[default; aceito 2026-10-06]` indica uma decisão pendente do plan-000009 que o designer aceitou no default.
>
> Cada regra tem identificador estável `GRL-NNN`, campo **Quem decide** e campo **Critério de aceitação**. Outros planos citam a regra em `Traces:`.

## Constantes

```
GRILL_MAX_ROUNDS = 5
GRILL_MAX_QUESTIONS_PER_ROUND = 4
GRILL_DIMENSIONS = (quem, o_que, gatilho, resultado, nao_faz, erros_limites)
GRILL_MAX_REQS = 12
MAX_SENTENCE_WORDS = 25
MAX_SENTENCES_PER_PARAGRAPH = 6
```

`GRILL_MAX_ROUNDS` e `GRILL_MAX_QUESTIONS_PER_ROUND` são palpite a calibrar no piloto (plan-000016); um projeto pode mudá-los em `product-design/conventions.md`. `MAX_SENTENCE_WORDS` e `MAX_SENTENCES_PER_PARAGRAPH` são os valores do §10 do as-intended para a voz controlada. O verificador lê as mesmas constantes.

---

## Regras

### GRL-001 -- Entrada e saída

- **Entrada**: o brief, recebido como veio (verbatim), e `product-design/product-design-as-intended.md` (CYC-007).
- **Saída**: `features/<slug>/intent.md`. Tarefa sem código não cria pasta (GRL-012).
- A fase nunca é pulada (CYC-002). Ela pode durar uma rodada quando o brief já traz intenção detalhada.
- O `intent.md` nasce na primeira rodada com `status: grilling` e cresce a cada rodada. Se a sessão cair, o arquivo guarda o que já foi dito (git é a recuperação).
- Ao criar a **primeira** pasta `features/<slug>/` do projeto, a grill escreve `features/adoption.json` (`{"schema_version": 1, "adopted_at": "AAAA-MM-DD"}`) se ele não existe, e nunca o reescreve: é a marca da leitura reversa do relatório (emenda 000015, CYC-034).

- **Quem decide**: designer (CYC-002); o `/plan` conduz.
- **Critério de aceitação**: depois da primeira rodada de uma feature com código existe `features/<slug>/intent.md` com `status: grilling`; ao fim da fase o mesmo arquivo está em `status: approved` ou a decisão voltou ao citizen (GRL-007).

### GRL-002 -- O slug `[default; aceito 2026-10-06]` (decisão pendente 5 = A)

O agente propõe um slug em kebab-case (`[a-z0-9]+(-[a-z0-9]+)*`) na primeira rodada, e o citizen confirma. O slug vira nome de pasta e parte de cada `REQ-<slug>-NNN`; ele nunca é renomeado. Se o brief já traz um nome, o agente o usa como base. Se `features/<slug>/` já existe, a grill não grava: ela pergunta se é a mesma feature (reentrada, GRL-011) ou outra (novo slug).

- **Quem decide**: o citizen confirma; o agente propõe.
- **Critério de aceitação**: o slug do frontmatter casa com a regex; todo `REQ-` do arquivo usa esse slug; nenhuma grill grava sobre pasta existente sem a resposta "mesma feature".

### GRL-003 -- Conduta da entrevista

- Rodadas de até `GRILL_MAX_QUESTIONS_PER_ROUND` perguntas.
- Uma ideia por pergunta. Pergunta aberta antes de pergunta fechada.
- A ordem segue as dimensões de GRL-004; a rodada pula a dimensão que o brief já respondeu.
- O agente **nunca** preenche uma resposta que o citizen não deu. Quando o citizen trava ou diz "não sei", o agente propõe um default e pergunta uma vez. O default entra em "Premissas" com `Confirmado: não` até o citizen confirmar (GRL-012, linha "não sei").
- Cada resposta é gravada verbatim em "Nas suas palavras", com índice `A<n>` (GRL-005).
- Ao fim de cada rodada o agente roda `check_intent.py` e decide pelo resultado, não por impressão (GRL-006).

- **Quem decide**: o citizen responde; o agente pergunta e grava.
- **Critério de aceitação**: nenhuma rodada registrada tem mais de 4 perguntas; toda resposta citada num REQ existe como `A<n>` ou `F<n>`; toda resposta proposta pelo agente aparece como premissa, nunca como resposta do citizen.

### GRL-004 -- As seis dimensões e as perguntas-modelo

Cada dimensão tem uma linha na tabela "Dimensões" do `intent.md`. As perguntas abaixo são modelo; o agente adapta o substantivo ao domínio e mantém a forma curta.

| Dimensão (id) | Pergunta-modelo pt-BR | Pergunta-modelo en-US |
|---|---|---|
| quem (`quem`) | "Quem vai usar isto?" e, em seguida, "O que essa pessoa já sabe fazer sem ajuda?" | "Who will use this?" and then "What can this person already do without help?" |
| o que faz (`o_que`) | "O que essa pessoa quer conseguir fazer?" | "What does this person want to be able to do?" |
| gatilho (`gatilho`) | "Quando isso começa? O que a pessoa faz primeiro?" | "When does this start? What does the person do first?" |
| resultado (`resultado`) | "Quando der certo, o que você vê na tela?" | "When it works, what do you see on the screen?" |
| não faz (`nao_faz`) | "O que isto não deve fazer, mesmo que pareça útil?" | "What should this not do, even if it looks useful?" |
| erros e limites (`erros_limites`) | "O que acontece quando algo dá errado? Há algum limite de tempo ou de quantidade?" | "What happens when something goes wrong? Is there a limit of time or amount?" |

A sub-pergunta "o que essa pessoa sabe fazer" (emenda 000009) existe para o `/plan` e o specify não pressuporem um usuário que lê código ou conhece o sistema. A resposta entra na linha `quem`.

Uma dimensão pode ficar sem requisito quando o citizen a declara fora: a célula "Resposta" recebe `fora do escopo: <motivo do citizen>`.

- **Quem decide**: o citizen responde ou declara fora do escopo; o agente não declara por ele.
- **Critério de aceitação**: a tabela "Dimensões" tem as seis linhas; nenhuma célula "Resposta" está vazia; toda marca `fora do escopo:` traz um motivo (P1, `check_intent.py`).

### GRL-005 -- O `intent.md` da grill: extensões ao esquema mínimo `[default; aceito 2026-10-06]` (decisão pendente 1 = B)

O esquema mínimo do plan-000007 (`feature-layout.md`: `slug`, `status`, "Nas suas palavras", "Requisitos" com REQ / Texto / Critério, "Fora do escopo", "Premissas") continua válido. A grill escreve um **superconjunto** dele; nenhum campo do mínimo é removido ou renomeado. As extensões:

| Onde | Extensão | Papel |
|---|---|---|
| frontmatter | `approved_at` (UTC, `YYYY-MM-DDTHH:MMZ`), `approved_by` | registro da aprovação (GRL-008) |
| frontmatter | `serve: [<ID>, ...]` (emenda 000009) | liga a feature a `REQ-MC-NNN`, `JM-TB-NNN` ou `D-NNN` do as-intended; permite a leitura reversa "intenção sem feature" do plan-000014; lista vazia é permitida |
| "Nas suas palavras" | frases do pedido indexadas `F1..Fn`; respostas da entrevista indexadas `A1..An` (emenda 000009) | cada REQ, item de "Fora do escopo" e premissa cita o índice de onde veio; as frases `F` sem REQ ativo e sem "Fora do escopo" são o degrau zero (D0, DRM-010) |
| "Requisitos" | colunas `Tipo`, `Nas suas palavras`, `Para que` (emenda 000009), `rev`, `Estado`; a coluna `Texto` do mínimo chama-se `Requisito` (os dois nomes são aceitos) | origem, tipo, propósito e ciclo de vida de cada REQ |
| seção nova | "Dimensões" (GRL-004) | regra de parada P1 |
| seção nova | "Modelo e termos" (emenda 000009) | os substantivos do domínio no sentido do citizen; o plan-000010 avisa quando um step de cenário usa um substantivo que não está aqui |
| seção nova | "Perguntas abertas" | regra de parada P3 |
| seção nova | "Mudanças" | histórico de reentrada (GRL-011) |
| "Premissas" | tabela com `Premissa`, `Fonte`, `Confirmado: sim \| não` | regra de parada P3 |

Ordem das seções no arquivo: Nas suas palavras, Requisitos, Dimensões, Modelo e termos, Fora do escopo, Premissas, Perguntas abertas, Mudanças.

**Índice do pedido.** O agente divide o brief em frases (ponto final, ponto de interrogação, ponto de exclamação ou quebra de item de lista) e numera `F1`, `F2`, ... na ordem do texto, sem mudar uma palavra. O índice é fixado na primeira rodada e nunca renumerado. Um pedido novo na reentrada continua a numeração.

**Nota C1 (emenda 000009).** O pedido verbatim vai para `features/<slug>/intent.md`, que é versionado com o código do projeto e lido por quem lê o repositório. Antes de gravar a primeira rodada, a grill avisa o citizen e oferece trocar nomes de pessoa, de cliente, de parceiro ou dados sensíveis por um marcador (`[nome omitido]`). A troca é escolha do citizen e fica registrada em "Mudanças". A grill não decide sozinha o que é sensível.

- **Quem decide**: designer (decisão pendente 1); o citizen decide a troca de C1.
- **Critério de aceitação**: um `intent.md` mínimo do plan-000007 passa em `check_intent.py` sem `--require-approved`; um `intent.md` da grill tem as extensões acima e passa com `--require-approved` depois da aprovação; o aviso de C1 aparece na primeira rodada.

### GRL-006 -- Regra de parada

A intenção está "detalhada o bastante" quando **todas** as condições valem. `check_intent.py` é o juiz: PASS é resultado de ferramenta, não frase (T1).

| # | Condição | Como `check_intent.py` confere |
|---|---|---|
| P1 | Cobertura das 6 dimensões: cada uma tem resposta, ou a marca `fora do escopo: <motivo do citizen>` | tabela "Dimensões" com as seis linhas, nenhuma célula vazia, motivo presente |
| P2 | Todo REQ ativo tem critério observável na forma "Quando <ação de quem usa>, o sistema <resultado que se vê>" ("When ..., the system ..." em en-US) | regex da forma; palavra vaga (`VAGUE_WORDS`) sem número no critério é erro |
| P3 | Nenhuma pergunta aberta e nenhuma premissa sem confirmação | "Perguntas abertas" vazia ou `nenhuma`; toda premissa com `Confirmado: sim` |
| P4 | IDs `REQ-<slug>-NNN` com o slug do frontmatter, únicos, contíguos de 001 a N, nunca reusados (retirado conta como usado); `rev` inteiro a partir de 1; REQ com `rev` > 1 ou `retirado` aparece em "Mudanças" | parse da tabela |
| P5 | Todo REQ ativo tem origem: na coluna "Nas suas palavras", índice `F<n>`/`A<n>` existente, citação entre aspas ou `derivado de: REQ-<slug>-NNN` existente; e tem texto na coluna "Requisito" | parse da tabela e do índice |
| P6 | Aprovação humana registrada: `status: approved` com `approved_at` e `approved_by`, escritos só depois de P1 a P5 passarem | frontmatter |

Sem `--require-approved`, o verificador avalia o que existe no arquivo (uma intenção em `grilling` é incompleta por definição); um arquivo só com o esquema mínimo do plan-000007 recebe só as regras do mínimo e um aviso de que a regra de parada não foi avaliada. Com `--require-approved`, P1 a P6 valem por inteiro e as seções da regra de parada precisam existir (Nas suas palavras, Requisitos, Dimensões, Premissas, Perguntas abertas); "Modelo e termos" ausente gera aviso, e "Mudanças" só é exigida quando algum REQ tem `rev` > 1 ou está `retirado`. Sem argumento, o verificador varre `features/*/intent.md`: intenção aprovada com `error` faz a varredura falhar; intenção em `grilling` só é relatada.

`VAGUE_WORDS` (pt-BR e en-US): rápido, rapidamente, fácil, facilmente, bom, boa, simples, seguro, segura, adequado, adequada, intuitivo, intuitiva, amigável, eficiente, robusto, melhor, etc, fast, quick, easy, good, simple, secure, intuitive, friendly, efficient. A palavra passa quando o critério tem um número ("responde em até 2 segundos").

- **Quem decide**: o verificador decide P1 a P5; o citizen decide P6.
- **Critério de aceitação**: `check_intent.py <intent.md> --require-approved --strict` sai 0 só quando P1 a P6 valem; cada condição tem teste positivo e negativo em `test_check_intent.py`.

### GRL-007 -- Teto de rodadas e devolução da decisão `[default; aceito 2026-10-06]` (decisão pendente 2 = B)

Se depois de `GRILL_MAX_ROUNDS` rodadas alguma condição de P1 a P5 ainda falha, a grill **para** e devolve a decisão ao citizen, com AskUserQuestion (C4):

- **Continuar** mais uma rodada. Recommended when falta uma resposta só e o citizen a sabe. NOT recommended when a mesma condição falhou em três rodadas seguidas.
- **Aceitar como premissa marcada** o que falta. Recommended when o ponto não muda o que se vê na tela. NOT recommended when o ponto decide o resultado que se vê (P2).
- **Arquivar o tema**. Recommended when o citizen ainda não sabe o que quer. NOT recommended when só falta um detalhe.

A grill nunca inventa resposta para sair do teto. "Aceitar como premissa" grava a premissa com `Confirmado: sim` e a fonte `teto` em "Premissas", e a escolha em "Mudanças".

- **Quem decide**: o citizen.
- **Critério de aceitação**: nenhuma grill registrada passa de 5 rodadas sem uma das três escolhas gravada em "Mudanças".

### GRL-008 -- Aprovação

Quando `check_intent.py` não devolve `error`, o agente mostra o resumo em voz controlada (GRL-010):

1. a lista de requisitos ativos, cada um com o critério em uma frase; o texto vem primeiro e o ID aparece pequeno, ao fim da linha;
2. a lista do que não será feito ("Fora do escopo");
3. as premissas que o citizen confirmou.

O citizen escolhe por AskUserQuestion (C4):

- **Aprovar**. Recommended when cada requisito diz algo que você reconhece. NOT recommended when algum requisito surpreendeu você.
- **Ajustar**. Recommended when um requisito está quase certo. NOT recommended when o tema inteiro mudou (então Descartar).
- **Descartar**. Recommended when o pedido mudou de natureza. NOT recommended when só falta um detalhe.

Só **Aprovar** grava `status: approved`, `approved_at` (UTC) e `approved_by: usuario`; o agente escreve esses campos, nunca o verificador. **Ajustar** abre mais uma rodada. **Descartar** mantém `status: grilling`, registra o motivo em "Mudanças" e encerra a fase sem plano. O specify recusa `intent.md` com outro status (CYC-008) e usa `check_intent.py --require-approved` como portão.

O resumo passa pelo teste da surpresa (CYC-014): cada linha diz algo que o citizen pode reconhecer como errado ("não é isso"). Percentual, contagem de condições ou "PASS" não entram no resumo do citizen; ficam para o power dev (CYC-013).

- **Quem decide**: o citizen.
- **Critério de aceitação**: todo `intent.md` com `status: approved` tem `approved_at` e `approved_by` (P6); nenhum resumo mostrado ao citizen traz número técnico.

### GRL-009 -- O que é um bom requisito `[default; aceito 2026-10-06]` (decisão pendente 3 = B)

Um bom requisito:

- é observável: diz o que quem usa vê ou recebe;
- tem um comportamento só;
- não traz solução técnica (nada de tabela, rota, framework ou nome de função);
- tem critério na forma "Quando <ação de quem usa>, o sistema <resultado que se vê>";
- tem "Para que": em uma frase, o que o citizen ganha com ele (emenda 000009). O "Para que" guarda o porquê que o `.feature` não representa (D-004).

Dois tipos: `comportamento` (o que o sistema faz) e `restrição` (desempenho, segurança, limite). A restrição também exige critério observável e ganha cenário no specify. O power dev pode acrescentar requisitos de tipo `restrição` com `derivado de:` ou com a própria resposta indexada. O D1 do plan-000008 conta os dois tipos igual.

Exemplos bons:

| Requisito | Critério |
|---|---|
| Você pode marcar uma conta como paga. | Quando você marca uma conta como paga, o sistema mostra a conta na lista de pagas. |
| Você recebe um aviso antes do vencimento. | Quando faltam 3 dias para o vencimento, o sistema mostra um aviso na tela inicial. |
| A lista abre sem espera longa (`restrição`). | Quando você abre a lista com 500 contas, o sistema mostra a lista em até 2 segundos. |

Exemplos ruins e o porquê:

| Requisito | Problema |
|---|---|
| O sistema deve ser rápido. | sem critério observável; "rápido" sem número (P2) |
| Gravar a conta na tabela `bills` com índice por data. | solução técnica, nada que quem usa veja |
| Você pode cadastrar, editar, apagar e exportar contas. | quatro comportamentos num requisito só |

- **Quem decide**: o agente reescreve; o citizen aprova (GRL-008).
- **Critério de aceitação**: todo REQ ativo tem `Tipo` igual a `comportamento` ou `restrição` (ou nenhum tipo, no esquema mínimo) e critério na forma de P2.

### GRL-010 -- Voz `[default; aceito 2026-10-06]` (decisão pendente 4 = B)

**Dentro da regra** (texto que o agente escreve para o citizen): perguntas, resumo da aprovação, colunas "Requisito", "Critério" e "Para que", respostas da tabela "Dimensões", itens de "Fora do escopo", premissas, sentidos em "Modelo e termos".

**Fora da regra**: citação verbatim do citizen (entre aspas, ou nas listas `F` e `A`), código, IDs, tabelas de código.

Regras mínimas, enquanto o lint de voz controlada (plano 000074 do ledger do pesquisador) não está no open-seja:

1. Frases de até `MAX_SENTENCE_WORDS` (25) palavras.
2. Até `MAX_SENTENCES_PER_PARAGRAPH` (6) frases por parágrafo ou célula.
3. Uma ideia por frase.
4. Termos fixos (glossário abaixo), um termo por conceito.
5. Aviso antes da instrução; imperativo nas instruções.

`check_intent.py` confere as regras 1 e 2 e devolve `warning` (nunca `error`). Sem o lint do 000074, a saída traz a ressalva `voz: não verificada` para as regras 3 a 5. Quando o lint existir, o verificador o chama e as constantes vêm de lá; o texto das regras não é copiado.

Glossário fixo de termos (pt-BR / en-US):

| Termo | Não usar | en-US |
|---|---|---|
| requisito | requirement, necessidade, regra | requirement |
| o que você vê | output, saída, retorno | what you see |
| fora do escopo | não-objetivo, backlog | out of scope |
| premissa | suposição, hipótese | assumption |
| pergunta aberta | pendência, TODO | open question |
| aprovar | validar, dar ok | approve |

- **Quem decide**: designer (decisão pendente 4).
- **Critério de aceitação**: `check_intent.py` devolve `warning` para frase de 26 palavras em "Requisito" e nada para citação de 40 palavras em "Nas suas palavras"; a saída traz `voz: não verificada` enquanto o lint do 000074 não existe.

### GRL-011 -- Reentrada e mudança depois da aprovação

`/plan --grill` sobre uma feature aprovada:

- `status` volta a `grilling`; `approved_at` e `approved_by` ficam até a nova aprovação sobrescrevê-los;
- REQ editado mantém o ID e sobe `rev`;
- REQ novo recebe o próximo número;
- REQ retirado fica na tabela com `Estado: retirado`; nunca é apagado, e o número nunca é reusado;
- cada mudança ganha uma linha em "Mudanças" (data, REQ, o que mudou, `rev`);
- a reaprovação (GRL-008) é exigida.
- depois de voltar o `status` a `grilling`, rodar `python .claude/skills/scripts/check_specify.py --reconcile <slug>` e dizer ao citizen, em uma frase, que os cenários aprovados voltaram a rascunho (emenda 000015, CYC-032).

Enquanto a reaprovação não vem, o D1 conta o REQ retirado como descoberto (plan-000008). Um `rev` novo marca os cenários do REQ como desatualizados até o specify reaprovar (lacuna para `drift-metric.md`, registrada no progress do plan-000009).

- **Quem decide**: o citizen (mudança e reaprovação).
- **Critério de aceitação**: depois da reentrada, os IDs continuam contíguos de 001 a N; todo REQ com `rev` > 1 ou `retirado` aparece em "Mudanças" (P4).

### GRL-012 -- Degradação

| Situação | O que a grill faz | Artefato |
|---|---|---|
| Feature com código (algum step terá `Tests:` não-N/A) | rodadas até P1 a P6 | `features/<slug>/intent.md` aprovado; plano v2 |
| Tarefa sem código (docs, pesquisa, harness, configuração) | entrevista **curta**: objetivo, resultado que se vê, o que não faz, critério de pronto; sem REQ IDs, sem pasta | seção `## Intenção` no próprio plano (4 linhas) e a linha `Specify: skipped -- <motivo>` (CYC-004); aprovação no mesmo AskUserQuestion do plano |
| Brief já detalhado (com requisitos ou critérios) | uma rodada de **confirmação**: o agente reescreve em voz controlada, aponta o que falta em P1 a P5 e pergunta só isso | mesmo `intent.md`; o brief inteiro indexado em `F<n>` |
| Brief grande demais (mais de `GRILL_MAX_REQS` requisitos prováveis) | propõe quebrar em duas features com slugs distintos antes de entrevistar | dois `features/<slug>/`; o roadmap fica com o orquestrador |
| Projeto sem `features/` ou plano v1 | a fase não muda o plano v1; quem não usa `features/` segue o fluxo antigo | nenhum; sem aviso de bloqueio |
| Citizen responde "não sei" | registra premissa com `Confirmado: não`, propõe um default e pergunta uma vez; sem confirmação, vira pergunta aberta e bloqueia P3 | linha em "Premissas" ou "Perguntas abertas" |
| Citizen muda a intenção depois de aprovada | GRL-011 | `intent.md` reaprovado |

A seção `## Intenção` da tarefa sem código tem quatro linhas, em voz controlada:

```markdown
## Intenção
- Objetivo: <uma frase>
- O que você vê no fim: <uma frase>
- Não faz: <uma frase>
- Pronto quando: <uma frase>
```

- **Quem decide**: o `/plan` classifica a tarefa; o designer pode contestar na revisão do plano.
- **Critério de aceitação**: um plano sem pasta de feature tem a seção `## Intenção` e a linha `Specify: skipped -- <motivo>`; um plano v1 antigo é lido pelo `/plan` sem mudança.

### GRL-013 -- O que a fase não faz

A fase grill **não**:

- escreve Gherkin (specify, plan-000011);
- valida `.feature` (plan-000010);
- decide o formato do plano (plan-000012; CYC-018);
- calcula divergência (plan-000014); ela só fornece o índice de frases que tira o D0 de `NM-SEM-INDICE-BRIEF`;
- muda portão, hooks, denies ou `settings` (S2).

- **Quem decide**: designer.
- **Critério de aceitação**: nenhum texto deste arquivo traz Gherkin executável, regra de validador de `.feature` ou fórmula de divergência; o diff do plan-000009 não toca arquivo de portão, hook ou `settings`.

### GRL-014 -- Interface `--grill` (implementa CYC-006 para a grill)

`/plan --grill [<slug>]` roda só a fase grill e para. Lê e escreve só `features/<slug>/intent.md`; nunca escreve plano, `.feature` nem `gate.json`. Reentrada é permitida (GRL-011). Sem `<slug>`, o agente propõe um (GRL-002). `--specify` deixou de ser reservada: o plan-000011 a implementa (`specify-phase.md`, SPC-016, passo 2c do `/plan`).

- **Quem decide**: designer (CYC-006).
- **Critério de aceitação**: depois de `/plan --grill`, o diff do projeto só toca `features/<slug>/intent.md`.

### GRL-015 -- Degrau zero: o índice do pedido como fonte

`check_intent.py --d0` lê o índice `F<n>` e lista as frases do pedido que não são citadas por REQ ativo nem por item de "Fora do escopo". Frase citada só por premissa entra na lista, marcada `só em premissa`. Sem índice, a saída é `não medido` com `NM-SEM-INDICE-BRIEF` (DRM-009). O D0 é leitura fora do vetor D, nunca portão (DRM-010): a lista não muda a regra de parada.

- **Quem decide**: designer (DRM-010); o verificador calcula.
- **Critério de aceitação**: num `intent.md` com índice, `--d0` lista exatamente as frases sem REQ ativo e sem fora-do-escopo; sem índice, devolve `NM-SEM-INDICE-BRIEF`; nenhum `error` vem do D0.

---

## Decisões pendentes do plan-000009 e o default adotado

| # | Decisão | Default adotado | Regra |
|---|---|---|---|
| 1 | Esquema extra do `intent.md` | B: este arquivo define as extensões; o mínimo do 000007 é subconjunto válido `[default; aceito 2026-10-06]` | GRL-005 |
| 2 | Teto de rodadas | B: 5 rodadas de até 4 perguntas; devolve a decisão `[default; aceito 2026-10-06]` | GRL-007 |
| 3 | Tipos de REQ | B: `comportamento` e `restrição` `[default; aceito 2026-10-06]` | GRL-009 |
| 4 | Dependência do 000074 | B: limites numéricos embutidos e ressalva `voz: não verificada` `[default; aceito 2026-10-06]` | GRL-010 |
| 5 | Quem escolhe o slug | A: o agente propõe, o citizen confirma `[default; aceito 2026-10-06]` | GRL-002 |
