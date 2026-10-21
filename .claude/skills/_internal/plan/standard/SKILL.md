---
name: plan-standard-internal
description: "Inlined worker for /plan standard single-plan mode. Not user-invocable."
compatibility: "Designed for Claude Code with the SEJA harness"
metadata:
  internal: true
  category: internal
  version: 1.0.0
---

> This is an inlined worker; execute these instructions as part of the caller's flow. The wrapper at .claude/skills/plan/SKILL.md has already run C1 (pre-skill) and the Design Guard; execute the steps below and invoke C6 (post-skill) at step 7. Note: when this internal is invoked inline from `_internal/plan/roadmap/SKILL.md` (Mode 1 step 9 or Mode 2 step 8), the caller instructs per-item execution to skip steps 7 and 8 -- the roadmap run owns the commit and the user prompt.

This mode is the reference prose -- other modes delta off of its shape. Step 2b plays the language game and writes the plan's intention sections (plan v3, D-006). Steps 1, 3 (reserve-ID + header), 5 (Review Depth), 7 (post-skill), and 8 (decision-point phrasing) reuse C1, C2+C3, C5, C6, and C4 respectively; the local prose below adds only the single-plan-specific content.

1. Apply C1 (pre-skill).

2. **Load references on demand** as needed:

   | When | Load |
   |---|---|
   | `--framing metacomm` | `product-design/product-design-as-intended.md` |
   | Plan touches backend/frontend/testing/i18n files | `product-design/standards.md` |
   | Plan involves auth, validation, or sensitive data | `product-design/security-checklists.md` |
   | Plan involves UX flows or visual design | `product-design/design-standards.md` |
   | Before step 2b | `general/plan-language-game.md`, `general/plan-intent-and-cases.md` |
   | Before Phase 1 review | `general/review-perspectives.md` |
   | Before writing the review log | `general/review-log-template.md` |

2b. **Language game (the interview).** Before the steps are written, play the language game of `general/plan-language-game.md` with the user. Reserve the ID and write the header first (C2, C3 with `plan_format_version: 3`), so each round is saved in the plan file as it grows (JDL-001).
   - **Task with code**: play rounds of up to 3 moves (scenes the user accepts, refuses or fixes; JDL-002 to JDL-006). After each round, write `## Intenção`, `## Requisitos`, `## Casos de uso` and `## Nas suas palavras` into the plan (shape: `general/plan-intent-and-cases.md`, PIC) and run `python3 .claude/skills/scripts/check_plan_intent.py <plan file> --phase game` (the game phase does not yet require the Retelling or the steps). Keep playing while it reports any `error`; the tool decides, not your impression. At the round ceiling, return the decision to the user with the three exits of JDL-007.
   - **Retelling and approval**: when the check has no `error`, write `## Retradução` (first person, controlled voice, with "O que eu não vou fazer"), show it, and ask via AskUserQuestion **Aprovar** / **Ajustar** / **Descartar** (JDL-010, phrased per C4). Ajustar goes back to the game with a fix move on the requirement pointed at; Descartar stops the plan. On Aprovar, add the line `Aprovação: aprovado em <YYYY-MM-DD>` under the Retelling and go on to step 3.
   - **Task without code** (DOCUMENT, CHORE or RESEARCH prefix, or steps touching only docs, config or the harness): play the short game (JDL-009, two moves), write `## Intenção`, a short `## Retradução` (one or two first-person sentences with "O que eu não vou fazer") and `## Nas suas palavras`, and write `nenhum (tarefa sem código)` under `## Requisitos` and `## Casos de uso`.
   - **Invoked inline from a roadmap**: always the short game, with `nenhum (jogo curto, item de roadmap)` under `## Requisitos` and `## Casos de uso`; the roadmap worker says so.

3. Complete the structured, self-contained plan with these sections (header per C3; `<depth>` set in step 5; the five intention sections of step 2b stay between *agent interpretation* and *steps*):
   - If default framing: *user brief*, *agent interpretation*, *files* -- per `general/report-conventions.md`.
   - If metacomm framing: *designer's metacommunication message* (the brief verbatim), *agent interpretation*, *files*.
   - *agent interpretation* covers three elements (four when `source:` is present):
     1. **Problem**: one sentence describing what problem this plan solves.
     2. **Approach**: the chosen approach and why it was selected.
     3. **Alternatives rejected** (Standard/Deep only; omit for Light): key alternatives considered and rejected.
     4. **Selection rationale** (Standard/Deep only; omit for Light; omit when no `source: <type>-<id>` header): bullet list of source recommendations with disposition. For each recommendation in the source artifact: `Included: R<n> -- <one-line reason>` or `Excluded: R<n> -- <one-line reason for deferral or rejection>`. When the source has no numbered recommendations, summarize the selection as a prose sentence.
   - If prefix is FIX (brief describes an error or bug), also include: *error log* (optional; if extensive, summarize and prepend "summarized error log:", and replace the inline log in the user brief with "<error log> (see summary below)"); *root cause*: diagnostics of the problem.
   - *best practices*: used in the plan.
   - *design decisions* (Standard/Deep only; omit for Light):
     - **User-visible impact**: what changes from the user's perspective (one paragraph).
     - **Trade-offs accepted**: what was gained, what was given up.
     - **Metacommunication impact** (when the plan modifies user-facing communication -- error messages, help, UI copy, CLI output, docs): what the system will now communicate differently. Use I/you phrasing per `shared-definitions.md`. Include regardless of `--framing metacomm`.
   - *steps*: structured step list -- step format and decomposition guidelines: see `.claude/references/template/plan-step.md`. Every step whose `Tests:` is not N/A carries a `Covers:` line with the plan requirements its tests demonstrate (PIC-008); every requirement is covered by at least one step.
   - *review log*: if applicable.
   - *outcomes*: expected outcomes.
   - *smoke*: `true` if any step creates or modifies API route files or frontend page/component files; `false` otherwise. Consumed by `/implement` to decide whether to run `/critique smoke api`.
   - *reflection* (optional, appended post-execution): a `## Reflection` section of dated bullets appended by `/implement` at wrap-up from the per-step notes (`step_notes.py reflect-bullet`). Absent by default; the section may be created on first use.

4. Save the plan. If not overwriting, proceed without asking for authorization.

4b. **Coverage check (advisory)**: if `product-design/product-design-as-intended.md` contains REQ markers (`<!-- REQ-*-NNN -->`), run `python .claude/skills/design/critique_plan_coverage.py --mode advisory` and include the coverage summary in the plan after the steps. Skip silently if no REQ markers exist.

5. **Review the plan** using a complexity-gated, two-phase process. Use `general/review-log-template.md` for the review log format.

   **Step metadata validation (before perspective review):**
   - Every step has all required fields (Files, References, Interface, Verify, Tests, checkbox). Optional fields (Depends on, Docs, Deploy, Traces) may be omitted entirely -- absent Depends on = no dependencies; absent Docs/Deploy/Traces = not applicable. `Interface:` is required but may be `N/A` -- omitting it entirely is a validation error; populate for dependency-producing steps.
   - `Covers:` (plan v3) appears on every step with non-N/A `Tests:` when the plan has requirements, only on those steps, cites only requirements of the plan's `## Requisitos`, and never goes inside `Traces:` (which cites the as-intended). Run `check_plan_intent.py <plan file>` again after the steps are written: no `error` is allowed.
   - Docs, Deploy, and Traces are present-when-relevant. When present, validate: Docs describes specific documentation to update; Deploy describes actionable deployment changes (specific env var names, ports, service names) covering Docker and standalone (Windows/Linux) where they differ; Traces lists valid REQ-xxx IDs.
   - For non-N/A `Tests:` entries: the description must express an observable behavior ('when X is called with Y, returns Z') rather than a structural assertion ('module exports class Z') or bare test name. Auto mode uses this to write a meaningful failing test before implementation.
   - `Tests: N/A` is appropriate for database migrations, configuration-only steps, pure refactors with pre-existing coverage, and framework/tooling-only steps that produce no business logic.
   - File paths for existing files verified on disk.
   - Dependencies flow forward (no circular, no backwards references).
   - No step touches >5 files (split if so).
   - Each step description is self-contained.

   Fix any issues before proceeding.

   **Complexity gate -- determine review depth:**
   - **Light**: <=6 action steps AND touches <=4 files. Phase 1 only.
   - **Standard**: 7-12 action steps OR touches 5-8 files. Phase 1; Phase 2 eligible.
   - **Deep**: >12 action steps OR touches >8 files OR involves migrations/auth/X-scope. Phase 1 + Phase 2 for all Deferred concerns.

   **Depth resolution:** apply Common Step C5 (Review Depth Override).

   **Phase 1 -- Perspective triage and scan (inline, no subagents):**
   Use the two-stage loading protocol (`general/review-perspectives.md` section "Two-Stage Loading"):
   1. Load `general/review-perspectives-index.md` to see all 16 perspectives.
   2. Identify the default shortlist of 3-6 perspectives using the Perspective Shortcuts by Plan Prefix table in `general/review-perspectives.md`.
   3. Optionally add up to 2 more with a one-line justification (e.g., "Added PERF: Step 3 introduces a bulk query not typical for CHORE-O scope").
   4. Load only the selected `review-perspectives/<tag>.md` files.
   Mark perspectives not in the shortlist as N/A in the review log. Scan and record Adopted/Deferred with a one-line concern. If Light, stop here.

   **Phase 2 -- Targeted deep-dives:**
   Trigger only for Deferred perspectives whose concern could cause regression, production incident, or standards violation. For Deep, also trigger for additive-improvement Deferred concerns. Never trigger for cosmetic or out-of-scope concerns.

   **Execution strategy by review depth:**
   - **Standard**: launch the `plan-reviewer` agent (Agent tool, subagent_type=`plan-reviewer`) with plan text, plan file path, depth=`standard`. Agent returns review log + amendments; append to the plan file.
   - **Deep**: launch `plan-reviewer` with depth=`deep`. Agent performs all deep-dives, conflict checks, and iterations autonomously; append output to the plan file.

   **Conflict check:** after each iteration producing Phase 2 recommendations, check for contradictions between perspectives. Resolve per `general/review-perspectives.md` section Resolving Perspective Conflicts. Log in the review log.

   **Iteration and convergence:** if Phase 2 changes the plan:
   1. Append a `### Plan Amendment (iteration N)` section with change + rationale (additive; do not modify existing text).
   2. Update the Steps section in place (only section allowed to change, since it is a living checklist).
   3. Re-evaluate perspectives whose steps were modified, plus any still Deferred.
   4. If all Phase 2 findings are "no change needed," terminate the loop immediately.
   5. Otherwise repeat until all Adopted or Deferred-with-rationale, or 3 iterations reached, or deep-dive budget (6) exhausted.

   **Execution metrics (mandatory):** append the Execution Metrics table (see `general/review-log-template.md`) at the end of the review log.

   Append review results to the plan file. Do not rewrite -- only add review log and amendment sections.

6. Output the plan id.

   **6a. Plan-phase reflection note and communication offer.** Before post-skill:

   - Write the plan-phase reflection-on-action note (past tense, what you observed): `python3 .claude/skills/scripts/step_notes.py append --plan <id> --phase plan --step 0 --title "<plan title>" --happened "..." --deviated "..." --less-sure "..." --gate not-applicable`. `deviated` says what changed from the brief to the plan; `less-sure` says what the review left open (use `none` when nothing). This creates the progress file, which post-skill commits with the plan.
   - Ask the user via AskUserQuestion whether they want the plan told to an audience (options phrased per C4):
     - **Communicate** -- run `/communicate <segment> --source <plan>`. Recommended when the plan changes what the user sees, or when the designer is at the citizen pole of H-003. NOT recommended when the plan is internal to the harness or a small fix.
     - **Proceed without communicating** -- continue to step 7. Recommended when the plan is internal or small. NOT recommended when the plan changes user-visible behavior.

     If accepted, run `/communicate` and record `python3 .claude/skills/scripts/step_notes.py record --plan <id> --kind communication --path <artifact path> --detail <segment>` (writes `- communication: <path> (<segment>)`). If declined, record `... --kind communication --declined` (writes `- communication: declined`). The offer never blocks.
   - Inline invocation from a roadmap (or any caller that skips the next-step prompt): write the note only, without the offer.

7. Run /post-skill <id> to commit the plan. The plan is now a durable git artifact regardless of the user's next choice.

8. Ask the user via AskUserQuestion what to do next (options phrased per C4):
   - **Implement now** -- run `/implement <id>`. Recommended when the plan has been reviewed and you are ready to proceed in this session. NOT recommended when you want to review the plan offline or implement in a separate session.
   - **End** -- the plan is committed; implement later via `/implement <id>`. Recommended when the current workflow is complete and you want to stop here. NOT recommended when the plan is trivially correct and implementing now would save context-switching cost.
