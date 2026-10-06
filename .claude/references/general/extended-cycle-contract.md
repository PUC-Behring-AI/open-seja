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
- **Protocolo**: ver `.claude/references/general/grill-phase.md` (GRL-001..015) e o verificador `.claude/skills/scripts/check_intent.py` (regra de parada P1 a P6).

### CYC-003 -- Fase specify

- **Entrada**: `intent.md` aprovado.
- **Saída**: um ou mais `features/<slug>/*.feature`; todo `Scenario` carrega a tag `@REQ-<slug>-NNN` do requisito que cobre.
- **Ponto de aprovação humana**: antes de escrever o plano, o designer aprova a mensagem e quem lê código aprova o `.feature` como contrato (CYC-013). No máximo 3 rodadas de ajuste; ajuste repetido indica REQ vago e a conversa volta à grill (§10, `[intended]`).
- **Quem decide**: designer (a mensagem) e quem lê código (o contrato) aprovam; o `/plan` escreve.
- **Critério de aceitação**: todo `Scenario` do `.feature` tem tag `@REQ-`; todo REQ aprovado do `intent.md` aparece em pelo menos um cenário, ou consta como descoberto (CYC-010); o registro da aprovação consta no plano.
- **Protocolo**: fase specify e aprovação dos cenários: ver `.claude/references/general/specify-phase.md` (SPC-001..018) e o verificador `.claude/skills/scripts/check_specify.py`.

### CYC-004 -- Quando a specify é pulada `[default; aceito 2026-10-06]` (decisão pendente 2 = A)

A decisão é por plano, não por step. A specify roda quando algum step do plano cria ou muda código com comportamento observável e tem `Tests:` não-N/A. Ela é pulada, por tipo de tarefa, nos prefixos DOCUMENT, CHORE e RESEARCH e nos planos só de configuração ou de harness; num plano que roda a specify, os steps de configuração ou de harness usam `Scenarios: N/A (motivo)` (seção "Compatibilidade"). Ao pular, o plano traz a linha `Specify: skipped -- <motivo>`. A grill continua valendo (CYC-002). Alternativas rejeitadas: nunca pular (obriga Gherkin para um README) e pular por escolha livre (vira opcional, o que H-009 não mede).

- **Quem decide**: o `/plan` aplica a regra e registra o motivo; o designer pode contestar na revisão do plano.
- **Critério de aceitação**: plano sem `*.feature` aprovado contém a linha `Specify: skipped -- <motivo>`; plano com algum step de comportamento observável e `Tests:` não-N/A, e sem essa linha, tem pasta `features/<slug>/` com `.feature` aprovado.

### CYC-005 -- Escrita do plano

A terceira fase do PLAN escreve o plano a partir de `intent.md` e dos `.feature` aprovados. O cabeçalho referencia a pasta por `Feature: <slug>`. Todo step com `Tests:` não-N/A declara os cenários que cobre (campo `Scenarios:`; definição do campo e da versão do formato na seção "Compatibilidade").

- **Quem decide**: `/plan` escreve; designer aprova o plano (fluxo existente do `/plan`).
- **Critério de aceitação**: o plano tem `Feature: <slug>` e todo step com `Tests:` não-N/A tem `Scenarios:` apontando para chaves de cenário que existem em `index` do `scenarios.lock.json` (emenda 000012, CYC-028). Plano de pesquisa ou documentação não cria pasta nem `Feature:`.

### CYC-006 -- Invocação avulsa `--grill` e `--specify` `[default; aceito 2026-10-06]` (decisão pendente 1 = B)

As fases são internas ao `/plan`. Cada uma também poderá ser invocada avulsa (`/plan --grill`, `/plan --specify`) para repetir só a entrevista ou só o Gherkin depois de mudança de intenção. Neste contrato as flags foram **reservadas em 2026-10-06 e implementadas pelos planos 000009 e 000011** (`grill-phase.md` GRL-014, `specify-phase.md` SPC-016, `plan/SKILL.md`): o nome e o sentido ficaram fixados aqui, a implementação vive nesses arquivos. Alternativa rejeitada: skills `/grill` e `/specify` separadas (bifurca o ciclo de H-008).

- **Quem decide**: designer, no plano que implementar as fases.
- **Critério de aceitação**: na data deste contrato nenhum texto executável das flags existia em `SKILL.md`; hoje existe (planos 000009 e 000011) e este contrato as registra como "reservadas em 2026-10-06; implementadas".
- **Implementação**: `--grill` implementada pelo plan-000009 (`grill-phase.md`, GRL-014); `--specify` implementada pelo plan-000011 (`specify-phase.md`, SPC-016).

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
2. Sem `.feature` aprovado não há plano v2 (plano v1 segue o fluxo existente; plano com `Specify: skipped` é v2 sem `Feature:`, CYC-018).
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
- **Medida**: ver `.claude/references/general/drift-metric.md` e `.claude/references/general/drift-control-protocol.md`. O degrau teste -> código + portão (D3) é reportado em duas partes, D3a (verdade: o cenário com teste passa no código e no portão) e D3b (excesso: linha ou ramo tocado pela feature sem cenário que o cubra), sempre separadas (DRM-001).

### CYC-017 -- Onde roda o teste-primeiro `[default; aceito 2026-10-06]` (decisão pendente 5 = A)

O teste-primeiro roda dentro do `/implement`, por step, consumindo o portão `--fast` e os hooks existentes sem mudá-los. Alternativa rejeitada: skill separada `/build`. A seção "IMPLEMENT" abaixo detalha o primeiro degrau em código: teste vermelho pelo motivo certo, por cenário, antes do código. Cleaner e Hardener ficam fora (CYC-019).

- **Quem decide**: designer.
- **Critério de aceitação**: nenhuma skill `/build` existe; o `/implement` aponta para este contrato; gate, hooks e `settings` não aparecem em diff de plano que só altera este contrato.

### CYC-018 -- Versão do formato de plano `[default; aceito 2026-10-06]` (decisão pendente 6 = B)

Plano novo sai `plan_format_version: 2` nos dois casos (`Specify: approved` ou `Specify: skipped`, PFS-013). Em v2 com `Specify: approved`, todo step declara `Scenarios:` (chaves de cenário, ou `N/A (motivo)` para step sem comportamento observável); em v2 com `Specify: skipped`, nenhum step tem `Tests:` não-N/A de comportamento observável. Plano v1 (ou sem versão) permanece **válido para sempre** (D-008); a recusa vale só para v2. Detalhes na seção "Compatibilidade".

- **Quem decide**: designer.
- **Critério de aceitação**: um plano v1 existente é lido pelo `/plan` e pelo `/implement` sem mudança de resultado; só um plano v2 `approved` com step sem `Scenarios:` (inclusive `Tests: N/A`, PFS-003) é classificado como inválido.

### CYC-019 -- O que o contrato não faz

Este contrato **não** define:

- validador de Gherkin nem runner de cenários (plan-000010);
- fórmula de divergência nem estudo de controle (plan-000008);
- Cleaner, Hardener ou o `--pipeline` do `/implement` (plan-000013);
- a implementação executável das fases ou das flags de CYC-006.

Ele também não muda o portão, os hooks ou os denies (S2).

- **Quem decide**: designer.
- **Critério de aceitação**: nenhum texto deste arquivo traz fórmula, regex de validador ou prompt executável de Cleaner/Hardener; um plano que precise de um deles cria sua própria regra e a cita aqui por emenda (CYC-014).
- **Implementação**: convenção e validador de Gherkin em `.claude/references/general/gherkin-spec-format.md` (GHK-001..019) e `.claude/skills/scripts/check_features.py` (plan-000010); o estado e a chave do runner em CYC-027.

---

## Decisões pendentes do plan-000007 e o default adotado

| # | Decisão | Default adotado | Regra |
|---|---|---|---|
| 1 | Forma das fases grill e specify | B: internas ao `/plan`, flags avulsas (reservadas em 2026-10-06; implementadas pelos planos 000009 e 000011) `[default; aceito 2026-10-06]` | CYC-006 |
| 2 | Quando a specify é pulada | A: por tipo de tarefa, com `Specify: skipped -- <motivo>` `[default; aceito 2026-10-06]` | CYC-004 |
| 3 | Layout por feature | A: `features/<slug>/` `[default; aceito 2026-10-06]` | CYC-015 |
| 4 | Definição de divergência | C: composta, por degrau `[default; aceito 2026-10-06]` | CYC-016 |
| 5 | Onde roda o teste-primeiro | A: dentro do `/implement`, por step `[default; aceito 2026-10-06]` | CYC-017 |
| 6 | Versão do formato de plano | B: `plan_format_version: 2` `[default; aceito 2026-10-06]` | CYC-018 |

---

## Compatibilidade

Esta seção fixa a versão do formato de plano (CYC-018) e o campo `Scenarios:`. Definição do campo: `.claude/references/template/plan-step.md`.

**Campo `Scenarios:`.** Linha de metadados do step, obrigatória em v2 com `Specify: approved` em todo step (com ou sem `Tests:`) e ausente em v1: lista de chaves de cenário `<slug>/<arquivo>.feature::<nome>` (emenda 000012, CYC-028; antes: tags `@REQ-` ou nomes), tiradas de `index` do `scenarios.lock.json` da `Feature: <slug>` do plano, que o step entrega. `N/A (motivo)` é permitido só para step sem comportamento observável (documentação, configuração, harness, refactor com cobertura prévia), inclusive quando o step tem `Tests:` não-N/A; o motivo é obrigatório e satisfaz a obrigatoriedade. Em v2 com `Specify: skipped` não há `Feature:` nem chaves: nenhum step tem `Tests:` não-N/A de comportamento observável (PFS-013), e `Scenarios: N/A (motivo)` justifica a exceção.

**Regra de versão.**

| Cabeçalho do plano | `Scenarios:` | Situação |
|---|---|---|
| `plan_format_version: 2` com `Specify: approved` | obrigatório em todo step (chaves, ou `N/A (motivo)`) | step sem `Scenarios:` torna o plano **inválido** (PFS-003, PFS-006) |
| `plan_format_version: 2` com `Specify: skipped` | sem chaves; nenhum step com `Tests:` não-N/A de comportamento observável | PFS-013 recusa o contrário |
| `plan_format_version: 2` | `N/A (motivo)` em step sem comportamento observável (com ou sem `Tests:`) | válido |
| `plan_format_version: 1` ou ausente | ausente | **válido para sempre**; `/plan` e `/implement` o leem como antes; no máximo advisory, nunca bloqueio |

**O que o `/implement` faz com `Scenarios:` ausente em v2.** Para a execução e informa qual step está sem `Scenarios:`. Não corrige o plano nem inventa cenário: a correção é do `/plan` e do designer. Em v1 não faz nada diferente do que fazia.

**Estado do `/implement` (atualizado pelo plan-000012).** O Auto Mode (Phase 0, passo 3, version check) aceita `plan_format_version: 2`: roda `check_plan_scenarios.py` e **para**, sem corrigir o plano, se o exit for diferente de 0; com exit 0 executa os steps como escritos. O ramo teste-primeiro por cenário (CYC-020 a CYC-024) é do plan-000013.

**Estado da recusa.** A recusa executável do v2 inválido é `.claude/skills/scripts/check_plan_scenarios.py` (plan-000012; regras `PFS-001..015` em `.claude/references/general/plan-from-scenarios.md`). As fixtures em `.claude/skills/scripts/tests/fixtures/plan_format/` (dois planos v1 reais, um v2 válido, um v2 inválido) documentam os casos.

## IMPLEMENT

> Regras CYC-020 a CYC-026. Esta seção diz o que o IMPLEMENT exige por step com cenário; ela **cita** o portão e os hooks existentes e não os altera (CYC-024).

### CYC-020 -- Quais steps seguem o teste-primeiro

Seguem o teste-primeiro os steps com `Scenarios:` preenchido por chaves de cenário (plano v2, CYC-018, CYC-028). Step sem cenário (infra, configuração, harness, `Tests: N/A`, plano com `Specify: skipped`, plano v1) segue o caminho atual do `/implement`, sem mudança (TDD red-green por `Tests:` quando não-N/A, ou ordem legada).

- **Quem decide**: o plano (campo `Scenarios:`); o designer na aprovação do plano.
- **Critério de aceitação**: um plano v1 e um step com `Scenarios: N/A (motivo)` produzem o mesmo fluxo de `/implement` da v0.10.1; só step com chaves de cenário entra em CYC-021 a CYC-023.

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
- **Implementação**: `.claude/references/general/implement-test-first.md` (ITF-010, ITF-011; papéis `cleaner` e `hardener`), plan-000013; ver CYC-030.

### CYC-026 -- Runner de Gherkin pendente

O runner que executa os `.feature` e emite o relatório do runner contract é **pendente do plan-000010**. A recomendação é pytest-bdd como primeiro adaptador para Python, apenas como recomendação: o contrato descreve o relatório (Cucumber JSON com chave de cenário, CYC-012) e não nomeia ferramenta como requisito. Enquanto o runner não existe, o projeto declara D2 e D3 `não medido` para os cenários sem runner, nunca como falha (T6).

- **Quem decide**: designer, no plan-000010.
- **Critério de aceitação**: nenhuma regra desta seção exige uma ferramenta específica; um projeto sem runner produz relatório com `não medido` e a razão dita.
- **Implementação**: plan-000010 descreve o relatório e prova o primeiro adaptador (`gherkin-spec-format.md`, seções 8 e 10; CYC-027).

### CYC-027 -- Estados e chave de cenário do runner contract (emenda 000010)

O relatório do runner é o Cucumber JSON (CYC-012). Ele liga o `Scenario` ao teste pela **chave de cenário** `<slug>/<arquivo>.feature::<nome>` (os dois últimos componentes do `uri` do `.feature` e o `name` do cenário; nome único por arquivo, GHK-010) e traz as tags `@REQ-` do cenário na lista `tags`. Os estados do DRM-003 (`passed`, `failed`, `error`, `skipped`, `xfail`, `undefined`, `absent`) não são todos nativos do Cucumber (`passed`, `failed`, `skipped`, `pending`, `undefined`, `ambiguous` por step): a tabela de mapeamento está em `.claude/references/general/gherkin-spec-format.md`, seção 8. Regras: `failed` exige mensagem de asserção (senão é `error`); `xfail` vem da tag; `Scenario Outline` é uma unidade e vale o pior estado das suas linhas; cenário que o runner não emite fica `absent` (ou `skipped` se tem tag de desativação). Um adaptador pode juntar outro relatório do mesmo runner (por exemplo o JUnit) quando o Cucumber JSON omite casos; o contrato não muda.

- **Quem decide**: designer; o adaptador do runner (plan-000013) e a junção (plan-000014) aplicam.
- **Critério de aceitação**: dado o mesmo Cucumber JSON, dois consumidores obtêm os mesmos estados por chave; nenhum cenário `skip`, `xfail` ou sem teste é contado como verde; nenhum `error` ou `undefined` é contado como vermelho pelo motivo certo (CYC-022).
- **Ruptura que pode provocar** (CYC-014): ao power dev, "meu cenário aparece como `undefined` e eu achava que estava vermelho". Registro do power dev; nada novo ao citizen.

### CYC-028 -- Plano v2 liga cada step aos cenários aprovados (emenda 000012)

O plano v2 traz `Feature: <slug>` e `Specify: approved (rev N)` (ou `Specify: skipped -- <motivo>`, sem `Feature:`). O campo `Scenarios:` de cada step lista as **chaves de cenário** (`<slug>/<arquivo>.feature::<nome>`, as de `index` do `scenarios.lock.json`, CYC-027), ou `N/A (<motivo>)`; a tag `@REQ-` não vale no lugar da chave. O step que lista o cenário é o dono do teste (um dono por cenário). A cobertura vale nos dois sentidos: step que muda comportamento sem cenário e cenário aprovado sem step são recusados; cenários `stale` ou `rev` velho recusam o plano. A recusa é de `check_plan_scenarios.py` (`.claude/references/general/plan-from-scenarios.md`, PFS-001..015); plano v1 nunca é recusado (CYC-018).

- **Quem decide**: designer; o `/plan` escreve e corrige, o verificador recusa.
- **Critério de aceitação**: `check_plan_scenarios.py` sai 0 sobre todo plano v2 salvo como pronto e sai 1 com PFS-006, PFS-009 ou PFS-011 nos casos dessas regras; um plano v1 sai 0 sem leitura do corpo.
- **Ruptura que pode provocar** (CYC-014): ao power dev, "meu plano foi recusado porque um cenário não tem step". Registro do power dev; ao citizen só chega o achado em voz controlada se o agente não conseguir corrigir em 3 tentativas.

### CYC-029 -- Proxy do skip: a grill classifica antes, o verificador confere depois (emenda 000012)

A classificação "com código / sem código" da grill (GRL-012) decide **antes** se a specify roda (CYC-004). `check_plan_scenarios.py` (PFS-013) confere **depois**: plano `Specify: skipped` com step de `Tests:` não-N/A e sem `Scenarios: N/A (<motivo>)` é recusado, sem promover a tarefa à specify sozinho; o agente volta à grill ou à specify, ou o designer justifica o `Tests: N/A`.

- **Quem decide**: designer; o verificador recusa.
- **Critério de aceitação**: plano pulado com step de teste e sem N/A justificado sai 1 com PFS-013; todos os steps `Tests: N/A` saem 0.
- **Ruptura que pode provocar** (CYC-014): ao power dev, "disse que não tinha código e o plano tem teste". Registro do power dev.

### CYC-030 -- O motor do teste-primeiro e onde ele grava (emenda 000013)

O teste-primeiro de CYC-020 a CYC-025 roda pela norma `.claude/references/general/implement-test-first.md` (`ITF-001..025`): vermelho pelo motivo certo decidido por `build_checks.py red-check` (R1 a R8; `failed` só com `AssertionError` no `Então`, `undefined` e `error` não contam, CYC-022), papéis com contexto curto (`scenario-tester`, Coder, `cleaner`, `hardener`), teto de 3 tentativas por fase e escalada ao humano. O registro do build mora em `features/<slug>/gate.json`, chave aditiva `build` (os campos `schema_version`, `fast`, `full` e `ts` de CYC-024 não mudam), e é exportado para os arquivos que o relatório de divergência lê (`runner/cucumber.json`, `drift/red-reason.json`, `drift/coverage.json`, `baseline_moved`). Plano v2 com `GATE_FULL_CMD` roda `full` uma vez no fim; sem ele o D3a fica `não medido`.

- **Quem decide**: as ferramentas (T1); o humano nas escaladas e no baseline (S2).
- **Critério de aceitação**: um step dono só sai do vermelho com `red-check` exit 0; o `gate.json` de uma feature construída tem `build.scenarios[<chave>].red.reason_ok`; plano v1 tem a mesma rota de antes (`build_checks.py route`).
- **Ruptura que pode provocar** (CYC-014): ao citizen, a demonstração por cenário ("não demonstrado") e o mutante recontado como pergunta ("isso importa para você?"); ao power dev, "meu teste vermelho foi recusado por R3".

---

## Emendas do item 9 (emenda 000015)

Integração do ciclo default (plan-000015). Só acréscimos: nenhuma regra anterior é removida ou renumerada. Decisões pendentes do plan-000015, todas `[default; aceito 2026-10-06]`: 1 = A (o `/implement` congela o M1), 2 = A (`--reconcile` grava `draft`), 3 = A (nenhuma chave nova), 4 = B (um guia pt-BR e ponteiros), 5 = A (bump minor), 6 = C (o upgrade só atualiza o plugin já instalado), 7 = A com gatilho para B (o Stop hook não muda agora), 8 = A (os checks rodam sem argumentos, sem agregador).

**Já fixado antes (emenda 000015 só aponta).** (a) O campo `Scenarios:` usa a chave `<slug>/<arquivo>.feature::<nome>` (CYC-028, emenda 000012): o texto "lista de `@REQ-...` ou nomes de cenário" do plan-000007 fica substituído; a tag `@REQ-` continua sendo a tag do cenário e a ligação REQ-cenário, não a chave de step. (b) O proxy do skip: a classificação da grill decide antes, `PFS-013` confere depois (CYC-029). O texto do próprio plano 000007 (artefato aprovado, imutável) recebe só um adendo do orquestrador.

### CYC-031 -- Quem congela o M1 e quando (emenda 000015) `[default; aceito 2026-10-06]` (decisão pendente 1 = A)

O `/implement` congela o M1 **uma vez, no fim do plano v2** com `Feature: <slug>` e `Specify: approved`, depois da rodada `full` (ou registrando `full: null` quando não há `GATE_FULL_CMD`): `drift_report.py --feature <slug> --plan <plano> --moment M1 --freeze --at <UTC>` (procedimento: `implement-test-first.md`, item 9 e seção "Congelar o M1"). Se o `M1.json` já existe, o script recusa (exit 2) e o `/implement` só avisa "M1 já congelado"; se o script falta ou falha por outro motivo, avisa e segue. O freeze **nunca** reprova o `/implement`. Plano v1, plano sem `Feature:` e `Specify: skipped` não congelam nada. Alternativas rejeitadas: o `/reflect` congelar (dias depois, a árvore já mudou: o M1 deixaria de ser M1); o designer congelar à mão (depende de memória; o piloto perde dados comparáveis).

- **Quem decide**: o `/implement` executa; o script recusa a sobrescrita.
- **Critério de aceitação**: depois de um plano v2 com `Feature: <slug>`, existe `features/<slug>/drift/M1.json`; rodar o freeze de novo sai 2 e deixa o arquivo igual byte a byte; plano v1 não cria `drift/`.
- **Ruptura que pode provocar** (CYC-014): ao power dev, "o M1 já existia e eu queria outro". Registro do power dev; ao citizen, nada.

### CYC-032 -- Reconciliação de `scenarios:` quando a aprovação fica velha (emenda 000015) `[default; aceito 2026-10-06]` (decisão pendente 2 = A)

Quando a grill reabre a intenção (`status: grilling`) ou o lock deixa de bater (`check_specify.py --status` = `stale`), `check_specify.py --reconcile [<slug>]` troca `scenarios: approved` por `scenarios: draft` **só** no `intent.md` daquela feature, preservando o resto do arquivo byte a byte e o `scenarios.lock.json`. A escrita é atômica, idempotente e confinada a `features/<slug>/`. A grill chama `--reconcile <slug>` logo depois de voltar o `status` a `grilling` (GRL-011); qualquer consumidor que veja `stale` pode chamá-lo. O `--status` continua a fonte de verdade: depois da reconciliação ele segue dizendo `stale` (com a razão `sem-campo` e as razões de antes) até a specify reaprovar. Nenhum consumidor decide pelo campo: `check_features.py --matrix` expõe `scenarios_state` (do `--status`) ao lado de `scenarios_approved` (o valor do disco). Alternativas rejeitadas: gravar um valor novo `stale` (emenda aos esquemas de três planos para um valor a mais); não gravar nada (o campo mentiria para quem lê o arquivo sem rodar script).

- **Quem decide**: o verificador (`check_specify.py`); a grill o chama.
- **Critério de aceitação**: depois de editar um `.feature` aprovado, `--reconcile <slug>` grava `scenarios: draft` e muda só essa linha; a segunda execução não muda nada; um slug fora de `features/` sai 2 sem escrever.
- **Ruptura que pode provocar** (CYC-014): ao citizen, "os cenários que eu aprovei voltaram a rascunho". A grill diz isso em uma frase ao reabrir; é o aviso que o citizen precisa para pedir nova aprovação.

### CYC-033 -- O ciclo default entra por upgrade de tag (emenda 000015) `[default; aceito 2026-10-06]` (decisão pendente 3 = A)

O ciclo default (grill, specify, plano v2, teste-primeiro, relatório por degrau) chega pela tag nova do harness e **só age onde há `features/<slug>/intent.md` ou plano v2**. Plano v1 é válido para sempre (CYC-018, D-008). Não há chave de ligar ou desligar (`CYCLE_MODE`, `--no-grill`): uma chave global seria um preset com outro nome (decisão fechada "sem preset") e contaminaria a medida de H-009. A saída para quem não quer a escada é a que já existe: `--light`, tarefa sem código (`Specify: skipped -- <motivo>`) e `--roadmap`. O braço de controle do piloto usa a **tag anterior pinada**, não uma chave. Os quatro checks do ciclo (`check_intent.py`, `check_features.py`, `check_specify.py`, `check_plan_scenarios.py`) rodam sem argumentos no `run_all_checks.py` e saem 0 com "nada a verificar" quando não há `features/` nem plano v2.

- **Quem decide**: designer.
- **Critério de aceitação**: num projeto sem `features/` e só com planos v1, atualizar para a tag nova não muda nenhum arquivo do projeto, e o `run_all_checks.py` devolve o mesmo conjunto de falhas de antes, com os quatro checks em PASS.
- **Ruptura que pode provocar** (CYC-014): ao citizen, "o /plan agora me faz perguntas antes de escrever o plano". O guia pt-BR (`docs/how-to/ciclo-default.pt-BR.md`) explica o porquê e a saída.

### CYC-034 -- Quem escreve os registros de leitura e em que registro o relatório fala (emenda 000015)

- `features/adoption.json` (`{"schema_version": 1, "adopted_at": "AAAA-MM-DD"}`): a grill o escreve **uma vez**, quando cria a primeira pasta `features/<slug>/` do projeto e o arquivo não existe; nunca o reescreve. É a marca da leitura reversa (DRP-014).
- `features/<slug>/drift/retraducao-pos-codigo.md`: o agente do `/reflect`, em primeira pessoa, **a partir da matriz** (cenários demonstrados, não demonstrados, não medidos), antes de rodar o relatório do Step B1, uma linha por REQ terminada por `(REQ-<slug>-NNN)` (DRP-010). Sem ele: `NM-SEM-RETRADUCAO-POS-CODIGO`.
- Registro do relatório de divergência: `--citizen` quando o `intent.md` da feature tem `scenarios_contract_by: ninguem` (ninguém lê código: a retradução é obrigatória, H-003) ou quando o designer pede; nos outros casos `--md`, e o `/reflect` oferece o `--citizen` (DRP-020).
- O `run_all_checks.py` não roda o relatório de divergência: `drift_report.py` não é um `check_*` e não bloqueia (DRP-019).

- **Quem decide**: designer; a grill, o `/reflect` e o `/implement` escrevem cada um o seu.
- **Critério de aceitação**: num projeto com uma feature, `features/adoption.json` existe com a data da primeira grill; um REQ com `scenarios_contract_by: ninguem` recebe o relatório no registro do citizen.
- **Ruptura que pode provocar** (CYC-014): ao citizen, a retradução depois do código lida ao lado da de antes ("eu pedi isso, ele entendeu aquilo").

### Ordem de edição dos `SKILL.md` (emenda 000015)

Seis planos editaram os mesmos arquivos, nesta ordem. A medida final está no Step 7 do plan-000015 e em `.claude/skills/scripts/check_docs_skill_body_length_baseline.md`.

| Ordem | Plano | `SKILL.md` de corpo que ele toca | Natureza |
|---|---|---|---|
| 1 | 000007 | `_internal/plan/standard`, `implement` | uma linha de ponteiro para este contrato |
| 2 | 000009 | `_internal/plan/standard`, `plan` | fase grill, flag `--grill` |
| 3 | 000011 | `_internal/plan/standard`, `plan` | fase specify, flag `--specify`, `Specify: skipped` |
| 4 | 000012 | `plan`, `_internal/plan/standard`, `implement` | `plan_format_version: 2`, recusa de step sem cenário, parada do `/implement` |
| 5 | 000013 | `implement` | `--pipeline`, ramo v2 (teste-primeiro), fim do plano com o freeze do M1 |
| 6 | 000014 | `reflect`, `explain`, `_internal/explain/drift` | relatório por degrau |
| 7 | 000015 | nenhum corpo novo | a fiação do M1 já estava no passo 12 do `/implement` (000013); o detalhe vai para as referências |

Medida final (2026-10-06, `check_docs.py --plugins skill-body-length --verbose`): `plan` 72/500, `implement` 254/500, `explain` 65/300, `reflect` 248/300, `help` 70/150, `seja-setup` 85/300; nenhum acima de 90% do tier. `_internal/plan/standard/SKILL.md` (141 linhas no arquivo) e `_internal/explain/drift/SKILL.md` (156) não são medidos pelo plugin. `Specify: skipped` aparece uma vez no `_internal/plan/standard/SKILL.md`; `--grill` e `--specify` uma vez cada na tabela de argumentos do `/plan`; `--pipeline` uma vez na do `/implement`; `plan_format_version: 2` só no C3 do modo standard.

Regra para o próximo plano que tocar estes arquivos: ler esta tabela, acrescentar a sua linha e manter o detalhe nas referências normativas (`grill-phase.md`, `specify-phase.md`, `plan-from-scenarios.md`, `implement-test-first.md`, `drift-report.md`), com uma linha de ponteiro no `SKILL.md`.
