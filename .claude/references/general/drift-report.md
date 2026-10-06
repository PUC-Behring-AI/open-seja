---
designer_description: "When /reflect or /explain drift needs to say where a feature's intent got lost, I'm the normative reading of the matrix into a per-step report (D1, D2, D3a, D3b, M1 against M2): which files are read, what a stale approval does, how each not-measured reason is worded, how the audit stays apart from D, and what the citizen is shown -- so the report counts what drift-metric.md defines and nothing more."
---

# GENERAL - DRIFT REPORT

> Referência normativa do relatório de divergência por degrau (roadmap-000006, plan-000014; H-009 no §3 subseção 2.9, D-004 e D-007 em `product-design/product-design-as-intended.md`). Este arquivo diz **de onde o calculador lê, em que ordem, o que escreve e com que palavras**. O que se mede e a fórmula são do `drift-metric.md` (DRM-001..014); este arquivo os cita e não os redefine. O calculador é `.claude/skills/scripts/drift_report.py`.
>
> Idioma: pt-BR (prosa), identificadores em en-US. Marcação: `[default; aceito 2026-10-06]` indica uma decisão pendente do plan-000014 que o designer aceitou no default.
>
> Cada regra tem identificador estável `DRP-NNN`, campo **Quem decide** e campo **Critério de aceitação**.

## Visão geral

```
features/<slug>/  ->  load_matrix  ->  compute_report  ->  render (power | citizen | html)
 (arquivos)           (junta e lê)     (função pura,        (frases fixas, sem LLM)
                                        sem I/O, sem LLM)
```

O relatório **mede e não bloqueia**: sai 0 quando foi produzido, mesmo com divergência alta. O portão é o gate (T1). O texto é gerado por modelo de frase fixa, nunca por LLM.

---

## Regras

### DRP-001 -- Entradas, caminhos e o que faltar

Todo caminho é relativo à raiz do projeto. Fonte **ausente** nunca é erro: é `não medido` com a razão (DRP-004). Fonte **ilegível ou inválida** (JSON ou XML mal formado, UTF-8 inválido) é erro de leitura: exit 2 com o arquivo citado, sem traceback.

| Coluna | Fonte | Quem a lê | Se faltar |
|---|---|---|---|
| REQ, estado (`ativo`, `retirado`), cenário, chave, `disabled`, `nao_faz` | `features/<slug>/intent.md` e `*.feature` | `check_features.py <raiz> --feature <slug> --matrix --json` (GHK, plan-000010) | sem `features/`: "não aplicável" (DRP-017) |
| `scenario_status` | `check_specify.py <raiz> --feature <slug> --status --json` (SPC-013, plan-000011) | `drift_report.py` | `check_specify.py` ausente: DRP-003 |
| cenário -> step dono (informativo) | `Scenarios:` do plano v2 | `check_plan_scenarios.py <plano> --json` (PFS, plan-000012) | sem plano: a coluna some; nada muda no vetor |
| `test_result` | `features/<slug>/runner/cucumber.json` (Cucumber JSON, CYC-027) | `drift_report.py` (mapeamento do `gherkin-spec-format.md` seção 8) | `NM-SEM-RUNNER` |
| adaptadores | `features/<slug>/runner/adapter.json` e `features/<slug>/gate.json` (campo `adapter`) | `drift_report.py` | tratados como existentes |
| gate `full`, `baseline_moved` | `features/<slug>/gate.json` | `drift_report.py` | `NM-SEM-GATE` |
| `red_reason_ok` | `features/<slug>/drift/red-reason.json` | `drift_report.py` | `NM-SEM-REGISTRO-VERMELHO` |
| `touched_total`, `touched_uncovered`, base do diff | `features/<slug>/drift/coverage.json` | `drift_report.py` | `NM-SEM-COBERTURA` ou `NM-SEM-BASE-DIFF` |
| D0 (resíduo do brief) | `check_intent.py features/<slug>/intent.md --d0` (GRL-011) | `drift_report.py` | `NM-SEM-INDICE-BRIEF` |
| auditoria semântica | `features/<slug>/drift/audit.json` | `drift_report.py` | coluna "não auditado" |
| oráculo (controle) | `features/<slug>/drift/oracle-result.json` | `drift_report.py` | `o1: null` |
| retradução depois do código | `features/<slug>/drift/retraducao-pos-codigo.md` | `drift_report.py` | `NM-SEM-RETRADUCAO-POS-CODIGO` |
| instantâneos | `features/<slug>/drift/M1.json` e `M2-<AAAA-MM-DD>.json` | `drift_report.py` | `NM-SEM-M1` |

Formatos aditivos (nenhum esquema de `feature-layout.md` muda; a emenda ao layout é do designer):

```json
// runner/adapter.json (opcional): {"schema_version": 1, "adapter": false}
// gate.json, campos opcionais acrescentados: {"adapter": false, "baseline_moved": false}
// drift/red-reason.json: {"schema_version": 1, "scenarios": {"<chave de cenario>": true}}
// drift/coverage.json:   {"schema_version": 1, "base": "<ref git>", "touched_total": 50, "touched_uncovered": 7}
// drift/oracle-result.json: {"schema_version": 1, "n": 5, "falham": 2}
```

`gate.json` `full` vale como PASS quando `full.category` é `"PASS"` ou `full.exit_code` é `0`; `"PASS_WITH_BASELINE"` e `baseline_moved: true` valem como baseline aceito. Os arquivos que ainda ninguém produz (`red-reason.json`, `coverage.json`, `baseline_moved`, `adapter`) são entrega do plan-000013 (`/implement`); até lá o D3b sai `não medido` e o D3a traz a ressalva do DRP-018.

- **Quem decide**: designer.
- **Critério de aceitação**: cada coluna tem fonte, comando e efeito da ausência; nenhuma fonte ausente produz erro; nenhuma entrada ilegível produz traceback; o calculador nunca escreve fora de `features/<slug>/drift/`.

### DRP-002 -- Colunas derivadas

`scenario_status`, `test_result`, `red_reason_ok`, `touched_uncovered` e `baseline_moved` são **derivadas** como o DRM-006 as define. Este arquivo as cita e não as redefine. Duas precisões de junção:

- **Chave de cenário.** `<slug>/<arquivo>::<nome>` (CYC-027). Um cenário com várias tags aparece sob vários REQs da matriz com a **mesma chave**; o calculador junta por chave e conta o cenário **uma vez** em D2 e D3a e uma vez por REQ em D1 e na cadeia (DRM-013).
- **`Scenario Outline`.** É um cenário só; vale o **pior** estado das suas linhas (`error`, `failed`, `undefined`, `skipped`, `passed`, nesta ordem). `xfail` pela tag vale para a unidade inteira.

Um teste coletado cuja chave não existe mais no `.feature` é **teste órfão**: aparece nas leituras (DRP-011) e em nenhum `D`.

- **Quem decide**: designer.
- **Critério de aceitação**: duas linhas de `Outline` com estados diferentes dão o pior estado; um cenário com duas tags conta uma vez em D2.

### DRP-003 -- Consulta obrigatória a `check_specify.py --status` `[default; aceito 2026-10-06]` (decisão pendente 5 = A)

Antes de usar a aprovação dos cenários, o calculador **sempre** roda `check_specify.py <raiz> --feature <slug> --status --json`. O campo `scenarios: approved` do `intent.md`, e o campo `scenarios_approved` de `check_features.py --matrix`, **não valem**: eles não veem `.feature` editado nem REQ com `rev` novo e continuam dizendo `approved` quando a grill reabre (plan-000011, lacunas 1 e 3).

| Estado do `--status` | D1 | D2, D3a, D3b |
|---|---|---|
| `approved` | medido | medidos |
| `stale` | `não medido`, `NM-CENARIOS-STALE` | medidos, com a ressalva `cenários desatualizados` |
| `draft` | `não medido`, `NM-CENARIOS-STALE` | medidos, com a ressalva `cenários não aprovados` |
| `missing` | `não medido`, `NM-CENARIOS-STALE` | medidos sobre o que existir, com a ressalva `sem cenários aprovados` |
| `check_specify.py` ausente | medido, com a ressalva `aprovação não verificada` | medidos |

Se o `.feature` foi editado de modo que a chave do cenário mudou, o calculador não acha o teste e o D2 já sai `descoberto`: isso é o dado, não um defeito.

Intenção ainda em `grilling` dá D1 `NM-INTENCAO-NAO-APROVADA`. O `rev` > 1 de um REQ depois da aprovação aparece como `stale` no `--status`; o calculador não reimplementa essa regra.

- **Quem decide**: designer.
- **Critério de aceitação**: com `status.txt` = `stale` e `scenarios: approved` no frontmatter, D1 sai `NM-CENARIOS-STALE` com `cobertos = descobertos = 0`; o teste prova que o status foi consultado.

### DRP-004 -- Razões de `não medido`

Os códigos do DRM-009 valem com o mesmo nome. Este arquivo fixa a **frase de relatório** de cada um (voz controlada, primeira pessoa do designer) e acrescenta dois códigos de leitura.

| Código | Onde | Frase |
|---|---|---|
| `NM-INTENCAO-NAO-APROVADA` | D1 | "Eu não medi: você ainda não aprovou os requisitos." |
| `NM-SPECIFY-PULADA` | D1 | "Eu não medi: esta tarefa não teve cenários." |
| `NM-CENARIOS-STALE` | D1 | "Eu não medi: os cenários mudaram depois da aprovação." |
| `NM-SEM-ADAPTADOR-RUNNER` | D2, D3a | "Eu não medi: esta stack ainda não tem executor de cenários." |
| `NM-SEM-RUNNER` | D2, D3a | "Eu não medi: não achei o relatório dos testes." |
| `NM-SEM-ADAPTADOR-GATE` | D3a, D3b | "Eu não medi: esta stack ainda não tem portão." |
| `NM-SEM-GATE` | D3a, D3b | "Eu não medi: o portão não rodou por inteiro." |
| `NM-SEM-REGISTRO-VERMELHO` | D3a | "Eu não medi: não há registro de que o teste falhou pelo motivo certo." |
| `NM-SEM-COBERTURA` | D3b | "Eu não medi: não há cobertura só dos testes de cenário." |
| `NM-SEM-BASE-DIFF` | D3b | "Eu não medi: não sei onde a feature começou." |
| `NM-SEM-M1` | delta | "Eu não medi a mudança: o estado da entrega não foi congelado." |
| `NM-SEM-INDICE-BRIEF` | D0 | "Eu não medi o que sobrou do pedido: as frases do pedido não foram indexadas." |
| `NM-SEM-RETRADUCAO-POS-CODIGO` | leitura | "Eu não medi: ainda não escrevi o que entendi depois do código." |
| `NM-SEM-MARCA-ADOCAO` | leitura | "Eu não medi o que ficou sem feature: não sei desde quando o projeto usa features." |

Os dois últimos são códigos de **leitura** (fora de qualquer `D`). O catálogo dos dez primeiros é do DRM-009; os dois acrescentados aqui são proposta de emenda a ele (o arquivo é do plan-000008).

A razão aparece **escrita na mesma linha** do degrau. `razao_nm` lista todas as razões aplicáveis, na ordem desta tabela. A razão do D2 vale também para o D3a (DRM-004).

- **Quem decide**: designer.
- **Critério de aceitação**: todo `não medido` do relatório traz código e frase; nenhum código fora desta tabela; a frase de cada código tem até 25 palavras.

### DRP-005 -- Fórmula e denominador zero

`D = descobertos / (cobertos + descobertos)` (DRM-001). O calculador guarda numerador e denominador **inteiros** e só formata `D` na saída (4 casas no JSON, 2 no texto do power dev). `não medido` fica fora do denominador. Denominador zero escreve `"n/a"`, nunca `0`. Nenhum campo de tempo entra dentro do vetor; o carimbo de hora vem de `--at`.

- **Quem decide**: designer.
- **Critério de aceitação**: os seis casos de `.claude/skills/scripts/tests/fixtures/drift/casos.json` saem iguais a `esperado`; duas execuções sobre os mesmos arquivos dão JSON idêntico byte a byte.

### DRP-006 -- Populações e estados por degrau

O calculador aplica o DRM-002 a DRM-005 com estas escolhas de junção, todas adotadas aqui e propostas ao `drift-metric.md`:

1. **D1** conta os REQs `ativo`. REQ `retirado` sai do denominador (DRM-013; antes da reaprovação o D1 já é `não medido` pelo DRP-003).
2. **D2** tem por população os cenários com pelo menos uma tag que aponta para um REQ `ativo`. Cenário `disabled` (tag `skip`, `wip` ou `ignore`) é `descoberto`, qualquer que seja o resultado do teste. `skipped`, `xfail` e `absent` são `descobertos`; `passed`, `failed`, `error` e `undefined` são `cobertos`.
3. **D3a** tem por população os cenários com D2 `coberto` **e** os com D2 `não medido`. Cenário com D2 `descoberto` fica fora (já foi contado). Um cenário com D2 `não medido` é `não medido` em D3a com a razão do D2.
4. Em D3a, para um cenário com D2 `coberto`, vale esta ordem: (a) teste vermelho (`failed`, `error`, `undefined`), `full` FAIL, baseline aceito ou `red_reason_ok` falso: `descoberto`; (b) gate indisponível (`NM-SEM-GATE`, `NM-SEM-ADAPTADOR-GATE`) ou registro de vermelho ausente (`NM-SEM-REGISTRO-VERMELHO`): `não medido`, com **todas** as razões que se aplicam; (c) caso contrário `coberto`.
5. **D3b** tem por população as linhas e ramos tocados pela feature (`touched_total`). Gate ausente dá `NM-SEM-GATE` (ou `NM-SEM-ADAPTADOR-GATE`) para todos; `touched_uncovered` ausente dá `NM-SEM-COBERTURA`; base do diff ausente dá `NM-SEM-BASE-DIFF` com `n = 0`. Código fora do perímetro da feature é `legado: não medido` e não entra (CYC-011).
6. **Cadeia completa** (DRM-008): REQ com cenário cujos cenários estão **todos** `cobertos` em D2 e D3a. O calculador devolve este número como o `casos.json` o define. Quando algum cenário do REQ ficou `não medido` em D3a, o REQ é **indeterminado**: o relatório traz `cadeia_indeterminada` ao lado e o texto diz "não medida"; o `0` do golden nunca é lido como "nenhum REQ tem cadeia".

- **Quem decide**: designer.
- **Critério de aceitação**: cenário `disabled` com teste verde é `descoberto` em D2; cenário com D2 `descoberto` não aparece em D3a; `nada-medido` tem `cadeia_completa: 0` e `cadeia_indeterminada` igual ao número de REQs.

### DRP-007 -- Momentos M1 e M2 e o delta `[default; aceito 2026-10-06]` (decisão pendente 2 = A)

O M1 é a matriz do fim do IMPLEMENT, congelada. O M2 é a matriz regenerada no REFLECT. A diferença `M2 - M1` é a deriva depois da entrega (DRM-012). Não há M0.

Quem congela o M1: o `/implement` é o dono do momento (o gate acabou de rodar), por `drift_report.py --feature <slug> --freeze --moment M1 --at <UTC>`. **A chamada no `/implement` é do plan-000013 e do plan-000015**; este plano entrega o comando e a degradação: sem instantâneo, o relatório diz `NM-SEM-M1` e não traz delta.

O delta traz, por degrau, numerador e denominador **dos dois lados** (o denominador pode mudar: REQ novo, REQ retirado). A diferença de `D` só existe quando os dois são números. Quando o denominador mudou, o texto diz "o denominador mudou de X para Y". Os arquivos de entrada cujo hash mudou depois do M1 são listados.

- **Quem decide**: designer.
- **Critério de aceitação**: M2 com 12 REQs e M1 com 10 dá o delta com "o denominador mudou de 10 para 12"; sem M1, só `NM-SEM-M1`.

### DRP-008 -- Instantâneos `[default; aceito 2026-10-06]` (decisão pendente 1 = A)

`features/<slug>/drift/M1.json` e `features/<slug>/drift/M2-<AAAA-MM-DD>.json`, versionados com a feature. Aditivo ao layout do plan-000007; a emenda ao `feature-layout.md` é do designer. Esquema:

```json
{"schema_version": 1, "feature": "<slug>", "momento": "M1", "at": "<UTC ISO>",
 "report": {"...relatório completo do DRP-015..."},
 "entradas": {"features/<slug>/gate.json": "<sha256>"}}
```

Regras: escrita atômica (arquivo temporário e `os.replace`); `--freeze` **recusa** sobrescrever um M1 existente (exit 2, mensagem curta, arquivo intacto); `at` vem de `--at`, nunca do relógio; o instantâneo grava o SHA-256 de cada entrada lida.

- **Quem decide**: designer.
- **Critério de aceitação**: `--freeze` duas vezes na mesma feature recusa na segunda e deixa o arquivo com o mesmo hash.

### DRP-009 -- Auditoria semântica, à parte do D `[default; aceito 2026-10-06]` (decisão pendente 6 = A)

A pergunta "o cenário captura o requisito?" é humana e cega, por amostra (DRM-010). O calculador **lista a amostra** e **lê** `audit.json`; ele nunca decide `adequado` e a coluna nunca altera um `D`.

```json
{"schema_version": 1,
 "itens": [{"req": "REQ-<slug>-NNN", "adequado": "sim", "por": "humano",
            "objeto": "cenario", "nota": "<palavras literais de quem julgou>"}]}
```

- `adequado`: `sim`, `parcial` ou `nao`; qualquer outro valor é erro de leitura (exit 2, REQ citado).
- `por`: `humano` ou `juiz` (acima de ~40 REQs por braço o juiz LLM em contexto limpo pode escrever; a leitura é a mesma).
- `objeto`: `cenario` (a amostra cega do DRM-010; padrão) ou `retraducao` (o julgamento do citizen do DRP-010).
- `nota`: palavras literais de quem julgou; ninguém as reescreve (regra do verbatim).
- **Amostra determinística**: ordenar os REQs por `sha1(slug + ":" + req)` e tomar `ceil(30%)`; todos os REQs no retrofit do braço A.
- A coluna do relatório traz contagens `sim`, `parcial`, `nao` e a lista dos REQs ainda não auditados. Frase fixa: "A auditoria não entra no D."
- Um `nao` entra no alerta "escada fechou sem capturar a intenção" (DRP-011); nada mais muda.

- **Quem decide**: designer; quem preenche `audit.json` é o humano (ou o juiz, registrado em `por`).
- **Critério de aceitação**: 10 REQs dão 3 na amostra, sempre os mesmos para o mesmo slug; um `nao` não altera nenhum `D`.

### DRP-010 -- Retradução depois do código, lado a lado

A retradução em primeira pessoa é o objeto de aprovação do citizen (D-004, CYC-013). Depois do código o relatório mostra, **por REQ**, três textos lado a lado:

| Coluna | Fonte |
|---|---|
| O que você pediu | frases do pedido citadas pelo REQ em `intent.md` ("Nas suas palavras", índices `F<n>` e `A<n>`) |
| O que eu entendi antes do código | a linha do REQ na seção `## Retradução` do `intent.md` (aprovada no specify) |
| O que eu entendi depois do código | a linha do REQ em `features/<slug>/drift/retraducao-pos-codigo.md`, escrita pelo agente do `/reflect` em primeira pessoa **a partir da matriz** (cenários demonstrados, não demonstrados, não medidos), sem inventar comportamento |

O calculador só **lê** e alinha os três textos pela marca `(REQ-<slug>-NNN)` no fim da linha; ele não gera a retradução. Se o arquivo falta: `NM-SEM-RETRADUCAO-POS-CODIGO`, e as outras duas colunas aparecem. Quem decide se a mensagem confere é o citizen: "é isso / não é isso" por REQ, gravado em `audit.json` com `objeto: "retraducao"` e as palavras dele em `nota`. Nenhuma contagem mecânica "confere" a equivalência entre a mensagem e o contrato (plan-000011, lacuna 6): o relatório diz que não mediu.

- **Quem decide**: o citizen julga; o designer fixa o formato.
- **Critério de aceitação**: três colunas por REQ quando as três fontes existem; sem `retraducao-pos-codigo.md`, a razão dita e nenhuma coluna inventada; nenhum julgamento sem palavra literal de quem julgou.

### DRP-011 -- Leituras fora do D

Acompanham o vetor; não entram em nenhum `D`.

| Leitura | O que é |
|---|---|
| `cadeia_completa`, `cadeia_indeterminada` | DRP-006 item 6 |
| `cenarios_orfaos`, `cenarios_sem_tag`, `testes_orfaos` | cenário com tag de REQ que não existe; cenário sem tag; teste sem cenário |
| `escada_fechou_sem_capturar` | D1 = D2 = D3a = 0 (todos numéricos) e (O1 > 0 ou algum `adequado: nao`) |
| `d0` | resíduo do brief (DRM-010): frases do pedido sem requisito e sem fora-do-escopo; `NM-SEM-INDICE-BRIEF` sem índice |
| `intencao_sem_feature` | DRP-014 |
| `nao_faz` | itens de "Fora do escopo" e cenários `@nao-faz`: `{itens, cenarios, sem_evidencia}`; `sem_evidencia = max(0, itens - cenarios)`. A contagem é por total; o vínculo item a cenário não é mecânico e o relatório diz isso |
| código sem cenário | é o D3b `descoberto`; o texto o chama de "código sem cenário (excesso)" |

- **Quem decide**: designer.
- **Critério de aceitação**: cenário sem tag não altera nenhum `D` e aparece em `cenarios_sem_tag`; "Fora do escopo" com 2 itens e nenhum `@nao-faz` dá `sem_evidencia: 2`.

### DRP-012 -- Rótulo de prova

Cada item do relatório diz **de que tipo é a prova** que o sustenta. Rótulos fixos:

| Rótulo | Quando |
|---|---|
| `prova: arquivo` | a existência de um requisito, de uma tag ou de uma frase (D1, D0, `nao_faz`) |
| `prova: ferramenta` | resultado de runner, de portão ou de cobertura (D2, D3a, D3b) |
| `prova: humano` | julgamento de uma pessoa (auditoria, retradução) |
| `prova: nenhuma` | nada sustenta o item; a razão `não medido` está ao lado |

O rótulo é escrito na tabela e no JSON (`prova` por degrau). Ele existe para que ninguém leia "arquivo" como "ferramenta": ter tag não prova que o cenário diz o que o requisito diz.

- **Quem decide**: designer.
- **Critério de aceitação**: nenhuma linha de degrau sem rótulo; D1 sempre `arquivo`; D3a sempre `ferramenta`.

### DRP-013 -- Dois registros: power dev e citizen

O relatório tem dois registros (CYC-013, CYC-014, D-004).

- **Registro do power dev** (padrão): o vetor completo com `n`, cobertos, descobertos, não medido com razão, `D`, M1, M2, mudança, rótulo de prova, ressalvas, leituras e a frase "O que o D não vê".
- **Registro do citizen** (`--citizen`): sem número técnico. Contagens de requisito, cenário e teste **em palavras** ("oito de dez requisitos"); as ausências **enumeradas** pelo nome do requisito, não por percentual; nenhum `D`, nenhum "PASS", nenhum "gate", nenhum percentual, nenhum nome de ferramenta. O teste da surpresa vale: item que só confirma não entra; entram o que falta, o que mudou depois da entrega e o que não foi medido.

Voz controlada nos dois: até 25 palavras por frase, até 6 frases por parágrafo, termos fixos (requisito, cenário, teste, entrega), primeira pessoa do designer ("eu").

- **Quem decide**: designer.
- **Critério de aceitação**: o texto do citizen de qualquer fixture não contém dígito, `%`, `PASS`, `gate` nem a sigla `D1`..`D3b`; toda frase tem até 25 palavras.

### DRP-014 -- Leitura reversa: intenção sem feature, só depois da adoção

Para cada intenção do as-intended nascida **depois da marca de adoção**, o relatório diz se alguma feature aprovada a serve. A marca é a data `adopted_at` de `features/adoption.json` (`{"schema_version": 1, "adopted_at": "AAAA-MM-DD"}`; arquivo aditivo, proposta de emenda ao layout).

- **Intenções consideradas**: IDs `REQ-<TIPO>-NNN` (TIPO em maiúsculas) e `JM-TB-NNN` de `product-design/product-design-as-intended.md`. Decisões `D-NNN` não entram (nem toda decisão pede feature).
- **Nascida**: a primeira linha do `## CHANGELOG` que cita o ID com `added`; a data da linha vale. Intenção nascida antes de `adopted_at` é legado e **não** entra (CYC-011).
- **Servida**: o ID consta em `serve:` do frontmatter de um `intent.md` aprovado.
- Sem `adoption.json` ou sem as-intended: `NM-SEM-MARCA-ADOCAO`; nada é contado.

- **Quem decide**: designer.
- **Critério de aceitação**: intenção anterior à adoção nunca aparece; intenção posterior e não servida aparece com o ID; sem a marca, a razão dita.

### DRP-015 -- Formato do relatório, destaque e as-coded regenerado

JSON com `schema_version: 1`. Os campos do DRM-007 são a base; o relatório acrescenta, **ao lado e nunca dentro do vetor**:

```json
{"schema_version": 1, "feature": "<slug>", "momento": "M2",
 "degraus": {"D1": {"n": 0, "cobertos": 0, "descobertos": 0, "nao_medidos": 0, "D": "n/a", "razao_nm": [], "prova": "arquivo"}},
 "leituras": {"...DRP-011..."}, "ressalvas": [],
 "itens": {"reqs_descobertos": [], "cenarios_descobertos": {"D2": [], "D3a": []}},
 "auditoria": {"sim": 0, "parcial": 0, "nao": 0, "nao_auditados": []},
 "retraducao": {"estado": "nao_medido", "razao_nm": ["NM-SEM-RETRADUCAO-POS-CODIGO"]},
 "delta": null, "entradas": {"<arquivo>": "<sha256>"}}
```

`compute_report` (função pura) devolve só os campos do DRM-007; o carregador e o renderizador acrescentam o resto. Tarefa sem medida possível devolve `{"schema_version": 1, "feature", "momento", "nao_aplicavel": true, "razao_nm": [...], "motivo": "..."}`.

**Destaque.** O texto pode dizer "O maior D está em D2: ...". Só entra degrau com `D` numérico. Empate é dito ("Empate entre D2 e D3a"). `n/a` e `não medido` nunca ganham. Nunca se soma.

**As-coded regenerado.** Com `--as-coded` o relatório traz a tabela "Como ficou", regenerada **da matriz** (REQ, cenários, resultado do teste, estado em D3a). É voz do agente, regenerável, nunca editada à mão; não substitui `product-design-as-coded.md`.

- **Quem decide**: designer.
- **Critério de aceitação**: o relatório tem as quatro linhas de degrau; nenhum campo traz número único; todo texto de destaque traz o degrau e a razão do que ficou de fora.

### DRP-016 -- Regra não prescritiva

O relatório está em tempo presente descritivo ou passado. Não escreve "deveria", "considere", "recomendamos", "você deve", "you should", "consider", "we recommend". `/reflect` registra as palavras de quem reflete e nunca prescreve (regra do `reflect/SKILL.md`). A frase "o que o D não vê" é descrição, não conselho.

- **Quem decide**: designer.
- **Critério de aceitação**: nenhum item de `FORBIDDEN_PHRASES` aparece em nenhuma saída de nenhuma fixture.

### DRP-017 -- Degradação e compatibilidade

| Caso | Saída |
|---|---|
| projeto sem `features/` (e sem `--feature`) | uma linha "Não aplicável: este projeto não tem features.", exit 0 |
| plano v1 ou sem `plan_format_version` | uma linha "Não aplicável: este plano é do formato antigo.", exit 0 |
| plano `Specify: skipped` | uma linha, `NM-SPECIFY-PULADA`, exit 0 |
| `--feature` sem pasta | uma linha "Não aplicável", exit 0 |
| feature sem M1 | relatório normal, `NM-SEM-M1`, sem delta |
| fonte ausente | `não medido` com a razão |
| fonte ilegível | exit 2 com o arquivo |

As skills `/reflect` e `/explain drift` **não acrescentam nada** quando o resultado é "não aplicável".

- **Quem decide**: designer.
- **Critério de aceitação**: nenhum dos casos acima produz erro ou seção vazia; `/reflect` e `/explain drift` sem `features/` produzem exatamente o que produziam antes.

### DRP-018 -- Anti-gaming

D3a só vale com as três condições do DRM-011. Sem `red-reason.json`, o cenário é `não medido` (`NM-SEM-REGISTRO-VERMELHO`) e o relatório traz a ressalva "D3a sem prova de vermelho". PASS com baseline aceito é `descoberto`, com a ressalva "baseline aceito". `baseline_moved` ausente em `gate.json` não desclassifica, mas traz a ressalva "baseline não verificado". Teste que `skip` ou `xfail` não é verde.

- **Quem decide**: designer; o ratchet é só dele (H-008).
- **Critério de aceitação**: nenhum cenário `coberto` em D3a sem as três condições; toda ausência de prova vira ressalva visível.

### DRP-019 -- O que o relatório não faz

Não bloqueia (exit 0 quando produzido). Não calcula com LLM. Não grava `scenarios:` nem edita `intent.md`, `.feature`, plano, `gate.json`, hook ou baseline. Não decide `adequado`. Não escreve fora de `features/<slug>/drift/`. Não soma degraus. Não mede nada fora do perímetro da feature.

- **Quem decide**: designer.
- **Critério de aceitação**: o diff da execução de qualquer fixture toca só `features/<slug>/drift/`.

---

## Quem alimenta e quem consome

| Item | Plano | Alimenta | Consome |
|---|---|---|---|
| 7 | plan-000013 (teste-primeiro) | `runner/cucumber.json`, `runner/adapter.json`, `gate.json` (+ `adapter`, `baseline_moved`), `drift/red-reason.json`, `drift/coverage.json`; chama `drift_report.py --freeze --moment M1 --at <UTC>` no fim do IMPLEMENT | DRP-001, DRP-007 |
| 8 | plan-000014 (este) | relatório, instantâneos, delta, amostra de auditoria | todo o `drift-metric.md` |
| 9 | plan-000015 (integração) | quickguide pt-BR; emenda de layout (`drift/`, `adoption.json`) | nomes dos degraus e DRP-012, DRP-013 |
| 10 | plan-000016 (piloto) | `audit.json`, `oracle-result.json`, `retraducao-pos-codigo.md` reais | DRP-009, DRP-010 |

## Propostas ao designer (nada aplicado em arquivo de outro plano)

1. `drift-metric.md` DRM-009: acrescentar `NM-SEM-RETRADUCAO-POS-CODIGO` e `NM-SEM-MARCA-ADOCAO` (leitura, fora do D) e a frase de cada um.
2. `drift-metric.md` DRM-008: dizer que, com D3a `não medido` para algum cenário do REQ, a cadeia do REQ é indeterminada (o golden `nada-medido` continua com `cadeia_completa: 0`).
3. `drift-metric.md` DRM-004: a população do D3a inclui os cenários com D2 `não medido` (com a razão do D2).
4. `feature-layout.md`: `features/<slug>/drift/` (instantâneos, `audit.json`, `red-reason.json`, `coverage.json`, `oracle-result.json`, `retraducao-pos-codigo.md`), `features/<slug>/runner/` (`cucumber.json`, `adapter.json`), `features/adoption.json`, e os campos opcionais `adapter` e `baseline_moved` de `gate.json`.
