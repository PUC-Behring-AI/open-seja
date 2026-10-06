# Plan 000008 | FEATURE-O | 2026-10-05 02:05 UTC | drift-metric: divergência por degrau e controle com o ciclo padrão | Review: standard

> **Origem**: movido do ledger do Doutourado em 2026-10-05 (proposal-000088; la era `plan-000077`). Os IDs roadmap-000006 e plan-000007..000016 sao deste ledger (tabela no roadmap). Referencias a research-NNNNNN, reflection-NNNNNN, communication-NNNNNN, roadmap-000062 e plan-000064..000074 apontam para o ledger do Doutourado (repositorio do pesquisador). Caminhos `open-seja/...` em Files passam a ser relativos a raiz deste repositorio.
plan_format_version: 1

> Item 2 do roadmap-000006 (Wave 0, "Depends on: nenhum"). Repositório de execução: **open-seja** (worktree/branch por plano); o plano vive no Doutourado. C1: nenhum nome de parceiro nos artefatos que forem ao open-seja. Consistente com o plano 000007 (contrato do item 1): usa o vocabulário `CYC-NNN`, o layout `features/<slug>/`, as tags `@REQ-<slug>-NNN`, `plan_format_version: 2` no open-seja e os estados coberto/descoberto/não medido. Não reabre nenhuma decisão do 000007.

## User brief

> Item 2 do roadmap-000006: `drift-metric` (Depends on: nenhum). "Definição operacional de divergência **por degrau** (intenção→cenário, cenário→teste, teste→código) e desenho do controle com o ciclo padrão".

## Agent interpretation

**Problem.** H-009 diz que a escada de representações reduz a divergência *as-coded* vs *as-intended*, "medida por degrau". O plano 000007 fixou só o vocabulário e a unidade (degrau, par de artefatos, três estados). Sem uma definição operacional (o que se conta, de onde vem o dado, como se calcula, contra o quê se compara), os itens 8 (relatório) e 10 (piloto) não têm o que implementar nem o que refutar.

**Approach.** Plano **técnico de definição** (sem runner, validador nem relatório executável: isso é dos itens 4, 7 e 8). Produz no open-seja dois documentos normativos e fixtures de referência:
1. `drift-metric.md`: por degrau, o que é medido, a fonte (matriz intenção-cenário-teste-código-gate), o cálculo (determinístico, sem LLM), e o formato do relatório (**vetor por degrau, nunca número único**).
2. `drift-control-protocol.md`: o desenho do controle (mesma feature no ciclo padrão PLAN→IMPLEMENT→REFLECT vs ciclo estendido), com **oráculo de intenção independente**, ordem dos braços, réplicas, covariáveis, tempo até a primeira feature aprovada e ameaças à validade.
3. Fixtures *golden* (matriz de entrada + relatório esperado) que o item 8 deve reproduzir.

**Alternatives rejected.**
- Número único (média ponderada dos degraus): esconde em que degrau a intenção se perde, e o peso é arbitrário. Rejeitado também pelo 000007 (Decisão pendente 4, opção C).
- Só cenários verdes (opção A do roadmap): um cenário verde que não cobre o REQ passa como "sem divergência".
- Medir o braço de controle só pelo seu próprio plano: o ciclo padrão não tem REQ nem cenário, então não há como medir degrau nele sem uma régua externa. Daí o oráculo independente.
- Implementar já a calculadora aqui: duplicaria o item 8. Aqui entram a definição e os dados de teste dela.

**Selection rationale.** Sem `source:`; o roadmap-000006 (item 2, tabela "Decisões", H-009) e o plano 000007 são as fontes. research-000050 §1.2 e §10 entram só como ressalva: o gate (CRAP, mutação, "PASS is a tool result") é a fonte do degrau teste→código, e o limiar do gate não é redefinido aqui.

### Decisões fechadas (não reabrir neste plano)

1. **Composta, reportada por degrau.** O relatório é um vetor `(D1, D2, D3a, D3b)` mais `n` e `não medido` de cada um. Não há número único nem pesos. Um "degrau de maior divergência" pode ser destacado por texto, nunca somado.
2. **Unidade por degrau** (a unidade é o item do degrau de cima, o que se pergunta é se o degrau de baixo o cobre):
   - D1 intenção→cenário: unidade = REQ (`REQ-<slug>-NNN` de `intent.md`).
   - D2 cenário→teste: unidade = cenário (`Scenario` em `*.feature` com tag `@REQ-...`).
   - D3 teste→código: duas medidas separadas. **D3a** (teste verde no código final e gate PASS, por cenário) e **D3b** (código tocado que nenhum teste de cenário exercita, por linha/ramo tocado).
3. **Estados** (vocabulário do 000007): `coberto`, `descoberto`, `não medido`. Fórmula do degrau: `D = descobertos / (cobertos + descobertos)`. **`não medido` fica fora do denominador e sempre aparece ao lado** (nunca é tratado como coberto nem como descoberto). Denominador zero = `D` indefinido, escrito "n/a", nunca 0.
4. **Cálculo determinístico.** Nenhum LLM entra no cálculo de D1 a D3b. Julgamento semântico (o cenário captura o REQ?) é uma **auditoria à parte**, reportada como coluna própria (ver Decisão pendente 1), nunca misturada ao D.
5. **Três momentos de medição**: M1 = fim do IMPLEMENT (matriz congelada com o gate), M2 = REFLECT (mesma fórmula, matriz regenerada; a diferença M2 - M1 é a deriva depois da entrega). Sem M0 (aprovação do plano): o D1 e o D2 em M0 já são exigidos como portão pelo contrato (000007), não medem divergência.
6. **Controle com oráculo independente**: o designer escreve, antes de qualquer braço rodar, a lista de REQs e os cenários de aceitação da feature (o *oráculo*). Os dois braços são medidos contra o mesmo oráculo no fim (métrica comparável **O1**: fração de cenários do oráculo que falham no código final).
7. **Estudo de caso, não teste estatístico**: poucas features. Reportam-se todos os números brutos e as réplicas; sem p-valor e sem "significativo". Feature com menos de 8 REQs é marcada `amostra pequena`.
8. **Tempo até a primeira feature aprovada** é medida complementar do controle (H-009), em duas formas: relógio de parede e tempo atendido pelo designer.
9. Este plano não escreve em `product-design/` do Doutourado, não edita roadmap nem INDEX, não altera o gate, os hooks nem o contrato do 000007 (só, opcionalmente, uma linha de ponteiro no contrato, Step 6).

### Definição operacional por degrau (resumo; o texto normativo é o Step 2)

| Degrau | Mede | Fonte (matriz) | Coberto quando | Descoberto quando | Não medido quando |
|---|---|---|---|---|---|
| D1 intenção→cenário | REQs sem cenário | `intent.md` x `*.feature` | REQ aprovado tem >=1 cenário com `@REQ-<slug>-NNN` em `.feature` aprovado | REQ aprovado sem cenário com a tag | `intent.md` não aprovado, ou `Specify: skipped` (contrato 000007) |
| D2 cenário→teste | Cenários sem teste executável | `*.feature` x relatório do runner | cenário tem teste vinculado que foi **coletado e executado** (não `skip`/`xfail`) | sem teste vinculado, ou vinculado só como `skip`/`xfail` | runner de Gherkin indefinido para a stack (item 4) ou relatório ausente |
| D3a teste→código (verdade) | Cenários cujo teste não passa no código final | relatório do runner + `gate.json` | teste verde **e** `gate.json` com `full` PASS sem `--accept-baseline` | teste vermelho, ou gate FAIL, ou PASS só com baseline aceito | gate não rodou (sem `gate.json` no M1) |
| D3b teste→código (excesso) | Código tocado não exercitado por teste de cenário | cobertura por linha/ramo só dos testes vinculados a cenários x diff do feature | linha/ramo tocado exercitado por teste de cenário | tocado e não exercitado | cobertura por cenário indisponível |

Leituras adicionais, **fora do D** (relatadas como contagens): REQ com cadeia completa (cenário + teste + verde); cenário órfão (tag sem REQ ou REQ inexistente); cenário sem tag; "escada fechou sem capturar a intenção" (D1=D2=D3a=0 e O1 > 0 no controle ou na auditoria semântica).

### Desenho do controle (resumo; o texto normativo é o Step 4)

- **Braços.** A = ciclo padrão (SEJA v0.10.x: PLAN→IMPLEMENT→REFLECT sem grill/specify, plano v1, `Tests:` por step). B = ciclo estendido (grill→specify→plano v2→teste vermelho por cenário→código→gate). Mesmo brief textual, mesmo commit inicial, mesma versão de modelo e mesmo orçamento (iterações, tempo máximo), cada braço em worktree limpo.
- **Régua comum.** Oráculo do designer, escrito antes, não mostrado ao agente do braço A e não copiado para o B (o B produz os seus REQs e cenários pelo grill; o designer responde ao grill só com base no oráculo, sem informação nova). Métrica comparável entre braços: **O1** (cenários do oráculo que falham no código final) e **D3b** calculado contra os testes do oráculo.
- **Degraus nativos só no B.** O A não tem REQ nem cenário próprios: D1 e D2 do A são medidos por **retrofit** (mapear os REQs do oráculo para os critérios do plano v1 e aos testes do A; ver Decisão pendente 1). A assimetria é declarada como ameaça à validade.
- **Ordem e réplicas.** Ordem dos braços alternada entre features (efeito de aprendizado do designer); 1 feature = 1 ordem sorteada e registrada. Réplicas por braço: ver Decisão pendente 2.
- **Tempo.** `t0` = primeira mensagem com o brief; `t_verde` = primeiro `gate full` PASS; `t_aprovada` = aceitação explícita do designer (ver Decisão pendente 3). Tempo atendido = soma dos intervalos entre eventos do designer menores que 10 min.
- **Regra de comparação (leitura operacional da condição de refutação do 000007).** "Divergência igual ou maior no estendido em um degrau" = `D_B >= D_A` para o degrau, com **empate** quando a diferença for menor que 1 item do denominador (não conta como redução). Degraus comparáveis: D3a, D3b e O1 diretos; D1 e D2 só pelo retrofit.

### Decisões pendentes
Cada uma tem default (a recomendação). Se o designer não responder, os steps seguem o default; mudar uma altera só o Step indicado.

**Decisão pendente 1 -- Adequação semântica ("o cenário captura o REQ?") e retrofit do braço A** (afeta Steps 2, 4)
- Opção A: só mecânico (tag presente); sem auditoria semântica.
- Opção B: auditoria humana cega por amostra: todos os REQs do braço A (retrofit) e >=30% dos REQs do braço B, resultado em coluna `adequado: sim/parcial/não`, separada do D.
- Opção C: LLM-judge em contexto limpo para o retrofit do A e para a amostra do B, com amostra humana de >=20% para medir a concordância.
- **Recomendação: B.** Recommended when o piloto tem poucas features (item 10) e o custo humano cabe; evita um juiz LLM medindo um ciclo feito por LLM. NOT recommended when o número de REQs passa de ~40 por braço (então C com amostra humana). A rejeitada: o D1 mecânico não vê cenário que existe e não cobre.

**Decisão pendente 2 -- Réplicas por braço** (afeta Step 4)
- Opção A: 1 execução por braço.
- Opção B: 3 execuções por braço.
- Opção C: 5 execuções por braço.
- **Recomendação: B.** Recommended when a feature é pequena (<= 1 dia de agente) e a variância do agente importa mais que a do designer. NOT recommended when o custo de 6 execuções excede o orçamento do piloto (então A, declarando que a variância do agente não foi medida). Relatar as três, nunca a média sozinha.

**Decisão pendente 3 -- Definição de "feature aprovada" para o tempo** (afeta Steps 4, 5)
- Opção A: aceitação explícita do designer, registrada como linha no `/reflect` ou no progress file.
- Opção B: primeiro `gate full` PASS.
- Opção C: O1 = 0 (oráculo 100% verde).
- **Recomendação: A**, reportando `t_verde` (B) e `O1` ao lado. Recommended when H-009 fala em tempo até aprovada pelo designer. NOT recommended: B sozinho (o gate verde não diz que a intenção foi atendida), C sozinho (o oráculo é do designer, mas o ciclo padrão pode nunca chegar a 0).

**Decisão pendente 4 -- Colunas derivadas da matriz** (afeta Steps 2, 6; é uma lacuna com o 000007, ver "Lacunas")
- Opção A: emenda aditiva ao `feature-layout.md` do item 1 com colunas `scenario_status`, `test_result`, `red_reason_ok`, `touched_uncovered`.
- Opção B: o `drift-metric.md` define as colunas **derivadas** (calculadas no item 8 juntando `*.feature`, relatório do runner, `gate.json` e diff); o esquema do item 1 não muda.
- **Recomendação: B.** Recommended when o 000007 já está revisto e não se quer reabri-lo. NOT recommended when o item 8 descobrir que alguma coluna não é derivável (então A, como emenda registrada).

## Files

Todos no **open-seja**, exceto onde dito. O submodule não está inicializado neste worktree; caminhos **não verificados**: o Step 1 os confere antes de qualquer escrita.

- `.claude/references/general/drift-metric.md` (create) -- definição normativa por degrau
- `.claude/references/general/drift-control-protocol.md` (create) -- desenho do controle
- `.claude/references/template/pilot-run-record.md` (create) -- registro de uma execução (braço, ordem, timestamps, versões)
- `tests/fixtures/drift/casos.json` e `README.md` (ou caminho equivalente achado no Step 1) (create) -- matrizes e relatórios *golden*
- `.claude/references/general/extended-cycle-contract.md` (modify, opcional: só linha de ponteiro, se existir após o 000007)
- `_output/plans/plan-000008-progress.md` (create no Doutourado)

## Best practices

- "PASS is a tool result, not a sentence" (research-000050): cada D é um cálculo reproduzível sobre arquivos, nunca uma opinião de agente.
- Contar o que falta ao lado do que existe: `não medido` visível; nunca esconder lacuna em média.
- Régua independente (oráculo) para evitar o viés de que o ciclo estendido mede a si mesmo com os cenários que ele mesmo escreveu (lei de Goodhart).
- Reportar bruto: numerador, denominador, `n`; sem arredondar para "limpar" amostra pequena.
- Voz controlada nos textos que o citizen lê (relatório por degrau em frases curtas, termos fixos, plano 000074).

## Design decisions

- **User-visible impact:** quando você pedir o relatório de divergência, eu mostro três barras (intenção→cenário, cenário→teste, teste→código) com os números brutos e o que não foi medido, em vez de uma nota única. No piloto, eu rodo a mesma feature nos dois ciclos e comparo contra a sua régua.
- **Trade-offs accepted:** ganha-se visibilidade de onde a intenção se perde; perde-se a simplicidade de um número. O retrofit do braço A é trabalhoso e assimétrico (ameaça declarada). Poucas features: evidência de caso, não estatística.
- **Metacommunication impact:** I know a single score would be easier to read; therefore I show you each step of the ladder apart and tell you what I could not measure, so that you see where your intent got lost and you decide what to fix.

## Steps

### Step 1: Conferir o terreno e as fontes de dado no open-seja
Na tag/branch `dev` do open-seja (`git submodule update --init open-seja` se vazio), confirmar o estado do plano 000007 no open-seja: existem `extended-cycle-contract.md` (vocabulário `CYC-NNN`, definição dos degraus), `feature-layout.md` (esquema de `intent.md`, `@REQ-<slug>-NNN`, `gate.json`, tabela de rastreabilidade) e a H-009? Ler também a saída JSON do gate do plano 000065 (campos de cobertura por arquivo, CRAP, baseline, `--accept-baseline`), o relatório de testes do runner de Python em uso e os registros de tempo existentes (`_output/briefs.md`, `_output/telemetry.jsonl`; `conversation-trace.jsonl` não está neste worktree, o Step 5 depende da existência dele no open-seja). Registrar no progress: o que o 000007 já fixou (citar `CYC-NNN` reais), o que ainda é rascunho, quais campos do gate/cobertura existem e quais fontes de tempo existem. Se o 000007 ainda não está no open-seja, escrever os Steps 2 a 6 contra o vocabulário do plano 000007 (Doutourado) e marcar cada citação `CYC-NNN` como "a confirmar". Nada é escrito no open-seja.
- **Files**: open-seja/.claude/references/general/extended-cycle-contract.md (read, se existir), open-seja/.claude/references/template/feature-layout.md (read, se existir), open-seja/.claude/references/template/quality-gate/python/gate.py (read), open-seja/_output/briefs.md (read), open-seja/_output/telemetry.jsonl (read)
- **References**: product-design/conventions.md, product-design/constitution.md
- **Interface**: N/A
- **Verify**: o progress lista, para cada fonte da matriz (`intent.md`, `*.feature`, relatório do runner, `gate.json`, cobertura, diff), "existe/definido", "rascunho" ou "ausente" com o caminho; `git -C open-seja status` limpo.
- **Tests**: N/A (verificação de estado)
- [x] Done

### Step 2: Escrever a definição normativa por degrau (`drift-metric.md`)
Criar o documento com: (1) unidade, estados e fórmula (`D = descobertos / (cobertos + descobertos)`, `não medido` fora do denominador, denominador zero = "n/a"); (2) seção por degrau (D1, D2, D3a, D3b) com a tabela do plano (o que mede, fonte, coberto, descoberto, não medido), a coluna da matriz de onde vem cada dado e **quem a escreve e quando** (item 3/5: `intent.md`; item 4/5: `.feature`; item 7: teste, relatório e `gate.json`; item 8: junção); (3) as colunas **derivadas** (Decisão pendente 4, default B) com regra de derivação; (4) formato do relatório: tabela por degrau com `n`, `cobertos`, `descobertos`, `não medido`, `D`, e as leituras fora do D (cadeia completa, órfãos, cenário sem tag, "escada fechou sem capturar a intenção"); (5) momentos M1 e M2 e a regra de diferença; (6) tratamento de casos limite: `Specify: skipped`, tarefa sem código (sem pasta de feature, relatório "não aplicável"), feature com <8 REQs (`amostra pequena`), REQ removido depois da aprovação (conta como descoberto até `intent.md` ser reaprovado), cenário com múltiplas tags, `xfail`/`skip`; (7) a regra anti-gaming: D3a só vale se o gate rodou sem `--accept-baseline` e o teste foi vermelho pelo motivo certo no registro do item 7 (se o registro não existe, o estado é `não medido` para essa evidência, e a leitura aparece como ressalva); (8) a auditoria semântica como coluna separada (Decisão pendente 1). Citar `CYC-NNN` do 000007 (ou "a confirmar" conforme o Step 1). Texto de relatório em voz controlada (frases curtas).
- **Files**: open-seja/.claude/references/general/drift-metric.md (create)
- **References**: product-design/constitution.md, product-design/standards.md § Testing
- **Depends on**: Step 1
- **Interface**: contrato de dados do relatório: `{feature, momento, degraus: {D1|D2|D3a|D3b: {n, cobertos, descobertos, nao_medidos, D}}, leituras: {...}, ressalvas: [...]}`
- **Verify**: o arquivo existe; cada um dos 4 degraus tem as linhas "mede", "fonte", "coberto", "descoberto", "não medido", "escrito por"; contém a fórmula e a regra de denominador zero; `git grep -ci` dos termos de C1 (lista do Step 1) devolve zero; `python .claude/skills/scripts/run_all_checks.py` igual ao baseline do Step 1.
- **Tests**: N/A (documento normativo; os dados de teste são o Step 3)
- **Docs**: o próprio documento; o quickguide pt-BR é do item 9.
- [x] Done

### Step 3: Criar fixtures golden da matriz e do relatório esperado
Criar, no caminho de fixtures do Step 1, matrizes de entrada (JSON) para uma feature fictícia (sem parceiro e sem dado real) e o relatório esperado de cada uma, calculado à mão pela fórmula do Step 2: (a) **normal**: 10 REQs, 12 cenários, mistura de cobertos/descobertos nos três degraus; (b) **nada medido**: sem `gate.json`, D3a e D3b todos `não medido` e D "n/a"; (c) **specify pulado**: D1 `não medido`, relatório "não aplicável"; (d) **órfão e sem tag**: um cenário sem tag e uma tag sem REQ, contados fora do D; (e) **escada fechada, intenção não capturada**: D1=D2=D3a=0 e O1>0 no oráculo, dispara a leitura de alerta; (f) **amostra pequena**: 5 REQs, marcada. Cada fixture traz numerador e denominador por degrau. Estes arquivos são o contrato de teste que o item 8 deve reproduzir.
- **Files**: <fixtures>/drift/casos.json (create; um arquivo com os seis casos, cada um com `entrada` e `esperado`), <fixtures>/drift/README.md (create)
- **References**: `.claude/references/general/drift-metric.md`
- **Depends on**: Step 2
- **Interface**: esquema de entrada = tabela de rastreabilidade do item 1 (colunas REQ, cenário, teste, código, gate) mais as colunas derivadas do Step 2; esquema de saída = o do Step 2.
- **Verify**: para cada fixture, recontar numerador e denominador por degrau com uma contagem independente dos estados da matriz de entrada (por exemplo `python -c` que lê o JSON e conta `cobertos`/`descobertos`/`nao_medidos`) e comparar com o `esperado` do mesmo caso; todas as seis coincidem; nenhum termo de C1 no diff.
- **Tests**: when a matriz-normal é lida e D1 é calculado, returns `descobertos/(cobertos+descobertos)` igual ao esperado; when não há `gate.json`, D3a e D3b returns `nao_medidos = n` e `D = "n/a"`; when um cenário não tem tag, aparece em `leituras.sem_tag` e não altera nenhum D. A execução automática desses testes é do item 8; aqui a verificação é a recontagem independente descrita em Verify.
- **Docs**: um `README` de uma linha por fixture no mesmo diretório.
- [ ] Done

### Step 4: Escrever o desenho do controle (`drift-control-protocol.md`)
Criar o protocolo com: (1) objetivo e a pergunta (H-009: o ciclo estendido reduz a divergência por degrau vs o ciclo padrão, com tempo até a primeira feature aprovada como medida complementar); (2) os dois braços e o que é fixado igual (brief textual, commit inicial, versão de modelo, orçamento de iterações e de tempo, worktree limpo, mesma versão do harness para A, v0.10.x pinada); (3) o **oráculo**: formato (lista de REQs e cenários Gherkin escritos pelo designer antes), regras de sigilo (não entra no contexto do agente do A; no B o designer responde ao grill só a partir do oráculo), versionamento do oráculo (congelado no commit, hash registrado); (4) métrica comparável O1 e D3b contra os testes do oráculo; retrofit do braço A para D1 e D2 conforme Decisão pendente 1; (5) ordem dos braços alternada e registrada, número de réplicas (Decisão pendente 2); (6) tempo: eventos `t0`, `t_verde`, `t_aprovada`, tempo atendido, fontes e a regra de 10 min (Decisão pendente 3); (7) a **regra de comparação** (`D_B >= D_A`, empate por <1 item, degraus diretos e por retrofit) e a tabela de resultados a preencher; (8) covariáveis a registrar: nº de iterações até PASS, nº de perguntas do grill, linhas de código, nº de REQs; (9) ameaças à validade e mitigação: efeito de aprendizado do designer, assimetria do retrofit, escopo de uma feature, viés de oráculo escrito pelo mesmo designer, variância do agente, Goodhart (cenários fracos). (10) critérios de parada e o que **não** concluir (sem generalizar de uma feature; sem p-valor).
- **Files**: open-seja/.claude/references/general/drift-control-protocol.md (create)
- **References**: product-design/constitution.md
- **Depends on**: Step 2
- **Interface**: N/A
- **Verify**: o arquivo existe com as 10 seções numeradas; a regra de comparação cita os mesmos nomes de degrau do `drift-metric.md` (`grep -c "D1\|D2\|D3a\|D3b"` em ambos >= 4); tabela de resultados tem uma linha por degrau mais O1 e tempo; nenhum termo de C1; `run_all_checks.py` igual ao baseline.
- **Tests**: N/A (protocolo documental)
- **Docs**: o próprio documento.
- [ ] Done

### Step 5: Template de registro de execução e captura do tempo
Criar `pilot-run-record.md` (template): feature, braço (A/B), ordem sorteada, réplica, commit inicial, versão do harness e do modelo, hash do oráculo, `t0`, `t_verde`, `t_aprovada`, tempo atendido, nº de iterações até PASS, nº de perguntas do grill, caminho da matriz M1 e M2, relatório de D por degrau, O1, notas do designer (verbatim). No `drift-control-protocol.md`, a seção de tempo aponta de onde sai cada timestamp (conforme o que o Step 1 achou: `briefs.md`, `telemetry.jsonl`, `conversation-trace.jsonl` e `gate.json`.ts). Se a fonte de `t_aprovada` não existir no open-seja, a linha de aceitação do designer vira campo do registro e fica declarado que o tempo atendido dessa execução é calculado a partir de `t0` e `t_aprovada` apenas.
- **Files**: open-seja/.claude/references/template/pilot-run-record.md (create), open-seja/.claude/references/general/drift-control-protocol.md (modify)
- **References**: product-design/constitution.md
- **Depends on**: Step 4
- **Interface**: campos do registro de execução (lista no próprio template)
- **Verify**: o template tem todos os campos acima; cada timestamp do protocolo tem a fonte ou "campo manual" ao lado; um registro de exemplo preenchido com dados fictícios existe e seu tempo atendido recalcula pela regra de 10 min (conta feita à mão no progress).
- **Tests**: N/A (template documental)
- **Docs**: o próprio template.
- [ ] Done

### Step 6: Costura com os itens vizinhos e lacunas com o 000007
Em `drift-metric.md`, acrescentar a tabela "quem alimenta e quem consome": item 3/5 (escreve `intent.md` e REQ IDs), 4/5 (`.feature` e validador de tags), 6 (campo `Scenarios:`), 7 (relatório do runner, `gate.json`, registro "vermelho pelo motivo certo"), 8 (calcula o relatório), 9 (quickguide), 10 (executa o protocolo). Listar as **lacunas** achadas contra o 000007 (as da seção "Lacunas" deste plano) com o item dono de cada uma. Se `extended-cycle-contract.md` existir (Step 1), acrescentar nele **só uma linha de ponteiro** (`Medida: ver drift-metric.md`); se não existir, registrar a linha no progress para o orquestrador. Não editar o esquema do `feature-layout.md` (Decisão pendente 4, default B).
- **Files**: open-seja/.claude/references/general/drift-metric.md (modify), open-seja/.claude/references/general/extended-cycle-contract.md (modify, só ponteiro, se existir)
- **References**: product-design/constitution.md
- **Depends on**: Step 2, Step 4
- **Interface**: N/A
- **Verify**: a tabela cobre os itens 3 a 10; `git diff --stat` do contrato mostra no máximo uma linha adicionada; o diff não toca `gate`, hooks, `settings` nem `feature-layout.md`.
- **Tests**: N/A (costura documental)
- [ ] Done

### Step 7: Fechar: consistência, C1 e decisões pendentes
Rodar `run_all_checks.py` e `/critique validate` nos arquivos novos; conferir que os nomes de degrau, estados e tags batem entre `drift-metric.md`, `drift-control-protocol.md`, fixtures e o plano 000007; conferir C1 (`git grep -i` dos termos do Step 1 sobre o diff). Registrar no progress `_output/plans/plan-000008-progress.md` (Doutourado): resultado dos checks, a tabela de recontagem do Step 3, as lacunas e quais decisões pendentes ainda estão no default, e o texto sugerido (para o designer colar via `/implement --manual`) de **uma frase** a acrescentar à medida de H-009 e à regra de comparação, sem editar prosa Human.
- **Files**: open-seja/.claude/references/general/drift-metric.md (read), open-seja/.claude/references/general/drift-control-protocol.md (read), `_output/plans/plan-000008-progress.md` (create no Doutourado)
- **References**: product-design/constitution.md
- **Depends on**: Step 3, Step 5, Step 6
- **Interface**: N/A
- **Verify**: `run_all_checks.py` retorna o mesmo conjunto de falhas pré-existentes do Step 1 (nenhuma nova); vocabulário consistente (`git grep -n "D3a" ` aparece nos quatro lugares); zero termos de C1; progress lista as pendências.
- **Tests**: N/A (verificação)
- [ ] Done

## Coverage (advisory)

`product-design/product-design-as-intended.md` do Doutourado não tem marcadores REQ; `critique_plan_coverage.py` não se aplica e `Traces:` fica ausente.

## Lacunas e conflitos com o plano 000007

1. **Esquema da matriz.** O 000007 (Step 4) fixa a tabela de rastreabilidade só com REQ, cenário, teste, código, gate, "só como esquema". D3a e D3b precisam também de resultado do teste, vermelho-pelo-motivo-certo e linhas tocadas não cobertas. Tratado como colunas **derivadas** (Decisão pendente 4, B); se o item 8 não as derivar, é preciso emenda aditiva ao `feature-layout.md`.
2. **Condição de refutação (rascunho do Step 6 do 000007).** Fala em "divergência composta igual ou maior no estendido em ao menos dois dos três degraus", mas o ciclo padrão não tem REQ nem cenário, então D1 e D2 do braço A só existem por retrofit. A regra de comparação deste plano resolve a operação; o texto de H-009 (prosa Human) deve ganhar a ressalva (Step 7 sugere a frase). Não editado aqui.
3. **"Composta" no 000007** é definida como "reportada por degrau, sem número único" (decisão pendente 4, C): este plano a adota sem alteração. A divisão do degrau teste→código em **D3a/D3b** é um refinamento (duas medidas dentro do mesmo degrau), não uma mudança de degrau.
4. **D-C do 000007 (divergência composta por degrau)** fica sem entrada D-NNN nova aqui; este plano só detalha. Se o designer quiser registrar o oráculo independente como decisão, é uma D-NNN para a prosa Human.
5. **Dependência.** O roadmap marca "Depends on: nenhum", mas a citação de `CYC-NNN` e do esquema de `feature-layout.md` depende de o 000007 ter rodado no open-seja; o Step 1 trata os dois casos (existe / "a confirmar").
6. **Versão de formato.** Este plano segue o cabeçalho de plano do Doutourado (`plan_format_version: 1`, como o 000007); o `v2` do 000007 vale para os planos que usarem a fase specify no open-seja, e este plano não tem `Scenarios:` (é de definição, `Tests: N/A`).

## Metacomm Intention
- **Summary**: I tell you that I will show where your intent gets lost, one step of the ladder at a time and with what I could not measure, and that I will compare the new cycle with the old one against your own yardstick.
- **Source**: agent (technical plan; metacomm text kept for the report to the designer)

## Review log

**Review depth:** Standard (7 steps, ~8 arquivos distintos). Phase 1 inline (sem subagente; mesmo critério do plano 000007); sem Phase 2 (nenhum Deferred com risco de regressão). Prefixo FEATURE-O: usei DX, TEST, DATA, COMPAT, SEC.

### Phase 1 -- Perspective scan

| Perspective | Status | Concern |
|---|---|---|
| DX | Adopted | Um relatório por degrau, com campos fixos; cada step com Verify por comando ou `grep`. |
| TEST | Adopted | Fixtures golden com recontagem independente; execução automática é do item 8 (declarado). Steps documentais: `Tests: N/A` justificado. |
| DATA | Adopted | `não medido` fora do denominador e sempre visível; denominador zero = "n/a"; contagens brutas; sem número único. |
| COMPAT | Adopted | Sem mudança no gate, hooks ou contrato do 000007 (no máximo uma linha de ponteiro); lacunas listadas. |
| SEC | Adopted | C1 verificado por `git grep` nos Steps 2, 3, 4, 7; fixtures fictícias, sem dado real; sem chaves. |
| PERF, DB, API, I18N, UX, A11Y, VIS, RESP, OPS, ARCH, MICRO | N/A | Sem superfície (plano de definição). |

### Riscos e lacunas registrados
- Caminhos e fontes de tempo do open-seja não verificados (submodule vazio): Step 1 é o portão.
- Assimetria do retrofit no braço A e uma feature só: ameaças declaradas, sem fingir poder estatístico.
- Oráculo escrito pelo mesmo designer que responde ao grill: viés possível, mitigado só por sigilo e congelamento por hash.

### Execution Metrics
| Metric | Value |
|---|---|
| Review depth | Standard |
| Phase 1 perspectives | 5 adopted, 11 N/A |
| Phase 2 deep-dives | 0 |
| Iterations | 0 |
| Pending decisions | 4 (defaults B, B, A, B) |

## Outcomes

- `drift-metric.md`: divergência por degrau (D1, D2, D3a, D3b), com unidade, fonte, cálculo, estados e formato do relatório.
- `drift-control-protocol.md` e `pilot-run-record.md`: controle com oráculo independente, braços A/B, réplicas, tempo até a primeira feature aprovada, regra de comparação e ameaças à validade.
- Seis casos golden em um arquivo (matriz e relatório esperado) como contrato de teste do item 8.
- Lista de lacunas contra o plano 000007 e a frase sugerida para H-009.

smoke: false
