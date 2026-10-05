# Plan 000016 | FEATURE-O | 2026-10-05 14:10 UTC | default-cycle-pilot: o TaskFlow (Python) nos dois ciclos, divergência por degrau, tempo até a primeira feature aprovada e /reflect | Review: standard

> **Origem**: movido do ledger do Doutourado em 2026-10-05 (proposal-000088; la era `plan-000085`). Os IDs roadmap-000006 e plan-000007..000016 sao deste ledger (tabela no roadmap). Referencias a research-NNNNNN, reflection-NNNNNN, communication-NNNNNN, roadmap-000062 e plan-000064..000074 apontam para o ledger do Doutourado (repositorio do pesquisador). Caminhos `open-seja/...` em Files passam a ser relativos a raiz deste repositorio.
plan_format_version: 1

> Item 10 do roadmap-000006 (Wave 4; Depends on: default-cycle-wiring = plan-000015). Plano de **execução com humano no loop**: quase tudo que ele produz são medidas, registros e uma decisão sobre H-009, não código de produto. Os steps marcados **[DESIGNER]** não andam sem você; os marcados **[AGENTE]** o agente faz sozinho; **[AMBOS]** é conversa. Repositório de execução do harness: **open-seja** (só leitura aqui, nenhuma alteração); a feature-piloto é o **TaskFlow em Python** (demo do open-seja; ver `### Feature-piloto`); os artefatos do piloto vivem no Doutourado, em `_output/pilot-default-cycle/`. C1: nenhum nome de parceiro em nada que sair do Doutourado. Este plano não edita o roadmap nem `_output/INDEX.md`, não publica, não faz merge nem push.
>
> **Pré-condição dura:** os planos 000007 a 000015 estão escritos, mas ainda **não executados** no open-seja. Este plano só começa depois que o 000015 entregou a tabela "o que este plano entrega ao item 10" (comando do braço novo, comando do braço de controle, onde ficam M1/M2). O Step 1 para se isso não existe.

## User brief

> Item 10: `default-cycle-pilot` (Depends on: default-cycle-wiring). "Uma feature real no ciclo novo e a mesma no ciclo padrão; medir divergência por degrau e tempo até a primeira feature aprovada; /reflect."
>
> Decisão do designer (2026-10-05): a feature é o TaskFlow, o projeto de demonstração do open-seja, em Python.

## Agent interpretation

**Problem.** H-009 (roadmap-000006) diz que decompor a intenção em representações progressivamente mais formais faz o *as-coded* divergir menos do *as-intended* do que o ciclo padrão. Os itens 1 a 9 construíram o ciclo e a régua (000008: D1, D2, D3a, D3b, O1, tempo; 000014: o calculador); nenhum deles rodou uma feature de verdade. Sem o piloto, H-009 continua uma proposta e o risco "fricção do citizen" do roadmap continua sem dado.

**Approach.** Estudo de caso controlado, uma feature, dois braços, **três réplicas por braço** (seis execuções), ordem alternada, com **oráculo independente congelado por hash** antes de qualquer execução (protocolo do 000008, sem reabri-lo). Cada execução é medida pelo `drift_report.py` (000014) e pelo oráculo; o tempo sai dos eventos `t0`, `t_verde`, `t_aprovada` do `pilot-run-record.md` (000008); a auditoria semântica é humana e cega (todos os REQs do braço A, ao menos 30% dos do B). A análise aplica a regra `D_B >= D_A` com empate abaixo de 1 item e as três cláusulas de refutação de H-009 (000007, Step 6), sem p-valor. O `/reflect` fecha o ciclo, ancorado nos artefatos, com as suas palavras registradas verbatim. A decisão sobre H-009 (prosa Human) é sua; o plano só prepara o texto.

**Alternatives rejected.**
- Rodar o braço de controle com uma chave de desativação no ciclo novo: contamina a medida (000015, Decisão pendente 3). O braço A usa a **tag anterior pinada**.
- Uma execução por braço: não mede a variância do agente (000008, Decisão pendente 2 = 3 réplicas).
- Dois designers (um deles citizen) já neste piloto: custo e coordenação fora do orçamento; vira follow-up (Decisão pendente 4).
- Candidatas K1 a K4 (`lint-sources`, guarda de segredos, validador de frontmatter, `status --json`): descartadas pelo designer em favor do TaskFlow.
- Deixar o próprio ciclo novo escrever o oráculo: o ciclo mediria a si mesmo (lei de Goodhart; 000008).
- Medir só o tempo e a nota final: esconde em que degrau a intenção se perdeu.

**Selection rationale.** Sem `source:`. Fontes lidas: roadmap-000006 (item 10, H-009, riscos "fricção do citizen" e "mudança no core"), planos 000007 (condição de refutação), 000008 (protocolo do controle, oráculo, réplicas, tempo), 000013 (teste-primeiro, `--pipeline` opt-in, escalada), 000014 (relatório por degrau, M1/M2, `audit.json`), 000015 (integração, ensaio, upgrade por tag, entrega ao item 10), roadmap-000062 (item 9 e backlog D9), o template do demo (`.claude/references/template/demo/`), research-000050 (gate: "PASS is a tool result, not a sentence"; Pocock: o humano como loop externo), constitution.md (T2, T3, Q1, Q2, S1, C1) e conventions.md.

### Decisões fechadas (não reabrir neste plano)
1. **3 réplicas por braço.** Ordem dos braços alternada (pares de réplica com ordens opostas) e registrada.
2. **Auditoria semântica humana cega:** todos os REQs do braço A (retrofit) e ao menos 30% dos REQs do B; coluna separada do D (`adequado: sim/parcial/não`).
3. **"Feature aprovada" = aceitação explícita do designer**, reportando `t_verde` (primeiro `gate full` PASS) e O1 ao lado.
4. **Estudo de caso, sem p-valor e sem "significativo".** Feature com menos de 8 REQs = `amostra pequena`.
5. **`--pipeline` (Cleaner, Hardener) opt-in:** o braço B roda **sem** `--pipeline` por default (Decisão pendente 5 trata a variante).
6. Divergência **composta, reportada por degrau** (D1, D2, D3a, D3b, mais O1); sem número único e sem pesos.
7. Regra de comparação: `D_B >= D_A` = sem redução; empate quando a diferença é menor que 1 item do denominador.
8. O braço A é o **ciclo padrão da tag anterior** (plano v1, sem grill/specify); o braço B é o **ciclo novo na tag corrente** do 000015 (publicada ou, antes da publicação, instalada de um clone local).

### Feature-piloto: TaskFlow em Python (decisão do designer)
**Decisão fechada (antes Decisão pendente 1):** a feature do piloto é o **TaskFlow**, o projeto de demonstração do open-seja (criado por `/seja-setup --demo`; template em `.claude/references/template/demo/`: `product-design-as-intended.md` com as entidades Category e Task e os REQ markers, `conventions.md`, `constitution.md`, `WALKTHROUGH.md`, `product-overview.yaml`). Hoje o demo é TypeScript + React, só navegador. **Decisão do designer sobre a stack: TaskFlow em Python.** O scratch gerado pelo `/seja-setup --demo` tem a stack trocada nas `conventions.md` do scratch (um passo documentado, Step 5), e a feature do piloto é uma **camada de domínio em Python puro**, sem UI e sem persistência em navegador, testada com **pytest-bdd**. Candidatas descartadas: K1 `pegasus lint-sources`, K2 guarda de segredos no ingest, K3 validador de frontmatter PKB, K4 `pegasus status --json` (alternativas do rascunho anterior; não são mais opções).

**Recorte proposto (a fixar no Step 3 e no Step 4; é o ponto de partida, não o oráculo).** Regras do domínio, tiradas do texto do demo (§2 Entity Hierarchy, §3 Status Toggle, §10 Validation Constants), cada uma observável:

| # | Regra candidata | Origem no demo |
|---|---|---|
| C-1 | Nome de Category com 1 a 30 caracteres | §2, §10 |
| C-2 | Nome de Category único **sem diferenciar maiúsculas** | §2 |
| C-3 | A Category "General" existe no início e **não pode ser deletada** | §2 |
| C-4 | No máximo 20 Categories | §10 |
| T-1 | Título de Task com 1 a 120 caracteres | §2, §10 |
| T-2 | Descrição de Task com 0 a 500 caracteres (opcional) | §2, §10 |
| T-3 | Status inicial `todo`; o toggle alterna `todo` <-> `done`, sem estado intermediário | §2, §3 |
| T-4 | Task pertence a exatamente uma Category existente | §2 |
| T-5 | No máximo 200 Tasks por Category | §10 |
| T-6 | Deleção de Task é permanente (sem soft delete) | §2 |

São 10 regras: o recorte tem folga sobre o mínimo de 8 (F2). O demo é **omisso** em pontos que a grill do braço B vai perguntar e que o oráculo precisa fixar (por exemplo, o que acontece com as Tasks ao deletar uma Category; o formato aceito de `color`; se "General" pode ser renomeada). Isso é desejável: são as ambiguidades que a escada deve fazer aparecer.

**Interface pública (proposta; o Step 3 a fixa no brief).** Módulo `taskflow.domain` com um repositório em memória e funções sobre ele: `new_store()`, `create_category(store, name, color)`, `delete_category(store, category_id)`, `create_task(store, category_id, title, description="")`, `toggle_task(store, task_id)`, `delete_task(store, task_id)`; entidades como dataclasses imutáveis; violações levantam `DomainError` com um `code` estável (`name_too_long`, `name_duplicate`, ...). A lista exata de nomes, assinaturas e códigos de erro é congelada no brief.

**Os REQ markers do demo não são o oráculo.** O demo tem apenas 4 marcadores, de granularidade grossa (`REQ-ENT-001`, `REQ-VAL-001`, `REQ-MC-001`, `REQ-JM-001`); os dois últimos são de UI (intenções de metacomunicação e jornada), fora do recorte. Servem de ponto de partida para o `requisitos.md`, que é **escrito pelo designer, mais granular (um REQ por regra observável), independente e congelado por hash antes de qualquer execução**, e **não é mostrado ao braço A**. O braço B tem acesso ao que a própria escada produzir (inclusive a grill), nunca ao oráculo.

### Critérios para escolher a feature-piloto, aplicados ao TaskFlow
Os critérios continuam sendo o que torna a feature medível. Análise honesta, contra o TaskFlow em Python:

| # | Critério | Por quê | TaskFlow em Python |
|---|---|---|---|
| F1 | **Python puro e sem modelo/rede nos testes** | Evita D9 (o smoke do harness só cobre Flask) e o ruído do `run_all_checks` em projeto novo; testes rápidos e determinísticos | **Atende só com a stack trocada.** O demo de fábrica é TypeScript + React; sem a troca nas conventions do scratch, não atende. Com ela, a camada de domínio é Python puro, em memória, sem rede (conferido nos Steps 2 e 5) |
| F2 | **>= 8 REQs observáveis** | Denominador mínimo para D1/D2/D3a/D3b | **Atende com o recorte escolhido, não com os markers do demo.** O demo tem 4 REQ markers, 2 deles de UI; o recorte C-1..T-6 dá 10 regras observáveis. Se o designer cortar o recorte abaixo de 8, declarar `amostra pequena` (Step 4) |
| F3 | **Interface pública fixável no brief** | O oráculo roda nos dois braços; sem interface comum, O1 não é comparável | **Atende:** módulo, funções, dataclasses e códigos de erro fixados no brief (Step 3) |
| F4 | **Cabe em um dia de agente por execução** | Orçamento: 3 réplicas por braço | **Atende:** camada de domínio pequena; o teto de 4 h por execução vale |
| F5 | **Valor real para o designer** | A aceitação (`t_aprovada`) só significa algo se o designer quer a feature | **NÃO atende de forma plena.** É um demo: o designer não precisa do TaskFlow. **Limitação registrada** (abaixo) |
| F6 | **O designer sabe responder à grill** | A grill do braço B só pode ser respondida a partir do oráculo | **Atende:** domínio pequeno e conhecido; as respostas saem do oráculo, que o designer escreve |
| F7 | **Não existe ainda e não está em outro plano aberto** | Evita braço que "já sabe" a resposta e conflito de trabalho | **Atende:** o scratch é gerado limpo; nada do TaskFlow existe no Doutourado. **Ressalva:** o TaskFlow é difundido e o modelo pode "já saber" (Decisão pendente 8) |
| F8 | **Sem segredo, `.env`, material institucional ou de parceiro** (S1, C1) | | **Atende:** o demo é público do upstream; os dados de teste são sintéticos |
| F9 | **Efeito colateral em disco previsível** | Cada execução em ambiente isolado | **Atende:** domínio em memória; o ambiente é o scratch por execução |

**Limitação de F5 e como o piloto lida com ela.** Como o TaskFlow é um demo, a aceitação do designer **não** mede "quero isso no meu arquivo". O piloto mantém como aceitação o que já estava decidido: **`t_aprovada` = aceitação explícita do designer** do que foi construído em relação ao que ele pediu (o oráculo), dada antes de ver O1 (Decisão pendente 6). Consequências declaradas: (i) "feature real" aqui significa uma feature com regras de negócio e ambiguidades reais, não uma necessidade do designer; (ii) o atrito registrado (Decisão pendente 4) reflete trabalho sobre um problema que o designer não precisa resolver, o que tende a **subestimar** a vontade de pular degraus; (iii) a Decisão pendente 7 (destino do código) passa a ser, na prática, "descartar", salvo se o designer quiser reaproveitar; (iv) o relatório (Step 10) lista isso entre as ameaças.

**Ganho opcional (sem acoplar planos).** O mesmo projeto pode servir de evidência ao item 9 do roadmap-000062 (`hypothesis-first-run` em `seja-demo-taskflow`). É reaproveitamento **opcional**: os dois planos continuam independentes, nenhum depende do outro nem muda o escopo do outro, e este plano não executa nem presume nada do item 9.

### Decisões pendentes
Cada uma tem default (a recomendação). Se você não responder, os steps seguem o default. A antiga Decisão pendente 1 ("qual feature") está **fechada**; a numeração das demais foi mantida, a 2 foi reescrita e a 8 é nova.

**Decisão pendente 1 -- FECHADA.** Feature-piloto = TaskFlow em Python (acima). Sem opções abertas.

**Decisão pendente 2 -- Onde cada execução roda** (a escolha do designer está feita; resta confirmar a mecânica; afeta Step 5)
Cada execução parte de um **scratch novo gerado por `/seja-setup --demo`** na **tag do braço** (A = tag anterior pinada; B = tag com o ciclo estendido, ou clone local se ainda não publicada), fora da árvore do Doutourado, com a troca de stack documentada em **um passo** (editar as `conventions.md` do scratch de TypeScript + React para Python 3.13 + `uv` + `pytest` + `pytest-bdd` + `ruff` + `pyright`, ajustando o que for específico de React). Se o `/seja-setup --demo` não suporta trocar a stack, não instala a tag anterior (`--version <tag>`) ou não combina `--demo` com `--version`, o Step 1 manda **parar e registrar**.
- Opção A (default): scratch novo por execução, gerado por `--demo` na tag do braço.
- Opção B: gerar o scratch uma vez por braço e copiá-lo por réplica.
- **Recomendação: A.** Recommended when o harness do Doutourado (v0.9.1, skills PKB) contaminaria os braços e o scratch limpo satisfaz F7. NOT recommended (B) when a cópia carrega histórico de agente e memória entre réplicas.

**Decisão pendente 3 -- Como contar os "três degraus" da condição de refutação** (**[DESIGNER]**; afeta Steps 10, 11; lacuna 2)
O 000007 fala em "ao menos dois dos três degraus" (intenção→cenário, cenário→teste, teste→código); o 000008 dividiu o último em D3a e D3b.
- Opção A: D3 conta como **reduzido** só se D3a e D3b não pioram e ao menos um cai além do empate; uma réplica "ganha" o degrau; o degrau vale se a maioria das 3 réplicas pareadas ganha (2 de 3).
- Opção B: contar D3a e D3b como degraus separados (quatro degraus, regra "ao menos 3 de 4").
- Opção C: comparar a mediana das réplicas.
- **Recomendação: A.** Recommended when o texto de H-009 fala em três degraus e as réplicas são pareadas por ordem oposta. NOT recommended (C) when 3 réplicas não sustentam mediana e o 000008 diz "relatar as três, nunca a média sozinha". NOT recommended (B) when muda o texto de H-009 sem você decidir.

**Decisão pendente 4 -- Fricção do citizen: o que este piloto pode e não pode dizer** (**[DESIGNER]**; afeta Steps 9, 11, 12)
Você é um desenvolvedor experiente; o roadmap pergunta sobre o citizen. O piloto mede só o **seu** atrito.
- Opção A: registrar o seu atrito (perguntas da grill, pontos de dúvida, vontade de pular um degrau) e declarar que **o citizen não foi testado**.
- Opção B: acrescentar, depois do estudo, uma execução do braço B com um citizen real como designer, só observação (sem entrar na regra `D_B >= D_A`).
- Opção C: não registrar atrito.
- **Recomendação: A agora, B como follow-up.** Recommended when o orçamento é de uma pessoa e o risco do roadmap (lentidão percebida) precisa de ao menos o dado qualitativo. NOT recommended (C) when "mais passos antes do código" é justamente o risco declarado. B vira plano próprio se H-009 sobreviver.

**Decisão pendente 5 -- Braço B com ou sem `--pipeline`** (afeta Step 5)
- Opção A: sem `--pipeline` (default do 000013, opt-in).
- Opção B: com `--pipeline` (Cleaner e Hardener) em todas as réplicas.
- Opção C: réplicas 1 e 2 sem; réplica 3 com, só para observação (fora da comparação).
- **Recomendação: A.** Recommended when o roadmap fechou `--pipeline` como opt-in e a hipótese é sobre a escada, não sobre mutação. NOT recommended (B) when isso confundiria o efeito da escada com o do endurecimento. C só se você quiser os "findings por step" do 000013 e aceitar uma execução fora da comparação.

**Decisão pendente 6 -- Você vê O1 antes de aceitar?** (**[DESIGNER]**; afeta Steps 6 a 8, 9)
- Opção A: a aceitação (`t_aprovada`) acontece **antes** de qualquer execução do oráculo; O1 é calculado depois e reportado ao lado.
- Opção B: você vê O1 e então aceita.
- **Recomendação: A.** Recommended when a aceitação precisa expressar "isto atende ao que eu quero", não "isto passa na minha régua". NOT recommended (B) when o objetivo é medir tempo até aprovação do designer: mostrar O1 transforma o oráculo em critério de parada.

**Decisão pendente 7 -- Destino do código depois do estudo** (**[DESIGNER]**; afeta Step 12)
- Opção A: aplicar no Doutourado a execução que você escolher (por patch, em plano próprio), independente do braço.
- Opção B: aplicar a melhor execução do braço B.
- Opção C: descartar tudo; só ficam as medidas (o código é de um demo; ver limitação de F5).
- **Recomendação: C**, com A só se você quiser o domínio TaskFlow como material de ensino ou como base do item 9 do roadmap-000062 (reaproveitamento opcional). Recommended when a feature é um demo que você não precisa no arquivo e escolher um braço enviesaria a leitura. NOT recommended (B) when isso faz o resultado parecer decidido. Nada é aplicado dentro deste plano.

**Decisão pendente 8 -- Contaminação por o TaskFlow ser conhecido** (**[DESIGNER]**; nova; afeta Steps 3, 4, 10)
O TaskFlow é um demo difundido: o modelo pode já "conhecer" o projeto e a stack original (TypeScript + React), o que (a) faz o braço A (e o B) acertar por memória e não por causa do ciclo, borrando a diferença entre braços, e (b) vaza para o oráculo se ele reproduzir o demo ao pé da letra (O1 mede conhecimento prévio, não a escada).
- Opção A: **recorte original**: renomear entidades e termos (por exemplo Category -> Lista, Task -> Tarefa/Item, "General" -> outro nome) e **mudar números e regras** do recorte (limites diferentes dos do demo, uma regra própria a mais), mantendo a estrutura. O oráculo é escrito sobre o recorte renomeado.
- Opção B: **REQs adicionais próprios** sem renomear: manter Category/Task e acrescentar 3 a 4 regras que o demo não tem (por exemplo, arquivar Category, ordenação estável, unicidade de título por Category), escritas pelo designer e fora do texto do demo.
- Opção C: usar o demo como está, só declarar a ameaça.
- **Recomendação: A, com 2 regras próprias do designer (A + B parcial).** Recommended when o objetivo é medir a escada e não a memória do modelo; renomear e mudar limites força o agente a derivar o comportamento do brief/grill, e as regras próprias dão um conjunto que nenhum material público contém. NOT recommended (C) when o resultado seria lido como efeito do ciclo. Mesmo com A, o relatório declara que a contaminação não se elimina (a estrutura Category/Task continua reconhecível) e o Step 4 inclui um teste de sanidade (sonda de contaminação) antes de congelar o oráculo: um agente sem harness recebe só o brief, e se reproduz regras do demo que o brief não cita, isso é registrado como contaminação e o recorte é alterado.
- **Aprovada pelo designer (2026-10-05): opção A.** Recorte original com entidades renomeadas e limites e regras alteradas, mais 2 regras próprias do designer (a aprovação aceitou a recomendação).
- **Dupla função do piloto (designer, 2026-10-05):** o mesmo projeto pode também ser a execução do novo fluxo da hipótese (PLAN → IMPLEMENT → REFLECT com o ciclo implementado por este roadmap). Não muda o desenho do piloto; é reaproveitamento como evidência do item 9 do roadmap-000062, citado como opcional sem acoplar os planos.

## Files

- `_output/pilot-default-cycle/README.md` (create) -- índice do piloto, decisões tomadas, hashes
- `_output/pilot-default-cycle/stack-swap.md` (create) -- o passo documentado da troca de stack do scratch
- `_output/pilot-default-cycle/oracle/` (create) -- `requisitos.md`, `*.feature`, testes executáveis do oráculo, `SHA256SUMS` (congelado)
- `_output/pilot-default-cycle/brief.md` (create) -- brief textual único, congelado por hash
- `_output/pilot-default-cycle/runbook.md` (create) -- procedimento de uma execução
- `_output/pilot-default-cycle/runs/<braco>-r<n>/` (create) -- registro, M1/M2, relatório, log de eventos, auditoria
- `_output/pilot-default-cycle/report.md` (create) -- análise e veredito preparado
- `_output/plans/plan-000016-progress.md` (create) -- progress file
- Lidos, não alterados: open-seja (`pilot-run-record.md`, `drift-metric.md`, `drift-control-protocol.md`, `drift_report.py`, tabela do 000015), o template do demo em `.claude/references/template/demo/` (ponto de partida do recorte). Caminhos do open-seja **não verificados nesta sessão** (submodule vazio); o Step 1 os confere.

## Best practices

- "PASS is a tool result, not a sentence" (research-000050): toda medida é calculada sobre arquivos; julgamento semântico fica em coluna à parte.
- Régua independente, escrita e congelada antes (hash), fora do alcance dos agentes dos braços.
- Reportar bruto: numerador, denominador, `n`, `não medido` e as três réplicas; nunca média sozinha.
- Pocock: o humano é o loop externo; o piloto registra onde você precisou intervir e por quê, não só o resultado.
- Registrar o que foi diferente do planejado (desvio de protocolo) no `pilot-run-record.md`; desvio sem registro invalida a execução.
- Voz controlada nos textos que o citizen lê (plano 000074); `/reflect` registra suas palavras verbatim, sem parafrasear.

## Design decisions

- **User-visible impact:** a feature é o TaskFlow em Python; você escreve o que quer dela (o oráculo), e eu a construo seis vezes, três no ciclo antigo e três no novo. Você aceita cada uma na sua vez, sem ver o placar. Depois eu mostro, por degrau, onde a intenção se perdeu em cada ciclo, e você decide o que fazer com H-009.
- **Trade-offs accepted:** ganha-se uma comparação honesta com o mesmo brief e a mesma régua; perde-se poder estatístico (uma feature, um designer experiente, estudo de caso). Custo: seis execuções e uma auditoria humana. O citizen não é testado (Decisão pendente 4).
- **Metacommunication impact:** I know you want evidence, not a good feeling about the new cycle; therefore I will tell you what I could not measure and where the comparison is weak (one feature, one designer, retrofit on the old cycle), and I will not call a result "significant". You decide what H-009 becomes.

## Steps

### Step 1: **[AGENTE]** Conferir pré-condições, tags e baseline
Confirmar, no open-seja, que os planos 000007 a 000015 foram executados: existem `drift-metric.md`, `drift-control-protocol.md`, `pilot-run-record.md`, `drift_report.py` (com `--freeze`, `--moment`, `--compare`), `check_*.py` do ciclo e a tabela "o que este plano entrega ao item 10" no progress do 000015. **Parar e avisar** se algo falta. Conferir também no `/seja-setup --demo` (SKILL e `_internal/seja-setup/demo/SKILL.md`) que ele (a) aceita `--version <tag>` junto com `--demo` e instala a tag anterior, (b) gera o scratch com `conventions.md` editável para trocar a stack; **se não, parar e registrar** (Decisão pendente 2). Ler: o `VERSION` corrente e a tag anterior (os dois braços), o teto de iterações e de tempo do `/implement` (000013), a forma do `audit.json` (000014) e o texto de H-009 e sua condição de refutação no `seja-as-intended.md`. Registrar no progress: tag do braço A, tag do braço B (ou clone local, se ainda não publicada), versão e identificador do modelo em uso, a lista de termos de C1 (`git grep` no repositório de origem) e o baseline do `run_all_checks.py` de um scratch `--demo` recém-gerado em cada tag.
- **Files**: `_output/plans/plan-000016-progress.md` (create), open-seja/.claude/references/general/drift-metric.md (read), open-seja/.claude/references/general/drift-control-protocol.md (read), open-seja/.claude/references/template/pilot-run-record.md (read), open-seja/.claude/skills/scripts/drift_report.py (read)
- **References**: product-design/constitution.md, product-design/conventions.md
- **Interface**: N/A
- **Verify**: o progress lista cada artefato acima como "existe" com caminho, as duas tags (`git tag --list` mostra a anterior; a nova ou o clone local resolvem), o modelo, e o baseline; `git -C open-seja status` limpo; nenhum arquivo do open-seja alterado; resultado do teste de `--demo --version <tag>` registrado (funciona / não funciona).
- **Tests**: N/A (verificação de estado)
- [ ] Done

### Step 2: **[DESIGNER]** Confirmar o TaskFlow em Python contra os critérios F1 a F9 e fixar o recorte
A feature já está decidida (TaskFlow em Python; Decisão pendente 1 fechada). Apresentar a tabela F1 a F9 (acima) e o recorte C-1..T-6, e registrar a confirmação e o recorte final. O agente confere **cada critério com evidência** no template do demo e em um scratch `--demo` de teste: F1 (stack trocada: o que de TypeScript/React precisa mudar nas conventions; testes sem rede), F2 (contagem de regras do recorte >= 8, ou `amostra pequena` declarada; comparar com os 4 REQ markers do demo), F3 (interface proposta), F5 (registrar a limitação: é um demo; a aceitação continua a de `t_aprovada`), F7 (scratch limpo; ressalva de o modelo conhecer o TaskFlow), F8 (nada de segredo nos dados de teste). Se F1, F3 ou F8 falha, volta ao designer. Resolver aqui a Decisão pendente 8 (recorte original). Registrar no `README.md` do piloto: feature, critérios com a evidência, a limitação de F5, a decisão sobre contaminação e os desvios aceitos por você.
- **Files**: `_output/pilot-default-cycle/README.md` (create), `_output/plans/plan-000016-progress.md` (modify), `.claude/references/template/demo/product-design-as-intended.md` (read)
- **References**: product-design/constitution.md (C1, S1)
- **Depends on**: Step 1
- **Interface**: N/A
- **Verify**: `README.md` tem a feature (TaskFlow em Python), F1 a F9 com "atende/não atende + evidência" (F1 "atende só com a stack trocada"; F5 "não atende plenamente: demo"), o recorte final, a escolha da Decisão pendente 8 e a sua confirmação textual (copiada verbatim); F1, F3 e F8 em "atende".
- **Tests**: N/A (decisão e verificação)
- [ ] Done

### Step 3: **[AMBOS]** Escrever o brief único e fixar a interface pública
Redigir `brief.md`, o texto que **os dois braços recebem idêntico** (mesma primeira mensagem ao agente): objetivo da feature em linguagem natural (o recorte, sem listar o oráculo), a **interface pública Python fixada** (critério F3: módulo, funções com assinaturas, dataclasses, formato de entrada e saída, `DomainError` e seus `code`), o ambiente (Python 3.13, `uv`, `pytest`, `pytest-bdd`), o teto de iterações e de tempo por execução (o do 000013 e um teto de relógio, default 4 h), e a regra de que o agente **não** deve ler `_output/pilot-default-cycle/oracle/`. Nada do brief diz qual é o ciclo. Congelar `brief.md` por `sha256sum`.
- **Files**: `_output/pilot-default-cycle/brief.md` (create), `_output/pilot-default-cycle/README.md` (modify)
- **References**: product-design/constitution.md
- **Depends on**: Step 2
- **Interface**: N/A
- **Verify**: `brief.md` contém interface, teto e a regra do oráculo; `sha256sum` registrado no `README.md`; `grep -ci "grill\|gherkin\|cenário\|ciclo"` em `brief.md` devolve zero (o brief não revela o braço).
- **Tests**: N/A (documento)
- [ ] Done

### Step 4: **[DESIGNER]** Escrever o oráculo e congelá-lo antes de qualquer execução
Você escreve `requisitos.md` (REQs observáveis, numerados, no formato de `intent.md` do 000007, sem a pasta de feature; ponto de partida: os REQ markers e o texto do demo, **sem tratá-los como o oráculo**, que é independente e não é mostrado ao braço A) e os cenários Gherkin de aceitação. Em contexto **limpo e separado** dos braços (sessão própria, sem o harness do ciclo novo), o agente escreve os testes executáveis do oráculo (`pytest-bdd`) contra a **interface pública do brief**, um teste por cenário, com a tag do REQ no nome; você revisa. Validar que o oráculo é uma régua útil: (a) roda contra um **stub vazio** que só tem a assinatura da interface e **todos os testes falham pelo motivo certo** (feature ausente, não erro de importação ou de configuração); (b) cada REQ tem ao menos um teste; (c) nenhum teste depende de detalhe interno. **Sonda de contaminação** (Decisão pendente 8): com um agente sem harness e só o `brief.md`, pedir a implementação e conferir se ele reproduz regras do demo que o brief não cita (limites, "General", etc.); registrar no `README.md` e, se houver, ajustar o recorte antes de congelar. Congelar: `SHA256SUMS` de toda a pasta `oracle/`, hash registrado no `README.md` e em cada `pilot-run-record` futuro; commit do oráculo antes de criar qualquer braço.
- **Files**: `_output/pilot-default-cycle/oracle/requisitos.md` (create), `_output/pilot-default-cycle/oracle/*.feature` (create), `_output/pilot-default-cycle/oracle/test_oracle.py` (create), `_output/pilot-default-cycle/oracle/SHA256SUMS` (create), `_output/pilot-default-cycle/README.md` (modify)
- **References**: product-design/standards.md § Testing
- **Depends on**: Step 3
- **Interface**: oráculo executável por `pytest` contra a interface pública do brief; saída por teste usável para calcular O1 (cenários do oráculo que falham no código final).
- **Verify**: `uv run pytest oracle/` contra o stub devolve N falhas = N testes, todas com a mensagem esperada (registrada no progress); `sha256sum -c SHA256SUMS` passa; `git log` mostra o commit do oráculo anterior a qualquer diretório de braço; contagem de REQs registrada (>= 8 ou `amostra pequena`); resultado da sonda de contaminação registrado; `ruff check` limpo no arquivo de teste.
- **Tests**: when o oráculo roda contra o stub vazio, returns todos os testes vermelhos pelo motivo "feature ausente"; when roda contra uma implementação trivial que só devolve o caso mais simples, returns pelo menos metade dos testes ainda vermelhos (a régua não é frouxa).
- [ ] Done

### Step 5: **[AGENTE]** Preparar os seis ambientes, o runbook e a ordem dos braços
Decisão pendente 2 (default A): por execução, gerar um **scratch novo com `/seja-setup --demo`** na **tag do braço** (A: tag anterior pinada; B: tag com o ciclo estendido, ou clone local), fora da árvore do Doutourado, e aplicar o **passo documentado de troca de stack** (`stack-swap.md`: editar as `conventions.md` do scratch de TypeScript + React para Python 3.13 + `uv` + `pytest` + `pytest-bdd` + `ruff` + `pyright`; remover o que é de React; commit-base do scratch). O mesmo `stack-swap.md` vale para os seis. Se o `--demo` não suporta a troca de stack ou a tag anterior, parar e registrar (Step 1). Cada diretório tem memória e histórico de agente próprios (caminhos distintos). Registrar `.seja-version` de cada um e o baseline de `run_all_checks.py` (ruído esperado em projeto novo, backlog do 62; o demo traz design files pré-preenchidos). Negar a leitura do diretório do oráculo em cada ambiente (regra de permissão do agente do braço, não nos hooks já entregues). Ordem: pares de réplica com ordens opostas e registro do que decidiu a ordem (default: R1 A depois B; R2 B depois A; R3 A depois B, ou sorteio com semente registrada). Escrever `runbook.md` (procedimento de **uma** execução, ver abaixo) e abrir seis `pilot-run-record.md` com os campos fixos preenchidos (braço, réplica, ordem, commit-base, versões, hash do oráculo, hash do brief, modelo). Braço B sem `--pipeline` (Decisão pendente 5, default A).
`runbook.md`, por execução: (1) sessão nova do agente no diretório; (2) registrar `t0` ao enviar `brief.md` verbatim; (3) braço A: `/plan` -> `/implement` -> fim; braço B: `/plan` (grill, specify, plano v2) -> `/implement` (que congela M1) -> fim; (4) o designer responde **apenas** o que o oráculo permite (braço B) e só quando perguntado; (5) registrar `t_verde` (primeiro `gate full` PASS); (6) o designer aceita ou rejeita **sem ver O1** (Decisão pendente 6 = A) e `t_aprovada` é registrado; (7) cada intervenção do designer vira uma linha no log de eventos (hora, o que disse, motivo); (8) ao fim, copiar o oráculo para a execução, rodar O1, rodar `drift_report.py` (M1 já congelado no braço B; no A, retrofit conforme 000008), copiar `runs/<braco>-r<n>/`; (9) **desvio do protocolo** é escrito no registro na hora.
- **Files**: `_output/pilot-default-cycle/runbook.md` (create), `_output/pilot-default-cycle/runs/*/pilot-run-record.md` (create), `_output/pilot-default-cycle/README.md` (modify)
- **References**: product-design/constitution.md (T2, S1, C1)
- **Depends on**: Step 4
- **Interface**: estrutura `runs/{A,B}-r{1,2,3}/` com `pilot-run-record.md`, `eventos.log`, e saídas do `drift_report.py` por momento.
- **Verify**: seis diretórios existem; o `stack-swap.md` foi aplicado igualmente nos seis (as `conventions.md` dos scratches são idênticas entre si; entre braços só diferem `.seja-version` e o harness); `cat .seja-version` dos braços A bate com a tag anterior e dos B com a nova; nenhum diretório de braço contém uma cópia do oráculo; a regra de negação do caminho do oráculo está presente em cada ambiente; ordem registrada; seis registros com hashes do oráculo e do brief iguais; `git status` do Doutourado sem alterações fora de `_output/pilot-default-cycle/` e do progress.
- **Tests**: N/A (preparação; as verificações são de configuração)
- [ ] Done

### Step 6: **[DESIGNER]** Executar a réplica 1 (A e B na ordem sorteada)
Seguir o `runbook.md` nas duas execuções da réplica 1. O agente conduz; **você** responde a grill (braço B), aprova o plano e a fase specify, e dá a aceitação final de cada execução. Entre as duas execuções, não consultar nem copiar nada da outra (inclusive o código). Ao fim de cada uma: `pilot-run-record.md` completo (timestamps, iterações até PASS, nº de perguntas da grill, linhas de código, nº de REQs, desvios), sua observação livre **verbatim** e o atrito do citizen/designer (Decisão pendente 4): pontos de dúvida, vontade de pular um degrau, o que pareceu lento. Uma execução que estourou o teto de iterações ou de tempo é registrada como **não concluída**, nunca descartada.
- **Files**: `_output/pilot-default-cycle/runs/{A,B}-r1/` (modify), `_output/plans/plan-000016-progress.md` (modify)
- **References**: `_output/pilot-default-cycle/runbook.md`
- **Depends on**: Step 5
- **Interface**: N/A
- **Verify**: os dois registros da réplica 1 têm `t0`, `t_verde` (ou "não atingido"), `t_aprovada` (ou "não aprovada"), log de eventos, saída do `drift_report.py` (M1 no B), e a observação do designer; o brief enviado tem o mesmo `sha256sum` nos dois; nenhuma linha do log de eventos cita o oráculo; o Doutourado não mudou fora de `_output/pilot-default-cycle/` (`git status`).
- **Tests**: N/A (execução humana)
- [ ] Done

### Step 7: **[DESIGNER]** Executar a réplica 2 (ordem oposta à da 1)
Idem Step 6, com a ordem invertida. Antes de começar, o agente relê o progress para confirmar que nenhum resultado da réplica 1 vai para o contexto das execuções (sessões novas, diretórios novos).
- **Files**: `_output/pilot-default-cycle/runs/{A,B}-r2/` (modify), `_output/plans/plan-000016-progress.md` (modify)
- **References**: `_output/pilot-default-cycle/runbook.md`
- **Depends on**: Step 6
- **Interface**: N/A
- **Verify**: os mesmos critérios do Step 6; a ordem da réplica 2 é oposta à da 1; `grep` do identificador da execução anterior nos logs de eventos desta devolve zero.
- **Tests**: N/A (execução humana)
- [ ] Done

### Step 8: **[DESIGNER]** Executar a réplica 3 (ordem oposta à da 2)
Idem Step 7. Ao fim, **conferir o protocolo inteiro**: os seis registros têm a mesma versão de modelo (ou a troca está registrada como desvio), os mesmos hashes e os mesmos tetos; se uma execução está inválida por desvio grave (por exemplo, o agente leu o oráculo), marcar `invalida` com o motivo e decidir com você: repetir essa execução ou seguir com `n` menor, **declarando**.
- **Files**: `_output/pilot-default-cycle/runs/{A,B}-r3/` (modify), `_output/plans/plan-000016-progress.md` (modify)
- **References**: `_output/pilot-default-cycle/runbook.md`
- **Depends on**: Step 7
- **Interface**: N/A
- **Verify**: seis registros completos (ou marcados `não concluída`/`invalida` com motivo e decisão sua verbatim); tabela de conferência de protocolo no progress com modelo, hashes, tetos e desvios por execução.
- **Tests**: N/A (execução humana)
- [ ] Done

### Step 9: **[AMBOS]** Coletar as medidas: D1, D2, D3a, D3b, O1, tempo e a auditoria cega
(a) **[AGENTE]** Para cada execução: `drift_report.py` em M1 e M2 (D1, D2, D3a, D3b, com `n`, cobertos, descobertos, `não medido`); O1 = cenários do oráculo que falham no código final (copiar o oráculo para a execução, rodar, descartar a cópia); `t_verde`, `t_aprovada`, tempo de relógio e **tempo atendido** (regra de 10 min do 000008) calculados dos eventos. No braço A, D1 e D2 por **retrofit** (mapear os REQs do oráculo aos critérios do plano v1 e aos testes do A), declarado como assimetria. (b) **[AGENTE]** Gerar o pacote de auditoria **cego**: para cada REQ da amostra (todos os do A; B com amostra determinística de ao menos 30%, semente registrada), um par REQ + cenário/teste correspondente, com identificadores embaralhados e **sem o rótulo do braço**; sem ordem que revele o braço. (c) **[DESIGNER]** Julga cada par: `adequado: sim/parcial/não`, no `audit.json` do 000014, com o campo `por` = designer. O agente só desfaz o embaralhamento **depois** de todas as notas. (d) Registrar o atrito (Decisão pendente 4): contagem de perguntas da grill, intervenções fora do roteiro, citações verbatim. Nada é calculado por LLM; o cálculo é do `drift_report.py`.
- **Files**: `_output/pilot-default-cycle/runs/*/` (modify), `_output/pilot-default-cycle/audit/` (create: pacote cego, notas, chave de desembaralhamento), `_output/pilot-default-cycle/report.md` (create)
- **References**: open-seja `drift-metric.md`, `drift-control-protocol.md`
- **Depends on**: Step 8
- **Interface**: tabela de resultados por execução (braço, réplica, D1, D2, D3a, D3b com `n` e `não medido`, O1, `t_verde`, `t_aprovada`, tempo atendido, adequação semântica).
- **Verify**: para cada execução existente há uma linha com os seis números ou "não medido + motivo"; recontagem independente de pelo menos duas execuções (contagem manual de cobertos/descobertos num caso do A e num do B bate com o relatório); `audit.json` cobre 100% dos REQs do A e >= 30% dos do B; a chave de desembaralhamento tem data **posterior** às notas; nenhum denominador zero aparece como 0 (aparece "n/a").
- **Tests**: when o `drift_report.py` é rodado duas vezes sobre o mesmo M1 congelado, returns relatório idêntico (mesmo hash); when uma execução não tem `gate.json`, returns D3a e D3b `não medido` com D "n/a".
- [ ] Done

### Step 10: **[AGENTE]** Analisar segundo a regra `D_B >= D_A` e classificar o resultado
Montar em `report.md`: (1) tabela por degrau e por réplica pareada (A_r vs B_r), com numerador e denominador, `não medido` ao lado, O1 e tempo; (2) a **regra de comparação**: por degrau, "redução" quando `D_B < D_A` com diferença >= 1 item do denominador; `empate` quando < 1 item; `sem redução` quando `D_B >= D_A`; D3 pela Decisão pendente 3 (default A); D1 e D2 marcados como "por retrofit" (assimetria); (3) as **três cláusulas de refutação** de H-009 (000007, Step 6): (i) `D_B >= D_A` em ao menos dois dos três degraus; (ii) D3 só cai porque o gate foi o único filtro: B tem D3 menor **e** O1_B >= O1_A **e** adequação semântica do B não melhor que a do A; (iii) o tempo até a primeira feature aprovada (`t_aprovada`, atendido e de relógio) aumenta no B **sem** queda em nenhum degrau; (4) a **classificação** (tabela abaixo); (5) ameaças e o que **não** se conclui (uma feature; um designer experiente; retrofit no A; oráculo do mesmo designer; amostra pequena se aplicável; modelo não determinístico); (6) o que ficou `não medido` e por quê.
| Resultado | Condição | O que fazer |
|---|---|---|
| **Consistente com H-009** | Redução em ao menos 2 dos 3 degraus (maioria das réplicas pareadas), nenhuma das três cláusulas de refutação, O1_B <= O1_A | Manter o default; propor 2ª feature de natureza diferente e a execução com citizen (Decisão pendente 4, B) antes de generalizar; ajustar limiares do `/implement` com os dados |
| **Refutada** | Qualquer cláusula de refutação verdadeira | **Não** retirar o ciclo por reflexo: você decide entre manter o default com ajuste do degrau culpado, torná-lo opt-in (`--grill`/`--specify` sem ser default) ou voltar ao ciclo anterior; abrir plano de ajuste com o degrau onde a intenção se perde |
| **Inconclusiva** | Redução em só 1 degrau, ou diferenças só nos degraus por retrofit, ou execuções inválidas demais, ou empates dominantes | Registrar como estudo de caso sem veredito; executar uma 2ª feature (outros critérios F1 a F9) antes de decidir |
- **Files**: `_output/pilot-default-cycle/report.md` (modify), `_output/plans/plan-000016-progress.md` (modify)
- **References**: `_output/plans/plan-000008-drift-metric.md`, `_output/plans/plan-000007-default-cycle-contract.md`
- **Depends on**: Step 9
- **Interface**: N/A
- **Verify**: `report.md` tem as seis seções; cada afirmação cita uma célula da tabela; nenhuma ocorrência de "significativo" ou p-valor (`grep -ci "significativ\|p-valor\|p <"` devolve zero); a classificação aponta a condição que a dispara; os números do relatório batem com os de `runs/` em uma conferência por amostragem (3 células).
- **Tests**: N/A (análise documental)
- [ ] Done

### Step 11: **[DESIGNER]** `/reflect` ancorado nos artefatos
Rodar `/reflect` com âncoras: `report.md`, os seis `pilot-run-record.md` e os planos 000008 e 000015. O `/reflect` resume os artefatos, pergunta se você reflete sobre o **produto** (o que foi construído) ou sobre a **prática** (como você trabalhou) e registra **suas palavras verbatim**; o agente não parafraseia nem completa a resposta. Se você reflete sobre os dois, rodar duas vezes. Se a feature rodou o `/reflect` do ciclo novo (relatório por degrau do 000014), ele lê a matriz do braço B. O atrito do citizen/designer (Step 9d) entra como âncora.
- **Files**: `_output/plans/plan-000016-progress.md` (modify), `_output/plans/plan-000016-default-cycle-pilot.md` (modify, seção `## Reflection` anexada pelo post-skill), `_output/pilot-default-cycle/README.md` (modify)
- **References**: .claude/skills/reflect/SKILL.md
- **Depends on**: Step 10
- **Interface**: N/A
- **Verify**: a seção de reflexão contém suas palavras entre aspas, sem edição (diff textual contra a transcrição); registra se foi produto ou prática; as âncoras estão listadas.
- **Tests**: N/A (reflexão)
- [ ] Done

### Step 12: **[DESIGNER]** Fechar: decisão sobre H-009, achados e destino do código
(1) Apresentar a classificação do Step 10 e as suas palavras do Step 11; **você decide** o que acontece com H-009 e com o default. O agente prepara o texto da atualização do status de H-009 e, se for o caso, de uma nova D-NNN, como proposta de prosa para você colar (`/implement --manual`); marcadores só via `apply_marker.py` com a sua confirmação. (2) Listar os **achados do harness** vistos nas seis execuções (fricção, bugs, mensagens confusas, ruído do `run_all_checks`, casos de D9) como itens de backlog, cada um com a execução de origem; **não corrigir aqui**. (3) Destino do código (Decisão pendente 7): nada é aplicado neste plano. (4) Conferir C1 (`git grep -i` dos termos do Step 1 sobre `_output/pilot-default-cycle/` e o diff), que o oráculo e os braços não contêm segredo, e que `run_all_checks.py` do Doutourado mantém o baseline. (5) Commit local dos artefatos; sem push. (6) Registrar no progress as pendências que ainda estão no default e a atualização que o orquestrador deve fazer no roadmap (status do item 10), sem editá-lo.
- **Files**: `_output/pilot-default-cycle/report.md` (modify), `_output/plans/plan-000016-progress.md` (modify), `_output/pilot-default-cycle/README.md` (modify)
- **References**: product-design/product-design-as-intended.md (somente leitura), product-design/constitution.md
- **Depends on**: Step 11
- **Interface**: N/A
- **Verify**: o progress tem a decisão sua sobre H-009 verbatim, o texto proposto, a lista de achados com origem, e as pendências; `git grep -i` dos termos de C1 devolve zero; `git status` limpo depois do commit; `product-design/` e o roadmap não foram alterados por este plano.
- **Tests**: N/A (fechamento)
- [ ] Done

## Coverage (advisory)

`product-design/product-design-as-intended.md` do Doutourado não tem marcadores REQ; `critique_plan_coverage.py` não se aplica e `Traces:` fica ausente. Os REQ markers do TaskFlow (demo do open-seja) são do projeto-piloto, não do Doutourado, e ficam fora desta cobertura.

## Riscos

| Risco | Efeito | Mitigação |
|---|---|---|
| **n pequeno** (1 feature, 3 réplicas, 1 designer) | Nenhuma generalização; ruído domina | Estudo de caso declarado; relatar as três réplicas; `amostra pequena` se < 8 REQs; sem p-valor; 2ª feature como follow-up |
| **Contaminação entre braços** (memória do agente, designer que aprende, oráculo lido) | Diferença que não vem do ciclo | Sessões e diretórios novos por execução; ordem alternada em pares; oráculo congelado por hash, fora das árvores e com leitura negada; conferência de logs por menção ao oráculo (Steps 5 a 8) |
| **LLM não determinístico** (mesmo brief, resultados diferentes; troca de versão do modelo no meio) | Variância confundida com efeito | Três réplicas; modelo registrado por execução; troca de modelo = desvio registrado |
| **Assimetria do retrofit** (D1 e D2 do braço A só por mapeamento) | Comparação de D1/D2 menos firme | Declarada; peso maior em D3a, D3b e O1 (diretos); auditoria cega |
| **Oráculo e respostas da grill do mesmo designer** | Viés a favor do braço B | Designer responde a grill só a partir do oráculo; aceitação antes de ver O1; auditoria cega |
| **Fricção do citizen não medida** (designer é experiente) | Risco central do roadmap fica sem resposta | Declarado; atrito registrado como qualitativo; follow-up B (Decisão pendente 4) |
| **Goodhart** (cenários fracos fecham a escada sem capturar a intenção) | D baixo sem qualidade | O1 e auditoria semântica à parte; leitura "escada fechou sem capturar a intenção" (000008) |
| **Ruído de ambiente** (D9: smoke só Flask; `run_all_checks` ruidoso em projeto novo) | Falso vermelho atribuído ao ciclo | Feature Python puro (F1); baseline do `run_all_checks` por braço antes de começar; achados vão ao backlog, não ao placar |
| **Hook `Stop` barrando entre RED e GREEN** (000013, lacuna 9; 000015, Decisão pendente 7) | Parece lentidão do ciclo novo | Contar barramentos no log de eventos e reportar ao lado do tempo; não editar hooks aqui |
| **Demo conhecido pelo modelo** (o TaskFlow é difundido; o modelo pode reproduzi-lo de memória) | Diferença entre braços encolhe; o oráculo mede memória, não a escada | Decisão pendente 8 (recorte original + regras próprias); sonda de contaminação no Step 4; declarado como ameaça no relatório |
| **F5 não atendido** (é um demo; aceitação sem desejo real) | `t_aprovada` e o atrito representam menos do que representariam numa feature desejada | Limitação registrada; a aceitação continua a de `t_aprovada`; ameaça no Step 10 |
| **Troca de stack no scratch** (TypeScript + React -> Python) | Resíduo de React ou convenções incoerentes enviesam um braço | Passo único e documentado (`stack-swap.md`), igual nos seis; conferido no Step 5 |
| **Custo** (6 execuções + auditoria humana) | Piloto abandonado | Teto de tempo e de iterações por execução; execução não concluída conta como dado |

## Lacunas e conflitos com os planos 000007 a 000015

1. **Pré-condição.** O roadmap diz "Depends on: default-cycle-wiring", mas os planos 76 a 84 estão só escritos. O Step 1 trata isso como parada, não como suposição. Também depende de o open-seja ter uma tag nova (ou clone local) para o braço B; o 000015 prepara a versão e **não publica**.
2. **"Dois dos três degraus" (000007) x D3a/D3b (000008).** O 000008 dividiu o degrau teste→código sem dizer como D3 entra na contagem da refutação. Resolvido por Decisão pendente 3 (default A); a frase deve ir para a prosa de H-009 pelo designer.
3. **Réplicas pareadas.** O 000008 manda "relatar as três, nunca a média sozinha" e fixa a regra `D_B >= D_A`, mas não diz como agregar três pares. Este plano usa maioria de réplicas pareadas (2 de 3); o designer pode mudar (Decisão pendente 3).
4. **Quem vê O1 antes de aceitar.** 000008 (Decisão pendente 3) fixa "aceitação explícita do designer, com `t_verde` e O1 ao lado", sem dizer se a aceitação é anterior ao O1. Fechado aqui por Decisão pendente 6 (default A).
5. **Interface comum.** O 000008 exige um oráculo comparável, mas não exige que o brief fixe a interface pública. Sem isso, O1 não roda nos dois braços. Entra como critério F3 e Step 3.
6. **Instalação por braço.** O 000015 prova upgrade por tag em projetos de fixture e cita o braço de controle com "tag anterior pinada"; não descreve instalar o harness num diretório novo por execução. O Step 5 usa o caminho do `/seja-setup`; se o instalador não suportar a tag anterior fora de um upgrade, parar e registrar (Step 1).
7. **Quem é o designer.** O roadmap cita citizen; o piloto tem um designer experiente. Declarado (Decisão pendente 4).
8. **Nome do campo e do arquivo de tempo.** `t_aprovada` depende de uma fonte que o 000008 deixou "campo manual" se não existir; o piloto usa o campo do registro (e o log de eventos do runbook) como fonte única.
9. **Stack do demo.** O demo de fábrica é TypeScript + React; a troca para Python é manual (conventions do scratch). Se o `--demo` não aceitar `--version <tag>` ou a troca de stack, o Step 1 para. O open-seja não foi lido nesta sessão (submodule vazio); só o template do demo em `.claude/references/template/demo/`.
10. **REQ markers do demo.** Apenas 4, 2 de UI; o recorte de 10 regras e o oráculo são do designer. Pontos omissos no demo (deleção de Category com Tasks, formato de `color`, renomear "General") são fixados pelo oráculo.
11. **Item 9 do roadmap-000062.** O TaskFlow pode servir de evidência a `hypothesis-first-run` em `seja-demo-taskflow`; reaproveitamento opcional, sem acoplar os planos.

## Metacomm Intention
- **Summary**: I tell you that I will build the same feature of your choosing with the old cycle and with the new one, three times each, and show you, step by step, where your intent got lost in each, with what I could not measure, without calling the result "significant"; and that you decide what happens with H-009.
- **Source**: agent (technical plan; metacomm text kept for the report to the designer)

## Review log

**Review depth:** Standard (12 steps, ~8 arquivos distintos nos Files). Phase 1 inline (sem subagente; mesmo critério dos planos 000007 a 000015); sem Phase 2 (nenhum Deferred com risco de regressão). Prefixo FEATURE-O: usei DX, TEST, DATA, COMPAT, SEC, OPS.

### Step metadata validation
- Todos os 12 steps têm Files, References, Interface, Verify, Tests e checkbox; `Interface: N/A` quando não há consumidor; Tests em steps de execução/documento = N/A justificado (o único com comportamento testável são os Steps 4 e 9, com forma "when X, returns Y").
- Dependências fluem para frente (1 -> 12, linear). Nenhum step passa de 5 arquivos distintos (Steps 4 e 9 usam diretórios).
- Caminhos do open-seja **não verificados** (submodule vazio): Step 1 é o portão. Template do demo (`.claude/references/template/demo/`) verificado em disco: 4 REQ markers, entidades Category e Task, limites do §10.
- Marcação **[DESIGNER]/[AGENTE]/[AMBOS]** em todo step; os que não andam sem você: 2, 3, 4, 6, 7, 8, 9 (c), 11, 12.

### Phase 1 -- Perspective scan

| Perspective | Status | Concern |
|---|---|---|
| DX | Adopted | Runbook de uma execução; cada step com Verify por comando ou conferência; papéis explícitos. |
| TEST | Adopted | Oráculo validado contra stub e contra implementação trivial antes de congelar; recontagem independente de duas execuções; relatório reproduzível por hash. |
| DATA | Adopted | `não medido` e denominador zero ("n/a") visíveis; brutos; três réplicas; sem número único, sem p-valor. |
| COMPAT | Adopted | Nada altera open-seja, hooks, roadmap, INDEX ou `product-design/`; braço A na tag anterior pinada. |
| SEC | Adopted | C1 por `git grep` (Steps 1, 12); sem segredo em dados de teste (F8); oráculo com leitura negada nos braços. |
| OPS | Adopted | Ambientes isolados fora da árvore do Doutourado; teto de tempo e de iterações; execução inválida registrada, nunca descartada. |
| ARCH, PERF, DB, API, I18N, UX, A11Y, VIS, RESP, MICRO | N/A | Plano de medição; sem superfície nova. |

### Riscos e lacunas registrados
- Caminhos do open-seja e flags reais de `drift_report.py` por confirmar no Step 1.
- Feature fechada (TaskFlow em Python); F1 depende da troca de stack e F5 não é atendido plenamente (declarado). Contaminação por demo conhecido: Decisão pendente 8.
- Uma feature, um designer experiente: evidência de caso.

### Execution Metrics
| Metric | Value |
|---|---|
| Review depth | Standard |
| Phase 1 perspectives | 6 adopted, 10 N/A |
| Phase 2 deep-dives | 0 |
| Iterations | 0 |
| Pending decisions | 7 abertas (2 A, 3 A, 4 A, 5 A, 6 A, 7 C, 8 A); a 1 está fechada (TaskFlow em Python) |

## Outcomes

- Feature-piloto TaskFlow em Python confirmada contra F1 a F9 (F1 condicionado à troca de stack; F5 declarado como limitação), com oráculo independente congelado por hash e brief único.
- Seis execuções (3 por braço, ordem alternada) com registro de eventos, tempos (`t0`, `t_verde`, `t_aprovada`, atendido) e atrito.
- D1, D2, D3a, D3b e O1 por execução, auditoria semântica cega, e relatório de análise sem p-valor com classificação (consistente, refutada, inconclusiva) e ação para cada caso.
- `/reflect` com suas palavras verbatim e a sua decisão sobre H-009; lista de achados do harness para o backlog.

smoke: false
