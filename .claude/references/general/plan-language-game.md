---
designer_description: "Before /plan writes a plan, I don't interrogate you: I play a game with you. I tell short scenes of what you asked working, and of what it should not do, and you accept, refuse or fix each one. What you accepted becomes the requirements and use cases of the plan, what you refused becomes what I will not do, and your corrections are quoted as you said them."
---

# GENERAL - PLAN LANGUAGE GAME

> Protocolo normativo da entrevista do `/plan` (D-006). O jogo é dono da saída, da regra de parada e da aprovação. A saída vai para o próprio plano, nas seções definidas em `.claude/references/general/plan-intent-and-cases.md` (regras PIC); o verificador é `.claude/skills/scripts/check_plan_intent.py`.
>
> Idioma: pt-BR (protocolo), identificadores em en-US. Cada regra tem identificador estável `JDL-NNN`, campo **Quem decide** e campo **Critério de aceitação**. Outros planos citam a regra em `Traces:`.

## Por que um jogo, e não perguntas

Uma entrevista por perguntas ("Quem vai usar isto?", "O que isto não deve fazer?") espera que você já tenha a resposta em palavras. No jogo de linguagem (Wittgenstein), o sentido de uma palavra se fixa pelo uso numa prática compartilhada. Aqui eu não pergunto o que você quer: eu **jogo um lance** (uma cena concreta de uso), e você aceita, recusa ou corrige. A intenção é o que ficou aceito; o "não faz" é o que foi recusado. Reconhecer uma cena custa menos do que formular um requisito, e a recusa mostra o limite que a pergunta direta não acha.

O jogo serve à mensagem, não ao contrato (D-004, D-006): você aprova o que reconhece, em primeira pessoa; quem lê código vê os testes por requisito.

## Constantes

```
JOGO_MAX_LANCES_POR_RODADA = 3
JOGO_MIN_LANCES_DE_FRONTEIRA_POR_RODADA = 1
JOGO_MAX_RODADAS = 5
JOGO_MAX_REQS = 12
JOGO_MAX_AJUSTES_DA_RETRADUCAO = 3
MAX_SENTENCE_WORDS = 25
MAX_SENTENCES_PER_PARAGRAPH = 6
```

Um lance cabe em no máximo 4 frases curtas. `JOGO_MAX_RODADAS` é teto, não alvo. Um projeto pode mudar os tetos em `product-design/conventions.md`.

---

## Regras

### JDL-001 -- Entrada e saída

- **Entrada**: o brief, recebido como veio (verbatim), e `product-design/product-design-as-intended.md`.
- **Saída**: as seções `## Intenção`, `## Requisitos`, `## Casos de uso`, `## Retradução` e `## Nas suas palavras` do próprio plano (PIC). Nenhum arquivo fora do plano é criado.
- O jogo nunca é pulado numa tarefa com código. Ele pode durar uma rodada quando o brief já traz intenção detalhada. Tarefa sem código joga o jogo curto (JDL-009).
- O plano nasce na primeira rodada, com as seções que já têm conteúdo, e cresce a cada rodada. Se a sessão cair, o arquivo guarda o que já foi dito (git é a recuperação).

- **Quem decide**: o designer (D-006); o `/plan` conduz.
- **Critério de aceitação**: ao fim do jogo, o plano tem as cinco seções e `check_plan_intent.py <plano>` sai 0; ou a decisão voltou a você no teto (JDL-007).

### JDL-002 -- Os lances

Eu só falo por lances. Cada lance é uma cena, não uma pergunta aberta.

| Lance | Forma | O que fixa |
|---|---|---|
| **Cena** | "Segunda, 10h. Você abre X, faz Y e vê Z." | quem, gatilho, o que faz, resultado |
| **Contra-cena** | uma cena plausível, que parece útil, e que eu suspeito que não deveria acontecer | não faz |
| **E se** | a cena aceita com um único elemento trocado: outra pessoa, outro momento, um limite estourado, uma falha | erros e limites, quem |
| **Nomear** | "Você chamou isso de X. Quando eu digo X, é isto: <cena curta>?" | os termos do domínio no seu sentido |
| **Sua vez** | eu peço que você conte a sua cena, com as suas palavras | abre o jogo; destrava quando você recusa duas cenas seguidas |

O jogo abre com **Sua vez** se o brief tem menos de três frases; senão, abre com uma **Cena** tirada do brief.

- **Quem decide**: eu escolho o lance; você decide o destino dele.
- **Critério de aceitação**: nenhuma rodada registrada tem pergunta aberta do tipo "o que você quer?" fora de um lance **Sua vez**.

### JDL-003 -- As três respostas e o destino de cada uma

Cada lance vai num AskUserQuestion com três opções: **Aceito**, **Recuso**, **Corrijo** (a correção vem no campo livre). O texto do lance fica na pergunta. Cada opção leva a justificativa curta da convenção de pontos de decisão (`.claude/references/general/constraints.md`), em uma linha, e nenhuma opção leva o rótulo de recomendada:

- **Aceito** -- Recommended when a cena é o que você quer que aconteça.
- **Recuso** -- Recommended when a cena não deve acontecer, mesmo parecendo útil.
- **Corrijo** -- Recommended when a cena está quase certa; escreva como ela é.

| Resposta | Destino no plano |
|---|---|
| Aceito | vira requisito em `## Requisitos` ou caso de uso em `## Casos de uso`; a origem é o `A<n>` do lance |
| Recuso | entra na linha "Não faz" de `## Intenção` com o `A<n>`; se você disser por quê, o motivo vai junto |
| Corrijo | a correção, verbatim, é citada em `## Nas suas palavras` como o `A<n>`; o requisito ou caso de uso sai da cena corrigida; eu reconto a cena no próximo lance só se a correção abriu dúvida |

O registro em `## Nas suas palavras` leva o lance e a resposta: `A4 (contra-cena, recusou): "<texto do lance>" -> "<resposta>"`. O lance é texto meu; só a resposta é sua, e só ela pode ser citada como suas palavras num requisito.

- **Quem decide**: você.
- **Critério de aceitação**: todo `A<n>` gravado tem o tipo do lance, a resposta e, quando houver, o texto livre verbatim; todo requisito cita a origem `A<n>` ou `F<n>`.

### JDL-004 -- De onde vêm as cenas

Eu monto cada cena só com: as frases do brief (`F<n>`), o `product-design-as-intended.md`, as notas que o brief cita e os lances já aceitos. Um elemento que não vem dessas fontes é marcado `(suposição)` dentro da cena. Se você aceita a cena, a suposição vira parte do requisito com a fonte `A<n>`; se corrige ou recusa, ela não entra.

**Índice do pedido.** Eu divido o brief em frases (ponto final, interrogação, exclamação ou item de lista) e numero `F1`, `F2`, ... na ordem do texto, sem mudar uma palavra. O índice é fixado na primeira rodada e nunca renumerado.

**Confidencialidade.** O brief verbatim vai para o plano, que é versionado. Antes de gravar a primeira rodada, eu aviso e ofereço trocar nomes de pessoa, de cliente, de parceiro ou dados sensíveis por um marcador (`[nome omitido]`). A troca é escolha sua.

- **Quem decide**: eu monto; você confirma pela resposta e decide a troca.
- **Critério de aceitação**: nenhum requisito usa uma suposição sem um `A<n>` aceito como fonte; o aviso de confidencialidade aparece na primeira rodada.

### JDL-005 -- Rodada e cobertura das seis dimensões

Uma rodada tem até `JOGO_MAX_LANCES_POR_RODADA` lances, enviados juntos num só AskUserQuestion (uma pergunta por lance). Eu escolho os lances pela dimensão que ainda está vazia, sem nomear a dimensão para você. As seis dimensões:

| Dimensão | O que a cobre | Lance típico |
|---|---|---|
| quem | quem usa, e o que essa pessoa já sabe fazer sem ajuda | Cena, E se (outra pessoa) |
| o que faz | o que a pessoa quer conseguir fazer | Cena |
| gatilho | quando começa, o que a pessoa faz primeiro | Cena |
| resultado | o que você vê quando dá certo | Cena |
| não faz | o que não deve acontecer, mesmo parecendo útil | Contra-cena |
| erros e limites | o que acontece quando algo dá errado; limite de tempo ou de quantidade | E se |

Uma dimensão pode ficar sem requisito quando você a declara fora: ela entra em "Não faz" com o seu motivo. Ao fim de cada rodada, eu gravo o plano e rodo `check_plan_intent.py`; o resultado do verificador decide se o jogo continua, não a minha impressão.

- **Quem decide**: o verificador diz se continua; eu escolho o próximo lance.
- **Critério de aceitação**: nenhuma rodada com mais de 3 lances; toda dimensão tem um `A<n>` ou `F<n>` que a preenche, ou está em "Não faz" com motivo.

### JDL-006 -- Teste da surpresa

Toda rodada tem pelo menos `JOGO_MIN_LANCES_DE_FRONTEIRA_POR_RODADA` lance de fronteira (**Contra-cena** ou **E se**): um lance que eu espero que possa ser recusado. Uma rodada em que tudo foi aceito não encerra o jogo sozinha: a próxima rodada abre com uma contra-cena. Um lance que só confirma o que já foi aceito não conta como lance: o que só confirma não entra no seu registro (D-004).

- **Quem decide**: eu.
- **Critério de aceitação**: toda rodada registrada tem ao menos um lance de fronteira; o jogo inteiro tem ao menos uma recusa ou uma correção, ou a Retradução diz "nenhuma cena foi recusada".

### JDL-007 -- Teto de rodadas: três saídas

Se depois de `JOGO_MAX_RODADAS` rodadas o verificador ainda devolve `error`, o jogo **para** e devolve a decisão a você, num AskUserQuestion:

- **Continuar** mais uma rodada -- Recommended when falta uma cena só e você sabe a resposta. NOT recommended when a mesma lacuna ficou aberta em três rodadas seguidas.
- **Aceitar como premissa** o que falta -- Recommended when o ponto não muda o que se vê. NOT recommended when o ponto decide o resultado que se vê.
- **Arquivar o tema** -- Recommended when você ainda não sabe o que quer. NOT recommended when só falta um detalhe.

Eu nunca invento resposta para sair do teto. "Aceitar como premissa" grava o ponto em `## Intenção` com a fonte `teto`, e a escolha fica registrada em `## Nas suas palavras`.

- **Quem decide**: você.
- **Critério de aceitação**: nenhum jogo registrado passa de 5 rodadas sem uma das três escolhas gravada.

### JDL-008 -- O que é um bom requisito

Um bom requisito:

- é observável: diz o que quem usa vê ou recebe;
- tem um comportamento só;
- não traz solução técnica (nada de tabela, rota, framework ou nome de função);
- tem um ou mais casos de uso em prosa: quem, quando, o que faz, o que vê;
- tem "Para que": em uma frase, o que você ganha com ele. O "Para que" guarda o porquê que o teste não representa.

Dois tipos: comportamento (o que o sistema faz) e restrição (desempenho, segurança, limite). A restrição também precisa de um caso de uso observável. Um plano tem no máximo `JOGO_MAX_REQS` requisitos; acima disso, o tema é grande demais para um plano e vira roadmap.

Exemplos bons:

| Requisito | Caso de uso |
|---|---|
| Você pode marcar uma conta como paga. | Você abre a lista de contas, marca uma como paga e ela aparece na lista de pagas. |
| Você recebe um aviso antes do vencimento. | Faltam 3 dias para o vencimento; você abre a tela inicial e vê o aviso. |
| A lista abre sem espera longa (restrição). | Você abre a lista com 500 contas e ela aparece em até 2 segundos. |

Exemplos ruins e o porquê:

| Requisito | Problema |
|---|---|
| O sistema deve ser rápido. | sem caso de uso observável; "rápido" sem número |
| Gravar a conta na tabela `bills` com índice por data. | solução técnica, nada que quem usa veja |
| Você pode cadastrar, editar, apagar e exportar contas. | quatro comportamentos num requisito só |

- **Quem decide**: eu reescrevo; você aprova (JDL-010).
- **Critério de aceitação**: todo requisito tem uma frase, "Para que", origem e ao menos um caso de uso (PIC).

### JDL-009 -- Jogo curto (tarefa sem código)

Uma rodada com dois lances: a **Cena** do fim ("Pronto: você abre ... e vê ...") e uma **Contra-cena**. As respostas preenchem as quatro linhas de `## Intenção` (Objetivo, O que você vê no fim, Não faz, Pronto quando). Não há `## Requisitos` nem `## Casos de uso`, e o plano registra os lances em `## Nas suas palavras`. Itens gerados por `/plan --roadmap` também usam o jogo curto.

- **Quem decide**: você, pelas respostas; a aprovação vem com o plano.
- **Critério de aceitação**: o plano sem código tem `## Intenção` com quatro linhas e `## Nas suas palavras` com dois `A<n>`.

### JDL-010 -- Retradução e aprovação

Quando `check_plan_intent.py` não devolve `error`, eu escrevo `## Retradução` em primeira pessoa e em voz controlada (JDL-011): o que entendi, o que vou construir (cada requisito com o seu caso de uso, o texto primeiro e o ID pequeno no fim da linha) e "O que eu não vou fazer" (a linha "Não faz"). Mostro a Retradução e você escolhe num AskUserQuestion:

- **Aprovar** -- Recommended when cada requisito diz algo que você reconhece. NOT recommended when algum requisito surpreendeu você.
- **Ajustar** -- Recommended when um requisito está quase certo. NOT recommended when o tema inteiro mudou (então Descartar).
- **Descartar** -- Recommended when o pedido mudou de natureza. NOT recommended when só falta um detalhe.

Ajustar volta ao jogo com um lance **Corrijo** sobre o requisito apontado. Depois de `JOGO_MAX_AJUSTES_DA_RETRADUCAO` ajustes, o requisito é vago: o jogo reabre a dimensão dele com uma cena nova. Você aprova a mensagem, não o contrato: os testes por requisito ficam para quem lê código (D-004, D-006).

- **Quem decide**: você.
- **Critério de aceitação**: nenhum plano segue para os steps sem a escolha **Aprovar** registrada; a Retradução tem "O que eu não vou fazer".

### JDL-011 -- Voz

**Dentro da regra** (texto que eu escrevo para você): lances, Retradução, requisitos, casos de uso, "Para que", linhas de `## Intenção`.

**Fora da regra**: citação verbatim sua (entre aspas, ou nas listas `F` e `A`), código, IDs.

1. Frases de até `MAX_SENTENCE_WORDS` (25) palavras.
2. Até `MAX_SENTENCES_PER_PARAGRAPH` (6) frases por parágrafo.
3. Uma ideia por frase.
4. Um termo por conceito: requisito (não "necessidade" nem "regra"), o que você vê (não "saída"), não faz (não "backlog"), premissa (não "hipótese"), aprovar (não "validar").
5. Aviso antes da instrução; imperativo nas instruções.

- **Quem decide**: o designer.
- **Critério de aceitação**: a Retradução de um plano registrado respeita as regras 1 e 2.

---

## Exemplo (jogo completo, uma rodada)

Brief: "quero marcar contas como pagas e ser avisado antes de vencer".

- **A1 (cena)**: "Segunda de manhã. Você abre a lista de contas, marca a de luz como paga e ela vai para a lista de pagas." -> Aceito.
- **A2 (e se)**: "A conta de água vence sexta. Na terça você abre a tela inicial e vê o aviso." -> Corrijo: "o aviso tem de chegar três dias antes, não dois".
- **A3 (contra-cena)**: "Ao marcar como paga, o sistema já envia o comprovante por e-mail ao seu contador." -> Recuso: "o comprovante eu mando quando quiser".

Saída: `REQ-contas-001` (marcar como paga; caso de uso de A1), `REQ-contas-002` (aviso três dias antes; caso de uso de A2, com a correção citada em `## Nas suas palavras`); "Não faz": não envia comprovante por e-mail (A3). A Retradução começa: "Eu entendi que você quer marcar contas como pagas e ver um aviso três dias antes do vencimento. O que eu não vou fazer: enviar comprovantes por e-mail."
