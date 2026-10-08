---
designer_description: "After you approve the scenarios, I'm the protocol /plan follows to write the plan: every step says which approved scenarios it delivers, every approved scenario belongs to one step, and a tool, not a sentence, refuses the plan when a step has no scenario, a scenario has no step, or the scenarios changed after you approved them."
---

# GENERAL - PLAN FROM SCENARIOS

> Protocolo normativo da terceira fase do PLAN, a escrita do plano a partir dos cenários aprovados (plan-000012; item 6 do roadmap-000006). Detalha CYC-005, CYC-008 e CYC-018 de `.claude/references/general/extended-cycle-contract.md` e fixa o **formato final do plano v2**: o cabeçalho (`Feature:`, `Specify:`), o campo `Scenarios:` de cada step, a cobertura nos dois sentidos e o estado dos cenários.
>
> Depende de: `intent.md` e cenários aprovados (`specify-phase.md`, SPC-010, SPC-013; verificador `check_specify.py --status`); chave de cenário `<slug>/<arquivo>::<nome>` (`gherkin-spec-format.md`, GHK-010, seção 8; CYC-027); formato do step (`.claude/references/template/plan-step.md`). Verificador deste protocolo: `.claude/skills/scripts/check_plan_scenarios.py`.
>
> Idioma: pt-BR (protocolo), identificadores em en-US. Marcação: `[default; aceito 2026-10-06]` indica uma decisão pendente do plan-000012 que o designer aceitou no default. Cada regra tem identificador estável `PFS-NNN`, campo **Quem decide** e campo **Critério de aceitação**. Outros planos citam a regra em `Traces:`.

## Visão geral

```
cenários aprovados            plano v2                            /implement
(scenarios.lock.json)  ->  cada step cita os cenários   ->   teste vermelho por cenário (plan-000013)
                            que entrega (Scenarios:)
                                  |
                      check_plan_scenarios.py: exit 0 ou o plano não é salvo
```

O plano v2 liga dois pontos que a escada já tinha: o cenário aprovado (D1) e o step que o entrega. A ligação é conferida **nos dois sentidos** por uma ferramenta: step que muda comportamento sem cenário é recusado, e cenário aprovado que nenhum step entrega também. Um plano que sobrevive a essa conferência é o único que o `/plan` mostra ao designer.

## Formato final do plano v2

### Cabeçalho

Linhas do cabeçalho: as linhas do arquivo **antes da primeira seção `## `**, em qualquer ordem; um bloco `> **Origem**` ou `source:` do C3 pode estar entre elas. Quem lê só o cabeçalho (PFS-001) não lê o corpo.

Plano com cenários aprovados:

```
# Plan 000123 | FEATURE-O | 2026-11-01 10:00 UTC | login com bloqueio | Review: standard
plan_format_version: 2
Feature: login
Specify: approved (rev 2)
```

Tarefa sem código (sem `Feature:`):

```
plan_format_version: 2
Specify: skipped -- tarefa sem código: só documentação
```

Expressões regulares (linha inteira, depois de `strip`):

| Linha | Expressão |
|---|---|
| versão | `^plan_format_version:\s*(\S+)$` |
| feature | `^Feature:\s*([a-z0-9]+(?:-[a-z0-9]+)*)$` |
| specify aprovada | `^Specify:\s*approved \(rev (\d+)\)$` |
| specify pulada | `^Specify:\s*skipped -- (\S.*)$` |

#### Classe do pulo e braço do plano (emenda 000022)

Gramática das classes de CYC-035 e da linha de CYC-036 (D-011). Ela mora aqui, não no contrato (CYC-019). Exemplos de cabeçalho:

```
plan_format_version: 2
Specify default: off
Specify: skipped -- default off
```

```
plan_format_version: 2
Specify default: on
Specify: skipped -- opt-out: protótipo de tela que vai ser descartado
```

**Classe.** Lida no texto que a expressão "specify pulada" captura (o *valor*, depois de `skipped -- `), nesta ordem:

| Classe | Expressão sobre o valor | Motivo |
|---|---|---|
| `opt-out` | `^opt-out:\s*(\S.*)$` | obrigatório; precisa passar no PFS-007 (não vazio, sem enchimento, pelo menos 3 palavras) |
| `default off` | `^default off(?::\s*(\S.*))?$` | opcional |
| `tarefa sem código` | `^tarefa sem código(?::\s*(\S.*))?$` | opcional |
| `tarefa sem código` (legado) | qualquer outro valor (o `SKIPPED_RE` atual já casou) | o valor inteiro |

- Valor que começa com `opt-out` ou com `default off`, seguido de fim de linha, `:` ou espaço, e não casa com a expressão da sua classe (por exemplo `opt-out` sem motivo, ou `opt-out: x y`) é erro PFS-002, nunca legado.
- Grafia próxima de uma classe também é erro PFS-002, nunca legado: o valor que começa com `opt-out` ou `default off` em qualquer caixa e com `-`, `.`, espaço ou nada entre as palavras (por exemplo `Opt-out: ...`, `DEFAULT OFF`, `default-off`, `default off. motivo`). Só as formas exatas da tabela, em minúsculas, são válidas (revisão de código do plan-000022).
- O legado cobre todos os planos v2 escritos antes desta emenda (`tarefa sem código: ...`, `tarefa sem código (só documentação)`, `tarefa sem codigo: ...` sem acento, `só documentação`): a classe é `tarefa sem código` e o motivo é o valor inteiro. O resultado de hoje desses planos não muda.

**Braço do plano.** Linha opcional do cabeçalho, no máximo uma vez:

| Linha | Expressão |
|---|---|
| specify default | `^Specify default:\s*(on\|off)$` |

- Ausente vale `on` (antes desta emenda só existia o `on`). Duas linhas, ou um valor fora de `on` e `off`, é erro PFS-002.
- A expressão "specify" (`^Specify:`) não casa com `Specify default:`; as duas linhas não colidem.
- O verificador lê só esta linha, nunca o `conventions.md` do projeto: o braço é o do momento em que o plano foi escrito (CYC-036).

### Campo `Scenarios:` de cada step

Linha de metadados do step, depois de `Tests:`:

```
- **Scenarios**: `login/login.feature::Entrar com senha correta`, `login/login.feature::Bloquear depois de 3 tentativas`
```

ou `- **Scenarios**: N/A (<motivo>)`.

- **Chave** = `<slug>/<arquivo>.feature::<nome>`, entre crases, exatamente a do campo `index` de `features/<slug>/scenarios.lock.json` (CYC-027). Expressão: `^([a-z0-9]+(?:-[a-z0-9]+)*)/([^/:]+\.feature)::(\S.*)$`. Scenario Outline conta **um** cenário e tem **uma** chave. A tag `@REQ-...` **não** é aceita no lugar da chave `[default; aceito 2026-10-06]` (decisão pendente 3 = A): uma tag cobre vários cenários e esconderia um cenário sem step. Nome de cenário com crase não pode ser citado: a specify o renomeia (PFS-004).
- **Dono do teste.** `Scenarios:` lista os cenários cujo **teste nasce neste step**: é nele que o plan-000013 transforma o cenário em teste vermelho e o leva a verde. Cada cenário tem um dono só (PFS-010).
- **`N/A (<motivo>)`** diz que o step não entrega nenhum cenário e a que o step serve (texto livre, por exemplo "tabela usada pelo cenário de login"). O motivo tem pelo menos 3 palavras (PFS-007).

### Situações do step

| Situação do step | `Tests:` | `Scenarios:` | Resultado |
|---|---|---|---|
| Entrega comportamento observável | não-N/A | 1+ chaves | válido |
| Infraestrutura, migração, configuração, refactor com cobertura prévia | N/A | `N/A (motivo)` | válido `[default; aceito 2026-10-06]` (decisão pendente 6 = A) |
| Step sem comportamento observável, mas com teste | não-N/A | `N/A (motivo)` | válido, com achado `info` (a ferramenta não julga "comportamento observável"; o motivo é lido por quem aprova o plano; a fração é medida no piloto) |
| Comportamento sem cenário aprovado | não-N/A | ausente | **recusado** (PFS-006): entra um cenário (volta à specify) ou o `Tests:` vira N/A com justificativa |
| Chaves citadas, mas sem teste | N/A | 1+ chaves | **recusado** (PFS-008): o dono precisa de teste |
| Chave que não está no lock (renomeada, retirada, inventada) | qualquer | chave inexistente | **recusado** (PFS-005) |
| Cenário aprovado que nenhum step cita | -- | -- | **recusado** (PFS-009, cobertura inversa) |
| Cenário citado por dois steps | -- | -- | **recusado** (PFS-010) `[default; aceito 2026-10-06]` (decisão pendente 2 = A) |

### Seção opcional `## Cobertura de cenários`

Tabela cenário -> step, gerada por `check_plan_scenarios.py --table` e colada no fim do plano. O parser **não** a lê: ela é só leitura humana.

## Como o `/plan` escreve o plano

Depois da grill e da specify, quando existe `Feature: <slug>` com cenários aprovados:

1. Ler `index` de `features/<slug>/scenarios.lock.json` (a lista de cenários aprovados). Nenhum cenário fica de fora.
2. Montar os steps por camada (dados, regra, interface, ...) e dar a cada cenário um step dono. Um cenário que não cabe em nenhum step pede um step novo ou a volta à specify; nunca se inventa step só para acomodar.
3. Preencher `Scenarios:` em **todo** step: chaves no step que entrega o cenário, `N/A (motivo)` nos steps de infraestrutura.
4. Salvar o rascunho e **antes da revisão** rodar `python3 .claude/skills/scripts/check_plan_scenarios.py <plano.md>`. Com exit 1, corrigir o plano sozinho, no máximo 3 vezes. Persistindo, dizer o achado em voz controlada e perguntar ao designer (AskUserQuestion, C4): **voltar à specify** ou **ajustar o plano**.
5. Só então a revisão do plano (passo 5 do `/plan`). Plano v2 que não sai 0 não é mostrado como pronto.

Tarefa sem código: a grill escreve `Specify: skipped -- <motivo>` **uma vez** (passo 2b do `standard/SKILL.md`); o plano é v2 com todos os steps `Tests: N/A`.

Specify desligada numa tarefa com código (emenda 000022, D-011): a grill escreve `Specify: skipped -- default off` ou `Specify: skipped -- opt-out: <motivo>` **uma vez**; o plano é v2, sem `Feature:`, e os steps de código podem ter `Tests:` não-N/A com `Scenarios: N/A (motivo)`. Todo plano v2 novo, nas três classes e em `approved`, tem a linha `Specify default: on|off`.

## Regras

### PFS-001 -- Versão

v1 ou sem `plan_format_version`: o verificador sai 0 com "v1: não verificado" e **não lê mais nada** além do cabeçalho. v2: aplica as regras abaixo. Qualquer outro valor: sai 2 ("versão do plano desconhecida"). v1 é válido para sempre (CYC-018, D-008).

- **Quem decide**: designer (D-008); o verificador aplica.
- **Critério de aceitação**: um plano v1 com corpo ilegível ou inválido sai 0 sem achado; `plan_format_version: 3` sai 2; a saída do v1 diz "v1: não verificado".

### PFS-002 -- Cabeçalho v2

Em v2, `Specify:` aparece exatamente uma vez, no formato `approved (rev N)` ou `skipped -- <motivo>` (motivo não vazio). `approved` exige uma linha `Feature: <slug>` (kebab-case) e a pasta `features/<slug>/` existente. `skipped` proíbe `Feature:`. Uma feature por plano `[default; aceito 2026-10-06]` (decisão pendente 5 = A).

- **Quem decide**: designer (CYC-004, CYC-005).
- **Critério de aceitação**: sem `Specify:`, com duas, com formato fora das expressões, `approved` sem `Feature:` ou com pasta inexistente, `skipped` com `Feature:` ou sem motivo disparam PFS-002 (erro, na linha do problema ou na do título); cabeçalho correto não dispara.
- **Emenda 000022** (D-011; CYC-035, CYC-036): PFS-002 aceita as três classes e o valor sem classe (legado = `tarefa sem código`). Disparam também (erro): `opt-out` sem motivo ou com motivo que não passa no PFS-007; valor que começa com `opt-out` ou `default off` e não casa com a expressão da classe; `Specify default:` duas vezes ou com valor fora de `on` e `off`; `default off` com `Specify default: on` ou sem a linha (incoerência do cabeçalho: ausente vale `on`); `opt-out` com `Specify default: off` (com `off`, `--without-specify` não faz nada, então o plano não pode ter `opt-out`).

### PFS-003 -- Campo presente

Com `Specify: approved`, todo step tem `Scenarios:`. Step com `Tests:` não-N/A que não tem o campo recebe PFS-006 (mais específico) em vez de PFS-003.

- **Quem decide**: o verificador.
- **Critério de aceitação**: step com `Tests: N/A` e sem o campo dispara PFS-003; com o campo, não.

### PFS-004 -- Chave bem formada

Cada item da lista é uma chave entre crases, na expressão acima, com o slug do `Feature:`, sem duplicata no mesmo step. Item sem crases ou com texto solto dispara; `@REQ-...` gera a dica "use o nome do cenário, não a tag". Chave com crase no nome (do lock) não pode ser citada: dispara com a dica de renomear o cenário na specify.

- **Quem decide**: o verificador.
- **Critério de aceitação**: chave sem crases, tag `@REQ-`, slug diferente do `Feature:`, duplicata no step e nome com crase no lock disparam; chave correta não dispara.

### PFS-005 -- Chave existente

A chave está em `index` do lock. Chave ausente (renomeada, retirada, inventada) dispara com a dica "o cenário mudou de nome; veja Mudanças do intent.md" (SPC-012).

- **Quem decide**: o verificador, contra o lock.
- **Critério de aceitação**: chave fora de `index` dispara com o número do step e a chave; chave de `index` não dispara.

### PFS-006 -- Step sem cenário

`Tests:` não-N/A com `Scenarios:` **ausente**. O step muda comportamento e nenhum cenário aprovado o cobre: ou entra um cenário (volta à specify) ou o `Tests:` vira N/A com justificativa. Com `Scenarios: N/A (motivo)` o step passa (seção "Situações do step") e a ferramenta emite um achado `info` PFS-006, que não bloqueia.

- **Quem decide**: o verificador recusa; o designer decide entre specify e `Tests: N/A`.
- **Critério de aceitação**: step com `Tests:` não-N/A e sem o campo dispara PFS-006 (erro) com o número do step; com `N/A (motivo)`, só `info`.

### PFS-007 -- N/A justificado

`N/A (motivo)` com motivo vazio, de enchimento (`n/a`, `-`, `tbd`, `todo`, `...`) ou com menos de 3 palavras dispara. `N/A` sem parênteses também.

- **Quem decide**: o verificador.
- **Critério de aceitação**: `N/A (n/a)`, `N/A (x y)` e `N/A` dispara; `N/A (tabela usada pelo cenário de login)` não.

### PFS-008 -- O dono precisa de teste

Chaves citadas com `Tests: N/A` (ou sem `Tests:`) disparam: o step dono transforma o cenário em teste (CYC-021).

- **Quem decide**: o verificador.
- **Critério de aceitação**: step com chave e `Tests: N/A` dispara; com `Tests:` não-N/A, não.

### PFS-009 -- Cenário sem step

Cada chave de `index` que nenhum step cita dispara, uma linha por chave. Cobertura no sentido inverso: o plano não pode nascer sem entregar um cenário aprovado.

- **Quem decide**: o verificador.
- **Critério de aceitação**: lock com 4 chaves e plano que cita 3 dispara PFS-009 com a chave que falta; plano que cita as 4 não dispara.

### PFS-010 -- Dono único `[default; aceito 2026-10-06]` (decisão pendente 2 = A)

Cenário citado por mais de um step dispara (erro): o plan-000013 precisa de um único ponto onde o teste fica verde. Os demais steps usam `N/A (motivo)`. Cenário dividido em camadas é sinal de step grande demais.

- **Quem decide**: designer; o piloto (plan-000016) pode pedir a opção B (vários donos, com aviso).
- **Critério de aceitação**: a mesma chave em dois steps dispara PFS-010 e lista os dois números; em um step, não.

### PFS-011 -- Estado dos cenários

`check_specify.py --feature <slug> --status --json` deve devolver `approved`. `stale`, `draft` ou `missing` dispara com "os cenários estão desatualizados: refaça a specify" e as razões que o `--status` traz. A chamada é por **subprocesso** (acopla à CLI, não aos internos; `schema_version` desconhecido sai 2). Sem `check_specify.py`: sai 2 com "validador de cenários não encontrado" (não dá para provar o estado). Só vale em `Specify: approved`.

- **Quem decide**: o verificador (`check_specify.py`); o designer reaprova.
- **Critério de aceitação**: com `stale`, `draft` ou `missing` dispara PFS-011 (exit 1); com `approved`, não; sem o validador, exit 2.

### PFS-012 -- Revisão

`Specify: approved (rev N)` tem N igual ao `rev` do lock. Diferente: o plano é velho em relação à última aprovação (ou escrito antes dela). Não há migração automática de chaves; o plano é atualizado à mão ou refeito.

- **Quem decide**: o verificador.
- **Critério de aceitação**: cabeçalho `rev 1` com lock `rev 2` dispara PFS-012; iguais, não.

### PFS-013 -- Skip coerente

Com `Specify: skipped`, todo step tem `Tests: N/A` e `Scenarios:` ausente ou `N/A (...)`. Step com `Tests:` não-N/A e sem `Scenarios: N/A (motivo)` dispara: "a tarefa muda comportamento; rode a specify ou justifique o Tests: N/A". Step com chaves num plano pulado dispara também. Fecha o *proxy* do skip: a grill classifica "com código / sem código" **antes** (decide se a specify roda, CYC-004, SPC-002) e este PFS confere **depois** (decide se o plano é coerente com a classificação). Tarefa classificada "sem código" cujo plano acaba com `Tests:` não-N/A é recusada, não promovida automaticamente: o agente volta à grill ou à specify.

- **Quem decide**: o verificador recusa; o designer decide entre a specify e o `Tests: N/A`.
- **Critério de aceitação**: plano pulado com um step de `Tests:` não-N/A e sem `Scenarios: N/A (motivo)` dispara PFS-013 (erro); com todos `Tests: N/A`, não.
- **Emenda 000022** (D-011; CYC-029 emendado): o alcance do texto acima, inclusive o achado `info` de step com `Tests:` não-N/A e `Scenarios: N/A (motivo)`, passa a ser só a classe `tarefa sem código` (explícita ou legado). Com `default off` ou `opt-out`, step com `Tests:` não-N/A e `Scenarios: N/A (motivo)` (motivo que passa no PFS-007) é o caso esperado e não dispara nada, nem `info`; step de `Tests:` não-N/A sem `Scenarios: N/A (motivo)`, e step com chaves de cenário, continuam disparando PFS-013 (erro), com a dica "a specify está desligada neste plano: use `Scenarios: N/A (motivo)`".

### PFS-014 -- Nenhum step com cenário

`Specify: approved` e nenhum step cita chave: coberto por PFS-009 (uma linha por cenário); PFS-014 acrescenta um achado `info` com a dica "se `features/<slug>/` nunca teve cenário, o plano é `Specify: skipped`".

- **Quem decide**: o verificador.
- **Critério de aceitação**: plano aprovado sem nenhuma chave dispara PFS-009 e o `info` PFS-014; com ao menos uma chave, não dispara PFS-014.

### PFS-015 -- O que o verificador não faz

O verificador **não** altera o plano nem o lock; não mede divergência (D1, D2, D3: plan-000014); não roda teste nem runner (plan-000013); não julga se um step "muda comportamento observável" (só confere o campo e o `Tests:`); não resolve o plano velho (PFS-011, PFS-012 só o recusam).

- **Quem decide**: designer.
- **Critério de aceitação**: o diff de uma execução do verificador é vazio (nenhum arquivo muda); `--json` não traz número único de divergência.

### PFS-016 -- Desvio do default (emenda 000022)

Achado `info`, que não bloqueia, quando a classe do plano contraria a linha `Specify default:` do **próprio plano** (ausente = `on`), sem ler o `conventions.md`: `opt-out` com `on` (o projeto liga a specify e o plano a desligou) e `approved` com `off` (o projeto desliga a specify e o plano a ligou com `--with-specify`). Mensagem: "leitura por protocolo: este plano conta como desvio do default". `tarefa sem código` nunca dispara (não é elegível para a medida, D-011); `default off` com `off` e `approved` com `on` seguem o braço e não disparam. As combinações incoerentes (`default off` com `on`, `opt-out` com `off`) são erro PFS-002, não PFS-016.

- **Quem decide**: designer (D-011); o verificador só registra.
- **Critério de aceitação**: `Specify: skipped -- opt-out: <motivo>` com `Specify default: on` (ou sem a linha) dá um `info` PFS-016 e exit 0; `approved` com `Specify default: off` dá um `info` PFS-016; `default off` com `off`, `approved` com `on` e `tarefa sem código` em qualquer braço não dão PFS-016.

## Estado `stale`: o que o `/plan` e o `/implement` dizem

Reaprovar os cenários invalida o plano até ele ser atualizado, sem migração automática (a alternativa, reescrever planos, viola T3):

| Quem | Diz | Faz |
|---|---|---|
| `/plan` (plano novo, cenários `stale`) | "os cenários estão desatualizados: refaça a specify" | volta ao passo 2c da `standard/SKILL.md`; não escreve plano |
| `/plan` (plano já escrito, achado PFS-011 ou PFS-012) | o achado, em voz controlada | corrige o plano até 3 vezes ou pergunta (C4) |
| `/implement` (plano v2 com exit != 0) | o achado e o que fazer | **para** sem corrigir o plano e sem inventar cenário |

## Compatibilidade

| Situação | O que o verificador faz | Exit |
|---|---|---|
| Plano v1 ou sem `plan_format_version` | lê só o cabeçalho; "v1: não verificado" (PFS-001) | 0 |
| Plano v2 com `Specify: approved` | PFS-002 a PFS-014 | 0 ou 1 |
| Plano v2 com `Specify: skipped` | PFS-002, PFS-007, PFS-013 (sem lock, sem `check_specify.py`) | 0 ou 1 |
| Plano v2 com `Specify: skipped -- default off` ou `-- opt-out: <motivo>` (emenda 000022) | PFS-002, PFS-007, PFS-013 no alcance emendado, PFS-016 (`info`) | 0 ou 1 |
| Plano v2 sem a linha `Specify default:` (todos os de antes da emenda 000022) | lida como `on`; nenhum resultado muda | o de antes |
| `plan_format_version` desconhecido (ex.: 3) | PFS-001 fatal | 2 |
| Projeto sem `features/` e sem plano v2 | varredura sem argumentos: "nada a verificar" | 0 |
| Harness antigo, sem `check_specify.py` | só plano v2 `approved` recebe "validador de cenários não encontrado" (PFS-011) | 2 |

Uso sem argumentos (o `run_all_checks.py` roda assim, na raiz do projeto): varre `_output/plans/plan-*.md`, ignora `*-progress.md`, `*-qa-*.md` e plano cujo título começa com `# DONE |` (história imutável, T3), e reprova só plano v2. Plano v1 nunca entra. A varredura é **fail-closed**: um plano v2 ilegível, ou com lock inválido, aborta a varredura inteira com exit 2 (não é pulado).

## Esquema de `--json`

```json
{
  "schema_version": 1,
  "plan": "_output/plans/plan-000123-login.md",
  "version": 2,
  "feature": "login",
  "specify": "approved (rev 2)",
  "status": "approved",
  "findings": [{"rule": "PFS-006", "severity": "error", "file": "plano.md", "line": 57, "message": "...", "hint": "..."}],
  "steps": [{"n": 1, "title": "...", "line": 40, "tests": "when ...", "tests_na": false,
             "scenarios": ["login/login.feature::Entrar com senha correta"], "scenarios_na": false, "scenarios_reason": ""}],
  "matrix": [{"scenario": "login/login.feature::Entrar com senha correta", "steps": [1]}]
}
```

`matrix` traz, por chave de `index`, os números dos steps que a citam (vazio quando nenhum). Ordem estável: achados por linha e regra, matriz pela ordem do `index`, steps pelo número.

Chaves aditivas (emenda 000022, D-011; o `schema_version` continua `1`):

- `skip_class`: `"tarefa sem código"`, `"default off"` ou `"opt-out"` em plano v2 pulado (o legado sai `"tarefa sem código"`); `null` em `approved` e em v1.
- `skip_reason`: o motivo em plano v2 pulado (o valor inteiro no legado; `""` quando a classe aceita motivo opcional e ele falta); `null` em `approved` e em v1.
- `specify_default`: `"on"` ou `"off"` em plano v2 (sem a linha = `"on"`); `null` em v1, que o verificador não lê além da versão.

Consumidores que não conhecem as chaves as ignoram; nenhuma chave existente muda de sentido.

## Emenda ao texto do plan-000007 (para o designer)

O contrato (`extended-cycle-contract.md`, seção "Compatibilidade", e `plan-step.md`) dizia "lista de tags `@REQ-<slug>-NNN` ou nomes de cenário". A forma final é só a **chave de cenário** (decisão pendente 3 = A). O texto sugerido: "`Scenarios:` -- lista de chaves `<slug>/<arquivo>.feature::<nome>` entre crases, tiradas de `index` do `scenarios.lock.json` da `Feature: <slug>`, ou `N/A (<motivo>)`". A emenda em `plan-step.md` entra no plan-000012 (Step 6); a do contrato entra como CYC-028 e CYC-029 (emenda 000012).

## Decisões pendentes do plan-000012 e o default adotado

| # | Decisão | Default adotado | Regra |
|---|---|---|---|
| 1 | Onde mora a recusa executável | A: script novo `check_plan_scenarios.py` `[default; aceito 2026-10-06]` | PFS-001 a PFS-014 |
| 2 | Um cenário, mais de um step dono | A: dono único `[default; aceito 2026-10-06]` | PFS-010 |
| 3 | Aceitar a tag `@REQ-...` na lista | A: só a chave `[default; aceito 2026-10-06]` | PFS-004 |
| 4 | O `/implement` repete a parada | A: uma linha, plano v2 com exit != 0 não começa `[default; aceito 2026-10-06]` | PFS-011, PFS-012 |
| 5 | Mais de uma feature por plano | A: uma feature por plano `[default; aceito 2026-10-06]` | PFS-002 |
| 6 | Step de infraestrutura sem cenário | A: `Scenarios: N/A (motivo)` com `Tests:` também N/A `[default; aceito 2026-10-06]` | PFS-007, PFS-008 |

## O que este protocolo não faz

Não define a fase grill nem a specify (`grill-phase.md`, `specify-phase.md`), o runner nem o teste-primeiro por cenário (plan-000013), a fórmula de divergência (plan-000008, plan-000014), nem a documentação ao usuário (plan-000015). Não muda o portão, os hooks, os denies nem `settings` (S2). Não migra plano velho. Não substitui `critique_plan_coverage.py` do upstream (rastreabilidade de design, `REQ-TYPE-NNN` contra `Traces:`), que trata de outro conceito: aqui a cobertura é de **cenário** contra step.
