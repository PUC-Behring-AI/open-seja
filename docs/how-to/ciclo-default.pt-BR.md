---
diataxis: how-to
freshness: release-bound
last-reviewed: 2026-10-07
---

# O ciclo default do SEJA

> Guia em português, em voz controlada: frases curtas, uma ideia por frase e termos fixos. Os comandos ficam em inglês, como no harness. As regras completas estão nas referências citadas no fim.

## O que mudou

Numa tarefa com código, o `/plan` agora começa por uma conversa. Eu pergunto o que você quer, nas suas palavras. Depois eu escrevo o que entendi, e você aprova. Só então eu escrevo o plano.

No `/implement`, cada cenário vira um teste que falha antes de o código existir. Depois eu escrevo o código até o teste passar. No fim, eu guardo um retrato do que foi entregue.

No `/reflect`, eu mostro onde a sua intenção se perdeu, degrau por degrau. Eu também digo o que não consegui medir, e por quê.

## Por que mudou

O código que eu escrevo pode estar errado sem estar quebrado. Ele roda, os testes passam, e mesmo assim não é o que você pediu. Por isso a sua intenção passa por uma escada antes de virar código. Em cada degrau dá para ver o que se perdeu.

## Termos fixos

| Termo | O que é |
|---|---|
| grill | a entrevista em que eu pergunto o que você quer |
| intenção | a lista de requisitos que você aprovou, em `features/<slug>/intent.md` |
| specify | a fase em que eu escrevo os cenários e o que entendi |
| cenário | um exemplo de uso, escrito num arquivo `.feature`, que vira teste |
| retradução | o que eu entendi, em primeira pessoa, com exemplos; é isto que você aprova |
| degrau | a passagem de uma forma da intenção para a seguinte |
| retrato | o estado da feature congelado no fim do `/implement` |
| não medido | o que eu não consegui verificar, sempre com o motivo |
| interruptor | a linha `SPECIFY_DEFAULT` do projeto: `on` ou `off` |
| desvio | um plano que fez o contrário do interruptor, com o motivo registrado |

## A escada

```mermaid
flowchart LR
    I["Intenção<br/>(intent.md)"] -->|"D1: cada requisito tem cenário?"| C["Cenário<br/>(.feature)"]
    C -->|"D2: cada cenário tem teste?"| T["Teste"]
    T -->|"D3a: o teste passa no código e no portão?"| K["Código<br/>e portão"]
    K -.->|"D3b: há código sem cenário?"| T
```

| Degrau | O que ele pergunta | Quem olha | Onde fica |
|---|---|---|---|
| D1, intenção para cenário | cada requisito tem um cenário? | você aprova a retradução; quem lê código aprova o `.feature` | `intent.md` e `*.feature` |
| D2, cenário para teste | cada cenário virou teste? | a máquina | os testes e o relatório do runner |
| D3a, teste para código | o teste passa no código final e no portão? | a máquina; quem programa, se quiser | `gate.json` |
| D3b, código sem cenário | há código novo que nenhum cenário exercita? | a máquina; quem programa, se quiser | a cobertura dos cenários |

Cada degrau tem três estados: coberto, descoberto e não medido. Eu nunca junto os degraus num número só. O que não foi medido aparece ao lado, com o motivo.

## O que você faz em cada fase

1. **Pedir.** Você escreve `/plan` e o seu pedido. Eu faço perguntas curtas, poucas de cada vez.
2. **Aprovar a lista.** Eu mostro os requisitos e o que eu não vou fazer. Você aprova, ajusta ou descarta.
3. **Aprovar a mensagem.** Eu mostro o que entendi, com um exemplo por requisito. Você aprova ou pede ajuste.
4. **O contrato.** Quem lê código aprova o arquivo `.feature`. Se ninguém lê código, diga isso: eu registro e mostro depois.
5. **O plano.** Cada passo do plano cita os cenários que entrega. Se o plano for recusado, eu corrijo sozinho.
6. **A construção.** No `/implement`, eu escrevo um teste que falha, depois o código. Você não precisa fazer nada.
7. **A demonstração.** No fim, eu conto cada cenário como demonstrado, não demonstrado ou não medido.
8. **As perguntas.** Às vezes eu pergunto: "Se o código fizesse outra coisa, nenhum cenário perceberia. Isso importa para você?"
9. **A reflexão.** No `/reflect`, eu mostro o que ficou entre o seu pedido e o que existe. Você diz "é isso" ou "não é isso".

## Comandos

| Comando | O que faz |
|---|---|
| `/plan "<pedido>"` | grill, specify e plano, nesta ordem |
| `/plan --grill [<slug>]` | só a entrevista; escreve só o `intent.md` |
| `/plan --specify [<slug>]` | só os cenários, a retradução e as duas aprovações |
| `/plan --with-specify "<pedido>"` | liga a especificação neste plano, quando o projeto está em `off` |
| `/plan --without-specify "<motivo>" "<pedido>"` | desliga a especificação neste plano, quando o projeto está em `on`; o motivo é obrigatório |
| `/implement <id>` | teste que falha por cenário, depois o código; no fim, o retrato |
| `/implement <id> --pipeline` | também simplifica o código e reforça os testes; só se você pedir |
| `/reflect` | a divergência por degrau, ao lado da sua reflexão |
| `/explain drift ladder [<slug>]` | a mesma divergência, sem a reflexão |

## Como pular a escada, com motivo

- Uma proposta rápida: `/plan --light`. Ela não passa pela escada.
- Uma tarefa sem código, como documentação: a grill faz uma pergunta só. O plano registra `Specify: skipped -- tarefa sem código` com o motivo.
- Uma tarefa com código, sem a especificação: o interruptor em `off`, ou `/plan --without-specify "<motivo>"`. Veja a seção abaixo.
- Um roadmap: `/plan --roadmap`. O documento do roadmap segue o formato antigo.

Existe uma chave para desligar a especificação, e ela nunca é escondida: todo desvio fica registrado no plano. Veja "Ligar e desligar a especificação", logo abaixo.

## Ligar e desligar a especificação

O interruptor é a linha `SPECIFY_DEFAULT` em `product-design/conventions.md`. Ela vale `on` ou `off`. Sem a linha, vale `on`.

- Com `on`, toda tarefa com código passa pela escada: grill, specify e plano.
- Com `off`, numa tarefa com código, eu faço a entrevista curta e não escrevo a especificação. O plano registra `Specify: skipped -- default off`.

O `/seja-setup` pergunta o valor na instalação. O `/seja-setup --upgrade` pergunta quando a linha falta. Eu só gravo a linha se você responder. Sem resposta, eu não gravo, e vale `on` até você responder. Para mudar depois, edite a linha.

Um plano pode desviar do interruptor com uma de duas flags:

| Flag | Quando usar | O que o plano registra |
|---|---|---|
| `/plan --with-specify "<pedido>"` | o projeto está em `off`, e esta tarefa precisa de cenários | a escada inteira e `Specify: approved (rev N)` |
| `/plan --without-specify "<motivo>" "<pedido>"` | o projeto está em `on`, e esta tarefa não precisa de cenários | `Specify: skipped -- opt-out: <motivo>` |

O motivo é obrigatório: uma linha, com pelo menos três palavras. Sem motivo, eu recuso o plano em uma frase. `--with-specify` com `on` não faz nada. `--without-specify` com `off` também não. As duas flags não se combinam entre si nem com `--light`, `--grill`, `--specify` ou `--roadmap`.

Um exemplo é a prototipação. Num protótipo, o que o sistema deve fazer muda toda semana. Cenários escritos à força viram ruído na medida da escada. Num projeto que prototipa, use `off`. Quando uma parte do protótipo ficar estável, use `--with-specify` só no plano dela. O caso inverso: num projeto em `on`, um experimento descartável pode usar `--without-specify "experimento descartável para testar a biblioteca"`.

Sem a especificação, o plano não tem `Feature:` nem pasta. Um passo com código pode ter `Tests:` real, com `Scenarios: N/A (specify desligada neste plano)`. Eu ainda escrevo o teste antes do código.

Todo plano novo grava o braço do projeto no cabeçalho, na linha `Specify default: on` ou `Specify default: off`. É o valor de `SPECIFY_DEFAULT` no momento em que o plano foi escrito. Se você mudar o interruptor depois, os planos antigos não mudam.

**Como o desvio aparece.** Um desvio é um plano que fez o contrário do braço: `opt-out` com `Specify default: on`, ou `approved` com `Specify default: off`. O desvio não bloqueia nada. Ele é um achado:

- `check_plan_scenarios.py` dá um aviso `info` (PFS-016): o plano conta como desvio do default.
- `python3 .claude/skills/scripts/cycle_adherence.py` lista todos os planos: o braço de cada um, o que ele fez e os desvios, com o motivo. Use `--json` para a máquina e `--since AAAA-MM-DD` para começar numa data. O relatório mede aderência, não o resultado da escada.
- No `/reflect`, o relatório de divergência diz por que não há escada. Com `opt-out`: "Você escolheu não escrever a especificação neste plano: <motivo>." Com `default off`: "Não aplicável: a especificação está desligada neste projeto."

## Quando algo bloqueia

**"Os cenários voltaram a rascunho."** A entrevista foi reaberta, ou um cenário mudou depois da aprovação. Eu troco o campo para rascunho sozinho. Peça nova aprovação com `/plan --specify <slug>`.

**"Os cenários estão desatualizados: refaça a specify."** O `/implement` para antes de construir. A aprovação não vale mais para o que está no disco. Refaça a specify e rode o `/implement` de novo.

**O plano foi recusado.** Um passo muda o comportamento sem cenário. Ou um cenário aprovado ficou sem passo. Ou os cenários mudaram depois do plano. Eu corrijo o plano; você só vê a recusa se eu não conseguir.

**Eu parei e pedi ajuda.** Depois de três tentativas numa fase, eu paro. Eu mostro quatro saídas: ajustar o cenário, você assumir o passo, aceitar como parcial, ou tentar mais uma vez. Eu nunca ofereço afrouxar o portão.

**O portão me barrou entre o teste e o código.** O teste vermelho é esperado no meio do passo. O hook de parada pode barrar a pausa até três vezes; depois ele libera. Responda "continue" e eu sigo.

## Como atualizar

Rode `/seja-setup --upgrade`. Nada muda no que já existe: seus planos antigos continuam válidos para sempre. O upgrade faz uma pergunta só: se a especificação é o padrão neste projeto. Sem resposta, ele não grava nada, e vale `on`. Fora isso, nada novo é perguntado até você pedir código numa feature nova. Os novos checks dizem "nada a verificar" enquanto não há `features/`.

Num projeto Python, o plugin de relatório dos cenários só é atualizado se já estava instalado. Se ele não estava, a atualização não o cria. O `/implement` o instala na primeira vez que precisar.

## Para quem lê código

- Plano novo sai `plan_format_version: 2`, com `Feature: <slug>` e `Specify: approved (rev N)` no cabeçalho.
- Plano v2 novo também tem `Specify default: on|off`; o pulo é `Specify: skipped -- <classe>[: <motivo>]`, com as classes `tarefa sem código`, `default off` e `opt-out`.
- Cada passo tem `Scenarios:` com chaves `<slug>/<arquivo>.feature::<nome>`, ou `N/A (motivo)`.
- `check_plan_scenarios.py` recusa passo sem cenário, cenário sem passo, cenários velhos e `tarefa sem código` com teste.
- `check_specify.py --status` é a fonte de verdade da aprovação; o campo `scenarios:` é só o valor no disco.
- O retrato fica em `features/<slug>/drift/M1.json` e nunca é sobrescrito; o estado atual é o M2.
- O relatório usa o registro sem número técnico quando `scenarios_contract_by: ninguem`, ou quando alguém pede.

Referências: `.claude/references/general/extended-cycle-contract.md` (CYC), `grill-phase.md` (GRL), `specify-phase.md` (SPC), `plan-from-scenarios.md` (PFS), `implement-test-first.md` (ITF), `drift-metric.md` (DRM) e `drift-report.md` (DRP). O interruptor: CYC-035 e CYC-036, D-011.
