# The PKB layer

An optional layer that turns what you say to the agent into a personal knowledge base you can review later. It adds an inbox, daily logs, note templates, a goals map and a catalogue, plus a capture step that runs after each skill. Nothing in the SEJA cycle depends on it: a project without the layer behaves as before.

The method (GTD, PARA, Zettelkasten) comes from the public bootstrap at `https://github.com/PUC-Behring-AI/personal_knowledge_base_bootstrap.git`.

## What the layer contains

| Item | Purpose |
|---|---|
| `inbox/` | Quick capture. Everything lands here before you sort it. Holds `README.md` and the generated `_live.md`. |
| `logs/` | Daily logs (`logs/YYYY/YYYY-MM-DD.md`), period summaries and `logs/log.md`. |
| `Templates/` | Six note templates: daily, paper, project, weekly, monthly and quarterly summary. |
| `Objetivos.md` | Goals map, one level above projects. |
| `index.md` | Human catalogue of the notes. |
| 5 maintenance skills | `daily-log`, `weekly-review`, `compress`, `next-action`, `process-inbox`. Optional. |

New notes carry frontmatter: `origem`, `tipo`, `tags`, `data` (always `YYYY-MM-DD`).

## Installing it

```
/seja-setup <target> --pkb          # also valid with --here and --demo
python .claude/skills/scripts/pkb_inbox.py init [--target DIR] [--with-skills] [--dry-run] [--json]
```

- Without `--pkb`, install, `--here` and `--demo` ask once whether you want the layer.
- `init` never overwrites a file you already have. It lists what it created and what it skipped. It never edits your `CLAUDE.md`: it only prints the line to add.
- `--with-skills` copies the five maintenance skills into `<target>/.claude/skills/`. Without it you get the notes and templates only.

## The switch

The layer is on when `PKB_DIR` in `product-design/conventions.md` is non-empty and `<PKB_DIR>/README.md` exists. The default is `inbox`. To turn capture off, empty the `PKB_DIR` value or delete the README. When the layer is off, the capture step stays silent.

## Capture

After a skill finishes, post-skill step 7f runs:

```
python .claude/skills/scripts/pkb_inbox.py capture --skill <skill> --artifact <id or path> --session-id $CLAUDE_SESSION_ID --json
python .claude/skills/scripts/pkb_inbox.py digest
```

`capture` writes one note in `<PKB_DIR>/` named `YYYY-MM-DD-<skill>-<artifact id>-<slug>.md`. The body holds your own words, quoted with the time. The frontmatter records `skill`, `artefato`, `fonte` (the event ids, or `briefs`), `mascarado`, and, for a plan, `as_expressed_igual_ao_brief`. Running it again for the same note appends a dated section instead of duplicating it.

Where the words come from:

1. The conversation trace. `conversation_trace.py list --session-id ID [--led-to-skill S] [--since-evt E]` prints a session's entries as JSON. `exchange_user_entries` (library function) finds your utterances by walking back from each agent reply tagged with the skill, following `preceding_evt_id` through user entries until it reaches an agent entry or another skill.
2. The brief, when the trace gives nothing.

The step stages `<PKB_DIR>/` into the same commit as the skill's artifacts.

### Limits you should know

- **Capture depends on the exchange chain.** It needs `preceding_evt_id` to be recorded correctly and a real `CLAUDE_SESSION_ID`. If the agent skipped the flag (the default is `null`) or the session id is missing, your utterances are not reached.
- **No trace, brief only.** In that case the note holds the brief alone and `fonte: briefs`. With neither trace nor brief, nothing is written (`nothing-to-capture`).
- **Masking is on, and it flags.** Text matching the harness secret patterns is replaced by `[MASKED:<name>]` and the note gets `mascarado: true`; post-skill prints one warning line. The patterns are the harness ones: a key written without quotes may not match. Read the note before you share it.
- **`as_expressed_igual_ao_brief` is a weak signal.** It compares your words with the plan's `User brief` after normalising case, quotes and spacing. It says whether they differ, not why.
- **The five PKB skills ship only in the template** (`.claude/references/template/pkb/skills`). They are not in the harness `.claude/skills/` and appear in a project only after `init --with-skills`. Their `SKILL.md` files are in pt-BR, because the method and its audience are.
- **The layer folders are not distributed.** The public `main` branch carries the template and the tooling, not `inbox/`, `logs/`, `Templates/`, `Objetivos.md` or `index.md` of the repository that develops the harness (the publish manifest is an allowlist).

## `_live.md`

`pkb_inbox.py digest` regenerates `<PKB_DIR>/_live.md`: a chronological table of the captures with date, skill, first quote, links to the note and the artifact, and a "Comunicado em" column that links the `communication-*.md` files that cite the artifact in their first 12 lines. It is deterministic: two runs give identical bytes.

`_live.md` is preparation, not emission. Nothing in it has passed `/critique` or left the project, so P-005 (validate before you communicate) is untouched. Do not edit it. If a file called `_live.md` exists and was not generated by `digest`, the command stops with an error and leaves it alone.

## The design trigger

Post-skill step 2c can recommend `/design` before your next `/plan`. It reads `DESIGN_TRIGGER_DRIFT_ITEMS` in `conventions.md`:

- Empty (the default): off. Nothing is printed.
- A number N: when a measured drift report shows N or more drift items, or when the skill was `/plan` and capture reported `as_expressed_igual_ao_brief: false`, the step prints a one-line recommendation. A drift that was not measured is printed as "deriva: nao medida".

The line is informational and never blocks. You fix the threshold; the harness never chooses it, and you should fix it before you look at data.

## Upgrades

`/seja-setup --upgrade` preserves `inbox/`, `logs/`, `Templates/`, `Objetivos.md` and the root `index.md`, and prints "camada PKB detectada" when it finds the layer. After the copy it offers to run `init` if the layer is missing.
