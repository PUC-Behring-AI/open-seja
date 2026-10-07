# Rascunho para o /design -- as-expressed, Q-014 e limiar do gatilho

> Origem: plan-000020, Step 9 (2026-10-07). Este arquivo é **proposta** para o designer. O agente não escreve prosa em `product-design/product-design-as-intended.md` (T4, Human (markers)); o texto abaixo é para você colar via `/design`, editar ou recusar. Nada aqui é decisão até você decidir.
>
> Fonte verbatim: a nota de inbox do Doutourado de 2026-10-06 (`inbox/2026-10-06-ideia-open-seja-chat-para-inbox-e-live-communicate.md`), com as palavras: "esta faltando o /design no ciclo quando o as-expressed, as-intended e as-coded divergem muito".
>
> Numeração proposta: a próxima decisão livre é D-012 e a próxima questão aberta é Q-014 (o CHANGELOG do as-intended já reserva Q-014). Confira antes de colar.

---

## 1. Emenda a H-005 (§3, 2.4)

Substituir o texto de H-005 por este, ou acrescentar como parágrafo de emenda.

**H-005 (hipótese, emendada) -- Há quatro estados da intenção, não dois, e só uma parte da primeira lacuna é comparável por máquina.**

O par de 1.2.2 (as-intended / as-coded) esconde dois termos. Há o que o designer **concebeu** (na cabeça, sem artefato); o que ele **disse** ao harness, em linguagem natural (**as-expressed**: a fala registrada no `conversation-trace.jsonl` e na nota de `inbox/`); o que ele **registrou** (`product-design-as-intended.md`, planos, briefs: o as-intended); e o que **existe** (as-coded). Isso dá lacunas assim:

| Lacuna | Entre | Verificável por máquina? | Como aparece |
|---|---|---|---|
| 1a | as-conceived -> as-expressed | não capturável | o designer não disse tudo o que queria; o que ficou na cabeça não deixa traço |
| 1b | as-expressed -> as-intended | sim, por texto | o registro (brief, plano, as-intended) diz outra coisa que a fala; o preposto parafraseou, resumiu ou deslocou |
| 2 | as-intended -> as-coded | sim (`/explain drift`, `check_plan_coverage`) | a implementação diverge do registro |

A 1a continua elicitável, não verificável: a surpresa no EXPLAIN (2.2) e o microloop de PLAN são as sondas. A 1b passa a ter um sinal determinístico: `pkb_inbox.py capture` compara a fala capturada com o `## User brief` do plano gerado, depois de normalizar, e grava `as_expressed_igual_ao_brief: true | false` no cabeçalho da nota. É um sinal de **presença de diferença**, não de fidelidade: `false` diz que o texto mudou, não que o sentido mudou nem que o sentido foi traído.

**O que a confirmaria:** notas de inbox com `as_expressed_igual_ao_brief: false` em que o designer, ao ler fala e brief lado a lado, aponta que o registro perdeu ou deslocou algo (um ajuste do registro, no `/design` ou no próprio plano); e `/design` sendo acionado a partir do gatilho (Q-014) e mudando o as-intended, não só o código. Em resumo: a 1b produzindo ajustes de registro.

**O que a refutaria:** toda diferença da 1b tratada como paráfrase inocente, sem nenhum ajuste de registro depois de uma janela de planos fixada antes (D-012); ou `as_expressed_igual_ao_brief` ficando `true` em quase todos os casos, o que indicaria que o sinal não discrimina (o brief é cópia da fala) e a 1b não é um lugar onde a intenção se perde.

**Limitação real, achada na construção (plan-000020, Steps 6 e 8):** a captura só vê a fala do designer quando o `conversation-trace.jsonl` a registrou e a encadeou. Duas dependências, ambas frágeis na prática:

1. **Encadeamento por `preceding_evt_id`.** A fala do usuário entra no trace com o campo `led_to_skill` nulo; só a resposta do agente costuma levar a skill. Sem o `preceding_evt_id` correto ligando fala e resposta, a captura não acha a fala e devolve `nothing-to-capture`. O `append` grava `null` por padrão quando o agente esquece a flag.
2. **Caminhada da cadeia da troca.** Por isso `conversation_trace.exchange_user_entries` parte de cada entrada do agente marcada com a skill e caminha `preceding_evt_id` por entradas do usuário até encontrar uma entrada do agente (ou outra skill). Se a cadeia estiver quebrada, a fala se perde e a nota sai sem ela, com `fonte: briefs` declarando a perda.

Consequência para a hipótese: onde a captura falha, a 1b fica **não medida**, e o `/reflect` deve dizer `não medido`, nunca `igual`. Um `true` só vale quando a fala foi de fato capturada.

*(Nota de nomenclatura: "as-expressed" é escolha deste documento para o estado dito, entre o concebido e o registrado.)*

---

## 2. Nova questão aberta (§3, tabela de Questões abertas)

Acrescentar a linha:

| ID | Questão | Bloqueia |
|---|---|---|
| `Q-014` | A partir de que medida de deriva o ciclo volta ao `/design` em vez de abrir outro `/plan`? A medida é o número de itens do relatório do `/explain drift` (construído sem intenção, intenção não construída) e o resíduo da 1b (`as_expressed_igual_ao_brief: false`). E em que ponto o gatilho dispara: na etapa 2c do post-skill (ao fim de um `/implement` com deriva medida, ou de um `/plan` cuja captura veio com `false`), no REFLECT, ou nos dois? D-012 propõe o mecanismo e deixa o valor para você. | gatilho de `/design` por deriva; leitura de H-005 |

---

## 3. Decisão proposta

Acrescentar ao fim de `## Decisions` (append-only). O valor numérico é seu: **não o preenchi**, porque `DESIGN_TRIGGER_DRIFT_ITEMS` sai vazio (= gatilho desligado) e fixar o valor depois de ver dados invalida a medida (constituição Q3).

### D-012: O gatilho de /design por deriva tem limiar e janela fixados antes do primeiro dado; vazio significa desligado

**Context**: A sessão de 2026-10-06 registrou a lacuna: falta o `/design` no ciclo quando as-expressed, as-intended e as-coded divergem muito. Hoje a deriva é medida (`/explain drift`) e a fala é capturada (inbox do plan-000020), mas nada leva deriva grande ao `/design`; o caminho natural é abrir outro `/plan`, que muda o código e deixa o registro como está (a deriva tratada como bug de código, refutação de H-005). O harness entrega o mecanismo (variável `DESIGN_TRIGGER_DRIFT_ITEMS` em `product-design/conventions.md`, vazia; etapa 2c do post-skill; sinal `as_expressed_igual_ao_brief`), mas não o valor.
**Decision**: O post-skill recomenda `/design` (nunca bloqueia) quando o relatório de deriva do `/implement` registra `n` itens com `n >= DESIGN_TRIGGER_DRIFT_ITEMS`, ou quando a captura de um `/plan` vem com `as_expressed_igual_ao_brief: false`. Valor inicial de `DESIGN_TRIGGER_DRIFT_ITEMS`: **`<N>` [PREENCHER PELO DESIGNER]**. Número mínimo de planos com deriva medida antes da primeira leitura de H-005 pela 1b: **`<M>` [PREENCHER PELO DESIGNER]**. O valor e a janela são gravados em `conventions.md` e neste registro **antes** de qualquer plano ser contado; mudá-los depois exige nova decisão que supere esta, com os dados anteriores marcados como lidos sob o limiar antigo. Vazio continua significando desligado, e o `/reflect` registra `gatilho desligado` ao lado do que mediu. Deriva `não medida` aparece como `não medida`, nunca como zero.
**Consequences**: O gatilho é recomendação, na linha da 2c; o `/design` continua sendo escolha sua (os espelhos são oferecidos, nunca impostos, D-002). A taxa de acionamento e o que o `/design` fez depois (mudou o as-intended, ou nada) viram dados de H-005. Onde a captura falha (cadeia `preceding_evt_id` quebrada), a 1b fica `não medida` e o plano não conta para a janela `<M>`. O sinal `as_expressed_igual_ao_brief` mede diferença de texto, não de sentido; falsos positivos (paráfrase inocente) são esperados e entram na leitura como o custo do sinal.
**Rejected Alternatives**: gatilho só por evento no `/implement` (perde a 1b: a intenção pode se desviar já no brief, antes de haver código); gatilho só por período, a verificação de 14 dias (tarde demais; a deriva acumula por semanas e o designer só volta ao `/design` por acaso); um LLM julgando se a divergência é grande (a medida deixa de ser resultado de ferramenta, T1, e não é reprodutível; o julgamento semântico fica com você, na retradução, D-004); fixar o limiar depois de ver os primeiros planos (invalida a medida, Q3).

*Source: plan-000020 Step 9, rascunho para /design (2026-10-07)*

---

## 4. Linhas de CHANGELOG para apensar à mão

`CHANGELOG_APPEND` não aceita ids H/Q, então estas linhas entram à mão (ajuste a data ao dia em que você decidir):

```
2026-10-07 | H-005 | revised | plan-000020 | as-expressed como quarto estado; lacuna 1 dividida em 1a (nao capturavel) e 1b (comparavel por texto, sinal as_expressed_igual_ao_brief); condicoes de confirmacao e refutacao atualizadas; limitacao da captura (encadeamento preceding_evt_id) declarada
2026-10-07 | Q-014 | added | plan-000020 | a partir de que medida de deriva o ciclo volta ao /design em vez de abrir outro /plan, e em que ponto (post-skill 2c, REFLECT)
2026-10-07 | D-012 | added | plan-000020 | limiar DESIGN_TRIGGER_DRIFT_ITEMS e janela minima de planos fixados antes do primeiro dado; vazio = desligado; valor numerico a preencher pelo designer
```

Se D-012 puder usar `DECISION_APPEND` (`apply_marker.py --marker DECISION_APPEND`), a linha de D-012 do CHANGELOG pode vir dele; as de H-005 e Q-014 não.

---

## 5. O que fica para você

- Preencher `<N>` e `<M>` em D-012 e gravar `DESIGN_TRIGGER_DRIFT_ITEMS` em `product-design/conventions.md` (o harness não grava).
- Decidir se Q-014 fica aberta até haver dados, ou se o ponto de disparo (2c, REFLECT, ambos) já fecha.
- Não medido neste plano: se o inbox é processado ou só acumula, e o valor do limiar. Ambos são objeto da janela `<M>`.
