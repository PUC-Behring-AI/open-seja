# Rascunho D-006 e reescrita do as-intended (plan-20261020-688kjs, Step 6)

> Proposta do agente. Nada daqui é gravado em `product-design/` sem a sua confirmação no mesmo turno.
> Override de T3 e T4 limitado a este Step (respostas de 2026-10-20: "Também reescrever H-009 e decisões").
> Marcadores: D-006 entra com `STATUS: proposed | plan-20261020-688kjs`; a D-004 recebe `STATUS: superseded | plan-20261020-688kjs` (os dois por `apply_marker.py`).

## 1. Decisão nova (fim de `## Decisions`)

### D-006: A escada vive no plano: jogo de linguagem, intenção, requisitos, casos de uso e testes por requisito; sem Gherkin, sem grill

**Context**: A D-004 leu o `.feature` como contrato, não como mensagem, e o ciclo default da linhagem v0.11.0 o manteve como degrau da escada (`features/<slug>/`, `intent.md`, specify, grill). A reflexão do designer de 2026-10-20 concluiu: "Contrato não é mensagem". Se o citizen aprova a mensagem, o degrau do cenário pede uma aprovação que ele não decodifica e duplica, num segundo artefato, o que o plano já carrega. Num projeto cliente, a entrevista por jogo de linguagem (cenas aceitas, recusadas ou corrigidas) substituiu a grill como experimento, e o designer preferiu reconhecer cenas a formular requisitos de cabeça. O multi-dev (D-005) precisa continuar.

**Decision**: A escada vive no próprio plano, formato v3. O `/plan` joga o jogo de linguagem (`general/plan-language-game.md`) e escreve no plano `## Intenção`, `## Requisitos` (`REQ-<slug>-NNN`), `## Casos de uso`, `## Retradução` e `## Nas suas palavras`; cada step com teste declara `Covers:`; o `/implement` escreve um teste vermelho por requisito antes do código, nos modos auto e manual; `check_plan_intent.py` confere o plano. Não há Gherkin, `.feature`, `features/`, `intent.md`, grill nem specify. Da D-004 fica o essencial: o citizen aprova a mensagem (a retradução), não o contrato; o contrato de quem lê código são os testes por requisito. A linhagem parte de `2b17d27`, com o ULID portado; a anterior fica na tag `archive/gherkin-ladder-v0.11.0`. Não confundir com a D-006 da linhagem arquivada (uma pasta por feature).

**Consequences**: A D-004 passa a superseded. H-009 é reescrita para a escada no plano. Planos v1 e v2 continuam válidos e não são reescritos (o `/implement` roda v2 em manual e ignora `Scenarios:`). O upgrade remove dos clientes v0.11.0 os arquivos do ladder idênticos aos que instalou e avisa sobre `features/` e a camada PKB, sem apagar nada do projeto. A linhagem perde a granularidade por cenário, a medida de divergência por degrau (fica `não medido` até a medida por requisito existir), a camada PKB e o sinal as-expressed. O portão com CRAP e mutação escrito no ciclo v3, e a volta do cleaner e do hardener, ficam para outra rodada. A reescrita de H-009, da D-004 e das seções derivadas foi feita com override de T3 e T4 autorizado pelo designer, registrado no CHANGELOG.

**Rejected Alternatives**: remover o Gherkin para a frente, arquivo a arquivo (cerca de 24 steps); portar ULID e PKB (a PKB vive por fora no cliente); manter a grill com o jogo como desvio local; reusar `plan_format_version: 2` (colide com os planos v2 do ladder nos clientes); manter o `.feature` como contrato aprovado pelo power dev (dois artefatos por mudança).

*Source: plan-20261020-688kjs Step 6; reflexão do designer de 2026-10-20 (2026-10-20)*

## 2. H-009 (§3, 2.9) -- substitui os três parágrafos

Título da subseção: `#### 2.9 A escada de representações no plano (proposta)`

**H-009 (proposta, filha de H-008; reescrita em 2026-10-20 pela D-006) -- se o `/plan` decompõe a intenção dita em linguagem natural, por um jogo de linguagem, em representações progressivamente mais formais dentro do próprio plano (intenção -> requisitos com REQ IDs -> casos de uso -> um teste por requisito, escrito antes do código), o *as-coded* diverge menos do *as-intended* do que no ciclo PLAN -> BUILD -> REFLECT de H-008.**

Alcance declarado (herdado da D-004): a escada é completa para comportamento operacionalizado, com perda declarada de racional, modelo, preferência e crença sobre o usuário; essas categorias ficam na retradução julgada pelo citizen e em "Nas suas palavras". A divergência por requisito ainda não é medida: o `/reflect` diz `não medido` até um plano a construir.

O que a refutaria: se, numa janela de planos v3 fixada antes do primeiro dado, as respostas "recuso" e "corrijo" do jogo, os requisitos sem teste vermelho antes do código e os escapes de intenção achados depois do código forem todos zero, o jogo virou ritual, H-009 cai e H-001 volta a pedir adequação por posição na escala. O que a confirmaria: recusas e correções no jogo que mudam requisitos, e escapes de intenção raros nos planos v3 em que a deriva foi medida.

O texto anterior desta hipótese (escada com cenários, roadmap-000006) está na tag `archive/gherkin-ladder-v0.11.0`.

## 3. Seções derivadas

| Onde | Texto proposto |
|---|---|
| §0, linha 1 | `v0.12` -- A escada vive no plano: o `/plan` joga um jogo de linguagem (cenas que você aceita, recusa ou corrige) e escreve no próprio plano a intenção, os requisitos, os casos de uso, a retradução e as suas palavras; o `/implement` escreve um teste vermelho por requisito antes do código (H-009, D-006) -- STATUS: intended. Motivo: decompor a intenção em representações progressivamente formais (intenção -> requisitos -> casos de uso -> testes -> código) num único artefato, para que o as-coded divirja menos do as-intended, sem pedir ao citizen que aprove um contrato. |
| §0, linha 2 | `v0.12` -- Retradução em primeira pessoa como objeto de aprovação do citizen, dentro do plano; os testes por requisito são o contrato de quem lê código -- STATUS: intended. Motivo: o citizen aprova a mensagem, não o contrato (D-004, mantida na D-006). |
| §2, abertura | Duas hierarquias paralelas: a **estrutura do harness** (o que existe) e a **escada de representações dentro do plano** (intended, D-006). |
| §2, diagrama 1 | `Step (Files, Verify, Tests, Traces; Covers em v3 [intended])` |
| §2, diagrama 2 | `[intended] Plano v3` com `## Intenção`, `## Requisitos (REQ-<slug>-NNN; Para que; origem A<n>)`, `## Casos de uso`, `## Retradução`, `## Nas suas palavras`, e `Step com Covers:` -> teste por requisito (vermelho pelo motivo certo, depois verde) -> código + resultado do portão |
| §2, entidade `Feature [intended]` | vira `Plano v3 [intended]`: **Representa** o artefato único de uma mudança (intenção, requisitos, casos de uso, retradução, steps). **Regra**: todo requisito tem caso de uso e é coberto por um step com `Covers:`; `check_plan_intent.py` confere; planos v1 e v2 continuam valendo e não são reescritos. |
| Glossário, "Escada de representações" | brief -> jogo de linguagem -> intenção, requisitos e casos de uso no plano -> teste por requisito -> código + gate (H-009, D-006). |
| Glossário, "Degrau zero" | sai; entra **Jogo de linguagem [intended]**: a entrevista do `/plan`; eu conto cenas, você aceita, recusa ou corrige; aceito vira requisito ou caso de uso, recusado vai para "Não faz", corrigido é citado em "Nas suas palavras" (D-006). |
| Glossário, "Contrato endereçável" | sai; entra **Requisito endereçável [intended]**: `REQ-<slug>-NNN` no plano é o endereço para onde apontam o caso de uso, o step (`Covers:`) e o teste; o signo para o citizen é a retradução, não o ID (D-004, D-006). |
| Q-004 | ... **Fechada por D-004 (2026-10-05), relida pela D-006 (2026-10-20):** é etapa do `/plan` (a seção Retradução do plano) e do REFLECT, não artefato novo nem modo de `/explain`. |
| Q-012 | ... **Resposta parcial (D-004, 2026-10-05; D-006):** a retradução é julgada pelo receptor ("é isso / não é isso" por requisito), lógica CEM; o lugar do registro fica para quando a medida por requisito existir. |
| §8, REQ-UX-006 | [intended] **Jogo de linguagem no `/plan`**: rodadas curtas de até 3 lances; eu conto cenas e você aceita, recusa ou corrige; a aprovação é sobre a retradução em voz controlada; quem lê código vê os testes por requisito. |
| §10, duas linhas | `[intended] Jogo de linguagem: lances por rodada x rodadas` = `3 x 5` (teto, não alvo; no teto: continuar, aceitar como premissa, arquivar); `[intended] Aprovação da retradução: rodadas de ajuste` = `3` (ajuste repetido indica requisito vago; volta ao jogo). |
| SS-002 | Setting: mesma escada, dentro do plano, sem perfil; muda o objeto de aprovação. Rationale: para o citizen o código não pode ser a mensagem (H-001); os testes são o contrato, a mensagem é a retradução (D-004, D-006). Corpo: o citizen joga o jogo de linguagem, aceitando, recusando ou corrigindo cenas nas próprias palavras; recebe no plano a retradução em primeira pessoa, com os casos de uso e a lista do que não será feito, e aprova a mensagem; quem lê código (ele mesmo, em outro papel, ou o power dev) vê os testes por requisito; ao fim, recebe o que foi demonstrado por requisito e o que ficou `não medido`. |
| US-003 | critério 1: "retradução no plano, com 'Nas suas palavras' ao lado" (os outros dois ficam). |
| §14, REQ-MC-011 | [intended] Jogo de linguagem no `/plan` -- Eu lhe conto cenas do que entendi, um pouco de cada vez; você aceita, recusa ou corrige, e eu escrevo no plano os requisitos e os casos de uso que você reconheceu, antes de qualquer código. (2026-10-20) |
| §14, REQ-MC-012 | [intended] Retradução como objeto de aprovação -- Eu lhe mostro no plano, em primeira pessoa, o que entendi e o que vou construir, com casos de uso; você aprova a mensagem, e os testes ficam para quem lê código. (2026-10-20) |
| §14, REQ-MC-013 | [intended] Divergência por requisito -- Eu mostro qual requisito foi demonstrado, qual não foi e o que não medi, em vez de uma nota única. (2026-10-20) |
| §14, REQ-MC-014 | fica como está (preset `apprentice`). |
| JM-TB-002 | título "O citizen dev no jogo de linguagem, aprovando a mensagem"; pré-condição "plano v3 (D-006) entregue"; passo 1 "Joga o jogo: aceita, recusa ou corrige cenas" (dor: lances demais); passo 3 "Aprova a retradução com casos de uso"; passo 4 "Recebe o que foi demonstrado por requisito" (oportunidade: só o não demonstrado, por padrão); passos 2 e 5 ficam. |
| §16, REQ-DELTA-001 | `§0, §2, §3` -- Escada no plano, jogo de linguagem, plano v3, requisito endereçável -- intended; H-009, D-006 |
| §17, REQ-DELTA-004 / 006 | "Jogo de linguagem no `/plan`" (ver REQ-MC-011); "Divergência por requisito" (ver REQ-MC-013) |
| `design-standards.md:24` | `[intended] Jogo de linguagem` -- rodadas curtas de cenas que você aceita, recusa ou corrige; aprovação da retradução em voz controlada; o citizen aprova a mensagem, quem lê código vê os testes -- D-004, D-006 |

## 4. CHANGELOG (três linhas apensadas)

```
2026-10-20 | D-006 | added | plan-20261020-688kjs | a escada vive no plano (jogo de linguagem, intenção, requisitos, casos de uso, testes por requisito); sem Gherkin, grill nem specify
2026-10-20 | D-004 | superseded | plan-20261020-688kjs | substituída pela D-006; fica dela que o citizen aprova a mensagem, não o contrato
2026-10-20 | H-009 | revised | plan-20261020-688kjs | escada no plano com teste por requisito; texto anterior na tag archive/gherkin-ladder-v0.11.0; reescrita de H-009 e de §0, §2, §3 (glossário, Q-004, Q-012), §8, §10, §13, §14, §15, §16, §17 com override explícito de T3 e T4 autorizado pelo designer
```
