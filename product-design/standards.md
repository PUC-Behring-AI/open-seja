# ENGINEERING STANDARDS -- open-seja

> Padrões de engenharia do open-seja, um harness de agente (skills em Markdown, subagentes, referências e scripts Python de verificação), não uma aplicação. Não há backend web, ORM, banco de dados nem frontend. A seção `## Backend` cobre os **scripts Python do harness e o template de portão**; `## Frontend` é **N/A**; `## Testing` cobre pytest e ruff; `## i18n` é orientação de idioma da documentação.
>
> As subseções web do template são mantidas como cabeçalhos **N/A** para que referências cruzadas do tipo "standards.md § Backend > N" continuem reconhecíveis.

---

## Backend

> **Escopo:** scripts em `.claude/skills/scripts/` e scripts co-localizados com skills (`.claude/skills/<skill>/*.py`), mais o template de portão em `.claude/references/template/quality-gate/<stack>/`.

### 1. [Core] Project Structure

```
.claude/
├── skills/<nome>/SKILL.md          # skill de usuário (thin wrapper) + SKILL-quickguide.md irmão
├── skills/_internal/<nome>/SKILL.md # workers internos, lidos pelo wrapper
├── skills/scripts/                 # scripts compartilhados (check_*.py, apply_marker.py, project_config.py, ...)
│   ├── check_plugin_registry.json  # registro dos verificadores
│   └── tests/                      # pytest do harness
├── agents/*.md                     # prompts de subagente (avaliador | gerador)
├── references/general/             # referências agnósticas de projeto
├── references/template/            # templates que o /design e o /seja-setup instanciam
│   └── quality-gate/<stack>/       # portão por stack (python é o primeiro adaptador)
├── rules/*.md                      # regras com escopo por caminho
└── hooks/                          # hooks Stop e PreToolUse do portão
```

**Regras:**
- Skill orquestra, agente executa (constituição T5). Executores não têm arquivo próprio: o `/implement` monta o prompt a partir do step.
- `project_config.py` é o único leitor de `product-design/conventions.md`; scripts não fazem parse próprio das convenções.
- Arquivos `Human (markers)` só recebem escrita por `apply_marker.py` (constituição T4).

### 2. [Core] Application Factory

> **N/A** -- não há aplicação. O ponto de entrada de cada script é `main()` com `argparse`.

### 3. [Core] Configuration

- Configuração de projeto vem de `product-design/conventions.md` via `project_config.py`; nenhum caminho de projeto é fixado no script.
- Variáveis do portão (`GATE_FAST_CMD`, `GATE_FULL_CMD`, `GATE_COMMIT_CMD`, `QUALITY_DIR`) só são editadas por mão humana.

### 4. [Core] Layered Architecture

> Não há camadas web. O equivalente: **skill (conversa) -> script determinístico (verificação) -> artefato (`_output/`, `product-design/`)**. Scripts não chamam LLM nem rede.

### 5. [Core] Exception Hierarchy

- Scripts terminam com código de saída, não com traceback para o usuário: `0` sem achados, `1` com achados, `2` erro de uso ou de script.
- O portão usa um código por categoria: `0` PASS; `1` configuração ou recusa; `2` lint/tipos; `3` testes; `4` CRAP; `5` arquitetura; `6` mutação; `7` marcadores de evasão.

### 6. [Core] Models & Data Handling

> **Sem ORM.** Os dados são arquivos: Markdown com cabeçalho de artefato, JSONL (`telemetry.jsonl`, `pending.jsonl`, `conversation-trace.jsonl`, `decision-digest.jsonl`) e JSON (gate, registro de plugins).

- Artefatos de `_output/` são imutáveis (constituição T3).
- JSON de saída carrega `schema_version`.

### 7. [Core] Authentication & Authorization

> **N/A** -- sem login. A fronteira é de voz (classificações de autoria) e de ratchet (denies e hooks). Ver `product-design-as-intended.md §4`.

### 7b. [Core] Object-Level Authorization (BOLA Prevention)

> **N/A.**

### 8. [Core] Output / Response Patterns

- Saída legível em stdout; diagnóstico em stderr.
- `--json` com `schema_version` para saída consumida por outra ferramenta.
- Determinismo: mesma entrada, mesma saída; nada depende do relógio além de datas passadas por argumento.

### 9. [Extended] Internationalization (i18n)

> Ver `## i18n`.

### 10. [Core] Database Access Patterns

> **N/A** -- sem banco.

### 11. [Core] Migrations

> **N/A.** Mudanças de formato de artefato são feitas por scripts de migração idempotentes com `--dry-run` (ex.: `backfill_decision_digest.py`).

### 12. [Core] Security

- Sem segredo em fonte ou em `_output/` (constituição S3); `check_secrets.py` roda no `/design` e no post-skill.
- O portão roda sem rede e sem chave de API no ambiente filho (S1).
- O agente não move o ratchet nem pula o portão (S2).
- Scripts do harness usam só a biblioteca padrão; dependência externa no harness é decisão de design, não detalhe de implementação.

### 13. [Core] Activity Logging

> `briefs.md`, `telemetry.jsonl`, `conversation-trace.jsonl`, `pending.jsonl`. Ver `product-design-as-intended.md §9`.

### 14. [Core] Testing

> Ver `## Testing`.

### 15. [Extended] Key Libraries

| Componente | Dependências |
|---|---|
| Scripts do harness | biblioteca padrão do Python 3 |
| Template de portão (Python) | ruff, pyright, pytest + coverage (ramos), radon, import-linter, mutmut; `tomllib` (3.11+) com `tomli` como fallback abaixo de 3.11 |

### 16. [Core] Naming Conventions

| Category | Convention | Examples |
|---|---|---|
| Verificadores | `check_<coisa>.py` | `check_human_markers_only.py`, `check_plan_coverage.py` |
| Geradores | `generate_<coisa>.py` | `generate_decision_digest.py` |
| Testes | `test_<módulo>.py` | `test_human_markers_registry.py` |
| Skills | `kebab-case` | `seja-setup`, `post-skill` |
| Arquivos de artefato | minúsculas, `<tipo>-NNNNNN-<slug>.md` | `plan-000007-default-cycle-contract.md` |

### 17. [Extended] File & Media Handling

- UTF-8 sem BOM; sem travessão tipográfico nem aspas curvas em arquivos do harness (`--` e aspas retas).
- Cabeçalho de artefato com ID, prefixo-escopo, data UTC e título; `source:`/`spawned:` quando derivado.

### 18. [Extended] Import/Export

> Ver `product-design-as-intended.md §6`.

### 19. [Core] Service / Script Contract

Verificadores (`check_*.py`):
- registrados em `check_plugin_registry.json`;
- sem LLM e sem rede;
- determinísticos;
- cada regra tem um caso de teste que a dispara e um negativo.

### 20. [Core] Input Validation Policy

- Argumentos validados por `argparse` (`choices`, `type`); uso incorreto sai com `2`.
- Valores de marcador validados por regex em `human_markers_registry.py` antes de qualquer escrita.

### 21. [Core] Logging Standards

- Diagnóstico em stderr; nada de `print()` de depuração em stdout de scripts com `--json`.

### 22. [Core] Dependency Management

- Harness: nenhuma dependência de runtime além da stdlib.
- Template de portão: dependências declaradas como `--dev` no projeto que o instala (`uv add --dev ...`), nunca no harness.

### 23. [Extended] Test Data / Fixtures

- Fixtures escritas antes do código; ficam em `.claude/skills/scripts/tests/fixtures/`.
- Ferramentas externas (ruff, pyright, mutmut) são stubadas nos testes do harness.

### 24. [Extended] API / Tool Documentation

- Cada script abre com o bloco `# designer:` (o que faz, na voz do harness) e a docstring com `Invocation`, `Lifecycle`, exit codes e `Usage`.
- Skills de usuário têm `SKILL-quickguide.md` irmão; `SKILL-rationale.md` quando a justificativa não cabe no SKILL.md.

### 25. [Extended] Module-Level README Convention

- Skills: `SKILL.md` com frontmatter (`metadata.references`, `context_budget`), concisão em instruções para agente, prosa humana não comprimida.

### 26. [Core] Operational Readiness

> **N/A** -- sem serviço implantado. Release por tag `vX.Y.Z` e `main` pelo manifesto (constituição C3).

### 27. [Extended] Async Patterns

> **N/A.**

### 28. [Extended] API Versioning

> Versão do harness em `.seja-version` e tag; JSON de saída versionado por `schema_version`.

---

## Frontend

> **N/A** -- não há frontend. HTML autocontido gerado por `--html` em `/explain`, `/communicate`, `/document` [intended] e o SPO (`generate_spo.py`) são artefatos de leitura, sem framework; se um dia houver UI, restaurar esta seção de `.claude/references/template/standards.md § Frontend`.

---

## Testing

### 1. Backend Testing (pytest)

| Ferramenta | Uso |
|---|---|
| pytest | `pytest .claude/skills/scripts/tests/` (e testes co-localizados, como `.claude/skills/seja-setup/test_*.py`) |
| `tmp_path` | repositórios e arquivos temporários; nunca tocar `product-design/` ou `_output/` reais |

**Regras:**
- Toda regra de verificador tem caso positivo e negativo.
- Testes escritos antes do código (teste-primeiro), vermelhos pelo motivo certo.
- Nada de `skip`/`xfail` sem motivo registrado.

### 2. Frontend Testing (vitest)

> **N/A.**

### 3. E2E Testing (Playwright)

> **N/A.** O equivalente é o ensaio de primeiro ciclo (ex.: plan-000073 step 8).

### 4. Linting & Type Checking

| Check | Comando |
|---|---|
| Lint | `ruff check .claude/skills/` |
| Harness | `python .claude/skills/scripts/run_all_checks.py` |

### 5. Cross-Cutting Rules

- Definição de pronto de mudança no harness: constituição Q1.
- O harness exige de si o que o portão exige dos projetos.

### 6. Smoke Testing (Registry-Driven)

> **N/A** -- sem serviço a atingir.

### 7. Security Testing Patterns

- Testes de `check_secrets.py` e dos hooks do portão (`quality_gate_pretool.py` recusa `--no-verify`, `-n`, `core.hooksPath`, `--accept-baseline`).

---

## i18n

### 1. Languages

| Priority | Locale | Uso |
|---|---|---|
| Primary | `pt-BR` | Sessões de design, `product-design/` (inclui a fundamentação, Q-005 aberta), artefatos do ledger |
| Secondary | `en-US` | `docs/` e README públicos, código, identificadores, mensagens de log, SKILL.md |

### 2. Rules

- Código e identificadores sempre em en-US.
- UTF-8; diacríticos do pt-BR preservados.

### 3. Not Applicable

> Catálogos de tradução, negociação de locale e e-mails localizados: **N/A**.
