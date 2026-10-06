---
designer_description: "When a report, a plan or the pilot needs to say how far what was built is from what was intended, I'm the normative definition of divergence per step of the ladder (D1, D2, D3a, D3b): the unit, the source, the states, the formula, the report shape and the not-measured codes -- so every item counts the same thing the same way."
---

# GENERAL - DRIFT METRIC

> Definição normativa da divergência por degrau (roadmap-000006, plan-000008; H-009 no §3 subseção 2.9 e D-004, D-007 em `product-design/product-design-as-intended.md`). Este arquivo diz **o que se conta, de onde vem o dado e como se calcula**. Ele não executa nada: o calculador é do plan-000014; o runner, do plan-000010; o registro do teste-primeiro, do plan-000013.
>
> Idioma: pt-BR (prosa), identificadores em en-US. Os termos de vocabulário (degrau, par, estados) vêm de `extended-cycle-contract.md` (CYC-009, CYC-010, CYC-016). Marcação: `[default; aceito 2026-10-06]` indica uma decisão pendente do plan-000008 que o designer aceitou no default.
>
> Cada regra tem identificador estável `DRM-NNN`, campo **Quem decide** e campo **Critério de aceitação**.

## Visão geral

```
brief --> intent.md --> .feature --> teste --> código + gate
  D0        D1           D2          D3a / D3b
(fora do D)
```

O relatório é um **vetor** `(D1, D2, D3a, D3b)`, com `n` e `não medido` de cada um. Não há número único nem pesos (CYC-016). Um degrau de maior divergência pode ser destacado por texto, nunca somado.

---

## Regras

### DRM-001 -- Unidade, estados e fórmula

A unidade de cada degrau é o item do degrau de cima. A pergunta é se o degrau de baixo o cobre.

| Degrau | Unidade |
|---|---|
| D1 intenção -> cenário | REQ (`REQ-<slug>-NNN` de `intent.md`) |
| D2 cenário -> teste | cenário (`Scenario` de `*.feature` com tag `@REQ-...` que aponta para um REQ existente; cenário sem tag ou com tag órfã fica fora do D e vai para as leituras, DRM-008) |
| D3a teste -> código (verdade) | cenário que tem teste (D2 coberto) |
| D3b teste -> código (excesso) | linha ou ramo tocado pela feature |

Estados (CYC-010): `coberto`, `descoberto`, `não medido`.

Fórmula do degrau: `D = descobertos / (cobertos + descobertos)`.

- `não medido` fica **fora do denominador** e aparece sempre ao lado, com a razão (DRM-009).
- Denominador zero: `D` é indefinido e se escreve `"n/a"`, nunca `0`.
- Os números são brutos: numerador, denominador e `n`; nada de arredondar para "limpar" amostra pequena. `D` sai arredondado a 4 casas decimais no JSON; as contagens nunca são arredondadas.
- O cálculo é determinístico e não usa LLM. A mesma matriz dá o mesmo relatório.

- **Quem decide**: designer.
- **Critério de aceitação**: dada uma matriz, duas execuções do calculador dão relatórios idênticos; nenhum degrau com denominador zero traz `0`; nenhum `não medido` entra no denominador.

### DRM-002 -- D1, intenção -> cenário

| Linha | Conteúdo |
|---|---|
| **Mede** | REQs sem cenário. |
| **Fonte** | `intent.md` x `*.feature` da pasta `features/<slug>/`. |
| **Coberto** | REQ aprovado com pelo menos um cenário com a tag `@REQ-<slug>-NNN` em `.feature` aprovado. |
| **Descoberto** | REQ aprovado sem nenhum cenário com a tag. |
| **Não medido** | `intent.md` não aprovado (`NM-INTENCAO-NAO-APROVADA`); `Specify: skipped` (`NM-SPECIFY-PULADA`); `.feature` desatualizado ou ausente em relação ao `intent.md` aprovado (`NM-CENARIOS-STALE`). |
| **Escrito por** | `intent.md`: plan-000009 (grill) e plan-000011 (aprovação); `.feature` e validador de tags: plan-000010 e plan-000011; junção: plan-000014. |

- **Quem decide**: designer.
- **Critério de aceitação**: um REQ aprovado sem tag em nenhum cenário conta como `descoberto`; um `intent.md` em `grilling` produz D1 `não medido` com o código dito, e não erro.

### DRM-003 -- D2, cenário -> teste

| Linha | Conteúdo |
|---|---|
| **Mede** | Cenários sem teste executável. |
| **Fonte** | `*.feature` x relatório do runner (chave de cenário, CYC-012). |
| **Coberto** | Cenário com teste vinculado que foi **coletado e executado** (resultado `passed` ou `failed`; não `skipped`, não `xfail`). |
| **Descoberto** | Cenário sem teste vinculado, ou com teste vinculado só como `skipped` ou `xfail`. |
| **Não medido** | Runner de Gherkin indefinido para a stack (`NM-SEM-ADAPTADOR-RUNNER`) ou relatório ausente (`NM-SEM-RUNNER`). |
| **Escrito por** | `.feature`: plan-000010 e plan-000011; teste e relatório do runner: plan-000013 (IMPLEMENT); junção: plan-000014. |

Um teste que termina em `error` ou `undefined` foi executado e não passou: conta como `coberto` em D2 e `descoberto` em D3a. O D2 pergunta se o teste existe, o D3a pergunta se ele diz a verdade.

- **Quem decide**: designer.
- **Critério de aceitação**: cenário só com `skipped` ou `xfail` é `descoberto` em D2; projeto sem runner dá D2 `não medido` com a razão, e não erro (CYC-012, CYC-026).

### DRM-004 -- D3a, teste -> código (verdade)

| Linha | Conteúdo |
|---|---|
| **Mede** | Cenários cujo teste não passa no código final. |
| **Fonte** | Relatório do runner + `gate.json` (`full`) + registro "vermelho pelo motivo certo". |
| **Coberto** | Teste verde **e** `gate.json` com `full` PASS **sem** baseline aceito **e** `red_reason_ok` verdadeiro. |
| **Descoberto** | Teste vermelho (`failed`, `error`, `undefined`), ou `full` FAIL, ou PASS só com baseline aceito (`PASS_WITH_BASELINE`), ou `red_reason_ok` falso. |
| **Não medido** | `full` nunca rodou: `gate.json` ausente, `fast`-só, ou `full: null` (`NM-SEM-GATE`); sem registro de vermelho (`NM-SEM-REGISTRO-VERMELHO`); D2 não medido (a razão de D2 vale). |
| **Escrito por** | Teste, relatório, `gate.json` e registro: plan-000013 (IMPLEMENT); junção: plan-000014. |

A população do D3a são os cenários com D2 `coberto`. Cenário sem teste já está contado em D2 e não entra duas vezes.

- **Quem decide**: designer.
- **Critério de aceitação**: com `full` PASS e baseline aceito, nenhum cenário é `coberto` em D3a; com `full` nunca rodado, D3a é `não medido` mesmo com todos os testes verdes.

### DRM-005 -- D3b, teste -> código (excesso)

| Linha | Conteúdo |
|---|---|
| **Mede** | Código tocado que nenhum teste de cenário exercita. |
| **Fonte** | Cobertura por linha e ramo **só dos testes ligados a cenários** x diff da feature. |
| **Coberto** | Linha ou ramo tocado exercitado por pelo menos um teste de cenário. |
| **Descoberto** | Linha ou ramo tocado e não exercitado (código sem cenário: excesso). |
| **Não medido** | Cobertura por cenário indisponível (`NM-SEM-COBERTURA`); base do diff ausente (`NM-SEM-BASE-DIFF`); portão ausente (`NM-SEM-GATE`). |
| **Escrito por** | Cobertura por cenário: plan-000013 e portão; diff: plan-000014; junção: plan-000014. |

Código fora de `features/` e fora do diff da feature é `legado: não medido`, não `descoberto` (CYC-011).

- **Quem decide**: designer.
- **Critério de aceitação**: código tocado só por teste de legado conta como `descoberto`; código fora do perímetro da feature não aparece no denominador.

### DRM-006 -- Colunas derivadas da matriz `[default; aceito 2026-10-06]` (decisão pendente 4 = B)

O esquema de `feature-layout.md` não muda. As colunas abaixo são **derivadas**: o calculador as obtém juntando `*.feature`, relatório do runner, `gate.json`, registro do teste-primeiro e diff. Elas não são escritas à mão.

| Coluna | Valores | Regra de derivação |
|---|---|---|
| `scenario_status` | `approved`, `stale`, `draft`, `missing` | resultado de `check_specify.py --status` (plan-000011); `approved` só se o status diz `approved` |
| `test_result` | `passed`, `failed`, `error`, `skipped`, `xfail`, `undefined`, `absent` | estado do teste ligado ao cenário pela chave de cenário; sem vínculo, `absent` |
| `red_reason_ok` | `true`, `false`, `null` | registro do teste-primeiro (CYC-022): `true` se o vermelho inicial foi `failed` por asserção; `null` se não há registro |
| `touched_uncovered` | inteiro | linhas e ramos tocados menos os exercitados por teste de cenário; o total tocado vem junto (`touched_total`) |
| `baseline_moved` | `true`, `false`, `null` | diff de `quality-baseline.json` entre o início e o fim da feature; `null` se não há como saber |

Se o plan-000014 descobrir que alguma coluna não é derivável, a saída é uma **emenda aditiva** ao `feature-layout.md`, registrada como emenda (CYC-014). Não é feita aqui.

- **Quem decide**: designer.
- **Critério de aceitação**: cada coluna tem fonte e regra; nenhuma coluna exige edição manual de `gate.json` (S2).

### DRM-007 -- Formato do relatório

Contrato de dados (JSON com `schema_version: 1`):

```json
{
  "schema_version": 1,
  "feature": "<slug>",
  "momento": "M1",
  "degraus": {
    "D1":  {"n": 0, "cobertos": 0, "descobertos": 0, "nao_medidos": 0, "D": "n/a", "razao_nm": []},
    "D2":  {"n": 0, "cobertos": 0, "descobertos": 0, "nao_medidos": 0, "D": "n/a", "razao_nm": []},
    "D3a": {"n": 0, "cobertos": 0, "descobertos": 0, "nao_medidos": 0, "D": "n/a", "razao_nm": []},
    "D3b": {"n": 0, "cobertos": 0, "descobertos": 0, "nao_medidos": 0, "D": "n/a", "razao_nm": []}
  },
  "leituras": {
    "cadeia_completa": 0,
    "cenarios_orfaos": 0,
    "cenarios_sem_tag": 0,
    "escada_fechou_sem_capturar": false,
    "d0": {"estado": "nao_medido", "razao_nm": ["NM-SEM-INDICE-BRIEF"]},
    "o1": null
  },
  "ressalvas": []
}
```

- `n = cobertos + descobertos + nao_medidos`. `D` é número entre 0 e 1 ou `"n/a"`.
- `razao_nm` lista **todas** as razões aplicáveis (DRM-009), na ordem do catálogo.
- `leituras.o1` traz `{n, falham, O1}` quando há oráculo (controle, ver `drift-control-protocol.md`) e `null` caso contrário.
- `ressalvas` recebe, entre outras, `"amostra pequena"` (menos de 8 REQs) e `"D3a sem prova de vermelho"`.
- Tarefa sem medida possível (`Specify: skipped`, sem `features/`, plano v1) produz relatório curto: `{"schema_version": 1, "feature": ..., "momento": ..., "nao_aplicavel": true, "razao_nm": ["NM-..."]}`.
- Texto do relatório em voz controlada: frases curtas, termos fixos. Exemplo: "Intenção para cenário: 8 de 10 requisitos têm cenário. 2 não têm. Nenhum ficou sem medida."
- O relatório é tempo passado e não prescreve ("deveria", "considere" não entram).
- Destaque textual do degrau de maior `D` é permitido; empate é dito como empate. Nunca se soma.
- **Registro do citizen** (CYC-013, CYC-014): sem número técnico. Contagens de requisito e de cenário em palavras, ausências enumeradas, nenhum percentual. O vetor completo com `D` vai ao registro do power dev.

- **Quem decide**: designer.
- **Critério de aceitação**: o relatório tem as quatro linhas de degrau, cada uma com os três estados e as razões de `não medido`; nenhum campo traz número único; o calculador (plan-000014) reproduz as saídas de `.claude/skills/scripts/tests/fixtures/drift/casos.json`.

### DRM-008 -- Leituras fora do D

São contagens e alertas que acompanham o vetor. Não entram em nenhum `D`.

| Leitura | O que é |
|---|---|
| `cadeia_completa` | REQs com a cadeia inteira: tem cenário e **todos** os seus cenários estão `coberto` em D2 e D3a |
| `cenarios_orfaos` | cenário cuja tag aponta para REQ que não existe |
| `cenarios_sem_tag` | cenário sem tag `@REQ-` |
| `escada_fechou_sem_capturar` | alerta quando D1 = D2 = D3a = 0 e (O1 > 0 no controle, ou algum `adequado: nao` na auditoria semântica) |
| `d0` | degrau zero (DRM-010) |

- **Quem decide**: designer.
- **Critério de aceitação**: cenário sem tag não altera nenhum `D` e aparece em `cenarios_sem_tag`; o alerta de "escada fechou" só dispara com D1 = D2 = D3a = 0 e uma das duas evidências.

### DRM-009 -- Razões de `não medido`

Todo `não medido` traz um código e uma frase. O código é estável. Os códigos que o plan-000014 já cita ficam com este nome.

| Código | Degrau | Frase de relatório |
|---|---|---|
| `NM-INTENCAO-NAO-APROVADA` | D1 | "Eu não medi: você ainda não aprovou os requisitos." |
| `NM-SPECIFY-PULADA` | D1 | "Eu não medi: esta tarefa não teve cenários." |
| `NM-CENARIOS-STALE` | D1 | "Eu não medi: os cenários mudaram depois da aprovação." |
| `NM-SEM-ADAPTADOR-RUNNER` | D2, D3a | "Eu não medi: esta stack ainda não tem executor de cenários." |
| `NM-SEM-RUNNER` | D2 | "Eu não medi: não achei o relatório dos testes." |
| `NM-SEM-ADAPTADOR-GATE` | D3a, D3b | "Eu não medi: esta stack ainda não tem portão." |
| `NM-SEM-GATE` | D3a, D3b | "Eu não medi: o portão não rodou por inteiro." |
| `NM-SEM-REGISTRO-VERMELHO` | D3a | "Eu não medi: não há registro de que o teste falhou pelo motivo certo." |
| `NM-SEM-COBERTURA` | D3b | "Eu não medi: não há cobertura só dos testes de cenário." |
| `NM-SEM-BASE-DIFF` | D3b | "Eu não medi: não sei onde a feature começou." |
| `NM-SEM-M1` | delta | "Eu não medi a mudança: o estado da entrega não foi congelado." |
| `NM-SEM-INDICE-BRIEF` | D0 | "Eu não medi o que sobrou do pedido: as frases do pedido não foram indexadas." |

`NM-SEM-ADAPTADOR-*` é a forma do CYC-012 (stack sem adaptador degrada para `não medido`, nunca para falha): o adaptador **não existe**. `NM-SEM-RUNNER` e `NM-SEM-GATE` são a forma em que o adaptador existe e o dado do projeto está ausente.

- **Quem decide**: designer.
- **Critério de aceitação**: nenhum `não medido` aparece sem código; stack sem adaptador produz relatório, não erro.

### DRM-010 -- O que o D não vê

O vetor D mede presença de tag, de teste e de verde sobre o que **já virou** REQ. Ele **não** vê:

- **Omissão**: o que o brief pediu e nunca virou requisito nem "fora do escopo". É o degrau zero (D0).
- **Distorção**: o REQ que reinterpreta o pedido, o cenário que tem a tag e não captura o REQ, o teste que passa e não prova o cenário.
- **Racional, modelo conceitual, preferência de forma e crença sobre o usuário**: a escada é completa para comportamento operacionalizado e perde essas categorias (D-004).

**D0, o resíduo do brief.** D0 é a parcela do brief que não virou REQ nem item de "Fora do escopo". É **leitura fora do vetor D** e nunca portão (não há M0, DRM-012). Quando o grill indexa as frases do brief (plan-000009), o calculador lista as frases sem requisito e sem fora-do-escopo. Sem índice, D0 é `não medido` com `NM-SEM-INDICE-BRIEF`. D0 não tem `D` nem entra em contagem de cobertura.

**Auditoria semântica** (decisão pendente 1 = B `[default; aceito 2026-10-06]`). O julgamento "o cenário captura o REQ?" é humano e cego, por amostra, e vive numa **coluna própria**, `adequado: sim | parcial | nao`, em `audit.json`. Regras:

- todos os REQs do braço A (retrofit, ver `drift-control-protocol.md`) e pelo menos 30% dos REQs do braço B;
- a amostra é determinística: ordenar os REQs por `sha1(slug + ":" + req)` e tomar `ceil(30%)`;
- a coluna nunca altera nenhum `D`; ela entra no alerta de DRM-008;
- acima de ~40 REQs por braço, trocar por juiz LLM em contexto limpo com amostra humana de pelo menos 20% para medir concordância (alternativa C, registrada como emenda).

**Os três medidores de ganho do citizen.** Fora do D, o piloto registra três contagens que dizem se a aprovação do citizen foi reflexão ou ritual (D-004, H-009):

1. **Ajustes e recusas no specify**: quantas vezes o citizen pediu mudança ou disse "não é isso" antes de aprovar.
2. **Escapes de intenção antes do código vs depois**: itens em que a intenção se perdeu e foram achados antes do primeiro teste vermelho, contra os achados só depois do código.
3. **Mutantes virados em REQ**: mutantes sobreviventes que, recontados ao citizen como pergunta, viraram requisito novo.

Os três são contagens brutas. Se os três forem zero no piloto, a aprovação virou ritual (condição de refutação de H-009).

- **Quem decide**: designer.
- **Critério de aceitação**: este relatório nunca apresenta D0 ou a auditoria semântica dentro de um `D`; o texto "O que o D não vê" aparece em todo relatório completo do power dev; os três medidores têm o mesmo nome aqui, no protocolo e no registro de execução.

### DRM-011 -- Anti-gaming

D3a só vale quando:

1. o `gate.json` tem `full` PASS;
2. o baseline não foi aceito (`baseline_moved` falso; `--accept-baseline` é negado ao agente, S2);
3. o teste foi vermelho pelo motivo certo antes do código (`red_reason_ok` verdadeiro, CYC-022).

Se o registro do item 3 não existe, o estado é `não medido` (`NM-SEM-REGISTRO-VERMELHO`) para essa evidência e o relatório traz a **ressalva** "D3a sem prova de vermelho". PASS com baseline aceito conta como `descoberto`, com a ressalva dita. Teste que `skip` ou `xfail` não é verde (DRM-003).

- **Quem decide**: designer; o ratchet é só dele (H-008).
- **Critério de aceitação**: nenhum cenário é `coberto` em D3a sem as três condições; toda ausência de prova vira ressalva visível.

### DRM-012 -- Momentos M1 e M2

| Momento | Quando | Matriz |
|---|---|---|
| M1 | fim do IMPLEMENT, com o gate | congelada |
| M2 | REFLECT | regenerada, mesma fórmula |

A diferença `M2 - M1` é a **deriva depois da entrega**. O delta mostra numerador e denominador dos dois lados, porque o denominador pode mudar (REQ novo, REQ retirado). O delta numérico só existe quando os dois `D` são números. Sem M1 congelado: `NM-SEM-M1`, sem delta.

Não há M0 (aprovação do plano). D1 e D2 em M0 já são portão do contrato (CYC-008), não medida de divergência.

- **Quem decide**: designer.
- **Critério de aceitação**: o delta traz os dois lados; M1 existente não é sobrescrito (é do plan-000014).

### DRM-013 -- Casos limite

| Caso | Tratamento |
|---|---|
| `Specify: skipped` | D1 `não medido` (`NM-SPECIFY-PULADA`); relatório "não aplicável" |
| Tarefa sem código (sem `features/<slug>/`) | relatório "não aplicável", uma linha; nenhum erro |
| Feature com menos de 8 REQs | ressalva `amostra pequena`; os números continuam brutos |
| REQ removido depois da aprovação | conta como `descoberto` até o `intent.md` ser reaprovado; depois da reaprovação o REQ é `retirado` e sai do denominador |
| REQ editado (`rev` novo) | cenários do REQ ficam `stale` até nova aprovação (`NM-CENARIOS-STALE`) |
| Cenário com várias tags | conta uma vez em D2 e D3a; conta para cada REQ citado em D1 e em `cadeia_completa` |
| `skip`, `xfail` | `descoberto` em D2 (DRM-003) |
| Plano v1 ou sem `features/` | relatório "não aplicável"; v1 continua válido para sempre (CYC-018) |
| Código fora de `features/` | `legado: não medido` (CYC-011) |

- **Quem decide**: designer.
- **Critério de aceitação**: cada caso tem uma saída definida; nenhum caso termina em erro por falta de fonte.

### DRM-014 -- O que este arquivo não faz

Este arquivo **não**:

- calcula (o calculador é do plan-000014; as matrizes e saídas *golden* em `.claude/skills/scripts/tests/fixtures/drift/` são o contrato de teste dele);
- desenha o estudo de controle (é `drift-control-protocol.md`);
- muda o portão, os hooks, os denies, o contrato do ciclo ou `feature-layout.md`;
- usa LLM no cálculo de D1 a D3b;
- redefine o limiar do portão (CRAP, mutação).

- **Quem decide**: designer.
- **Critério de aceitação**: nenhum texto deste arquivo traz código de calculador nem altera um limiar do portão.

---

## Quem alimenta e quem consome

| Item | Plano | Alimenta | Consome |
|---|---|---|---|
| 3 | plan-000009 (grill) | `intent.md`, REQ IDs, índice de frases do brief (D0) | DRM-002 (unidade do D1); `NM-SEM-INDICE-BRIEF` |
| 4 | plan-000010 (formato Gherkin) | `.feature`, validador de tags `@REQ-`, relatório do runner | DRM-003 (tag e chave de cenário) |
| 5 | plan-000011 (specify) | aprovação do `intent.md` e dos `.feature`, `check_specify.py --status` | DRM-006 (`scenario_status`) |
| 6 | plan-000012 (plano a partir de cenários) | campo `Scenarios:` (informativo, fora do vetor) | -- |
| 7 | plan-000013 (teste-primeiro) | teste, relatório do runner, `gate.json`, registro "vermelho pelo motivo certo", cobertura por cenário, `baseline_moved` | DRM-004, DRM-005, DRM-011 |
| 8 | plan-000014 (relatório no REFLECT) | calcula o relatório, congela M1, calcula o delta | todo este arquivo; `casos.json` como contrato de teste |
| 9 | plan-000015 (integração) | quickguide pt-BR e ponteiros | nomes dos degraus (D1, D2, D3a, D3b) |
| 10 | plan-000016 (piloto) | registros de execução (`pilot-run-record.md`), oráculo | `drift-control-protocol.md` e este arquivo |

## Lacunas contra o plan-000007 e o item dono de cada uma

| # | Lacuna | Item dono |
|---|---|---|
| 1 | O esquema de rastreabilidade de `feature-layout.md` só tem REQ, cenário, teste, código e gate. D3a e D3b precisam também de `test_result`, `red_reason_ok`, `touched_uncovered` e `baseline_moved`. Tratadas como colunas **derivadas** (DRM-006). Se alguma não for derivável, é emenda aditiva a `feature-layout.md`. | plan-000014 |
| 2 | A condição de refutação do plan-000007 fala em "dois dos três degraus", mas o ciclo padrão não tem REQ nem cenário. A regra de comparação em `drift-control-protocol.md` (seção 7) opera isso. O texto de H-009 (prosa Human) pede a ressalva correspondente. | designer (via `/implement --manual`) |
| 3 | O `gate.json` não traz indicador de baseline aceito; o plan-000013 o deriva do diff de `quality-baseline.json`. Este arquivo cita a fonte (`baseline_moved`, DRM-006). | plan-000013 |
| 4 | O `/implement` por step só roda `--fast`; D3a exige `full` PASS. Sem a rodada `full` ao fim do plano, D3a fica `NM-SEM-GATE` mesmo com testes verdes. | plan-000013 |
| 5 | O contrato diz Cucumber JSON com chave de cenário (CYC-012); os planos 000010 e 000014 citam JUnit XML. Este arquivo só exige estados (`passed`, `failed`, `error`, `skipped`, `xfail`, `undefined`, `absent`) e chave de cenário. **Fechada pelo plan-000010:** formato Cucumber JSON, chave `<slug>/<arquivo>::<nome>` e mapeamento de estados em CYC-027 e `gherkin-spec-format.md` seção 8. | plan-000010 |
| 6 | Quem congela M1 (`--freeze`) não estava fixado entre os planos. | plan-000014 e plan-000015 |
| 7 | "Cadeia completa" e a população do D3a são definições deste arquivo, não do contrato; o plan-000014 as adota ou emenda. | plan-000014 |
| 8 | Registrar o oráculo independente como `D-NNN` é decisão do designer (prosa Human); não foi feito. | designer |
