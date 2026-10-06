---
designer_description: "When a plan, a skill, or a later roadmap item needs to know what the extended cycle reads, writes, and who approves at each phase -- grill, specify, plan writing, test-first, and the three steps of the ladder -- I'm the normative contract with stable CYC-NNN rules, so each item cites a rule instead of re-deriving the cycle."
---

# GENERAL - EXTENDED CYCLE CONTRACT

> Contrato normativo do ciclo estendido (roadmap-000006, plan-000007; H-009 no §3 subseção 2.9 e D-004 em `product-design/product-design-as-intended.md`). Este arquivo diz **o que** cada fase lê, escreve e quem aprova. Ele não executa nada: validador, fórmula e pipeline são de outros planos (ver CYC-019).
>
> Idioma: pt-BR (documento de contrato), identificadores em en-US. Marcação: `[default; aceito 2026-10-06]` indica uma decisão pendente do plan-000007 que o designer aceitou no default.
>
> Cada regra tem identificador estável `CYC-NNN`, campo **Quem decide** e campo **Critério de aceitação**. Outros planos citam a regra em `Traces:`.

## Visão geral

```
PLAN                                         IMPLEMENT                 REFLECT
grill -> specify -> escrever o plano   ->    teste vermelho -> código  ->  divergência
(intent.md)  (.feature)  (plano v2)          -> gate                       por degrau
```

A escada tem cinco representações: brief -> `intent.md` -> `.feature` -> teste -> código + gate. A divergência é medida em três degraus (CYC-009). O ciclo continua PLAN -> BUILD -> REFLECT (D-001, H-008); grill e specify são fases do `/plan`, não skills.

---

## Regras

### CYC-001 -- O ciclo e a posição das fases

O ciclo é PLAN, IMPLEMENT, REFLECT. O PLAN contém, nesta ordem, as fases grill, specify e escrita do plano. O IMPLEMENT contém, por step, teste vermelho por cenário, código e gate. O REFLECT lê a divergência por degrau. Não há skill nova, preset nem perfil: o comportamento é igual para o citizen e para o power dev; muda quem olha cada degrau (CYC-013).

- **Quem decide**: designer (D-001; decisão fechada 1 do plan-000007).
- **Critério de aceitação**: nenhuma skill `/grill`, `/specify` ou `/build` existe: `ls -d .claude/skills/grill .claude/skills/specify .claude/skills/build` falha nos três.

### CYC-002 -- Fase grill

- **Entrada**: o brief.
- **Saída**: `features/<slug>/intent.md` com requisitos `REQ-<slug>-NNN` (formato em CYC-015), escritos em linguagem que o citizen valida, mais as seções "Nas suas palavras", "Fora do escopo" e "Premissas".
- **Regra**: a grill nunca é pulada. Ela pode ser curta (uma pergunta) quando o brief já traz intenção detalhada. O teto é de 5 rodadas de 4 perguntas, com uma ideia por pergunta (§10 do as-intended, `[intended]`); esgotado o teto, a decisão volta ao citizen.
- **Aprovação**: o designer aprova a lista de requisitos e o "não faz" antes de o `intent.md` ir a `status: approved`.
- **Quem decide**: designer (aprova o `intent.md`); o `/plan` conduz a entrevista.
- **Critério de aceitação**: existe `features/<slug>/intent.md` com `status: approved` e todo REQ tem texto em linguagem natural e um critério; o texto do citizen usa voz controlada (frases curtas, termos fixos; §10).

### CYC-003 -- Fase specify

- **Entrada**: `intent.md` aprovado.
- **Saída**: um ou mais `features/<slug>/*.feature`; todo `Scenario` carrega a tag `@REQ-<slug>-NNN` do requisito que cobre.
- **Ponto de aprovação humana**: antes de escrever o plano, o designer aprova a mensagem e quem lê código aprova o `.feature` como contrato (CYC-013). No máximo 3 rodadas de ajuste; ajuste repetido indica REQ vago e a conversa volta à grill (§10, `[intended]`).
- **Quem decide**: designer (a mensagem) e quem lê código (o contrato) aprovam; o `/plan` escreve.
- **Critério de aceitação**: todo `Scenario` do `.feature` tem tag `@REQ-`; todo REQ aprovado do `intent.md` aparece em pelo menos um cenário, ou consta como descoberto (CYC-010); o registro da aprovação consta no plano.

### CYC-004 -- Quando a specify é pulada `[default; aceito 2026-10-06]` (decisão pendente 2 = A)

A decisão é por plano, não por step. A specify roda quando algum step do plano cria ou muda código com comportamento observável e tem `Tests:` não-N/A. Ela é pulada, por tipo de tarefa, nos prefixos DOCUMENT, CHORE e RESEARCH e nos planos só de configuração ou de harness; num plano que roda a specify, os steps de configuração ou de harness usam `Scenarios: N/A (motivo)` (seção "Compatibilidade"). Ao pular, o plano traz a linha `Specify: skipped -- <motivo>`. A grill continua valendo (CYC-002). Alternativas rejeitadas: nunca pular (obriga Gherkin para um README) e pular por escolha livre (vira opcional, o que H-009 não mede).

- **Quem decide**: o `/plan` aplica a regra e registra o motivo; o designer pode contestar na revisão do plano.
- **Critério de aceitação**: plano sem `*.feature` aprovado contém a linha `Specify: skipped -- <motivo>`; plano com algum step de comportamento observável e `Tests:` não-N/A, e sem essa linha, tem pasta `features/<slug>/` com `.feature` aprovado.

### CYC-005 -- Escrita do plano

A terceira fase do PLAN escreve o plano a partir de `intent.md` e dos `.feature` aprovados. O cabeçalho referencia a pasta por `Feature: <slug>`. Todo step com `Tests:` não-N/A declara os cenários que cobre (campo `Scenarios:`; definição do campo e da versão do formato na seção "Compatibilidade").

- **Quem decide**: `/plan` escreve; designer aprova o plano (fluxo existente do `/plan`).
- **Critério de aceitação**: o plano tem `Feature: <slug>` e todo step com `Tests:` não-N/A tem `Scenarios:` apontando para tags `@REQ-` que existem nos `.feature`. Plano de pesquisa ou documentação não cria pasta nem `Feature:`.

### CYC-006 -- Invocação avulsa `--grill` e `--specify` `[default; aceito 2026-10-06]` (decisão pendente 1 = B)

As fases são internas ao `/plan`. Cada uma também poderá ser invocada avulsa (`/plan --grill`, `/plan --specify`) para repetir só a entrevista ou só o Gherkin depois de mudança de intenção. Neste contrato as flags são **interface reservada**: o nome e o sentido ficam fixados, a implementação é decidida pelos planos que tratam das fases. Alternativa rejeitada: skills `/grill` e `/specify` separadas (bifurca o ciclo de H-008).

- **Quem decide**: designer, no plano que implementar as fases.
- **Critério de aceitação**: nenhum texto executável das flags existe em `SKILL.md` até a implementação; as flags aparecem neste contrato como "reservada".

### CYC-007 -- O que cada fase lê, escreve e quem aprova

| Fase | Lê | Escreve | Aprova |
|---|---|---|---|
| Grill | brief, `product-design-as-intended.md` | `features/<slug>/intent.md` | designer |
| Specify | `intent.md` aprovado | `features/<slug>/*.feature` | designer (a mensagem, CYC-013) e quem lê código (o contrato) |
| Escrever o plano | `intent.md`, `*.feature` aprovados | plano v2 em `_output/plans/` | designer |
| IMPLEMENT (por step) | plano, `.feature`, código | teste, código, `features/<slug>/gate.json` | o portão (resultado de ferramenta, T1) |
| REFLECT | tudo acima | nota e divergência por degrau | designer (aceita ou recusa o espelho) |

- **Quem decide**: designer.
- **Critério de aceitação**: cada fase do `/plan` registra, no plano ou no progress, o que leu, o que escreveu e quem aprovou; nenhuma fase escreve em arquivo de classificação Human (markers) fora do `apply_marker.py` (T4).

### CYC-008 -- Ordem e portões

1. Sem `intent.md` aprovado não há specify.
2. Sem `.feature` aprovado não há plano v2 (plano v1 e plano com `Specify: skipped` seguem o fluxo existente).
3. Sem plano aprovado não há IMPLEMENT.
4. Sem as-intended não há ciclo (T2, D-002).

- **Quem decide**: designer; o `/plan` recusa partir fora de ordem.
- **Critério de aceitação**: tentar specify com `intent.md` em `status: grilling` termina em recusa com a razão dita; o mesmo para plano v2 sem `.feature` aprovado. (A recusa executável é de plano posterior; aqui o critério é a regra escrita e citável.)

### CYC-009 -- Os três degraus e os artefatos de cada par

| Degrau | Par | Artefatos comparados |
|---|---|---|
| D1 | intenção -> cenário | REQ de `intent.md` x tags `@REQ-` dos `.feature` |
| D2 | cenário -> teste | `Scenario` x teste executável (chave de cenário no relatório do runner, CYC-012) |
| D3 | teste -> código + gate | teste verde x código existente x resultado do portão em `gate.json` |

Antes do D1 existe o **degrau zero (D0)**: o resíduo do brief que não virou requisito nem fora-do-escopo. D0 é leitura fora do vetor D (D-004); ele é objeto da auditoria semântica e da retradução, não de contagem.

- **Quem decide**: designer; a medida é do plan-000008.
- **Critério de aceitação**: os planos 000008 a 000015 citam D1, D2, D3 e D0 com estes sentidos; nenhum plano usa "divergência" sem dizer o degrau.

### CYC-010 -- Estados do vocabulário de medida

Cada elemento de um degrau está em um destes estados:

- **coberto**: o elemento da esquerda do par tem correspondente na direita (REQ com cenário; cenário com teste; teste verde com código e gate PASS);
- **descoberto**: não tem correspondente;
- **não medido**: não há como medir (fora do perímetro, CYC-011; stack sem adaptador, CYC-012).

`não medido` aparece sempre ao lado de coberto e descoberto, nunca fundido em média ou número único (constituição Q4). Este contrato fixa só o vocabulário e a unidade (degrau, par, estado); a fórmula é do plan-000008.

- **Quem decide**: designer.
- **Critério de aceitação**: todo relatório de divergência lista, por degrau, as contagens dos três estados e o que está `não medido`; nenhum relatório traz número único sem a decomposição.

### CYC-011 -- Regra do perímetro

A feature (`features/<slug>/`) é a unidade de medida da divergência. Código, testes e requisitos fora de uma feature são `legado: não medido`, não descobertos. A pasta de feature nunca é apagada (git é a recuperação; `product-design-as-intended.md` §2 e D-006).

- **Quem decide**: designer.
- **Critério de aceitação**: relatório de divergência de um projeto com código fora de `features/` marca esse código como `legado: não medido` e não o conta como descoberto.

### CYC-012 -- Fronteira agnóstica de stack

O ciclo consome **contratos**, nunca a ferramenta (constituição T6):

- **Gate contract**: o JSON do portão, os códigos de saída por categoria (0 PASS; 1 configuração ou recusa; 2 lint/tipos; 3 testes; 4 CRAP; 5 arquitetura; 6 mutação; 7 evasão) e as variáveis `GATE_FAST_CMD`, `GATE_FULL_CMD`, `GATE_COMMIT_CMD`.
- **Runner contract**: o relatório do runner de cenários em Cucumber JSON, com a **chave de cenário** (identificador estável que liga o `Scenario` ao teste).

Stack sem adaptador (portão ou runner ausente) degrada para `não medido`, nunca para falha. Dizer "não medido" é a declaração explícita que T1 exige quando o projeto não tem portão.

- **Quem decide**: designer.
- **Critério de aceitação**: projeto sem `GATE_FAST_CMD` produz relatório com D3 `não medido` e a razão dita, e não produz erro; nenhum texto deste ciclo nomeia uma ferramenta de linguagem como requisito do contrato (recomendação de primeiro adaptador é permitida quando marcada como recomendação, como em CYC-026).

### CYC-013 -- Degrau x receptor

O objeto de aprovação muda por receptor, sem perfil e sem bifurcar o ciclo (D-004, H-003):

| Degrau | Citizen dev aprova | Power dev aprova |
|---|---|---|
| D0 e D1 | a lista de requisitos e o "não faz", em voz controlada | o `intent.md` e a rastreabilidade REQ -> cenário |
| D2 | a **mensagem**: a retradução em primeira pessoa e os exemplos narrados | o `.feature`, como **contrato** |
| D3 | a demonstração por cenário e os mutantes sobreviventes recontados como perguntas | o resultado cru do portão e do runner |

O `.feature` é um contrato endereçável entre o humano e o preposto, não a mensagem de metacomunicação. O citizen não é convidado a aprovar o texto do `.feature`.

- **Quem decide**: designer.
- **Critério de aceitação**: o ponto de aprovação da specify mostra ao citizen a retradução em primeira pessoa com exemplos narrados e a lista do que não será feito; o texto do `.feature` vai ao power dev; nenhum número técnico entra no registro do citizen.

### CYC-014 -- Teste da surpresa

Toda emenda a este ciclo e todo signo devolvido ao citizen devem passar pelo teste da surpresa: o item deve poder provocar uma **ruptura decodificável** pelo receptor (algo que ele possa reconhecer como diferente do esperado e dizer "não é isso"). Item que só confirma (PASS, percentuais) não entra no registro do citizen; fica no registro do power dev.

- **Quem decide**: designer, na revisão da emenda.
- **Critério de aceitação**: toda emenda a este arquivo, e todo plano que acrescenta um signo ao citizen, registra em uma frase qual ruptura o item pode provocar; item sem ruptura possível é recusado ou movido ao registro do power dev.

### CYC-015 -- Layout por feature `[default; aceito 2026-10-06]` (decisão pendente 3 = A)

Cada feature vive em `features/<slug>/` na raiz do projeto: `intent.md`, `*.feature` e `gate.json`. Slug em kebab-case; requisitos `REQ-<slug>-NNN`; uma pasta por feature; tarefas sem código não criam pasta. Alternativa rejeitada: arquivos soltos em `_output/` (perde a ligação com o código versionado). O esquema normativo (frontmatter e seções do `intent.md`, convenção de tags `@REQ-`, esquema do `gate.json`, tabela de rastreabilidade) é `.claude/references/template/feature-layout.md`.

- **Quem decide**: designer.
- **Critério de aceitação**: a pasta de uma feature aprovada contém `intent.md` com `status: approved` e pelo menos um `.feature`; todo REQ citado em plano existe no `intent.md` da pasta.

### CYC-016 -- Divergência composta, por degrau `[default; aceito 2026-10-06]` (decisão pendente 4 = C)

A divergência é reportada **por degrau** (D1, D2, D3), com os estados de CYC-010, sem número único. Alternativas rejeitadas: só cenários verdes (esconde cenário que não cobre o REQ) e número único (esconde em que degrau a intenção se perde). Este contrato fixa vocabulário e unidade; a operação (fórmulas, controle) é do plan-000008.

- **Quem decide**: designer; plan-000008 opera.
- **Critério de aceitação**: nenhum artefato do ciclo apresenta divergência como um único número; todo relatório separa D1, D2, D3.
- **Medida**: ver `.claude/references/general/drift-metric.md` e `.claude/references/general/drift-control-protocol.md`. O degrau teste -> código + portão (D3) é reportado em duas partes, D3a (teste e portão) e D3b (código tocado sem cobertura), sempre separadas (DRM-001).

### CYC-017 -- Onde roda o teste-primeiro `[default; aceito 2026-10-06]` (decisão pendente 5 = A)

O teste-primeiro roda dentro do `/implement`, por step, consumindo o portão `--fast` e os hooks existentes sem mudá-los. Alternativa rejeitada: skill separada `/build`. A seção "IMPLEMENT" abaixo detalha o primeiro degrau em código: teste vermelho pelo motivo certo, por cenário, antes do código. Cleaner e Hardener ficam fora (CYC-019).

- **Quem decide**: designer.
- **Critério de aceitação**: nenhuma skill `/build` existe; o `/implement` aponta para este contrato; gate, hooks e `settings` não aparecem em diff de plano que só altera este contrato.

### CYC-018 -- Versão do formato de plano `[default; aceito 2026-10-06]` (decisão pendente 6 = B)

O plano com fase specify rodada usa `plan_format_version: 2`, com `Scenarios:` obrigatório em todo step de `Tests:` não-N/A. Plano v1 (ou sem versão) permanece **válido para sempre**; a recusa vale só para v2. Detalhes na seção "Compatibilidade".

- **Quem decide**: designer.
- **Critério de aceitação**: um plano v1 existente é lido pelo `/plan` e pelo `/implement` sem mudança de resultado; só um plano v2 sem `Scenarios:` em step de `Tests:` não-N/A é classificado como inválido.

### CYC-019 -- O que o contrato não faz

Este contrato **não** define:

- validador de Gherkin nem runner de cenários (plan-000010);
- fórmula de divergência nem estudo de controle (plan-000008);
- Cleaner, Hardener ou o `--pipeline` do `/implement` (plan-000013);
- a implementação executável das fases ou das flags de CYC-006.

Ele também não muda o portão, os hooks ou os denies (S2).

- **Quem decide**: designer.
- **Critério de aceitação**: nenhum texto deste arquivo traz fórmula, regex de validador ou prompt executável de Cleaner/Hardener; um plano que precise de um deles cria sua própria regra e a cita aqui por emenda (CYC-014).

---

## Decisões pendentes do plan-000007 e o default adotado

| # | Decisão | Default adotado | Regra |
|---|---|---|---|
| 1 | Forma das fases grill e specify | B: internas ao `/plan`, flags avulsas reservadas `[default; aceito 2026-10-06]` | CYC-006 |
| 2 | Quando a specify é pulada | A: por tipo de tarefa, com `Specify: skipped -- <motivo>` `[default; aceito 2026-10-06]` | CYC-004 |
| 3 | Layout por feature | A: `features/<slug>/` `[default; aceito 2026-10-06]` | CYC-015 |
| 4 | Definição de divergência | C: composta, por degrau `[default; aceito 2026-10-06]` | CYC-016 |
| 5 | Onde roda o teste-primeiro | A: dentro do `/implement`, por step `[default; aceito 2026-10-06]` | CYC-017 |
| 6 | Versão do formato de plano | B: `plan_format_version: 2` `[default; aceito 2026-10-06]` | CYC-018 |

---

## Compatibilidade

Esta seção fixa a versão do formato de plano (CYC-018) e o campo `Scenarios:`. Definição do campo: `.claude/references/template/plan-step.md`.

**Campo `Scenarios:`.** Linha de metadados do step, obrigatória em v2 em todo step com `Tests:` não-N/A e ausente em v1: lista de tags `@REQ-<slug>-NNN` ou nomes de cenário, tirados dos `.feature` da pasta `Feature: <slug>` do plano, que o step cobre. `N/A (motivo)` é permitido só para step sem comportamento observável (documentação, configuração, harness, refactor com cobertura prévia), inclusive quando o step tem `Tests:` não-N/A; o motivo é obrigatório e satisfaz a obrigatoriedade.

**Regra de versão.**

| Cabeçalho do plano | `Scenarios:` | Situação |
|---|---|---|
| `plan_format_version: 2` | obrigatório em todo step com `Tests:` não-N/A | step sem `Scenarios:` torna o plano **inválido** |
| `plan_format_version: 2` | `N/A (motivo)` em step sem comportamento observável (com ou sem `Tests:`) | válido |
| `plan_format_version: 1` ou ausente | ausente | **válido para sempre**; `/plan` e `/implement` o leem como antes; no máximo advisory, nunca bloqueio |

**O que o `/implement` faz com `Scenarios:` ausente em v2.** Para a execução e informa qual step está sem `Scenarios:`. Não corrige o plano nem inventa cenário: a correção é do `/plan` e do designer. Em v1 não faz nada diferente do que fazia.

**Fato do estado atual (2026-10-06).** O Auto Mode do `/implement` (Phase 0, passo 3, version check) cai para o modo manual quando `plan_format_version` é diferente de `1`. Portanto um plano v2 hoje não roda em Auto Mode. Adaptar isso é do plan-000012 e do plan-000013; este contrato não altera `implement/SKILL.md`.

**Estado da recusa.** Nenhum script lê `plan_format_version` hoje; a recusa executável do v2 inválido é do plan-000012. As fixtures em `.claude/skills/scripts/tests/fixtures/plan_format/` (dois planos v1 reais, um v2 válido, um v2 inválido) documentam os casos.

## IMPLEMENT

> Regras CYC-020 a CYC-026. Esta seção diz o que o IMPLEMENT exige por step com cenário; ela **cita** o portão e os hooks existentes e não os altera (CYC-024).

### CYC-020 -- Quais steps seguem o teste-primeiro

Seguem o teste-primeiro os steps com `Scenarios:` preenchido por tags `@REQ-` (plano v2, CYC-018). Step sem cenário (infra, configuração, harness, `Tests: N/A`, plano com `Specify: skipped`, plano v1) segue o caminho atual do `/implement`, sem mudança (TDD red-green por `Tests:` quando não-N/A, ou ordem legada).

- **Quem decide**: o plano (campo `Scenarios:`); o designer na aprovação do plano.
- **Critério de aceitação**: um plano v1 e um step com `Scenarios: N/A (motivo)` produzem o mesmo fluxo de `/implement` da v0.10.1; só step com tags `@REQ-` entra em CYC-021 a CYC-023.

### CYC-021 -- O cenário vira teste executável

Para cada cenário listado em `Scenarios:`, o step cria ou localiza um teste executável ligado ao `Scenario` pela chave de cenário do runner contract (CYC-012). O teste é escrito **antes** de qualquer código de produção do step.

- **Quem decide**: o subagente do step escreve; o designer revisa pelo plano.
- **Critério de aceitação**: todo cenário do step aparece, pela chave de cenário, no relatório do runner; cenário sem teste fica `descoberto` em D2 (CYC-010), nunca omitido.

### CYC-022 -- Vermelho pelo motivo certo

Antes de escrever código, o teste deve falhar **por comportamento ausente**. Conta como vermelho o estado `failed` do runner contract (CYC-012) com a asserção do cenário falhando. Não contam como vermelho: `ERROR`, `ImportError`, erro de sintaxe, falha de fixture ou de configuração, nem `undefined` (passo sem definição). Teste vermelho por motivo errado é corrigido (o erro de import, sintaxe, fixture ou passo indefinido é resolvido) e a execução repetida até a falha ser a asserção do cenário. Teste que já passa antes do código é relatado como PARTIAL com a nota "test already passes", como no `/implement` atual.

- **Quem decide**: o relatório do runner (resultado de ferramenta, T1); o subagente não declara vermelho por prosa.
- **Critério de aceitação**: o relatório do runner anexado ao progress file mostra, para cada cenário do step, estado `failed` com mensagem de asserção, e nenhum `ERROR`, `ImportError` ou `undefined`; sem esse relatório o step não passa a CYC-023.

### CYC-023 -- Código mínimo até o verde

O Coder escreve o mínimo de código para os testes do step ficarem verdes. Refatorar, limpar e endurecer além do mínimo não entra aqui (CYC-025).

- **Quem decide**: o runner (verde ou não); o designer revisa o diff.
- **Critério de aceitação**: o relatório do runner mostra todos os cenários do step em `passed`; o diff do step só toca arquivos declarados em `Files:`.

### CYC-024 -- Portão por step e resultado em `gate.json`

Depois do verde, o portão `--fast` roda por step como já roda no `/implement`: as mesmas 3 tentativas, a falha após a terceira como PARTIAL com os achados no progress file. O resultado da última rodada entra em `features/<slug>/gate.json` (esquema em `.claude/references/template/feature-layout.md`; `fast` com `exit_code`, `category`, `ref`). Projeto sem `GATE_FAST_CMD`: `fast: null` ou arquivo ausente, D3 `não medido` com a razão dita, nota do step com `--gate not-installed` (CYC-012, T1, T6).

O contrato **só cita** o portão e os hooks: o portão (`gate.py` e os adaptadores), os hooks `Stop` e `PreToolUse` em commit, o deny de `--no-verify` e de `--accept-baseline`, o baseline e as linhas `GATE_*` **não mudam** (S2). O agente escreve `gate.json` a partir do JSON do portão, nunca à mão sobre um resultado inventado e nunca para mover limiar.

- **Quem decide**: o portão (T1); o limiar é do humano (S2).
- **Critério de aceitação**: o diff de um plano que aplica este contrato não toca arquivo de portão, de hook nem de `settings`; `gate.json` de uma feature com step em PASS traz `fast.exit_code` 0 e `ref` que aponta para um JSON existente em `QUALITY_DIR`.

### CYC-025 -- `--pipeline` reservado (Cleaner, Hardener)

A flag `/implement --pipeline`, com os papéis Cleaner e Hardener depois do Coder, é **interface reservada** do plan-000013. Neste contrato o nome e o lugar na cadeia (após CYC-023, antes de CYC-024) ficam fixados; não há prompt, regra de decisão nem texto executável.

- **Quem decide**: designer, no plan-000013.
- **Critério de aceitação**: nenhum `SKILL.md` contém texto executável de `--pipeline`, Cleaner ou Hardener até o plan-000013.

### CYC-026 -- Runner de Gherkin pendente

O runner que executa os `.feature` e emite o relatório do runner contract é **pendente do plan-000010**. A recomendação é pytest-bdd como primeiro adaptador para Python, apenas como recomendação: o contrato descreve o relatório (Cucumber JSON com chave de cenário, CYC-012) e não nomeia ferramenta como requisito. Enquanto o runner não existe, o projeto declara D2 e D3 `não medido` para os cenários sem runner, nunca como falha (T6).

- **Quem decide**: designer, no plan-000010.
- **Critério de aceitação**: nenhuma regra desta seção exige uma ferramenta específica; um projeto sem runner produz relatório com `não medido` e a razão dita.
