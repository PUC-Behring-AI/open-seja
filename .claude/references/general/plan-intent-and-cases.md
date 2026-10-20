---
designer_description: "When /plan writes a plan in format v3, I'm the shape it follows: the intention, the requirements, the use cases, my retelling in first person and your words, once per plan and before the steps, and a Covers: line on every step that tests a requirement -- so one file carries what you asked, what I understood and what proves it, and a tool can check that nothing was left without a use case or a test."
---

# GENERAL - PLAN INTENT AND CASES (plano v3)

> Formato do plano v3 (D-006). A entrevista que preenche estas seções é o jogo de linguagem (`.claude/references/general/plan-language-game.md`, regras JDL). O verificador é `.claude/skills/scripts/check_plan_intent.py`. Cada regra tem identificador estável `PIC-NNN`, **Quem decide** e **Critério de aceitação**.
>
> Planos v1 (`plan_format_version: 1`, ou sem versão) e v2 (ciclo com cenários da linhagem anterior) continuam válidos e nunca são reescritos; o verificador os relata como "nada a verificar".

## Constantes

```
PLAN_FORMAT_VERSION = 3
REQ_ID_REGEX = REQ-<slug>-NNN, slug = [a-z0-9]+(-[a-z0-9]+)*, NNN = 3 dígitos
INTENT_LINES = (Objetivo, O que você vê no fim, Não faz, Pronto quando)
SECTIONS = (Intenção, Requisitos, Casos de uso, Retradução, Nas suas palavras)
```

---

## Regras

### PIC-001 -- Cabeçalho

O H1 do plano segue `report-conventions.md`, seguido da linha `uid:` e da linha `plan_format_version: 3`. `--light` (proposal) e o resumo de roadmap continuam v1.

- **Quem decide**: o `/plan`.
- **Critério de aceitação**: `check_plan_intent.py` reconhece o plano como v3 pela linha `plan_format_version: 3` nas primeiras 10 linhas.

### PIC-002 -- Ordem e lugar das seções

Uma vez por plano, depois de `## User brief` e de `## Agent interpretation`, e antes de `## Steps`, nesta ordem:

1. `## Intenção`
2. `## Requisitos`
3. `## Casos de uso`
4. `## Retradução`
5. `## Nas suas palavras`

Nenhuma das cinco fica vazia num plano com código. Num plano do jogo curto (JDL-009), `## Requisitos` e `## Casos de uso` podem conter só uma linha `nenhum (<motivo>)`: `nenhum (tarefa sem código)` ou, num item de roadmap, `nenhum (jogo curto, item de roadmap)`.

- **Quem decide**: o `/plan`.
- **Critério de aceitação**: as cinco seções existem e têm conteúdo; o verificador devolve `error` para seção ausente ou vazia.

### PIC-003 -- `## Intenção`

Quatro linhas, cada uma uma frase ou uma lista curta:

```markdown
## Intenção
- Objetivo: <o que você quer, em uma frase> (A1, F2)
- O que você vê no fim: <o resultado observável> (A1)
- Não faz: <o que foi recusado, com o motivo quando houver> (A3)
- Pronto quando: <a condição de pronto, observável> (A1, A2)
```

As referências entre parênteses apontam para `## Nas suas palavras`. Um ponto aceito no teto do jogo (JDL-007) leva a fonte `teto`.

- **Quem decide**: você, pelas respostas do jogo.
- **Critério de aceitação**: as quatro linhas existem, cada uma com texto.

### PIC-004 -- `## Requisitos`

Uma linha de lista por requisito:

```markdown
## Requisitos
- REQ-contas-001: Você pode marcar uma conta como paga. Para que: você sabe o que ainda falta pagar. (A1)
- REQ-contas-002 (restrição): A lista abre em até 2 segundos com 500 contas. Para que: você não espera. (F3)
```

- O ID é `REQ-<slug>-NNN`, com o slug **em minúsculas** (kebab-case). O slug minúsculo não colide com os requisitos do as-intended (`REQ-ENT-001`, `REQ-MC-011`), que são em maiúsculas e são citados em `Traces:`.
- IDs únicos, contíguos de 001 a N, nunca reusados.
- Uma frase por requisito, com um comportamento só (JDL-008); `(restrição)` depois do ID marca o tipo restrição.
- "Para que:" em uma frase.
- A origem entre parênteses: `A<n>`, `F<n>` ou `teto`.
- No máximo 12 requisitos (`JOGO_MAX_REQS`).

- **Quem decide**: eu reescrevo; você aprova na Retradução (JDL-010).
- **Critério de aceitação**: todo requisito tem ID válido, frase, "Para que:" e origem; IDs únicos.

### PIC-005 -- `## Casos de uso`

Um ou mais casos de uso por requisito, em prosa e voz controlada. Cada caso de uso abre com o ID do requisito em negrito ou como subtítulo:

```markdown
## Casos de uso
- **REQ-contas-001**: Segunda de manhã, você abre a lista de contas, marca a de luz como paga e ela aparece na lista de pagas. (A1)
- **REQ-contas-002**: Você abre a lista com 500 contas e ela aparece em até 2 segundos. (F3)
```

Um caso de uso diz quem, quando, o que faz e o que vê. Ele é a cena aceita no jogo, reescrita em voz controlada. Não traz solução técnica.

- **Quem decide**: você, pelas cenas aceitas.
- **Critério de aceitação**: todo requisito de `## Requisitos` tem ao menos um caso de uso; todo caso de uso cita um requisito existente.

### PIC-006 -- `## Retradução`

Em primeira pessoa e em voz controlada: "Eu entendi que você quer ...", depois o que vou construir (requisito por requisito, o texto primeiro e o ID pequeno no fim), e uma subseção ou linha que começa com **"O que eu não vou fazer"**, com o "Não faz" da Intenção. Se nenhuma cena foi recusada, a Retradução diz "nenhuma cena foi recusada". A aprovação (Aprovar / Ajustar / Descartar, JDL-010) é registrada logo abaixo, na linha `Aprovação: aprovado em AAAA-MM-DD`.

- **Quem decide**: você aprova a mensagem; quem lê código vê os testes por requisito (D-004, D-006).
- **Critério de aceitação**: a seção existe e contém "O que eu não vou fazer" (`error` se faltar); a linha `Aprovação:` ausente é `warning`, porque o verificador roda durante o jogo, antes da aprovação.

### PIC-007 -- `## Nas suas palavras`

O índice do brief (`F1..Fn`, verbatim) e os lances do jogo (`A1..An`) no formato `A<n> (<lance>, <resposta>): "<texto do lance>" -> "<sua resposta>"`. As escolhas do teto (JDL-007) e as trocas de confidencialidade (JDL-004) também ficam aqui.

- **Quem decide**: você (as respostas são suas; os lances são meus).
- **Critério de aceitação**: toda origem `A<n>` ou `F<n>` citada em Intenção, Requisitos ou Casos de uso existe nesta seção.

### PIC-008 -- `Covers:` nos steps

Cada step com `Tests:` diferente de N/A declara, numa linha própria, os requisitos do plano que o teste dele demonstra:

```markdown
- **Tests**: when você marca uma conta como paga, ela aparece na lista de pagas (REQ-contas-001)
- **Covers**: REQ-contas-001
```

- `Covers:` só cita IDs de `## Requisitos` deste plano.
- `Covers:` só aparece em step com `Tests:` não-N/A.
- `Covers:` nunca vai dentro de `Traces:`. `Traces:` continua citando o as-intended (`REQ-MC-011`, `D-006`).
- Todo requisito é coberto por ao menos um step.
- O `/implement` escreve, para cada ID de `Covers:`, um teste que cita o ID no nome ou na docstring e fica vermelho pelo motivo certo antes do código.

- **Quem decide**: o `/plan` escreve; o `/implement` cumpre.
- **Critério de aceitação**: o verificador devolve `error` para requisito sem step, `Covers:` com ID inexistente, `Covers:` em step com `Tests: N/A` e ID de requisito do plano dentro de `Traces:`.

### PIC-009 -- O verificador

`check_plan_intent.py [<plano>] [--json]`:

- com um caminho, confere esse plano; sem argumento, varre `${PLANS_DIR}` (só arquivos `plan-*.md` que não são `-progress` nem `-qa-`);
- plano v1, v2 ou sem versão: "nada a verificar", saída 0;
- saída 0 sem `error`, 1 com algum `error`, 2 erro de uso;
- `--json` traz `schema_version`, a lista de planos e os achados (`severity`, `rule`, `message`, `line`).

- **Quem decide**: o verificador; PASS é resultado de ferramenta, não frase (T1).
- **Critério de aceitação**: cada regra PIC-002 a PIC-008 tem teste positivo e negativo em `test_check_plan_intent.py`.
