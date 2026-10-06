---
designer_description: "When /plan writes the scenarios you approve, or a later plan needs to read, write or check a .feature file, I'm the normative convention with stable GHK-NNN rules -- language, the @REQ tag, one behavior per scenario, step style, the reserved tags, the runner report and the validator output -- so every scenario can be traced to a requirement and checked by a tool before anyone reads it."
---

# GENERAL - GHERKIN SPEC FORMAT

> Convenção normativa dos `.feature` do ciclo estendido (roadmap-000006, plan-000010; H-009 e D-004 em `product-design/product-design-as-intended.md`). Diz **como** se escreve um `.feature` que sirva de critério de aceitação e **o que** o validador `.claude/skills/scripts/check_features.py` confere. Ele não calcula divergência (DRM-001, plan-000008), não decide aprovação (CYC-003, CYC-013) e não executa cenários (CYC-012, CYC-026).
>
> Idioma: pt-BR (convenção), identificadores em en-US. `[default; aceito 2026-10-06]` marca uma decisão pendente do plan-000010 que o designer aceitou no default. Cada regra tem identificador estável `GHK-NNN`, severidade e **Critério de aceitação**. Outros planos citam a regra em `Traces:`.
>
> Contratos de que depende: layout e esquema em `.claude/references/template/feature-layout.md` (CYC-015); `intent.md` em `.claude/references/template/intent.md` e `grill-phase.md` (GRL-005); medida em `drift-metric.md` (D1 = DRM-002, D2 = DRM-003).

## 1. Objetivo e leitor

O `.feature` é um **contrato endereçável** (D-004, CYC-013): quem lê código o aprova; o citizen aprova a retradução, não este texto. Por isso o texto precisa ser legível em quase linguagem natural **e** verificável por máquina. A convenção existe para que os defeitos mecânicos que fazem o Gherkin virar ruído (cenário sem requisito, requisito sem cenário, tag que não aponta para nada, step repetido ou ambíguo, cenário com dois comportamentos) sejam achados por uma ferramenta antes do ponto de aprovação, e não por uma pessoa depois.

Quem escreve: o `/plan` (fase specify). Quem confere: `check_features.py`, sem LLM e sem rede. Quem aprova: o power dev (o contrato) e o designer (a mensagem).

## 2. Idioma das palavras-chave `[default; aceito 2026-10-06]` (decisão pendente 1 = C)

O arquivo declara o idioma na primeira linha. O validador aceita `en` (padrão, sem declaração) e `pt` (`# language: pt`). Texto dos steps em pt-BR; código, nomes de arquivo e step definitions em en-US (`standards.md` § i18n). Palavra-chave em português **sem** `# language: pt` é erro (GHK-001).

| en | pt |
|---|---|
| `Feature`, `Rule`, `Background` | `Funcionalidade`, `Regra`, `Contexto` |
| `Scenario`, `Scenario Outline`, `Examples` | `Cenário`, `Esquema do Cenário`, `Exemplos` |
| `Given`, `When`, `Then`, `And`, `But`, `*` | `Dado`, `Quando`, `Então`, `E`, `Mas`, `*` |

Exemplo mínimo em português:

```gherkin
# language: pt
Funcionalidade: Gerenciar tarefas

  @REQ-task-list-001
  Cenário: Acrescentar uma tarefa
    Dado que a lista de tarefas está vazia
    Quando eu acrescento a tarefa "Comprar pão"
    Então a lista mostra "Comprar pão" como pendente
```

Exemplo mínimo em inglês:

```gherkin
Feature: Manage tasks

  @REQ-task-list-001
  Scenario: Add a task
    Given the task list is empty
    When I add the task "Buy bread"
    Then the list shows "Buy bread" as pending
```

Alternativas rejeitadas: só inglês (o citizen lê e aprova em pt-BR) e só português (o ecossistema de ferramentas está em inglês).

## 3. A tag `@REQ-`

Todo `Scenario` e todo `Scenario Outline` carrega **ao menos uma** tag `@REQ-<slug>-NNN`, em linha acima dele. Vários REQs no mesmo cenário são permitidos (várias tags). A tag **não** é herdada: é proibida em `Feature`, `Rule` e `Examples` `[default; aceito 2026-10-06]` (decisão pendente 2 = A), para que `grep '@REQ-'` ao lado de cada cenário seja a prova de rastreabilidade e a unidade do D1 e do D2 seja o cenário.

Expressão oficial: `^@REQ-[a-z][a-z0-9]*(-[a-z0-9]+)*-[0-9]{3,}$`. O `<slug>` da tag é o nome da pasta `features/<slug>/`. Slugs reservados (colidem com os `REQ-TYPE-NNN` do design): `ent`, `perm`, `ux`, `mc`, `jm`, `i18n`, `val`, `delta`. Slug em kebab-case.

A frase `@REQ-NNN` da tabela do roadmap-000006 é abreviação desta tag.

## 4. Como o validador lê o `intent.md`

O validador **reutiliza** `parse` e `table` de `check_intent.py` (um parser só para `intent.md`).

- Os REQs são as linhas da tabela da seção "Requisitos" cuja primeira célula casa `REQ-<slug>-NNN`. Linha com `Estado: retirado` existe (a tag que a cita não é órfã), mas não exige cenário.
- `status` do frontmatter: `grilling` ou `approved` (feature-layout.md). Só `approved` torna REQ sem cenário um **erro** (GHK-005); em `grilling` é informação (`não medido`).
- Campo opcional `scenarios: approved` no frontmatter `[default; aceito 2026-10-06]` (decisão pendente 5 = A): o validador só o **lê** e expõe `scenarios_approved: true | false | null` na matriz (`null` = campo ausente). Quem o escreve é o ponto de aprovação do plan-000011. Sem o campo, o D1 não separa cenário rascunho de aprovado (`NM-CENARIOS-STALE`, DRM-002).
- A seção "Modelo e termos" (coluna `Termo`) alimenta GHK-017; "Fora do escopo" alimenta o aviso de GHK-019; `serve:` alimenta GHK-018.

## 5. Um cenário por comportamento

- Uma ação `When` por cenário; 3 a 7 steps típicos; no máximo 10 (GHK-012).
- Não encadear `When`, `Then`, `When` (dois comportamentos: dois cenários).
- `Background` com no máximo 3 steps, sem ação (`When`).
- `Scenario Outline` só para variar **dados** do mesmo comportamento. A unidade do D2 é o `Outline` inteiro `[default; aceito 2026-10-06]` (decisão pendente 6 = A): coberto só se **todas** as linhas de `Examples` foram executadas e nenhuma foi `skip` ou `xfail`. A matriz traz `rows` por `Outline` para o relatório detalhar. Linhas de `Examples` que expressam comportamentos distintos pedem cenários separados.
- Nome de cenário único dentro do arquivo (GHK-010): a chave do relatório é `<slug>/<arquivo>::<nome>` (seção 8).

## 6. Estilo dos steps

- **Declarativo**, na voz do domínio, no presente: o que o usuário faz e vê, não como a tela ou o código faz.
- **Sem detalhe de implementação** (GHK-013): nada de URL, caminho de arquivo, SQL, seletor CSS, nome de função ou de classe.
- Valores variáveis entre aspas ou em `<coluna>` (no `Outline`); um conceito por step.
- Substantivos do domínio vêm do "Modelo e termos" do `intent.md` (GHK-017): o texto do step usa as palavras que o citizen usou.
- `And` e `But` herdam o tipo do step anterior; o primeiro step não pode ser `And` nem `But`.

## 7. Jornada, "não faz" e tags reservadas

**`Rule:` como jornada ordenada** (GHK-018, emenda do adendo do roadmap-000006). Um `Rule:` agrupa os cenários de **uma jornada** e **cita `JM-TB-NNN`** no nome ou na descrição. A ordem dos cenários dentro do `Rule` é a ordem da jornada; a matriz registra `journey: {rule, jm, order}`. A tag `@REQ-` continua no cenário, nunca no `Rule`. Se o `intent.md` tem `serve:`, o `JM-TB-NNN` citado deve constar nele (aviso).

**`@nao-faz`** (GHK-019, opt-in). Tag de **cenário** que marca um comportamento que o sistema **não** pode ter (item de "Fora do escopo", ou restrição em negativo). O cenário continua exigindo a tag `@REQ-`. A tag é proibida em `Feature`, `Rule` e `Examples`. A matriz marca `nao_faz: true`. O validador só informa quando "Fora do escopo" tem itens e nenhum cenário `@nao-faz` existe: é leitura de cobertura, não obrigação.

**Tags de desativação** (GHK-014): `@skip`, `@wip`, `@xfail`, `@ignore`, em qualquer nível. Cenário desativado conta como **descoberto** no D2 (DRM-003); o aviso aparece antes do runner. A matriz marca `disabled: true`.

## 8. Contrato do relatório do runner (Cucumber JSON)

O runner contract do ciclo é o **Cucumber JSON** (CYC-012, CYC-027). Este arquivo não nomeia ferramenta como requisito; a recomendação de primeiro adaptador para Python é pytest-bdd (`--cucumberjson`), marcada como recomendação (CYC-026). Os planos 000010 e 000014 falavam em JUnit XML: o desvio está registrado no progress do plan-000010.

**Chave de cenário.** `<slug>/<arquivo>::<nome>`, onde `<slug>` e `<arquivo>` saem do `uri` do `.feature` (`features/<slug>/<arquivo>.feature`) e `<nome>` é o `name` do elemento. É única porque GHK-010 exige nome único por arquivo. Para `Scenario Outline` a chave é a mesma para todas as linhas; o D2 agrega as linhas (decisão pendente 6 = A).

**Tag no relatório.** Cada cenário do Cucumber JSON traz a lista `tags`; a ligação cenário -> REQ é essa lista (a convenção do runner pode gravá-la com ou sem `@`; o consumidor normaliza). Não há propriedade extra.

**Estado do cenário.** Os estados do DRM-003 (`passed`, `failed`, `error`, `skipped`, `xfail`, `undefined`, `absent`) não são todos nativos do Cucumber. Mapeamento:

| No relatório (status dos steps e tags) | Estado do DRM-003 | Observação |
|---|---|---|
| todos os steps `passed` | `passed` | |
| algum step `failed` e a mensagem de erro é de **asserção** | `failed` | é o único "vermelho pelo motivo certo" (CYC-022) |
| algum step `failed` e a mensagem **não** é de asserção (importação, sintaxe, fixture, configuração) | `error` | |
| algum step `ambiguous` | `error` | duas definições casam o mesmo step |
| algum step `undefined` | `undefined` | passo sem definição; normal no teste-primeiro, nunca vermelho |
| algum step `pending` | `undefined` | passo declarado e não implementado |
| todos os steps `skipped` e o cenário não tem tag `xfail` | `skipped` | `@skip` e afins |
| cenário com tag `xfail` e status `failed` ou `skipped` | `xfail` | `xfail` não é nativo: sai da tag |
| cenário do `.feature` sem elemento no relatório | `absent` | o relatório ausente inteiro é `NM-SEM-RUNNER` (DRM-003) |

O Step 8 do plan-000010 verifica este mapeamento contra pytest-bdd e registra o que o runner de fato emite (seção 10).

## 9. Regras `GHK-NNN`

Severidades: `erro` falha o validador (exit 1); `aviso` só falha sob `--strict`; `info` nunca falha e diz o que **não** foi medido.

| Regra | O que detecta | Severidade | Alimenta |
|---|---|---|---|
| GHK-001 | Arquivo não parseia; sem `Feature:`; idioma não suportado; palavra-chave `pt` sem `# language: pt` | erro | todos |
| GHK-002 | `Scenario` ou `Scenario Outline` sem tag `@REQ-` | erro | 000008: "cenário sem tag" |
| GHK-003 | Tag `@REQ-` malformada; slug diferente da pasta; `@REQ-` no nível `Feature`, `Rule` ou `Examples` | erro | D1 |
| GHK-004 | Tag órfã: `@REQ-<slug>-NNN` que não existe na tabela de `intent.md` | erro | 000008: "tag sem REQ" |
| GHK-005 | REQ ativo sem cenário: `approved` = erro; `grilling` = info | erro / info | D1 |
| GHK-006 | Step duplicado no mesmo cenário (mesmo tipo efetivo e mesmo texto) | erro | ruído |
| GHK-007 | Mesmo texto de step com tipos efetivos diferentes (Given e Then) na mesma feature | erro | ambiguidade |
| GHK-008 | Steps iguais após normalização (caixa, pontuação, aspas) mas escritos diferentes | aviso | quase-duplicata |
| GHK-009 | Primeiro step `And` ou `But`; `<x>` sem coluna em `Examples`; coluna de `Examples` não usada | erro | estrutura |
| GHK-010 | Nome de cenário repetido no mesmo arquivo | erro | D2 (chave) |
| GHK-011 | `Scenario Outline` sem `Examples`, ou `Examples` sem linhas | erro | estrutura |
| GHK-012 | Novo `When` depois de `Then`; mais de 10 steps; `Background` com mais de 3 steps ou com `When` | aviso | um cenário por comportamento |
| GHK-013 | Detalhe de implementação no step (URL, caminho, SQL, seletor CSS, nome de função ou classe) | aviso | critério de aceitação |
| GHK-014 | Tag de desativação (`@skip`, `@wip`, `@xfail`, `@ignore`) | aviso | D2: descoberto |
| GHK-015 | Só com `--steps`: definição duplicada (erro); definição que casa 0 steps (aviso); step sem definição ou padrão não verificável (info) | erro / aviso / info | duplicata |
| GHK-016 | Pasta com `intent.md` sem REQ válido na tabela; slug inválido ou reservado; slug do frontmatter diferente da pasta; pasta com `.feature` e sem `intent.md` (info, não validada) | erro / info | rastreabilidade |
| GHK-017 | Substantivo entre aspas ou com inicial maiúscula no meio do step que não consta em "Modelo e termos" (info se a seção falta) | aviso / info | vocabulário do citizen |
| GHK-018 | `Rule:` sem `JM-TB-NNN` no nome ou na descrição; `JM-TB-NNN` fora de `serve:` | erro / aviso | jornada |
| GHK-019 | `@nao-faz` em `Feature`, `Rule` ou `Examples`; "Fora do escopo" com itens e nenhum cenário `@nao-faz` | erro / info | "não faz" |

Cada regra a seguir tem mensagem-modelo (frases curtas, voz controlada) e **Critério de aceitação**: um caso que a dispara e um que não (fixtures em `.claude/skills/scripts/tests/fixtures/features/`).

- **GHK-001.** Modelo: "Não consegui ler este arquivo: <motivo>." Critério: arquivo sem `Feature:` dispara; arquivo com `# language: pt` e palavras `pt` não dispara.
- **GHK-002.** Modelo: "O cenário <nome> não tem tag @REQ-." Critério: cenário sem tag dispara com a linha do `Scenario`; cenário com tag não dispara.
- **GHK-003.** Modelo: "A tag <tag> não tem a forma @REQ-<slug>-NNN com o slug <slug>." Critério: `@REQ-login-1`, slug alheio e tag em `Feature` disparam; tag correta não dispara.
- **GHK-004.** Modelo: "A tag <tag> cita um requisito que não existe em intent.md." Critério: `@REQ-login-009` com tabela até 003 dispara; REQ existente (inclusive retirado) não dispara.
- **GHK-005.** Modelo: "O requisito <REQ> não tem cenário." Critério: `approved` sem cenário dispara erro; `grilling` dispara info; REQ coberto não dispara.
- **GHK-006.** Modelo: "Este step repete o da linha <n> no mesmo cenário." Critério: dois steps iguais no cenário disparam; o mesmo texto em dois cenários não dispara.
- **GHK-007.** Modelo: "Este texto aparece como <tipo> e como <tipo> nesta feature." Critério: "o saldo é 10" como Given e como Then dispara; `And` herdando o tipo não dispara.
- **GHK-008.** Modelo: "Este step só difere do da linha <n> por caixa ou pontuação." Critério: dois steps que diferem só por caixa disparam; mesmos steps com valores diferentes não disparam.
- **GHK-009.** Modelo: "O primeiro step não pode começar com E, Mas, And ou But" ou "A coluna <x> não existe em Exemplos" ou "A coluna <x> de Exemplos não é usada." Critério: cada caso dispara; Outline com colunas e placeholders coerentes não dispara.
- **GHK-010.** Modelo: "O nome <nome> já foi usado na linha <n>." Critério: dois cenários com o mesmo nome no arquivo disparam; o mesmo nome em arquivos diferentes não dispara.
- **GHK-011.** Modelo: "O esquema de cenário <nome> não tem exemplos" ou "Os exemplos de <nome> não têm linhas." Critério: Outline sem `Examples` e `Examples` só com cabeçalho disparam.
- **GHK-012.** Modelo: "Este cenário parece ter mais de um comportamento." Critério: `When`, `Then`, `When` dispara; 3 a 7 steps com um `When` não dispara.
- **GHK-013.** Modelo: "O step fala de <o quê>. Diga o que o usuário vê, não como o sistema faz." Critério: `https://`, `SELECT ... FROM`, caminho com extensão, `#id` e `funcao()` disparam; texto no domínio não dispara. Lista fixa de padrões no validador; **nunca** é erro.
- **GHK-014.** Modelo: "Este cenário está desligado (<tag>) e conta como não coberto." Critério: `@skip` dispara; arquivo sem tag de desativação não dispara.
- **GHK-015.** Modelo: "A definição de step <padrão> existe duas vezes (<arquivo>, <arquivo>)." Critério: duas definições iguais disparam erro; diretório sem definições dá só info por step; `re.compile` dá info "não verificado".
- **GHK-016.** Modelo: "intent.md não tem nenhum requisito REQ-<slug>-NNN" ou "O nome <slug> não pode ser usado." Critério: pasta com `intent.md` sem tabela de REQ dispara; slug `ux` dispara; pasta só com `.feature` dá info.
- **GHK-017.** Modelo: "A palavra <termo> não está em Modelo e termos." Critério: termo ausente da tabela dispara aviso; termo presente não dispara; sem a seção, uma info por feature.
- **GHK-018.** Modelo: "O grupo <nome> não diz de qual jornada JM-TB-NNN ele é." Critério: `Rule` sem `JM-TB-NNN` dispara erro; `Rule` com a jornada e na lista `serve:` não dispara.
- **GHK-019.** Modelo: "A tag @nao-faz vale só em cenário." Critério: `@nao-faz` em `Feature` dispara; em `Scenario` não dispara.

### Heurística de GHK-013 (lista fixa)

URL (`http://`, `https://`, `www.`); caminho com barra e extensão (`dir/arquivo.ext`) ou letra de unidade (`C:\`); SQL (`SELECT ... FROM`, `INSERT INTO`, `UPDATE ... SET`, `DELETE FROM`); seletor (`#id`, `.classe` precedido de espaço); chamada (`nome_funcao()`); `CamelCase` de duas ou mais partes. Pode errar para os dois lados: por isso é aviso.

### Heurística de GHK-017

Candidatos: texto entre aspas retas (exceto o que tem dígito: valor) e palavra com inicial maiúscula que **não** abre o step. Um candidato está coberto se algum termo de "Modelo e termos" está contido nele ou o contém (sem acento, sem caixa, sem `s` final). Substantivo comum sem aspas e sem maiúscula não é medido: a heurística não vê o que não marca.

## 10. Rodando no pytest-bdd

Seção preenchida no Step 8 do plan-000010 (exemplo executável em `.claude/references/template/feature-example/`).

## 11. Saída do validador

`python .claude/skills/scripts/check_features.py [raiz] [--feature <slug>] [--steps <dir>] [--json] [--matrix] [--strict] [--quiet]`

Sem argumentos, a raiz é a pasta atual (é assim que o `run_all_checks.py` o chama). O validador olha só as pastas `features/<slug>/` que têm `intent.md` ou `.feature`; sem nenhum `features/<slug>/intent.md` ele imprime `check_features: nenhum features/<slug>/intent.md; nada a verificar.` e sai 0. Isto é a retrocompatibilidade: projeto sem `features/`, ou com `features/` de outro estilo (por exemplo behave), não é afetado.

### Saída legível

Relatório em stdout, uma linha por achado, agrupada por feature (`[<slug>]`), em frases curtas:

```
[login]
features/login/login.feature:9: GHK-002 erro: O cenário Sair da conta não tem tag @REQ-. Dica: Ponha a tag @REQ-<slug>-NNN do requisito na linha acima.
1 erro, 0 avisos, 0 informações; 1 REQ, 2 cenários, 0 REQ sem cenário
```

`--quiet` esconde as informações (o resumo continua). `--matrix` acrescenta, por feature, cada REQ com seus cenários e a chave `<slug>/<arquivo>::<nome>`. Diagnóstico de uso vai para stderr. O validador nunca imprime o conteúdo de um arquivo além da linha do achado.

### Saída `--json`

Um único objeto em stdout, com `schema_version: 1`:

```json
{
  "schema_version": 1,
  "root": ".",
  "summary": {"errors": 0, "warnings": 0, "infos": 0, "reqs": 3, "scenarios": 5, "uncovered_reqs": 0},
  "findings": [{"rule": "GHK-002", "severity": "error", "file": "features/login/a.feature", "line": 9,
                "scenario": "Sair da conta", "message": "...", "hint": "..."}],
  "features": [{"slug": "login", "status": "approved", "scenarios_approved": true}],
  "matrix": {}
}
```

`findings` segue a mesma ordem da saída legível (arquivo, linha, regra). `matrix` só existe com `--matrix`:

```json
{"login": {"status": "approved", "scenarios_approved": true,
           "reqs": {"REQ-login-001": {"state": "ativo",
                                      "scenarios": [{"key": "login/a.feature::Entrar", "file": "...", "name": "Entrar",
                                                     "line": 4, "rows": null, "disabled": false, "nao_faz": false,
                                                     "journey": null}]}}}}
```

Todo REQ de `intent.md` aparece, inclusive o sem cenário (lista vazia) e o retirado (`state: retirado`). `rows` é o número de linhas de `Examples` do `Scenario Outline` (`null` em cenário comum). `journey` é `{rule, jm, order}` dentro de um `Rule`. `scenarios_approved` é `true`, `false` ou `null` (campo ausente). O D1 do plan-000008 lê esta matriz; ela não calcula D.

### Códigos de saída

| Código | Quando |
|---|---|
| 0 | sem erros (avisos e informações não falham) |
| 1 | com erros, ou com avisos sob `--strict` |
| 2 | uso incorreto, raiz ou pasta de definições ilegível, `--feature` sem pasta, ou falha interna (mensagem curta em stderr, nunca um traceback) |

A convenção 0/1/2 é a dos outros `check_*.py` do harness (`check_intent.py`: 0, e 1 só sob `--strict`; aqui o erro falha por padrão porque o check roda no `run_all_checks.py`).

## 12. O que a convenção não faz

- Não julga se o cenário **captura** o requisito: é a auditoria humana por amostra do plan-000008 e o ponto de aprovação da specify.
- Não calcula D, nem decide cobertura do D2 ou do D3: entrega a matriz REQ -> cenários e os achados.
- Não faz mutação de `.feature`.
- Não resolve ambiguidade por casamento entre definições de step (padrões `parse`, `re`): é do plan-000013, com definições reais.
- Não altera o portão, os hooks, os denies, `settings` nem o esquema de `feature-layout.md` (CYC-024).
