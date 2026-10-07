# Plan 000019 | FEATURE-X | 2026-10-06 23:18 | Upgrade multi-dev: identidade por ULID, gramatica aditiva e verificador | Review: deep
plan_format_version: 1
source: research-000018 -- IDs sequenciais locais colidem entre maquinas; D-005 adota ULID sem coordenacao

## User brief

> source: research-000018 -- identidade de artefato por ULID sem coordenacao (D-005). Upgrade multi-dev, primeiro recorte (R2-1, R2-2, R2-3): (1) reserve_id.py deixa de ler INDEX.md e passa a gerar um ULID local com registro de nascimento (tipo, titulo, autor, timestamp UTC, origem) em _output/ids/<uid>.json; ID visivel = <YYYYMMDD>-<6 chars do ULID>; nome de arquivo <tipo>-<YYYYMMDD>-<6 chars>-<slug>.md; header "# Plan 20261006-q8zrj4 | ..." mais linha "uid: <ULID>"; INDEX.md 100% derivado (generate_macro_index.py le RESERVED de _output/ids/ e nao preserva mais linhas RESERVED). (2) Gramatica aditiva: regexes do macro-index, check_plan_coverage, human_markers_registry (STATUS, ESTABLISHED, INCORPORATED, CHANGELOG_APPEND), apply_marker --plan, update_cross_refs, step_notes, summarize_artifacts, check_docs, pending.py, generate_decision_digest, verify_commit_scope, reflect scripts, e os textos "6-digit ID" em report-conventions.md, skills e agentes passam a aceitar \d{6} OU \d{8}-[0-9a-z]{6}; artefatos antigos nao sao tocados (T3). (3) check_ledger_ids.py novo, registrado em check_plugin_registry.json e no run_all_checks.py e chamado pelo pre-skill: IDs duplicados em ambos formatos, RESERVED orfaos, pa-/D-NNN duplicados; casos positivo e negativo. Incluir no plano os dois bugs achados ao aplicar D-005: apply_marker CHANGELOG_APPEND com --plan manual gera linha que o proprio regex rejeita (precisa mapear manual -> "-"), e check_human_markers_only --staged acusa a linha "*Source: from ...*" escrita pelo DECISION_APPEND. Fora do escopo deste plano: merge=union e ids secundarios pa-/qa- (R2-5), apelido derivado e resolve_artifact.py (R2-4), seja-mcp.

## Agent interpretation

**Problem**: `reserve_id.py` aloca IDs por max+1 sobre o `_output/INDEX.md` local ("single-writer assumed"), de modo que dois devs em maquinas diferentes reservam o mesmo numero sem que nada avise, e o INDEX.md carrega estado de alocacao (linhas RESERVED) dentro de um arquivo derivado.

**Approach**: a identidade do artefato passa a ser um ULID gerado localmente no nascimento (D-005), com o registro de nascimento num arquivo por artefato em `_output/ids/`, o que faz o merge entre devs ser trivial e torna o INDEX.md inteiramente derivado. O ID visivel vira `<YYYYMMDD>-<6 chars do ULID>`, que preserva a ordem cronologica na arvore do sistema de arquivos sem contador. A gramatica dos regexes e dos marcadores e **alargada**, nao trocada: toda regex que hoje casa `\d{6}` passa a casar tambem `\d{8}-[0-9a-z]{6}`, por meio de um unico modulo `artifact_id.py` que os demais importam, e os artefatos antigos ficam como estao (constituicao T3). Um verificador novo torna qualquer colisao visivel. A ordem dos steps vai do modulo de ID (sem dependentes) ate os textos das skills, para que cada step seja verificavel com a suite do harness verde.

**Alternatives rejected**:

- **Numero global reservado por push na branch (D' da research-000018)**: exige rede na reserva, modo provisorio e renumeracao de artefato nunca compartilhado; o designer abriu mao do numero curto "plan 7" em favor do apelido (R2-4, fora deste plano), o que dispensa o ponto de serializacao.
- **Trocar o formato de todos os artefatos (renumerar os existentes para ULID)**: viola T3 e reescreveria marcadores em prosa humana; a gramatica aditiva custa uma alternativa por regex e nada mais.
- **Uma regex por script, editada a mao**: espalha a definicao do ID por ~15 arquivos; um modulo compartilhado (`artifact_id.py`) faz o alargamento numa linha e e o lugar natural para o parser e o gerador.
- **ULID completo (26 chars) no nome do arquivo**: ordena igualmente, mas torna nomes e citacoes longos; a data legivel mais seis caracteres do ULID da ordem na arvore, unicidade pratica dentro do dia e o verificador cobre o resto.

**Selection rationale** (research-000018, recomendacoes revisadas R2):
- Included: R2-1 -- identidade por ULID em `reserve_id.py` e `_output/ids/`, INDEX.md derivado (Steps 1-3).
- Included: R2-2 -- gramatica aditiva em regexes, marcadores e textos (Steps 4-6, 9-10).
- Included: R2-3 -- `check_ledger_ids.py` com casos positivo e negativo, no pre-skill e no `run_all_checks.py` (Steps 7-8).
- Excluded: R2-4 -- apelido derivado, apelido livre e `resolve_artifact.py`: segundo plano, ligado a retraducao do citizen (D-004).
- Excluded: R2-5 -- `merge=union`, `spawned:` append-only, ids `pa-`/`qa-` por ULID curto: terceiro plano; independente deste.
- Excluded: R2-6 -- ja feito: D-005 registrado nesta sessao.
- Included (bugs achados ao aplicar D-005): `apply_marker` CHANGELOG_APPEND com `--plan manual` e a linha `*Source:*` do DECISION_APPEND fora da allowlist (Step 4).

## Files

Lidos / analisados:

- `.claude/skills/scripts/reserve_id.py` -- max+1 sobre a coluna ID (:44, :64-67, :115); RESERVED no fim (:120-127); "single-writer assumed" (:8, :16).
- `.claude/skills/scripts/generate_macro_index.py` -- preserva RESERVED (:585-626), descarta quando o artefato aparece (:649-653); regex de H1 por tipo (:90-218) com `(\d+)` e `zfill(6)`; `finalize_reserved` (:694).
- `.claude/skills/scripts/human_markers_registry.py` -- `plan-\d{6}` em STATUS (:81), ESTABLISHED (:105), INCORPORATED (:112), CHANGELOG_APPEND (:118-120: aceita `plan-\d{6}|-`); DECISION_APPEND (:134) nao lista a linha `*Source: ... (data)*` que o `apply_marker.py:265` escreve.
- `.claude/skills/scripts/apply_marker.py` -- normalizador de `--plan` (:425-437: `\d{6}`, `plan-\d{6}`, `manual`); `_apply_changelog` (:310-328) monta a linha com o valor cru de `--plan`, e `manual` nao casa o regex do CHANGELOG.
- `.claude/skills/scripts/check_human_markers_only.py` -- `_line_is_allowed` (:91) consulta os regexes do registry linha a linha.
- `.claude/skills/design/check_plan_coverage.py` -- `plan-(\d{6})` (:216), glob ordenado (:226).
- `.claude/skills/scripts/update_cross_refs.py` -- `_SOURCE_RE` (:42), `_INDEX_ROW_RE` (:48), `zfill(6)` (:93, :100), `isdigit()` (:72-79).
- `.claude/skills/scripts/step_notes.py` (:102, :112-117), `.claude/skills/reflect/summarize_artifacts.py` (:29-30, :82-90, :209), `.claude/skills/scripts/pending.py` (:58-59, :442-528), `.claude/skills/scripts/verify_commit_scope.py` (:111-119).
- `.claude/skills/critique/check_docs.py` (:1587-1589, :1686, :2170-2173), `.claude/skills/post-skill/generate_decision_digest.py` (:58, :64, :116), `.claude/skills/scripts/generate_pending_roadmap.py` (:44, :52, :55), `.claude/skills/reflect/reflect_stuck_loops.py` (:90), `.claude/skills/reflect/reflect_deep_scope.py` (:113), `.claude/skills/reflect/generate_reflection_report.py` (:500).
- `.claude/skills/scripts/run_all_checks.py` -- descobre `check_*.py` por glob (:92-96) e filtra pelo registry (:104-142).
- `.claude/skills/scripts/run_preflight_fast.py` -- `FAST_CHECKS` (:48-80).
- `.claude/skills/scripts/check_plugin_registry.json`, `.claude/skills/scripts/check_conventions.py` (forma canonica de um verificador: bloco `# designer:`, docstring com exit codes e `CHECK_PLUGIN_MANIFEST`).
- `.claude/skills/pre-skill/SKILL.md` -- estagio pending-check (:65).
- `.claude/references/general/report-conventions.md:9` -- "sequential number, zero-padded to 6 chars".
- Skills que citam "6-digit" ou escrevem o header com o ID: plan, research, reflect, communicate, onboard, explain, critique, mob, qa-log, implement; agentes communication-generator, explanation-generator, onboarding-generator, architecture-explainer, evolution-explainer; `.claude/references/template/docs/ddr.md:78`; `docs/reference/harness-reference.md:149`; `.claude/skills/_internal/explain/drift/SKILL.md:21`.
- `product-design/constitution.md` (T3, T4, Q1), `product-design/standards.md § Backend` (scripts so com stdlib; verificador com caso positivo e negativo; `schema_version` em JSON).

A criar:

- `.claude/skills/scripts/artifact_id.py` (create)
- `.claude/skills/scripts/check_ledger_ids.py` (create)
- `.claude/skills/scripts/tests/test_artifact_id.py`, `tests/test_reserve_id.py`, `tests/test_check_ledger_ids.py` (create)
- `_output/ids/` (diretorio; criado pelo `reserve_id.py` na primeira reserva)

A modificar: os scripts e textos listados nos steps.

## Best practices

- Um unico modulo define o ID (gerador, parser, regexes); os demais importam. Sem duplicar regex.
- Gramatica aditiva: o regex novo e uma alternativa do antigo; nenhum artefato existente muda de nome (T3).
- Verificador com caso positivo e negativo, determinista, sem rede, stdlib apenas (standards § Backend > 19, 22).
- JSON de saida e de registro com `schema_version`.
- ULID: 48 bits de timestamp em ms + 80 bits aleatorios, Crockford base32, 26 chars; implementado em ~30 linhas com `os.urandom` e `time.time_ns`, sem dependencia externa. Os 6 chars do ID visivel sao os **ultimos** seis do ULID (parte aleatoria), minusculos.
- Testes antes do codigo em cada step (constituicao Q1; standards § Testing).

## Design decisions

**User-visible impact**: o ID de um artefato novo deixa de ser `000020` e passa a ser `20261007-k3m9qz`; o nome do arquivo vira `plan-20261007-k3m9qz-<slug>.md` e o header ganha a linha `uid: 01K6...`. Artefatos antigos continuam com o numero de seis digitos e continuam citaveis. Dois devs em maquinas diferentes podem rodar qualquer skill ao mesmo tempo sem combinar nada; o INDEX.md deixa de ter linhas RESERVED e passa a ser regeneravel a qualquer momento. Um verificador novo acusa ID duplicado e registro de nascimento orfao.

**Trade-offs accepted**: perde-se o numero curto e a ordem total implicita nele; a ordem intradia entre devs diferentes nao e garantida (o designer aceitou). Ganha-se zero coordenacao, zero renumeracao e um arquivo por ID que o git funde sem conflito. O harness passa a carregar dois formatos de ID por tempo indefinido; o custo e uma alternativa por regex, concentrada num modulo.

**Metacommunication impact**: quando eu reservo um ID, eu lhe digo "reservado 20261007-k3m9qz (uid 01K6...)", e nao mais "reservado 000020". Quando dois artefatos tiverem o mesmo ID, eu lhe digo qual e qual antes de voce commitar, em vez de deixar os dois coexistirem em silencio. Nos marcadores que escrevo nos seus arquivos Human (markers), eu aceito os dois formatos de plano sem lhe pedir para reescrever nada do que ja existe.

## Steps

### Step 1: Criar o modulo artifact_id.py (gerador ULID, ID visivel, regexes compartilhados)
Criar `.claude/skills/scripts/artifact_id.py` com: `new_ulid() -> str` (26 chars Crockford base32, timestamp ms + 80 bits de `os.urandom`); `ulid_timestamp(ulid: str) -> datetime` (decodifica os 10 primeiros chars; UTC); `visible_id(ulid: str) -> str` retornando `YYYYMMDD-<6 ultimos chars do ULID em minusculas>`, com a data **derivada do proprio ULID** (o `id` e funcao pura do `uid`; nenhum relogio externo); `LEGACY_ID = r"\d{6}"`, `ULID_ID = r"\d{8}-[0-9a-z]{6}"`, `ARTIFACT_ID = rf"(?:{LEGACY_ID}|{ULID_ID})"` (sem grupos de captura) e `ARTIFACT_ID_RE = re.compile(rf"^{ARTIFACT_ID}$")`; `normalize_id(raw)` (`zfill(6)` so para valor puramente numerico com ate 6 digitos; o resto inalterado); `is_legacy_id`, `is_ulid_id`; `birth_record(type_, title, author, origin) -> dict` com `schema_version: 1`, `uid`, `id`, `type`, `title`, `author`, `ts_utc` (ISO, igual a `ulid_timestamp`), `origin` (ou null). **Autor nunca e o nome da pessoa** (constituicao C2): `default_author()` devolve `sha256(git config user.email)[:12]` (fallback `sha256($USER)`, senao `"unknown"`); o chamador pode passar um handle via `--author`. Stdlib apenas. Docstring no padrao dos scripts (`# designer:`, Invocation, Lifecycle, Usage). Acrescentar a linha do `artifact_id.py` nas duas tabelas de `docs/reference/harness-reference.md` (o arquivo se declara gerado por `priv/generate_harness_reference.py`, ausente neste repo; o plugin `harness-reference-coverage` do preflight acusa script nao listado).
- **Files**: `.claude/skills/scripts/artifact_id.py` (create), `.claude/skills/scripts/tests/test_artifact_id.py` (create), `docs/reference/harness-reference.md` (modify)
- **References**: `product-design/standards.md § Backend > 16, 19, 22`; `product-design/constitution.md` (C2)
- **Interface**: exports `new_ulid() -> str`, `ulid_timestamp(ulid: str) -> datetime`, `visible_id(ulid: str) -> str`, `default_author() -> str`, `ARTIFACT_ID: str`, `ARTIFACT_ID_RE: re.Pattern`, `normalize_id(raw: str) -> str`, `is_legacy_id(s) -> bool`, `is_ulid_id(s) -> bool`, `birth_record(type_: str, title: str, author: str | None, origin: str | None) -> dict`
- **Verify**: `pytest .claude/skills/scripts/tests/test_artifact_id.py` verde; `ruff check .claude/skills/scripts/artifact_id.py` limpo; `python3 .claude/skills/critique/check_docs.py --plugins harness-reference-coverage --filter warning` sem achado novo
- **Tests**: quando `new_ulid()` e chamado 10.000 vezes, todos tem 26 chars, sao distintos e dois ULIDs gerados com 2 ms de intervalo ordenam lexicograficamente; quando `visible_id` recebe um ULID cujo timestamp e 2026-10-07T23:59:59Z, retorna `20261007-` + 6 ultimos chars em minusculas, e `ulid_timestamp` devolve esse instante; quando `normalize_id("7")` retorna `000007` e `normalize_id("20261007-k3m9qz")` retorna o valor inalterado; `ARTIFACT_ID_RE` casa `000007` e `20261007-k3m9qz` e nao casa `0007`, `20261007-K3M9QZ` nem `20261007-k3m9`; `birth_record` devolve `schema_version`, `uid`, `id == visible_id(uid)` e `ts_utc == ulid_timestamp(uid)`; `default_author()` nunca contem o valor de `git config user.name` (monkeypatch) e tem 12 hex chars.
- [ ] Done

### Step 2: Reescrever reserve_id.py para gerar ULID e gravar o registro de nascimento
Reescrever `.claude/skills/scripts/reserve_id.py` para nao ler nem escrever o INDEX.md. Fluxo: `reserve(type, title, origin=None, author=None, dry_run=False)` chama `artifact_id.birth_record`, escreve `_output/ids/<uid>.json` (criando o diretorio; tempfile + `os.replace`), e imprime em stdout **somente o ID visivel** (compatibilidade com todas as skills que capturam a saida); imprime `uid: <ULID>` em stderr (informativo); com `--json` imprime o registro completo em stdout. Manter `--type`, `--title`, `--dry-run`, `--output-dir`; acrescentar `--origin <tipo>-<id>` (validado por `^[a-z][a-z-]*-` + `ARTIFACT_ID` + `$`; valor invalido sai com 2), `--author <handle>` (opcional; default `artifact_id.default_author()`) e `--json`. Atualizar `# designer:` e docstring: remover "single-writer assumed"; dizer que dois devs nunca colidem porque o ID nasce de um ULID local. Remover `_extract_max_id`, `_format_id`, `_ID_RE` e `INDEX_HEADER` (nenhum modulo ou teste os importa; grep em `.claude/`). Atualizar a linha do `reserve_id.py` em `docs/reference/harness-reference.md` (:149) com a nova primeira linha da docstring.
- **Files**: `.claude/skills/scripts/reserve_id.py` (modify), `.claude/skills/scripts/tests/test_reserve_id.py` (create), `docs/reference/harness-reference.md` (modify)
- **References**: `product-design/standards.md § Backend > 8, 19, 20`
- **Depends on**: Step 1
- **Interface**: CLI `reserve_id.py --type T --title X [--origin TIPO-ID] [--author HANDLE] [--dry-run] [--json] [--output-dir DIR]`; stdout `YYYYMMDD-xxxxxx`, exit 0; exit 2 em `--origin` invalido; grava `<output-dir>/ids/<uid>.json`
- **Verify**: `pytest .claude/skills/scripts/tests/test_reserve_id.py` verde; `reserve_id.py --type plan --title t --dry-run --output-dir <tmp>` nao cria arquivo e imprime um ID no formato novo
- **Tests**: quando dois processos reservam em copias identicas de `_output` em duas `tmp_path`, IDs e uids sao distintos; quando a reserva e feita, existe exatamente um `ids/<uid>.json` com `schema_version`, `type`, `title`, `author`, `ts_utc` e o INDEX.md nao e modificado (mtime e conteudo iguais); quando `--dry-run`, nenhum arquivo e criado e stdout tem o ID; quando `--json`, stdout e um JSON com `id` e `uid`; quando `--origin foo` (sem ID), exit 2 e nenhum arquivo; quando `--author` nao e passado, o registro nao contem `git config user.name`.
- **Docs**: `docs/reference/harness-reference.md` linha do `reserve_id.py`
- [ ] Done

### Step 3: INDEX.md inteiramente derivado: RESERVED vem de _output/ids/, e o extrator aceita os dois formatos
Em `generate_macro_index.py`: (a) substituir `_extract_reserved_rows()` (:585-620) e o merge-back (:649-653) por `_reserved_from_ids_dir()` que le `_output/ids/*.json` e produz `{date: ts_utc em YYYY-MM-DD HH:MM UTC, type: RESERVED, id, title: "<type>: <title>", status: RESERVED, file: ""}` para cada registro cujo `id` nao esta em `scanned_ids`; nao preservar mais linhas do INDEX.md existente; (b) em cada regex de H1 (:90-218) trocar `(\d+)` do campo ID por `(\d+|\d{8}-[0-9a-z]{6})` (ou `artifact_id.ARTIFACT_ID` com grupo externo) e cada `.zfill(6)` por `artifact_id.normalize_id`; nos tres regexes de plano tolerar o campo opcional `METACOMM |` apos o prefixo-scope; (c) nos regexes de QA (:157, :163, :385-386) aceitar o ID novo no pipe do pai e no `parent_ref`; (d) **nas deteccoes de QA companheiro `^plan-\d{6}-qa-` em :282, :296 e :310, usar `^plan-` + `ARTIFACT_ID` + `-qa-`** (senao um QA log de plano novo e indexado como Plan e contado como duplicado pelo Step 7); (e) `finalize_reserved`/`--finalize` (sem chamadores em `.claude/`) viram no-op: imprimem "deprecated: INDEX.md is derived; just regenerate" em stderr e saem 0. Rodar `generate_macro_index.py` neste repo e conferir que as linhas RESERVED 000002, 000003, 000007, 000009, 000015 e 000019 desaparecem e que os planos com METACOMM sao indexados como Plan com ID; **registrar na nota do step as linhas RESERVED removidas** (proveniencia; INDEX.md e arquivo regenerado, T3 nao se aplica a linhas de alocacao).
- **Files**: `.claude/skills/scripts/generate_macro_index.py` (modify), `.claude/skills/scripts/tests/test_generate_macro_index.py` (modify)
- **References**: `product-design/standards.md § Backend > 8`; `product-design/constitution.md` (T3)
- **Depends on**: Step 1, Step 2
- **Interface**: N/A (`--finalize` mantido como no-op depreciado)
- **Verify**: `pytest .claude/skills/scripts/tests/test_generate_macro_index.py` verde; `python3 .claude/skills/scripts/generate_macro_index.py` neste repo produz INDEX.md sem linhas RESERVED e com plan-000007/000009/000015 indexados como Plan com ID
- **Tests**: quando `_output/ids/` tem um registro sem artefato, o INDEX.md tem uma linha RESERVED com aquele ID e titulo; quando o artefato existe, a linha nao aparece; quando um plano tem header `# Plan 20261007-k3m9qz | FEATURE-O | <data> | t | Review: light`, e indexado como Plan com ID `20261007-k3m9qz`; quando o header tem `| METACOMM |` apos o prefixo, e indexado com ID e nao como Other; quando existe `plan-20261007-k3m9qz-qa-x.md`, e indexado como QA Log do plano e nao como Plan; quando um INDEX.md anterior contem linhas RESERVED, elas nao sao preservadas; quando `--finalize 000007` e chamado, exit 0 com aviso em stderr.
- [ ] Done

### Step 4: Gramatica dos marcadores e apply_marker: dois formatos de plano, manual -> "-", linha Source permitida
Em `human_markers_registry.py`: definir `_PLAN_REF = r"plan-(?:\d{6}|\d{8}-[0-9a-z]{6})"` (ou importar `artifact_id.ARTIFACT_ID`) e usa-lo em STATUS (:81), ESTABLISHED (:105), INCORPORATED (:112) e CHANGELOG_APPEND (:120, mantendo `|-`); em DECISION_APPEND (:134) acrescentar **exatamente** a alternativa `\*Source: [^*<>\n]{1,200} \(\d{4}-\d{2}-\d{2}\)\*` (a forma que `apply_marker.py:265` escreve; nao usar `.{1,200}`, que abriria um canal de prosa). Em `apply_marker.py`: o normalizador de `--plan` (:425-437) aceita `\d{8}-[0-9a-z]{6}` (auto-prefixa `plan-`) e `plan-<novo>`; a mensagem de erro **mantem a substring** `--plan must be 'plan-NNNNNN'` (asserida em `test_apply_marker.py:641`) e acrescenta o formato novo; em `_apply_changelog` (:310-328) mapear `manual` -> `-` ao montar a linha (so para CHANGELOG_APPEND; STATUS continua aceitando `manual`); em `_apply_decision` (:230-240), se a primeira linha de `--value` comecar com `D-\d{3}:` ou `D-NEXT:`, remover esse prefixo antes de montar o heading (evita "D-005: D-005:").
- **Files**: `.claude/skills/scripts/human_markers_registry.py` (modify), `.claude/skills/scripts/apply_marker.py` (modify), `.claude/skills/scripts/tests/test_human_markers_registry.py` (modify), `.claude/skills/scripts/tests/test_apply_marker.py` (modify), `.claude/skills/scripts/tests/test_check_human_markers_only.py` (modify)
- **References**: `product-design/constitution.md` (T4), `product-design/standards.md § Backend > 19, 20`
- **Depends on**: Step 1
- **Interface**: N/A
- **Verify**: os tres arquivos de teste verdes mais `tests/test_check_changelog_append_only.py`; `check_human_markers_only.py` aceita um diff que adiciona uma entrada D-NNN completa com a linha `*Source: ...*`
- **Tests**: quando um marcador STATUS traz `plan-20261007-k3m9qz`, o regex casa; quando traz `plan-0007`, nao casa; quando `apply_marker --marker CHANGELOG_APPEND --plan manual` e invocado, a linha tem `| - |` e passa pelo regex; quando `--plan 20261007-k3m9qz`, e normalizado para `plan-20261007-k3m9qz`; quando `--plan invalid`, exit 1 e stderr contem `--plan must be 'plan-NNNNNN'`; quando `check_human_markers_only --staged` ve `+*Source: from research-000018 (2026-10-06)*` dentro de uma entrada D-NNN, retorna 0; quando ve `+*Source: texto livre sem data*`, retorna 1; quando o valor de DECISION_APPEND comeca com `D-NEXT: `, o heading contem o prefixo uma unica vez.
- [ ] Done

### Step 5: Alargar os parsers de ID do nucleo (coverage, cross-refs, step notes, summarize, pending)
Trocar cada regex local por `artifact_id.ARTIFACT_ID` (para scripts fora de `scripts/`, usar o mesmo `sys.path.insert` que `check_plan_coverage.py` ja usa para `project_config`): `check_plan_coverage.py:216`; `update_cross_refs.py` (:42 `_SOURCE_RE`; :48 `_INDEX_ROW_RE`; :72-80 `_artifact_token_from_path` usa `ARTIFACT_ID_RE` em vez de `isdigit()`; :93/:100 `zfill` -> `normalize_id`); `step_notes.py:102` (`_norm_id` -> `normalize_id`; glob funciona com os dois); `summarize_artifacts.py:29-30` (`(\d{6})` -> `ARTIFACT_ID`, e tolerar o campo opcional `METACOMM |` apos o prefixo), :82-90 (busca por substring continua valida), :209; `pending.py:58-59`. Nao mudar `pa-` (:50; R2-5). **Deixar como estao** (legado ou nao-artefato, registrados aqui para o implementador nao os perseguir): `backfill_open_plans.py:59-67`, `backfill_qa_dates.py:148`, `seja-setup/migrate_qa_logs_to_parent_dirs.py:44`, `_internal/seja-setup/upgrade/SKILL.md:59`, `conversation_trace.py:58`, `generate_reflection_report.py:500` (`zfill(6)` e no-op para o ID novo).
- **Files**: `.claude/skills/design/check_plan_coverage.py` (modify), `.claude/skills/scripts/update_cross_refs.py` (modify), `.claude/skills/scripts/step_notes.py` (modify), `.claude/skills/reflect/summarize_artifacts.py` (modify), `.claude/skills/scripts/pending.py` (modify)
- **References**: `product-design/standards.md § Backend > 19`
- **Depends on**: Step 1
- **Interface**: N/A
- **Verify**: `pytest .claude/skills/scripts/tests/test_check_plan_coverage.py tests/test_pending.py tests/test_pending_integration.py tests/test_step_notes.py tests/test_summarize_artifacts.py` verdes; testes novos (Step 7) verdes
- **Tests**: cobertos no Step 7
- [ ] Done

### Step 6: Alargamento dos scripts perifericos
`check_docs.py` (:1587-1589, :1686, :2170-2173: citacoes `plan-`, `advisory-`, `research-` aceitam o ID novo); `generate_decision_digest.py` (:58, :64 `(\d+)` -> `ARTIFACT_ID`; :116 `advisory-(\d+)` -> `advisory-` + `ARTIFACT_ID`); `generate_pending_roadmap.py` (:44, :52, :55; tolerar `METACOMM |` opcional); `reflect_stuck_loops.py:90` (primeiro token que casa `ARTIFACT_ID` na linha do brief); `reflect_deep_scope.py:113` (`PLAN\s*\|\s*(\d+)` -> `ARTIFACT_ID`, senao o ID novo e truncado em `20261007`). `backfill_decision_digest.py` (em `.claude/skills/scripts/`, nao em `post-skill/`) fica fora: migracao unica de advisory logs legados, nunca recebe ID novo. `verify_commit_scope.py:111` nao muda (glob funciona).
- **Files**: `.claude/skills/critique/check_docs.py` (modify), `.claude/skills/post-skill/generate_decision_digest.py` (modify), `.claude/skills/scripts/generate_pending_roadmap.py` (modify), `.claude/skills/reflect/reflect_stuck_loops.py` (modify), `.claude/skills/reflect/reflect_deep_scope.py` (modify)
- **References**: `product-design/standards.md § Backend > 19`
- **Depends on**: Step 5
- **Interface**: N/A
- **Verify**: `pytest .claude/skills/scripts/tests/test_check_docs.py tests/test_generate_pending_roadmap.py tests/test_reflect_primitives.py tests/test_post_skill_scripts.py` verdes
- **Tests**: cobertos no Step 7
- [ ] Done

### Step 7: Testes dos parsers alargados (nucleo e perifericos)
Criar `tests/test_id_grammar.py` cobrindo os parsers dos Steps 5 e 6 e acrescentar casos aos testes existentes de `step_notes`, `summarize_artifacts` e `generate_pending_roadmap`.
- **Files**: `.claude/skills/scripts/tests/test_id_grammar.py` (create), `.claude/skills/scripts/tests/test_step_notes.py` (modify), `.claude/skills/scripts/tests/test_summarize_artifacts.py` (modify), `.claude/skills/scripts/tests/test_generate_pending_roadmap.py` (modify)
- **References**: `product-design/standards.md § Testing > 1`
- **Depends on**: Step 6
- **Interface**: N/A
- **Verify**: `pytest .claude/skills/scripts/tests/` verde; `python3 .claude/skills/scripts/run_all_checks.py` sem falha nova em relacao ao baseline (constituicao Q1)
- **Tests**: para cada parser (coverage, cross_refs, step_notes, summarize, pending, check_docs, decision_digest, pending_roadmap, stuck_loops, deep_scope): quando a entrada traz `plan-000007`, o resultado e o mesmo de antes; quando traz `plan-20261007-k3m9qz`, o ID e extraido inteiro; quando traz `plan-0007`, nao casa. Para `update_cross_refs`: quando um artefato novo tem `source: plan-20261007-k3m9qz -- motivo`, a linha `spawned:` do plano de origem recebe o token do artefato novo. Para `summarize_artifacts` e `generate_pending_roadmap`: um header `# Plan 000007 | FEATURE-O | METACOMM | 2026-10-05 02:00 UTC | t | Review: standard` e parseado com prefixo `FEATURE-O`, data e titulo corretos. Para `pending`: `_plan_file_present("plan-20261007-k3m9qz")` e False quando nao ha arquivo e True quando `plan-20261007-k3m9qz-x.md` existe.
- [ ] Done

### Step 8: Criar check_ledger_ids.py (IDs duplicados, registros orfaos, pa-/D-NNN duplicados)
Criar `.claude/skills/scripts/check_ledger_ids.py` no padrao de `check_conventions.py` (bloco `# designer:`, docstring com exit codes, `CHECK_PLUGIN_MANIFEST` stack any/any, scope `ledger`, critical true). Verificacoes: (1) **ID duplicado**: percorrer `_output/**/*.md` (exceto companheiros `<tipo>-<id>-qa-*.md` e `-progress.md`), extrair o ID do nome com `ARTIFACT_ID` e acusar qualquer ID usado por mais de um artefato primario; (2) **registro orfao**: `_output/ids/*.json` cujo `id` nao tem artefato e cujo `ts_utc` e mais antigo que `--orphan-days` (default 7) -> aviso (exit 0) ou erro com `--strict`; (3) **`pa-` duplicado**: em `pending.jsonl` **nao ha campo `action`**; registro de criacao e o que carrega `created_at` (`cmd_add`), atualizacoes trazem so `id`/`status`/`closed_at` ou `snooze_until`; dois registros com o mesmo `id` ambos com `created_at` -> erro; (4) **`D-NNN` duplicado**: dois headings `### D-NNN:` com o mesmo numero na secao `## Decisions` de `product-design/product-design-as-intended.md` -> erro; (5) **uid duplicado** em `_output/ids/` -> erro; (6) **id incoerente**: registro cujo `id != artifact_id.visible_id(uid)` -> erro. Quando `OUTPUT_DIR` nao existe (projeto sem ledger), sair 0 sem saida. Saida legivel em stdout, `--json` com `schema_version`, exit 0 sem achados, 1 com erros, 2 uso incorreto. Acrescentar a linha do script nas duas tabelas de `docs/reference/harness-reference.md`.
- **Files**: `.claude/skills/scripts/check_ledger_ids.py` (create), `.claude/skills/scripts/tests/test_check_ledger_ids.py` (create), `.claude/skills/scripts/tests/fixtures/ledger_ids/` (create), `docs/reference/harness-reference.md` (modify)
- **References**: `product-design/standards.md § Backend > 5, 8, 19, 23`
- **Depends on**: Step 1
- **Interface**: CLI `check_ledger_ids.py [--output-dir DIR] [--orphan-days N] [--strict] [--json]`; exit 0/1/2
- **Verify**: `pytest .claude/skills/scripts/tests/test_check_ledger_ids.py` verde; rodar no repo retorna 0 (apos o Step 3)
- **Tests**: quando `plan-000007-a.md` e `plan-000007-b.md` existem, retorna 1 e lista os dois caminhos; quando existem `plan-000007-a.md`, `plan-000007-qa-a.md` e `plan-000007-progress.md`, retorna 0; quando `ids/01K6...json` tem `id` sem artefato e `ts_utc` de 10 dias atras, retorna 0 com aviso e 1 com `--strict`; quando o mesmo `pa-000012` aparece em dois registros com `created_at`, retorna 1, e quando aparece em um registro com `created_at` e outro so com `status`, retorna 0; quando `### D-005:` aparece duas vezes, retorna 1; quando um registro tem `id` diferente de `visible_id(uid)`, retorna 1; quando `--output-dir` aponta para pasta inexistente, retorna 0 sem saida; no fixture limpo, retorna 0 e `--json` tem `schema_version` e listas vazias.
- [ ] Done

### Step 9: Registrar o verificador no registry, no preflight rapido e no pre-skill
Acrescentar a entrada de `check_ledger_ids.py` em `check_plugin_registry.json`; acrescentar `("ledger-ids", [sys.executable, str(SCRIPTS_DIR / "check_ledger_ids.py")])` em `FAST_CHECKS` de `run_preflight_fast.py` logo apos `plan-coverage`; no `pre-skill/SKILL.md`, estagio pending-check, acrescentar: rodar `python .claude/skills/scripts/check_ledger_ids.py` e imprimir a saida se nao vazia, sem bloquear. No `CHANGELOG.md`, secao `## [Unreleased]`: linha `<!-- bump: minor -->` (D-005 chama a mudanca de MAJOR na gramatica; em v0.x isso e minor), `### Changed` com o formato novo de ID (`YYYYMMDD-xxxxxx` + `uid:`), `_output/ids/`, INDEX.md derivado e o verificador, e um paragrafo **Upgrade**: "devs que compartilham um ledger devem atualizar juntos: um harness anterior continua emitindo IDs legados, indexa artefatos novos como Other, nao os rastreia em coverage/pending e **recusa commitar** marcadores `plan-YYYYMMDD-xxxxxx` em arquivos Human (markers); IDs legados continuam validos para sempre; `migrate_qa_logs_to_parent_dirs.py` e os `backfill_*.py` continuam so para o formato legado". Acrescentar um bullet no resumo do passo 6 de `_internal/seja-setup/upgrade/SKILL.md`: "se `_output/ids/` nao existe, nada a migrar; IDs legados ficam".
- **Files**: `.claude/skills/scripts/check_plugin_registry.json` (modify), `.claude/skills/scripts/run_preflight_fast.py` (modify), `.claude/skills/pre-skill/SKILL.md` (modify), `CHANGELOG.md` (modify), `.claude/skills/_internal/seja-setup/upgrade/SKILL.md` (modify)
- **References**: `product-design/standards.md § Testing > 4`
- **Depends on**: Step 8
- **Interface**: N/A
- **Verify**: `python3 .claude/skills/scripts/run_all_checks.py` lista `check_ledger_ids.py`; `run_preflight_fast.py` mostra `ledger-ids`; `check_version_changelog_sync.py` continua passando
- **Tests**: N/A (configuracao; coberto pelo Step 8 e pelos verificadores de registry/changelog)
- **Docs**: `CHANGELOG.md` (Unreleased)
- [ ] Done

### Step 10: Atualizar referencias e agentes: a definicao do ID e o header com uid
Em `report-conventions.md:9`, substituir a definicao do *id* por: ID visivel `YYYYMMDD-xxxxxx` derivado de um ULID gerado localmente por `reserve_id.py` (artefatos anteriores a esta versao mantem o numero sequencial de 6 digitos; os dois formatos sao validos); acrescentar o campo *uid* (linha `uid: <ULID>` imediatamente apos o header, antes de `source:`/`tags:`) e atualizar o padrao de nome de arquivo. Em `template/docs/ddr.md:78` e nos tres agentes listados (communication-generator.md:24, explanation-generator.md:22, onboarding-generator.md:27) trocar "reserved 6-digit ID" por "reserved artifact ID (see report-conventions)". Em `batch-execution-pattern.md:22`, ajustar a frase sobre reservar IDs antecipadamente (continua valida; nota de que a unicidade agora e local). Os agentes `architecture-explainer` e `evolution-explainer` ficam para o Step 13.
- **Files**: `.claude/references/general/report-conventions.md` (modify), `.claude/references/template/docs/ddr.md` (modify), `.claude/agents/communication-generator.md` (modify), `.claude/agents/explanation-generator.md` (modify), `.claude/agents/onboarding-generator.md` (modify)
- **References**: `product-design/standards.md § Backend > 24`
- **Depends on**: Step 2
- **Interface**: N/A
- **Verify**: `grep -rn "6-digit" .claude/references .claude/agents` so retorna mencoes historicas explicitas e os dois agentes do Step 13; `check_docs.py` e `check_skill_spec.py` sem falha nova
- **Tests**: N/A (prosa de referencia)
- **Docs**: as proprias referencias
- [ ] Done

### Step 11: Atualizar as skills que reservam ID e escrevem o header (primeira leva)
Nas skills `plan` (SKILL.md:87), `research` (:50, :75), `reflect` (:51, :148, :231 e o regex do macro-index citado no fim), `implement` (:33 "The 6-digit ID of the plan"; `pre-plan-<id>` funciona com os dois formatos) e `_internal/explain/drift/SKILL.md:21` (`plan-NNNNNN` -> aceitar o formato novo): trocar "6-digit zero-padded ID" por "artifact ID returned by reserve_id.py" e acrescentar, no padrao de header de cada uma, a linha `uid: <ULID>` logo apos o H1 (valor de `reserve_id.py --json` ou de `_output/ids/<uid>.json`). As skills internas `_internal/plan/*` nao citam o formato nem montam o header (grep): sem edicao. Rodar `generate_skills_manifest.py` e `check_skill_spec.py` ao final.
- **Files**: `.claude/skills/plan/SKILL.md` (modify), `.claude/skills/research/SKILL.md` (modify), `.claude/skills/reflect/SKILL.md` (modify), `.claude/skills/implement/SKILL.md` (modify), `.claude/skills/_internal/explain/drift/SKILL.md` (modify)
- **References**: `product-design/standards.md § Backend > 25`
- **Depends on**: Step 10
- **Interface**: N/A
- **Verify**: `check_skill_spec.py` e `check_skill_system.py` sem falha nova; `generate_skills_manifest.py --check` passa
- **Tests**: N/A (prosa de skill; comportamento coberto pelos Steps 2-7)
- **Docs**: as proprias skills; `SKILL-quickguide.md` de `plan` e `research` se citarem o formato do ID
- [ ] Done

### Step 12: Segunda leva de skills
Mesma edicao do Step 11 em `communicate` (:71, :82, :116), `onboard` (:66, :99, :150), `explain` (:53), `critique` (:52, :193, :205, :257), `mob` (:65).
- **Files**: `.claude/skills/communicate/SKILL.md` (modify), `.claude/skills/onboard/SKILL.md` (modify), `.claude/skills/explain/SKILL.md` (modify), `.claude/skills/critique/SKILL.md` (modify), `.claude/skills/mob/SKILL.md` (modify)
- **References**: `product-design/standards.md § Backend > 25`
- **Depends on**: Step 11
- **Interface**: N/A
- **Verify**: `check_skill_spec.py`, `check_skill_system.py` e `generate_skills_manifest.py --check` sem falha nova
- **Tests**: N/A (prosa de skill)
- [ ] Done

### Step 13: qa-log, agentes restantes e ensaio ponta a ponta
Mesma edicao em `qa-log/SKILL.md` (:33, :51) e nos agentes `architecture-explainer.md:21` e `evolution-explainer.md:21` ("reserved 6-digit ID" -> "reserved artifact ID (see report-conventions)"). Depois, ensaio: em um clone temporario deste repo (`git clone . <tmp>`), reservar um ID com `reserve_id.py --type research --title ensaio`, criar `_output/research-logs/research-<id>-ensaio.md` com header no formato novo e linha `uid:`, rodar `generate_macro_index.py`, `update_cross_refs.py`, `check_ledger_ids.py` e `check_plan_coverage.py --mode blocking`, e conferir que o artefato aparece no INDEX.md com o ID novo e nenhum verificador falha; conferir tambem que `grep -rn "6-digit" .claude/` so retorna mencoes historicas. Registrar o resultado na nota do step.
- **Files**: `.claude/skills/qa-log/SKILL.md` (modify), `.claude/agents/architecture-explainer.md` (modify), `.claude/agents/evolution-explainer.md` (modify)
- **References**: `product-design/standards.md § Backend > 24, 25`
- **Depends on**: Step 12, Step 14
- **Interface**: N/A
- **Verify**: ensaio com exit 0 em todos os scripts; `pytest .claude/skills/scripts/tests/` verde; `run_all_checks.py` sem falha nova
- **Tests**: N/A (prosa mais ensaio manual registrado na nota do step)
- [ ] Done

### Step 14: Alargar os parsers do ciclo default que ficaram fora do levantamento
Emenda 2026-10-07 (conferencia do terreno depois do merge `8f8a601`): este plano foi escrito no lado de `origin/dev`, sem os scripts do ciclo default (plans 000007-000015, 000022). Dois parsers deles nao aceitam o ID novo. `check_plan_scenarios.py:119` `PLAN_FILE_RE = ^plan-\d{6}-.+\.md$` -> usar `artifact_id.ARTIFACT_ID` (a varredura sem argumento passaria a ignorar planos com ULID). `build_brief.py:288` `re.match(r"(plan-\d+)", path.name)` -> `plan-` + `ARTIFACT_ID` (hoje um nome `plan-20261007-k3m9qz-x.md` vira `plan-20261007`, truncado, sem erro). `cycle_adherence.py:77` ja aceita os dois formatos: trocar o padrao local por `artifact_id.ARTIFACT_ID` para ter uma fonte so. Antes de editar, refazer o grep de `\d{6}`, `\d+` junto de `plan-`, `zfill(6)` e `:06d` em `.claude/` e acrescentar aqui o que mais aparecer.
- **Files**: `.claude/skills/scripts/check_plan_scenarios.py` (modify), `.claude/skills/scripts/build_brief.py` (modify), `.claude/skills/scripts/cycle_adherence.py` (modify), `.claude/skills/scripts/tests/test_check_plan_scenarios.py` (modify), `.claude/skills/scripts/tests/test_build_brief.py` (modify)
- **References**: `product-design/standards.md § Backend > 19`
- **Depends on**: Step 1
- **Interface**: N/A
- **Verify**: `pytest .claude/skills/scripts/tests/test_check_plan_scenarios.py .claude/skills/scripts/tests/test_build_brief.py .claude/skills/scripts/tests/test_cycle_adherence.py` verdes; todas as fixtures de `plan_scenarios/` com o `esperado.json` igual
- **Tests**: quando a varredura do `check_plan_scenarios.py` encontra `plan-20261007-k3m9qz-x.md` v2 aberto, ela o verifica; quando `build_brief` recebe `plan-20261007-k3m9qz-x.md`, o ID extraido e `plan-20261007-k3m9qz`; quando recebe `plan-000022-x.md`, continua `plan-000022`
- [ ] Done

## Coverage (advisory)

Review depth overridden: auto=deep (X-scope, >8 files), floor=light, flag=none, effective=deep.

`check_plan_coverage.py --mode advisory`: 0/40 requisitos rastreados. Nenhum REQ-* do `product-design-as-intended.md` descreve identidade de artefato ou o ledger; este plano implementa D-005 (decisao), nao um REQ. Sem `Traces:` nos steps por isso.

## Outcomes

- Dois devs em maquinas diferentes rodam qualquer skill ao mesmo tempo sem colisao de ID e sem combinar nada; o merge de `_output/ids/` nunca conflita.
- INDEX.md deixa de carregar estado de alocacao: e regeneravel a qualquer momento, e as linhas RESERVED orfas de hoje (000002, 000003, 000007, 000009, 000015) desaparecem.
- Toda regex e marcador do harness aceita os dois formatos; nenhum artefato existente muda de nome (T3).
- `check_ledger_ids.py` acusa ID duplicado, registro orfao, `pa-`/`D-NNN` duplicado, no pre-skill, no preflight rapido e no `run_all_checks.py`.
- Os dois bugs do `apply_marker`/`check_human_markers_only` achados em 2026-10-06 ficam corrigidos com teste.
- O `uid:` passa a existir em todo artefato novo: e a chave que R2-4 (apelidos) e o seja-mcp (H-007) vao consumir.

## Smoke

false

## Metacomm Intention
- **Summary**: Eu dou a cada artefato uma identidade que nasce na sua maquina e nunca colide com a de outro dev, mantenho a ordem na sua arvore de arquivos, aceito os IDs antigos sem lhe pedir para reescrever nada, e lhe aviso antes do commit quando dois artefatos tiverem o mesmo ID.
- **Source**: agent (metacomm)

## Review Log

**Review depth:** Deep (overridden; auto=deep, floor=light, flag=none)
**Deep-dive budget:** 6/6 used

### Step metadata validation (pre-scan)

- Todos os steps com Files / References / Interface / Verify / Tests / checkbox; dependencias fluem para a frente.
- Antes da emenda, os Steps 6, 10 e 11 descreviam edicoes em arquivos fora das suas listas (Step 6 nomeava 7 scripts; Step 11, 8 arquivos); um caminho inexistente (`post-skill/backfill_decision_digest.py`; o script vive em `scripts/`). Corrigido na emenda (split 6/7 e 12/13; renumeracao).
- Cobertura: o plano implementa D-005, sem REQ rastreavel; coerente com o aviso do `check_plan_coverage --mode advisory`.

### Phase 1 -- Perspective Scan (2026-10-06 23:40 UTC)

| Perspective | Status | Concern |
|-------------|--------|---------|
| SEC | Deferred | allowlist `*Source: .{1,200}*` mais larga do que o `apply_marker.py:265` escreve; `--origin` sem validacao; strip do prefixo D-NNN subespecificado -- Phase 2 |
| DB | N/A | sem banco |
| API | Adopted | contrato de stdout do `reserve_id.py` (ID puro) preservado; nenhum chamador parseia alem do ID nem importa `_extract_max_id`/`_format_id`; `--json` e opt-in |
| ARCH | Deferred | "INDEX.md derivado" esquecia os regexes de QA companheiro em `generate_macro_index.py:282,296,310`; `finalize_reserved` sem chamadores mas `--finalize` existe; scripts novos precisam constar em `docs/reference/harness-reference.md` (preflight `harness-reference-coverage`) -- Phase 2 |
| UX | Adopted | stdout = ID puro (scriptavel) + `--json`; recomendacao: imprimir `uid:` em stderr para o humano ver sem quebrar a captura (incorporado no Step 2) |
| A11Y | N/A | sem UI |
| I18N | N/A | sem i18n em runtime |
| TEST | Deferred | Files/escopo do Step 6 em desacordo; `test_apply_marker.py:641` fica vermelho se a mensagem de erro for reescrita -- Phase 2 |
| DX | Deferred (acrescentada: mudanca de formato interna toca 15+ arquivos) | Steps 10/11 nomeavam `qa-log/SKILL.md` e dois agentes fora das Files; skills internas de plan nao precisam de edicao; tolerancia a METACOMM so no macro-index -- Phase 2 |
| COMPAT | Deferred (acrescentada: versoes mistas do harness numa branch) | sem nota de CHANGELOG/upgrade; comportamento do harness antigo com artefatos novos nao analisado; `pending.jsonl` nao tem campo `action` -- Phase 2 |
| OPS | Adopted (com rationale) | `check_ledger_ids` no pre-skill a cada invocacao: `rglob` barato neste tamanho de ledger; deve sair 0 em silencio sem `OUTPUT_DIR` (adicionado ao Step 8); `critical: true` defensavel |
| DATA | Deferred (acrescentada: registro persistente novo com campo pessoal) | `author = git config user.name` em `_output/ids/*.json` viola a constituicao **C2**; `visible_id(ulid, when)` deixa `id` derivar de `uid` -- Phase 2 |

### Phase 2 -- Deep-dive: DATA (iteration 1, deep-dive 1/6)

**Concern:** nome de pessoa persistido no ledger; `id` nao e funcao pura de `uid`.
**Step ref:** Step 1, Step 2.
**Files read:** `product-design/constitution.md` (C2, S3), D-005, `_output/pending.jsonl`, `_output/briefs.md`, `tools/publish-manifest.txt`.
**Finding:** D-005 diz que o registro de nascimento carrega "autor", e o Step 1 o resolvia de `git config user.name`. C2 proibe nome de pessoa em `_output/`; hoje nenhum arquivo de `_output/` carrega o nome do usuario git, e este plano introduziria o primeiro. `_output/**` fica fora de `main` pelo manifesto, mas `dev` e visivel a organizacao, exatamente o que C2 protege. `visible_id(ulid, when=None)` tomava a data de um relogio externo enquanto `ts_utc` vem do registro: dois relogios podem discordar na virada de dia UTC, e nada permitiria ao verificador conferir `id == f(uid)`. Crockford base32 (0-9, A-Z sem I/L/O/U) em minusculas cabe inteira em `[0-9a-z]`; os 6 ultimos chars sao os 30 bits baixos da parte aleatoria, logo P(colisao num dia) ~ n^2 / 2^31 (n=100 -> 5e-6; n=1000 -> 5e-4), adequado com o verificador.
**Recommendation:** (a) `author` = token pseudonimo `sha256(git config user.email)[:12]` (fallback `sha256($USER)`), sobrescrevivel por `--author`; nunca `user.name`. (b) `visible_id(ulid)` deriva `YYYYMMDD` do timestamp do ULID; `check_ledger_ids` ganha a verificacao (6) `id == visible_id(uid)`.
**Resolution:** Plano emendado -- Steps 1, 2 e 8. Nota ao designer: isto estreita o "autor" literal de D-005; a constituicao prevalece; registrar o estreitamento via `/design` se desejar.

### Phase 2 -- Deep-dive: SEC (iteration 1, deep-dive 2/6)

**Concern:** alargamento da allowlist podia deixar prosa passar; `--origin` sem validacao; prefixo D-NNN.
**Step ref:** Step 4, Step 2.
**Files read:** `human_markers_registry.py:60-160`, `apply_marker.py:195-330,410-440`, `check_human_markers_only.py:91-150`, `explain/check_changelog_append_only.py`, `security-checklists.md` (K, O).
**Finding:** `_line_is_allowed` faz `fullmatch` de cada linha do diff contra todos os regexes do registry. `\*Source: .{1,200}\*` aceitaria qualquer linha em italico comecando por `Source:`: um canal de 200 chars de prosa num arquivo Human (markers). O `apply_marker.py:265` escreve exatamente `*Source: {note} ({date})*`, entao a allowlist pode ter essa forma exata. Alargar `plan-\d{6}` e seguro em STATUS, ESTABLISHED, INCORPORATED e CHANGELOG_APPEND, e `check_changelog_append_only.py` herda. Mapear `manual -> "-"` em `_apply_changelog` e correto contra `:118-120` e deve ficar restrito a CHANGELOG_APPEND. `_apply_decision` usa a primeira linha do valor como titulo, por isso um titulo ja iniciado por `D-005:` duplica. `--origin` ia direto ao JSON.
**Recommendation:** alternativa DECISION_APPEND = `\*Source: [^*<>\n]{1,200} \(\d{4}-\d{2}-\d{2}\)\*`; manter a substring `--plan must be 'plan-NNNNNN'` na mensagem de erro; validar `--origin`.
**Resolution:** Plano emendado -- Steps 2 e 4.

### Phase 2 -- Deep-dive: ARCH (iteration 1, deep-dive 3/6)

**Concern:** INDEX.md fica mesmo inteiramente derivado? Consumidores de RESERVED/ID esquecidos?
**Step ref:** Step 3, Steps 1/2/8.
**Files read:** `generate_macro_index.py:88-220,276-312,370-400,575-760`, `_output/INDEX.md:11-35`, `plan-000007-*.md:1`, `check_docs.py:776-1030`, `docs/reference/harness-reference.md`, `run_preflight_fast.py:45-90`, `tests/test_generate_macro_index.py`.
**Finding:** `_extract_reserved_rows` e o merge-back sao os unicos consumidores de RESERVED alem de `finalize_reserved`, que nao tem chamadores nem teste. Os regexes de plano exigem `Plan (\d+) | (\S+) | data`; os planos com `| METACOMM |` caem em "Other" e suas linhas RESERVED persistem. **Omitido**: `:282`, `:296`, `:310` detectam QA companheiro com `^plan-\d{6}-qa-`; um QA log de plano novo seria tipado como Plan e contado como duplicado pelo verificador. `docs/reference/harness-reference.md` e declarado gerado por `priv/generate_harness_reference.py` (ausente aqui), e o plugin `harness-reference-coverage` avisa para todo script nao mencionado; `artifact_id.py` e `check_ledger_ids.py` precisam de linhas a mao. Remover as linhas RESERVED orfas e permitido sob T3: INDEX.md e arquivo regenerado, e linhas RESERVED sao estado de alocacao, nao artefatos; registrar as removidas na nota do step.
**Recommendation:** incluir os tres regexes de QA no Step 3; `--finalize` vira no-op com aviso; linhas no harness-reference nos Steps 1 e 8.
**Resolution:** Plano emendado -- Steps 1, 3, 8.

### Phase 2 -- Deep-dive: COMPAT (iteration 1, deep-dive 4/6)

**Concern:** versoes mistas do harness numa branch; deteccao de `pa-` duplicado; caminho de upgrade.
**Step ref:** Steps 8, 9.
**Files read:** `pending.py:50-60,118-200,234-320,442-462`, `_output/pending.jsonl`, `CHANGELOG.md:1-25`, `.seja-version`, `_internal/seja-setup/upgrade/SKILL.md:39-66`, `reserve_id.py:44`.
**Finding:** um dev ainda em v0.10.1 que puxa artefatos novos: o `reserve_id.py` antigo ignora as linhas novas e segue alocando legado max+1 (a janela de colisao legada fica aberta para ele); o macro-index antigo indexa os arquivos novos como "Other" sem ID; o `check_plan_coverage` antigo pula planos novos; o `apply_marker` antigo rejeita `--plan 20261007-...` e o `check_human_markers_only` antigo **bloqueia o commit** de qualquer arquivo com marcador no formato novo; o `pending.py` antigo nunca orfana `source: plan-2026...`. Nada corrompe dados, mas e invisivel ao dev. Registros de `pending.jsonl` **nao** tem campo `action`: criacao carrega `created_at/type/source/description/status`; atualizacoes so `id/status/closed_at` (ou `snooze_until`).
**Recommendation:** Step 8(3): `pa-` duplicado = dois registros com o mesmo `id` ambos com `created_at`. Step 9: CHANGELOG `## [Unreleased]` com `<!-- bump: minor -->`, `### Changed` e paragrafo Upgrade ("devs que compartilham um ledger atualizam juntos"); bullet no passo 6 do upgrade do seja-setup.
**Resolution:** Plano emendado -- Steps 8, 9.

### Phase 2 -- Deep-dive: TEST (iteration 1, deep-dive 5/6)

**Concern:** escopo do Step 6 versus Files; quais asserts existentes ficam vermelhos.
**Step ref:** Steps 5, 6, 4.
**Files read:** `tests/conftest.py`, `tests/test_apply_marker.py:483-642`, `tests/test_check_human_markers_only.py:209-240`, `tests/test_pending.py`, `tests/test_generate_macro_index.py`, `reflect_deep_scope.py:110-116`, `generate_reflection_report.py:496-503`, `update_cross_refs.py:72-100`, `step_notes.py:100-112`.
**Finding:** `conftest.py` poe `scripts/` e as pastas das skills no `sys.path`, entao `import artifact_id` funciona nos testes de todos os modulos do plano. O Step 6 nomeava sete scripts e listava quatro: `reflect_deep_scope.py:113` (`PLAN\s*\|\s*(\d+)` truncaria o ID novo em `20261007`; **precisa** mudar) e `backfill_decision_digest.py` (caminho errado; migracao legada; excluir). `generate_reflection_report.py:500`, `update_cross_refs.py:93,100` e `step_notes.py:102` usam `zfill(6)`, no-op num ID de 15 chars (so o `isdigit()` de `update_cross_refs.py:80` muda). Asserts vermelhos: `test_apply_marker.py:641` (`"--plan must be 'plan-NNNNNN'" in result.stderr`) se a mensagem for reescrita; `test_check_human_markers_only.py::test_other_bold_label_lines_still_rejected` so fica verde com a allowlist estrita; nenhum teste exercita RESERVED/finalize nem importa internos do `reserve_id`.
**Recommendation:** Step 6 com os cinco scripts que mudam; testes num step proprio (Step 7); manter a substring da mensagem no Step 4.
**Resolution:** Plano emendado -- Steps 4, 6, 7.

### Phase 2 -- Deep-dive: DX (iteration 1, deep-dive 6/6)

**Concern:** Steps 10/11 editavam arquivos fora das suas Files; sites `\d{6}` nao classificados.
**Step ref:** Steps 9, 10, 11 (originais); grep.
**Files read:** grep `\d{6}` em `.claude/` e `tools/` (sem testes), `_internal/plan/**`, `qa-log/SKILL.md:33,51`, `architecture-explainer.md:21`, `evolution-explainer.md:21`, `implement/SKILL.md:33,53`, `summarize_artifacts.py:29-30`, `generate_pending_roadmap.py:52,55`.
**Finding:** (1) `_internal/plan/standard|light|roadmap` nem citam "6-digit" nem montam o header; sem edicao. (2) `qa-log/SKILL.md` e os dois agentes estavam fora das Files. (3) Inventario completo de `\d{6}` com disposicao: `generate_macro_index.py:282,296,310` (alargar, Step 3); `backfill_open_plans.py:59-67`, `backfill_qa_dates.py:148`, `migrate_qa_logs_to_parent_dirs.py:44`, `_internal/seja-setup/upgrade/SKILL.md:59` (migracoes legadas; deixar); `conversation_trace.py:58` (IDs de evento; deixar); `pending.py:50` (R2-5; deixar). (4) `summarize_artifacts.py:29-30` e `generate_pending_roadmap.py:52,55` tambem nao toleram `| METACOMM |`; um token por regex nos Steps 5/6. (5) `git branch pre-plan-20261007-k3m9qz` e nome de ref valido.
**Recommendation:** split do Step 11 (skills) e 13 (qa-log, agentes, ensaio); tirar as skills internas do Step 11; tolerancia a METACOMM nos Steps 5/6; listar os sites a deixar no texto do Step 5.
**Resolution:** Plano emendado -- Steps 5, 6, 11, 12, 13.

### Conflict Check (iteration 1)

Um conflito: DATA/SEC (constituicao C2, sem nome de pessoa em `_output/`) versus a redacao literal de D-005 ("registro de nascimento: ... autor"). Resolvido pela regra default (SEC prevalece): `author` vira token pseudonimo com `--author` explicito; o designer pode re-decidir via `/design`. Sem outros conflitos: os splits de TEST e DX acrescentam steps mantendo cada um em <= 5 arquivos; a nota de CHANGELOG (COMPAT) e as linhas do harness-reference (ARCH) sao aditivas.

### Iteration 2 -- re-evaluation (sem deep-dives novos; orcamento esgotado)

| Perspective | Status | Note |
|-------------|--------|------|
| SEC | Adopted | allowlist estrita; `--origin` validado; strip de prefixo especificado |
| ARCH | Adopted | regexes de QA incluidos; `--finalize` depreciado; harness-reference nos Steps 1/2/8 |
| COMPAT | Adopted | regra do registro de criacao; CHANGELOG + nota de upgrade |
| TEST | Adopted | split 6/7; assert vermelho listado |
| DX | Adopted | split 11/12/13; inventario `\d{6}` classificado |
| DATA | Adopted | autor pseudonimo; `id = f(uid)` + verificacao (6) |

### Execution Metrics

| Metric | Value |
|--------|-------|
| Deep-dives used | 6/6 |
| Iterations completed | 2/3 |
| Perspectives shortlisted | 12 (8 default + DX, COMPAT, OPS, DATA) |
| Perspectives Adopted | 9 (API, UX, OPS na iteracao 1; SEC, ARCH, COMPAT, TEST, DX, DATA na iteracao 2) |
| Perspectives Deferred (with rationale) | 0 (3 N/A: DB, A11Y, I18N) |
| Convergence reason | all resolved; deep-dive budget reached |

### Plan Amendment (iteration 1)

**Change summary**: (A1) `author` pseudonimo e `id` derivado do timestamp do ULID (C2, DATA); (A2) allowlist `*Source:*` exata, validacao de `--origin`, strip do prefixo D-NNN, substring da mensagem de erro mantida (SEC/TEST); (A3) regexes de QA `:282/:296/:310`, `--finalize` depreciado, linhas no harness-reference (ARCH); (A4) Step 6 original dividido em 6 e 7 com Files corrigidas (TEST); (A5) regra de registro de criacao para `pa-`, comportamento sem `OUTPUT_DIR`, verificacao (6) (COMPAT/OPS/DATA); (A6) CHANGELOG com nota de upgrade e bullet no upgrade do seja-setup (COMPAT); (A7) Step 11 original dividido em 12 e 13, Step 10 original enxugado, tolerancia a METACOMM nos Steps 5/6 (DX). Steps renumerados 1-13 (6b -> 7, 11b -> 13; os demais deslocados).

**Rationale**: a constituicao C2 e as regras de seguranca prevalecem sobre a redacao literal de D-005; o preflight do harness (`harness-reference-coverage`, `check_human_markers_only`) falharia ou seria afrouxado; tres steps excediam suas Files como escritos.

**Asserts que ficam vermelhos para o implementador**: `test_apply_marker.py:641` se a mensagem for reescrita (o Step 4 emendado mantem a substring); `test_check_human_markers_only.py:227` so se a allowlist for mais larga que a forma exata; preflight `harness-reference-coverage` ate as linhas de `artifact_id.py` e `check_ledger_ids.py` entrarem; `check_version_changelog_sync.py` se o bump do CHANGELOG discordar do `.seja-version`; `check_ledger_ids.py` neste repo antes do Step 3 (linhas RESERVED orfas).

## Adendo 2026-10-07 -- renumeração da decisão

A decisão de ULID citada neste artefato como **D-005** passou a **D-010** no merge de `origin/dev` em `dev` (2026-10-07, commit `8f8a601`): duas sessões de 2026-10-06 numeraram D-005 em paralelo, e a D-005 do ciclo default (grill e specify como fases do `/plan`) ficou com o número. Leia D-005 acima como D-010. O texto acima não foi alterado (T3).

## Emenda 2026-10-07 -- registro de nascimento sem autor e parsers do ciclo default

- **Sem autor.** Decisão do designer em 2026-10-07: o registro de nascimento não guarda autor. Quem criou o artefato fica no commit do git. Isso substitui a recomendação (a) do deep-dive DATA e a emenda A1 deste plano (token `sha256(email)[:12]` e `--author`), e resolve de outro jeito o conflito C2 x "autor" registrado no Conflict Check. Steps 1 e 2 editados in place: `default_author()` e `--author` saem; `birth_record` perde o parâmetro e a chave `author`. A D-010 ainda cita "autor" no registro de nascimento; a mudança da prosa é do designer (`/design`, T4).
- **Terreno.** Este plano foi escrito em `origin/dev`, sem os 98 commits do ciclo default (plans 000007 a 000015) nem o plan-000022, integrados no merge `8f8a601`. Um grep de padrões de ID nos scripts acrescentados desde então achou dois parsers fora dos Steps 5 e 6: `check_plan_scenarios.py:119` e `build_brief.py:288`. Entram no Step 14 novo, junto com a unificação do padrão do `cycle_adherence.py`. O Step 13 (ensaio ponta a ponta) passa a depender também do Step 14.
- **Versão.** O plan-000022 colocou o interruptor da specify na v0.11.0 (seção do CHANGELOG cortada, sem tag) e o PKB (plan-000020) na v0.12.0. A entrada de CHANGELOG deste plano (`[Unreleased]`, `bump: minor`) fica para a release em que ele sair; a sequência é do designer.

## Emenda 2026-10-07 (2) -- o autor fica

O designer revisou a decisão da emenda anterior e manteve o autor no registro de nascimento, como a D-010 já diz. Vale de novo a recomendação (a) do deep-dive DATA e a emenda A1: `author` é o token pseudônimo `sha256(git config user.email)[:12]` (fallback `sha256($USER)`, senão `"unknown"`), sobrescrevível por `--author`, nunca `user.name` (C2). Os Steps 1 e 2 voltaram ao texto anterior à emenda. Não há D-NNN nova: a D-010 continua valendo como está. O item "Sem autor" da emenda anterior fica sem efeito; os itens "Terreno" (Step 14) e "Versão" continuam valendo.
