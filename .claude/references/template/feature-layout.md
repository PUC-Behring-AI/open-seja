---
designer_description: "When /plan runs the grill or specify phase, or a later plan needs to read or write a feature folder, I'm the normative layout of features/<slug>/ -- intent.md, the .feature files, gate.json, the REQ and scenario tag convention, and the traceability table schema -- so every item addresses the same files in the same shape."
---

# Template: Feature Layout

Esquema normativo do CYC-015 (`.claude/references/general/extended-cycle-contract.md`). Este arquivo diz **onde** cada artefato da feature vive e **qual forma** ele tem. Ele não valida nada: o validador é do plan-000010; a leitura por `/critique` e `/explain drift` é dos planos 000014 e 000015 (aqui só se declara que `features/` entra na lista de diretórios que eles leem).

Idioma: pt-BR (prosa), identificadores em en-US.

## Estrutura de pastas

```
features/
└── <slug>/
    ├── intent.md        (grill; requisitos REQ-<slug>-NNN)
    ├── <nome>.feature   (specify; um ou mais; tag @REQ-<slug>-NNN em cada Scenario)
    └── gate.json        (IMPLEMENT; resultado do portão por feature)
```

## Regras de pasta

- `<slug>` em kebab-case (`[a-z0-9]+(-[a-z0-9]+)*`); uma pasta por feature.
- A pasta nunca é apagada; o git é a recuperação (CYC-011).
- Tarefa sem código (documentação, pesquisa, configuração, harness) não cria pasta (CYC-004, CYC-005).
- O plano referencia a feature no cabeçalho com `Feature: <slug>` (CYC-005).
- `features/` entra na lista de diretórios que `/critique` e `/explain drift` leem. Declaração apenas; a leitura é implementada nos planos 000014 e 000015.
- Código, testes e requisitos fora de `features/` são `legado: não medido` (CYC-011).

## `intent.md`

Frontmatter obrigatório:

```yaml
---
slug: <slug>
status: grilling | approved
---
```

- `grilling`: a entrevista está em curso; a specify não pode começar (CYC-008, regra 1).
- `approved`: o designer aprovou a lista de requisitos e o "não faz" (CYC-002).

Seções, nesta ordem (o conteúdo detalhado de cada uma é do plan-000009; aqui só o esquema):

| Seção | Papel |
|---|---|
| Nas suas palavras | o pedido do citizen, registrado literalmente |
| Requisitos | tabela de `REQ-<slug>-NNN` (abaixo) |
| Fora do escopo | o que não será feito (o "não faz" aprovado no CYC-002) |
| Premissas | o que se assume sem ter sido dito |

Tabela de requisitos:

| REQ | Texto (linguagem natural, voz controlada) | Critério |
|---|---|---|
| `REQ-<slug>-NNN` | uma frase que o citizen valida | uma frase que diz como se reconhece o requisito atendido |

`NNN` tem três dígitos, sequencial dentro da feature, nunca reutilizado. Todo REQ tem texto e critério (CYC-002).

> **Emenda 000009 (aditiva).** A fase grill escreve um superconjunto deste esquema: índice das frases do pedido (`F<n>`) e das respostas (`A<n>`) em "Nas suas palavras"; colunas `Tipo`, `Nas suas palavras`, `Para que`, `rev` e `Estado` (a coluna `Texto` também pode se chamar `Requisito`); seções "Dimensões", "Modelo e termos", "Perguntas abertas" e "Mudanças"; frontmatter `approved_at`, `approved_by` e `serve:`. Nada deste esquema mínimo muda ou é removido. Regras: `.claude/references/general/grill-phase.md` (GRL-005); modelo completo: `.claude/references/template/intent.md`; verificador: `.claude/skills/scripts/check_intent.py`.

## `*.feature`

- Um ou mais arquivos por pasta; o nome descreve o comportamento (`<nome>.feature`, kebab-case).
- Todo `Scenario` carrega a tag `@REQ-<slug>-NNN` do requisito que cobre, na linha imediatamente acima do `Scenario`. Um cenário pode carregar mais de uma tag; um REQ pode ter vários cenários (CYC-003).
- Estilo critério de aceitação: `Given` (contexto), `When` (ação do usuário), `Then` (resultado observável). Sem detalhe de implementação: nada de nome de função, tabela, rota, seletor ou tecnologia.
- O `.feature` é um contrato endereçável, aprovado pelo power dev; o citizen aprova a retradução, não este texto (CYC-013, D-004).

## `gate.json`

Resultado do portão por feature. Escrito pelo IMPLEMENT (CYC-007); nunca editado à mão (S2).

```json
{
  "schema_version": 1,
  "fast": { "exit_code": 0, "category": "PASS", "ref": "<QUALITY_DIR>/<arquivo>.json" },
  "full": null,
  "ts": "YYYY-MM-DDTHH:MM:SSZ"
}
```

- `schema_version`: inteiro; sobe quando o esquema muda.
- `fast`, `full`: resultado da última rodada `--fast` e `--full`, ou `null` se nunca rodou (isso é `não medido`, não falha, CYC-012). `exit_code` segue as categorias de CYC-012 (0 PASS; 1 a 7 por categoria); `ref` aponta para o JSON do portão no diretório `QUALITY_DIR` do projeto (variável do portão; o valor vem de `product-design/conventions.md` via `project_config.py`).
- `ts`: data e hora UTC da última escrita.
- Projeto sem portão (`GATE_FAST_CMD` ausente): o arquivo pode faltar ou ter `fast: null`; D3 fica `não medido` com a razão dita (CYC-012).

## Tabela de rastreabilidade (esquema)

Esquema da tabela que os planos 000008 e 000015 preenchem ao medir. Este arquivo só fixa as colunas e os estados; a fórmula é do plan-000008 (CYC-016).

| Coluna | Conteúdo | Degrau |
|---|---|---|
| REQ | `REQ-<slug>-NNN` do `intent.md` | origem |
| cenário | `Scenario` do `.feature` com a tag do REQ | D1 |
| teste | teste executável ligado ao cenário pela chave de cenário do runner (CYC-012) | D2 |
| código | código que o teste verde exercita | D3 |
| gate | resultado do portão em `gate.json` | D3 |

Cada célula está em um estado de CYC-010: **coberto**, **descoberto** ou **não medido**. Elemento fora do perímetro da feature (CYC-011) é `legado: não medido`, não descoberto. `não medido` aparece sempre ao lado dos outros dois estados, nunca fundido em número único (Q4).

## Exemplo completo (feature fictícia: lista de tarefas)

`features/task-list/intent.md`:

```markdown
---
slug: task-list
status: approved
---

# Lista de tarefas

## Nas suas palavras

"Quero anotar o que preciso fazer e riscar o que já fiz. Não quero que
nada suma sem eu pedir."

## Requisitos

| REQ | Texto | Critério |
|---|---|---|
| REQ-task-list-001 | Eu posso acrescentar uma tarefa à lista. | Depois de acrescentar, a tarefa aparece na lista. |
| REQ-task-list-002 | Eu posso marcar uma tarefa como feita. | Uma tarefa marcada continua na lista e aparece como feita. |

## Fora do escopo

- Prazos e lembretes.
- Compartilhar a lista com outras pessoas.

## Premissas

- Há uma única lista por usuário.
- Tarefa marcada como feita não some até o usuário a remover.
```

`features/task-list/manage-tasks.feature`:

```gherkin
Feature: Gerenciar tarefas

  @REQ-task-list-001
  Scenario: Acrescentar uma tarefa
    Given a lista de tarefas está vazia
    When eu acrescento a tarefa "Comprar pão"
    Then a lista mostra "Comprar pão" como pendente

  @REQ-task-list-001
  Scenario: Acrescentar uma segunda tarefa mantém a primeira
    Given a lista tem a tarefa pendente "Comprar pão"
    When eu acrescento a tarefa "Pagar a conta"
    Then a lista mostra "Comprar pão" e "Pagar a conta" como pendentes

  @REQ-task-list-002
  Scenario: Marcar uma tarefa como feita
    Given a lista tem a tarefa pendente "Comprar pão"
    When eu marco "Comprar pão" como feita
    Then a lista ainda mostra "Comprar pão"
    And "Comprar pão" aparece como feita
```

`features/task-list/gate.json` (depois do primeiro `--fast` com PASS):

```json
{
  "schema_version": 1,
  "fast": { "exit_code": 0, "category": "PASS", "ref": "<QUALITY_DIR>/fast-2026-10-06.json" },
  "full": null,
  "ts": "2026-10-06T15:40:00Z"
}
```

Tabela de rastreabilidade correspondente, na primeira medida (o teste do terceiro cenário ainda não existe; `full` nunca rodou):

| REQ | cenário | teste | código | gate |
|---|---|---|---|---|
| REQ-task-list-001 | coberto (2 cenários) | coberto | coberto | coberto (`fast` PASS) |
| REQ-task-list-002 | coberto (1 cenário) | descoberto | descoberto | não medido |
