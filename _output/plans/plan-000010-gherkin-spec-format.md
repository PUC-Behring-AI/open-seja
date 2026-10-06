# Plan 000010 | FEATURE-O | 2026-10-05 11:35 UTC | gherkin-spec-format: convenção de .feature (tag @REQ-) e validador determinístico | Review: standard

> **Origem**: movido do ledger do Doutourado em 2026-10-05 (proposal-000088; la era `plan-000079`). Os IDs roadmap-000006 e plan-000007..000016 sao deste ledger (tabela no roadmap). Referencias a research-NNNNNN, reflection-NNNNNN, communication-NNNNNN, roadmap-000062 e plan-000064..000074 apontam para o ledger do Doutourado (repositorio do pesquisador). Caminhos `open-seja/...` em Files passam a ser relativos a raiz deste repositorio.
plan_format_version: 1

> Item 4 do roadmap-000006 (Wave 1, Depends on: default-cycle-contract / plan-000007). Repositório de execução: **open-seja** (worktree/branch por plano); o plano vive no Doutourado. C1: nenhum nome de parceiro nos artefatos que forem ao open-seja. Usa o vocabulário do plano 000007 (`CYC-NNN`, `features/<slug>/{intent.md,*.feature,gate.json}`, `@REQ-<slug>-NNN`, `plan_format_version: 2`) e fornece a entrada que o plano 000008 espera (D1 e D2, casos "órfão" e "sem tag"). Não reabre nenhuma decisão fechada daqueles planos.

## User brief

> Item 4 do roadmap-000006: `gherkin-spec-format` (Depends on: default-cycle-contract). "Convenção de `.feature` (tag `@REQ-`) + validador (steps sem duplicata/ambiguidade, rastreabilidade)."

## Agent interpretation

**Problem.** O ciclo estendido (000007) faz a fase specify escrever Gherkin que o citizen aprova e que depois vira teste vermelho por cenário. O 000007 fixou só o layout e a tag; não diz como escrever um `.feature` que seja bom critério de aceitação, nem como detectar mecanicamente os defeitos que tornam Gherkin "ruído" (risco do roadmap): cenário sem REQ, REQ sem cenário, tag que não aponta para nada, step repetido ou ambíguo, cenário que testa dois comportamentos. O 000008 mede D1 (REQ→cenário) e D2 (cenário→teste) sobre esses mesmos artefatos e precisa de uma fonte determinística e legível por máquina. Sem o item 4, os itens 5 (specify), 6 (plano por cenários) e 8 (relatório de divergência) não têm o que validar nem o que ler.

**Approach.** Plano **técnico** (o primeiro do ciclo com código), no open-seja, em três peças:
1. **Convenção normativa** `gherkin-spec-format.md` com regras `GHK-NNN` (idioma, tag `@REQ-`, um cenário por comportamento, `Scenario Outline`, estilo dos steps, tags reservadas), cada uma com severidade e critério de aceitação.
2. **Validador determinístico** `check_features.py` (Python, só biblioteca padrão, sem LLM e sem rede): parser de Gherkin próprio e mínimo, regras de estrutura, de rastreabilidade (cenário↔REQ de `intent.md`) e de steps (duplicata, ambiguidade, quase-duplicata); saída legível e `--json`; `--matrix` com a tabela REQ→cenários que o item 8 e o 000008 (D1) consomem; exit codes; opcionalmente confere definições de step em Python (`--steps`).
3. **Fixtures golden** (um caso por regra) escritas **antes** do validador, e a integração com `run_all_checks.py` como check **condicional**: projeto sem `features/<slug>/intent.md` não é afetado.
Mais uma prova curta de que a convenção é executável no runner recomendado (pytest-bdd), com um `conftest` modelo; a ligação do runner ao `/implement` é do item 7.

**Alternatives rejected.**
- Depender de um parser externo para o validador: acrescenta dependência a um harness cujos checks rodam com a biblioteca padrão; o subconjunto de Gherkin necessário é pequeno (ver Decisão pendente 3).
- Deixar a validação para o runner (pytest-bdd): o runner só acusa step sem definição e erro de sintaxe; não vê cenário sem REQ, REQ sem cenário, tag órfã nem duplicata (override silencioso de definição de step por fixture).
- Validar semântica ("o cenário captura o REQ?") com LLM: é a auditoria humana por amostra do 000008 (Decisão pendente 1 dele), nunca parte de um check determinístico.
- Número de regras mínimo (só tags): o roadmap pede steps sem duplicata/ambiguidade; sem isso o risco "Gherkin mal escrito vira ruído" fica sem defesa mecânica.

**Selection rationale.** Sem `source:`. Fontes: roadmap-000006 (item 4, tabela "Decisões", risco "Gherkin mal escrito vira ruído"), plano 000007 (Steps 2 e 4: `CYC-NNN`, layout, tag), plano 000008 (Steps 2 e 3: D1, D2, casos golden), research-000050 (Specifier: "registro de steps sem duplicata/ambiguidade"; mutação dos `.feature` fica para depois) e roadmap-000062 (Gherkin como critério de aceitação, estilo Uncle Bob).

### Decisões fechadas (não reabrir neste plano)

1. Layout `features/<slug>/{intent.md,*.feature,gate.json}`; tag `@REQ-<slug>-NNN` em cada cenário (000007). A frase `@REQ-NNN` da tabela do roadmap é lida como abreviação desta.
2. Runner de Gherkin em Python recomendado: **pytest-bdd** (mesmo `uv run pytest`). Este plano não o reabre; só prova que a convenção roda nele (Step 8).
3. `skip`/`xfail` contam como descoberto no D2 (000008): o validador sinaliza tags de desativação (GHK-014) para que isso apareça antes do runner.
4. Divergência composta por degrau (000007/000008): o validador **não calcula D**; entrega a matriz REQ→cenários e os achados que alimentam D1 e as leituras "órfão" e "sem tag".
5. Retrocompatibilidade: sem `features/<slug>/intent.md` o validador não faz nada e retorna 0.
6. Este plano não escreve em `product-design/` do Doutourado, não edita roadmap nem INDEX, não altera gate, hooks nem o texto do contrato do 000007 (no máximo uma linha de ponteiro, Step 9).

### Regras da convenção (resumo; o texto normativo é o Step 2)

| Regra | O que detecta | Severidade | Alimenta |
|---|---|---|---|
| GHK-001 | Arquivo não parseia; sem `Feature:`; idioma não suportado | erro | todos |
| GHK-002 | `Scenario`/`Scenario Outline` sem tag `@REQ-` | erro | 000008: "cenário sem tag" |
| GHK-003 | Tag `@REQ-` malformada; slug diferente da pasta; `@REQ-` no nível `Feature`/`Rule` | erro | D1 |
| GHK-004 | Tag órfã: `@REQ-<slug>-NNN` que não existe na tabela de `intent.md` | erro | 000008: "tag sem REQ" |
| GHK-005 | REQ sem cenário. `intent.md` `status: approved` = erro (descoberto no D1); `grilling` = informação (não medido) | erro / info | D1 |
| GHK-006 | Step duplicado no mesmo cenário (mesmo tipo efetivo e mesmo texto normalizado) | erro | ruído |
| GHK-007 | Mesmo texto de step com tipos efetivos diferentes (Given vs Then) na mesma feature: ambíguo para o runner | erro | ambiguidade |
| GHK-008 | Steps iguais após normalização agressiva (caixa, pontuação, aspas, números) mas escritos diferentes | aviso | quase-duplicata |
| GHK-009 | Primeiro step com `And`/`But`; placeholder `<x>` sem coluna; coluna de `Examples` não usada | erro | estrutura |
| GHK-010 | Nome de cenário repetido no mesmo arquivo (o runner liga por nome; a chave do relatório é `<slug>/<arquivo>::<nome>`) | erro | D2 |
| GHK-011 | `Scenario Outline` sem `Examples`, ou `Examples` sem linhas | erro | estrutura |
| GHK-012 | Cenário com mais de um comportamento (novo `When` após `Then`); mais de 10 steps; `Background` com mais de 3 steps | aviso | um cenário por comportamento |
| GHK-013 | Detalhe de implementação no texto do step (URL, caminho de arquivo, SQL, seletor CSS, nome de função/classe) | aviso | critério de aceitação |
| GHK-014 | Tag de desativação (`@skip`, `@wip`, `@xfail`, `@ignore`) | aviso | 000008 D2: descoberto |
| GHK-015 | Só com `--steps`: definição de step duplicada (mesmo tipo e padrão); definição que casa 0 steps; step sem definição (informação, normal no teste-primeiro) | erro / aviso / info | duplicata |
| GHK-016 | Pasta com `intent.md` e sem nenhum REQ válido na tabela; slug inválido (não kebab-case) ou reservado (`ent`, `perm`, `ux`, `mc`, `jm`, `i18n`, `val`, `delta`) | erro | rastreabilidade |

### Decisões pendentes
Cada uma tem default (a recomendação). Se o designer não responder, os steps seguem o default; mudar uma altera só o Step indicado. Nenhuma foi perguntada ao usuário.

**Decisão pendente 1 -- Idioma das palavras-chave do Gherkin** (afeta Steps 2, 3, 4, 8)
- Opção A: sempre inglês (`Given/When/Then`), texto dos steps em pt-BR.
- Opção B: sempre português (`# language: pt`: `Dado/Quando/Então`).
- Opção C: o arquivo declara; o validador aceita `en` e `pt` (tabelas embutidas); exemplos e templates em pt-BR; `# language: pt` obrigatório em arquivo que usa palavras-chave pt.
- **Recomendação: C.** Recommended when o citizen lê e aprova o cenário em quase linguagem natural (pt-BR), enquanto o power dev e o ecossistema de ferramentas estão em inglês. NOT recommended when o Step 1 mostrar que o pytest-bdd instalado não lê `# language:` (então A, sem mudar o resto). Código, nomes de arquivo e de step definitions seguem em inglês (standards.md § i18n).

**Decisão pendente 2 -- Herança de tag `@REQ-` do nível `Feature`** (afeta Steps 2, 4)
- Opção A: proibida; a tag vai em cada `Scenario`/`Scenario Outline` (GHK-003).
- Opção B: herdada pelos cenários (semântica padrão do Gherkin).
- **Recomendação: A.** Recommended when a unidade do D1/D2 é o cenário e se quer que `grep '@REQ-'` ao lado de cada cenário seja a prova de rastreabilidade. NOT recommended when as features são todas de um REQ só (B reduziria ruído, mas dois estilos em convivência confundem o relatório). Um cenário pode ter várias tags `@REQ-` (cobre vários REQs).

**Decisão pendente 3 -- Como o validador lê Gherkin** (afeta Steps 1, 4)
- Opção A: parser próprio mínimo, só biblioteca padrão (`Feature`, `Rule`, `Background`, `Scenario`, `Scenario Outline`, `Examples`, tags, comentários, doc strings, data tables, `# language:` en/pt).
- Opção B: depender do pacote oficial `gherkin-official`.
- Opção C: reutilizar o parser do pytest-bdd.
- **Recomendação: A.** Recommended when os checks do harness rodam sem ambiente instalado e o subconjunto necessário é pequeno e testável por fixtures. NOT recommended when o Step 1 achar que o harness já tem um mecanismo de dependência opcional por check (então B é viável). C acopla o validador ao runner, que é justamente o que se quer poder trocar.

**Decisão pendente 4 -- Escopo da checagem de definições de step (`--steps`)** (afeta Step 5)
- Opção A: só `.feature`; nenhuma leitura de código Python.
- Opção B: `--steps <dir>` lê as definições com `ast` (`@given/@when/@then` com literal de string ou `parsers.parse`) e acusa duplicata exata e definição sem uso; padrões `re`/`cfparse` ficam "não verificado".
- Opção C: B mais ambiguidade por casamento (duas definições casam o mesmo step).
- **Recomendação: B.** Recommended when ainda não há definições reais para exercitar C (elas nascem no item 7, no teste-primeiro) e a duplicata exata já cobre o override silencioso de fixture. NOT recommended when o item 7 não fechar o contrato de step definitions (então C é refeito lá). Fica registrado como lacuna: ambiguidade por casamento no nível das definições é do item 7.

**Decisão pendente 5 -- Onde se registra a aprovação dos `.feature`** (afeta Steps 4, 6; lacuna com o 000007/000008)
- Opção A: o validador não julga aprovação; lê `scenarios: approved` do frontmatter de `intent.md` **se existir** (campo aditivo que o item 5 passa a escrever) e expõe `scenarios_approved: true|false|null` na matriz.
- Opção B: tratar todo `.feature` presente como aprovado.
- Opção C: emenda já agora ao `feature-layout.md` do 000007 com o campo.
- **Recomendação: A.** Recommended when o ponto de aprovação humana é do item 5 e o 000008 já trata "`.feature` não aprovado" como `não medido` no D1. NOT recommended: B (cenário rascunho contaria como coberto) e C (reabre um plano revisto). O campo é proposto aqui só como convenção; quem o escreve é o item 5.

**Decisão pendente 6 -- Unidade do `Scenario Outline` no D2** (afeta Steps 2, 6; lacuna com o 000008)
- Opção A: o `Outline` inteiro é **um** cenário; coberto no D2 só se **todas** as linhas de `Examples` foram executadas e nenhuma foi `skip`/`xfail`.
- Opção B: cada linha de `Examples` é um cenário.
- **Recomendação: A.** Recommended when o REQ descreve um comportamento e as linhas só variam os dados; mantém `n` do D2 comparável com o número de comportamentos aprovados. NOT recommended when linhas de `Examples` expressam comportamentos distintos (isso é sinal de cenário mal escrito: dividir em cenários, ver GHK-012). A matriz traz `rows` por Outline para o item 8 poder detalhar.

**Decisão pendente 7 -- Quanto da prova de runner entra aqui** (afeta Step 8)
- Opção A: só documentar a convenção; nenhuma execução em runner.
- Opção B: prova de execução com pytest-bdd (um cenário verde e um vermelho, mapeamento tag→relatório) e um `conftest` modelo; sem ligar ao `/implement`.
- Opção C: já ligar ao `/implement`.
- **Recomendação: B.** Recommended when o item 4 precisa garantir que "um `.feature` válido aqui roda no runner escolhido" e o item 7 só consome. NOT recommended when pytest-bdd não puder ser instalado no ambiente de verificação (então A, registrando "não provado"). C invade o item 7.

## Files

Todos no **open-seja**, exceto onde dito. O submodule não está inicializado neste worktree; caminhos **não verificados**: o Step 1 os confere antes de qualquer escrita.

- `.claude/references/general/gherkin-spec-format.md` (create) -- convenção normativa `GHK-NNN`
- `.claude/skills/scripts/check_features.py` (create) -- parser, regras e CLI do validador
- `.claude/skills/scripts/run_all_checks.py` (modify) -- registra o check condicional
- `tests/` (caminho do Step 1): `test_check_features.py` (create) e `fixtures/features/` (create) -- casos golden
- `.claude/references/template/feature-example/` (create) -- feature fictícia válida e `conftest.py` modelo (Step 8)
- `.claude/references/template/feature-layout.md` e `.claude/references/general/extended-cycle-contract.md` (modify, só linha de ponteiro, se existirem após o 000007)
- `_output/plans/plan-000010-progress.md` (create no Doutourado)

## Best practices

- "PASS is a tool result, not a sentence" (research-000050): toda regra é verificável por comando sobre arquivos; sem LLM no validador.
- Fixtures primeiro (teste-primeiro, o mesmo princípio que o ciclo estendido impõe ao código): cada regra `GHK-NNN` tem um caso mínimo que a dispara e um que não.
- Achado = `{regra, severidade, arquivo, linha, cenário, mensagem, dica}`; mensagens em frases curtas e termos fixos (voz controlada, plano 000074) porque o citizen as lê.
- Reportar o que não foi medido ao lado do que foi (`info`), nunca silenciar.
- Biblioteca padrão, funções puras (`parse`, `validate`) separadas de CLI e de I/O (standards.md § Backend 1, 4, 19); `ruff` e `pyright` limpos no arquivo novo se o open-seja os usa.
- Datas e timestamps em UTC; saída `--json` estável e versionada (`schema_version`).

## Design decisions

- **User-visible impact:** quando o `/plan` escrever os cenários, eu os confiro antes de mostrar a você: acuso cenário sem REQ, REQ sem cenário, step repetido ou confuso e cenário que mistura dois comportamentos, com a linha do problema e uma dica em frases curtas. Projetos sem `features/` seguem como antes.
- **Trade-offs accepted:** um parser de Gherkin próprio a manter (subconjunto pequeno, coberto por fixtures) em troca de zero dependência; heurísticas de aviso (GHK-012, GHK-013) podem errar para os dois lados, por isso são avisos e não bloqueiam; ambiguidade no nível das definições de step fica para o item 7.
- **Metacommunication impact:** I know you want to approve *what* will be built without reading code; therefore I check your scenarios before you see them, tell you in plain words what is missing or repeated, and say clearly when a scenario is turned off (it then counts as not covered).

## Steps

### Step 1: Conferir o terreno no open-seja e fixar os pontos de integração
Na tag/branch `dev` do open-seja (`git submodule update --init open-seja` se vazio): (a) confirmar se o 000007 e o 000008 já estão lá (`extended-cycle-contract.md`, `feature-layout.md`, `drift-metric.md`) e citar os `CYC-NNN` reais; se não, escrever os Steps 2 a 9 contra o vocabulário dos planos do Doutourado e marcar cada citação "a confirmar"; (b) ler `run_all_checks.py`: como um check é registrado, convenção de exit code dos `check_*.py` existentes, como um check pode ser pulado, e a versão mínima de Python; (c) achar o diretório de testes e o padrão de fixtures do open-seja; (d) ler `critique_plan_coverage.py` e `check_human_markers_only.py` para garantir que o regex `REQ-<slug>-NNN` e a tag `@REQ-` não colidem com `REQ-TYPE-NNN` (`REQ-ENT`, `REQ-UX`...); (e) spike de 10 min: `uv run --with pytest-bdd` num diretório temporário, confirmar versão, se lê `# language: pt` e como converte tags em markers (nome com hífen, `--strict-markers`). Registrar no progress, com o resultado de cada item e qual decisão pendente ele fecha (1, 3, 7). Nada é escrito no open-seja.
- **Files**: open-seja/.claude/skills/scripts/run_all_checks.py (read), open-seja/.claude/skills/design/critique_plan_coverage.py (read), open-seja/.claude/references/template/feature-layout.md (read, se existir), `_output/plans/plan-000010-progress.md` (create no Doutourado)
- **References**: product-design/conventions.md, product-design/constitution.md
- **Interface**: N/A
- **Verify**: o progress responde (a) a (e) com caminho ou "ausente"; registra a convenção de exit code existente, o diretório de testes, a versão do pytest-bdd e sim/não para `# language: pt`; `git -C open-seja status` limpo.
- **Tests**: N/A (verificação de estado e spike descartável)
- [x] Done

### Step 2: Escrever a convenção normativa (`gherkin-spec-format.md`)
Criar o documento com: (1) objetivo e leitor (o citizen aprova; o power dev revisa); (2) idioma (Decisão pendente 1, default C) e exemplo mínimo nos dois idiomas; (3) a regra da tag: `@REQ-<slug>-NNN` em cada `Scenario`/`Scenario Outline`, várias tags permitidas, proibida em `Feature`/`Rule` (Decisão pendente 2, default A), regex oficial `^@REQ-[a-z][a-z0-9]*(-[a-z0-9]+)*-[0-9]{3,}$` e a lista de slugs reservados; (4) a regra do parse de `intent.md`: o REQ é a primeira célula de toda linha de tabela Markdown que casa `REQ-<slug>-NNN`, `slug` = nome da pasta, `status` do frontmatter (`grilling|approved`) e campo opcional `scenarios: approved` (Decisão pendente 5); (5) um cenário por comportamento (uma ação `When`, 3 a 7 steps típicos, sem encadear `When`-`Then`-`When`); (6) `Scenario Outline` só para variar **dados** do mesmo comportamento; unidade = o Outline (Decisão pendente 6); (7) estilo de step: declarativo, na voz do domínio, presente, sem detalhe de implementação (GHK-013), valores variáveis entre aspas ou `<coluna>`, um conceito por step; `Background` curto e sem ações; (8) tags reservadas e de desativação (GHK-014) e o que significam para o D2; (9) a tabela completa `GHK-001..016` com severidade, mensagem-modelo e **Critério de aceitação** de cada uma; (10) o que a convenção **não** faz (semântica do cenário, cálculo de D, mutação de `.feature`). Citar `CYC-NNN` do 000007 e as leituras do 000008 conforme o Step 1.
- **Files**: open-seja/.claude/references/general/gherkin-spec-format.md (create)
- **References**: product-design/constitution.md, product-design/standards.md § i18n
- **Depends on**: Step 1
- **Interface**: regex da tag, esquema de parse de `intent.md`, tabela `GHK-NNN`.
- **Verify**: o arquivo existe; as 16 regras têm severidade e "Critério de aceitação"; `grep -c "GHK-0" ` >= 16; os exemplos (pt e en) passam no validador quando o Step 4 existir (re-executado no Step 9); nenhum termo de C1 (`git grep -i` com a lista do Step 1 devolve zero); `run_all_checks.py` igual ao baseline do Step 1.
- **Tests**: N/A (documento normativo; os testes são as fixtures do Step 3)
- **Docs**: o próprio documento; o quickguide pt-BR é do item 9.
- [x] Done

### Step 3: Criar as fixtures golden (teste primeiro)
Criar, no diretório de fixtures do Step 1, uma árvore `features/` por caso, todas fictícias (sem parceiro, sem dado real): `ok-minimo` (1 REQ, 1 cenário), `ok-completo` (3 REQs, Outline com 3 linhas, Background curto, tag em pt e em en, múltiplas tags num cenário), e um caso mínimo por regra `GHK-001..016` (disparo) mais os **negativos** que não devem disparar (por exemplo mesmo texto de step em dois cenários diferentes **não** é duplicata; `And` herdando o tipo anterior). Casos extras de retrocompatibilidade: `sem-features` (diretório sem `features/`), `features-de-terceiros` (um `features/` estilo behave com `steps/`, `environment.py` e `.feature` sem tags e sem `intent.md`), `pasta-sem-intent` (pasta com `.feature` e sem `intent.md`). Cada caso traz `esperado.json` com a lista exata `[{rule, severity, file, line}]`, o exit code e, para os casos válidos, a matriz esperada. Incluir os casos que alimentam o 000008: "cenário sem tag" (GHK-002) e "tag sem REQ" (GHK-004) com contagem esperada 1 cada.
- **Files**: open-seja/tests/fixtures/features/ (create; árvore de casos), open-seja/tests/fixtures/features/README.md (create, uma linha por caso)
- **References**: `.claude/references/general/gherkin-spec-format.md`
- **Depends on**: Step 2
- **Interface**: esquema de `esperado.json` (`findings`, `exit_code`, `matrix`).
- **Verify**: existe um caso de disparo e um negativo para cada `GHK-NNN` (conferido por script que lista as regras citadas nos `esperado.json` e compara com a tabela do Step 2); cada `esperado.json` tem a linha (`line`) conferida à mão contra o arquivo; nenhum termo de C1 no diff.
- **Tests**: N/A (dados de teste; os testes que os usam são o Step 4 em diante)
- [x] Done

### Step 4: Implementar o parser e as regras de estrutura e rastreabilidade
Em `check_features.py`: (a) `parse_feature(text) -> Feature` (tags com linha, `Feature`, `Rule`, `Background`, `Scenario`, `Scenario Outline`, `Examples` com tabela, steps com tipo efetivo resolvido para `And`/`But`/`*`, doc strings e data tables sem interpretar, comentários, `# language:` en/pt), com erros tipados (`ParseError(linha, mensagem)`); (b) `load_intent(path) -> Intent` (frontmatter `status`, `scenarios`, REQs da tabela); (c) `validate_structure(features, intent)` com GHK-001, 002, 003, 004, 005, 009, 010, 011, 014, 016 e a descoberta de features (só pastas `features/<slug>/` com `intent.md`; o resto vira `info`, nunca erro); (d) `build_matrix(...)` com `{REQ: {status_req, scenarios:[{file, name, line, rows, disabled}]}, scenarios_approved}`. Funções puras, sem I/O dentro de `validate_*`; sem importar nada fora da biblioteca padrão.
- **Files**: open-seja/.claude/skills/scripts/check_features.py (create), open-seja/tests/test_check_features.py (create)
- **References**: product-design/standards.md § Testing, § Backend 19
- **Depends on**: Step 3
- **Interface**: `parse_feature(text: str) -> Feature`; `load_intent(path) -> Intent`; `validate_structure(...) -> list[Finding]`; `build_matrix(...) -> dict`; `Finding(rule, severity, file, line, scenario, message, hint)`.
- **Verify**: `pytest tests/test_check_features.py -k "structure or matrix"` verde sobre as fixtures do Step 3; `ruff check` e `pyright` limpos no arquivo (se o open-seja os usa; senão registrar "n/a" no progress); `python check_features.py` sem argumentos num diretório sem `features/` não lança exceção.
- **Tests**: when um cenário não tem tag `@REQ-`, returns um achado GHK-002 com a linha do `Scenario`; when a tag cita `REQ-login-009` e a tabela só tem até 003, returns GHK-004; when o REQ 002 existe na tabela de `intent.md` `status: approved` e nenhum cenário o cita, returns GHK-005 com severidade erro, e com `status: grilling` returns GHK-005 com severidade info; when a tag de `Feature` é `@REQ-login-001`, returns GHK-003; when um arquivo tem `# language: pt` e palavras-chave pt, parses sem erro e os tipos efetivos são Given/When/Then; when um `Outline` usa `<x>` sem coluna `x`, returns GHK-009; when o arquivo é um `.feature` em pasta sem `intent.md`, returns apenas `info` e nenhum erro; when o mesmo arquivo é validado duas vezes, returns achados idênticos e na mesma ordem (determinismo).
- [x] Done

### Step 5: Implementar as regras de step (duplicata, ambiguidade, estilo) e `--steps`
Em `check_features.py`: `normalize_step(text)` (minúsculas, espaços colapsados, aspas e pontuação removidas, valores numéricos e entre aspas trocados por `<v>`), `validate_steps(features)` com GHK-006, 007, 008, 012, 013; e `validate_step_defs(features, dir)` com GHK-015 conforme Decisão pendente 4 (default B): lê `*.py` com `ast`, extrai `@given/@when/@then` com literal de string ou `parsers.parse(...)`, acusa definição duplicada (mesmo tipo e padrão), definição sem uso (aviso) e step sem definição (informação); padrões `re`/`cfparse` e decoradores dinâmicos viram `info: não verificado`. A heurística GHK-013 usa lista fixa de padrões (URL, caminho com `/` ou `\\` e extensão, `SELECT|INSERT|UPDATE`, seletor `#id`/`.classe`, `snake_case()`/`CamelCase`) documentada no `gherkin-spec-format.md` e nunca é erro.
- **Files**: open-seja/.claude/skills/scripts/check_features.py (modify), open-seja/tests/test_check_features.py (modify)
- **References**: `.claude/references/general/gherkin-spec-format.md`, product-design/standards.md § Testing
- **Depends on**: Step 4
- **Interface**: `normalize_step(text: str) -> str`; `validate_steps(...) -> list[Finding]`; `validate_step_defs(features, steps_dir) -> list[Finding]`.
- **Verify**: `pytest tests/test_check_features.py -k "steps or step_defs"` verde; os negativos (mesmo texto em dois cenários diferentes; `And` herdando tipo) não disparam; `ruff`/`pyright` limpos conforme o Step 4.
- **Tests**: when um cenário repete "Dado que o usuário está logado" duas vezes, returns GHK-006 na segunda ocorrência; when "Então o saldo é 10" e "Dado que o saldo é 10" existem na mesma feature, returns GHK-007 (mesmo texto, tipos diferentes); when dois steps diferem só por caixa ou pontuação, returns GHK-008 como aviso e não erro; when um cenário tem `When`, `Then`, `When`, returns GHK-012 como aviso; when um step contém `https://` ou `SELECT * FROM`, returns GHK-013 como aviso; when dois `@given("um usuário")` existem em `steps/`, returns GHK-015 erro com os dois caminhos; when `--steps` aponta para diretório sem definições, returns GHK-015 info por step e nenhum erro (teste-primeiro: "ainda não definido" é normal); when a definição usa `re.compile`, returns info "não verificado" e não falha.
- [x] Done

### Step 6: CLI, saída legível, `--json`, `--matrix` e exit codes
Em `check_features.py`: `main(argv)` com `argparse`: `check_features.py [raiz] [--feature <slug>] [--steps <dir>] [--json] [--matrix] [--strict] [--quiet]`. Saída legível em stderr/stdout conforme standards.md § Backend 8 (relatório em stdout, diagnóstico em stderr): uma linha por achado `features/login/login.feature:12: GHK-002 erro: cenário "Sair da conta" sem tag @REQ-... Dica: ...`, agrupados por feature, e um resumo final (`2 erros, 1 aviso, 0 informações; 3 REQs, 5 cenários, 1 REQ sem cenário`), em frases curtas e termos fixos. `--json`: `{schema_version, root, summary:{errors,warnings,infos,reqs,scenarios,uncovered_reqs}, findings:[...], features:[{slug,status,scenarios_approved}]}`; `--matrix` acrescenta `matrix` (REQ→cenários) com a chave estável `<slug>/<arquivo>::<nome>`. Exit codes: `0` sem erros (avisos e informações não falham); `1` com erros, ou com avisos sob `--strict`; `2` uso incorreto, raiz ilegível ou exceção interna (nunca uma exceção bruta: mensagem curta e `2`). Ajustar à convenção de exit code que o Step 1 achou, se diferir, registrando o motivo. Nunca imprimir conteúdo de arquivo além da linha do achado.
- **Files**: open-seja/.claude/skills/scripts/check_features.py (modify), open-seja/tests/test_check_features.py (modify)
- **References**: product-design/standards.md § Backend 8, § Backend 20
- **Depends on**: Step 5
- **Interface**: CLI acima; esquema JSON versionado (`schema_version: 1`) documentado em `gherkin-spec-format.md` (seção "Saída").
- **Verify**: `pytest tests/test_check_features.py -k "cli or json or exit"` verde; `python check_features.py tests/fixtures/features/ok-completo --json | python -m json.tool` válido; os exit codes dos casos válidos, de erro e de uso incorreto conferem com o `esperado.json`; `ruff`/`pyright` limpos.
- **Tests**: when a raiz tem só avisos, returns exit 0, e com `--strict` returns exit 1; when há um erro, returns exit 1 e a linha contém `arquivo:linha`, o ID da regra e uma dica; when `--json` é passado, stdout é um único objeto JSON com `schema_version` e `findings` na mesma ordem da saída legível; when `--matrix` é passado, a matriz contém todo REQ da tabela, inclusive os sem cenário (lista vazia); when a raiz não existe ou o argumento é inválido, returns exit 2 e nenhuma exceção bruta em stderr; when `--feature login` é passado, só essa feature é validada e as demais não aparecem.
- **Docs**: seção "Saída" e "Códigos de saída" em `gherkin-spec-format.md`.
- [x] Done

### Step 7: Integrar ao `run_all_checks` e provar a retrocompatibilidade
Registrar o check em `run_all_checks.py` como **condicional**: roda `check_features.py` só se existir ao menos um `features/<slug>/intent.md` na raiz do projeto; caso contrário o check é "pulado" (mesma forma que os outros checks condicionais, conforme o Step 1) e não altera o resultado nem o tempo perceptível. Erro do validador (exit 1) reprova o `run_all_checks`; aviso não. Provar a retrocompatibilidade: (a) `run_all_checks.py` no open-seja e num projeto fictício **sem** `features/` devolve exatamente o mesmo conjunto de resultados do baseline do Step 1; (b) fixtures `sem-features`, `features-de-terceiros` e `pasta-sem-intent` retornam exit 0 e nenhum achado de erro; (c) o `check_skill_system`/estrutura de SKILL.md continua igual (nenhum SKILL.md alterado neste step).
- **Files**: open-seja/.claude/skills/scripts/run_all_checks.py (modify), open-seja/tests/test_check_features.py (modify)
- **References**: product-design/standards.md § Testing 6
- **Depends on**: Step 6
- **Interface**: entrada nova no registro de checks (nome `features`, condicional).
- **Verify**: `run_all_checks.py` sem `features/` tem o mesmo conjunto de falhas pré-existentes do baseline (nenhuma nova) e lista `features: pulado`; com a fixture `ok-completo` como raiz lista `features: ok`; com a fixture `GHK-002` lista `features: falhou` e exit diferente de 0; `git diff --stat` mostra só `run_all_checks.py` e o teste.
- **Tests**: when a raiz não tem `features/`, returns `pulado` e o conjunto de resultados dos outros checks é idêntico ao baseline; when a raiz tem `features/` estilo behave sem `intent.md`, returns `pulado` (não valida arquivos de terceiros); when uma feature tem erro GHK, returns que `run_all_checks` reprova com o nome do check `features`.
- [x] Done

### Step 8: Provar a convenção no runner (pytest-bdd) e deixar um `conftest` modelo
Conforme a Decisão pendente 7 (default B): criar `template/feature-example/` com uma feature fictícia válida (2 REQs, 3 cenários, um Outline), suas step definitions mínimas e um `conftest.py` modelo que (a) registra os markers `REQ-...` para o `--strict-markers` não falhar (via `pytest_bdd_apply_tag`), (b) escreve a tag `@REQ-...` como propriedade no relatório JUnit/JSON do teste, para o relatório do runner permitir a ligação cenário→REQ→teste que o 000008 (D2) e o item 8 exigem. Rodar com `uv run --with pytest-bdd pytest` num diretório temporário: 2 cenários verdes e 1 vermelho **pelo motivo certo** (asserção do cenário, não `ERROR`/`ImportError`), um cenário com `@skip` aparecendo como `skipped` no relatório, e conferir que o `check_features.py` aprova o mesmo exemplo. Se pytest-bdd não puder ser instalado, registrar "não provado" no progress e manter só o modelo (opção A). Não ligar ao `/implement`.
- **Files**: open-seja/.claude/references/template/feature-example/ (create: `intent.md`, `login.feature`, `test_login.py`, `conftest.py`), `_output/plans/plan-000010-progress.md` (modify no Doutourado)
- **References**: research-000050, product-design/standards.md § Testing
- **Depends on**: Step 7
- **Interface**: contrato do relatório do runner para o D2: cada teste de cenário traz `req` (lista de tags `@REQ-...`) e o nome do cenário; `skip`/`xfail` aparecem com esse estado.
- **Verify**: o progress registra a saída do `pytest` (3 testes: 2 passed, 1 failed por `AssertionError` do cenário, mais o `skipped`); o relatório tem a propriedade `req` em todos os testes de cenário; `python check_features.py .claude/references/template/feature-example` retorna 0 (ajustar a raiz do exemplo conforme o Step 1); o exemplo não contém nome de parceiro.
- **Tests**: when o cenário vermelho do exemplo roda, returns uma falha de asserção (não `ERROR` de coleta) e o relatório mostra o `req` correspondente; when o cenário marcado `@skip` roda, returns `skipped` no relatório com o `req`; when o `conftest` registra os markers e o `--strict-markers` está ligado, returns coleta sem `PytestUnknownMarkWarning`. Executado por script do Step; se pytest-bdd estiver ausente, `N/A (não provado; registrado)`.
- **Docs**: seção "Rodando no pytest-bdd" em `gherkin-spec-format.md`.
- [ ] Done

### Step 9: Fechar: consistência com os planos 000007 e 000008, C1 e pendências
Reexecutar `pytest tests/test_check_features.py`, `check_features.py` sobre os exemplos de `gherkin-spec-format.md` (pt e en) e sobre `template/feature-example/`, e `run_all_checks.py`; conferir que o vocabulário (`REQ-<slug>-NNN`, estados, `slug`, `status: grilling|approved`) bate com `extended-cycle-contract.md`, `feature-layout.md` e `drift-metric.md` (ou com os planos, se ainda não estiverem no open-seja); conferir C1 (`git grep -i` dos termos do Step 1 sobre o diff). Se `feature-layout.md` e `extended-cycle-contract.md` existirem, acrescentar **uma linha de ponteiro** em cada (`Convenção e validador: ver gherkin-spec-format.md`); não editar o esquema. Registrar no progress: resultados, a tabela GHK→000008 (qual regra alimenta qual leitura), as lacunas abertas (abaixo), o que ficou no default e o texto sugerido, para o designer colar via `/implement --manual`, do campo `scenarios: approved` e da regra "Outline = um cenário" no `feature-layout.md` e no `drift-metric.md`.
- **Files**: open-seja/.claude/references/general/gherkin-spec-format.md (read), open-seja/.claude/references/template/feature-layout.md (modify, só ponteiro, se existir), open-seja/.claude/references/general/extended-cycle-contract.md (modify, só ponteiro, se existir), `_output/plans/plan-000010-progress.md` (modify no Doutourado)
- **References**: product-design/constitution.md
- **Depends on**: Step 8
- **Interface**: N/A
- **Verify**: suíte do validador verde; `run_all_checks.py` com o mesmo conjunto de falhas pré-existentes do baseline do Step 1; `git diff --stat` dos dois arquivos de ponteiro mostra no máximo uma linha adicionada cada e nenhuma alteração em gate, hooks, `settings` ou esquema; zero termos de C1; o progress lista as pendências e a tabela GHK→000008.
- **Tests**: N/A (verificação final; a suíte dos Steps 4 a 8 é o teste)
- [ ] Done

## Coverage (advisory)

`product-design/product-design-as-intended.md` do Doutourado não tem marcadores REQ; `critique_plan_coverage.py` não se aplica e `Traces:` fica ausente. O plano executa no open-seja.

## Lacunas e conflitos com os planos 000007 e 000008

1. **Aprovação do `.feature` (000007 x 000008).** O 000008 define D1 como "REQ aprovado tem >=1 cenário em `.feature` **aprovado**" e `não medido` quando não aprovado, mas o esquema do 000007 só tem `status: grilling|approved` em `intent.md` (aprova os REQs), não os cenários. Este plano propõe o campo aditivo `scenarios: approved` (Decisão pendente 5, default A: o validador só o lê, quem o escreve é o item 5). Sem ele, o D1 não consegue separar cenário rascunho de aprovado.
2. **Tag `@REQ-NNN` (roadmap) x `@REQ-<slug>-NNN` (000007).** A tabela de decisões do roadmap abrevia; este plano segue o 000007. Sugestão: o orquestrador corrigir a abreviação ao atualizar o roadmap.
3. **Formato da tabela de REQ em `intent.md`.** O 000007 diz "tabela de `REQ-<slug>-NNN` com texto e critério" sem fixar colunas; este plano fixa só a regra de parse (REQ na primeira célula). O item 3 (grill) deve emitir a tabela nesse formato; o validador acusa GHK-016 se não houver nenhum REQ válido.
4. **Unidade do `Scenario Outline` no D2.** O 000008 define a unidade como "`Scenario` com tag" e não trata `Outline`/`Examples`. Decisão pendente 6 (default A: o Outline é um cenário; coberto só se todas as linhas rodaram). O `drift-metric.md` e as fixtures golden do 000008 (Step 3) precisam de um caso com `Outline`; sugerido para o item 8.
5. **Chave do cenário no relatório do runner.** O D2 do 000008 liga cenário a "teste coletado e executado", mas nenhum plano fixa a chave. Este plano propõe `<slug>/<arquivo>::<nome>` (nome único por arquivo, GHK-010) e a propriedade `req` no relatório (Step 8); o item 7 deve produzi-la no gate e o item 8 consumi-la.
6. **Ambiguidade no nível das definições de step.** Só duplicata exata é verificada aqui (Decisão pendente 4, default B); o casamento de padrões (`parse`, `re`) é do item 7, quando houver definições reais.
7. **Colisão de nomes com REQ do design.** `REQ-TYPE-NNN` (`REQ-ENT`, `REQ-UX`...) já existe no `product-design/` (uso em `critique_plan_coverage.py`). O slug reservado (GHK-016) e a regra "prefixo `REQ` em maiúsculas, slug em minúsculas" evitam colisão; o Step 1 confirma no regex do open-seja.
8. **Risco do roadmap "Gherkin mal escrito vira ruído".** O validador cobre só o que é mecânico (GHK-012 e GHK-013 são heurísticas de aviso). A adequação semântica continua sendo a auditoria humana por amostra do 000008 e o ponto de aprovação do item 5.

## Metacomm Intention
- **Summary**: I tell you that, before you approve any scenario, I check it for missing links to what you asked for, repeated or confusing steps, and scenarios that try to do two things at once, and I show you each problem in plain words.
- **Source**: agent (technical plan; metacomm text kept for the report to the designer)

Metacomm contradiction check: nenhuma intenção existente em `product-design-as-intended.md` (D-001 a D-005) conflita; o plano executa no open-seja e não toca D-004 nem D-005.

## Review log

**Review depth:** Standard (9 steps, ~9 arquivos distintos, em dois grupos: scripts/testes e referências). Phase 1 inline (sem subagente; mesmo critério dos planos 000007 e 000008); sem Phase 2 (nenhum Deferred com risco de regressão não resolvido). Prefixo FEATURE-O: usei DX, TEST, COMPAT, ARCH, SEC.

### Phase 1 -- Perspective scan

| Perspective | Status | Concern |
|---|---|---|
| DX | Adopted | Achados com `arquivo:linha`, ID, dica e resumo em frases curtas; `--json` versionado; cada step com Verify por comando. |
| TEST | Adopted | Fixtures por regra criadas antes do código (Step 3); Tests de cada step com comportamento observável; negativos explícitos; determinismo testado. Steps 1, 2, 3 e 9 são documentais ou de dados: `Tests: N/A` justificado. |
| COMPAT | Adopted | Check condicional (Step 7); fixtures de `features/` de terceiros e pasta sem `intent.md`; baseline do Step 1 comparado; nenhum SKILL.md, gate ou hook alterado. |
| ARCH | Adopted | Parser, regras e CLI separados (funções puras); sem dependência externa; runner desacoplado (o validador não importa pytest-bdd). Step 4 concentra parser e várias regras: aceito, por isso 5 e 6 foram separados. |
| SEC | Adopted | C1 verificado em Steps 2, 3, 8, 9; fixtures fictícias; o validador só lê arquivos e nunca executa o código das step definitions (usa `ast`); sem chaves nem `.env`. |
| PERF, DB, API, I18N, UX, A11Y, VIS, RESP, DATA, OPS, MICRO | N/A | Sem superfície relevante (I18N: apenas a Decisão pendente 1, de idioma do Gherkin, tratada em DX). |

### Riscos e lacunas registrados
- Caminhos do open-seja, convenção de exit code e suporte do pytest-bdd a `# language: pt` não verificados (submodule vazio): o Step 1 é o portão e a Decisão pendente 1 tem rota de recuo (A).
- Heurísticas GHK-012/013 podem gerar falso positivo: por isso aviso, não bloqueio; `--strict` é opt-in.
- Step 8 depende de instalar pytest-bdd com rede; se indisponível, vira "não provado" (Decisão pendente 7, opção A).
- Lacunas 1, 4 e 5 exigem emendas aditivas nos itens 5, 7 e 8; registradas, não resolvidas aqui.

### Execution Metrics
| Metric | Value |
|---|---|
| Review depth | Standard |
| Phase 1 perspectives | 5 adopted, 11 N/A |
| Phase 2 deep-dives | 0 |
| Iterations | 0 |
| Pending decisions | 7 (defaults C, A, A, B, A, A, B) |

## Outcomes

- `gherkin-spec-format.md`: convenção de `.feature` com 16 regras `GHK-NNN`, severidade e critério de aceitação.
- `check_features.py`: validador determinístico (biblioteca padrão), saída legível e `--json`, `--matrix` (REQ→cenários, entrada do D1), exit codes 0/1/2, `--strict`, `--steps`.
- Fixtures golden por regra, com negativos e casos de retrocompatibilidade; suíte de testes do validador.
- Check `features` condicional no `run_all_checks.py`: projetos sem `features/<slug>/intent.md` não são afetados.
- Exemplo fictício rodando em pytest-bdd e `conftest` modelo que expõe `@REQ-` no relatório do runner (entrada do D2).
- Lista de lacunas contra os planos 000007 e 000008 e texto sugerido para o designer.

smoke: false
