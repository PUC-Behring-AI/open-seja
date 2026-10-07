---
designer_description: "When a skill produces a report file under your output directory -- a plan, a research report, a review, a proposal -- I'm the reference that codifies the shared header fields (id, uid, datetime, prefix, scope, source, spawned), the artifact-immutability rule that keeps design history intact, the research tagging scheme, and the ASCII-only character restrictions every authored artifact must pass."
---

# FRAMEWORK - REPORT CONVENTIONS

When a skill produces a report file in `${OUTPUT_DIR}` (see product-design/conventions.md), apply these conventions for common sub-fields:

- *id*: visible ID `YYYYMMDD-xxxxxx` (UTC date plus the last six characters of the ULID, lowercase; e.g., `20261007-k3m9qz`), derived from a ULID that `reserve_id.py` generates locally, with no coordination and no network. Uniqueness is local by construction: two devs on different machines never pick the same ID, and `check_ledger_ids.py` reports any duplicate. Artifacts created before this version keep their 6-digit zero-padded sequential number (e.g., `000042`); both formats are valid everywhere an ID is cited, and old artifacts are never renumbered.
- *uid*: the full ULID behind the *id* (26 chars, Crockford base32), written as the line `uid: <ULID>` immediately after the header, before any `source:`/`spawned:`/`tags:` lines. Take it from `reserve_id.py --json` (field `uid`) or from the birth record `${OUTPUT_DIR}/ids/<uid>.json`. Artifacts with a 6-digit *id* have no `uid:` line.
- *current datetime*: format `YYYY-MM-DD HH:MM` in UTC.
- *prefix* (when applicable): one of `[FEATURE, REDESIGN, FIX, REFACTOR, DOCUMENT, TEST, CHORE]`.
- *scope* (when applicable): one of `[-B backend, -F frontend, -X cross-cutting, -O other]`.
- *short title*: brief descriptive title.
- *user brief*: user-provided description, verbatim.
- *agent interpretation*: processed description after interpreting the user's request.
- *source* (optional): `source: <type>-<id> -- <motivation>` -- artifact that triggered this one; the inline motivation (under 80 chars) lets readers understand why without opening the source. Example: `source: research-000042 -- review perspectives lack communicability vocabulary`.
- *spawned* (optional): `spawned: <type>-<id>[, ...]` -- artifacts created from this one (updated by post-skill).
- *files*: files relevant to the skill output.

### Research tags (optional)

Research reports may include a `tags:` line after the header and any `source:`/`spawned:` lines. Tags are lowercase kebab-case slugs, comma-separated, enabling topic discovery (e.g., `grep "tags:.*notification-system" _output/research-logs/ _output/advisory-logs/`). Example:

```
tags: notification-system, ux-patterns, modal-vs-page
```

Derive 2-5 tags from: (a) the question's topic, (b) affected components/areas, (c) review perspective tags evaluated (e.g., `security`, `architecture`, `ux`). Freeform -- no controlled vocabulary; existing logs are not retroactively modified.

---

Truncate sluggified short titles as needed. If not overwriting a file, proceed without asking for authorization. Reserve the id via `python .claude/skills/scripts/reserve_id.py --type <type> --title '<title>'` before writing content (stdout is the visible *id*; add `--json` to also get the *uid*). If a clarification question is asked (excluding authorization prompts), include both question and answer in the report.

NEVER replace existing plan text. Mark it revoked or superseded with a rationale, assign an identifier to the revoked fragment, and append the replacement text referencing that fragment.

## Artifact Immutability

Existing artifacts in `${OUTPUT_DIR}` are immutable design history. When format conventions change (new sections, enriched fields), apply them only to newly generated artifacts; do not retroactively modify existing ones. If rationale must be added after the fact, create a companion QA log or advisory that references the artifact.

## Report Filenames

All reports and plans under `${OUTPUT_DIR}` must use lowercase filenames.

Filename pattern: `<type>-<id>-<slug>.md`, where `<id>` is the visible ID returned by `reserve_id.py` (e.g., `plan-20261007-k3m9qz-<slug>.md`). The date followed by the ULID suffix keeps chronological order in the file tree without a counter; order within the same day is not guaranteed. Legacy artifacts keep `<type>-NNNNNN-<slug>.md` (e.g., `plan-000007-<slug>.md`).

## File Encoding

All files created by scripts, skills, or agents must be saved as **UTF-8 without BOM** (reports, plans, generated code, configs, any output).

- Never use platform-specific encodings (Windows-1252, ISO-8859-1, Shift-JIS).
- Accented characters (e.g., ã, é, ç, ü) must be properly encoded UTF-8 and used naturally (e.g., Portuguese text). Never emit mojibake or escaped sequences.
- When writing programmatically, specify `encoding='utf-8'` explicitly.

## Character Restrictions

All files created by scripts, skills, or agents must contain no ANSI escape sequences, no non-printable control characters (except `\n` and `\t`), and no typographic substitution characters.

- **ANSI codes**: prohibited. Escape codes (`\x1b[...`: color, cursor movement, bold/underline) are terminal-only and corrupt Markdown. Detect with regex `\x1b\[[\d;]*[A-Za-z]`.
- **Typographic characters**: prohibited. Em-dashes (`U+2014`), en-dashes (`U+2013`), curly/smart quotes (`U+2018`, `U+2019`, `U+201C`, `U+201D`) -- use ASCII equivalents: hyphen `-`, double-hyphen `--`, straight `'` and `"`.
- **Script output capture**: strip ANSI before writing (`re.sub(r'\x1b\[[\d;]*[A-Za-z]', '', text)` in Python).
- **Validation**: contamination must be cleaned before commit.
