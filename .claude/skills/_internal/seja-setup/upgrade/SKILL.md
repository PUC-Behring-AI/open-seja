---
name: seja-setup-upgrade-internal
description: "Inlined worker for /seja-setup Upgrade Flow. Not user-invocable."
compatibility: "Designed for Claude Code with the SEJA harness"
metadata:
  internal: true
  category: internal
  version: 1.0.0
---

> This is an inlined worker; execute these instructions as part of the caller's flow. The wrapper at `.claude/skills/seja-setup/SKILL.md` has already run the Entry-Point Routing dispatch; execute the steps below as part of the `/seja-setup` skill's flow.

## Upgrade Flow

> **Precondition**: target is in `finalised` (or user-confirmed `partial-init`) state with `.claude/`, `product-design/conventions.md`, and `.seja-version` (or legacy no-pin fallback). Entry-point routing has already redirected or refused `dev-repo-refuse`, `no-harness`, and `fresh-download`.

Runs from the **target project** (not the source repo). Applies safe updates to project-independent files and preserves project-specific customizations.

> **Scaffolding-migration note**: Upgrade never re-runs the Section 1 scaffolding questionnaire. Per the File Classification table below, `product-design/**` is classified "Never overwrite" -- your existing `conventions.md` is preserved unchanged. Projects finalised before the scaffolding move (those whose `conventions.md` still carries `{{VAR}}` placeholders) will retain those placeholders through the upgrade; run `/design update stack` afterwards to fill them and regenerate downstream artifacts (CLAUDE.md, rules, smoke-test infra) via the named scaffolding anchors. Greenfield and brownfield legacy projects both route through the same migration path.

### File Classification

| Category | Files | Overwrite? | Action |
|----------|-------|------------|--------|
| Skills | `.claude/skills/*/SKILL.md` | Yes | Auto-update |
| General references | `.claude/references/general/*.md` | Yes | Auto-update |
| Templates | `.claude/references/template/**` | Yes | Auto-update |
| Harness metadata | `.claude/CHANGELOG.md`, `VERSION`, `CHEATSHEET.md` | Yes | Auto-update |
| Scripts | `.claude/skills/scripts/*.py` | Yes -- auto-overwritten by `upgrade_harness.py` | Auto-update |
| Agents | `.claude/agents/*.md` | Mostly -- may have local tweaks | Show diff, ask per file |
| Rules | `.claude/rules/*.md` | Yes -- auto-overwritten by `upgrade_harness.py`; review with `git diff` afterwards | Auto-update (the rule files are harness inventory, not project convention) |
| Project definitions | `product-design/**` | Never | Skip |
| Settings | `.claude/settings.json`, `settings.local.json` | Never | Skip |
| Output directory | `_output/` (or configured) | Never | Skip |
| CLAUDE.md | `CLAUDE.md` | Never | Skip |
| PKB layer | `inbox/`, `logs/`, `Templates/`, `Objetivos.md`, `index.md`, `.claude/skills/{daily-log,weekly-review,compress,next-action,process-inbox}/` | Never (not in source) | Skip; `init` adds missing files only |

### Steps

1. **Resolve target version**: `python .claude/skills/seja-setup/resolve_seja_version.py [--version <tag>]` (default: latest SemVer tag on the open-seja remote -- `$SEJA_REMOTE` if set, else `git@github.com:PUC-Behring-AI/open-seja.git`). Capture the resolved tag for steps 3 and 5; surface the `HEAD` fallback warning if emitted. If resolved tag matches current `.seja-version`, print "Harness already up to date at `<tag>`" and exit.

2. **Locate SEJA source repo**: if a path is provided, trust the user has it at the desired tag. Otherwise `git clone --depth 1 --branch <resolved-tag> "${SEJA_REMOTE:-git@github.com:PUC-Behring-AI/open-seja.git}" <temp-dir>` (drop `--branch` if resolved ref is `HEAD`). On clone failure, ask for a local path.

3. **Validate source repo**: confirm it contains `.claude/skills/` with skill definitions. (Releases are tags on open-seja's distribution branch `main`, which carries no `product-design/`; `upgrade_harness.py` only needs `.claude/`.)

4. **Read project conventions**: read `product-design/conventions.md` for output-directory name and other project-specific paths.

4b. **Quality gate check (before step 5)**: if the project has `gate.py` at its root, compare it with the project's own template copy (`.claude/references/template/quality-gate/python/gate.py`) BEFORE the auto-update of `.claude/references/template/**` overwrites it. Identical -> after the upgrade, replace the project's `gate.py` with the new template. Different (local changes) -> show the diff and ask whether to replace, keep, or merge. Never touch `.baseline` files in `QUALITY_DIR`.

5. **Run upgrade script**: `python <source-path>/.claude/skills/scripts/upgrade_harness.py --from <source-path> --target . --new-version <resolved-tag>` -- the script of the release being installed, not the copy already in the project (the new release may copy files the old script skips). Add `--dry-run` for preview. Omit `--new-version` only on the pre-release HEAD fallback path. The script reads existing `.seja-version` for the banner's "from" half and writes the resolved tag on success.

5b. **Test-first plugin (only if already installed)**: if the project has `tests/scenario_report.py`, run `python .claude/skills/scripts/build_checks.py install-plugin .` after step 5. It is idempotent and refuses a copy edited by hand (show that message). If the file is absent, do nothing: an upgrade never creates the plugin; `/implement` installs it on the first red step.

6. **Review summary**: highlight public-release pin change (e.g., `v0.1.0 -> v0.2.0`), internal harness version change, old-layout migration if any, new convention variables, files auto-updated vs needing manual merge.
   - Artifact IDs (D-010): if `_output/ids/` does not exist, there is nothing to migrate; legacy 6-digit IDs stay as they are and remain valid.

7. **Show diffs for manual-merge files**: unified diff for each script/rule/agent that differs. For agents: ask "Accept source / Keep current / Show diff?" per file. For scripts and rules: show diff and advise on merge.

8. **Offer follow-up actions**:
   - New convention variables -> "Add to your `product-design/conventions.md`?"
   - `SPECIFY_DEFAULT` missing (listed by `diff_conventions` in the step 5 report as missing from `product-design/conventions.md`; D-011, CYC-036) -> ask one `AskUserQuestion` (rationale per C4), same text as install step 4d (`Ask-SpecifyDefault`):

     > A especificação em Gherkin é o padrão neste projeto? Gherkin é um texto curto que diz, com exemplos, o que o sistema deve fazer, antes do código. Um exemplo de quando não vale: num protótipo, o que o sistema deve fazer ainda muda toda semana.

     - **`on`** -- Recommended when o projeto vai medir a escada ou já tem requisitos estáveis. NOT recommended when o projeto está em prototipação.
     - **`off`** -- Recommended when o projeto está em prototipação. NOT recommended when o projeto vai medir a escada.

     On an explicit answer, add the `SPECIFY_DEFAULT` row from the template's Review Configuration table to the same table of `product-design/conventions.md`, with the answer in backticks (`` `on` `` or `` `off` ``). Never write `SPECIFY_DEFAULT` without an explicit answer: in non-interactive mode, with `--dry-run`, or when the user does not answer, do not write the row and tell the user, in pt-BR: "Não gravei `SPECIFY_DEFAULT`. Vale `on` até você responder." This is the only upgrade write to `product-design/`; `upgrade_harness.py` still never touches `conventions.md`.
   - `has_pkb_layer` (from `detect_setup_state.py --json`, or the "camada PKB detectada" line of the step 5 output) -> "Run `python .claude/skills/scripts/pkb_inbox.py init` to add the new PKB templates without overwriting anything?"
   - Old path references -> "Update the references?"
   - Stale CLAUDE.md -> "Regenerate your CLAUDE.md?"
   - `${QA_LOGS_DIR}` (default `_output/qa-logs/`) contains files matching `^<prefix>-\d{6}-qa-.*\.md$` (legacy centralized layout) -> "Post-skill now collocates QA logs with the parent artifact, not `${QA_LOGS_DIR}`. Migrate N detected files via `python .claude/skills/seja-setup/migrate_qa_logs_to_parent_dirs.py --apply`? (safe, uses `git mv` to preserve history, `--dry-run`-previewable.)"

9. **Clean up**: remove the temp clone directory if one was created.

10. **Post-upgrade summary**:
    > Upgrade complete.
    >
    > - Pinned to `<resolved-tag>` (recorded in `.seja-version`)
    > - N files auto-updated
    > - N files need manual merge (diffs shown above)
    > - N new files added
    > - Reference files regenerated (harness-reference.md, skills.md, perspectives.md)
    >
    > Run `git diff` to review all changes before committing.
