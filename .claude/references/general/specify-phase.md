---
designer_description: "After you approve the list of requirements, I'm the protocol /plan follows to turn it into scenarios: I write what I understood back to you in first person, with a short story for each requirement and the list of what I will not do; the scenarios go to whoever reads code as a contract; a tool checks both before anyone sees them, and only your approval, recorded by that tool, lets the plan begin."
---

# GENERAL - SPECIFY PHASE

> Protocolo normativo da fase specify do `/plan` (plan-000011; item 5 do roadmap-000006). Detalha CYC-003, CYC-004, CYC-006, CYC-007, CYC-008, CYC-013 e CYC-014 de `.claude/references/general/extended-cycle-contract.md`, com a emenda D-004 de `product-design/product-design-as-intended.md`: o citizen aprova a **mensagem** (a retradução em primeira pessoa e os exemplos narrados); o `.feature` é derivado dela e aprovado como **contrato** por quem lê código.
>
> Depende de: `intent.md` aprovado pela grill (`grill-phase.md`, GRL-006, GRL-008; verificador `check_intent.py`); convenção e validador do `.feature` (`gherkin-spec-format.md`, GHK-001..019; `check_features.py`); layout `features/<slug>/` (`.claude/references/template/feature-layout.md`). Verificador desta fase: `.claude/skills/scripts/check_specify.py`.
>
> Idioma: pt-BR (protocolo), identificadores em en-US. Marcação: `[default; aceito 2026-10-06]` indica uma decisão pendente do plan-000011 que o designer aceitou no default. Cada regra tem identificador estável `SPC-NNN`, campo **Quem decide** e campo **Critério de aceitação**. Outros planos citam a regra em `Traces:`.

## Constantes

```
SPECIFY_MAX_ROUNDS = 3        # rodadas de ajuste pedidas pelo citizen (SPC-011)
MAX_SENTENCE_WORDS = 25       # importada de check_intent.py (voz controlada, §10 do as-intended)
MAX_SENTENCES_PER_PARAGRAPH = 6
LOCK_SCHEMA_VERSION = 1       # scenarios.lock.json
```

`SPECIFY_MAX_ROUNDS` é palpite a calibrar no piloto (plan-000016). As constantes de voz não são copiadas: `check_specify.py` as importa de `check_intent.py`, que as importa do lint de voz controlada quando ele existir.

## Entrada e saída

| | Artefato | Quem escreve |
|---|---|---|
| Entrada | `features/<slug>/intent.md` com `status: approved`, passando em `check_intent.py --require-approved --strict` | grill (GRL-008) |
| Saída | `features/<slug>/<slug>.feature` (um ou mais `*.feature`) | o `/plan` (LLM), conferido por `check_specify.py` |
| Saída | seção `## Retradução` do `intent.md`, com `rev` | o `/plan` (LLM), conferida por `check_specify.py` |
| Saída | campos `scenarios`, `scenarios_approved_at`, `scenarios_approved_by`, `scenarios_contract_by`, `scenarios_rev` no frontmatter do `intent.md` | só `check_specify.py --approve` |
| Saída | `features/<slug>/scenarios.lock.json` | só `check_specify.py --approve` |
| Saída | linhas em "Mudanças" do `intent.md` (ajuste, renomeação de cenário) | o `/plan` |

A fase não escreve o plano. Ela termina com a aprovação registrada (ou com a decisão devolvida ao citizen), e só então o `/plan` escreve o plano (CYC-005, CYC-008).

---

## Regras

### SPC-001 -- Entrada

A fase só começa com `features/<slug>/intent.md` em `status: approved` e `check_intent.py <intent.md> --require-approved --strict` saindo 0. Caso contrário ela **recusa**, diz o motivo em uma frase ("A lista de requisitos ainda não foi aprovada.") e oferece voltar à grill (`/plan --grill <slug>`). Nada é escrito.

- **Quem decide**: o verificador (`check_specify.py` chama `check_intent` por importação).
- **Critério de aceitação**: com `intent.md` em `grilling`, `check_specify.py --feature <slug>` devolve um achado SPC-001 (erro) e `--approve` sai 1 sem escrever nada; com `intent.md` aprovado e sem erro, nenhum SPC-001.

### SPC-002 -- Quando roda

A specify roda quando a grill classificou a tarefa "com código" (existe `features/<slug>/intent.md`, GRL-012). Tarefa sem código não cria pasta e o plano traz a linha `Specify: skipped -- <motivo>` (CYC-004). A classificação da grill é o *proxy* da regra "algum step terá `Tests:` não-N/A", porque os steps só existem depois da specify; o plan-000012 confere depois que plano v2 com `Tests:` não-N/A e `Specify: skipped` é inválido.

- **Quem decide**: o `/plan` classifica (GRL-012); o designer pode contestar na revisão do plano.
- **Critério de aceitação**: plano de tarefa sem código não tem pasta `features/` nova e tem a linha `Specify: skipped -- <motivo>`.

### SPC-003 -- Derivação: todo requisito ativo tem cenário

Todo REQ `ativo` ganha pelo menos um `Scenario` com a tag `@REQ-<slug>-NNN`. REQ `retirado` não tem cenário: o cenário dele sai do `.feature` com uma linha em "Mudanças" (SPC-012). O critério "Quando A, o sistema B" do REQ vira `Quando A` e `Então B`; o `Dado` vem das dimensões "quem" e "gatilho" do `intent.md` (tabela abaixo).

- **Quem decide**: o verificador (`check_specify.py`, sobre a matriz de `check_features.py`).
- **Critério de aceitação**: REQ ativo sem cenário devolve SPC-003 (erro) com o ID do REQ; REQ retirado sem cenário não dispara; REQ retirado com cenário dispara SPC-003 (erro). O validador do plan-000010 não acusa o cenário de REQ retirado (GHK-004); a specify é mais estrita porque grava a aprovação.

### SPC-004 -- Restrição tem número `[default; aceito 2026-10-06]` (decisão pendente 5 = A)

REQ de tipo `restrição` vira cenário como os demais, com um **valor numérico** num step `Então` (ou `E`/`Mas` que o herda) ou nas linhas de `Exemplos` do cenário (limite, tempo, tamanho). Se o critério não admite número nem observação ("compatível com o navegador X", "sem dependência Y"), a fase **volta à grill**: o critério falha P2 (GRL-006). Ela não inventa cenário.

- **Quem decide**: o verificador.
- **Critério de aceitação**: restrição cujo cenário não tem número no `Então` nem em `Exemplos` devolve SPC-004 (erro); "em até 2 segundos" no `Então`, ou uma linha numérica em `Exemplos`, não dispara.

### SPC-005 -- Erros e limites

Cada caso de erro ou de limite da dimensão "erros e limites" que a grill ligou a um REQ ganha cenário próprio, com a tag desse REQ. Caso sem REQ: a fase **pergunta** se ele vira requisito (volta à grill) ou fica fora do escopo. Nunca cria cenário sem tag (GHK-002).

- **Quem decide**: o citizen (vira requisito ou fica fora); o `/plan` escreve.
- **Critério de aceitação**: nenhum cenário sem tag `@REQ-`; cada caso de "erros e limites" citado por um REQ ativo aparece em algum cenário desse REQ (conferência do power dev ao aprovar o contrato; o verificador só garante a tag).

### SPC-006 -- "Não faz" fica sem cenário e aparece na mensagem

Itens de "Fora do escopo" **não** geram cenário obrigatório. Eles aparecem na retradução, sob "O que eu não vou fazer", para o citizen ver o que ficou fora. A tag `@nao-faz` (GHK-019) continua opt-in: quem lê código pode pedir um cenário negativo, sempre com a tag `@REQ-` de um requisito.

- **Quem decide**: o citizen (vê a lista); quem lê código (decide sobre `@nao-faz`).
- **Critério de aceitação**: a retradução tem pelo menos tantos itens em "O que eu não vou fazer" quantos itens há em "Fora do escopo" (SPC-017).

### SPC-007 -- Voz dos steps

Cada step tem no máximo `MAX_SENTENCE_WORDS` (25) palavras, contadas no texto depois da palavra-chave (`Dado`, `Quando`, ...) e fora os valores entre aspas; uma ideia por step; presente; o papel nomeado como na dimensão "quem" (ou "eu", na voz de quem usa); sem detalhe técnico (GHK-013). As tabelas `Exemplos` ficam fora da regra.

- **Quem decide**: o verificador (tamanho); quem lê código (uma ideia por step, papel).
- **Critério de aceitação**: step de 26 palavras devolve SPC-007 (aviso, bloqueia a aprovação); step de 25 não dispara. Sem o lint de voz controlada, a saída traz a ressalva `voz: não verificada`.

### SPC-008 -- Validação mecânica

`check_specify.py` roda as regras de `check_features.py` sobre a feature, em modo estrito: cada **erro** GHK vira um achado SPC-008 erro e cada **aviso** GHK (por exemplo GHK-013, detalhe técnico; GHK-014, tag de desativação) vira um achado SPC-008 aviso, com a regra GHK na mensagem e a mesma linha. Informações GHK não entram, nem o GHK-005 (requisito sem cenário), que a SPC-003 já diz com o ID do requisito. Antes de mostrar qualquer coisa a alguém, o agente corrige sozinho os achados, em no máximo 3 tentativas (limite que vive só aqui, neste SPC e no SKILL do `/plan`; o verificador não o conhece nem o aplica); se ainda restar achado, ele o mostra em voz controlada e pergunta.

- **Quem decide**: o verificador (resultado de ferramenta, T1).
- **Critério de aceitação**: um `.feature` com aviso GHK-013 devolve SPC-008 aviso e `--approve` sai 1; um com `@skip` devolve SPC-008 aviso; um sem achado GHK de erro ou aviso não dispara.

### SPC-009 -- Aprovação humana: a mensagem e o contrato (emenda D-004)

Há **dois** objetos de aprovação, sem perfil e sem bifurcar o ciclo (CYC-013):

1. **A mensagem** (citizen). O agente mostra a retradução (SPC-017): o que entendeu, em primeira pessoa, um item por requisito com o exemplo narrado, e a lista "O que eu não vou fazer". O citizen **não** vê o `.feature`, as tags nem contagens. Ele escolhe por AskUserQuestion (C4): **Aprovar / Ajustar / Voltar à entrevista / Descartar** (textos abaixo).
2. **O contrato** (quem lê código). O agente mostra o `.feature` e a saída crua de `check_specify.py`. A pessoa escolhe **Aprovar o contrato / Pedir mudança / Ninguém aqui lê código**. A última opção é honesta, não um atalho: o registro diz `scenarios_contract_by: ninguem` e o relatório mostra "contrato: não lido" (Q4).

A mesma pessoa pode responder às duas perguntas, em papéis diferentes (SS-002). A ordem é: mensagem primeiro, contrato depois. Só com as duas respostas positivas a fase vai a SPC-010.

- **Quem decide**: o citizen (a mensagem); quem lê código (o contrato).
- **Critério de aceitação**: o ponto de aprovação mostra ao citizen a retradução e o "não faz", nunca o texto do `.feature`; o texto do `.feature` vai a quem lê código; nenhum número técnico entra no registro do citizen (CYC-013).

### SPC-010 -- Registro da aprovação

`check_specify.py --approve --at <UTC> --by <quem aprovou a mensagem> --contract-by <quem aprovou o contrato | ninguem>` grava, nesta ordem e com escrita atômica **por arquivo** (arquivo temporário e `rename`, mantendo a permissão do original):

1. `features/<slug>/scenarios.lock.json` (esquema abaixo);
2. no frontmatter do `intent.md`: `scenarios: approved`, `scenarios_approved_at`, `scenarios_approved_by`, `scenarios_contract_by`, `scenarios_rev` (= `rev` da retradução).

O resto do `intent.md` fica igual byte a byte. `--at` vem de quem chama (o verificador não lê relógio): o mesmo comando com os mesmos argumentos produz os mesmos bytes. Se **qualquer** regra devolve erro ou aviso, nada é escrito e a saída é 1. A atomicidade não cobre o par: se a execução falhar entre a escrita do lock e a do frontmatter, o `intent.md` fica sem `scenarios: approved`, o estado cai em `stale` com a razão `sem-campo`, e rodar `--approve` de novo recupera. Aprovar é um comando que sai 0 e grava, nunca uma frase do agente.

- **Quem decide**: o verificador grava; o humano aprova (SPC-009). A aprovação humana é necessária, não suficiente.
- **Critério de aceitação**: depois de `--approve` com tudo verde, o frontmatter tem os cinco campos e o lock tem `basis`, `index`, `files` e `retraducao`; repetir o comando produz arquivos idênticos; com qualquer achado de erro ou aviso, nenhum dos dois arquivos muda.

### SPC-011 -- Ajuste `[default; aceito 2026-10-06]` (decisão pendente 2 = B)

Em **Ajustar**, o agente edita a retradução e os `.feature` juntos (a mensagem e o contrato dizem a mesma coisa), sobe o `rev` da retradução e registra a rodada em "Mudanças" (`Retradução rev N: <o que mudou>`). Depois repete SPC-008 e SPC-009. Pedido que muda **o que** se quer (e não **como se descreve**) volta à grill: o REQ muda lá (GRL-011), não aqui. Depois de `SPECIFY_MAX_ROUNDS` (3) rodadas, a fase devolve a decisão ao citizen: aprovar como está, voltar à entrevista ou descartar. Ajuste repetido costuma indicar REQ vago.

- **Quem decide**: o citizen pede; o agente nunca ajusta REQ por conta própria.
- **Critério de aceitação**: retradução com `rev` > 1 sem linha "Retradução" em "Mudanças" devolve SPC-011 (erro); `rev` acima de `SPECIFY_MAX_ROUNDS` + 1 devolve SPC-011 (informação: "passou do teto de ajustes").

### SPC-012 -- Nomes estáveis

Cenário aprovado não muda de nome nem some sem uma linha em "Mudanças" que cite o nome antigo. A chave `<slug>/<arquivo>::<nome>` (CYC-027) liga o cenário ao teste (D2) e ao relatório.

- **Quem decide**: o verificador, contra o lock existente.
- **Critério de aceitação**: cenário do lock que não existe mais e cujo nome não aparece em "Mudanças" devolve SPC-012 (erro, no lock); com a linha em "Mudanças", não dispara.

### SPC-013 -- Estado dos cenários (`stale`)

`check_specify.py --status` devolve um destes estados (DRM-006 `scenario_status`):

| Estado | Quando |
|---|---|
| `missing` | a pasta não tem `*.feature` |
| `draft` | há `*.feature`, sem lock e sem `scenarios: approved` |
| `approved` | o lock existe, `scenarios: approved` no frontmatter, `status: approved`, e o lock **bate**: mesmos REQs `ativo` com o mesmo `rev`, mesmo sha256 de cada `.feature` (sem BOM, com fim de linha LF), mesmo sha256 da retradução |
| `stale` | o lock existe e não bate; ou `scenarios: approved` sem lock (aprovação sem prova); ou o `intent.md` voltou a `grilling` |

`stale` traz as razões (`req-rev`, `req-novo`, `req-retirado`, `feature`, `retraducao`, `intencao-reaberta`, `sem-lock`, `sem-campo`) e a lista de REQs afetados, para a fase reescrever **só** os cenários desses REQs, mantendo o nome dos demais. `stale` observa apenas três coisas: a tabela de REQs (id e `rev`), os `.feature` e a seção Retradução. Editar "Fora do escopo", "Nas suas palavras" ou "Mudanças" não invalida a aprovação. É decisão de design: o que o citizen aprovou foi a mensagem e o contrato, e essas seções não os mudam; o que muda o sentido de um requisito sobe o `rev`, e isso o lock vê. Invalidar por edição de prosa faria o citizen reaprovar sem mudança de sentido, e a aprovação viraria ritual. O D1 trata `stale`, `draft` e `missing` como `não medido` (`NM-CENARIOS-STALE`), nunca como `coberto`.

- **Quem decide**: o verificador.
- **Critério de aceitação**: depois de editar o `.feature` aprovado, `--status` devolve `stale` com a razão `feature`; depois de subir o `rev` de um REQ, `stale` com `req-rev`; com tudo igual, `approved`.

### SPC-014 -- Degradação

Plano v1, projeto sem `features/`, open-seja antigo: a fase não existe e o `/plan` segue como sempre, sem aviso de bloqueio. Sem o validador do plan-000010 (`check_features.py`), a fase **não aprova**: `check_specify.py` sai 2 com "validador de cenários não encontrado" e não escreve nada. Os cenários ficam como rascunho (`draft`). Tabela completa abaixo.

- **Quem decide**: designer.
- **Critério de aceitação**: com o validador ausente, `--approve` sai 2 e nenhum arquivo muda; uma raiz sem `features/` sai 0 sem achado.

### SPC-015 -- O que a fase não faz

A fase **não**: escreve o plano nem o campo `Scenarios:` (plan-000012); liga runner ou escreve teste (plan-000013); calcula D1, D2 ou D3 (plan-000014); muda portão, hooks, denies ou `settings` (S2); altera o `intent.md` além da seção `## Retradução`, dos campos `scenarios_*` e das linhas em "Mudanças".

- **Quem decide**: designer.
- **Critério de aceitação**: o diff de uma specify só toca `features/<slug>/*.feature`, `features/<slug>/scenarios.lock.json` e, no `intent.md`, a retradução, os campos `scenarios_*` e "Mudanças".

### SPC-016 -- Interface `--specify` (implementa CYC-006 para a specify)

`/plan --specify [<slug>]` roda só a specify e para. Lê o `intent.md` aprovado; escreve só os `*.feature`, a retradução, o lock, os campos `scenarios_*` e as linhas em "Mudanças"; nunca escreve plano. Reentrada é permitida (por exemplo depois de `stale`). Sem a pasta `features/`, a varredura (sem `--feature`) sai 0; com `--feature <slug>` e sem a pasta, sai 2. Sem `features/<slug>/`, recusa em uma frase ("A entrevista vem antes: rode /plan --grill.") e não escreve nada.

- **Quem decide**: designer (CYC-006).
- **Critério de aceitação**: depois de `/plan --specify`, o diff do projeto só toca a pasta `features/<slug>/`; sem a pasta, nenhum arquivo é criado.

### SPC-017 -- A retradução (a mensagem ao citizen)

Seção `## Retradução` do `intent.md`, escrita pelo agente na voz controlada, em primeira pessoa ("eu" é o preposto, "você" é o citizen). Forma:

```markdown
## Retradução

rev: 1

<uma ou duas frases: o que eu entendi que você quer>

- <o que eu vou fazer, em primeira pessoa, com o "Para que" do requisito>. (REQ-<slug>-NNN)
  - Exemplo: <uma situação narrada, com valores concretos, em que você vê o requisito funcionar>
- ...

O que eu não vou fazer:

- <item de "Fora do escopo", em primeira pessoa>. (F<n>)
```

Regras: `rev:` é um inteiro a partir de 1; todo REQ `ativo` aparece em um item (o ID pequeno, ao fim da linha, como em GRL-008) com pelo menos um `Exemplo:`; o item fala em primeira pessoa; o REQ `retirado` não aparece; "O que eu não vou fazer" (en-US: "What I will not do") tem pelo menos um item por item de "Fora do escopo". O "Para que" do requisito e os índices `F<n>`/`A<n>` são a matéria da retradução: o citizen reconhece as próprias palavras.

- **Quem decide**: o verificador (forma); o citizen (conteúdo, SPC-009).
- **Critério de aceitação**: sem a seção, ou com REQ ativo fora dela, ou com item sem exemplo, ou com "não faz" faltando, SPC-017 (erro); item sem primeira pessoa, SPC-017 (aviso).

### SPC-018 -- Registro do citizen: teste da surpresa e voz (CYC-014)

Todo signo devolvido ao citizen deve poder provocar uma ruptura decodificável: o citizen precisa poder dizer "não é isso". Por isso a retradução traz exemplos narrados com valores do domínio, e **não** traz o que só confirma: PASS, FAIL, percentuais, nomes de regra (GHK-, SPC-, CYC-), tags `@REQ-` ou o nome do arquivo `.feature`. Cada frase da retradução (fora das aspas) tem no máximo 25 palavras, e cada item ou parágrafo no máximo 6 frases.

- **Quem decide**: o verificador (tamanho e lista fixa de termos técnicos); o designer (se a ruptura é possível, na revisão).
- **Critério de aceitação**: "PASS" ou "%" na retradução devolve SPC-018 (aviso); frase de 26 palavras devolve SPC-018 (aviso); o ID `REQ-<slug>-NNN` entre parênteses e números do domínio ("7 dias", "2 segundos") não disparam. Ruptura que estas regras podem provocar: o citizen lê "em até 2 segundos, mesmo com 500 contas" e diz "não, eu tenho só 50 contas e espero na hora".

---

## Derivação: de onde vem cada step

| Step | Vem de | Exemplo (REQ-contas-da-semana-001) |
|---|---|---|
| `Dado` | dimensões "quem" e "gatilho"; premissas confirmadas; o estado anterior que o critério supõe | "Dado que eu tenho uma conta que vence daqui a 3 dias" |
| `Quando` | a ação do critério ("Quando você abre a tela inicial") | "Quando eu abro a tela inicial" |
| `Então` | o resultado que se vê no critério ("o sistema mostra as contas que vencem nos próximos 7 dias") | "Então eu vejo a conta que vence daqui a 3 dias" |
| `Exemplos` | os limites e números de "erros e limites" e do critério da restrição | `quantidade 500, segundos 2` |

O nome do cenário diz o comportamento em poucas palavras, no domínio do citizen. Idioma `[default; aceito 2026-10-06]` (decisão pendente 3 = A): o do pedido do citizen em "Nas suas palavras" (maioria das frases `F`; empate = pt), declarado em `# language:`. Código, nome de arquivo e step definitions em en-US. Um arquivo `<slug>.feature` por feature `[default; aceito 2026-10-06]` (decisão pendente 6 = A); acima de 15 cenários, sugerir (não exigir) dividir por tema. Quem escreve é o LLM, e as máquinas conferem `[default; aceito 2026-10-06]` (decisão pendente 4 = A).

### Exemplos bons

Contexto: `intent.md` de `.claude/references/template/intent.md` (contas da semana). Os três passam em `check_features.py --strict` contra esse `intent.md` (teste em `test_check_specify.py`).

Comportamento (pt):

```gherkin
# language: pt
Funcionalidade: Contas da semana

  @REQ-contas-da-semana-001
  Cenário: Ver as contas que vencem nos próximos 7 dias
    Dado que eu tenho uma conta que vence daqui a 3 dias
    E eu tenho uma conta que vence daqui a 10 dias
    Quando eu abro a tela inicial
    Então eu vejo a conta que vence daqui a 3 dias
    E eu não vejo a conta que vence daqui a 10 dias
```

Restrição com limite numérico (pt):

```gherkin
# language: pt
Funcionalidade: Contas da semana

  @REQ-contas-da-semana-003
  Esquema do Cenário: A lista abre logo com muitas contas
    Dado que eu tenho <quantidade> contas cadastradas
    Quando eu abro a tela inicial
    Então eu vejo a lista em até <segundos> segundos

    Exemplos:
      | quantidade | segundos |
      | 100        | 2        |
      | 500        | 2        |
```

Erro (pt):

```gherkin
# language: pt
Funcionalidade: Contas da semana

  @REQ-contas-da-semana-002
  Cenário: Desfazer uma conta marcada como paga por engano
    Dado que eu marquei uma conta como paga
    Quando eu escolho desfazer
    Então a conta volta para a lista da semana
```

Os mesmos três em en-US (contexto: `intent.md` com slug `weekly-bills`, fixture `ok-en` de `check_specify.py`):

```gherkin
Feature: Weekly bills

  @REQ-weekly-bills-001
  Scenario: See the bills due in the next 7 days
    Given I have a bill due in 3 days
    And I have a bill due in 10 days
    When I open the home screen
    Then I see the bill due in 3 days
    And I do not see the bill due in 10 days

  @REQ-weekly-bills-003
  Scenario Outline: The list opens soon with many bills
    Given I have <amount> bills saved
    When I open the home screen
    Then I see the list within <seconds> seconds

    Examples:
      | amount | seconds |
      | 100    | 2       |
      | 500    | 2       |

  @REQ-weekly-bills-002
  Scenario: Undo a bill marked as paid by mistake
    Given I marked a bill as paid
    When I choose undo
    Then the bill goes back to the weekly list
```

### Exemplos ruins e o porquê

| Cenário | Problema | Regra |
|---|---|---|
| `Cenário: Ver as contas` com `Dado que eu tenho contas` e `Então eu vejo a lista`, sem `Quando` | sem ação: não diz o que quem usa faz; o critério "Quando A, o sistema B" se perdeu | SPC-003 (derivação), revisão do contrato |
| `Quando eu abro https://app.local/contas` | detalhe técnico: o citizen não reconhece um endereço | SPC-008 via GHK-013 |
| `@REQ-contas-da-semana-001` sobre um cenário que também marca a conta como paga (REQ 002 sem tag) | dois requisitos num cenário, um sem tag: o REQ 002 parece descoberto e o cenário tem dois comportamentos | SPC-003, GHK-012 |

Em en-US: `Scenario: See bills` sem `When`; `When I open https://app.local/bills`; `@REQ-weekly-bills-001` sobre um cenário que também marca a conta como paga.

---

## Apresentação de aprovação (texto exato)

### Para o citizen: a mensagem

O agente mostra a seção `## Retradução` tal como está no `intent.md`, precedida de uma frase:

> Isto é o que eu entendi e o que eu vou construir. Leia cada item e o exemplo. Se algum exemplo surpreender você, diga.

Pergunta (AskUserQuestion, C4): "Isto é o que você quer?"

- **Aprovar**. Recommended when cada item e cada exemplo diz algo que você reconhece. NOT recommended when algum exemplo surpreendeu você.
- **Ajustar**. Recommended when um item está quase certo e só a forma de dizer precisa mudar. NOT recommended when você mudou de ideia sobre o que quer (então Voltar à entrevista).
- **Voltar à entrevista**. Recommended when um requisito está errado ou falta um requisito. NOT recommended when só um exemplo está mal contado.
- **Descartar**. Recommended when o pedido mudou de natureza. NOT recommended when só falta um detalhe.

### Para quem lê código: o contrato

O agente mostra o caminho e o texto de cada `.feature` e a saída de `check_specify.py --feature <slug>`.

Pergunta (AskUserQuestion, C4): "Os cenários são o contrato desta feature. Você os aprova?"

- **Aprovar o contrato**. Recommended when cada cenário tem a tag certa, um comportamento e um resultado observável. NOT recommended when um cenário não corresponde ao item da retradução.
- **Pedir mudança**. Recommended when um cenário diverge da mensagem aprovada ou falta um caso de erro. NOT recommended when a divergência é de intenção (então a mensagem volta ao citizen).
- **Ninguém aqui lê código**. Recommended when o projeto não tem quem leia código agora. NOT recommended when alguém pode ler (o registro diz "contrato: não lido").

**Voltar à entrevista** mantém o `intent.md`, abre `/plan --grill <slug>` (GRL-011) e deixa os cenários em `draft` ou `stale`. **Descartar** registra o motivo em "Mudanças" e encerra a fase sem plano; os `.feature` ficam no git (CYC-011).

## Esquema da aprovação

Frontmatter do `intent.md` (só `check_specify.py --approve` escreve):

```yaml
scenarios: approved
scenarios_approved_at: 2026-10-06T15:00Z
scenarios_approved_by: usuario
scenarios_contract_by: usuario   # ou: ninguem
scenarios_rev: 1                 # = rev da retradução aprovada
```

Campos inseridos antes do `---` de fechamento, nesta ordem, quando não existem; substituídos no lugar quando existem. `check_features.py` lê só `scenarios` (`scenarios_approved` na matriz); os outros campos são tolerados pelos dois parsers.

`features/<slug>/scenarios.lock.json` (JSON com chaves ordenadas, indentação 2, UTF-8, fim de linha `\n`):

```json
{
  "approved_at": "2026-10-06T15:00Z",
  "approved_by": "usuario",
  "basis": {"REQ-contas-da-semana-001": 1, "REQ-contas-da-semana-002": 1, "REQ-contas-da-semana-003": 1},
  "contract_by": "usuario",
  "files": {"contas-da-semana.feature": "<sha256>"},
  "index": ["contas-da-semana/contas-da-semana.feature::Ver as contas que vencem nos próximos 7 dias"],
  "retraducao": "<sha256 da seção Retradução>",
  "rev": 1,
  "schema_version": 1,
  "slug": "contas-da-semana"
}
```

- `basis`: cada REQ `ativo` e o seu `rev` (1 quando a coluna `rev` não existe).
- `index`: chaves de cenário `<slug>/<arquivo>::<nome>`, ordenadas.
- `files`: sha256 dos bytes de cada `*.feature` da pasta.
- `retraducao`: sha256 das linhas da seção `## Retradução` (sem o título; comentários HTML apagados, como no parser de `check_intent.py`; espaços finais removidos; sem linhas vazias no começo e no fim; unidas por `\n`).
- `schema_version` desconhecido: `check_specify.py` sai 2.

## Degradação

| Situação | O que a fase faz | Artefato |
|---|---|---|
| Feature com código, `intent.md` aprovado | Fluxo completo SPC-003 a SPC-010 | `.feature` e retradução aprovados, lock; plano v2 depois (plan-000012) |
| Tarefa sem código (docs, pesquisa, harness, config) | Não roda; não cria pasta | `Specify: skipped -- <motivo>` no plano |
| Tarefa mista (alguns steps com `Tests:` não-N/A) | Roda para os REQs com comportamento; steps sem comportamento observável usam `Scenarios: N/A (motivo)` (plan-000012) | `.feature` só dos REQs com código |
| `intent.md` não aprovado ou em `grilling` | Recusa: "A lista de requisitos ainda não foi aprovada."; oferece `/plan --grill` | nenhum |
| Plano v1, projeto sem `features/`, open-seja antigo | A fase não existe; o `/plan` segue como sempre | nenhum; sem aviso de bloqueio |
| `check_features.py` ausente | Escreve cenários e retradução como rascunho, **não aprova**, diz o motivo | `draft` (sem lock, sem `scenarios: approved`) |
| Cenário que nenhum REQ justifica | Pergunta: vira REQ (volta à grill) ou sai | nenhum cenário sem tag |
| Citizen muda a intenção depois (grill de novo) | `--status` devolve `stale` com os REQs afetados; a fase reescreve só esses cenários e itens, mantém os nomes dos demais e pede nova aprovação | lock regravado na reaprovação |
| Ninguém lê código | A mensagem é aprovada pelo citizen; o contrato fica `ninguem` | `scenarios_contract_by: ninguem`; "contrato: não lido" ao lado do resultado |
| `--specify` avulsa sem `features/<slug>/` | Recusa e diz que a grill vem antes | nenhum |

## Voz

**Dentro da regra** (texto do agente para o citizen): a retradução inteira (exceto citações entre aspas), as perguntas, as dicas do verificador. Os steps do `.feature` também (SPC-007), embora o leitor do contrato seja quem lê código.

**Fora da regra**: citações verbatim do citizen, IDs, código, tabelas `Exemplos`, nomes de arquivo.

Termos fixos (somam-se ao glossário de GRL-010): **cenário** (não "caso de teste"), **o que eu não vou fazer** (não "não-objetivo"), **exemplo** (não "caso de uso"), **contrato** (só no registro de quem lê código).

## O que este arquivo não faz

Não define o formato do plano v2 (plan-000012; ver `plan-from-scenarios.md`, PFS-001..015), o runner nem o teste-primeiro (plan-000013), a fórmula de divergência (plan-000014). Não muda `feature-layout.md`, `gherkin-spec-format.md` nem o contrato do ciclo além de uma linha de ponteiro em cada; as emendas aditivas (o lock e os campos `scenarios_*` no esquema; `stale` = `não medido` na métrica) são texto sugerido ao designer no progress do plan-000011.

---

## Decisões pendentes do plan-000011 e o default adotado

| # | Decisão | Default adotado | Regra |
|---|---|---|---|
| 1 | Prova de que os cenários aprovados são os de agora | A: `scenarios.lock.json` ao lado, mais `scenarios: approved` no frontmatter `[default; aceito 2026-10-06]` | SPC-010, SPC-013 |
| 2 | Teto de rodadas de ajuste | B: 3 rodadas; depois devolve a decisão `[default; aceito 2026-10-06]` | SPC-011 |
| 3 | Idioma do `.feature` | A: o do pedido do citizen, declarado em `# language:` `[default; aceito 2026-10-06]` | Derivação |
| 4 | Quem escreve os cenários | A: o LLM; as máquinas conferem `[default; aceito 2026-10-06]` | SPC-008 |
| 5 | Restrição não observável | A: sempre cenário com número; senão volta à grill `[default; aceito 2026-10-06]` | SPC-004 |
| 6 | Tamanho e divisão em arquivos | A: um `<slug>.feature`; sugestão acima de 15 cenários `[default; aceito 2026-10-06]` | Derivação |
