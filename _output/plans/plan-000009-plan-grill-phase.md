# Plan 000009 | FEATURE-O | METACOMM | 2026-10-05 11:26 UTC | plan-grill-phase: fase grill do /plan (entrevista até intenção detalhada com REQ IDs, voz que o citizen valida) | Review: standard

> **Origem**: movido do ledger do Doutourado em 2026-10-05 (proposal-000088; la era `plan-000078`). Os IDs roadmap-000006 e plan-000007..000016 sao deste ledger (tabela no roadmap). Referencias a research-NNNNNN, reflection-NNNNNN, communication-NNNNNN, roadmap-000062 e plan-000064..000074 apontam para o ledger do Doutourado (repositorio do pesquisador). Caminhos `open-seja/...` em Files passam a ser relativos a raiz deste repositorio.
plan_format_version: 1

> Item 3 do roadmap-000006 (Wave 1; Depends on: `default-cycle-contract` = plan-000007). Repositório de execução: **open-seja** (worktree/branch por plano). O plano vive no Doutourado. C1: nenhum nome de parceiro nos artefatos que forem ao open-seja. ID alocado pelo orquestrador (não usa `reserve_id.py`). Este plano é `plan_format_version: 1` porque o formato v2 só existe depois que o plano 000007 executar.

## Designer's metacommunication message (verbatim)

> Item 3 do roadmap-000006: `plan-grill-phase` (Depends on: default-cycle-contract). "Fase grill do /plan: entrevista até intenção detalhada com REQ IDs, em linguagem que o citizen valida (voz controlada do item 11 do roadmap-000062, plan-000074)."

## Agent interpretation

**Problem.** O plano 000007 fixou que o `/plan` tem uma fase grill que nunca é pulada e que escreve `features/<slug>/intent.md` com `REQ-<slug>-NNN`. Ele não diz **como** a entrevista corre, **quando ela para**, **o que é um bom REQ**, **como o citizen aprova** e **o que acontece quando não há código**. Sem isso, o item 5 (specify) não tem entrada confiável, e o D1 do plano 000008 (intenção→cenário, unidade = REQ) mede um REQ vago. Uma intenção mal entrevistada derruba a escada inteira de H-009 no primeiro degrau.

**Approach.** Plano **técnico** com um núcleo de design. Produz no open-seja: (a) a referência normativa `grill-phase.md` (protocolo, regra de parada, aprovação, degradação, voz); (b) o texto da fase grill dentro de `_internal/plan/standard/SKILL.md` e da flag reservada `--grill`; (c) um verificador **determinístico** `check_intent.py` (sem LLM) que decide se um `intent.md` está "detalhado o bastante" e se pode ser aprovado; (d) fixtures de três entrevistas (feature com código, tarefa sem código, brief já detalhado) como prova. O LLM conduz a entrevista; o verificador só confere a regra de parada, no estilo "PASS is a tool result, not a sentence" (research-000050). Nada aqui implementa specify (item 5), validador de `.feature` (item 4) ou formato v2 do plano (item 6).

**Alternatives rejected.**
- Parar a entrevista por julgamento livre do agente ("acho que já entendi"): não é verificável e o citizen não vê o critério. Rejeitado em favor de regra de parada mecânica mais aprovação humana.
- Número fixo de perguntas: uma feature pequena fica sobrecarregada e uma grande fica rasa. Rejeitado; entra só como **teto** de rodadas (Decisão pendente 2).
- Entrevista em formulário único com todas as perguntas de uma vez: o citizen não consegue responder ao que ainda não viu. Rejeitado; rodadas curtas, uma ideia por pergunta.
- Escrever o `intent.md` só ao fim: perde a entrevista se a sessão cair. Rejeitado; `intent.md` nasce em `status: grilling` e cresce a cada rodada (git é a recuperação, Q2).
- Skill `/grill` separada: já descartada pelo 000007 (Decisão pendente 1).

**Selection rationale.** Sem `source:`; o roadmap-000006 (item 3, H-009, tabela "Decisões") e os planos 000007 e 000008 são as fontes. O plano 000074 fornece a voz controlada (7 regras mensuráveis, limites `MAX_SENTENCE_WORDS=25`, `MAX_SENTENCES_PER_PARAGRAPH=6`, glossário opcional).

### Decisões fechadas (aprovadas pelo designer; não reabrir)
1. Grill e specify são fases internas do `/plan` e também invocáveis avulsas (`/plan --grill`, `/plan --specify`).
2. **Grill nunca é pulada.** Pode ser curta (uma rodada) quando o brief já traz intenção detalhada; a regra de parada vale igual.
3. Specify é pulada por tipo de tarefa (sem step com `Tests:` não-N/A); isso muda o que a grill entrega (ver "Degradação"), não se ela roda.
4. Layout `features/<slug>/{intent.md,*.feature,gate.json}`; REQ = `REQ-<slug>-NNN`; cenário tem `@REQ-<slug>-NNN`.
5. Divergência composta por degrau (000008): a unidade do D1 é o REQ de `intent.md` aprovado.
6. `plan_format_version: 2` exige `Scenarios:`; v1 é válido para sempre. A grill não muda v1.
7. Mesma fase para citizen e power dev: sem perfil. Muda quem olha cada degrau; o power dev pode acrescentar REQs de tipo `restrição`.
8. Voz controlada (plano 000074) em **tudo que o agente escreve para o citizen** nesta fase: perguntas, resumo, REQs reescritos. Fora da regra: citação verbatim do citizen, código, tabelas.

### Regra de parada (resumo; o texto normativo é o Step 2 e o verificador é o Step 4)
A intenção está "detalhada o bastante" quando **todas** as condições valem:

| # | Condição | Como se verifica |
|---|---|---|
| P1 | Cobertura das 6 dimensões: quem usa, o que faz, quando começa (gatilho), resultado que se vê, o que **não** faz, casos de erro e limites. Cada uma tem resposta, ou a marca `fora do escopo: <motivo do citizen>` | tabela "Dimensões" do `intent.md`; `check_intent.py` confere que nenhuma célula está vazia |
| P2 | Todo REQ tem **critério de aceitação** observável, na forma "Quando <ação de quem usa>, o sistema <resultado que se vê>" | regex da forma + lista de palavras vagas sem número (rápido, fácil, bom, simples, seguro, "etc") |
| P3 | Nenhuma **pergunta aberta** e nenhuma **premissa** sem confirmação | seções "Perguntas abertas" e "Premissas" vazias ou com `confirmado: sim` |
| P4 | IDs `REQ-<slug>-NNN` únicos, contíguos na criação, nunca reusados | `check_intent.py` |
| P5 | Cada REQ tem a coluna **"Nas suas palavras"** (citação verbatim do citizen ou `derivado de: REQ-...`) e a coluna **"Requisito"** (texto reescrito) | `check_intent.py`: nenhum REQ sem origem |
| P6 | **Aprovação humana** registrada | `status: approved`, `approved_at` (UTC), `approved_by: usuario` no frontmatter, escritos só depois de P1 a P5 passarem |

Teto: se após **5 rodadas** (≤ 4 perguntas cada) alguma condição P1 a P5 ainda falha, a grill **para e devolve a decisão ao citizen** (continuar, aceitar como premissa marcada, ou arquivar o tema). Nunca inventa resposta (Decisão pendente 2).

### Aprovação humana
O agente mostra o resumo em voz controlada: uma lista de REQs, cada um com critério em uma frase, mais a lista de "não faz". O citizen escolhe **Aprovar** / **Ajustar** / **Descartar** (AskUserQuestion, opções com `Recommended when` e `NOT recommended when`, C4). Só **Aprovar** grava `status: approved`. O specify (item 5) recusa `intent.md` com outro status. O citizen lê o texto, não o ID: o ID aparece pequeno, ao fim da linha.

### Degradação
| Situação | O que a grill faz | Artefato |
|---|---|---|
| Feature com código (algum step terá `Tests:` não-N/A) | Rodada completa até P1 a P6 | `features/<slug>/intent.md` aprovado; plano v2 |
| Tarefa sem código (docs, pesquisa, harness, config) | Entrevista **curta**: objetivo, resultado que se vê, o que não faz, critério de pronto. Sem REQ IDs, sem pasta | Seção `## Intenção` no próprio plano (4 linhas) e linha `Specify: skipped -- <motivo>`; aprovação do citizen no mesmo AskUserQuestion do plano |
| Brief já detalhado (colado pelo citizen com REQs ou critérios) | Uma rodada de **confirmação**: o agente reescreve em voz controlada, aponta o que falta em P1 a P5 e pergunta só isso | Mesmo `intent.md`; `Nas suas palavras` recebe o brief verbatim |
| Brief grande demais (mais de ~12 REQs prováveis) | Propõe quebrar em duas features com slugs distintos antes de entrevistar | Dois `features/<slug>/`; roadmap fica com o orquestrador |
| Projeto sem `features/` ou open-seja antigo (plano v1) | A fase não existe nessa versão; plano v1 segue como sempre | Nenhum; sem aviso de bloqueio |
| Citizen responde "não sei" | Registra **Premissa** (`confirmado: não`), propõe um default e pergunta uma vez; sem confirmação, vira pergunta aberta e bloqueia P3 | linha em "Premissas" |
| Citizen muda a intenção depois de aprovada (`/plan --grill` de novo) | `status` volta a `grilling`; REQ editado mantém o ID e sobe `rev`; REQ novo recebe o próximo número; REQ retirado vira `retirado` (nunca apagado, nunca reusado); histórico em "Mudanças"; reaprovação exigida | `intent.md` reaprovado; o specify marca cenários desatualizados |

### Decisões pendentes
Cada uma tem default (recomendação). Se o designer não responder, os steps seguem o default; mudar uma altera só o Step indicado.

**Decisão pendente 1 -- Esquema extra de `intent.md` (lacuna com o 000007, Step 4 dele)** (afeta Steps 2, 3, 4)
O 000007 define só: frontmatter `slug`, `status: grilling|approved`, tabela de REQ com texto e critério. A grill precisa de mais: `approved_at`, `approved_by`, `brief` verbatim, `rev` por REQ, coluna "Nas suas palavras", tabelas "Dimensões", "Perguntas abertas", "Premissas", "Mudanças".
- Opção A: emenda **aditiva** ao `feature-layout.md` do 000007 (campos novos, nenhum removido), feita por este plano.
- Opção B: `grill-phase.md` define as extensões e o `feature-layout.md` não muda; o validador aceita o esquema do 000007 como subconjunto.
- Opção C: reabrir o 000007.
- **Recomendação: B.** Recommended when o 000007 já foi revisto e executado e não se quer reabri-lo. NOT recommended when o item 4 (validador de `.feature`) for ler `intent.md` e precisar de uma única fonte de esquema (então A, como emenda registrada). C rejeitada: o 000007 já está fechado.

**Decisão pendente 2 -- Teto de rodadas e o que fazer ao atingi-lo** (afeta Steps 2, 4)
- Opção A: sem teto.
- Opção B: teto de 5 rodadas de até 4 perguntas; ao atingir, devolve a decisão ao citizen.
- Opção C: teto de 3 rodadas.
- **Recomendação: B.** Recommended when o roadmap lista fricção do citizen como risco e o piloto (item 10) mede o tempo até a primeira feature aprovada. NOT recommended when o piloto mostrar que features reais precisam de mais rodadas (então subir o teto por `conventions.md`). Os números 5 e 4 são palpite a calibrar no piloto; ficam em constantes (`GRILL_MAX_ROUNDS`, `GRILL_MAX_QUESTIONS_PER_ROUND`).

**Decisão pendente 3 -- Tipos de REQ** (afeta Steps 2, 4)
- Opção A: um tipo só (comportamento observável).
- Opção B: dois tipos, `comportamento` e `restrição` (desempenho, segurança, limite); restrição também exige critério observável e ganha cenário no specify.
- **Recomendação: B.** Recommended when o power dev precisa registrar limites que o citizen não pensaria em pedir. NOT recommended when o specify (item 5) não souber transformar restrição em cenário (então A e restrição vira texto do critério). O D1 do 000008 conta os dois tipos igual.

**Decisão pendente 4 -- Dependência do plano 000074 (voz controlada)** (afeta Steps 4, 5)
O verificador de voz `lint_controlled_language.py` é um passo do 000074, que pode ainda não estar entregue no open-seja. 
- Opção A: este plano exige o 000074 entregue (bloqueia o Step 4 até lá).
- Opção B: `check_intent.py` chama o lint do 000074 **se existir** e, se não existir, aplica só os dois limites numéricos (25 palavras por frase, 6 frases por parágrafo) com as mesmas constantes, e registra `voz: não verificada` como ressalva.
- **Recomendação: B.** Recommended when o roadmap-000062 item 11 ainda está `pending` (está, no ledger). NOT recommended when o 000074 já estiver entregue (então A, sem duplicar). Evita duas implementações divergentes: B importa as constantes, nunca copia o texto das regras.

**Decisão pendente 5 -- Quem escolhe o slug** (afeta Step 2)
- Opção A: o agente propõe em kebab-case e o citizen confirma na primeira rodada.
- Opção B: o agente escolhe sem perguntar.
- **Recomendação: A.** Recommended when o slug vira nome de pasta e tag de REQ para sempre (nunca renomeado). NOT recommended when o brief já traz um nome. Colisão com pasta existente: a grill recusa e pergunta se é a mesma feature (reentrada) ou outra.

## Files

Todos no **open-seja** (repositório de execução), exceto onde dito. O submodule não está inicializado neste worktree; caminhos **não verificados**: o Step 1 os confere antes de qualquer escrita.

- `.claude/references/general/grill-phase.md` (create) -- protocolo normativo da fase
- `.claude/references/template/intent.md` (create) -- modelo de `intent.md` com exemplo fictício
- `.claude/skills/scripts/check_intent.py` (create) -- verificador determinístico (local conforme o Step 1)
- `.claude/skills/scripts/tests/test_check_intent.py` (create)
- `.claude/skills/_internal/plan/standard/SKILL.md` (modify) -- texto da fase grill e flag `--grill`
- `.claude/skills/plan/SKILL.md` (modify) -- argumento `--grill` na tabela
- `tests/fixtures/grill/` (create) -- 3 entrevistas e `intent.md` esperados (caminho conforme o Step 1)
- `.claude/references/general/extended-cycle-contract.md` (modify, só linha de ponteiro, se existir após o 000007)
- `_output/plans/plan-000009-progress.md` (create no Doutourado)

## Best practices

- Contrato primeiro, execução depois: citar `CYC-NNN` do 000007 em `Traces:`/texto; se ainda não existir no open-seja, marcar "a confirmar" (como o 000008).
- "PASS is a tool result, not a sentence" (research-000050): a regra de parada é função pura sobre o arquivo.
- Grill é do humano; o agente conduz e escreve, o citizen decide (Pocock: o humano como loop externo que impõe a opinião). O agente **nunca** preenche resposta que o citizen não deu: o que não veio vira premissa marcada.
- Critério de aceitação em forma observável (Uncle Bob: Gherkin é critério de aceitação), mas sem Given/When/Then ainda: essa tradução é do specify.
- Voz controlada: frases ≤ 25 palavras, uma ideia por frase, ≤ 6 frases por parágrafo, um termo por conceito, aviso antes da instrução, imperativo nas instruções (plano 000074). Termos fixos nas perguntas: "requisito" (não "requirement", "necessidade", "regra"), "o que você vê" para resultado observável, "fora do escopo" para o que não se faz.
- Texto do citizen é verbatim e fica fora do lint; o texto reescrito pelo agente fica dentro.
- Determinismo: ordem de saída estável, sem relógio dentro do verificador (o `approved_at` é escrito pela fase, não pelo `check_intent.py`).

## Design decisions

- **User-visible impact:** antes de qualquer plano de código, eu te faço poucas perguntas por vez, em frases curtas. Cada resposta sua vira um requisito com uma frase de critério ("Quando você faz X, o sistema mostra Y"). Eu paro quando todas as seis dimensões estão respondidas, não há dúvida aberta e você aprova a lista. Se for uma tarefa sem código, a conversa é curta e não cria pasta.
- **Trade-offs accepted:** mais conversa antes do código (fricção do citizen, medida no piloto do item 10) em troca de um primeiro degrau que se pode medir. A regra de parada mecânica pode aceitar uma intenção bem formada e ainda errada; por isso a aprovação humana e a auditoria semântica do 000008 (Decisão pendente 1 dele) existem. O teto de rodadas pode devolver ao citizen uma decisão que ele preferiria que o agente tomasse; aceito, porque H-009 mede a intenção, não a esperteza do agente.
- **Metacommunication impact:** I know you may not program by trade; therefore I ask you, a little at a time and in short sentences, what you want in your own words, and I write it back as a list of requirements you can read and correct. I only go on to the scenarios after you say "approve". If I cannot find out something, I tell you it is an assumption instead of deciding for you.

## Steps

### Step 1: Conferir o terreno e as dependências no open-seja
Na branch `dev` do open-seja (`git submodule update --init open-seja` se vazio), registrar no progress: (a) se o plano 000007 já está lá (`extended-cycle-contract.md`, `feature-layout.md`, `plan-step.md` com `Scenarios:`) e os `CYC-NNN` reais da fase grill e do layout; (b) se o plano 000074 já está lá (`controlled-language.md`, `lint_controlled_language.py`, constantes `MAX_SENTENCE_WORDS`, `MAX_SENTENCES_PER_PARAGRAPH`); (c) o texto atual de `_internal/plan/standard/SKILL.md` (onde entra a fase, antes do atual passo 3) e da tabela de argumentos de `plan/SKILL.md`; (d) onde moram os scripts e os testes de `.claude/skills/scripts/`; (e) o glossário `product-design/glossary.md`, se existir. Se (a) faltar, escrever os Steps 2 a 6 contra o vocabulário do plano 000007 do Doutourado e marcar cada `CYC-NNN` como "a confirmar". Nada é escrito no open-seja.
- **Files**: open-seja/.claude/references/general/extended-cycle-contract.md (read, se existir), open-seja/.claude/references/template/feature-layout.md (read, se existir), open-seja/.claude/references/general/controlled-language.md (read, se existir), open-seja/.claude/skills/_internal/plan/standard/SKILL.md (read), open-seja/.claude/skills/plan/SKILL.md (read)
- **References**: product-design/conventions.md, product-design/constitution.md
- **Interface**: N/A
- **Verify**: o progress lista, para cada item (a) a (e), "existe", "rascunho" ou "ausente" com caminho; `git -C open-seja status` limpo.
- **Tests**: N/A (verificação de estado)
- [x] Done

### Step 2: Escrever o protocolo normativo `grill-phase.md`
Criar o documento com regras `GRL-NNN` (cada uma com "Quem decide" e "Critério de aceitação", no molde de `CYC-NNN`): (1) entrada (brief verbatim) e saída (`features/<slug>/intent.md`); (2) conduta da entrevista: rodadas de até `GRILL_MAX_QUESTIONS_PER_ROUND` perguntas, uma ideia por pergunta, pergunta aberta antes de fechada, o agente propõe um default quando o citizen trava, mas grava como premissa; (3) as 6 dimensões e uma pergunta-modelo em voz controlada por dimensão (pt-BR e en-US); (4) o que é um bom REQ (observável, um comportamento por REQ, sem solução técnica no texto, critério na forma "Quando ..., o sistema ...") com 3 exemplos bons e 3 ruins; (5) a regra de parada P1 a P6 do plano, tal como na tabela acima; (6) o teto `GRILL_MAX_ROUNDS` e a devolução da decisão; (7) a aprovação (resumo, opções Aprovar/Ajustar/Descartar, o que `Aprovar` grava); (8) a tabela de degradação do plano; (9) reentrada e mudança depois de aprovada (ID estável, `rev`, `retirado`, "Mudanças"); (10) a voz: quais textos estão dentro e fora da regra, glossário fixo de termos; (11) o que a fase **não** faz: não escreve Gherkin (item 5), não valida `.feature` (item 4), não decide formato do plano (item 6), não reconstrói gate nem hooks; (12) a interface reservada `--grill`: lê/escreve só `intent.md`, nunca escreve plano. Incluir, para as Decisões pendentes 1 a 5, o default adotado marcado `[default; pendente]`. C1: sem nome de parceiro.
- **Files**: open-seja/.claude/references/general/grill-phase.md (create)
- **References**: product-design/constitution.md, product-design/product-design-as-intended.md
- **Depends on**: Step 1
- **Interface**: constantes `GRILL_MAX_ROUNDS=5`, `GRILL_MAX_QUESTIONS_PER_ROUND=4`, `GRILL_DIMENSIONS=(quem, o_que, gatilho, resultado, nao_faz, erros_limites)`.
- **Verify**: o arquivo existe; todo `GRL-NNN` tem "Quem decide" e "Critério de aceitação"; `grep -c "GRL-"` >= 12; cada dimensão tem pergunta-modelo; `git grep -ci` dos termos de C1 devolve zero; `python .claude/skills/scripts/run_all_checks.py` igual ao baseline do Step 1.
- **Tests**: N/A (documento normativo; a verificação mecânica é o Step 4)
- **Docs**: o próprio arquivo; o quickguide pt-BR fica para o item 9.
- [x] Done

### Step 3: Escrever o modelo de `intent.md` com exemplo fictício
Criar `template/intent.md`: frontmatter (`slug`, `status: grilling|approved`, `brief` verbatim, `approved_at`, `approved_by`, `rev`), tabela de REQ (colunas: ID, tipo, **Nas suas palavras**, **Requisito**, **Critério**, `rev`, `estado: ativo|retirado`), tabela "Dimensões" (6 linhas), "Fora do escopo", "Perguntas abertas", "Premissas" (com `confirmado`), "Mudanças". Exemplo fictício completo (sem parceiro, sem dado real): feature de 3 REQs, uma restrição, uma premissa confirmada, tudo em voz controlada. Marcar com comentário o que é emenda aditiva ao esquema do 000007 (Decisão pendente 1, default B: o modelo é um **superconjunto** do esquema do 000007; um `intent.md` mínimo do 000007 continua válido).
- **Files**: open-seja/.claude/references/template/intent.md (create)
- **References**: open-seja/.claude/references/template/feature-layout.md (read)
- **Depends on**: Step 2
- **Interface**: esquema de `intent.md` lido por `check_intent.py` (Step 4) e, depois, pelo specify (item 5) e pelo relatório (item 8).
- **Verify**: o exemplo passa em `check_intent.py` (Step 4) com `--require-approved`; o arquivo mínimo do esquema do 000007 também passa sem `--require-approved`; nenhum termo de C1.
- **Tests**: N/A (modelo; coberto pelas fixtures do Step 4)
- **Docs**: o próprio modelo.
- [x] Done

### Step 4: Verificador determinístico `check_intent.py` (regra de parada)
Função pura `check_intent(text: str, *, require_approved: bool = False) -> list[Finding]` mais CLI (`check_intent.py <intent.md> [--require-approved] [--json]`). Confere P1 a P6: dimensões preenchidas ou `fora do escopo: <motivo>`; critério na forma "Quando ..., o sistema ..." e sem palavra vaga sem número (lista em constante); "Perguntas abertas" vazia e "Premissas" todas `confirmado: sim` (para P3); IDs `REQ-<slug>-NNN` com slug igual ao do frontmatter, únicos, sem reuso (retirado conta como usado); cada REQ com "Nas suas palavras" ou `derivado de:`; `status: approved` só se `approved_at` e `approved_by` existem; voz controlada no texto do agente (colunas "Requisito" e "Critério", resumos) por `lint_controlled_language` se existir, senão pelos dois limites numéricos com as constantes do 000074 (Decisão pendente 4, default B), com ressalva `voz: não verificada`. Citação do citizen e tabelas de código ficam fora. Exit 0 sempre, exceto `--strict` (exit 1 se houver `error`); saída ordenada e idêntica para o mesmo texto; sem relógio. Cada `Finding`: `regra`, `linha`, `mensagem` em voz controlada, `severidade` (`error` para P1 a P6; `warning` para voz).
- **Files**: open-seja/.claude/skills/scripts/check_intent.py (create), open-seja/.claude/skills/scripts/tests/test_check_intent.py (create)
- **References**: product-design/standards.md § Testing, product-design/constitution.md
- **Depends on**: Step 2, Step 3
- **Interface**: `check_intent(text: str, *, require_approved: bool = False) -> list[Finding]`; `Finding(regra: str, linha: int, mensagem: str, severidade: str)`; constantes `VAGUE_WORDS`, `GRILL_DIMENSIONS`.
- **Verify**: `pytest .claude/skills/scripts/tests/test_check_intent.py` verde; `ruff check` e `pyright` limpos no escopo do open-seja; `python .claude/skills/scripts/check_intent.py template/intent.md --require-approved --strict` sai 0.
- **Tests**: quando um REQ não tem critério, devolve `error` P2 na linha do REQ; quando o critério é "o sistema deve ser rápido", devolve `error` P2 por palavra vaga sem número; com "responde em até 2 segundos" não devolve; quando uma dimensão está vazia, devolve `error` P1 com o nome da dimensão; com `fora do escopo: <motivo>` não devolve; quando há linha em "Perguntas abertas", devolve `error` P3 e `--require-approved` falha; quando uma premissa tem `confirmado: não`, devolve `error` P3; quando dois REQs têm o mesmo ID, devolve `error` P4; quando o slug do ID difere do frontmatter, devolve `error` P4; quando um REQ não tem "Nas suas palavras" nem `derivado de:`, devolve `error` P5; quando `status: approved` e falta `approved_by`, devolve `error` P6; quando uma frase do "Requisito" tem 26 palavras, devolve `warning` de voz; citação em "Nas suas palavras" com 40 palavras não devolve nada; mesmo texto duas vezes produz saída idêntica; `--strict` sai 1 com `error` e 0 sem; `intent.md` mínimo do esquema do 000007 passa sem `--require-approved`.
- **Docs**: cabeçalho do script com a tabela P1 a P6 e ponteiro para `grill-phase.md`.
- [x] Done

### Step 5: Escrever a fase grill no `/plan` e a flag `--grill`
Em `_internal/plan/standard/SKILL.md`, inserir a fase **antes** da criação das seções do plano: ler `grill-phase.md`; classificar o tipo de tarefa (com código / sem código / brief já detalhado); conduzir a entrevista por rodadas; gravar `features/<slug>/intent.md` em cada rodada (`status: grilling`); rodar `check_intent.py` ao fim de cada rodada para decidir se continua; ao passar, apresentar o resumo e pedir aprovação (AskUserQuestion, C4); só então gravar `approved` e seguir. Para tarefa sem código, escrever a seção `## Intenção` e a linha `Specify: skipped -- <motivo>`. Em `plan/SKILL.md`, acrescentar `--grill` à tabela de argumentos ("roda só a grill e para; escreve só `intent.md`; reentrada permitida") e manter `--specify` como reservada do item 5. Não mudar o texto da fase de revisão nem do `/implement`. Metacomm: a pergunta e o resumo usam I/you quando o brief é metacomm.
- **Files**: open-seja/.claude/skills/_internal/plan/standard/SKILL.md (modify), open-seja/.claude/skills/plan/SKILL.md (modify), open-seja/.claude/references/general/extended-cycle-contract.md (modify, só ponteiro)
- **References**: product-design/constitution.md, product-design/standards.md
- **Depends on**: Step 4
- **Interface**: flag `--grill` do `/plan`; a fase lê `GRILL_*` de `grill-phase.md` e chama `check_intent.py`.
- **Verify**: `git diff --stat` mostra só os três arquivos listados; `python .claude/skills/scripts/check_skill_system.py` e `run_all_checks.py` com resultado igual ao baseline; `grep -n "grill" .claude/skills/plan/SKILL.md` acha `--grill` na tabela; `grep -n "skipped" .claude/skills/_internal/plan/standard/SKILL.md` acha a linha `Specify: skipped`; nenhum arquivo de gate, hook ou `settings` no diff.
- **Tests**: N/A (instruções de skill; a prova de comportamento é o Step 6)
- **Docs**: SKILL-quickguide do `/plan` fica para o item 9.
- [x] Done

### Step 6: Provar a fase com três entrevistas de referência
Criar três fixtures (transcrição curta + `intent.md` final esperado) e um roteiro de execução manual: (a) **feature com código** fictícia, 3 rodadas, termina em `approved`; (b) **tarefa sem código** (atualizar um README fictício): entrevista curta, sem pasta, com `Specify: skipped`; (c) **brief já detalhado**: uma rodada de confirmação. Para cada uma, anexar a saída de `check_intent.py` e provar a regra de parada com pares negativos (a versão da rodada anterior falha com a regra certa). Rodar a fase real (`/plan --grill`) uma vez em modo dry-run sobre (a) e registrar no progress: número de rodadas, número de perguntas, avisos de voz, e se o citizen fictício (o designer) entendeu cada pergunta sem pedir reformulação (observação manual; é dado de calibração para os números 5 e 4). Rodar `run_all_checks.py` e a leitura de um plano v1 antigo no `/plan` para provar que nada mudou para quem não usa a fase.
- **Files**: open-seja/tests/fixtures/grill/ (create), `_output/plans/plan-000009-progress.md` (create no Doutourado)
- **References**: product-design/constitution.md
- **Depends on**: Step 4, Step 5
- **Interface**: N/A
- **Verify**: `check_intent.py --require-approved --strict` sai 0 nas três versões finais e sai 1 nas versões intermediárias marcadas; o progress tem rodadas, perguntas e avisos de voz de (a); `run_all_checks.py` retorna o mesmo conjunto de falhas pré-existentes que o baseline (nenhuma nova); nenhum termo de C1 no diff (`git grep -i` com a lista do Step 1).
- **Tests**: when `check_intent.py` roda sobre cada versão intermediária das fixtures, returns o `error` esperado (P1, P2, P3 conforme a fixture); sobre cada versão final, returns lista sem `error`. Reusa os testes do Step 4 com as fixtures como entrada.
- [x] Done

### Step 7: Fechar o contrato com os itens vizinhos
Registrar no progress uma tabela "o que este plano entrega a quem": item 4 (convenção `.feature` lê `REQ-<slug>-NNN` e `intent.md` aprovado), item 5 (specify recusa `intent.md` sem `status: approved`, usa `check_intent.py --require-approved` como portão), item 6 (o plano v2 cita `Feature: <slug>`), item 8 e plano 000008 (D1 conta os REQs `ativo` de `intent.md` aprovado; REQ `retirado` não entra no denominador depois de reaprovado, e conta como descoberto até a reaprovação, como o 000008 já define), item 9 (quickguide e `/help` descrevem `--grill`), item 10 (tempo de grill é parte do tempo até a primeira feature aprovada; usar os dados do Step 6 como linha de base). Listar as lacunas com os planos 000007 e 000008 (abaixo) e as decisões pendentes que ficaram no default.
- **Files**: `_output/plans/plan-000009-progress.md` (modify no Doutourado)
- **References**: product-design/constitution.md
- **Depends on**: Step 6
- **Interface**: N/A
- **Verify**: a tabela cobre os itens 4, 5, 6, 8, 9, 10; cada linha cita uma regra `GRL-NNN`; lista as 5 decisões pendentes com o default em uso.
- **Tests**: N/A (registro)
- [ ] Done

## Lacunas e conflitos com os planos 000007 e 000008

1. **Esquema de `intent.md` (000007, Step 4).** O 000007 não prevê `approved_at`, `approved_by`, `brief`, `rev`, "Nas suas palavras", "Dimensões", "Premissas", "Mudanças". Tratado como superconjunto (Decisão pendente 1, default B). Risco: o item 4 pode escrever um validador só para o esquema mínimo.
2. **Ciclo de vida do REQ (000008, D1).** O 000008 diz que REQ removido depois da aprovação conta como descoberto até a reaprovação. Este plano define `retirado` com ID nunca reusado e reaprovação obrigatória, o que é compatível; mas o 000008 não trata `rev` (REQ editado). Proposta: `rev` incrementado marca os cenários do REQ como desatualizados até o specify reaprovar; o D1 não muda. Falta uma linha no `drift-metric.md` do 000008.
3. **Tipo `restrição` (Decisão pendente 3).** O 000008 conta REQ sem distinguir tipo; o 000007 também. Sem impacto se contado igual; confirmar no Step 1 do 000008.
4. **Tarefa sem código.** O 000007 diz que não cria pasta; este plano coloca a intenção curta no plano. O 000008 marca relatório "não aplicável" para esse caso; consistente.
5. **Voz controlada.** O 000074 fixa D2 (fora: citação verbatim, `product-design/`); aqui o texto reescrito do REQ está dentro e a citação do citizen fora. Se o 000074 ainda não estiver entregue, vale a Decisão pendente 4 (default B).
6. **Ordem de aprovação.** O 000007 exige "sem `intent.md` aprovado não há specify". O verificador deste plano é o mecanismo que o item 5 deve usar; hoje o 000007 não nomeia um verificador.
7. **`--specify` e `--grill` avulsos.** O 000007 trata as flags como interface reservada, a decidir nos itens 3/5. Este plano as implementa só para `--grill`.

## Coverage (advisory)

`product-design/product-design-as-intended.md` do Doutourado não tem marcadores REQ; `critique_plan_coverage.py` não se aplica e `Traces:` fica ausente. O plano executa no open-seja.

## Metacomm Intention
- **Summary**: I tell you that, before any plan for code, I ask you a little at a time what you want, I write it back as numbered requirements in short sentences you can correct, I stop only when nothing is open, and I only go on after you approve.
- **Source**: agent (metacomm)

Metacomm contradiction check: nenhuma intenção existente em `product-design-as-intended.md` (D-001 a D-005) conflita; D-004 (`apprentice`) e D-005 (`literature-reviewer`) tratam de presets e ficam fora do escopo, como no roadmap.

## Review log

**Review depth:** Standard (7 steps, ~9 arquivos distintos). Phase 1 inline; o agente `plan-reviewer` não foi lançado nesta execução (plano gerado em subagente isolado). Sem Phase 2 (nenhum Deferred com risco de regressão). Prefixo FEATURE-O sem linha na tabela de atalhos: usei DX, TEST, COMPAT, ARCH, SEC, UX.

### Step metadata validation
- Todo step tem Files, References, Interface, Verify, Tests, checkbox; `Depends on` forward-only; nenhum step toca mais de 5 arquivos (Step 5 toca 3; Step 4 toca 2).
- `Tests:` não-N/A (Steps 4 e 6) expressam comportamento observável ("when X, devolve Y").
- Caminhos do open-seja **não verificados** (submodule vazio): o Step 1 é o portão.

### Phase 1 -- Perspective scan

| Perspective | Status | Concern |
|---|---|---|
| DX | Adopted | Regra de parada em tabela P1 a P6; cada step com Verify por comando ou `grep`. |
| TEST | Adopted | Verificador determinístico com testes de comportamento; pares negativos nas fixtures. Steps 2, 3, 5, 7 documentais: `Tests: N/A` justificado. |
| COMPAT | Adopted | Plano v1 e `intent.md` mínimo do 000007 continuam válidos; Step 6 prova leitura de plano v1. |
| ARCH | Adopted | Sem LLM no verificador; gate e hooks não tocados (diff do Step 5 limitado). |
| SEC | Adopted | C1 por `git grep` nos Steps 2, 6; nenhuma chave nem `.env`. |
| UX | Adopted | Aprovação humana explícita; premissas marcadas; voz controlada; teto de rodadas contra fricção. |
| PERF, DB, API, I18N, A11Y, VIS, RESP, DATA, OPS, MICRO | N/A | Sem superfície. I18N: pergunta-modelo em pt-BR e en-US no Step 2. |

### Riscos e lacunas registrados
- Números 5 rodadas e 4 perguntas são palpite; calibrar no Step 6 e no piloto (item 10).
- Regra de parada mecânica não prova que a intenção está certa; depende da aprovação humana e da auditoria semântica do 000008.
- O lint de voz depende do 000074 (Decisão pendente 4).
- Fricção do citizen só é medida no item 10.

### Execution Metrics
| Metric | Value |
|---|---|
| Review depth | Standard |
| Phase 1 perspectives | 6 adopted, 10 N/A |
| Phase 2 deep-dives | 0 |
| Iterations | 0 |
| Pending decisions | 5 (defaults indicados) |

## Outcomes

- `grill-phase.md` com regras `GRL-NNN`, regra de parada P1 a P6, aprovação humana e degradação.
- `template/intent.md` com REQ IDs estáveis, critério por REQ, "Nas suas palavras" e exemplo fictício.
- `check_intent.py` determinístico, testado, que decide se a intenção está detalhada o bastante.
- Fase grill e flag `--grill` no `/plan`; plano v1 e tarefas sem código continuam funcionando.
- Fixtures de três entrevistas e dados de calibração (rodadas, perguntas, avisos de voz).

smoke: false
