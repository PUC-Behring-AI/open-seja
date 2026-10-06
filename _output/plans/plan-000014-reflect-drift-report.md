# Plan 000014 | FEATURE-O | 2026-10-05 12:41 UTC | reflect-drift-report: /reflect e /explain drift leem a matriz e reportam divergência por degrau (M1 vs M2) | Review: standard

> **Origem**: movido do ledger do Doutourado em 2026-10-05 (proposal-000088; la era `plan-000083`). Os IDs roadmap-000006 e plan-000007..000016 sao deste ledger (tabela no roadmap). Referencias a research-NNNNNN, reflection-NNNNNN, communication-NNNNNN, roadmap-000062 e plan-000064..000074 apontam para o ledger do Doutourado (repositorio do pesquisador). Caminhos `open-seja/...` em Files passam a ser relativos a raiz deste repositorio.
plan_format_version: 1

> Item 8 do roadmap-000006 (Wave 3; Depends on: drift-metric = plan-000008, plan-from-scenarios = plan-000012). Repositório de execução: **open-seja** (worktree/branch por plano); o plano vive no Doutourado. C1: nenhum nome de parceiro nos artefatos que forem ao open-seja. ID alocado pelo orquestrador (não usa `reserve_id.py`). Este plano é `plan_format_version: 1` porque o v2 só existe depois que o 000012 rodar. Usa o vocabulário dos planos 000007 a 000012 (`CYC-NNN`, `GRL-NNN`, `GHK-NNN`, `SPC-NNN`, `PFS-NNN`, `features/<slug>/`, `@REQ-<slug>-NNN`, chave de cenário `<slug>/<arquivo>::<nome>`, estados coberto/descoberto/não medido, vetor `(D1, D2, D3a, D3b)`). Não reabre nenhuma decisão fechada deles.

## User brief

> Item 8 do roadmap-000006: `reflect-drift-report` (Depends on: drift-metric, plan-from-scenarios). "/reflect e /explain drift leem a matriz intenção-cenário-teste-código-gate e reportam divergência por degrau."

## Agent interpretation

**Problem.** O 000008 definiu *o que* medir (D1, D2, D3a, D3b, momentos M1/M2, "não medido") e deixou seis casos golden como contrato de teste, mas disse que "a calculadora é do item 8". Os planos 000010, 000011 e 000012 entregam as peças de leitura (`check_features.py --matrix`, `check_specify.py --status`, `check_plan_scenarios.py --json`), e o 000011 deixou uma **emenda explícita para o item 8**: não confiar em `scenarios: approved` sem consultar `--status`. Hoje `/reflect` lê notas e gate por step (plan-000066) e `/explain drift` compara só `as-coded` vs `as-intended` de `product-design/`. Nenhum dos dois sabe ler a matriz nem diz **em que degrau a intenção se perdeu**.

**Approach.** Plano **técnico** no molde dos 000010 a 000012. Entrega no open-seja:
1. Um **calculador determinístico** `drift_report.py` (Python, biblioteca padrão, sem LLM, sem rede), em duas camadas separadas: (a) `load_matrix(...)` junta as fontes (`intent.md`, `*.feature`, relatório do runner, `gate.json`, plano v2, `check_specify.py --status`) numa matriz com as colunas derivadas do `drift-metric.md`; (b) `compute_report(matrix)` é função pura que devolve o vetor por degrau. Os **casos golden do 000008** testam (b) diretamente; fixtures de árvore testam (a).
2. **Instantâneos M1 e M2** (`--freeze`, `--moment`, `--compare`): M1 congelado com o gate; M2 regenerado no `/reflect`; a diferença M2 - M1 é a deriva depois da entrega.
3. **Coluna de auditoria semântica separada** (`audit.json` escrito por humano, amostra determinística de REQs a auditar), nunca misturada ao D.
4. **Relatório** em Markdown (obrigatório, voz controlada do 000074) e HTML (opcional, só se o 000074 estiver entregue), por degrau, com M1 vs M2 e `não medido` sempre ao lado.
5. **Integração mínima** nos `SKILL.md`: `/reflect` (conversacional) acrescenta a seção "Divergência por degrau" quando o plano ancorado tem `Feature:`; `/explain drift` ganha o escopo `ladder` (e o inclui em `all` só quando existe `features/`).
6. Referência normativa `drift-report.md` (regras `DRP-NNN`) que fecha as entradas, as razões de "não medido" e a degradação.

**Alternatives rejected.**
- Pedir ao LLM que "leia a matriz e diga o D": viola a decisão fechada 4 do 000008 (cálculo sem LLM) e não reproduz os golden.
- Um número único ("saúde da feature"): rejeitado pelos 000007 e 000008. O destaque do degrau de maior divergência é só texto.
- Deixar o relatório como skill nova (`/drift`): bifurca o ciclo (decisão fechada 1 do 000007: sem skill nova). Entra em `/reflect` e `/explain drift`.
- Confiar em `scenarios: approved` lido do frontmatter via `--matrix`: o campo não vê `.feature` editado nem REQ com `rev` novo (000011, lacuna 1) e fica mentindo quando a grill reabre (lacuna 4). Rejeitado: `check_specify.py --status` é consultado sempre.
- Tornar o relatório um portão (exit 1 com divergência): o portão é o gate (research-000050, "PASS is a tool result"); o relatório mede, não bloqueia. Exit 0 quando o relatório foi produzido.
- Estender `summarize_artifacts.py` para ler a matriz: ele resume artefatos por ID; a matriz é por feature, não por artefato. Rejeitado; `drift_report.py` é chamado ao lado dele.
- Gerar HTML por obrigação: depende do 000074 (ainda não entregue neste worktree); Markdown basta para o piloto (Decisão pendente 3).

**Selection rationale.** Sem `source:`. Fontes: roadmap-000006 (item 8, tabela "Decisões", H-009), plano 000008 (fórmula, estados, momentos, golden, controle A/B, decisão 4 = B), plano 000007 (vocabulário e layout), plano 000010 (`--matrix`, chave do cenário, contrato do relatório do runner), plano 000011 (`--status`, estado `stale`, lacunas 1 e 4), plano 000012 (cabeçalho v2, `Scenarios:`, matriz cenário→step), roadmap-000062 (H-008, `/reflect` transversal, gate), research-000050 (gate determinístico), plano 000074 (voz e HTML).

### Decisões fechadas (aprovadas; não reabrir neste plano)

1. **Divergência composta, por degrau, nunca número único.** O relatório é o vetor `(D1, D2, D3a, D3b)` com `n`, `cobertos`, `descobertos` e `não medido` de cada um (000008, decisão 1).
2. **Colunas derivadas definidas no `drift-metric.md`** (000008, decisão pendente 4 = B): `scenario_status`, `test_result`, `red_reason_ok`, `touched_uncovered` são **calculadas aqui** juntando as fontes; o esquema do item 1 não muda. Se alguma não for derivável, a emenda aditiva ao `feature-layout.md` é registrada como lacuna, não feita aqui.
3. **`stale` e `--matrix` desatualizado.** Antes de usar `scenarios: approved` (ou o campo `scenarios_approved` da matriz), o calculador roda `check_specify.py --status`. `stale`, `draft` e `missing` tornam o **D1 `não medido`** (000008 e 000011, lacuna 1). Nunca confiar só no campo.
4. **Cálculo determinístico, sem LLM.** A auditoria semântica é uma coluna **à parte** (`adequado: sim/parcial/não`), lida de `audit.json`; nunca entra no D (000008, decisões 4 e pendente 1 = B).
5. **`não medido` fica fora do denominador e sempre aparece ao lado, com a razão.** Denominador zero = `D` "n/a", nunca 0 (000008, decisão 3).
6. **Momentos M1 e M2.** M1 = fim do IMPLEMENT (matriz congelada com o gate). M2 = REFLECT (matriz regenerada). O relatório mostra os dois e a diferença. Sem M0.
7. **Compatibilidade.** Plano v1 (ou sem `plan_format_version`) e projetos sem `features/` **não são afetados**: o script diz "não aplicável" numa linha, sai 0, e as duas skills não acrescentam seção nenhuma. `Specify: skipped` também é "não aplicável".
8. **O relatório não bloqueia.** Exit 0 quando o relatório foi produzido, mesmo com divergência alta; exit 2 só para erro de argumento ou de leitura. O portão continua sendo o gate.
9. **`/reflect` continua não prescritivo.** O relatório escreve observações em tempo passado; nunca "você deveria" nem "considere" (regra do `/reflect`, coberta por teste).
10. **Escopo.** Este plano não edita o gate, os hooks, o contrato do 000007, o `feature-layout.md`, os `casos.json` do 000008, `check_features.py`, `check_specify.py`, `check_plan_scenarios.py` nem o `/implement`; não edita roadmap nem `_output/INDEX.md`; não escreve em `product-design/` do Doutourado; não escreve quickguides (item 9).

### Mapa das fontes (resumo; o texto normativo é o Step 2)

| Coluna da matriz | Fonte | Lido por | Escrito por (item) |
|---|---|---|---|
| REQ, `status`, `rev`, tipo | `features/<slug>/intent.md` | `check_features.py --matrix --json` (000010) | grill (3/5) |
| `scenario_status` do REQ (aprovado, rascunho, desatualizado) | `check_specify.py --status` + `scenarios.lock.json` (000011) | `drift_report.py` | specify (5) |
| cenário, tag `@REQ-...`, chave | `features/<slug>/*.feature` | `check_features.py --matrix --json` | specify (5) |
| cenário → step dono | `Scenarios:` do plano v2 | `check_plan_scenarios.py --json` (000012) | plano (6) |
| `test_result` (verde, vermelho, `skip`, `xfail`, ausente) | relatório do runner (JUnit com propriedade `req`, contrato do 000010 Step 8) | `drift_report.py` | runner (7) |
| `red_reason_ok` | registro "vermelho pelo motivo certo" | `drift_report.py` | `/implement` (7) |
| gate PASS, `--accept-baseline` | `features/<slug>/gate.json` | `drift_report.py` | gate (62) via `/implement` (7) |
| `touched_uncovered` | cobertura só dos testes de cenário x diff da feature | `drift_report.py` | `/implement` (7) |
| adequação semântica | `features/<slug>/drift/audit.json` | `drift_report.py` | humano |

### Razões de "não medido" (códigos fixos, ver Step 2)

`NM-INTENCAO-NAO-APROVADA`, `NM-SPECIFY-PULADA`, `NM-CENARIOS-STALE` (D1), `NM-SEM-RUNNER` (D2), `NM-SEM-GATE`, `NM-SEM-REGISTRO-VERMELHO` (D3a), `NM-SEM-COBERTURA`, `NM-SEM-BASE-DIFF` (D3b), `NM-SEM-M1` (delta). Cada razão aparece escrita ao lado do degrau.

### Decisões pendentes
Cada uma tem default (a recomendação). Se o designer não responder, os steps seguem o default; mudar uma altera só o Step indicado.

**Decisão pendente 1 -- Onde ficam os instantâneos M1 e M2** (afeta Steps 2, 6)
- Opção A: `features/<slug>/drift/M1.json` e `M2-<AAAA-MM-DD>.json` (versionados com a feature).
- Opção B: `_output/drift/<slug>/` (local por fork, fora da árvore da feature).
- **Recomendação: A.** Recommended when o M1 precisa sobreviver ao plano e ser lido pelo `/reflect` e pelo piloto (item 10), e quando `_output/` é local por fork (mesma razão do 000007, decisão pendente 3). NOT recommended when o projeto não versiona `features/` ou não quer arquivos derivados na árvore (então B, e o M1 some com o fork). Aditivo ao layout do 000007; emenda ao `feature-layout.md` via designer.

**Decisão pendente 2 -- Quem congela o M1** (afeta Steps 6, 8; é uma lacuna com os 000007/000008, ver "Lacunas")
- Opção A: o `/implement` chama `drift_report.py --freeze` ao fim (fiação feita pelo item 7 ou 9; este plano só entrega o comando e o texto sugerido).
- Opção B: o `/reflect` reconstrói o M1 do histórico git (gate.json no commit do fim do IMPLEMENT).
- Opção C: manual (o designer roda `--freeze`).
- **Recomendação: A**, com degradação para "M1 não congelado" (sem delta, `NM-SEM-M1`) quando o instantâneo não existe. Recommended when o `/implement` é o dono do momento M1 e o gate acabou de rodar. NOT recommended: B sozinho (depende de convenção de commit que ninguém fixou) e C sozinho (esquecível; vira ausência de M1 no piloto).

**Decisão pendente 3 -- Saída HTML** (afeta Step 7)
- Opção A: só Markdown agora.
- Opção B: Markdown obrigatório; HTML opcional (`--html`) usando o gerador do 000074 **se existir**; senão "HTML: não gerado" numa linha.
- Opção C: HTML obrigatório.
- **Recomendação: B.** Recommended when o 000074 pode ainda não estar entregue no open-seja e o relatório tem barras por degrau que ganham com o HTML. NOT recommended: C (cria dependência dura de um plano de outra trilha) e A se o 000074 já estiver lá (perde a barra por degrau para o citizen).

**Decisão pendente 4 -- `/explain drift`: onde entra o relatório** (afeta Step 8)
- Opção A: só o escopo `ladder [<slug>]`, avulso.
- Opção B: escopo `ladder` e também dentro de `all` quando existe `features/`.
- **Recomendação: B.** Recommended when `all` é o escopo padrão e o designer espera uma visão única de deriva; sem `features/` nada muda (compatibilidade). NOT recommended when o relatório fica longo demais no `all` (então A). O escopo `--promote` e `--scope since-plan` ficam intactos.

**Decisão pendente 5 -- D2, D3a e D3b quando o estado é `stale`** (afeta Steps 2, 4)
- Opção A: só o D1 vira `não medido`; D2, D3a e D3b são calculados com a ressalva "cenários desatualizados" (default).
- Opção B: os quatro viram `não medido`.
- **Recomendação: A.** Recommended when o teste e o gate ainda dizem a verdade sobre o código entregue, e esconder isso apaga o dado que mostra a deriva. NOT recommended when o `.feature` foi editado de modo que a chave do cenário mudou (então o calculador não acha o teste e o D2 já sai `descoberto`; nesse caso B é mais honesto).

**Decisão pendente 6 -- Auditoria semântica: quem preenche** (afeta Step 6; segue a decisão pendente 1 do 000008)
- Opção A: humano cego por amostra (default do 000008, opção B): o script lista a amostra e lê `audit.json`; todos os REQs do braço A e >= 30% do braço B.
- Opção B: LLM-judge em contexto limpo, com amostra humana >= 20% (opção C do 000008).
- **Recomendação: A.** Recommended when o piloto tem poucas features. NOT recommended when passa de ~40 REQs por braço (então B, mesma leitura de `audit.json`; muda só quem escreve). O calculador lê o mesmo arquivo nos dois casos; o campo `por` registra humano ou juiz.

## Files

Todos no **open-seja**, exceto onde dito. O submodule não está inicializado neste worktree; caminhos **não verificados**: o Step 1 os confere antes de qualquer escrita.

- `.claude/references/general/drift-report.md` (create) -- referência normativa (`DRP-NNN`)
- `.claude/skills/scripts/drift_report.py` (create) -- carregador, calculador, instantâneos, renderizadores, CLI
- `.claude/skills/scripts/tests/test_drift_report.py` (create)
- `tests/fixtures/drift_report/` (create) -- árvores fictícias por caso (`esperado.json` em cada)
- `tests/fixtures/drift/casos.json` (read-only; propriedade do 000008)
- `.claude/skills/reflect/SKILL.md` (modify) -- seção opcional no fluxo conversacional
- `.claude/skills/explain/SKILL.md` (modify) -- escopo `ladder` na tabela de argumentos
- `.claude/skills/_internal/explain/drift/SKILL.md` (modify) -- passo do relatório por degrau
- `_output/plans/plan-000014-progress.md` (create no Doutourado)

## Best practices

- "PASS is a tool result, not a sentence" (research-000050): cada D é cálculo reproduzível sobre arquivos; o texto do relatório é gerado por modelo de frase fixa, não por LLM.
- Funções puras separadas de I/O e de CLI (standards.md § Backend 1, 4, 19); `ruff` e `pyright` limpos no escopo do open-seja.
- Contar o que falta ao lado do que existe: `não medido` com razão; nunca esconder lacuna em média.
- Saída reprodutível: mesmo conjunto de arquivos produz JSON e Markdown byte a byte iguais (ordem estável, sem timestamp dentro do vetor; o carimbo de hora vem de `--at`).
- Teste-primeiro: golden do 000008 e fixtures de árvore antes do código (Steps 3 e 4).
- Voz controlada nos textos que o citizen lê (frases <= `MAX_SENTENCE_WORDS` = 25, plano 000074); "Dado/Quando/Então" não é voz do relatório.
- Escrita atômica dos instantâneos (arquivo temporário e `os.replace`); instantâneo grava o hash SHA-256 de cada entrada para detectar edição depois do M1.

## Design decisions

- **User-visible impact:** quando você pedir uma reflexão sobre um plano com feature, ou rodar `/explain drift`, eu mostro três barras (intenção→cenário, cenário→teste, teste→código) com os números brutos, o que não foi medido e por quê, e o que mudou desde a entrega. Sem `features/`, nada muda.
- **Trade-offs accepted:** ganha-se um relatório que reproduz as fixtures e diz em que degrau a intenção se perdeu; perde-se a simplicidade de um número. O D3b depende de cobertura por cenário que o item 7 ainda produz: até lá aparece `não medido`. Cálculo e relatório ficam num único script (~700 linhas estimadas), aceito porque as camadas (carregar, calcular, renderizar) são funções separadas com testes próprios.
- **Metacommunication impact:** I know a single score would be easier to read; therefore I show you each step of the ladder apart, with what I could not measure and why, so that you see where your intent got lost and what changed after delivery, and you decide what to fix. I only describe what happened; I do not tell you what to do.

## Steps

### Step 1: Conferir o terreno, as CLIs reais e as skills atuais
Na branch `dev` do open-seja (`git submodule update --init open-seja` se vazio), registrar no progress: (a) se os planos 000007, 000008, 000010, 000011 e 000012 já estão lá, com os identificadores reais (`CYC-NNN`, `SPC-NNN`, `PFS-NNN`) e o texto final de `drift-metric.md` (nomes exatos das colunas derivadas, das razões de "não medido", do esquema `{feature, momento, degraus, leituras, ressalvas}`); (b) o caminho e o esquema real de `tests/fixtures/drift/casos.json` (campos `entrada` e `esperado`); (c) CLI real e JSON de `check_features.py --matrix --json`, `check_specify.py --status` e `check_plan_scenarios.py --json` (flags, exit codes, `schema_version`); (d) o formato do relatório do runner (propriedade `req` do 000010, Step 8), os campos reais do `gate.json` e se existem registro de "vermelho pelo motivo certo", cobertura só dos testes de cenário e referência-base do diff (item 7 é da mesma Wave e pode não ter rodado); (e) o texto atual de `reflect/SKILL.md`, `explain/SKILL.md` e `_internal/explain/drift/SKILL.md` (versão, onde entram as mudanças, se algum plano 76 a 81 já os tocou); (f) se o 000074 entregou `lint_controlled_language.py` e o gerador de HTML; (g) baseline de `python .claude/skills/scripts/run_all_checks.py`; (h) a lista de termos de C1 (nomes de parceiro) para os `git grep` dos Steps seguintes. Para cada fonte da matriz: "existe", "rascunho" ou "ausente". Se o 000008 ou o 000012 não estiver no open-seja, escrever os Steps 2 a 8 contra o texto dos planos (Doutourado) e marcar cada citação como "a confirmar". Nada é escrito no open-seja.
- **Files**: open-seja/.claude/references/general/drift-metric.md (read, se existir), open-seja/tests/fixtures/drift/casos.json (read, se existir), open-seja/.claude/skills/scripts/check_features.py (read, se existir), open-seja/.claude/skills/scripts/check_specify.py (read, se existir), open-seja/.claude/skills/reflect/SKILL.md (read)
- **References**: product-design/conventions.md, product-design/constitution.md
- **Interface**: N/A
- **Verify**: o progress lista, para cada fonte da tabela "Mapa das fontes", "existe/rascunho/ausente" com o caminho, e responde (a) a (h); registra as lacunas encontradas contra o texto "Lacunas e conflitos" deste plano; `git -C open-seja status` limpo.
- **Tests**: N/A (verificação de estado)
- [x] Done

### Step 2: Escrever a referência normativa `drift-report.md` (`DRP-NNN`)
Criar o documento com regras `DRP-001..` (molde de `CYC-NNN`, `SPC-NNN`, `PFS-NNN`; cada regra com "Quem decide" e "Critério de aceitação"): (1) **entradas e precedência**: cada coluna da tabela "Mapa das fontes", com o comando exato que a lê e o que acontece se a fonte falta; (2) **derivação das colunas** `scenario_status`, `test_result`, `red_reason_ok`, `touched_uncovered` como o `drift-metric.md` as define (citar, não redefinir); (3) **consulta obrigatória a `check_specify.py --status`** antes de usar `scenarios: approved`, e a tabela estado → efeito (`approved` mede D1; `stale`, `draft`, `missing` → D1 `NM-CENARIOS-STALE`/`NM-INTENCAO-NAO-APROVADA`, D2/D3 conforme Decisão pendente 5); (4) **razões de não medido** (os códigos `NM-*`, uma frase de relatório por código, em voz controlada); (5) **fórmula e denominador zero** por referência ao `drift-metric.md` (sem copiar números); (6) **M1, M2 e delta**: quando o delta aparece (os dois `D` definidos), quando fica `NM-SEM-M1`, e que o delta mostra numerador e denominador dos dois lados porque o denominador pode mudar (REQ novo, REQ retirado); (7) **auditoria semântica**: formato de `audit.json` (`req`, `adequado: sim|parcial|nao`, `por: humano|juiz`, `nota` verbatim), regra da amostra determinística (ordenar os REQs por `sha1(slug + ":" + req)` e tomar `ceil(30%)`; todos no retrofit do braço A), e que a coluna nunca altera D; (8) **leituras fora do D** (do 000008): cadeia completa por REQ, cenário órfão, cenário sem tag, "escada fechou sem capturar a intenção" (D1 = D2 = D3a = 0 e (O1 > 0 ou algum `adequado: nao`)); (9) **formato do relatório** (tabela por degrau com `n`, `cobertos`, `descobertos`, `não medido` + razão, `D`, M1, M2, delta; destaque textual do degrau de maior `D` definido, sem somar; empate declarado) e o JSON versionado (`schema_version: 1`); (10) **regra não prescritiva**: tempo passado, sem "deveria/considere/recomendamos"; (11) **degradação e compatibilidade** (plano v1, sem `features/`, `Specify: skipped`, tarefa sem código: "não aplicável"); (12) **anti-gaming**: D3a só vale com gate `full` PASS sem `--accept-baseline` e com `red_reason_ok` registrado; sem registro, o estado é `NM-SEM-REGISTRO-VERMELHO` e o relatório traz a ressalva (000008); (13) **o que o relatório não faz** (não bloqueia, não grava `scenarios:`, não edita `intent.md`, não altera plano). Citar os IDs reais (ou "a confirmar" conforme o Step 1).
- **Files**: open-seja/.claude/references/general/drift-report.md (create)
- **References**: product-design/constitution.md, product-design/standards.md § Backend 8, 19
- **Depends on**: Step 1
- **Interface**: regras `DRP-001..`; esquema JSON do relatório (`schema_version`, `feature`, `momento`, `degraus`, `leituras`, `ressalvas`, `auditoria`, `delta`, `entradas` com hashes); códigos `NM-*`; formato de `audit.json` e de instantâneo.
- **Verify**: o arquivo existe; cada código `NM-*` do plano aparece com sua frase; a tabela estado → efeito do `--status` cobre `approved`, `stale`, `draft`, `missing`; os nomes `D1`, `D2`, `D3a`, `D3b` e as colunas derivadas coincidem com o `drift-metric.md` (`git grep -c "D3a"` em ambos >= 1); nenhum termo de C1; `run_all_checks.py` igual ao baseline do Step 1.
- **Tests**: N/A (documento normativo; os testes são dos Steps 3 a 7)
- **Docs**: o próprio documento; o quickguide pt-BR é do item 9.
- [x] Done

### Step 3: Fixtures de árvore e testes que falham (teste-primeiro)
Antes do código, criar `tests/fixtures/drift_report/<caso>/` (todas fictícias, sem parceiro e sem dado real), cada uma com `features/<slug>/` (`intent.md`, `*.feature`, `scenarios.lock.json` quando couber, `gate.json`, relatório do runner, `drift/` quando couber), um `plan.md` v2 mínimo, um arquivo `status.txt` (resultado simulado de `check_specify.py --status`, lido por um stub injetado nos testes) e `esperado.json` (relatório completo). Casos: `ok-m1` (feature completa, M1); `ok-m2-deriva` (mesma feature depois de um `.feature` mudar e um teste ficar vermelho: M1 congelado e M2 com delta); `stale` (`status.txt` = `stale` com `intent.md` dizendo `scenarios: approved`: D1 `NM-CENARIOS-STALE`); `sem-runner` (D2 `NM-SEM-RUNNER`); `sem-gate` (D3a e D3b `não medido`); `sem-registro-vermelho` (D3a com ressalva); `skip-xfail` (contam como `descoberto` no D2); `specify-pulado` e `plano-v1` e `sem-features` (todos "não aplicável", saída de uma linha); `denominador-zero` (D "n/a"); `denominador-muda` (REQ novo entre M1 e M2); `auditoria` (`audit.json` com um `nao`, sem alterar nenhum D); `escada-fechada` (D1 = D2 = D3a = 0 e auditoria `nao`: leitura de alerta); `entrada-corrompida` (JSON inválido no gate: exit 2, mensagem com o arquivo). Escrever `test_drift_report.py` com um teste por caso, importando funções que ainda não existem (devem falhar por `ImportError`/asserção). Incluir **três testes dos golden do 000008**: carregar `casos.json`, passar cada `entrada` a `compute_report` e comparar com `esperado` (os seis casos), mais um teste de determinismo (duas execuções, saída idêntica).
- **Files**: open-seja/tests/fixtures/drift_report/ (create; árvores e `esperado.json`), open-seja/.claude/skills/scripts/tests/test_drift_report.py (create), open-seja/tests/fixtures/drift_report/README.md (create; uma linha por caso)
- **References**: `.claude/references/general/drift-report.md`, `tests/fixtures/drift/casos.json`
- **Depends on**: Step 2
- **Interface**: esquema de `esperado.json` = o relatório do Step 2; `compute_report(matrix: dict) -> dict`; `load_matrix(root: Path, slug: str, *, status_fn=None, moment: str = "M2") -> dict`.
- **Verify**: `pytest .claude/skills/scripts/tests/test_drift_report.py` roda e **falha** em todos os testes por ausência do módulo (registrar a saída no progress); recontagem independente de numerador e denominador por degrau de cada `esperado.json` (por exemplo `python -c` que conta os estados da matriz de entrada) coincide com o `esperado` do mesmo caso; nenhum termo de C1 no diff.
- **Tests**: when a matriz do caso golden "normal" é calculada, returns `D1 = descobertos/(cobertos+descobertos)` igual ao `esperado`; when o caso golden "nada medido" é calculado, returns `nao_medidos = n` e `D = "n/a"` em D3a e D3b; when o caso golden "escada fechada" é calculado, returns a leitura de alerta; when `status.txt` diz `stale` e o frontmatter diz `approved`, returns D1 com `NM-CENARIOS-STALE` e `cobertos = descobertos = 0`; when `skip` ou `xfail` vincula o único teste de um cenário, returns esse cenário como `descoberto` no D2; when duas execuções rodam sobre os mesmos arquivos, returns JSON byte a byte igual.
- **Docs**: README de uma linha por caso no mesmo diretório.
- [x] Done

### Step 4: Calculador puro `compute_report` (faz os golden do 000008 passarem)
Em `drift_report.py`, implementar `compute_report(matrix) -> dict` **sem I/O e sem LLM**: contar por degrau `cobertos`, `descobertos`, `nao_medidos` segundo as colunas derivadas (D1 por REQ; D2 por cenário; D3a por cenário; D3b por linha/ramo tocado), aplicar `D = descobertos/(cobertos+descobertos)` com `não medido` fora do denominador e denominador zero = "n/a", gerar as leituras fora do D (cadeia completa, órfãos, sem tag, "escada fechou sem capturar a intenção"), as ressalvas (anti-gaming, amostra pequena < 8 REQs, `stale` conforme Decisão pendente 5) e a marca textual do degrau de maior `D` (empate declarado; `n/a` e `não medido` nunca ganham). Aritmética exata: guardar numerador e denominador inteiros e só formatar `D` na saída (duas casas, sem arredondar o numerador). Nenhum campo de tempo dentro do vetor.
- **Files**: open-seja/.claude/skills/scripts/drift_report.py (create)
- **References**: `.claude/references/general/drift-report.md`, `.claude/references/general/drift-metric.md`
- **Depends on**: Step 3
- **Interface**: `compute_report(matrix: dict) -> dict` (esquema do Step 2); `Degrau = Literal["D1","D2","D3a","D3b"]`; `format_d(num: int, den: int) -> str`.
- **Verify**: `pytest ... -k "golden or compute"` verde (os seis casos do 000008 e os casos de cálculo do Step 3); `ruff check` e `pyright` limpos em `drift_report.py` (ou "n/a" registrado se o open-seja não os usa); o módulo não importa `subprocess`, `socket` nem `anthropic` nesta camada (`git grep` no trecho de `compute_report`).
- **Tests**: when um degrau tem 3 cobertos, 1 descoberto e 2 não medidos, returns `D = 1/4`, `nao_medidos = 2` e a razão ao lado; when cobertos + descobertos = 0, returns `D = "n/a"` e não 0; when D1 = D2 = D3a = 0 e uma auditoria diz `nao`, returns a leitura "escada fechou sem capturar a intenção"; when dois degraus empatam no maior `D`, returns o destaque com os dois nomes e a palavra "empate"; when um cenário tem teste verde mas o gate rodou com `--accept-baseline`, returns esse cenário como `descoberto` em D3a com a ressalva.
- **Docs**: cabeçalho do script com a tabela de regras `DRP-NNN` e ponteiro para `drift-report.md`.
- [x] Done

### Step 5: Carregador `load_matrix` (fontes → matriz) com `--status` obrigatório
Funções que juntam as fontes: (a) `intent.md` e `*.feature`: chamar `check_features.py [raiz] --feature <slug> --matrix --json` (por subprocesso com `sys.executable`, lista de argumentos, sem shell, tempo-limite) e ler o JSON versionado, **sem reimplementar o parser**; (b) `status_fn(root, slug) -> "missing"|"draft"|"approved"|"stale"` que roda `check_specify.py --status --feature <slug>`; resultado não-`approved` define `scenario_status` e a razão do D1, **ignorando o campo `scenarios_approved` da matriz** quando o status diz outra coisa (o campo só é usado se `check_specify.py` não existe, e então o D1 sai com ressalva "aprovação não verificada"); (c) plano v2: `check_plan_scenarios.py <plano> --json` para a coluna cenário → step dono (informativa, **não** entra no vetor); (d) relatório do runner: ler JUnit XML (propriedade `req` e chave do cenário `<slug>/<arquivo>::<nome>`, 000010 Step 8) e mapear `passed`, `failed`, `skipped`, `xfail`; teste coletado sem cenário vira "teste órfão" fora do D; (e) `gate.json`: `full` PASS, `--accept-baseline`, ts; (f) registro "vermelho pelo motivo certo" e cobertura só dos testes de cenário x diff (caminhos e nomes conforme achados no Step 1; arquivo ausente = `NM-SEM-REGISTRO-VERMELHO` / `NM-SEM-COBERTURA`; base do diff ausente = `NM-SEM-BASE-DIFF`); (g) preencher as colunas derivadas do `drift-metric.md` e o bloco `entradas` com o SHA-256 de cada arquivo lido. Erros de leitura (JSON inválido, XML mal formado, ferramenta ausente que não seja `check_specify.py`) viram exceção tipada `DriftInputError(arquivo, motivo)`; fonte **ausente** nunca é erro, é `não medido` com razão. Plano v1, sem `features/` ou `Specify: skipped` devolvem a matriz especial `nao_aplicavel` com o motivo.
- **Files**: open-seja/.claude/skills/scripts/drift_report.py (modify), open-seja/.claude/skills/scripts/tests/test_drift_report.py (modify)
- **References**: `.claude/references/general/drift-report.md`, `check_features.py` (000010), `check_specify.py` (000011), `check_plan_scenarios.py` (000012)
- **Depends on**: Step 4
- **Interface**: `load_matrix(root: Path, slug: str, *, plan: Path | None = None, moment: str = "M2", status_fn: Callable[[Path, str], str] | None = None, run_fn: Callable[..., dict] | None = None) -> dict`; `class DriftInputError(Exception)`; as funções de execução externa são injetáveis para os testes não dependerem dos três scripts.
- **Verify**: `pytest ... -k "load or stale or sem or corrompida or nao_aplicavel"` verde sobre as árvores do Step 3; `ruff` e `pyright` limpos; um teste de integração opcional (marcado, pulado quando os scripts dos 000010 a 000012 não existem) roda os três scripts reais sobre a árvore `ok-m1` e coincide com o `esperado.json`; `git grep -n "shell=True"` no arquivo devolve zero.
- **Tests**: when `status.txt` diz `stale` e o frontmatter diz `scenarios: approved`, returns D1 `NM-CENARIOS-STALE` e consultou o status (o stub registra a chamada); when `check_specify.py` não existe, returns D1 com a ressalva "aprovação não verificada" e não `approved` silencioso; when o relatório do runner não existe, returns D2 `NM-SEM-RUNNER` e nenhum erro; when o `gate.json` é JSON inválido, returns `DriftInputError` com o caminho do arquivo e a CLI sai 2; when o projeto não tem `features/`, returns `nao_aplicavel` sem tocar em disco além de `os.path.isdir`; when o plano é v1, returns `nao_aplicavel` e nenhuma outra fonte é lida; when um teste tem `req` mas o cenário não existe mais, returns o teste como órfão fora de qualquer D.
- **Docs**: tabela fonte → coluna → razão no cabeçalho do módulo.
- [ ] Done

### Step 6: Instantâneos M1/M2, delta, auditoria semântica e CLI
Acrescentar: (a) `freeze(report, root, slug, moment, at)` que escreve `features/<slug>/drift/M1.json` (ou `M2-<data>.json`; Decisão pendente 1) por escrita atômica, **recusando sobrescrever um M1 existente** (exit 2 com mensagem; M1 é congelado); (b) `compare(m1, m2) -> delta`: por degrau, numerador e denominador dos dois lados e a diferença de `D` só quando os dois são numéricos; `NM-SEM-M1` quando não há instantâneo; denominador diferente é anotado ("o denominador mudou de X para Y"); entradas com hash diferente do M1 listadas (quais arquivos mudaram depois da entrega); (c) auditoria: `read_audit(path) -> dict` (valida `adequado`, rejeita valor fora do conjunto com `DriftInputError`), `audit_sample(reqs, slug, pct=30) -> list` determinística (hash, não aleatória), e a coluna `auditoria` no relatório (contagens sim/parcial/não e REQs ainda não auditados), nunca alterando `D`; (d) CLI `drift_report.py [raiz] --feature <slug> [--plan <plano.md>] [--moment M1|M2] [--freeze] [--compare] [--audit-sample] [--json] [--md] [--html] [--out <dir>] [--at <UTC ISO>]`; sem `--feature`, descobrir as features de `features/` em ordem alfabética e reportar cada uma; exit 0 com relatório produzido, 2 em erro de argumento/leitura; stdout recebe o relatório, stderr os diagnósticos (standards.md § Backend 8).
- **Files**: open-seja/.claude/skills/scripts/drift_report.py (modify), open-seja/.claude/skills/scripts/tests/test_drift_report.py (modify)
- **References**: `.claude/references/general/drift-report.md`
- **Depends on**: Step 5
- **Interface**: `freeze(...) -> Path`; `compare(m1: dict | None, m2: dict) -> dict`; `read_audit(path: Path) -> dict`; `audit_sample(reqs: list[str], slug: str, pct: int = 30) -> list[str]`; `main(argv) -> int`; flags acima.
- **Verify**: `pytest ... -k "freeze or compare or audit or cli"` verde; `ruff` e `pyright` limpos; rodar a CLI duas vezes sobre `ok-m2-deriva` e comparar `--json` com `diff` (idêntico); `--freeze` duas vezes na mesma feature recusa na segunda e deixa o arquivo intacto (hash antes e depois igual).
- **Tests**: when `--freeze` roda e já existe `M1.json`, returns exit 2 e o arquivo não muda; when M2 tem 12 REQs e M1 tinha 10, returns o delta com "o denominador mudou de 10 para 12" e a diferença de D calculada sobre os dois lados; when não há `M1.json`, returns `NM-SEM-M1` e nenhum delta numérico; when `audit.json` traz `adequado: "talvez"`, returns exit 2 com o REQ citado; when 10 REQs são listados, `audit_sample` returns 3 REQs, sempre os mesmos para o mesmo slug, e não altera nenhum D; when `--feature` é omitido e `features/` tem duas pastas, returns dois relatórios em ordem alfabética.
- **Docs**: `--help` do CLI com um exemplo por flag.
- [ ] Done

### Step 7: Renderizadores Markdown (voz controlada, não prescritivo) e HTML opcional
Implementar `render_markdown(report, *, lang="pt-BR") -> str` por modelo de frase fixa (nada de LLM): título `## Divergência por degrau (<feature>, <momento>)`; uma tabela por momento com colunas `Degrau | n | Cobertos | Descobertos | Não medido (razão) | D | M1 | M2 | Mudança`; frase de destaque ("O maior D está em D2: 3 de 12 cenários sem teste executado") ou "Empate entre D2 e D3a"; lista curta das leituras fora do D; ressalvas; coluna `Auditoria` à parte, com a frase "A auditoria não entra no D"; linha final "Medido em <M1 data> e <M2 data>. Fontes: <arquivos>". Todas as frases em tempo presente descritivo ou passado, <= 25 palavras, sem "deveria", "considere", "recomendamos", "você deve". `render_html(report) -> str` (autocontido, sem rede) **só se** o gerador do 000074 existe (Step 1): barra horizontal por degrau com o numerador/denominador no texto (a cor não é o único canal), seções recolhíveis por degrau; senão `render_html` levanta `HtmlUnavailable` e a CLI escreve "HTML: não gerado (gerador não instalado)" em stderr e segue (Decisão pendente 3, default B). Texto "não aplicável" de uma linha para os casos de compatibilidade.
- **Files**: open-seja/.claude/skills/scripts/drift_report.py (modify), open-seja/.claude/skills/scripts/tests/test_drift_report.py (modify)
- **References**: `.claude/references/general/drift-report.md`, `.claude/references/general/controlled-language.md` (000074, se existir), `.claude/skills/reflect/SKILL.md` § Strictly non-prescriptive rule
- **Depends on**: Step 6
- **Interface**: `render_markdown(report: dict, *, lang: str = "pt-BR") -> str`; `render_html(report: dict) -> str` (pode levantar `HtmlUnavailable`); constante `FORBIDDEN_PHRASES`.
- **Verify**: `pytest ... -k "render"` verde; o Markdown de cada fixture, passado ao `lint_controlled_language.py` quando existe, sai sem aviso de frase longa (senão o teste aplica o limite de 25 palavras por contagem própria e registra `voz: não verificada pelo lint`); nenhum item de `FORBIDDEN_PHRASES` aparece em nenhuma saída; o relatório do caso `ok-m2-deriva` lido em voz alta cabe em uma tela (<= 40 linhas, registrar a contagem).
- **Tests**: when o relatório tem `não medido` em um degrau, returns a razão escrita na mesma linha da tabela; when todos os D são "n/a", returns a tabela sem destaque de degrau e a frase "Nenhum degrau tinha itens para medir"; when qualquer relatório é renderizado, returns um texto sem nenhuma das frases proibidas e com a frase "A auditoria não entra no D" quando há auditoria; when o projeto é `nao_aplicavel`, returns exatamente uma linha; when o gerador de HTML não existe e `--html` é pedido, returns exit 0, o Markdown é escrito e a mensagem sai em stderr.
- **Docs**: exemplo do relatório renderizado em `drift-report.md` (copiar a saída do caso `ok-m2-deriva`).
- [ ] Done

### Step 8: Integração mínima em `/reflect` e `/explain drift`
Mudanças pequenas, só prosa de skill, **sem alterar o que as skills fazem para quem não tem `features/`**. (a) `reflect/SKILL.md`, fluxo conversacional, depois do Step B (resumo) e antes do Step C: "Se algum artefato escolhido é um plano com `Feature: <slug>` no cabeçalho, rodar `python .claude/skills/scripts/drift_report.py --feature <slug> --plan <plano> --moment M2 --compare --md` e apresentar a saída; se o M1 não existe, a saída diz isso e o `/reflect` segue." No Step D, acrescentar à estrutura do arquivo a seção `## Divergência por degrau` (a saída do script, verbatim) entre `## Summary` e `## Reflection`, **omitida** quando não há `Feature:`. Se `audit_sample` retornar REQs sem auditoria, o `/reflect` apresenta a lista ao designer e registra a resposta em `audit.json` **só com a palavra dele** (verbatim em `nota`). Os modos `--deep` e `--telemetry` e o formato do cabeçalho `# Reflection <id> | ...` não mudam. (b) `explain/SKILL.md`: na tabela de argumentos, `drift [scope]` ganha o escopo `ladder [<slug>]`; na tabela de despacho, sem linha nova. (c) `_internal/explain/drift/SKILL.md`: novo passo A.2b (somente se `features/` existe e o escopo é `all` ou `ladder`, Decisão pendente 4 default B): rodar o script com `--moment M2 --compare --md`, incluir a saída como seção `## Divergência por degrau` do relatório de deriva, e **não** acrescentar nada à tabela `Drift Summary` nem aos prompts do Step B (sync) ou do `--promote`. Registrar no progress o texto sugerido (**não aplicado**) para o `/implement` chamar `--freeze` ao fim (Decisão pendente 2, default A): é do item 7 ou 9.
- **Files**: open-seja/.claude/skills/reflect/SKILL.md (modify), open-seja/.claude/skills/explain/SKILL.md (modify), open-seja/.claude/skills/_internal/explain/drift/SKILL.md (modify)
- **References**: `.claude/references/general/drift-report.md`, `.claude/skills/reflect/SKILL.md`, `.claude/skills/explain/SKILL.md`
- **Depends on**: Step 7
- **Interface**: escopo `ladder [<slug>]` de `/explain drift`; seção `## Divergência por degrau` em reflexões e relatórios de deriva.
- **Verify**: `git diff --stat` mostra só os três `SKILL.md` com poucas linhas cada (registrar o total; alvo <= 40 linhas somadas) e nenhuma linha removida de `--deep`, `--telemetry`, `--promote` nem do cabeçalho `# Reflection`; `python .claude/skills/scripts/check_skill_spec.py` e `check_skill_system.py` iguais ao baseline do Step 1; `run_all_checks.py` sem falha nova; o teste existente `test_generate_reflection_report.py` (regra não prescritiva) continua verde.
- **Tests**: when a skill `reflect` é lida por `check_skill_spec.py` depois da mudança, returns o mesmo resultado do baseline; when um teste de texto procura `Divergência por degrau` em cada `SKILL.md` modificado, returns que a seção está condicionada a `Feature:` (reflect) ou a `features/` (explain drift).
- **Docs**: o quickguide pt-BR e `/help` são do item 9; aqui só o texto dos `SKILL.md`.
- [ ] Done

### Step 9: Ensaio ponta a ponta, compatibilidade, C1 e fechamento
Sobre uma feature fictícia descartável (sem parceiro): rodar `--freeze` no estado "fim do IMPLEMENT" (M1), alterar um `.feature` e quebrar um teste, rodar M2 com `--compare`, e simular `/reflect` e `/explain drift --scope ladder` lendo a saída; registrar no progress a saída, o que o agente fez de errado ao seguir o texto dos `SKILL.md` e o tempo. Rodar os **quatro casos de compatibilidade**: projeto sem `features/`, plano v1, `Specify: skipped`, e projeto com `features/` mas sem M1: nenhum quebra, nenhum acrescenta seção ao relatório de deriva existente (comparar com a saída do baseline). Rodar `run_all_checks.py` e `/critique validate` nos arquivos novos; conferir que nomes de degrau, razões `NM-*` e colunas coincidem entre `drift-metric.md`, `drift-report.md`, fixtures e o 000008; `git grep -i` dos termos de C1 sobre o diff. Registrar no progress `_output/plans/plan-000014-progress.md` (Doutourado): resultado dos checks, tabela de recontagem do Step 3, as lacunas e quais decisões pendentes ainda estão no default, a divergência (se houver) entre o esquema do `casos.json` e o relatório, e o texto sugerido para o item 7/9 (chamar `--freeze`; produzir registro "vermelho pelo motivo certo", cobertura por cenário e referência-base do diff nos caminhos que `drift-report.md` fixou).
- **Files**: `_output/plans/plan-000014-progress.md` (create no Doutourado), open-seja/tests/fixtures/drift_report/ (read), open-seja/.claude/skills/scripts/run_all_checks.py (read)
- **References**: product-design/constitution.md
- **Depends on**: Step 8
- **Interface**: N/A
- **Verify**: `pytest .claude/skills/scripts/tests/test_drift_report.py` todo verde e os seis golden do 000008 passam; `run_all_checks.py` mostra o mesmo conjunto de falhas pré-existentes do baseline; os quatro casos de compatibilidade têm saída vazia ou de uma linha e exit 0; `git grep -n "D3a"` aparece em `drift-metric.md`, `drift-report.md`, no script e nas fixtures; zero termos de C1; `git -C open-seja status` só com os arquivos previstos; progress lista as pendências.
- **Tests**: N/A (ensaio e verificação; os testes automáticos são dos Steps 3 a 8)
- [ ] Done

## Coverage (advisory)

`product-design/product-design-as-intended.md` do Doutourado não tem marcadores REQ; `critique_plan_coverage.py` não se aplica e `Traces:` fica ausente.

## Lacunas e conflitos com os planos 000007 a 000012

1. **Item 7 roda na mesma Wave e nenhum plano fixa as fontes do D3.** O 000008 diz que o item 7 escreve o relatório do runner, o `gate.json` e o registro "vermelho pelo motivo certo", mas só o relatório do runner tem contrato (000010, Step 8). Não há plano com: nome e esquema do registro de "vermelho pelo motivo certo"; cobertura **só dos testes de cenário** (base do D3b, que o 000008 exige "por linha/ramo tocado"); referência-base do diff da feature (de onde o "tocado" sai); campos de `gate.json` por cenário. Este plano lê esses arquivos de caminhos fixados em `drift-report.md` e trata ausência como `não medido`; **item 7 deve produzi-los (ou o designer emenda)**. Até lá, D3b sai `não medido` e D3a com ressalva. Depende também de a chave `<slug>/<arquivo>::<nome>` estar no relatório (000010, lacuna 5).
2. **Quem congela o M1.** O 000008 diz "M1 = matriz congelada com o gate", mas nem ele nem o 000007 dizem quem executa nem onde guarda. Este plano entrega `--freeze` e a regra de recusa de sobrescrita (Decisão pendente 2); a chamada no `/implement` é do item 7 ou 9. Aditivo ao layout `features/<slug>/{intent.md,*.feature,gate.json}` do 000007 e ao `scenarios.lock.json` do 000011: `features/<slug>/drift/` (Decisão pendente 1), emenda via designer.
3. **Emenda do 000011 (lacunas 1 e 4) para o item 8.** O 000011 pede que o item 8 consulte `check_specify.py --status`; este plano o faz (decisão fechada 3). Isso também fecha a lacuna 4 do 000011 (campo `scenarios: approved` desatualizado quando a grill reabre), **para o relatório**; o campo no disco continua mentindo até o item 9 decidir se a grill escreve `stale`.
4. **Esquema do `casos.json` (000008, Step 3) ainda não existe.** O 000008 define `entrada` como "tabela de rastreabilidade mais colunas derivadas" e `esperado` como o relatório do Step 2 do 000008. Se o formato final divergir do `compute_report`, o Step 1/9 registra a diferença e **não** edita o `casos.json` (propriedade do 000008): ajusta-se um adaptador fino no teste.
5. **Matriz cenário→step (000012) não é degrau.** O 000012 expõe a matriz cenário→step (cobertura nos dois sentidos, `PFS-009`), mas o 000007/000008 só têm quatro degraus. Aqui a coluna "step dono" é informativa e fica fora do vetor; se o designer quiser um degrau "cenário→step" é emenda ao 000008.
6. **`/reflect` não prescritivo vs. destaque do degrau de maior D.** Resolvido com frase descritiva ("O maior D está em ..."); coberto por teste de frases proibidas.
7. **Pontos de contato nos mesmos `SKILL.md`.** Os 000007, 000009 e 000011 tocam `plan/SKILL.md` e `_internal/plan/standard/SKILL.md`; este plano toca `reflect`, `explain` e `_internal/explain/drift`. Se o 000007 (Step 5) também edita `reflect`/`explain`, o Step 1 lê o texto atual antes de editar.
8. **Dependência do 000074 (voz e HTML).** O lint de linguagem controlada e o gerador HTML podem não existir no open-seja; tratado por degradação (Decisão pendente 3; limite de 25 palavras por contagem própria).
9. **Condição de refutação do 000007 usa `D_B >= D_A` e O1.** O cálculo de O1 e do retrofit do braço A é do protocolo de controle (000008, Step 4) e do item 10; este plano só lê um `oracle-result.json` opcional para a leitura de alerta e não calcula O1 sozinho.
10. **Denominador variável entre M1 e M2.** Não há regra no 000008 para a comparação quando REQs entram ou saem; este plano mostra os dois lados e anota a mudança (Step 6). Se o designer preferir fixar o denominador do M1, é emenda ao 000008.

## Metacomm Intention
- **Summary**: I tell you that when you reflect on a feature, I show where its intent got lost, one step of the ladder at a time, with what I could not measure and what changed after delivery, and that I only describe what happened.
- **Source**: agent (technical plan; metacomm text kept for the report to the designer)

## Review log

**Review depth:** Standard (9 steps; ~9 arquivos distintos). Phase 1 inline (sem subagente; mesmo critério dos planos 000008 a 000012); sem Phase 2 (nenhum Deferred com risco de regressão). Prefixo FEATURE-O: usei DX, TEST, DATA, COMPAT, SEC, ARCH.

### Step metadata validation
- Todo step tem Files, References, Interface, Verify, Tests, checkbox; `Tests:` não-N/A em comportamento observável ("when X, returns Y"); `Tests: N/A` só nos Steps 1, 2, 9 (estado, documento, ensaio). Nenhum step toca mais de 5 arquivos (Step 3 conta a árvore de fixtures como um). Dependências só avançam. Caminhos do open-seja não verificados (submodule vazio): Step 1 é o portão.

### Phase 1 -- Perspective scan

| Perspective | Status | Concern |
|---|---|---|
| DX | Adopted | Relatório de uma tela por feature, campos fixos; cada step com Verify por comando; CLI com flags documentadas. |
| TEST | Adopted | Golden do 000008 + fixtures de árvore antes do código; carregador com funções externas injetáveis; teste de determinismo e de frases proibidas. |
| DATA | Adopted | `não medido` fora do denominador com razão; denominador zero = "n/a"; contagens inteiras; hashes das entradas no instantâneo; M1 imutável. |
| COMPAT | Adopted | Plano v1, sem `features/`, `Specify: skipped` e sem M1 degradam sem erro; `/reflect --deep/--telemetry`, `--promote` e cabeçalho `# Reflection` intactos; sem mudança em gate, hooks, layout. |
| SEC | Adopted | `subprocess` com lista de argumentos e sem shell; leitura só de arquivos da feature; escrita só em `features/<slug>/drift/`; C1 verificado por `git grep` nos Steps 2, 3, 9; fixtures fictícias. |
| ARCH | Adopted | Carregar, calcular e renderizar separados; casos golden exercitam o calculador sem I/O; relatório não bloqueia; item 7 produz as fontes. Step 7 concentra dois renderizadores: aceito. |
| PERF, DB, API, I18N, UX, A11Y, VIS, RESP, OPS, MICRO | N/A | Sem superfície relevante (script local, textos pt-BR de modelo fixo; a barra HTML repete o número no texto). |

### Riscos e lacunas registrados
- Fontes do D3 (registro de vermelho, cobertura por cenário, base do diff) dependem do item 7 (mesma Wave): D3b pode sair `não medido` no primeiro piloto.
- Esquema do `casos.json` do 000008 ainda não existe: possível adaptador fino.
- Texto de `SKILL.md` pode ter mudado no open-seja (v0.10.x): Step 1 lê antes de editar.

### Execution Metrics
| Metric | Value |
|---|---|
| Review depth | Standard |
| Phase 1 perspectives | 6 adopted, 10 N/A |
| Phase 2 deep-dives | 0 |
| Iterations | 0 |
| Pending decisions | 6 (defaults A, A, B, B, A, A) |

## Outcomes

- `drift_report.py`: carregador, calculador puro (vetor `D1, D2, D3a, D3b`, sem LLM), instantâneos M1/M2 com delta, auditoria semântica à parte, CLI e renderizadores (Markdown obrigatório, HTML opcional).
- `drift-report.md` (`DRP-NNN`): entradas, razões de "não medido", consulta obrigatória a `--status`, formato do relatório e regra não prescritiva.
- Os seis casos golden do 000008 e as fixtures de árvore como testes automáticos; determinismo e compatibilidade cobertos.
- Seção `## Divergência por degrau` em `/reflect` (quando o plano tem `Feature:`) e escopo `ladder` em `/explain drift`; nada muda sem `features/`.
- Lista de lacunas contra os planos 000007 a 000012 e texto sugerido para os itens 7 e 9.

smoke: false
