# Plan 000011 | FEATURE-O | 2026-10-05 12:17 UTC | plan-specify-phase: fase specify do /plan (intenção aprovada vira .feature validado e aprovado pelo citizen) | Review: standard

> **Origem**: movido do ledger do Doutourado em 2026-10-05 (proposal-000088; la era `plan-000080`). Os IDs roadmap-000006 e plan-000007..000016 sao deste ledger (tabela no roadmap). Referencias a research-NNNNNN, reflection-NNNNNN, communication-NNNNNN, roadmap-000062 e plan-000064..000074 apontam para o ledger do Doutourado (repositorio do pesquisador). Caminhos `open-seja/...` em Files passam a ser relativos a raiz deste repositorio.
plan_format_version: 1

> Item 5 do roadmap-000006 (Wave 2; Depends on: plan-grill-phase = plan-000009, gherkin-spec-format = plan-000010). Repositório de execução: **open-seja** (worktree/branch por plano); o plano vive no Doutourado. C1: nenhum nome de parceiro nos artefatos que forem ao open-seja. ID alocado pelo orquestrador (não usa `reserve_id.py`). É `plan_format_version: 1` porque o formato v2 só existe depois que o plano 000007 executar. Usa o vocabulário dos planos 000007 (`CYC-NNN`, `features/<slug>/`, `plan_format_version: 2`, `Specify: skipped -- <motivo>`), 000008 (D1 e D2; `não medido` quando `.feature` não aprovado), 000009 (`intent.md`, `check_intent.py --require-approved`, REQs `comportamento`/`restrição`, slug confirmado, `rev`, `retirado`) e 000010 (`check_features.py`, `GHK-001..016`, `scenarios: approved`, Outline = um cenário, `# language:`, chave `<slug>/<arquivo>::<nome>`). Não reabre nenhuma decisão fechada daqueles planos.

## User brief

> Item 5 do roadmap-000006: `plan-specify-phase` (Depends on: plan-grill-phase, gherkin-spec-format). "Fase specify do /plan: intenção detalhada vira .feature validado; ponto de aprovação humana (o citizen valida aqui)."

## Agent interpretation

**Problem.** O 000007 diz que, depois da grill, o `/plan` escreve cenários e pede aprovação antes do plano. O 000010 entrega a convenção e o validador do `.feature`. O 000009 entrega o `intent.md` aprovado. Falta a fase que liga os três: **como** um REQ vira cenário, **em que voz** o cenário é escrito para o citizen aprovar, **o que fazer** com REQ de tipo `restrição`, **como** a aprovação é gravada de forma que o D1 do 000008 possa confiar nela, **o que acontece** quando o citizen pede ajuste, quando a intenção muda depois, ou quando não há código. Sem isso o degrau intenção→cenário (D1) mede cenário rascunho como se fosse aprovado, e os itens 6 (plano por cenários) e 7 (teste vermelho por cenário) não têm entrada confiável.

**Approach.** Plano **técnico** com um núcleo de design, no mesmo molde do 000009. Produz no open-seja: (a) a referência normativa `specify-phase.md` (regras `SPC-NNN`: entrada, derivação REQ→cenário, restrição, voz, validação, aprovação, ajuste, degradação); (b) um verificador **determinístico** `check_specify.py` (sem LLM, biblioteca padrão) que confere o portão de entrada, a cobertura REQ→cenário, o caso `restrição`, a voz dos steps, chama o `check_features.py` do 000010 em `--strict` e, só quando tudo passa, grava a aprovação (`--approve`); (c) o texto da fase em `_internal/plan/standard/SKILL.md` e a flag `--specify` em `plan/SKILL.md`; (d) fixtures golden (escritas antes) e três execuções de referência. O LLM escreve os cenários e conduz a conversa; as máquinas só conferem e registram, no estilo "PASS is a tool result, not a sentence" (research-000050). Não implementa o formato do plano v2 (item 6), o runner (item 7) nem o relatório (item 8).

**Alternatives rejected.**
- Deixar o validador do 000010 ser o único portão: ele acusa estrutura, rastreabilidade e steps, mas não sabe se o `.feature` foi aprovado nem se os cenários ainda correspondem à versão aprovada dos REQs; nada grava a aprovação. Rejeitado: `check_specify.py` fica **por cima** do `check_features.py`, não o duplica.
- O agente gravar `scenarios: approved` à mão no frontmatter: depende de o LLM não errar o campo e não o grava depois de falha de validação. Rejeitado: só `check_specify.py --approve` escreve, e só com tudo verde.
- Gerar os cenários por template determinístico a partir do critério "Quando A, o sistema B": cobre o caso feliz, mas não pré-condições, erros e limites; mais código para manter. Rejeitado como default (Decisão pendente 4); o validador já garante que nenhum REQ fica sem cenário.
- Pedir aprovação de cada cenário isoladamente: fricção alta para o citizen (risco do roadmap). Rejeitado: uma aprovação sobre o conjunto, agrupado por requisito, com o ajuste por requisito.
- Mostrar o `.feature` cru ao citizen: o Gherkin pt é quase linguagem natural, mas marcações (`@REQ-...`, `Examples` em tabela) são ruído. Rejeitado: a apresentação é um resumo por requisito; o arquivo é o mesmo texto, sem tradução intermediária (o que o citizen aprova é o que vai para o teste).

**Selection rationale.** Sem `source:`. Fontes: roadmap-000006 (item 5, risco "Gherkin mal escrito vira ruído"), planos 000007 a 000010, roadmap-000062 (item 11, voz controlada, plano 000074), research-000050 (Specifier; Gherkin como critério de aceitação) e `product-design/constitution.md` (Q2: git é a recuperação; nada de soft-delete).

### Decisões fechadas (aprovadas pelo designer; não reabrir)
1. Grill e specify são fases internas do `/plan`, também invocáveis avulsas (`/plan --specify`).
2. Specify é pulada **por tipo de tarefa** (sem step com `Tests:` não-N/A), com a linha `Specify: skipped -- <motivo>` no plano. A grill nunca é pulada.
3. Layout `features/<slug>/{intent.md,*.feature,gate.json}`; `plan_format_version: 2`; teste-primeiro no `/implement`.
4. Mesmo caminho para citizen e power dev; o power dev pode ter acrescentado REQs `restrição` na grill. Muda quem olha cada degrau, não a fase.
5. Recomendações dos planos 000009 e 000010 adotadas: REQ com tipo `comportamento`/`restrição` (`restrição` também ganha cenário); slug confirmado na grill; `Outline` = um cenário; `# language:` en/pt declarado no arquivo (pt como padrão dos exemplos); tag `@REQ-` em cada cenário e proibida em `Feature`/`Rule`; chave do cenário `<slug>/<arquivo>::<nome>`; o validador só **lê** `scenarios: approved`, quem **escreve** é este item.
6. Voz controlada (plano 000074) em tudo que o agente escreve para o citizen: aqui, os steps dos cenários, o resumo e as perguntas. Fora da regra: citação verbatim do citizen, código, tabelas.

### Regras da fase (resumo; o texto normativo é o Step 2)

| Regra | Conteúdo | Quem confere |
|---|---|---|
| SPC-001 | **Entrada.** `features/<slug>/intent.md` com `status: approved` e `check_intent.py --require-approved --strict` saindo 0. Caso contrário a fase **recusa** e oferece voltar à grill. | `check_specify.py` |
| SPC-002 | **Quando roda.** Roda se a grill classificou a tarefa "com código" (existe `features/<slug>/`). Tarefa sem código: não cria pasta e escreve `Specify: skipped -- <motivo>`. | fase (texto) |
| SPC-003 | **Derivação.** Todo REQ `ativo` ganha >= 1 cenário com `@REQ-<slug>-NNN`; REQ `retirado` não tem cenário. Critério "Quando A, o sistema B" vira `Quando A` e `Então B`; `Dado` vem das dimensões "quem" e "gatilho" do `intent.md`. | `check_specify.py` + `GHK-002/004/005` |
| SPC-004 | **Restrição.** REQ `restrição` vira cenário como os demais, com **valor numérico** no `Então` ou nas linhas de `Examples` (limite, tempo, tamanho). Se o critério não admite número ou observação, a fase **volta à grill** (o critério falha P2), não inventa cenário. | `check_specify.py` |
| SPC-005 | **Erros e limites.** Cada caso de erro/limite da dimensão `erros_limites` que a grill ligou a um REQ ganha cenário próprio. Caso sem REQ: a fase **pergunta** se vira REQ (volta à grill) ou fica fora; nunca cria cenário sem REQ. | fase (texto) + `GHK-002` |
| SPC-006 | **"Não faz".** Itens de "Fora do escopo" não geram cenário. Aparecem no resumo de aprovação, para o citizen ver o que ficou fora. | fase (texto) |
| SPC-007 | **Voz.** Cada step <= `MAX_SENTENCE_WORDS` (25) palavras, uma ideia por step, presente, papel nomeado como na dimensão "quem", sem detalhe técnico (avisos de `GHK-013` viram bloqueio na entrega, porque o gate é `--strict`). | `check_specify.py` + `GHK-013` |
| SPC-008 | **Validação.** `check_features.py --strict --feature <slug>` sai 0 (sem erro e sem aviso) e `scenarios` não contém tag de desativação (`GHK-014`). | `check_specify.py` |
| SPC-009 | **Aprovação humana.** Resumo por requisito; o citizen escolhe **Aprovar / Ajustar / Voltar à entrevista / Descartar** (AskUserQuestion, C4). Só **Aprovar** leva a SPC-010. | fase (texto) |
| SPC-010 | **Registro.** `check_specify.py --approve --at <UTC> --by usuario` escreve no `intent.md` `scenarios: approved`, `scenarios_approved_at`, `scenarios_approved_by`, `scenarios_rev`, e grava `features/<slug>/scenarios.lock.json` (versão de cada REQ, chaves de cenário, hash dos `.feature`). Falha em qualquer regra: não escreve nada. | `check_specify.py` |
| SPC-011 | **Ajuste.** Rodadas de ajuste (teto `SPECIFY_MAX_ROUNDS = 3`); cada rodada sobe `scenarios_rev` e entra em "Mudanças" do `intent.md`. Pedido que muda *o que* se quer (não *como se descreve*) volta à grill. | fase (texto) + `check_specify.py` |
| SPC-012 | **Nomes estáveis.** Cenário aprovado não muda de nome nem some sem linha em "Mudanças"; a chave é a ligação com o D2 e o relatório. | `check_specify.py` (contra o lock) |
| SPC-013 | **Cenários desatualizados.** `scenarios: approved` só vale se o lock bate: mesmos REQs `ativo` com o mesmo `rev`, mesmo hash dos `.feature`. Senão o estado é `stale` e o D1 deve tratá-lo como `não medido`. | `check_specify.py --status` |
| SPC-014 | **Degradação.** Plano v1 / projeto sem `features/` / open-seja antigo: a fase não existe. Sem `check_features.py`: a fase **não aprova** (não há validador) e diz o motivo. | fase (texto) |
| SPC-015 | **Não faz.** Não escreve o plano nem o campo `Scenarios:` (item 6), não liga runner (item 7), não calcula D (itens 2 e 8), não altera `intent.md` além dos campos `scenarios_*` e da linha em "Mudanças". | revisão do diff |
| SPC-016 | **Avulsa.** `/plan --specify [<slug>]`: lê `intent.md` aprovado, escreve só `*.feature`, o lock e os campos `scenarios_*`; nunca escreve plano. Reentrada permitida. | fase (texto) |

### Fluxo da fase (visão do citizen)
1. A grill termina com `intent.md` aprovado. Eu escrevo os cenários, um grupo por requisito, em frases curtas.
2. Eu mesmo rodo as conferências. Se algo falha, corrijo antes de mostrar; você não vê cenário com defeito mecânico.
3. Eu mostro, por requisito: o requisito, os cenários (o texto do arquivo) e a lista "o que não faz". Você escolhe aprovar, ajustar, voltar à entrevista ou descartar.
4. Só depois de "aprovar" eu registro a aprovação. Mudou a intenção depois? Os cenários viram `stale` e eu peço nova aprovação.

### Decisões pendentes
Cada uma tem default (a recomendação). Se o designer não responder, os steps seguem o default; mudar uma altera só o Step indicado.

**Decisão pendente 1 -- Onde fica a prova de que os cenários aprovados são os mesmos de agora** (afeta Steps 2, 4; lacuna com o 000010, Decisão pendente 5)
O 000010 lê só `scenarios: approved` do frontmatter; isso não impede que um `.feature` seja editado depois da aprovação, nem que um REQ suba de `rev`.
- Opção A: arquivo ao lado, `features/<slug>/scenarios.lock.json` (versão de cada REQ, chaves de cenário, hash dos `.feature`), mais o campo plano `scenarios: approved` no frontmatter.
- Opção B: tudo no `intent.md` (tabela "Cenários aprovados" no corpo).
- Opção C: só o campo no frontmatter (como no 000010), sem prova de conteúdo.
- **Recomendação: A.** Recommended when o D1 do 000008 precisa distinguir cenário rascunho/desatualizado de aprovado sem confiar na memória do agente, e o arquivo novo não colide com o parser do 000010 (que só lê `*.feature` e linhas de tabela do `intent.md`). NOT recommended when o designer não quer um arquivo a mais por feature (então C, e registrar que `stale` não é detectável). B rejeitada: uma tabela com `REQ-...` na primeira célula seria lida como REQ duplicado por `check_features.py` (000010) e por `check_intent.py` (000009, P4). O arquivo extra é uma emenda **aditiva** ao layout do 000007 (lacuna 2 abaixo).

**Decisão pendente 2 -- Teto de rodadas de ajuste** (afeta Steps 2, 4, 6)
- Opção A: sem teto.
- Opção B: 3 rodadas (`SPECIFY_MAX_ROUNDS = 3`); ao atingir, devolve a decisão ao citizen: aprovar como está, voltar à entrevista ou arquivar.
- Opção C: 5 rodadas.
- **Recomendação: B.** Recommended when o roadmap lista fricção do citizen como risco e o piloto (item 10) mede o tempo até a primeira feature aprovada; ajuste repetido costuma indicar REQ vago, que se resolve na grill. NOT recommended when o piloto mostrar que features reais pedem mais ajustes (então subir a constante). Palpite a calibrar; a constante fica em `specify-phase.md` e em `check_specify.py`.

**Decisão pendente 3 -- Idioma do `.feature`** (afeta Steps 2, 6; escolha dentro da Decisão pendente 1 do 000010)
- Opção A: o mesmo idioma das palavras do citizen em "Nas suas palavras" (maioria; empate = pt); declarado em `# language:`.
- Opção B: sempre pt.
- Opção C: o agente pergunta.
- **Recomendação: A.** Recommended when o citizen precisa ler o cenário na língua em que pensou o requisito. NOT recommended when o projeto tem política de idioma único para artefatos (então B, via `conventions.md`). C acrescenta uma pergunta a uma conversa que já tem teto de rodadas. Código, nomes de arquivo e de step definitions seguem em inglês.

**Decisão pendente 4 -- Quem escreve os cenários** (afeta Steps 2, 6)
- Opção A: o LLM escreve; `check_features.py` e `check_specify.py` conferem (default).
- Opção B: esqueleto determinístico a partir de "Quando A, o sistema B" (um cenário por REQ), o LLM completa `Dado`, erros e limites.
- **Recomendação: A.** Recommended when o validador já garante que nenhum REQ fica sem cenário e nenhum cenário fica sem tag, e se quer evitar mais um script. NOT recommended when o piloto (item 10) mostrar REQs sem cenário com frequência (então B, para garantir o caso feliz). Reabrir só com dado do Step 7.

**Decisão pendente 5 -- Restrição que não é observável como cenário** (afeta Steps 2, 4; lacuna com o 000009 e o 000010)
Exemplos: "compatível com o navegador X", "sem dependência Y". O D1 do 000008 conta REQ sem cenário como `descoberto` (GHK-005).
- Opção A: sempre cenário; se não houver como observar, o critério volta à grill (default; SPC-004).
- Opção B: permitir `verificação: gate` no REQ e excluí-lo do D1 (exige emenda ao 000008 e ao 000010).
- Opção C: permitir cenário em prosa sem número.
- **Recomendação: A.** Recommended when se quer manter D1 sem exceção e o gate (CRAP, mutação) já cobre a qualidade do código, não as restrições do produto. NOT recommended when o piloto mostrar restrições reais que só um gate externo mede (então B, em plano próprio que altere 000008/000010). C rejeitada: cenário sem número vira ruído, o risco do roadmap.

**Decisão pendente 6 -- Tamanho do conjunto de cenários e divisão em arquivos** (afeta Steps 2, 6)
- Opção A: um arquivo `<slug>.feature` por feature; sugestão (não bloqueio) de dividir por tema acima de 15 cenários.
- Opção B: um arquivo por REQ.
- **Recomendação: A.** Recommended when o citizen aprova o conjunto por requisito e a chave `<slug>/<arquivo>::<nome>` fica curta. NOT recommended when a feature passa de ~12 REQs (a grill já propõe quebrar em duas features, 000009). Nomes de cenário únicos por arquivo (GHK-010) continuam valendo.

## Files

Todos no **open-seja** (repositório de execução), exceto onde dito. O submodule não está inicializado neste worktree; caminhos **não verificados**: o Step 1 os confere antes de qualquer escrita. Itens marcados "se existir" dependem de os planos 000007, 000009 e 000010 já estarem executados.

- `.claude/references/general/specify-phase.md` (create) -- protocolo normativo `SPC-NNN`
- `.claude/skills/scripts/check_specify.py` (create) -- verificador e gravador de aprovação
- `.claude/skills/scripts/tests/test_check_specify.py` (create)
- `tests/fixtures/specify/` (create; caminho conforme o Step 1) -- casos golden e três execuções de referência
- `.claude/skills/_internal/plan/standard/SKILL.md` (modify) -- texto da fase specify (depois da grill) e `Specify: skipped`
- `.claude/skills/plan/SKILL.md` (modify) -- argumento `--specify` na tabela
- `.claude/skills/scripts/run_all_checks.py` (modify, opcional) -- ver Step 7; só se o Step 1 mostrar um ponto de registro limpo
- `.claude/references/general/extended-cycle-contract.md`, `.claude/references/template/feature-layout.md`, `.claude/references/general/gherkin-spec-format.md` (modify, só linha de ponteiro cada, se existirem)
- `_output/plans/plan-000011-progress.md` (create no Doutourado)

## Best practices

- Contrato primeiro, execução depois: citar `CYC-NNN`, `GRL-NNN` e `GHK-NNN` reais; se ainda não existirem no open-seja, marcar "a confirmar" (como 000008, 000009 e 000010).
- "PASS is a tool result, not a sentence" (research-000050): aprovar é um **comando que sai 0 e grava**, nunca uma frase do agente. A aprovação humana é necessária, não suficiente: sem o comando verde, não é gravada.
- Teste-primeiro também aqui: fixtures golden antes do `check_specify.py` (mesmo princípio do ciclo estendido).
- Humano como loop externo (Pocock): o citizen decide *o que*; o agente nunca ajusta REQ por conta própria durante o ajuste de cenário; pedido que muda a intenção volta à grill.
- Gherkin como critério de aceitação (Uncle Bob): declarativo, um comportamento por cenário, sem detalhe de implementação (000010).
- Voz controlada (000074): frases <= 25 palavras, uma ideia por frase, termos fixos ("requisito", "o que você vê", "fora do escopo", "cenário"), aviso antes da instrução. Importar as constantes do 000074/000009; nunca copiar o texto das regras.
- Determinismo: ordem de saída estável, sem relógio no verificador (`--at` vem de quem chama), UTC.
- Biblioteca padrão; funções puras (`check_specify(...)`) separadas de CLI e I/O (standards.md § Backend 1, 4, 19); `ruff` e `pyright` limpos no escopo do open-seja.

## Design decisions

- **User-visible impact:** depois que você aprova a lista de requisitos, eu escrevo os cenários e confiro sozinho se cada requisito tem cenário, se há step repetido ou confuso e se os limites têm número. Eu só te mostro o que passou. Você vê, por requisito, as frases dos cenários e a lista do que não será feito, e escolhe aprovar, ajustar, voltar à entrevista ou descartar. Se você mudar a intenção depois, eu aviso que os cenários estão desatualizados e peço nova aprovação. Tarefa sem código: nenhum cenário, e o plano diz por quê.
- **Trade-offs accepted:** mais um arquivo por feature (`scenarios.lock.json`) e mais um script a manter, em troca de uma aprovação que não pode ficar velha sem ninguém notar; mais uma aprovação do citizen antes do plano (fricção, medida no piloto do item 10); a conferência de voz é mecânica (comprimento, termos técnicos) e pode aceitar um cenário bem formado e ainda errado, por isso a aprovação humana e a auditoria semântica do 000008 existem.
- **Metacommunication impact:** I know you may not program by trade; therefore I write what the system will do as short sentences, one group per requirement, and I check them before you see them. You only approve what already passed my checks. I only go on to the plan after you say "approve", and if you change what you want later, I tell you the scenarios are out of date instead of keeping an old approval.

## Steps

### Step 1: Conferir o terreno e as dependências no open-seja
Na branch `dev` do open-seja (`git submodule update --init open-seja` se vazio), registrar no progress: (a) se os planos 000007, 000009 e 000010 já estão lá e os identificadores reais (`CYC-NNN` da fase specify e do layout, `GRL-NNN`, `GHK-NNN`); (b) CLI real de `check_features.py` (flags `--feature`, `--strict`, `--json`, `--matrix`, exit codes, `schema_version` do JSON) e de `check_intent.py` (`--require-approved`, `--strict`, `--json`); (c) se o parser de frontmatter e de tabelas de `check_intent.py` e de `check_features.py` **tolera chaves extras** no frontmatter do `intent.md` (`scenarios_approved_at`, `scenarios_approved_by`, `scenarios_rev`) sem erro; (d) o texto atual de `_internal/plan/standard/SKILL.md` (onde a fase grill entrou, para encaixar a specify logo depois) e a tabela de argumentos de `plan/SKILL.md` (se `--grill` já está e como `--specify` foi reservada); (e) as constantes do 000074 (`MAX_SENTENCE_WORDS`) e a existência de `lint_controlled_language.py`; (f) onde moram scripts, testes e fixtures; (g) como `run_all_checks.py` registra um check condicional. Se (a) faltar, escrever os Steps 2 a 8 contra o vocabulário dos planos do Doutourado e marcar cada identificador "a confirmar". Se (c) falhar, o Step 4 não usa o frontmatter novo sem emenda e a Decisão pendente 1 cai para C (registrar). Nada é escrito no open-seja.
- **Files**: open-seja/.claude/references/general/extended-cycle-contract.md (read, se existir), open-seja/.claude/references/general/grill-phase.md (read, se existir), open-seja/.claude/references/general/gherkin-spec-format.md (read, se existir), open-seja/.claude/skills/scripts/check_features.py (read, se existir), open-seja/.claude/skills/scripts/check_intent.py (read, se existir), open-seja/.claude/skills/_internal/plan/standard/SKILL.md (read), open-seja/.claude/skills/plan/SKILL.md (read), `_output/plans/plan-000011-progress.md` (create no Doutourado)
- **References**: product-design/conventions.md, product-design/constitution.md
- **Interface**: N/A
- **Verify**: o progress responde (a) a (g) com "existe", "rascunho" ou "ausente" e o caminho; registra as flags reais, a decisão sobre chaves extras (sim/não) e a lista de termos de C1 usada nos Steps seguintes; `git -C open-seja status` limpo.
- **Tests**: N/A (verificação de estado)
- [x] Done

### Step 2: Escrever o protocolo normativo `specify-phase.md`
Criar o documento com as regras `SPC-001..016` da tabela acima, cada uma com "Quem decide" e "Critério de aceitação" (molde de `CYC-NNN` e `GRL-NNN`). Incluir: (1) entrada e saída (`intent.md` aprovado → `features/<slug>/*.feature` + `scenarios.lock.json` + campos `scenarios_*`); (2) a derivação REQ→cenário com **3 exemplos bons e 3 ruins** (um `comportamento`, uma `restrição` com limite numérico e um erro; ruins: cenário sem `Quando`, step com URL, cenário que cobre dois requisitos sem tag para ambos), em pt-BR e en-US; (3) a tabela "de onde vem cada step" (`Dado` = dimensões quem/gatilho; `Quando` = ação do critério; `Então` = resultado que se vê); (4) o texto exato da apresentação de aprovação (um bloco por requisito: requisito, cenários, "o que não faz") e das opções Aprovar/Ajustar/Voltar à entrevista/Descartar, com `Recommended when` e `NOT recommended when` (C4); (5) o ciclo de ajuste e o teto `SPECIFY_MAX_ROUNDS = 3` (Decisão pendente 2) e quando volta à grill; (6) o esquema dos campos `scenarios_*` e de `scenarios.lock.json` (`schema_version`, `slug`, `basis: {REQ: rev}`, `index: [chave de cenário]`, `files: {arquivo: sha256}`, `rev`), e as regras `stale` (SPC-013); (7) a tabela de degradação (abaixo); (8) a voz: quais textos estão dentro e fora, termos fixos; (9) o que a fase **não** faz (SPC-015); (10) a interface `--specify` (SPC-016). Defaults das Decisões pendentes 1 a 6 marcados `[default; pendente]`. C1: sem nome de parceiro.

Tabela de degradação a incluir:

| Situação | O que a fase faz | Artefato |
|---|---|---|
| Feature com código, `intent.md` aprovado | Fluxo completo SPC-003 a SPC-010 | `.feature` aprovado + lock; plano v2 depois (item 6) |
| Tarefa sem código (docs, pesquisa, harness, config) | Não roda; não cria pasta | `Specify: skipped -- <motivo>` no plano |
| Tarefa mista (alguns steps com `Tests:` não-N/A) | Roda para os REQs com comportamento; steps sem comportamento observável usam `Scenarios: N/A (motivo)` (item 6) | `.feature` só dos REQs com código |
| `intent.md` não aprovado ou `grilling` | Recusa; diz "a lista de requisitos ainda não foi aprovada"; oferece `/plan --grill` | nenhum |
| Plano v1, projeto sem `features/`, open-seja antigo | A fase não existe; o `/plan` segue como sempre | nenhum; sem aviso de bloqueio |
| `check_features.py` ausente | Escreve os cenários como rascunho, **não aprova**, diz o motivo | `.feature` rascunho; `scenarios: draft` |
| Cenário que nenhum REQ justifica | Pergunta: vira REQ (volta à grill) ou sai | nenhum cenário sem tag |
| Citizen muda a intenção depois (grill de novo) | Cenários viram `stale`; a fase atualiza só os REQs com `rev` novo, mantém nomes dos demais | lock regravado na reaprovação |
| `--specify` avulsa sem `features/<slug>/` | Recusa e diz que a grill vem antes | nenhum |

- **Files**: open-seja/.claude/references/general/specify-phase.md (create)
- **References**: product-design/constitution.md, product-design/product-design-as-intended.md, product-design/standards.md § i18n
- **Depends on**: Step 1
- **Interface**: constantes `SPECIFY_MAX_ROUNDS = 3`; esquema de `scenarios.lock.json` (`schema_version: 1`); campos `scenarios`, `scenarios_approved_at`, `scenarios_approved_by`, `scenarios_rev` do frontmatter.
- **Verify**: o arquivo existe; todo `SPC-NNN` tem "Quem decide" e "Critério de aceitação"; `grep -c "SPC-"` >= 16; os exemplos bons (pt e en) passam em `check_features.py --strict` quando o Step 4 existir (reexecutado no Step 8); `git grep -ci` dos termos de C1 devolve zero; `python .claude/skills/scripts/run_all_checks.py` igual ao baseline do Step 1.
- **Tests**: N/A (documento normativo; a verificação mecânica é o Step 4)
- **Docs**: o próprio arquivo; o quickguide pt-BR fica para o item 9.
- [x] Done

### Step 3: Criar as fixtures golden (teste primeiro)
Antes do código, criar em `tests/fixtures/specify/` uma árvore por caso, todas fictícias (sem parceiro, sem dado real), cada uma com `features/<slug>/intent.md`, `*.feature` (quando couber) e `esperado.json` (`findings: [{rule, severity, file, line}]`, `status`, `exit_code`, e, para `--approve`, o `intent.md` e o lock finais). Casos: `ok-completo` (3 REQs: 2 `comportamento` e 1 `restrição` com limite numérico; 1 erro com cenário próprio; um `Outline` de limites; pt), `ok-minimo` (1 REQ, 1 cenário), `ok-en` (en), e um caso mínimo de **disparo** mais um **negativo** por regra checável: SPC-001 (`intent.md` em `grilling`; `intent.md` aprovado), SPC-003 (REQ `ativo` sem cenário; REQ `retirado` sem cenário **não** dispara; REQ `retirado` **com** cenário dispara), SPC-004 (`restrição` sem número; com número), SPC-007 (step de 26 palavras; de 25), SPC-008 (aviso GHK-013 vira bloqueio; tag `@skip`), SPC-010 (aprovação grava os campos e o lock; falha não grava nada; aprovar duas vezes com o mesmo `--at` produz bytes idênticos), SPC-012 (cenário renomeado sem linha em "Mudanças"; renomeado com a linha), SPC-013 (`rev` do REQ subiu depois da aprovação; hash do `.feature` mudou; tudo igual → `approved`). Casos de retrocompatibilidade: `sem-features`, `features-de-terceiros` (estilo behave, sem `intent.md`), `pasta-sem-intent`, `check-features-ausente` (simula o validador do 000010 ausente). Mais as três **execuções de referência** do roteiro do Step 7 (transcrição curta + `.feature` final esperado): (a) feature com código, uma rodada de ajuste; (b) tarefa sem código; (c) mudança de intenção depois da aprovação (stale). `README.md` com uma linha por caso.
- **Files**: open-seja/tests/fixtures/specify/ (create; árvore de casos), open-seja/tests/fixtures/specify/README.md (create)
- **References**: `.claude/references/general/specify-phase.md`
- **Depends on**: Step 2
- **Interface**: esquema de `esperado.json` (`findings`, `status`, `exit_code`, `intent_final`, `lock_final`).
- **Verify**: existe um caso de disparo e um negativo para cada regra checável (script lista as regras citadas nos `esperado.json` e compara com a tabela do Step 2); `line` de cada achado conferida à mão contra o arquivo; todos os `.feature` e `intent.md` válidos das fixtures passam em `check_intent.py` e `check_features.py` quando executados à parte; nenhum termo de C1 no diff.
- **Tests**: N/A (dados de teste; os testes que os usam são do Step 4 em diante)
- [x] Done

### Step 4: Implementar `check_specify.py` (verificação, `--status`, `--approve`)
Funções puras mais CLI: `check_specify.py [raiz] --feature <slug> [--json] [--status] [--approve --at <UTC ISO> --by <nome>]`. `check_specify(root, slug, *, features_report) -> Report` confere, nesta ordem: (SPC-001) `intent.md` existe, `status: approved` e `check_intent` sem `error` (chamada ao `check_intent.py` por importação de função ou por subprocesso `--json`, conforme o Step 1); (SPC-008) executa `check_features.py --strict --feature <slug> --json` por **subprocesso** e lê o JSON versionado (acopla à CLI, não aos internos do 000010; recusa `schema_version` desconhecido com exit 2); (SPC-003) todo REQ `ativo` tem >= 1 cenário e nenhum REQ `retirado` tem cenário (lê a matriz `--matrix`); (SPC-004) todo REQ `restrição` tem, em algum cenário ligado a ele, um literal numérico no `Então` ou nas linhas de `Examples`; (SPC-007) nenhum step passa de `MAX_SENTENCE_WORDS` (constante importada do 000074 se existir; senão 25, com ressalva `voz: não verificada` no relatório); (SPC-012) contra o lock existente, toda chave de cenário aprovada continua presente ou há linha correspondente em "Mudanças"; (SPC-013) cálculo de `status`: `missing` (sem `.feature`), `draft` (nunca aprovado), `approved` (lock bate com REQs `ativo`/`rev` e hashes), `stale` (lock existe e não bate, ou `intent.md` voltou a `grilling`). `--approve`: só se não houver nenhum achado de erro ou aviso, grava (nesta ordem, com escrita atômica por arquivo temporário e `rename`) `scenarios.lock.json` e depois os quatro campos no frontmatter do `intent.md`, sem tocar o resto do arquivo (preserva comentários e ordem); `--at` e `--by` são obrigatórios com `--approve` e entram como estão (sem relógio dentro do verificador). Saída legível em stdout/diagnóstico em stderr (standards.md § Backend 8), uma linha por achado `features/login/login.feature:12: SPC-004 erro: o requisito REQ-login-003 é uma restrição e o cenário não tem número. Dica: ...` em voz controlada, resumo final e `--json` com `schema_version: 1`. Exit codes iguais aos do 000010: `0` sem erro e sem aviso (informações não falham), `1` com erro ou aviso, `2` uso incorreto, arquivo ilegível, validador ausente ou `schema_version` desconhecido (nunca exceção bruta). Sem LLM, sem rede, biblioteca padrão. Se o Step 1 mostrou que o 000010 ainda não existe, implementar contra a CLI descrita no plano 000010 e marcar os testes que dependem dele "a confirmar".
- **Files**: open-seja/.claude/skills/scripts/check_specify.py (create), open-seja/.claude/skills/scripts/tests/test_check_specify.py (create)
- **References**: product-design/standards.md § Testing, § Backend 8, 19, 20; product-design/constitution.md
- **Depends on**: Step 3
- **Interface**: `check_specify(root: Path, slug: str, *, features_report: dict | None = None) -> Report`; `approve(root, slug, *, at: str, by: str) -> Report`; `Finding(rule, severity, file, line, message, hint)`; `status(root, slug) -> Literal["missing","draft","approved","stale"]`; CLI acima.
- **Verify**: `pytest .claude/skills/scripts/tests/test_check_specify.py` verde sobre as fixtures do Step 3; `ruff check` e `pyright` limpos no escopo do open-seja (ou "n/a" registrado); `python check_specify.py` num diretório sem `features/` não lança exceção e sai 0 com `status: missing` apenas quando `--feature` não foi dado; mesmo texto duas vezes produz saída idêntica (ordem estável).
- **Tests**: when `intent.md` está em `grilling`, returns um achado SPC-001 (erro) e `--approve` sai 1 sem escrever nada; when um REQ `ativo` não tem cenário, returns SPC-003 com o ID do REQ; when um REQ `retirado` tem cenário, returns SPC-003; when um REQ `restrição` tem cenário sem número, returns SPC-004, e com "no máximo 2 segundos" ou uma linha de `Examples` numérica returns nenhum; when um step tem 26 palavras, returns SPC-007, e com 25 não; when `check_features.py` devolve aviso GHK-013, returns SPC-008 (o gate é `--strict`); when todas as conferências passam e `--approve --at 2026-10-05T12:00:00Z --by usuario` é executado, returns exit 0, o frontmatter contém `scenarios: approved` e os três campos, o lock contém `basis`, `index` e `files`, e o restante do `intent.md` é byte a byte igual; when `--approve` é repetido com os mesmos argumentos, returns arquivos idênticos; when `--approve` falha, returns que nenhum dos dois arquivos mudou; when o `.feature` é editado depois da aprovação, `--status` returns `stale`; when o `rev` de um REQ sobe, `--status` returns `stale`; when um cenário aprovado é renomeado sem linha em "Mudanças", returns SPC-012; when `check_features.py` não existe, returns exit 2 com a mensagem "validador de cenários não encontrado" e nada é escrito; when a raiz é de terceiros (`features/` estilo behave sem `intent.md`), returns exit 0 sem achados.
- **Docs**: cabeçalho do script com a tabela de regras checáveis e ponteiro para `specify-phase.md`.
- [x] Done

### Step 5: Escrever o texto da fase specify no `/plan` e a flag `--specify`
Em `_internal/plan/standard/SKILL.md`, inserir a fase logo **depois** da fase grill e **antes** da criação das seções do plano: (1) ler `specify-phase.md`; (2) se a grill classificou a tarefa "sem código", escrever a linha `Specify: skipped -- <motivo>` no plano e seguir (nenhuma pasta, nenhuma pergunta); (3) senão, exigir o portão SPC-001 (`check_intent.py --require-approved --strict` e `check_specify.py --status`); recusar com a mensagem e a oferta de `/plan --grill` se falhar; (4) escrever `features/<slug>/<slug>.feature` na voz controlada, na linguagem escolhida (Decisão pendente 3), um grupo de cenários por REQ ativo, com `@REQ-<slug>-NNN` em cada cenário; (5) rodar `check_specify.py` e **corrigir sozinho** os achados antes de mostrar qualquer coisa ao citizen (no máximo 3 correções automáticas; se persistir, mostrar o achado em voz controlada e perguntar); (6) montar o resumo por requisito e perguntar (AskUserQuestion, C4) Aprovar / Ajustar / Voltar à entrevista / Descartar; (7) em **Ajustar**, editar só `*.feature`, subir `scenarios_rev`, registrar em "Mudanças" e repetir (5) e (6), até o teto `SPECIFY_MAX_ROUNDS`; pedido que muda *o que* se quer volta à grill; (8) em **Aprovar**, executar `check_specify.py --approve --at <agora UTC> --by usuario`; só com exit 0 dizer "aprovado" e seguir para o plano; (9) o plano cita `Feature: <slug>` e, no cabeçalho, `Specify: approved (rev N)`. Metacomm: pergunta e resumo em I/you quando o brief é metacomm. Em `plan/SKILL.md`, acrescentar `--specify` à tabela de argumentos ("roda só a specify e para; lê `intent.md` aprovado, escreve só `.feature`, lock e campos `scenarios_*`; reentrada permitida"). Não mudar a fase de revisão nem o `/implement`. O campo `Scenarios:` nos steps e a recusa de step sem cenário são do item 6: aqui o texto só diz "o item 6 liga os steps aos cenários".
- **Files**: open-seja/.claude/skills/_internal/plan/standard/SKILL.md (modify), open-seja/.claude/skills/plan/SKILL.md (modify), open-seja/.claude/references/general/extended-cycle-contract.md (modify, só linha de ponteiro, se existir)
- **References**: product-design/constitution.md, product-design/standards.md
- **Depends on**: Step 4
- **Interface**: flag `--specify` do `/plan`; a fase lê `SPECIFY_MAX_ROUNDS` de `specify-phase.md` e chama `check_specify.py`.
- **Verify**: `git diff --stat` mostra só os três arquivos listados; `python .claude/skills/scripts/check_skill_system.py` e `run_all_checks.py` com resultado igual ao baseline; `grep -n "\-\-specify" .claude/skills/plan/SKILL.md` acha a flag na tabela; `grep -n "Specify: skipped" .claude/skills/_internal/plan/standard/SKILL.md` acha a linha; a fase aparece **depois** da grill e **antes** da criação das seções; nenhum arquivo de gate, hook ou `settings` no diff.
- **Tests**: N/A (instruções de skill; a prova de comportamento é o Step 7)
- **Docs**: SKILL-quickguide do `/plan` fica para o item 9.
- [x] Done

### Step 6: Provar a voz e o ciclo de ajuste com cenários de referência
Escrever, nas fixtures do Step 3, o roteiro e os `.feature` esperados de três conversas, cada uma com o que o citizen vê no resumo: (a) **feature com código** (3 REQs, uma `restrição`): primeira versão com um defeito de proposta (um step com termo técnico e um REQ sem cenário), a saída de `check_specify.py` que o agente corrige sozinho, a versão mostrada ao citizen, **uma rodada de ajuste** ("o limite é 3 segundos, não 2") que sobe `scenarios_rev` e termina em `--approve`; (b) **tarefa sem código** (atualizar um README fictício): nenhuma pasta, linha `Specify: skipped -- <motivo>`; (c) **mudança de intenção depois da aprovação**: o REQ 002 sobe de `rev`, `--status` devolve `stale`, a fase reescreve só os cenários do REQ 002 preservando as chaves dos outros, e a reaprovação regrava o lock. Para cada uma, anexar a saída do verificador e provar a regra com pares negativos (a versão anterior falha com a regra certa). Medir e registrar no progress, como dado de calibração: número de rodadas de ajuste, número de correções automáticas antes do resumo, avisos de voz, e se o citizen fictício (o designer) entendeu cada cenário sem pedir reformulação (observação manual).
- **Files**: open-seja/tests/fixtures/specify/ (modify), `_output/plans/plan-000011-progress.md` (modify no Doutourado)
- **References**: product-design/constitution.md, `.claude/references/general/specify-phase.md`
- **Depends on**: Step 4, Step 5
- **Interface**: N/A
- **Verify**: `check_specify.py --approve --by usuario --at <fixo>` sai 0 nas versões finais de (a) e (c) e sai 1 nas versões intermediárias marcadas, com a regra esperada; `status` de (c) é `stale` antes da reaprovação e `approved` depois; (b) não cria `features/`; o progress traz rodadas, correções automáticas e avisos de voz de (a); nenhum termo de C1 no diff.
- **Tests**: when `check_specify.py` roda sobre cada versão intermediária das fixtures, returns o achado esperado (SPC-003, SPC-004, SPC-007 ou SPC-008 conforme a fixture); sobre cada versão final, returns lista sem achados e a aprovação grava lock idêntico ao esperado. Reusa os testes do Step 4 com as fixtures como entrada.
- [x] Done

### Step 7: Provar a execução real da fase (dry-run) e a retrocompatibilidade
Rodar `/plan --specify` uma vez, em modo de teste descartável, sobre o `intent.md` aprovado de (a) (saída da grill do 000009, fixture `grill/` ou a do Step 3), conferindo o texto escrito no Step 5: o agente escreve o `.feature`, roda o verificador, corrige, apresenta o resumo e pede aprovação; registrar no progress o que o agente fez de errado (cenário sem tag, step técnico, número faltando) para calibrar a SKILL. Provar que nada muda para quem não usa a fase: (1) `run_all_checks.py` no open-seja e num projeto fictício **sem** `features/` devolve o mesmo conjunto de resultados do baseline do Step 1; (2) as fixtures `sem-features`, `features-de-terceiros` e `pasta-sem-intent` retornam exit 0 e nenhum erro; (3) um plano v1 antigo é lido pelo `/plan` e pelo `/implement` como antes; (4) `--specify` sem `features/<slug>/` recusa em uma frase e não escreve nada. Registro opcional do check no `run_all_checks.py` (condicional, só se existir ao menos um `features/<slug>/scenarios.lock.json`): se o Step 1 mostrou ponto de registro limpo, registrar `specify` como check condicional que roda `check_specify.py --status` e **reprova** só quando o `status` é `stale` em feature que o `intent.md` marca como `scenarios: approved` (aprovação velha); sem lock, "pulado". Sem o ponto limpo, deixar como lacuna registrada.
- **Files**: `_output/plans/plan-000011-progress.md` (modify no Doutourado), open-seja/.claude/skills/scripts/run_all_checks.py (modify, opcional), open-seja/.claude/skills/scripts/tests/test_check_specify.py (modify)
- **References**: product-design/standards.md § Testing 6, product-design/constitution.md
- **Depends on**: Step 6
- **Interface**: entrada nova no registro de checks (nome `specify`, condicional) se aplicada.
- **Verify**: o progress registra o dry-run (arquivos escritos, saída do verificador, resumo mostrado, falhas do agente); `run_all_checks.py` sem `features/` lista `specify: pulado` e o conjunto de falhas pré-existentes é o do baseline (nenhuma nova); com a fixture `ok-completo` lista `specify: ok`; com a fixture stale lista `specify: falhou`; `git diff --stat` mostra só os arquivos esperados.
- **Tests**: when a raiz não tem `features/`, returns `pulado` e os resultados dos outros checks são idênticos ao baseline; when a raiz tem `features/` de terceiros sem `intent.md`, returns `pulado`; when uma feature tem `scenarios: approved` e o lock não bate, returns que `run_all_checks` reprova com o nome do check `specify`. Se o registro opcional não for feito: `N/A (lacuna registrada)`.
- [x] Done

### Step 8: Fechar o contrato com os itens vizinhos
Registrar no progress uma tabela "o que este plano entrega a quem": item 6 (plano v2 cita `Feature: <slug>` e `Specify: approved (rev N)`; `Scenarios:` lista chaves `<slug>/<arquivo>::<nome>` ou tags `@REQ-...` lidas de `scenarios.lock.json`; o `/plan` recusa step sem cenário só quando `Specify` não foi `skipped`), item 7 (cenário → teste usa a chave do lock; `skip`/`xfail` já são acusados antes por GHK-014/SPC-008), item 8 e plano 000008 (D1 conta `não medido` quando `check_specify.py --status` não é `approved`; `stale` = `não medido`, nunca `coberto`; a matriz de `check_features.py --matrix` mais o lock dão a chave do D2), item 9 (quickguide e `/help` descrevem `--specify` e o resumo de aprovação), item 10 (tempo de specify = parte do tempo até a primeira feature aprovada; usar os dados do Step 6 como linha de base). Reexecutar `pytest` do verificador, `check_features.py --strict` sobre os exemplos de `specify-phase.md` e `run_all_checks.py`; conferir vocabulário contra os planos 000007 a 000010; conferir C1 (`git grep -i` dos termos do Step 1 sobre o diff). Acrescentar **uma linha de ponteiro** (`Fase specify e aprovação dos cenários: ver specify-phase.md`) em `extended-cycle-contract.md`, `feature-layout.md` e `gherkin-spec-format.md`, se existirem; não editar esquema. Registrar as lacunas abaixo, as decisões pendentes que ficaram no default e o texto sugerido para o designer colar via `/implement --manual` (emendas aditivas ao `feature-layout.md`: o arquivo `scenarios.lock.json` e os campos `scenarios_*`; ao `drift-metric.md`: `stale` conta como `não medido`).
- **Files**: `_output/plans/plan-000011-progress.md` (modify no Doutourado), open-seja/.claude/references/general/extended-cycle-contract.md (modify, só ponteiro, se existir), open-seja/.claude/references/template/feature-layout.md (modify, só ponteiro, se existir), open-seja/.claude/references/general/gherkin-spec-format.md (modify, só ponteiro, se existir)
- **References**: product-design/constitution.md
- **Depends on**: Step 7
- **Interface**: N/A
- **Verify**: a tabela cobre os itens 6, 7, 8, 9, 10 e o plano 000008, cada linha citando uma regra `SPC-NNN`; suíte do verificador verde; `run_all_checks.py` com o mesmo conjunto de falhas pré-existentes do baseline; `git diff --stat` dos arquivos de ponteiro mostra no máximo uma linha adicionada cada e nenhuma alteração em gate, hooks, `settings` ou esquema; zero termos de C1; o progress lista as 6 decisões pendentes com o default em uso.
- **Tests**: N/A (verificação final; a suíte dos Steps 4 a 7 é o teste)
- [x] Done

## Coverage (advisory)

`product-design/product-design-as-intended.md` do Doutourado não tem marcadores REQ; `critique_plan_coverage.py` não se aplica e `Traces:` fica ausente. O plano executa no open-seja.

## Lacunas e conflitos com os planos 000007 a 000010

1. **Quem grava `scenarios: approved` e com que prova (000010, Decisão pendente 5; 000008, D1).** O 000010 só **lê** o campo, que este plano passa a escrever. O campo sozinho não detecta `.feature` editado ou REQ com `rev` novo depois da aprovação; o 000008 trata "`.feature` não aprovado" como `não medido`, mas `check_features.py --matrix` expõe `scenarios_approved` lendo só o campo. Por isso este plano acrescenta o lock e o estado `stale` (SPC-013). **Falta** o `check_features.py` (000010) ou o item 8 ler `check_specify.py --status` (ou o lock) antes de usar o campo; registrado como emenda para o item 8 e como texto sugerido no Step 8.
2. **Layout do 000007.** O layout fixa `{intent.md, *.feature, gate.json}`; este plano acrescenta `scenarios.lock.json` por feature (aditivo). O descobridor de features do 000010 lê `*.feature` e `intent.md`; o arquivo novo não deve colidir (Step 1 confirma). Emenda aditiva ao `feature-layout.md`, via designer.
3. **Frontmatter do `intent.md` (000009).** O `check_intent.py` do 000009 pode rejeitar chaves desconhecidas. Step 1 confere; se rejeitar, a emenda é ao 000009 (aceitar o prefixo `scenarios_`). Risco análogo no `check_features.py` do 000010.
4. **Grill reaberta (000009, "Degradação").** O 000009 diz que, ao reabrir a intenção, `status` volta a `grilling` e "o specify marca cenários desatualizados". Aqui isso é `stale` (SPC-013), mas **ninguém** reescreve `scenarios: approved` para `draft` quando a grill reabre; o campo fica mentindo até o próximo `--status`. Proposta: a leitura do campo exige `--status` (lacuna 1). Alternativa para o item 9: a grill reaberta também escreve `scenarios: stale`. Fica como decisão do designer na fase de integração.
5. **Tipo `restrição` (000009, Decisão pendente 3; 000008).** Este plano fecha a lacuna do 000009 ("o specify sabe transformar restrição em cenário?"): sim, com número obrigatório (SPC-004). Restrição que só um gate externo mede continua sem solução e volta à grill; alternativa (REQ "verificação: gate", fora do D1) exige emenda ao 000008 e ao 000010 (Decisão pendente 5).
6. **Skip por tipo de tarefa (000007, Decisão pendente 2).** A regra do 000007 é "algum step tem `Tests:` não-N/A", mas os steps só existem **depois** da specify. Este plano usa a classificação da grill ("com código" / "sem código") como proxy e deixa ao item 6 conferir depois: plano com `Tests:` não-N/A e `Specify: skipped` é inválido em v2. Sugestão: o contrato do 000007 esclarecer que o proxy é a classificação da grill.
7. **Voz controlada (000074).** Se o `lint_controlled_language.py` não estiver entregue, `check_specify.py` aplica só o limite de palavras com a constante do 000074 e registra `voz: não verificada` (mesma regra do 000009). Os steps do Gherkin são texto do agente (dentro da regra); os valores entre aspas e as tabelas `Examples` ficam fora.
8. **Escrita concorrente nos mesmos `SKILL.md` (000007 Step 5, 000009 Step 5, este Step 5).** Três planos tocam `_internal/plan/standard/SKILL.md` e `plan/SKILL.md`. A ordem de execução 000007 → 000009 → este plano precisa ser respeitada; o Step 1 lê o texto atual antes de editar.
9. **Formato de plano v2 (item 6).** Este plano grava `Specify: approved (rev N)` e `Feature: <slug>` no plano v1 que ele próprio gera para o open-seja ainda sem v2; o item 6 define o cabeçalho final. Divergência de cabeçalho é cosmética e é corrigida lá.
10. **Risco do roadmap "Gherkin mal escrito vira ruído".** A defesa mecânica é `GHK-*` + SPC-007; a defesa semântica é a aprovação do citizen e a auditoria por amostra do 000008. Um cenário bem formado e errado passa nas duas máquinas.

## Metacomm Intention
- **Summary**: I tell you that, after you approve the list of requirements, I write what the system will do as short scenarios, I check them myself before you see them, I show you one group per requirement and the list of what will not be done, and I only record your approval after the checks pass.
- **Source**: agent (technical plan; metacomm text kept for the report to the designer)

Metacomm contradiction check: nenhuma intenção existente em `product-design-as-intended.md` (D-001 a D-005) conflita; D-004 e D-005 (presets) ficam fora de escopo, como no roadmap.

## Review log

**Review depth:** Standard (8 steps, ~12 arquivos distintos, em dois grupos: scripts/testes/fixtures e referências/skill). Phase 1 inline (sem subagente; mesmo critério dos planos 000007 a 000010); sem Phase 2 (nenhum Deferred com risco de regressão não resolvido). Prefixo FEATURE-O sem linha na tabela de atalhos: usei DX, TEST, COMPAT, ARCH, SEC, UX.

### Step metadata validation
- Todo step tem Files, References, Interface, Verify, Tests, checkbox; `Depends on` só aponta para trás; nenhum step toca mais de 5 arquivos (Step 5 e Step 8 tocam 3 a 4; Step 4 toca 2).
- `Tests:` não-N/A (Steps 4, 6, 7) expressam comportamento observável ("when X, returns Y").
- Caminhos do open-seja **não verificados** (submodule vazio): o Step 1 é o portão.

### Phase 1 -- Perspective scan

| Perspective | Status | Concern |
|---|---|---|
| DX | Adopted | Tabela SPC-001..016 com "quem confere"; achados `arquivo:linha`, regra, dica; cada step com Verify por comando. |
| TEST | Adopted | Fixtures antes do código (Step 3); verificador determinístico com negativos; idempotência da aprovação; Steps 1, 2, 5, 8 documentais: `Tests: N/A` justificado. |
| COMPAT | Adopted | Plano v1 e projetos sem `features/` inalterados (Step 7); check opcional só dispara com lock; `intent.md` mínimo do 000007 continua válido; byte a byte fora dos campos `scenarios_*`. |
| ARCH | Adopted | `check_specify.py` acopla ao `check_features.py` pela CLI/JSON versionado, não pelos internos; sem LLM no verificador; gate e hooks intocados; escrita atômica. |
| SEC | Adopted | C1 por `git grep` nos Steps 2, 3, 6, 8; fixtures fictícias; o verificador só escreve `intent.md` e o lock da feature indicada (caminho resolvido sob `features/<slug>/`, sem seguir `..`); sem chaves nem `.env`. |
| UX | Adopted | Aprovação humana explícita com 4 opções; o citizen só vê o que passou nas conferências; teto de ajuste contra fricção; voz controlada. |
| PERF, DB, API, I18N, A11Y, VIS, RESP, DATA, OPS, MICRO | N/A | Sem superfície. I18N: apenas a Decisão pendente 3 (idioma do `.feature`), tratada em DX. |

### Riscos e lacunas registrados
- Caminhos, CLI dos validadores e tolerância a chaves extras do frontmatter não verificados (submodule vazio); Step 1 é o portão, com rota de recuo (Decisão pendente 1, opção C).
- Lacunas 1 e 4 exigem emendas aditivas nos itens 8 e 9 (ou no 000010); registradas, não resolvidas aqui.
- O teto de 3 ajustes e o limite de 25 palavras são palpite a calibrar no Step 6 e no piloto (item 10).
- Conferência mecânica de voz não prova entendimento; só a observação do designer no Step 6 e o piloto medem isso.

### Execution Metrics
| Metric | Value |
|---|---|
| Review depth | Standard |
| Phase 1 perspectives | 6 adopted, 10 N/A |
| Phase 2 deep-dives | 0 |
| Iterations | 0 |
| Pending decisions | 6 (defaults A, B, A, A, A, A) |

## Outcomes

- `specify-phase.md`: protocolo com regras `SPC-001..016` (entrada, derivação, restrição, voz, validação, aprovação, ajuste, degradação).
- `check_specify.py`: verificador determinístico por cima do `check_features.py`, com `--status` (`missing|draft|approved|stale`) e `--approve` que só grava com tudo verde.
- Aprovação com prova: campos `scenarios_*` no `intent.md` e `scenarios.lock.json` por feature.
- Fase specify e flag `--specify` no `/plan`; plano v1, projetos sem `features/` e tarefas sem código continuam funcionando.
- Fixtures golden, três execuções de referência (com ajuste, sem código, stale) e dados de calibração (rodadas de ajuste, correções automáticas, avisos de voz).
- Lista de lacunas contra os planos 000007 a 000010 e texto sugerido para o designer.

smoke: false
