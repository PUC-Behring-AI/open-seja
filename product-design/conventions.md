# PROJECT CONVENTIONS

> Centralized project-specific definitions. All skills and reference files reference variables from this file instead of hardcoding project-specific values. To adapt the skill system to a different project, edit only this file.

---

## Project Identity

| Variable | Value | Description |
|----------|-------|-------------|
| `PROJECT_NAME` | open-seja | Project display name |
| `PROJECT_DESCRIPTION` | Personal experimentation/extension fork of the SEJA agent harness, kept close to the upstream `simonedjb/seja` so it can adopt new capabilities (e.g. OpenCode compatibility) without diverging much. This repo dogfoods SEJA on itself: the harness manages its own evolution through its own research/plan/implement cycle. | One-line project description |
| `PROJECT_MODE` | brownfield | Project mode: greenfield (new project) or brownfield (existing codebase) |

---

## Directory Structure

| Variable | Value | Description |
|----------|-------|-------------|
| `SKILLS_DIR` | `.claude/skills` | Root directory for skill definitions |
| `AGENT_SPECS_DIR` | `product-design/agent` | Agent-facing structured specifications in YAML |
| `OUTPUT_DIR` | `_output` | Root directory for all generated artifacts |
| `PLANS_DIR` | `${OUTPUT_DIR}/plans` | Plan output folder |
| `SCRIPTS_DIR` | `${OUTPUT_DIR}/generated-scripts` | Script output folder |
| `ADVISORY_DIR` | `${OUTPUT_DIR}/advisory-logs` | Legacy advisory log output folder |
| `RESEARCH_DIR` | `${OUTPUT_DIR}/research-logs` | Research log output folder |
| `PROPOSALS_DIR` | `${OUTPUT_DIR}/proposals` | Lightweight change proposals |
| `INVENTORIES_DIR` | `${OUTPUT_DIR}/inventories` | Inventory output folder |
| `USER_TESTS_DIR` | `${OUTPUT_DIR}/user-tests` | User test plan output folder |
| `EXPLAINED_BEHAVIORS_DIR` | `${OUTPUT_DIR}/explained-behaviors` | Behavior explanation output folder |
| `EXPLAINED_CODE_DIR` | `${OUTPUT_DIR}/explained-code` | Code explanation output folder |
| `EXPLAINED_DATA_MODEL_DIR` | `${OUTPUT_DIR}/explained-data-model` | Data model explanation output folder |
| `EXPLAINED_ARCHITECTURE_DIR` | `${OUTPUT_DIR}/explained-architecture` | Architecture explanation output folder |
| `BEHAVIOR_EVOLUTION_DIR` | `${OUTPUT_DIR}/behavior-evolution` | Behavior evolution explanation output folder |
| `REFLECTIONS_DIR` | `${OUTPUT_DIR}/reflections` | Reflection report output folder |
| `MOB_SESSIONS_DIR` | `${OUTPUT_DIR}/mob-sessions` | Mob programming session records |
| `ONBOARDING_PLANS_DIR` | `${OUTPUT_DIR}/onboarding-plans` | Onboarding plan output folder |
| `COMMUNICATION_DIR` | `${OUTPUT_DIR}/communication` | Communication material output folder |
| `ROADMAP_DIR` | `${OUTPUT_DIR}/roadmaps` | Roadmap output folder |
| `QA_LOGS_DIR` | `${OUTPUT_DIR}/qa-logs` | QA session log output folder |
| `CRITIQUE_LOGS_DIR` | `${OUTPUT_DIR}/critique-logs` | Critique/preflight/review output folder |
| `TMP_DIR` | `${OUTPUT_DIR}/tmp` | Temporary/helper scripts |
| `CODEBASE_DIR` | `.` | Root directory of the project codebase (embedded) |

---

## Key Files

| Variable | Value | Description | Maintained by |
|----------|-------|-------------|-------------- |
| `BRIEFS_FILE` | `${OUTPUT_DIR}/briefs.md` | Execution log of all skill invocations | Agent |
| `BRIEFS_INDEX_FILE` | `${OUTPUT_DIR}/briefs-index.md` | Lightweight briefs index (one-line summaries) | Agent |
| `ARTIFACT_INDEX_FILE` | `${OUTPUT_DIR}/INDEX.md` | Single global artifact index (no per-folder INDEX.md files) | Agent |
| `CONSTITUTION_FILE` | `product-design/constitution.md` | Project constitution -- immutable principles | Human |
| `AS_CODED` | `product-design/product-design-as-coded.md` | Unified implementation state: Conceptual Design, Metacommunication, Journey Maps | Agent |
| `CD_AS_IS_CHANGELOG` | `product-design/product-design-changelog.md` | As-built conceptual design changelog | Agent |
| `DESIGN_INTENT` | `product-design/product-design-as-intended.md` | Unified working intent (§0-§17) + DDR Decision log (## Decisions) + CHANGELOG | Human (markers) |
| `DESIGN_INTENT_TO_BE` | `product-design/product-design-as-intended.md` | Legacy alias for `DESIGN_INTENT` | Human (markers) |
| `UX_RESEARCH` | `product-design/ux-research-results.md` | UX research: personas, problem scenarios, journeys, processing status, CHANGELOG | Human (markers) |
| `STANDARDS` | `product-design/standards.md` | Unified engineering standards: Backend, Frontend, Testing, i18n | Human / Agent |
| `DESIGN_STANDARDS` | `product-design/design-standards.md` | Unified design standards: UX patterns and graphic/visual design | Human / Agent |
| `SESSION_NOTES_FILE` | `${TMP_DIR}/session-notes.md` | Session-scoped working memory for structured note-taking | Agent |
| `DECISION_DIGEST_FILE` | `${OUTPUT_DIR}/decision-digest.jsonl` | Machine-readable decision index (one JSON line per design decision) | Agent |
| `CONVERSATION_TRACE_FILE` | `${OUTPUT_DIR}/conversation-trace.jsonl` | Append-only conversation trace log | Agent |
| `SPO_DATA_FILE` | `product-design/product-overview.yaml` | Structured Product Overview data | Human |
| `SPO_OUTPUT_FILE` | `${OUTPUT_DIR}/docs/spo.html` | Generated interactive SPO HTML | Agent |

---

## As-Intended / As-Coded Registry

| As-Intended file | Section | As-Coded counterpart |
| ---------------- | ------- | -------------------- |
| `${DESIGN_INTENT}` | §0-§17 design intent + Decisions + CHANGELOG | `${AS_CODED}` |
| `${DESIGN_INTENT}` | §15 designed journeys | `${AS_CODED} § Journey Maps` |
| `${UX_RESEARCH}` | all (personas, scenarios, journeys, CHANGELOG) | `-` |
| `${SPO_DATA_FILE}` | layers, personas, quality criteria, cards | `${SPO_OUTPUT_FILE}` |

---

## Review Configuration

| Variable | Value | Description |
|----------|-------|-------------|
| `MINIMUM_REVIEW_DEPTH` | `light` | Minimum review depth floor. Valid values: `light`, `standard`, `deep`. |

---

## Periodic Triggers

| Trigger | Interval (days) | Action type | Description |
|---------|-----------------|-------------|-------------|
| Periodic curation | 30 | `periodic-curation` | Review `product-design-as-intended.md` for items ready to promote from `implemented` to `established` |
| Spec-drift check | 14 | `spec-drift-check` | Run `/explain drift` to surface drift between design intent and as-coded state |
| Git freshness check | 7 | `check-git-freshness` | Compare each project git repo to its upstream; surface behind/ahead counts. Resolve via `/critique freshness`. |

| Threshold | Value | Description |
|-----------|-------|-------------|
| Pending plan age escalation | 30 | Days before an open `implement` pending entry is surfaced with the overdue banner in pre-skill. |
| Verify-as-coded file threshold | 5 | Minimum number of files changed by a plan before post-skill auto-creates a `verify-as-coded` pending action |
| Pending age escalation | 14 | Days before a pending action is flagged "overdue" in pre-skill notices |
| Pending auto-dismiss | 90 | Days after which unaddressed pending actions are auto-dismissed by `pending.py cleanup` |

---

## Source Directories

> No backend or frontend framework -- this project is the SEJA agent harness itself (skills + reference files + Python utility scripts), not an application.

| Variable | Value | Description |
|----------|-------|-------------|
| `BACKEND_FRAMEWORK` | none | Backend framework identifier (`none` -- harness/tooling project) |
| `FRONTEND_FRAMEWORK` | none | Frontend framework identifier (`none` -- no web UI) |

---

## Stack Description

| Variable | Value | Description |
|----------|-------|-------------|
| `TESTING_STACK` | pytest (harness scripts under `.claude/skills/scripts/tests/`) | Testing technology summary |
| `DEPLOYMENT_STACK` | git-distributed (cloned by consumers via `/seja-setup <target>` or `git clone` + `/seja-setup --here`) | Deployment technology summary |

---

## Architecture Description

| Variable | Value | Description |
|----------|-------|-------------|
| `ARCHITECTURE_DESCRIPTION` | Agent skill harness: `SKILL.md` definitions (thin wrappers delegating to internal `_internal/*/SKILL.md` workers), Python utility scripts, Markdown reference files, and subagent prompts, orchestrated via Claude Code's Skill/Agent tools | High-level architecture description |
| `ARCHITECTURE_PATTERN` | Thin skill wrapper -> state-driven internal dispatch -> Python scripts as the sole mutation path for structured/marker-governed files | Architecture pattern |
| `CONVENTION_1` | This repo dogfoods SEJA on itself -- every change to the harness follows the same research/plan/implement cycle it gives consumer projects | Key project convention #1 for CLAUDE.md |
| `CONVENTION_2` | Stay close to upstream `simonedjb/seja`: keep `main` a fast-forward-able mirror, do personal experiments on separate branches (see research-000026 in the Doutourado archive) | Key project convention #2 for CLAUDE.md |
| `CONVENTION_3` | License stays Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC), same as upstream -- never relicense without explicit confirmation | Key project convention #3 for CLAUDE.md |

---

## Secret Scanning

| Variable | Value | Description |
|----------|-------|-------------|
| `SECRETS_EXTRA_SKIP_PATTERNS` |  | Additional filename substrings to skip during secret scanning (comma-separated) |
| `SECRETS_EXTRA_SKIP_DIRS` |  | Additional directory names to skip during secret scanning (comma-separated) |
| `SECRETS_EXTRA_SKIP_EXTENSIONS` |  | Additional file extensions to skip during secret scanning (comma-separated, with dots) |
| `SECRETS_EXTRA_FALSE_POSITIVES` |  | Additional false-positive regex patterns (comma-separated, case-insensitive) |
| `SECRETS_EXTRA_PATTERNS` |  | Additional secret-detection regex patterns (comma-separated, case-insensitive, auto-named) |

---

## Build & Test Commands

| Variable | Value | Description |
|----------|-------|-------------|
| `ALL_TESTS_CMD` | pytest .claude/skills/scripts/tests/ | Command to run all tests (harness script test suite) |

---

## Workspace Deployment

This project uses the **embedded** deployment pattern: `.claude/`, `product-design/`, and `_output/` live in the project root. `CODEBASE_DIR` is `.`. No companion-workspace separation is in use. Unlike a typical consumer project, this repo *is* the foundational SEJA harness source -- it is not itself installed via `/seja-setup <target>` from elsewhere; it was finalised in place via `/seja-setup --here` after being seeded from `simonedjb/seja`.
