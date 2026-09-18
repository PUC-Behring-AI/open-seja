# Plan 000005 | REDESIGN-O | 2026-09-18 14:28 | Registrar a hipótese SDLC 3.0 em seja-as-intended (seção 2 + Decisions) | Review: Light
plan_format_version: 1

source: research log privado (arquivo Doutourado) -- mapear a hipótese SDLC 3.0 para o design-intent do open-seja

> **Restrição C1 deste plano.** O artefato de origem vive num arquivo privado e **não é citado por ID** aqui nem em nenhum arquivo do open-seja. Este plano não carrega ID de artefato privado, data de apresentação, nome de parceiro nem imagem de deck. A proveniência corre só na direção privado -> público (o log privado aponta para o commit do open-seja; nunca o inverso).

## User brief

> source: research-NNNNNN (Doutourado, privado -- não citar por ID no open-seja). Registrar a hipótese SDLC 3.0 no product-design/seja-as-intended.md como nova seção 2 + seção ## Decisions. Passos, nesta ordem: (1) adicionar product-design/seja-as-intended.md a HUMAN_MARKERS_FILES em .claude/skills/scripts/human_markers_registry.py, com teste; (2) entregar a prosa da seção 2 (2.1 três fases como grão grosso de P-005; 2.2 faixa EXPLAIN/COMMUNICATE -- EXPLAIN-deriva contínua vs EXPLAIN-retradução por H-003, COMMUNICATE gated por P-005; 2.3 seta REDESIGN = deriva por evento; 2.4 H-005 as-conceived/as-intended/as-coded com duas lacunas e refutação; 2.5 governança = P-004+H-002, sem ID; 2.6 três registros de Schön relidos nas fases, refina 1.2.4; 2.7 H-006 harness que evolui da reflexão do time, WikiSkill arXiv 2608.27454 como contraste), Q-011..Q-013, e ## Decisions vazia entre ## Questões abertas e ## Referências -- prosa é autoria humana, pronta para colar; (3) --dry-run e aplicar D-001 (três fases = grão grosso de P-005; fecha Q-008) via DECISION_APPEND sem --note; (4) CHANGELOG_APPEND: seção 2 added, H-005/H-006 added, Q-011..Q-013 added, Q-008 answered D-001, Q-004 candidate, Q-006 partial, 1.2.4 refined, hipótese do plan-000004 passa a ser H-007; (5) editar Step 6 do plan-000004 (achado "## Decisions não existe" fica obsoleto; numeração H-007); (6) verificar grep -ri "stone|tecgraf" vazio e a citação Hassan et al. TOSEM 2026. Restrição C1: nenhum ID de artefato privado, nenhuma data de apresentação, nenhum nome de parceiro, nenhuma imagem de deck.

*(O ID numérico do log de origem foi substituído por `NNNNNN` neste registro, por C1. O brief literal, com o ID, está em `_output/briefs.md` e no conversation trace -- ver Step 5.)*

## Agent interpretation

**Problema.** A hipótese de trabalho da pesquisa (ciclo em três fases PLAN / BUILD / REFLECT atravessado por uma faixa de retorno EXPLAIN / COMMUNICATE; seta REDESIGN; trio as-conceived / as-intended / as-coded; governança; harness que evolui da reflexão do time) foi formulada fora deste repositório e ainda não está registrada no documento de intenção do SEJA. Sem esse registro, `seja-as-intended.md` diz o que o SEJA é para ser sem dizer para onde a hipótese o empurra, e as decisões que ela fecha (Q-008) continuam abertas no papel. Há, além disso, um bloqueio mecânico: o arquivo é classificado `Human (markers)` mas **não consta** de `HUMAN_MARKERS_FILES`, então `apply_marker.py` recusa qualquer marcador nele -- inclusive o `DECISION_APPEND` de que a seção `## Decisions` precisa.

**Abordagem.** Cinco passos, na ordem que o brief pede, com uma correção de mecânica confirmada com o designer (ver abaixo):

1. Registrar o arquivo na allowlist do harness, com teste -- pré-condição de qualquer marcador.
2. Entregar, **neste plano**, o bloco de prosa pronto para colar: seção 2 inteira (2.1-2.7), as três questões novas, a seção `## Decisions` vazia (sem `---` antes de `## Referências`, pelo motivo mecânico verificado em `_apply_decision_append`), as duas referências novas (citações verificadas) e as linhas do `## CHANGELOG`. O designer cola e commita por fora do post-skill.
3. `--dry-run` e aplicação de `D-001` via `apply_marker.py --marker DECISION_APPEND`, sem `--note`.
4. Emendar o plan-000004 de forma aditiva (imutabilidade de artefato): os fragmentos do Step 6 que ficam obsoletos recebem identificador e marca de superseded, e o texto substituto é apensado.
5. Verificações finais de C1 (grep, IDs privados nos arquivos rastreados) e das duas citações.

**Correção de mecânica, decidida com o designer neste turno.** O passo (4) do brief pedia as linhas de CHANGELOG via `CHANGELOG_APPEND`. Verificado em `human_markers_registry.py` e testado contra o regex: `CHANGELOG_APPEND` valida a linha como `DATA | [A-Z]+-[A-Z]+-\d{3,} | (added|revised|revoked|superseded) | (plan-NNNNNN|-) | nota`. Nenhuma das linhas pedidas passa -- os IDs deste arquivo (`H-005`, `Q-008`, `§ 2`, `1.2.4`) têm um só grupo alfabético, e as ações `answered`, `candidate`, `partial`, `refined` não estão no conjunto permitido. As três linhas já existentes no `## CHANGELOG` do arquivo (`§ 1 | added`, `Q-003 | held-open`, `Apêndice B | added`) foram escritas à mão, o que é coerente com isso. Opções apresentadas: (a) linhas de CHANGELOG como prosa humana, coladas junto com a seção 2; (b) alargar o regex no fork; (c) reformular os IDs para o esquema do script (`SEJA-H-005`). **Escolhida (a)**: zero mudança no harness além da allowlist, fork colado ao upstream (`CONVENTION_2`), um só esquema de ID no documento público. Consequência registrada: o cabeçalho do arquivo promete "apensar linhas ao `## CHANGELOG` via `apply_marker.py`", e essa promessa segue não cumprível para os IDs deste arquivo -- fica anotado como parte de `Q-006` (linha `partial` do CHANGELOG) e não é resolvido por este plano.

**Alternativas rejeitadas.**

- **Escrever a prosa no arquivo via `Edit`/`Write`** -- rejeitada pela classificação `Human (markers)` (`permissions.md`): a prosa é de autoria humana; o agente entrega o bloco, o designer cola.
- **Commitar a prosa colada no mesmo commit dos marcadores (via post-skill)** -- rejeitada: após o Step 1, `check_human_markers_only.py --staged` (post-skill 6c) passa a guardar o arquivo e sinalizaria os hunks de prosa. O designer commita a prosa por fora do post-skill, antes do Step 3, e o commit dos marcadores fica só com hunks permitidos.
- **Ordem "prosa primeiro, allowlist depois"** (recomendação do log de origem) -- rejeitada em favor da ordem do brief (allowlist primeiro). As duas funcionam; a do brief tem a vantagem de o Step 1 já estar commitado quando o designer colar, então o `--dry-run` do Step 3 roda imediatamente após o commit humano.
- **Reescrever o Step 6 do plan-000004 no lugar** -- rejeitada por `report-conventions.md` (artefatos em `_output/` são história de design imutável; "NEVER replace existing plan text"). O Step 4 emenda aditivamente, com identificadores de fragmento.
- **`D-002` para a pergunta de pesquisa (preâmbulo da seção 2)** -- não incluída: o log de origem a deixa como opcional "se o designer quiser STATUS nela"; a pergunta entra como prosa sem ID, e um `D-002` pode ser acrescentado depois com o mesmo mecanismo do Step 3.
- **Registrar `seja-as-intended.md` também no registro As-Intended/As-Coded do `conventions.md` e no `generate_decision_digest.py`** -- fora de escopo (o brief não pede; é matéria de `Q-006`). Anotado na linha `Q-006 | partial` do CHANGELOG.

**Selection rationale** (recomendações do log de origem, R1-R9):

- Included: R1 -- allowlist com teste antes de qualquer marcador (Step 1).
- Included: R2 -- 2.2 com as três distinções; Q-004 candidata; Q-011 aberta (Step 2, prosa).
- Included: R3 -- trio as-conceived / as-intended / as-coded como H-005, com nota de nomenclatura sem citar fonte, elicitação da lacuna 1 via P-003 e refutação (Step 2, prosa).
- Included: R4 -- C1 de proveniência: sem ID privado, sem data, sem `--note` no D-001, sem imagem; grep antes do commit; citação Hassan verificada (Steps 3 e 5).
- Included: R5 -- H-005/H-006 e Q-011..Q-013 tomados aqui; linha de CHANGELOG sobre H-007; emenda ao plan-000004 (Steps 2 e 4).
- Included: R6 -- microloops como refinamento de 1.2.4 em prosa, não H (Step 2, 2.6).
- Included: R7 -- D-001 fecha Q-008; pergunta de pesquisa como preâmbulo sem ID; D-002 não incluída (Step 3).
- Included: R8 -- 2.3 com a consequência verificável (gatilho por evento) como estado intencional (Step 2, prosa).
- Included: R9 -- linha `Q-006 | partial` e nota sobre o decision digest (Step 2, CHANGELOG).

## Files

Lidos durante o planejamento (existência verificada em disco):

- `product-design/seja-as-intended.md` (607 linhas) -- seção 1 (P-001..P-007, H-001..H-004), `## Questões abertas` (Q-001..Q-010, linha 451), `## Referências` (linha 484), Apêndices A/B, `## CHANGELOG` (linha 603, três linhas manuais). Sem `## Decisions`. Seções separadas por `---`.
- `.claude/skills/scripts/human_markers_registry.py` -- `HUMAN_MARKERS_FILES` (cinco entradas; padrão template + projeto para os dois arquivos reais); `ALLOWED_MARKERS` com os regexes verificados acima.
- `.claude/skills/scripts/apply_marker.py` -- `_apply_decision_append` (linhas 192-272): localiza `## Decisions`, calcula o próximo `D-NNN` dentro da seção, insere **após a última linha não vazia antes do próximo `## `** -- logo, um `---` entre `## Decisions` e `## Referências` faria o `D-001` cair depois da régua. Simulado em Python: sem o `---`, a entrada cai dentro da seção. `--id` é obrigatório no argparse mas ignorado por `DECISION_APPEND`; `--note` gera a linha `*Source: <note> (<date>)*` (não usar).
- `.claude/skills/scripts/check_human_markers_only.py` -- verificador do post-skill 6c; só olha o diff staged; em violação pergunta abortar/prosseguir.
- `.claude/skills/scripts/tests/test_apply_marker.py`, `test_check_human_markers_only.py` -- padrão de teste (runner que injeta `HUMAN_MARKERS_FILES` num repo fake). Não há `test_human_markers_registry.py`.
- `_output/plans/plan-000004-seja-como-servico-mvp-seja-config-kb-seja-setup.md` -- Step 6 (linhas 152-176) e a emenda ARCH (linha 296) assumem que `## Decisions` não existe e que `CHANGELOG_APPEND` se aplica ao arquivo; numera "a última hipótese é H-004, a última questão Q-010".
- `.claude/skills/post-skill/generate_decision_digest.py` (linha 15, 48) -- lê só `product-design-as-intended.md`; `D-NNN` de `seja-as-intended.md` ficam fora do digest.
- `product-design/conventions.md` -- registro As-Intended/As-Coded não lista `seja-as-intended.md`.

Tocados por este plano:

- `.claude/skills/scripts/human_markers_registry.py` (modify)
- `.claude/skills/scripts/tests/test_human_markers_registry.py` (create)
- `product-design/seja-as-intended.md` (modify -- prosa pelo designer; `D-001` só via `apply_marker.py`)
- `_output/plans/plan-000004-seja-como-servico-mvp-seja-config-kb-seja-setup.md` (modify, aditivo)

## Best practices

- `permissions.md`: nenhum `Edit`/`Write` em arquivo `Human (markers)`; marcadores só por `apply_marker.py`, após confirmação explícita no mesmo turno; `--dry-run` sempre antes.
- `report-conventions.md`: artefatos em `_output/` são imutáveis -- emenda aditiva com identificador de fragmento; sem em-dash, aspas curvas ou ANSI nos arquivos gerados; UTF-8 sem BOM; pt-BR com diacríticos.
- `constraints.md`: não inventar dados -- as duas citações novas foram verificadas na web durante o planejamento (ver Step 5); não comprimir prosa humana.
- `coding-standards.md`: teste que expressa comportamento observável; não reduzir cobertura; commit no formato convencional.
- Registro abdutivo do próprio documento: cada `H-NNN` carrega o que a confirmaria e o que a refutaria; hipótese não é decisão; `D-001` fecha `Q-008` por testemunho do autor do desenho, não por abdução.
- C1: proveniência só privado -> público.

## Design decisions

**User-visible impact.** Quem lê `seja-as-intended.md` passa a encontrar, depois da seção 1, a hipótese que orienta a evolução do SEJA: as três fases como grão grosso do ciclo canônico, a faixa de retorno e sua relação com o portão de P-005, o terceiro estado da intenção (as-conceived) e a ideia de um harness que evolui da reflexão do time. O arquivo ganha uma seção `## Decisions` endereçável, com `D-001` fechando `Q-008`, e três questões novas. Para o harness, o arquivo passa a ser guardado por `check_human_markers_only.py`, e `apply_marker.py` passa a aceitá-lo para `STATUS` e `DECISION_APPEND`.

**Trade-offs accepted.** Ganha-se um mecanismo de decisão endereçável no arquivo onde as decisões sobre o harness moram, sem tocar o regex compartilhado com `ux-research-results.md` e `product-design-as-intended.md`. Abre-se mão, por ora, de `CHANGELOG_APPEND` por script neste arquivo (os IDs `X-NNN` e as ações do documento não cabem no regex) -- as linhas de CHANGELOG continuam manuais, como as três já existentes. Abre-se mão também de `D-NNN` deste arquivo no decision digest até `Q-006` se resolver. O vocabulário público diverge de formulações anteriores do trio (termo do meio renomeado para as-conceived) para não criar dois sentidos de "as-intended" num arquivo que já usa o termo oito vezes.

**Metacommunication impact.** Eu (SEJA, no arquivo de intenção) passo a dizer a você que o ciclo de sete skills que apresento em P-005 tem uma leitura em três fases, que a deriva que meço em `/explain drift` é o instrumento de um retorno cuja surpresa deve mandar você de volta ao design (e não só ao código), e que há uma lacuna entre o que você concebeu e o que registrou que eu não consigo verificar mas posso ajudar a eliciar. Eu também passo a dizer, em `## Decisions`, quais questões fechei e por quê, em vez de deixá-las abertas na tabela.

## Steps

### Step 1: Registrar `product-design/seja-as-intended.md` na allowlist `Human (markers)`, com teste

Em `.claude/skills/scripts/human_markers_registry.py`, acrescentar `"product-design/seja-as-intended.md"` ao final de `HUMAN_MARKERS_FILES` (caminho POSIX, repo-relativo, correspondência exata). Atualizar o comentário acima da lista: este arquivo **não segue o padrão template + projeto** -- é um documento de intenção específico deste fork (fundamentação teórica do SEJA, ver `Q-006` no próprio arquivo), sem contraparte em `.claude/references/template/`, então recebe uma única entrada. Manter a frase existente sobre o helper `_paths_for` como está.

Criar `.claude/skills/scripts/tests/test_human_markers_registry.py` no estilo dos vizinhos (docstring de módulo, `from __future__ import annotations`, `sys.path.insert(0, SCRIPTS_DIR)` antes de `import human_markers_registry  # noqa: E402`). Não usar o runner de repo fake: os testes aqui são sobre o registro real.

Rodar a suíte inteira depois: `pytest .claude/skills/scripts/tests/` (regressão -- os testes de `apply_marker` e `check_human_markers_only` patcheiam a lista e não devem ser afetados).

- **Files**: `.claude/skills/scripts/human_markers_registry.py` (modify), `.claude/skills/scripts/tests/test_human_markers_registry.py` (create)
- **References**: `product-design/conventions.md` (`ALL_TESTS_CMD`)
- **Interface**: `human_markers_registry.HUMAN_MARKERS_FILES` contém `"product-design/seja-as-intended.md"`; `is_human_markers_file("product-design/seja-as-intended.md") -> True`
- **Verify**: `pytest .claude/skills/scripts/tests/test_human_markers_registry.py` passa; `pytest .claude/skills/scripts/tests/` sem regressão; `python .claude/skills/scripts/apply_marker.py --file product-design/seja-as-intended.md --id Q-008 --marker STATUS --value proposed --dry-run` **não** retorna mais "is not classified as Human (markers)" (deve falhar adiante, com "entry id 'Q-008' not found", o que prova que o portão de allowlist foi passado sem escrever nada)
- **Tests**: (1) quando `is_human_markers_file` recebe `"product-design/seja-as-intended.md"`, retorna `True`; (2) quando recebe a forma Windows `"product-design\\seja-as-intended.md"`, retorna `True` (cobre `normalize_path`); (3) quando recebe `"product-design/seja-as-intended.md.bak"` ou `"docs/seja-as-intended.md"`, retorna `False` (correspondência exata, não por sufixo); (4) para cada entrada de `HUMAN_MARKERS_FILES` que comece por `product-design/`, o arquivo existe em disco relativo à raiz do repo (`Path(__file__).resolve().parents[4]`) -- pega entrada morta na allowlist
- [ ] Done

### Step 2: Entregar o bloco pronto para colar e o designer commitar a prosa por fora do post-skill

O agente **não escreve** em `product-design/seja-as-intended.md` (classificação `Human (markers)`). Este passo consiste em (a) apresentar ao designer o bloco abaixo, tal como está neste plano, com os cinco pontos de inserção, e (b) o designer colar, revisar como autor e commitar **por fora do post-skill** (`git add product-design/seja-as-intended.md && git commit -m "docs: seção 2 de seja-as-intended -- hipótese SDLC 3.0, Q-011..Q-013, Decisions"`), antes do Step 3. Motivo da ordem: após o Step 1, `check_human_markers_only.py --staged` (post-skill 6c) guarda o arquivo e sinalizaria os hunks de prosa se eles fossem parar no commit do agente; commitando a prosa antes, o commit dos marcadores (Step 3) contém só hunks permitidos.

A prosa é a do log de origem, de autoria humana; o agente não a reescreve. As únicas adições do agente ao bloco são mecânicas e estão marcadas: a ausência do `---` entre `## Decisions` e `## Referências` (ver Files: `_apply_decision_append`), as duas referências bibliográficas com dados verificados (Step 5) e as linhas do CHANGELOG (decisão do designer neste turno: prosa humana, não `CHANGELOG_APPEND`).

**Ponto de inserção 1** -- entre o `---` que fecha 1.3.3 (linha 449) e `## Questões abertas` (linha 451): a seção 2 inteira, seguida de `---`.

```markdown
## 2. De AI-assisted a AI-Native: a hipótese

A literatura sobre desenvolvimento assistido por IA investiga majoritariamente a
comunicação humano -> IA: como o desenvolvedor instrui, corrige e restringe o modelo.
A pergunta de pesquisa que este documento serve aponta na direção inversa: **como o
sistema comunica ao humano as intenções que realizou, e se essa comunicação é
reconstruível por quem a recebe.** É P-003 (a mão de volta) e H-001 (o receptor não é
único) ditas como pergunta -- e é o que a engenharia semiótica chama de
comunicabilidade, aplicada ao preposto generativo de P-002.

A hipótese de trabalho é que o ciclo de desenvolvimento se reorganiza em três fases --
PLAN, BUILD, REFLECT -- atravessadas por uma faixa de retorno contínua. Esta seção
lê cada elemento contra a seção 1: o que já estava lá, o que se refina, o que é novo.
Os termos *AI-assisted* e *AI-native* seguem Hassan et al. (2026), que os usam para
nomear SE 2.0 e SE 3.0.

### 2.1 Três fases como grão grosso do caminho canônico

PLAN, BUILD e REFLECT não são um ciclo novo; são o caminho canônico de P-005 em grão
mais grosso:

| Fase | Skills de P-005 | O que a fase materializa |
|---|---|---|
| **PLAN** | `/research` ou `/explain` > `/design` ou `/plan` | intenção e design. A intenção não nasce pronta: prototipar -> observar -> ajustar, antes de travar o design |
| **BUILD** | `/implement`, com `/critique` **dentro** | o incremento, a partir da intenção registrada; refinar e refatorar são parte da fase, não uma fase depois |
| **REFLECT** | `/reflect` | o que o episódio ensinou, antes do próximo começar |

Duas precisões que evitam contradição com P-005. Primeira: `/critique` não desaparece --
ele vive dentro de BUILD, e o portão "validar antes de comunicar" permanece. Segunda: o
"documentar" que acontece dentro de BUILD é a nota de reflexão-sobre-a-ação do post-skill
e a regeneração do as-coded (voz do agente); não é `/document`, que produz artefato
para leitor e continua vindo depois de `/critique`.

Isto responde Q-008: o `Agent WF` de quatro itens da Figura 2 era este grão grosso, não
uma proposta de ciclo sem validação. Registrado em D-001.

### 2.2 A faixa transversal EXPLAIN / COMMUNICATE

Atravessando as três fases corre uma faixa de retorno, e ela não é uma coisa só:

- **EXPLAIN** é o retorno IA -> humano: o que o preposto entendeu e construiu, no registro
  que o receptor decodifica (P-003). O instrumento é a deriva (H-002, item 3): a
  comparação contínua entre as-coded e as-intended. Mas a deriva é o instrumento, não o
  EXPLAIN -- o EXPLAIN é o retorno cuja *surpresa* dispara o REFLECT.
- **COMMUNICATE** é entre pessoas, mesmo quando mediado por IA: o que o time diz ao
  cliente, ao revisor, ao próximo desenvolvedor.

Duas distinções mantêm a faixa coerente com o que a seção 1 já fixou:

1. **Contínuo para EXPLAIN, gated para COMMUNICATE.** A faixa é contínua para o retorno
   IA -> humano, que não sai do envelope, e para a *preparação* de COMMUNICATE. Cada
   emissão pessoa -> pessoa continua passando por `/critique` (P-005). É uma posição
   semiótica, não de processo: uma mensagem entregue sem validação é o preposto falando
   sem saber se o que diz é verdade.
2. **EXPLAIN-deriva é agnóstico de audiência; EXPLAIN-retradução não.** A comparação
   as-coded x as-intended roda sempre e custa pouco. O registro em que o resultado é
   devolvido depende da posição do humano na escala citizen <-> power (H-003):
   obrigatório num polo, eletivo no outro.

A faixa é uma resposta *candidata* a Q-004 (etapa do post-skill que compara e devolve).
Q-004 permanece aberta até o mecanismo rodar. Abre Q-011.

### 2.3 A seta REDESIGN: deriva como detecção precoce

Quando o EXPLAIN surpreende -- o que voltou não é o que se pretendia -- a seta REDESIGN
volta da faixa ao PLAN. Isto já existe em H-002 (deriva como cidadã de primeira classe,
reconciliada por `/explain drift`). O que a seta muda é o **gatilho**: hoje a deriva é
periódica (verificação a cada 14 dias) e eletiva; detecção precoce pede que ela dispare
por evento, ao fim de cada `/implement`. Esta é a consequência verificável desta
subseção -- e é estado intencional, não atual.

### 2.4 As-conceived / as-intended / as-coded: duas lacunas

<!-- H-005 -->
**H-005 (hipótese) -- Há três estados da intenção, não dois, e só a segunda lacuna
entre eles é verificável por máquina.**

O par de 1.2.2 (as-intended / as-coded, dois arquivos em tensão) esconde um terceiro
termo. Há o que o designer **concebeu** (na cabeça, sem artefato), o que ele
**registrou** (`product-design-as-intended.md`, planos, briefs -- o as-intended, que
continua sendo o arquivo) e o que **existe** (as-coded). Isso dá duas lacunas:

| Lacuna | Entre | Verificável por máquina? | Como aparece |
|---|---|---|---|
| 1 | as-conceived -> as-intended | não | o registro não diz o que se queria; várias realizações cabem no mesmo texto (subespecificação; ver Q-007) |
| 2 | as-intended -> as-coded | sim (`/explain drift`, `check_plan_coverage`) | a implementação diverge do registro |

A lacuna 1 não é verificável, mas é **elicitável**: a surpresa no EXPLAIN (2.2) é a
lacuna 1 detectada através de artefatos da lacuna 2 -- o código voltou fiel ao registro
e ainda assim não era o que se queria. O microloop de PLAN (prototipar -> observar ->
ajustar) é a sonda humana da mesma lacuna, antes de travar o design.

O que a confirmaria: `/explain drift` produzindo, com alguma frequência, propostas de
`/design` (mudar o registro) e não só de `/plan` (mudar o código). O que a refutaria:
toda deriva tratada como bug de código e nunca como bug de expressão -- as surpresas no
EXPLAIN nunca resultando em mudança do as-intended.

Nota de nomenclatura: o termo "as-conceived" para o estado tácito é escolha deste
documento; formulações anteriores usaram outro nome para o termo do meio. O arquivo
as-intended mantém o sentido que tem em 1.2.2 e H-002.

### 2.5 Governança, proveniência, rastreabilidade

A terceira perna da hipótese -- quem altera o quê, de onde veio cada item, cada decisão
ligada à sua intenção -- não acrescenta princípio novo. É P-004 (o sistema de marcadores
e as quatro classificações de autoria dizem de quem é a voz em cada arquivo) e H-002
(IDs estáveis endereçáveis; passos de plano declarando que requisito satisfazem). O que
a hipótese faz é nomeá-la como condição: sem rastreabilidade, o EXPLAIN de 2.2 não sabe
*a que intenção* cada trecho responde, e a retradução vira opinião. Q-007 (de quem é a
voz quando duas vias de autoria escrevem no mesmo texto) continua sendo a questão
aberta desta perna.

### 2.6 Os três registros de Schön relidos nas três fases

A seção 1.2.4 localizou os três registros de Schön em andaimes concretos. A hipótese os
relê sobre o desenho das três fases:

| Registro | Onde vive no desenho | Andaime |
|---|---|---|
| **Reflexão-na-ação** | a faixa EXPLAIN / COMMUNICATE, e os microloops dentro de PLAN (prototipar -> observar -> ajustar) e BUILD (testar -> validar -> refinar -> refatorar) | a justificativa das `AskUserQuestion`; o `/critique` dentro do `/implement`; a comparação contínua da faixa |
| **Reflexão-sobre-a-ação** | o painel REFLECT, depois do episódio | a nota do post-skill; `/reflect` com lente *produto* |
| **Reflexão-sobre-a-prática** | o harness que evolui (2.7) | `/reflect` com lente *prática*, alimentando as skills |

Isto refina 1.2.4 em dois pontos: a reflexão-na-ação deixa de ser só a justificativa
da `AskUserQuestion` e passa a incluir os microloops de PLAN e BUILD; e o `/reflect`
se desdobra pelas duas lentes que a skill já oferece.

### 2.7 O harness que evolui da reflexão do time

<!-- H-006 -->
**H-006 (hipótese) -- As skills e regras do harness podem evoluir a partir dos
registros de reflexão-sobre-a-prática do time, e não apenas de traces de execução do
agente.**

Hoje nenhuma skill lê os registros de `/reflect` como entrada: `/reflect` escreve, o
post-skill indexa, e nada consome. A hipótese está, portanto, não refutada por ausência
de mecanismo -- o que é diferente de confirmada.

A referência mais próxima é o WikiSkill (Tang et al., 2026), que co-evolui
skills reutilizáveis de agente com uma base de conhecimento persistente em três camadas
de escrita: traces de execução imutáveis; um wiki de padrões que acumula e nunca reseta;
skills com atualizações reversíveis. As três camadas mapeiam sobre o SEJA: `_output/`
(imutável, por convenção de artefato), `product-design/` (acumula, `Human (markers)`)
e `.claude/skills` (reversível). O contraste é o que importa: lá, quem propõe e quem
mantém são agentes, e a fonte é a experiência do agente; aqui a fonte são palavras
humanas registradas literalmente, e a mudança de skill passa por autoria humana. É o
mesmo eixo da pergunta de pesquisa desta seção -- humano -> IA no WikiSkill, IA -> humano
aqui -- aplicado ao próprio harness.

O que a confirmaria: uma mudança de skill cujo plano cita um registro de reflexão como
origem (rastreabilidade de P-004). O que a refutaria: reflexões acumuladas sem nenhum
plano que as cite -- a crítica de Eraut (1994) a andaimes que viram ritual, já
registrada em H-002. Abre Q-013.

---
```

**Ponto de inserção 2** -- três linhas novas ao fim da tabela de `## Questões abertas` (após a linha de `Q-010`); e, na linha de `Q-008`, acrescentar ao fim da célula "Questão" o texto ` **Fechada por D-001 (2026-09-18).**`:

```markdown
| `Q-011` | Como a faixa contínua de EXPLAIN (2.2) respeita o portão de P-005 sem virar ritual -- o que é "preparar" um COMMUNICATE sem emiti-lo? | 2.2, Q-004 |
| `Q-012` | O `semiotic-inspector` avalia signos de interface via SIM. Avaliar a retradução (se a mensagem IA -> humano é reconstruível pelo receptor) pede um modo novo. Qual método -- CEM adaptado? | pergunta de pesquisa da seção 2 |
| `Q-013` | Qual skill consome os registros de `/reflect` como entrada, e com que regra de escrita sobre `.claude/skills` (reversível? proposta + confirmação humana?) | H-006 |
```

**Ponto de inserção 3** -- entre o `---` que fecha `## Questões abertas` (depois da nota sobre `Q-006`) e `## Referências`. **Sem `---` entre `## Decisions` e `## Referências`**: `apply_marker.py` insere cada `D-NNN` após a última linha não vazia antes do próximo `## `, e uma régua ali faria o `D-001` cair depois dela (verificado por simulação no planejamento). A seção fica vazia neste commit; `D-001` entra no Step 3.

```markdown
## Decisions

> Decisões registradas por `apply_marker.py --marker DECISION_APPEND` (formato DDR:
> Context / Decision / Consequences / Rejected Alternatives). Uma decisão fecha ou
> reencaminha uma questão aberta; hipóteses não entram aqui até serem decididas.

```

(O `## Referências` existente segue imediatamente após a linha em branco, sem `---`.)

**Ponto de inserção 4** -- duas entradas ao fim da lista de `## Referências`, antes da linha `- Abrahão, ... -- Q-001, a completar.` (dados verificados no Step 5):

```markdown
- Hassan, A.E., Oliva, G.A., Lin, D., Chen, B. e Jiang, Z.M. (2026). "Towards AI-Native
  Software Engineering (SE 3.0): A Vision and a Challenge Roadmap." *ACM Transactions on
  Software Engineering and Methodology*. DOI 10.1145/3807901 (online em 21 ago. 2026;
  preprint arXiv:2410.06107, 2024). Origem dos termos AI-assisted (SE 2.0) e AI-native
  (SE 3.0) do título da seção 2.
- Tang, L., Rashtchian, C., Ferng, C.-S., Tomkins, A., Juan, D.-C. e Vu, T. (2026).
  "WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution."
  arXiv:2608.27454. Contraste de H-006: três camadas de escrita (traces imutáveis, wiki
  que acumula, skills reversíveis), com a experiência do agente como fonte.
```

**Ponto de inserção 5** -- linhas ao fim de `## CHANGELOG` (prosa humana, no formato das três linhas existentes; decisão deste turno: não via `CHANGELOG_APPEND`, cujo regex não aceita os IDs nem as ações deste arquivo):

```markdown
2026-09-18 | § 2 | added | - | Seção 2 (De AI-assisted a AI-Native: a hipótese) redigida: três fases como grão grosso de P-005, faixa EXPLAIN/COMMUNICATE, seta REDESIGN, trio as-conceived/as-intended/as-coded, governança como condição, Schön relido nas fases, harness que evolui da reflexão do time
2026-09-18 | H-005 | added | - | três estados da intenção (as-conceived / as-intended / as-coded) e duas lacunas; só a segunda é verificável por máquina, a primeira é elicitável via P-003
2026-09-18 | H-006 | added | - | skills e regras do harness evoluindo a partir dos registros de /reflect; WikiSkill (Tang et al., 2026) como referência e contraste
2026-09-18 | Q-011..Q-013 | added | - | faixa contínua vs portão de P-005; método para avaliar a retradução; skill que consome os registros de /reflect
2026-09-18 | Q-008 | answered | plan-000005 | fechada por D-001: o Agent WF de quatro itens da Figura 2 é o grão grosso do caminho canônico, não um ciclo sem validação
2026-09-18 | Q-004 | candidate | - | a faixa de 2.2 (etapa do post-skill que compara e devolve) é resposta candidata; segue aberta até o mecanismo rodar
2026-09-18 | Q-006 | partial | - | seção ## Decisions criada neste arquivo independentemente da fusão com o template; D-NNN daqui ficam fora do decision digest e CHANGELOG_APPEND não aceita os IDs deste arquivo até o registro As-Intended/As-Coded e o regex do harness os conhecerem; Q-006 segue aberta só na fusão
2026-09-18 | 1.2.4 | refined | - | reflexão-na-ação passa a incluir os microloops de PLAN e BUILD; /reflect se desdobra pelas lentes produto (sobre-a-ação) e prática (sobre-a-prática) -- ver 2.6
2026-09-18 | H-007 | renumbered | plan-000004 | a hipótese que o plan-000004 (SEJA como serviço) propõe registrar passa a ser H-007, e a próxima questão aberta é Q-014
```

- **Files**: `product-design/seja-as-intended.md` (modify -- **pelo designer**, não pelo agente)
- **References**: `.claude/references/general/permissions.md` (classificação `Human (markers)`), `.claude/references/general/constraints.md` (não comprimir prosa humana)
- **Depends on**: Step 1
- **Interface**: N/A
- **Verify**: `git log -1 --format=%s -- product-design/seja-as-intended.md` mostra o commit humano; `grep -c "^## Decisions$" product-design/seja-as-intended.md` = 1; `grep -n -A3 "^## Decisions" product-design/seja-as-intended.md` não mostra `---` antes de `## Referências`; `grep -c "<!-- H-005 -->\|<!-- H-006 -->" ...` = 2; a tabela de questões tem `Q-013`; `git status --porcelain product-design/seja-as-intended.md` vazio antes do Step 3
- **Tests**: N/A (prosa humana)
- [ ] Done

### Step 3: `--dry-run` e aplicar `D-001` via `DECISION_APPEND`, sem `--note`

Com o Step 2 commitado (working tree limpo para o arquivo), rodar primeiro o `--dry-run` e mostrar o diff ao designer; só após confirmação explícita **no mesmo turno**, rodar sem `--dry-run`. Não passar `--note` (geraria `*Source: ... (data)*` -- o único lugar onde um ID privado entraria). Não passar `--plan` (ignorado por `DECISION_APPEND`). `--id` é obrigatório no argparse e ignorado; passar `D-001`. O script auto-numera: a seção está vazia, então sai `D-001`.

```bash
DVALUE="$(cat <<'EOF'
O Agent WF de três fases é o grão grosso do caminho canônico; Q-008 fechada
**Context**: A Figura 2 lista Research -> Plan -> Implement -> Reflect, mais curto que o ciclo de P-005. Q-008 perguntava se era simplificação do desenho ou proposta de ciclo sem validação.
**Decision**: PLAN / BUILD / REFLECT são o caminho canônico em grão grosso: PLAN = investigar + dar forma; BUILD = `/implement` com `/critique` dentro; REFLECT = `/reflect`. O portão "validar antes de comunicar" permanece.
**Consequences**: Q-008 fechada por testemunho do autor do desenho. `/document` e `/communicate` continuam depois de `/critique`; o "documentar" interno a BUILD é a voz do agente (nota do post-skill, as-coded), não artefato para leitor. Ver seção 2.1.
**Rejected Alternatives**: tratar o Agent WF como ciclo reduzido sem `/critique` -- colide com o único invariante rígido do harness.
EOF
)"
python3 .claude/skills/scripts/apply_marker.py \
  --file product-design/seja-as-intended.md --id D-001 \
  --marker DECISION_APPEND --value "$DVALUE" --dry-run
# após confirmação explícita do designer:
python3 .claude/skills/scripts/apply_marker.py \
  --file product-design/seja-as-intended.md --id D-001 \
  --marker DECISION_APPEND --value "$DVALUE"
```

Depois de aplicar, rodar `git add product-design/seja-as-intended.md && python3 .claude/skills/scripts/check_human_markers_only.py --staged` e exigir exit 0 (o hunk é só o bloco `### D-001: ...`; linhas em branco são permitidas). Se sair 1, o Step 2 não foi commitado antes -- desfazer o stage e voltar ao Step 2.

- **Files**: `product-design/seja-as-intended.md` (modify -- somente via `apply_marker.py`)
- **References**: `.claude/references/general/permissions.md`, `.claude/skills/scripts/apply_marker.py` (`_apply_decision_append`)
- **Depends on**: Step 2
- **Interface**: N/A
- **Verify**: `--dry-run` imprime um diff em que `### D-001: O Agent WF de três fases ...` aparece **entre** `## Decisions` e `## Referências` (não depois de `## Referências`); após aplicar, `grep -n "^### D-001:" product-design/seja-as-intended.md` retorna uma linha com número menor que o de `## Referências`; `grep -c "Source:" product-design/seja-as-intended.md` = 0; `check_human_markers_only.py --staged` exit 0
- **Tests**: N/A (marcador aplicado por script já coberto por `test_apply_marker.py::test_decision_append_first_entry`)
- [ ] Done

### Step 4: Emendar o Step 6 do plan-000004 de forma aditiva

O plan-000004 (não executado) assume em três lugares algo que este plano torna falso. Por `report-conventions.md` (artefatos em `_output/` são história imutável; nunca substituir texto de plano), a emenda é **aditiva**: cada fragmento obsoleto recebe um identificador e uma marca de superseded imediatamente acima dele, e o texto substituto é apensado numa seção `### Plan Amendment (iteração 2)` no fim do `## Review Log`. Não apagar nem reescrever nenhuma linha existente.

Fragmentos a marcar (inserir a linha `> **Superseded por plan-000005 (2026-09-18) -- fragmento P4-S6-F<n>; ver Plan Amendment (iteração 2).**` na linha imediatamente acima de cada um):

- **P4-S6-F1** -- Step 6, parágrafo "Registrar também, como achado do próprio passo, que o mecanismo de registro de decisão do SEJA **não está disponível neste arquivo** ..." (linha 158). Obsoleto: `## Decisions` passa a existir e `D-001` já foi registrado por `DECISION_APPEND`.
- **P4-S6-F2** -- Step 6, frase "Numerar continuando a sequência existente (a última hipótese é `H-004`, a última questão `Q-010`)." (fim da linha 156). Obsoleto: a hipótese do plan-000004 passa a ser **H-007** e as questões continuam de **Q-014** (H-005/H-006 e Q-011..Q-013 tomados por este plano).
- **P4-S6-F3** -- Step 6, parágrafo "Não escrever a prosa no arquivo de intenção ... O que é aplicável é `CHANGELOG_APPEND`" e o bloco de comando que o segue (linhas 160-170). Obsoleto em duas partes: `DECISION_APPEND` **passa a servir**; e `CHANGELOG_APPEND` **não** aceita os IDs (`H-NNN`, `Q-NNN`) nem as ações deste arquivo (regex `[A-Z]+-[A-Z]+-\d{3,}` / `added|revised|revoked|superseded`) -- as linhas de CHANGELOG são prosa humana, coladas junto com a hipótese.
- A linha `- **Verify**:` do Step 6 (linha 175) cita "a numeração continua de `H-004` e `Q-010`" e "a ausência da seção `## Decisions` está registrada" -- marcar como **P4-S6-F4** com a mesma linha de superseded acima.

Texto a apensar ao fim do `## Review Log` do plan-000004:

```markdown
### Plan Amendment (iteração 2) -- 2026-09-18, por plan-000005

Origem: plan-000005 registrou `## Decisions` e `D-001` em `seja-as-intended.md`, tomou `H-005`/`H-006` e `Q-011`..`Q-013`, e adicionou o arquivo a `HUMAN_MARKERS_FILES`. Quatro fragmentos do Step 6 ficam obsoletos; substituições:

- **P4-S6-F1 ->** A seção `## Decisions` existe (entre `## Questões abertas` e `## Referências`, sem `---` antes de `## Referências`). Decisões que este plano assentar entram via `apply_marker.py --marker DECISION_APPEND --value "<título>\n**Context**: ...\n**Decision**: ...\n**Consequences**: ...\n**Rejected Alternatives**: ..."`, sem `--note`, `--dry-run` primeiro, confirmação explícita no mesmo turno. O achado sobre indisponibilidade do mecanismo não deve mais ser registrado; `Q-006` segue aberta só quanto à fusão com o template e ao decision digest.
- **P4-S6-F2 ->** Numerar a hipótese deste plano como **`H-007`** e as questões novas a partir de **`Q-014`**.
- **P4-S6-F3 ->** A prosa (H-007, Q-014..) continua sendo bloco pronto para colar, commitado pelo designer por fora do post-skill (o arquivo agora é guardado por `check_human_markers_only.py`). As linhas de `## CHANGELOG` também são prosa humana: `CHANGELOG_APPEND` não aceita os IDs (`H-NNN`, `Q-NNN`, `§ N`) nem as ações (`answered`, `candidate`, ...) deste arquivo. O comando de exemplo com `CHANGELOG_APPEND` não se aplica.
- **P4-S6-F4 ->** Verify passa a ser: `apply_marker.py --dry-run` de `DECISION_APPEND` roda limpo quando houver decisão a registrar; a hipótese carrega condições de confirmação e refutação; a numeração é `H-007` / `Q-014`; nenhuma escrita direta em `seja-as-intended.md` pelo agente fora do script; o commit da prosa é humano e precede o commit de marcadores.
```

- **Files**: `_output/plans/plan-000004-seja-como-servico-mvp-seja-config-kb-seja-setup.md` (modify, aditivo)
- **References**: `.claude/references/general/report-conventions.md` (imutabilidade de artefato; "mark it revoked or superseded ... assign an identifier to the revoked fragment")
- **Depends on**: Step 3
- **Interface**: N/A
- **Verify**: `git diff --stat` do arquivo mostra só linhas adicionadas (0 deletions); `grep -c "P4-S6-F" _output/plans/plan-000004-*.md` >= 8 (4 marcas + 4 substituições); os quatro fragmentos originais continuam presentes literalmente
- **Tests**: N/A (artefato de plano)
- [ ] Done

### Step 5: Verificações finais de C1 e das citações

Rodar, a partir da raiz do open-seja, antes do commit do post-skill:

1. `grep -rniE "stone|tecgraf" . --exclude-dir=.git --exclude-dir=.venv --exclude-dir=node_modules --exclude-dir=__pycache__ | grep -viE "milestone"` -- deve ser vazio. ("milestone" é a única ocorrência aceitável; a linha de base já era limpa.)
2. `grep -rnE "research-0000[0-9]{2}|reflection-0000[0-9]{2}|draft[- ]?0[0-9]{2}" product-design/seja-as-intended.md _output/plans/plan-000005-*.md _output/plans/plan-000004-*.md` -- deve ser vazio. (A menção pré-existente a `research-000026` em `product-design/conventions.md` está fora dos arquivos deste plano e fora do escopo; não tocar.)
3. **Residual conhecido, decisão do designer**: `_output/briefs.md` (linha do `STARTED` deste plano) e `_output/conversation-trace.jsonl` carregam o ID do log de origem porque o brief é registrado literalmente pelo pre-skill. Ambos são arquivos `Agent` rastreados pelo git. Apresentar ao designer via AskUserQuestion: redigir o ID nesses dois arquivos (substituir por `research-NNNNNN`) antes do commit, ou aceitar (o ID sozinho não revela conteúdo). Recomendação: redigir -- o brief deste plano fixa "nenhum ID de artefato privado" sem exceção.
4. `grep -nP "[\x{2014}\x{2013}\x{201C}\x{201D}\x{2018}\x{2019}]" .claude/skills/scripts/human_markers_registry.py .claude/skills/scripts/tests/test_human_markers_registry.py _output/plans/plan-000005-*.md` vazio (sem em-dash / aspas curvas nos arquivos gerados pelo agente; a prosa colada pelo designer não é verificada aqui).
5. Citações (verificadas na web durante o planejamento, 2026-09-18; reconfirmar só se o designer alterar o texto): Hassan, A.E., Oliva, G.A., Lin, D., Chen, B., Jiang, Z.M., "Towards AI-Native Software Engineering (SE 3.0): A Vision and a Challenge Roadmap", *ACM TOSEM*, DOI 10.1145/3807901, publicado online em 21 ago. 2026 (preprint arXiv:2410.06107, out. 2024) -- "TOSEM 2026" confere. Tang, L., Rashtchian, C., Ferng, C.-S., Tomkins, A., Juan, D.-C., Vu, T., "WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution", arXiv:2608.27454, submetido em 27 ago. 2026 -- ID e título conferem.
6. `pytest .claude/skills/scripts/tests/` verde (repetição do Step 1 após tudo).

- **Files**: `product-design/seja-as-intended.md` (read), `_output/plans/plan-000004-seja-como-servico-mvp-seja-config-kb-seja-setup.md` (read), `_output/briefs.md` (modify, condicional ao item 3), `_output/conversation-trace.jsonl` (modify, condicional ao item 3)
- **References**: `.claude/references/general/report-conventions.md` (restrições de caractere)
- **Depends on**: Step 1, Step 2, Step 3, Step 4
- **Interface**: N/A
- **Verify**: itens 1, 2, 4 e 6 vazios/verdes; item 3 decidido e registrado na nota de reflexão do post-skill; item 5 sem divergência com o texto colado
- **Tests**: N/A (verificação)
- [ ] Done

## Outcomes

- `product-design/seja-as-intended.md` registrado em `HUMAN_MARKERS_FILES`, com teste; `apply_marker.py` e `check_human_markers_only.py` passam a alcançar o arquivo.
- Seção 2 (2.1-2.7), `H-005`, `H-006`, `Q-011`..`Q-013`, `## Decisions`, duas referências verificadas e nove linhas de CHANGELOG no documento de intenção -- prosa de autoria humana, commitada pelo designer.
- `D-001` registrado por script na seção `## Decisions`, fechando `Q-008`, sem rastro de proveniência privada.
- plan-000004 emendado aditivamente (fragmentos P4-S6-F1..F4 superseded; numeração `H-007` / `Q-014`; `DECISION_APPEND` disponível; `CHANGELOG_APPEND` não aplicável aos IDs do arquivo).
- C1 verificado: grep `stone|tecgraf` limpo; nenhum ID privado nos arquivos deste plano; residual em `briefs.md` / conversation trace decidido pelo designer.
- Pendências herdadas, não resolvidas aqui e anotadas em `Q-006 | partial`: `D-NNN` de `seja-as-intended.md` fora do decision digest; registro As-Intended/As-Coded do `conventions.md` sem o arquivo; `CHANGELOG_APPEND` incompatível com o esquema de IDs do arquivo.

## Smoke

false

## Review Log

**Review depth:** Light (auto=Light: 5 passos, 4 arquivos tocados; floor=light; sem `--review`)
**Deep-dive budget:** 0/6 used

Prefixo-escopo `REDESIGN-O` não tem linha na tabela de atalhos; shortlist montada pelo conteúdo: ARCH, DX, SEC, COMPAT, TEST, DATA (6). Justificativas: SEC e DATA pela restrição C1 (proveniência, arquivo público); COMPAT pela mudança num script compartilhado com o upstream; TEST pelo teste novo; ARCH pela coerência da seção 2 com P-005/H-003; DX pela legibilidade do documento público sem o deck.

### Phase 1 -- Perspective Scan (2026-09-18 14:28 UTC)

| Perspective | Status | Concern |
|-------------|--------|---------|
| ARCH | Adopted | 2.2 mantém o portão de P-005 (COMMUNICATE gated) e a variação por H-003 (EXPLAIN-retradução); 2.1 mantém `/critique` dentro de BUILD; `## Decisions` sem `---` antes de `## Referências` respeita a mecânica de `_apply_decision_append` (simulada). Ordem allowlist -> prosa (commit humano) -> marcador evita que 6c sinalize prosa. |
| DX | Adopted | Sem IDs privados como links pendentes; nota de nomenclatura do trio sem citar fonte; `/explain` nos dois modos explicado em 2.2; `H-007`/`Q-014` reservados no CHANGELOG e na emenda do plan-000004 para evitar colisão de numeração. Glosa inline de cada ID citado na seção 2 já está na prosa. |
| SEC | Adopted | C1: sem `--note` no `D-001`; sem data de apresentação, parceiro ou imagem; grep antes do commit (Step 5.1); residual do ID no `briefs.md`/trace levado ao designer (Step 5.3) em vez de silenciado. |
| COMPAT | Adopted | Mudança no harness restrita a uma entrada na allowlist + teste; regex de `CHANGELOG_APPEND` intocado (decisão do designer), então `ux-research-results.md` e `product-design-as-intended.md` não mudam de comportamento; fork segue fast-forward-able frente ao upstream exceto pela entrada nova, que é específica deste fork e fácil de rebasear. |
| TEST | Adopted | Teste do registro expressa comportamento observável (`is_human_markers_file` -> True/False; existência em disco de cada entrada `product-design/`); suíte inteira rodada nos Steps 1 e 5; `DECISION_APPEND` já coberto por `test_apply_marker.py`. |
| DATA | Adopted | Conteúdo sem PII e sem dado observado; proveniência só privado -> público; `*Source:*` ausente. |
| PERF, DB, API, I18N, OPS, UX, A11Y, VIS, RESP, MICRO | N/A | |

### Conflict Check (iteração 1)

No inter-perspective conflicts detected.

### Execution Metrics

| Metric | Value |
|--------|-------|
| Deep-dives used | 0/6 |
| Iterations completed | 1/3 |
| Perspectives shortlisted | 6 |
| Perspectives Adopted | 6 |
| Perspectives Deferred (with rationale) | 0 |
| Convergence reason | all resolved (Light: Phase 1 only) |
