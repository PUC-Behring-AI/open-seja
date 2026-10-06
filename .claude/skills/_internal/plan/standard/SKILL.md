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

> Extended cycle (grill, specify, test-first): see .claude/references/general/extended-cycle-contract.md.

This mode is the reference prose -- other modes delta off of its shape. Steps 1, 3 (reserve-ID + header), 5 (Review Depth), 7 (post-skill), and 8 (decision-point phrasing) reuse C1, C2+C3, C5, C6, and C4 respectively; the local prose below adds only the single-plan-specific content.

1. Apply C1 (pre-skill).

2. **Load references on demand** as needed:

   | When | Load |
   |---|---|
   | `--framing metacomm` | `product-design/product-design-as-intended.md` |
   | Plan touches backend/frontend/testing/i18n files | `product-design/standards.md` |
   | Plan involves auth, validation, or sensitive data | `product-design/security-checklists.md` |
   | Plan involves UX flows or visual design | `product-design/design-standards.md` |
   | Before Phase 1 review | `general/review-perspectives.md` |
   | Before writing the review log | `general/review-log-template.md` |

2b. **Grill phase** (always runs for a new plan -- CYC-002, D-005; only the specify can be skipped, CYC-004). Read `.claude/references/general/grill-phase.md` and follow its `GRL-NNN` rules. In short:
   - Classify the task (GRL-012): with code (some step will have non-N/A `Tests:`), without code, or brief already detailed. More than 12 likely requirements: propose two features first.
   - With code: propose the slug and let the user confirm (GRL-002); give the C1 notice before recording the brief verbatim (GRL-005); index the brief as `F1..Fn`. Interview in rounds of at most 4 questions, one idea each (GRL-003, GRL-004). Write `features/<slug>/intent.md` with `status: grilling` after every round (model: `.claude/references/template/intent.md`). Never fill in an answer the user did not give: record it as an assumption.
   - After each round run `python3 .claude/skills/scripts/check_intent.py features/<slug>/intent.md --json` and continue while it reports any `error`. After 5 rounds, hand the decision back (GRL-007).
   - With no `error`: show the summary in controlled voice (short sentences, fixed terms; no technical numbers) and ask Approve / Adjust / Discard (AskUserQuestion, C4; GRL-008). Only Approve writes `status: approved`, `approved_at` (UTC) and `approved_by: usuario`; then `check_intent.py <intent.md> --require-approved --strict` must exit 0 before step 3. Add `Feature: <slug>` under the plan header.
   - Without code (DOCUMENT, CHORE, RESEARCH, or a plan only of config/harness): the grill is a single question confirming the intent. Do not create `features/<slug>/intent.md` and no `features/` folder. Write a `## Intenção` section (4 lines, GRL-012) and the line `Specify: skipped -- <reason>` (CYC-004) in the plan (the only place this line is written, PFS-013); the user approves it with the plan. The plan is v2 and every step has `Tests: N/A`.
   - Metacomm framing: questions and summary use I/you.
   - `--grill`: run only this step and stop; write only `features/<slug>/intent.md`, never a plan (GRL-014). Re-entry follows GRL-011.
   - Existing v1 plans, and projects that do not use `features/`, are read and executed as before (D-008); the grill never rewrites them.

2c. **Specify phase** (CYC-003; runs only when step 2b wrote `features/<slug>/intent.md`; tasks without code skip it (step 2b writes the skip line), and v1 plans and projects without `features/` are unchanged, D-008). Read `.claude/references/general/specify-phase.md` and follow its `SPC-NNN` rules. In short:
   - Gate (SPC-001): `check_intent.py features/<slug>/intent.md --require-approved --strict` exits 0; otherwise refuse in one sentence and offer `/plan --grill <slug>`. If `check_specify.py --feature <slug> --status` says `stale`, rewrite only the scenarios and items of the REQs it lists, keeping the other scenario names (SPC-012, SPC-013).
   - Write `features/<slug>/<slug>.feature` (language of the user's words, declared in `# language:`; scenarios grouped by active REQ, each tagged `@REQ-<slug>-NNN`; a `restrição` REQ has a number) and the `## Retradução` section of `intent.md` (`rev: 1`; first person; one item per active REQ with its "Para que" and an `Exemplo:`; then "O que eu não vou fazer"), in controlled voice.
   - Run `python3 .claude/skills/scripts/check_specify.py --feature <slug>` and fix every finding yourself, at most 3 times, before showing anything to anyone (SPC-008).
   - The message (SPC-009): show the user the Retradução, never the `.feature`, tags or counts; ask Approve / Adjust / Back to the interview / Discard (AskUserQuestion, C4; texts in specify-phase.md). Adjust edits the Retradução and the `.feature` together, bumps `rev` and adds `Retradução rev N: <what changed>` to "Mudanças"; after 3 rounds hand the decision back (SPC-011). A change in *what* is wanted goes back to the grill.
   - The contract (SPC-009): show whoever reads code the `.feature` and the raw checker output; ask Approve the contract / Ask for a change / Nobody here reads code.
   - Only then run `check_specify.py --feature <slug> --approve --at <now UTC> --by usuario --contract-by <name or ninguem>`; say "approved" only on exit 0 (SPC-010). Add `Specify: approved (rev N)` under the plan header (N = `rev` of `scenarios.lock.json`). Step 3 links the steps to the scenarios.
   - `--specify`: run only this step and stop (SPC-016); without `features/<slug>/`, refuse: "A entrevista vem antes: rode /plan --grill." Without `check_features.py`, leave the drafts unapproved and say why (SPC-014).

3. Create a structured, self-contained plan with these sections (header per C3; `<depth>` set in step 5):
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
   - *steps*: structured step list -- step format and decomposition guidelines: see `.claude/references/template/plan-step.md`. With approved scenarios, build the steps from `index` of `features/<slug>/scenarios.lock.json` (`.claude/references/general/plan-from-scenarios.md`): every approved scenario is owned by exactly one step (`Scenarios:`), infrastructure steps say `N/A (<reason>)`, and the header is v2 (C3).
   - *review log*: if applicable.
   - *outcomes*: expected outcomes.
   - *smoke*: `true` if any step creates or modifies API route files or frontend page/component files; `false` otherwise. Consumed by `/implement` to decide whether to run `/critique smoke api`.
   - *reflection* (optional, appended post-execution): a `## Reflection` section of dated bullets appended by `/implement` at wrap-up from the per-step notes (`step_notes.py reflect-bullet`). Absent by default; the section may be created on first use.

4. Save the plan. If not overwriting, proceed without asking for authorization.

4b. **Coverage check (advisory)**: if `product-design/product-design-as-intended.md` contains REQ markers (`<!-- REQ-*-NNN -->`), run `python .claude/skills/design/critique_plan_coverage.py --mode advisory` and include the coverage summary in the plan after the steps. Skip silently if no REQ markers exist.

4c. **Scenario check** (plan v2 only; v1 plans skip it): run `python3 .claude/skills/scripts/check_plan_scenarios.py <plan file>` before the review. Exit 1: fix the plan yourself and run it again, at most 3 times, never inventing a scenario. If it persists, say the finding in controlled voice and ask (AskUserQuestion, C4): back to the specify (`/plan --specify`) or adjust the plan. Exit 2: say it in one sentence and do not call the plan ready. Optionally append `--table` output as `## Cobertura de cenários`.

5. **Review the plan** using a complexity-gated, two-phase process. Use `general/review-log-template.md` for the review log format.

   **Step metadata validation (before perspective review):**
   - Every step has all required fields (Files, References, Interface, Verify, Tests, checkbox). Optional fields (Depends on, Docs, Deploy, Traces) may be omitted entirely -- absent Depends on = no dependencies; absent Docs/Deploy/Traces = not applicable. `Interface:` is required but may be `N/A` -- omitting it entirely is a validation error; populate for dependency-producing steps.
   - Docs, Deploy, and Traces are present-when-relevant. When present, validate: Docs describes specific documentation to update; Deploy describes actionable deployment changes (specific env var names, ports, service names) covering Docker and standalone (Windows/Linux) where they differ; Traces lists valid REQ-xxx IDs.
   - For non-N/A `Tests:` entries: the description must express an observable behavior ('when X is called with Y, returns Z') rather than a structural assertion ('module exports class Z') or bare test name. Auto mode uses this to write a meaningful failing test before implementation.
   - `Tests: N/A` is appropriate for database migrations, configuration-only steps, pure refactors with pre-existing coverage, and framework/tooling-only steps that produce no business logic.
   - File paths for existing files verified on disk.
   - Dependencies flow forward (no circular, no backwards references).
   - No step touches >5 files (split if so).
   - Each step description is self-contained.
   - Plan v2: every step has `Scenarios:` consistent with `Tests:` (step 4c exited 0).

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
