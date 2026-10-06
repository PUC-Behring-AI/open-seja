# Changelog

Public-facing changelog for the SEJA harness.

This file is hand-edited before each tag cut. Entries describe **consumer-visible** changes (skills, rules, agents, references, CLI behavior) and omit private dev-repo concerns. For tag convention and release process, see `tools/release-process.md` in the `dev` branch (not distributed).

Format: loosely based on [Keep a Changelog](https://keepachangelog.com/). SemVer: `vMAJOR.MINOR.PATCH`.

<!--
  Optional: place a line like `<!-- bump: minor -->` (values: patch, minor, major)
  at the top of the `## Unreleased` section to override `tools/publish.py`'s
  automatic bump-level inference. Without a hint, publish.py infers from
  subsection presence (Breaking -> major/minor-under-v0.x; Added -> minor;
  Fixed/Changed only -> patch).
-->

## [Unreleased]

## [v0.11.0] - 2026-10-06

### Added

- **Default cycle**: `/plan` now runs the whole ladder before any code: a short interview in your own words (grill), requirements and scenarios you approve (specify), a plan in format v2 with a `Scenarios:` list on every step that has tests, and then `/implement` builds test first: red for the right reason, then green, with the gate at each step. When the plan ends, `/implement` freezes the first measurement (M1) so `/reflect` and `/explain drift` can compare it with what was delivered, step by step on the ladder, and say what was not measured. The new feature folder is `features/<slug>/` (`intent.md`, `*.feature`, `gate.json`, `scenarios.lock.json`, `drift/`).
- **`/plan --grill` and `/plan --specify`**: run one phase alone. A task that needs no code (documentation, chore, research) skips specify with a recorded reason (`Specify: skipped -- <reason>`); the grill is never skipped but can be short.
- **`/implement --pipeline`** (opt-in): adds the Cleaner and Hardener roles after the green step. Without the flag the default build is unchanged.
- **`scenarios: draft`** in `intent.md`: when the interview is reopened and the requirements change, `check_specify.py --reconcile` sets the field to `draft` instead of leaving a stale `approved`. `check_features.py --matrix` reports the true state (`approved`, `stale`, `draft`, `missing`).
- **Four checks in `run_all_checks.py`**: `check_intent`, `check_features`, `check_specify` and `check_plan_scenarios`. They print "nada a verificar" and pass where the project has no `features/` and no v2 plan.
- **Guide**: `docs/how-to/ciclo-default.pt-BR.md` (pt-BR) explains the ladder, the commands, how to skip, what to do when something blocks, and how to update.
- **Test-first plugin** (`tests/scenario_report.py`, pytest): an upgrade updates it only if the project already installed it; it never creates it, and it never overwrites a copy edited by hand.

### Changed

- **Upgrading is safe for existing projects and needs no switch**: the new cycle acts only where the project has `features/` with an `intent.md` or a plan in format v2. **Plans in v1 stay valid** and are never rewritten; `--light` and the task type remain the way out. `/seja-setup --upgrade` does not touch `product-design/`, `conventions.md`, settings, `CLAUDE.md`, `_output/` or `features/`. Running the upgrade twice changes nothing the second time.
- `/seja-setup --upgrade` runs the `upgrade_harness.py` of the release it installs, not the one already in the project.

### Fixed

- **`upgrade_harness.py` now copies every file of `.claude/references/template/`** (`gate.py`, `*.example`, `*.toml`, `*.yaml`), not only `.md` and `.json`. Before, an upgraded project kept an old quality-gate template and could not install the test-first plugin, because its template never arrived.

## [v0.10.1] - 2026-10-04

### Fixed

- **First cycle with the quality gate, as rehearsed on v0.10.0**: `/seja-setup` now offers the gate when the backend is Python (the old trigger waited for a `pytest` answer that the setup questions never ask). Setup makes its initial commit first and writes the gate's commands to `product-design/conventions.md` afterwards, uncommitted; you commit them yourself after `uv run python gate.py --init-baseline`. Before, the commit hook refused setup's own commit and every later agent commit, and the `Stop` hook blocked setup turns before the project existed. The commands are now `uv run python gate.py --fast --json` and `--full --json`, so the hooks get a JSON report and find the venv's tools. With a backend folder (for example `backend/`), the gate measures that folder instead of an empty `src/` package. The template's `[tool.ruff] extend-exclude` adds `product-design`, `docs` and `_output`, so `ruff format --check .` no longer fails on Python snippets inside the design files. `docs/quickstart.md` "Your first cycle" follows the new order (baseline and gate commit before `/design`) and lists the full `uv add --dev` line.
- **`/implement` shows each step note as it is written**: in auto and manual mode the note and its gate result are shown after each step, not first met in `/reflect`. Manual mode runs the gate per step on that step's files; a gate run over the whole change is not attributed to any step.
- **Human (markers) verifier in `/post-skill`**: step 6c called a script that does not exist (`critique_human_markers_only.py`) and was silently skipped; it now calls `check_human_markers_only.py`.

## [v0.10.0] - 2026-10-04

### Breaking changes

- **`/document --type drr` renamed to `/document --type ddr`**: DDR (Design Decision Record) replaces DRR (Design Rationale Record). The acronym change aligns the name to what the record contains; scope is unchanged. Update saved prompts or scripts that pass `--type drr`.

### Added

- **Front door: README top, hypothesis page, first cycle**: the README now opens with one install command (`npx open-seja my-project`), the PLAN -> IMPLEMENT -> REFLECT cycle, the conditions of use (Python with pytest for the gate; `/design` before the first `/plan`) and a note that the cycle is a hypothesis; the upstream SEJA text moves under `## About SEJA`. New `docs/hypothesis.md` states H-008, the measures, and the conditions that would refute it. `docs/quickstart.md` gains `## Your first cycle`, a guided first cycle (gate, `/design`, baseline, `/plan`, `/implement`, `/reflect`) with a sample step note, and `npm/README.md` gains `## What happens next` pointing to it.

- **Agent-facing quality gate: per-step gate, `Stop` and `PreToolUse` hooks, `deny` rules**: `/implement` auto mode now requires the gate (`GATE_FAST_CMD` on the touched files) to pass before a step counts as SUCCESS, with 3 gate runs per step and PARTIAL on the third failure; the attempt count is recorded in the step note (`step_notes.py`, `parse --json` returns `gate_attempts`). Two hooks ship in `.claude/hooks/`: `quality_gate_stop.py` blocks ending a turn while the gate fails (released after 3 consecutive blocks), and `quality_gate_pretool.py` refuses `--no-verify`, `-n`, `core.hooksPath` and `--accept-baseline`, writes to `quality-baseline.json`, and commits that change `GATE_*` rows or fail `GATE_COMMIT_CMD`. `quality-gate/settings.fragment.json` carries the hook wiring and five complementary `permissions.deny` rules; `/seja-setup` merges it when the gate is accepted. The hooks are not a sandbox: limits, how to switch them off, how to lower `GATE_COMMIT_CMD` to `--fast`, and how to confirm the wiring with `/hooks` and `/permissions` are in the template README ("How the agent is held"). Existing installs upgraded with `/seja-setup upgrade` get the hook files but must merge the settings fragment by hand. The `deny` patterns have not been tested in a live session.

- **Quality gate for Python projects (template + critical plugin)**: `.claude/references/template/quality-gate/python/` holds `gate.py` (ruff, pyright, test lint, pytest with branch coverage, CRAP per function joined from radon and coverage, import-linter, marker ratchet; `--full` adds mutmut on touched functions), a README, and example `importlinter`/`pyproject` snippets. Stable JSON output and one exit code per category (0 pass; 2 lint/types; 3 tests; 4 CRAP; 5 architecture; 6 mutation; 7 evasion markers; 1 configuration or refusal). The new critical plugin `check_quality_gate.py` runs it from `/critique validate`, `preflight` and the end of `/implement`, and SKIPs where the gate is not installed. `/seja-setup` (install, here) offers the gate when the project uses pytest (anchor `Offer-QualityGate`), `--upgrade` refreshes it without overwriting customization, and `rules-tests.md` gains the anti-gaming rules. New `## Quality Gate` variables in conventions: `GATE_FAST_CMD`, `GATE_FULL_CMD`, `GATE_COMMIT_CMD`, `QUALITY_DIR`.
- **`/mob` skill -- timed mob programming session (PLAN -> BUILD -> REFLECT)**: runs a group session against a wall clock, chaining `/plan --plan`, `/implement --manual --skip-docs`, and `/reflect`. The slot, total duration, and per-phase times are always asked (flags such as `--duration`, `--slot`, `--split`, `--plan-min`/`--build-min`/`--reflect-min`, and `--rotation` only pre-select the answers). Two deterministic scripts back it: `mob_schedule.py` builds the clock agenda (phases, slack, driver rotations) and `mob_timer.py` runs the timebox timer, announcing phase and driver changes, writing a JSONL log, and answering `status` queries. Each session writes a `mob-session-<id>.md` record (planned vs actual times, linked plan and reflection IDs) to the new `${MOB_SESSIONS_DIR}` (`_output/mob-sessions`); `generate_macro_index.py` indexes these records as type "Mob Session", and `verify_commit_scope.py` accepts the new output folder. `skill-graph.md` gains `/mob` -> `/reflect --deep` and `/mob` -> `/implement` edges. The governance decision (3/4 test, rejected alternatives) is recorded in `harness-governance.md`; the skill count is now 17 (15 user-facing + 2 internal lifecycle hooks).

- **Reflection-on-action notes and evidence for `/reflect`**: `step_notes.py` writes a fixed-form note per step (`happened`, `deviated`, `less-sure`, `gate`) into the plan progress file, in both `/implement` modes, and a plan-phase note at the end of `/plan`. `/plan` offers `/communicate` for the plan and `/implement` offers `/explain drift` at wrap-up; both answers are recorded. `/reflect` on a plan shows the step notes, the quality-gate evidence, the communication and the drift report (agent words quoted and attributed), and says which were not measured.

### Changed

- **Install by `git clone` + `/seja-setup --here`**: the README, the quickstart and its first cycle now install with `git clone git@github.com:PUC-Behring-AI/open-seja my-project` followed by `/seja-setup --here`; the repository is shared with members of the PUC-Behring-AI organization. The `npx open-seja` package in `npm/` is not published yet and says so.
- **`/seja-setup --upgrade` and version resolution use the open-seja remote**: `resolve_seja_version.py` and the upgrade flow query and clone `git@github.com:PUC-Behring-AI/open-seja.git` instead of upstream SEJA; set `SEJA_REMOTE` (or pass `--remote`) to use another URL, e.g. HTTPS. A failed lookup no longer waits for a credential prompt and prints that hint.
- **Releases on `main` are distribution snapshots**: `main` carries only the harness and its public documentation (no `product-design/`, `_output/` or `tools/`), so a fresh clone is detected as a new project; development happens on `dev`, where the design record (`product-design/seja-as-intended.md`) lives. `docs/hypothesis.md` links to it there.

- **Attribution and trademark notice**: `README.md` and `npm/README.md` now carry an Attribution block (derivative of SEJA by Simone Diniz Junqueira Barbosa, CC BY-NC 4.0, provided as-is without warranties, changes made, non-commercial use). `TRADEMARKS.md` gains a *Permission for the open-seja name* section (scope, no endorsement, revocable). The npm package now ships `LICENSE` and declares `CC-BY-NC-4.0`.
- **`/implement` manual mode: partial-stop contract**: when execution stops with steps still unchecked (at the user's or the caller's request), `/implement` no longer marks the plan `# DONE`, does not close the `implement` pending entry, skips the roadmap status update, and appends `PARTIAL: N/M steps; stopped by <reason>` to its summary; the commit via `/post-skill` still runs. `/post-skill` step 2g.iv now closes the `implement` pending entry only when the plan header is marked `# DONE` (previously unconditional).
- **`/post-skill`: design-intent reminder and DONE marker proposal gated on a DONE plan**: steps 2c (design intent curation reminder) and 2e (DONE marker proposal) now run only when the plan header is marked DONE (`# DONE | ...` or legacy `# Plan NNNN | DONE | ...`), like 2g.iv; a partial plan skips them.
- **Known stale generated docs**: `docs/concepts/call-graph.*`, `.claude/references/general/call-graph.json`, and `docs/reference/harness-reference.md` were not regenerated for `/mob`; their generators live in `scripts/priv/`, which is absent from this repository. They stay stale until the next upstream sync.
- **DDR (Design Decision Record) replaces DRR (Design Rationale Record)** throughout the harness. The rename sharpens the naming — "Decision" is the noun; "Rationale" was an attribute of one section. DDR scope explicitly covers product, architecture, UX, and any other design discipline. Adds an optional `links:` field to the DDR format (supersedes / related / implements) for semantic cross-references between records.

- **`/plan` requires `product-design/product-design-as-intended.md`**: the Design Guard stops with "No design intent found. Run `/design` first" when it is missing, so the PLAN -> BUILD -> REFLECT cycle always has an as-intended to measure drift against.
- **Manual `/implement` now creates the progress file** and, like auto mode, writes a `## Reflection` bullet at wrap-up (`step_notes.py reflect-bullet`).

### Fixed

- **`/seja-setup --upgrade` no longer requires `product-design/` in the source**: only `.claude/skills/` is checked, matching what `upgrade_harness.py` reads.

- **Quality gate: pytest-timeout, CRAP message, hook release, setup excludes**: `gate.py` no longer passes `-p pytest_timeout` (pytest died with "Plugin already registered" when the plugin was autoloaded) and reports a configuration finding when the plugin is missing; the CRAP finding now shows `cc` and `cov` and says whether to simplify or add tests; the `Stop` hook repeats the last findings when it releases after 3 blocks; `step_notes.py parse --stats` prints the gate attempt count; `pyproject-dev.example.toml` and the install step exclude `gate.py` and `.claude` from ruff and pyright so a fresh install does not fail its first run.

## [v0.6.0] - 2026-06-29

### Breaking changes

- **`/check` renamed to `/critique`**: the skill is now invoked as `/critique <mode>`. All prior `/check` modes (`validate`, `review`, `smoke`, `preflight`, `health`, `test-plan`, `docs`, `freshness`, `telemetry`) are preserved as-is under `/critique`. Update any saved prompts or documentation that reference `/check`. (plan-000585)

### Added

- **`/reflect` product/practice lens**: `/reflect` now offers a product lens (user-facing impact, metacommunication alignment) and a practice lens (team workflow, AI collaboration patterns) alongside the existing technical lens. Available in both standard and `--deep` modes.
- **Call-graph HTML: self-contained offline viewer**: the interactive Cytoscape.js call-graph viewer now embeds the graph JSON inline in the HTML file, removing the HTTP fetch dependency. The viewer works fully offline and from `file://` URLs without a local server.
- **`docs/concepts.md`: REQ-TYPE-NNN requirement traceability types**: new section documents the 8 requirement traceability marker types (ENT, PERM, VAL, UX, MC, JM, I18N, DELTA), their blocking/advisory classification, and how plan steps reference them via the `Traces:` field.
- **`docs/how-to/upgrade.md`: Harness migrations section**: documents the idempotent migration scripts under `.claude/migrations/`, how `run_migrations.py` applies them during `upgrade_harness.py`, and where upgrade reports land (`_output/upgrade-reports/`).

### Fixed

- **`pending.py`: stale `implement` entries auto-dismissed on cleanup**: `pending.py cleanup` now checks whether a plan file carries a `# DONE` header in addition to checking for deletion. Implement entries whose plan completed but whose post-skill mark-done call failed silently are automatically dismissed within 24 hours (next pre-skill run). Dismissal reason: `plan already completed`.
- **Call-graph**: suggest-edge filter incorrectly split on the wrong token; `research`/`orchestrates` edge type false positive. Both corrected in `generate_call_graph.py`.
- **`generate_macro_index.py`**: `/explain` output artifact types (`behavior`, `behavior-evolution`, `code`, `data-model`, `architecture`) were missing from the index; now included.
- **`publish.py`**: Unreleased-section detection now matches both `## Unreleased` and `## [Unreleased]` heading forms (bracket notation). Fixes false "empty Unreleased section" preflight errors.

## [v0.3.0] - 2026-05-01

### Added

- **`/publish` skill and `tools/publish.py` automated release pipeline**: 8-step lifecycle (preflight, cut tag, clone public, copy prose, sync harness, smoke test, commit, push). Replaces the prior manual sync runbook for routine releases. (plan-000533)
- **Roadmap pending integration**: `/plan --roadmap` files an `implement` pending entry at finalization; `/implement --roadmap` closes it on completion; `pending.py cleanup` auto-dismisses orphaned roadmap entries; pre-skill heavy tier emits a compaction warning when session context grows. (plan-000531)
- **Unified D-NNN decision entries inline in `/research`**: step 9b proposes structured D-NNN entries; `document-generator` wires the `drr` doc-type to D-NNN entries. (plan-000539)
- **Post-skill telemetry and metadata**: new fields (`research_decisions`, `decision_points`, `qa_type`, `tokens_used`); context-filtering with top-N cap on next-step suggestions. (plan-000530, plan-000543)
- **`pending.py --format banner` / `--formatted` output modes**: pre-skill renders compact pending banners. (plan-000534, plan-000541)

### Changed

- **Framework → Harness terminology rename** across rules, references, scripts, agents, tutorial, and code identifiers. File renames include `.claude/rules/framework-structure.md` → `.claude/references/general/harness-governance.md`, `generate_framework_reference.py` → `generate_harness_reference.py`, `framework-health-evaluator.md` → `harness-health-evaluator.md`, `upgrade_framework.py` → `upgrade_harness.py`. (plan-000525, plan-000535, plan-000537)
- **DRR (Decision Record Recommendation) replaces ADR** across the harness, references, tools, and tutorial. (plan-000526)
- **Split model: `seja-public` no longer mirrors `.claude/`.** Consumers receive only public-authored prose; `.claude/` and root `CLAUDE.md` are generated by `sync_to_public.py` at publish time. Leak checker adapted for split model. (plan-000533, plan-000544)
- **Refactored `/plan` SKILL.md as a thin wrapper** dispatching to `_internal/plan/{standard,light,roadmap}/SKILL.md` worker skills via the Mode factoring pattern Dispatch B. Wrapper body reduced from 419 to 122 lines; per-mode workflow prose relocated verbatim. (plan-000475)
- **Pre-skill stages merged 8 → 6** (`orphan-check` and `compaction-check` became sub-steps of `budget-eval`); body compressed. (plan-000534)
- **Post-skill SKILL.md slimmed** by referencing a `SKILL-reference.md` companion that extracts static schemas; `harness-structure.md` slimmed to a lean inventory; new `harness-governance.md` carries extracted governance content. (plan-000541)

### Removed

- Retired `decision-entry.md` template (decision-entry instructions inlined into `/research` step 9b). (plan-000539)
- `seja-public/.claude/` mirror directory and the redundant duplication of harness scripts/skills/agents/tests in the public repo. (plan-000533)

<!-- Versions v0.3.0 through v2.13.0 were internal-only iterations not published individually; public releases resume at the next unified version. See .claude/CHANGELOG.md for the full internal history. -->

## [v0.2.0] - 2026-04-23

### Added

- Added `/critique freshness` mode and `check-git-freshness` periodic trigger for git upstream-freshness checks. The mode compares local branches to their upstreams for the codebase (and companion workspace, in two-repo deployments) and reports ahead/behind counts. No automatic pulls. The periodic trigger surfaces a pending-ledger entry every 7 days (configurable; blank to disable). See `.claude/rules/framework-structure.md` Architectural Decisions for why this signal lives outside pre-skill. (plan-000479, research-000477)

### Changed

- **Framework reference files compressed for conciseness** (plan-000471). Edited 24 files in `.claude/references/general/` to tighten agent-facing instructional prose, tables, and bullet structures while preserving every rule, classification, and invariant. Aggregate reduction: 363 lines (10.9%) across the `general/` reference surface; net 335 lines (10.1%) including the new `designer-copy-voice-rationale.md` sibling. Extracted maintainer-only rationale (plan-000426/000427 origin citations, the `## Pointer` block) from `designer-copy-voice.md` into the sibling per the SKILL-rationale pattern. Designer-facing `designer_description` frontmatter values were preserved byte-identical per plan A9 invariant. No behavioral changes; hot-path files (`shared-definitions.md`, `ci-integration.md`, `coding-standards.md`, `report-conventions.md`) remain semantically intact.

### Breaking changes

- **Framework simplification: skill renames and merges** (plan-000433, advisory-000431). Four breaking skill-name changes, applied in a single coordinated batch. No backward-compat aliases are provided; users who type the old verbs after upgrading will see "unknown skill."
  - **Renamed `/advise` to `/research`.** The skill's role as the iteration-2+ lifecycle entry point for investigation is clearer with the new verb. Output artifacts retain the `advisory-NNN` prefix for ID and link continuity.
  - **Renamed `/communication` to `/communicate`.** Consistency with verb-form skill naming. Output artifacts retain the `communication-NNN` prefix and live in `_output/communication/`.
  - **Renamed `/onboarding` to `/onboard`.** Consistency with verb-form skill naming. Output artifacts retain the `onboarding-NNN` prefix and live in `_output/onboarding-plans/`.
  - **Merged `/setup` and `/upgrade` into `/seja-setup`.** One unified framework-state command with state-driven dispatch (fresh / finalised / partial-init / public-clone / dev-repo) via `detect_setup_state.py`. Invocations that previously went to `/setup <target>` now go to `/seja-setup <target>`; invocations that previously went to `/upgrade` now go to `/seja-setup --upgrade` (or no-arg `/seja-setup` in a finalised project, which offers "Upgrade to latest" among other options).
- **Renamed `/seed` skill to `/setup`** (plan-000406, advisory-000405). No backward-compat alias is provided. Existing projects upgrade via `/upgrade`, which runs migration `0002_rename_seed_to_setup` and drops the old `.claude/skills/seed/` directory. Users who type `/seed` after upgrading will see "unknown skill" -- the new verb is `/setup`, a location-agnostic name that pairs with `/upgrade` as the install/refresh lifecycle. See advisory-000405 for the rationale. (Note: the `/setup` verb itself is superseded by `/seja-setup` in this same release -- see the framework-simplification entry above.)

### Changed

- Collapse `apply-promote-proposal` into `apply-promote-markers`: `/explain spec-drift --promote` Phase 3a now files a single pending entry; Phase 3b closure matrix reduced from 4 branches to 2. See plan-000470, research-000469.
- Merge `spec-drift-check` + `periodic-curation` dispatch in `/pending` into a single drift-review handler. Cron cadences (14d + 30d) unchanged.
- **`/research` output files**: new invocations emit `research-<id>-*.md` under `_output/research-logs/` with header `# Research <id> | ...`. Historical `advisory-<id>-*.md` files under `_output/advisory-logs/` are preserved in place; read-path scripts (`summarize_artifacts.py`, `generate_macro_index.py`, `generate_decision_digest.py`, `backfill_decision_digest.py`, `check_docs.py`, `check_telemetry.py`) scan both folders and both filename prefixes. Per advisory-000448 (follow-on to 000431 P4); supersedes the "advisory-NNN prefix retained" note in the Breaking changes section above.
- **Canonical writing surface renamed `advis*` to `research`** (research-000467, plan-000468, follow-up to advisory-000448). Eleven-step rename across skill bodies, reference prose, and script help: `/research` skill body renamed "Advisory Workflow" -> "Research Workflow" and associated prose; `/explain spec-drift` row corrected to write to `${RESEARCH_DIR}` with `Research` header (closes a plan-000449 miss). Agent renamed: `advisory-reviewer` -> `research-reviewer` (single call site updated). Telemetry adopts a dual-key transition: writers emit both `advisory_decisions` + `research_decisions` and both `"advisory-follow-up"` + `"research-follow-up"` `qa_type` values with identical payload; readers prefer research-prefixed keys with fallback. Dual-key retirement is scheduled with advisory-000448 Rec 5's 6-month legacy-folder revisit (pending-ledger entry pa-000115 files the reminder). A semiotic rule is documented in `general/shared-definitions.md § Advisory terminology rule`: Sense A (artifact-type) -> research; Sense B (non-blocking adjective, e.g., "Coverage check (advisory)") -> unchanged. Legacy reads preserved under advisory-000448 forward-only rule: `${ADVISORY_DIR}`, `reserve_id.py --type advisory`, `advisory-NNN` cross-references in historical artifacts, sense-B adjective usages.

### Added

- Add `/explain spec-drift --scope since-plan plan-NNNNNN` to narrow drift scans to registry rows touched by one plan.
- **New `docs/how-to/which-communicative-skill.md` decision page** (plan-000433 step 8). A one-page decision table keyed by (audience, artifact kind) routes readers to `/document`, `/onboard`, `/communicate`, or `/explain`. Addresses the council-note in advisory-000431 that the four communicative skills lacked a single "which one do I use?" reference. Diataxis: how-to.
- **Quick Guide breadcrumbs across user-facing skills** (plan-000433 steps 9-12). Each user-facing SKILL.md Quick Guide now carries a terse `Not for:` line naming the sibling skill(s) that cover adjacent intents, and a `Next step:` line drawn from `.claude/references/general/skill-graph.md`'s "After" rows. Improves navigability between related skills at decision time without inflating the Quick Guide.
- **`/setup --version <tag>` and `/upgrade --version <tag>`.** Both skills now pin to a public `seja` SemVer release tag (default: latest tag on `simonedjb/seja`; fallback to `HEAD` with a warning when no tags exist). Resolution uses the new `.claude/skills/scripts/resolve_seja_version.py` helper. Bootstrapped projects record the pinned tag in a `.seja-version` file; subsequent `/upgrade` runs read it as the "from" half of the version banner (`Upgrading public pin from <old> to <new>`) and write the resolved tag on success. Legacy projects without `.seja-version` are treated as `unknown → <target-tag>`. (roadmap-000372 Wave 2 / plans-000379 and 000380)
- `upgrade_framework.py --new-version <tag>` CLI flag: writes the provided tag to the target's `.seja-version` file after a successful upgrade.
- **`.claude/skills/scripts/backfill_open_plans.py`**: one-shot tool to file `implement` pending entries for existing plan files missing the `-done-` rename. Supports `--dry-run`, `--bulk-dismiss-older-than <days>` (default 30), and `--reset`. Respects prior user dismissals (a previously-dismissed entry is not resurrected). Intended as a one-shot migration; routine `/plan` → `/implement` flow is filed live via post-skill. (plan-000408)

### Changed

- **Canonical lifecycle path revised** (plan-000433, advisory-000431). The lifecycle narrative in `CLAUDE.md § Key workflows`, `docs/quickstart.md`, and `docs/concepts.md § Lifecycle` now presents a single canonical path -- `/research` (or `/explain`) > `/design` | `/plan` > `/implement` > `/critique` > `/document` | `/communicate` > `/reflect` -- with the single gating invariant "validate before you communicate" (`/critique` always comes before `/document` and `/communicate`). Replaces the prior two-path framing (first iteration vs iteration 2+) with one unified sequence; iteration-1 bootstrapping via `/seja-setup` -> `/design` is noted as the lead-in, not a separate path. `/reflect` is now explicit as the cycle-closing step in the documented flow.
- **Pre-skill pending-check stage surfaces publish entries separately.** Pending-ledger entries whose description starts with `PUBLISH:` (filed by `tools/cut_tag.py` at release time) are now rendered as a dedicated banner before the generic pending notice. Entries older than 3 days escalate to a stronger "OVERDUE publish" warning. Implements the drift-prevention mechanism that closes A2's manual-sync gap (advisory-000366, roadmap-000372 Wave 1 / plan-000376).
- `pending.py status --json` payload gains `publish` (list of publish entries), `publish_overdue_count`, and `publish_overdue_threshold_days` fields. Existing fields (`count`, `overdue_count`, `top_3`, `warnings`) are unchanged; the new fields are additive and safe for existing consumers to ignore.
- **`implement` pending action type and overdue banner.** Post-skill now files an `implement` pending entry when `/plan` completes (via `pending.py add --if-absent` for atomic uniqueness); the entry is closed by `/implement`'s rename-to-`-done-` step and by a post-skill safety net, both using `pending.py done --source <plan-id> --type implement` (idempotent). Pre-skill's pending-check stage surfaces open entries via a new banner, with a stronger overdue warning past the `Pending plan age escalation` threshold (default 30 days; configurable in `conventions.md § Periodic Triggers`). A plan generated via `/plan` but never run via `/implement` no longer accumulates silently. `pending.py status --json` gains `implement`, `implement_overdue`, `implement_overdue_count`, and `implement_overdue_threshold_days` fields. (advisory-000407, plan-000408)
- **`pending.py cleanup` auto-dismisses orphaned `implement` entries.** The 24h-throttled cleanup pass now also checks whether each open `implement` entry's plan file still exists in `_output/plans/`. If absent (with leftover `-progress.md` / `-qa-*.md` siblings explicitly ignored), the entry is dismissed with reason `plan file deleted`. (plan-000408)
- **`pending.py done` accepts `--source <id> --type <type>` as an alternative to a positional id.** Closes ALL matching open entries (pending or snoozed) to actively restore the (source, type) uniqueness invariant. No-op when no open entry matches, when the entry is already done, or when only done/dismissed entries match — idempotent for callers. (plan-000408)
- **`pending.py add` accepts `--if-absent`.** With `--if-absent` + `--source` + `--type`, the script skips the add when an open entry already exists for that pair. Used by post-skill for eager filing to guarantee single-entry uniqueness under checkpoint recovery. (plan-000408)
- **Skills: Quick Guide moved to `SKILL-quickguide.md` sibling file.** Each user-facing `SKILL.md` body previously embedded a `## Quick Guide` H2 with designer-facing narrative; plan-000466 extracts that block to a sibling `SKILL-quickguide.md` and leaves a one-line blockquote pointer in `SKILL.md` (blockquote within the first 15 non-blank body lines, containing the literal `SKILL-quickguide.md`; canonical form `> Overview: see [./SKILL-quickguide.md](./SKILL-quickguide.md)`). `/help <skill>` output is unchanged. Reduces per-invocation context load by ~500-800 tokens and resolves pin-debt between designer-facing narrative and the agent-executional body. A new `check_docs.py` scanner `quickguide-pointer-compliance` (severity: error) enforces pointer presence when a sibling exists. Sibling prose edits are maintainer-only (no runtime pinning); example snippets in the sibling that mention CLI arguments must stay in sync with `## Arguments` in SKILL.md when argument signatures change. Pattern documented alongside `SKILL-rationale.md` in `.claude/rules/framework-structure.md § Skill Authoring Patterns`. `/seja-setup --upgrade` now collects `SKILL-*.md` siblings alongside SKILL.md so upgraded consumers receive both the pointer and the narrative. See research-000465 and plan-000466.
- **Refactor: `.claude/rules/*.md` and `.claude/references/template/rules-*.md` are now path-scoped pointer files.** Each file references `.claude/references/general/review-perspectives/<tag>.md` (review questions) and `project/standards.md § <domain>` (full conventions) rather than restating P0 rules inline. Removes the P0-rule drift surface between `.claude/rules/*.md` and `review-perspectives/*.md`. If consumer feedback shows the pointer format delays recall of critical P0 rules during editing, revert per advisory-000417's documented counter-position (reinstate inline rules with an explicit "subset of review-perspectives/<tag>.md P0 questions" maintenance note). (advisory-000417, plan-000421)
- **Upgrade note:** `.claude/rules/*.md` remain in the "manual-merge" upgrade category (`/upgrade` SKILL.md § Merge strategy). Existing consumer projects that customized these files will see the new pointer format as a proposed diff; review and merge deliberately. Consumers can adopt the pointer format verbatim or keep their existing inline rules.

### Migration — plan-000447 (Option A scaffolding split)

Pre-plan-447 projects upgrading via `/seja-setup --upgrade` retain their existing `project-design/conventions.md` unchanged (per File Classification "Never overwrite"). Users observing `{{VAR}}` placeholders in `conventions.md` after upgrade should run `/design update stack` (which orchestrates the `Scaffold-CLAUDE.md` / `Scaffold-Rules` / `Scaffold-SmokeTestInfra` anchors) to fill placeholders and regenerate CLAUDE.md, `.claude/rules/`, and smoke-test infra for the current stack.

<!-- Next-version placeholder. Example format:

## v0.1.0 — 2026-MM-DD

### Added
- ...

### Changed
- ...

### Fixed
- ...

-->
