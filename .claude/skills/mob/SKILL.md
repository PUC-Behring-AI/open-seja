---
name: mob
description: "Run a timed mob programming (ensemble programming) group session: PLAN -> BUILD -> REFLECT with adjustable duration. I ask for the slot and phase times, build a clock agenda, run a timebox timer that announces phase and driver changes, chain /plan, /implement and /reflect, and write a session record comparing planned and actual times."
argument-hint: "<goal> [--duration 75] [--slot 90|120] [--split 20/60/20] [--plan-min N] [--build-min N] [--reflect-min N] [--rotation 10] [--no-timer]"
compatibility: "Designed for Claude Code with the SEJA harness"
metadata:
  last-updated: 2026-09-26 02:09 UTC
  version: 1.0.0
  category: planning
  context_budget: heavy
  eager_references:
    - product-design/conventions.md
    - general/constraints.md
  references:
    - product-design/conventions.md
    - general/constraints.md
    - general/shared-definitions.md
---

> Overview: see [./SKILL-quickguide.md](./SKILL-quickguide.md)

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<goal>` | Yes | What the group wants to build in this session. No participant names. |
| `--duration N` | No | Work minutes (PLAN + BUILD + REFLECT). Pre-selects the duration answer. Default: `75`. |
| `--slot N` | No | Booked minutes (e.g. `90`, `120`); the slack becomes opening + reserve + closing. Pre-selects the slot answer. Default: `90`. |
| `--split P/B/R` | No | Proportional weights for PLAN/BUILD/REFLECT, summing to 100. Default: `20/60/20`. |
| `--plan-min N`, `--build-min N`, `--reflect-min N` | No | Explicit minutes for one phase; the others stay proportional. Pre-select the per-phase answer. |
| `--rotation N` | No | Minutes per driver during BUILD. Default: `10`. |
| `--no-timer` | No | Do not launch the timer in the background; the facilitator runs it in a separate terminal. |

Flags never skip a question: every session asks slot, duration and per-phase times (step 4); flags only mark the pre-selected option.

# Mob session

> Rationale for design choices: see `SKILL-rationale.md` in this directory.

Output folder: `${MOB_SESSIONS_DIR}` (see product-design/conventions.md)
Filename pattern: `mob-session-<id>-<truncated short title slug>.md` (6-digit zero-padded ID)
Header pattern: `# Mob Session <id> | <YYYY-MM-DD HH:MM UTC> | <short title>` (macro-index regex requires this exact shape)
Sibling files (same folder): `mob-session-<id>-agenda.json`, `mob-session-<id>-timer.jsonl`, `mob-session-<id>-state.json`.

## Roles

- **Driver**: the person at the keyboard who operates the agent -- types the instructions and the approvals for each step. Only the driver types.
- **Navigators**: everyone else. They guide the driver: what to ask, what to approve, what to check.
- **Facilitator**: the person who invoked `/mob`; answers the setup questions and types the reflection lines. May also be a driver.
- **Rotation**: the driver changes every `--rotation` minutes of BUILD, in the agreed order, and only at a step boundary -- never in the middle of a step. A rotation due mid-step waits for the step to finish.

## Session state and the source of truth

- Timer status: `python .claude/skills/mob/mob_timer.py status --agenda <agenda.json> --log <timer.jsonl>`. Always pass the **same** `--log` used by `run`, or the rebase offset is lost and every time is off.
- Run `status` before every phase transition, before every overrun question, and after any context compaction; re-read the state file at the same moments. Never trust remembered times.
- `status.phase`, `phase_end`, `minutes_remaining`, `driver` and `next_event` describe the agenda. `status.state` is computed from the clock only; read `status.timer` (`running` | `ended` | `interrupted` | `stale` | `null`) to know whether the timer process is alive; `stale` (the log says running but its `pid` is gone) counts as not running.
- Once the group uses the reserve or shortens a phase, the agenda no longer matches reality: the actual phase comes from the state file `transitions`, and `status` is used only for the clock (`now`) and the remaining time. Rotations are then computed from BUILD's actual start in `transitions`: the driver advances by one at a step boundary when the elapsed BUILD time has crossed the next `--rotation` mark.
- State file `mob-session-<id>-state.json`: `{"session": "<id>", "state": "running|completed|interrupted", "phase": "...", "plan_id": null, "reflection_id": null, "driver_index": 0, "timer_pid": null, "participants": ["P1", ...], "research_data": false, "consent_confirmed": null, "transitions": [{"phase": "PLAN", "event": "start|end", "at": "<UTC ISO>"}], "pending": []}`. Participant **labels only**; never the name->pseudonym map. Update it at every transition, taking `at` from `status.now`.
- Chained skills: before each `/plan`, `/implement` and `/reflect`, state in the conversation `parent_skill: mob (session mob-session-<id>)` so their post-skill step 8b records `parent_skill: mob` in telemetry. Do not rewrite or override any instruction of a chained skill; each one runs its own pre-skill/post-skill cycle and commits its own artifact.

## Skill-specific Instructions

1. Run `/pre-skill "mob" $ARGUMENTS` to add general instructions to the context window. If `<goal>` is missing, ask for it in plain text.

2. Reserve the ID: `python .claude/skills/scripts/reserve_id.py --type mob-session --title '<short goal>'`. Capture the 6-digit ID.

3. **Research data and participants.** Ask via AskUserQuestion: "Will this session be used as research data?" Options:
   - **No** -- Recommended when the session is ordinary team work or a class exercise not covered by a research protocol. NOT recommended when anything from it (plan, reflection lines, record) may appear in a study.
   - **Yes** -- Recommended when the session is part of a study (e.g. a CEP-approved protocol). NOT recommended when no ethics protocol covers the participants -- then it is not research data.

   If **Yes**, apply the consent condition:
   - Ask the facilitator to confirm that every participant signed the protocol's consent form (TCLE). Without that confirmation, the session proceeds with initials or pseudonyms only and no identifiable reflection lines.
   - Pseudonyms (`P1`, `P2`, ...) are the default labels.
   - Tell the facilitator to keep the name->pseudonym map outside the repository (never under `_output/`).
   - Without consent confirmation, `--drivers` (step 4) receives pseudonyms or initials only.

   In every case, warn that the plan, the reflection, the commit messages and the four session files -- record `.md`, `-agenda.json` (its `drivers` list), `-timer.jsonl` (driver names in `driver_change`) and `-state.json` -- go into the git history.

   Then ask in **plain text** (not AskUserQuestion) for the participant list, in the form the facilitator chooses (names, initials or pseudonyms; pseudonyms when research data), and the driver order. Never put participant names in the goal, the titles or commit messages.

4. **Agenda.** Always ask, via one AskUserQuestion call with three questions and rationale on every option, even when flags were given (a flag only moves its value to the first, pre-selected option):
   - **Slot**: `1h30 (90 min)` -- Recommended when the booking is a single class period. / `2h (120 min)` -- Recommended when you expect breaks or a long REFLECT; NOT recommended when the room is booked for 90 min. / Other value in "Other".
   - **Work duration**: `1h15 (75 min)` -- Recommended as the default; leaves 15 min of slack in a 90-min slot. / a shorter value (e.g. `60 min`) -- Recommended when setup or onboarding will eat into the slot; NOT recommended when the goal needs several BUILD steps. / Other value in "Other".
   - **Per-phase times**: `Proportional 20/60/20` (or the `--split` value) -- Recommended when you have no reason to favor a phase. / Own minutes in "Other", as `PLAN/BUILD/REFLECT` (e.g. `10/50/15`) -- Recommended when the plan is already clear or the group wants a longer reflection; NOT recommended when you are unsure how long planning takes.

   Map the answers to `mob_schedule.py` flags (own minutes -> `--plan-min/--build-min/--reflect-min`; when all three are explicit and the duration answer was the default, drop `--duration`). Run:
   ```bash
   python .claude/skills/mob/mob_schedule.py <flags> --rotation <N> --drivers "<labels in driver order>" --format md
   python .claude/skills/mob/mob_schedule.py <flags> --rotation <N> --drivers "<labels in driver order>" --format json > ${MOB_SESSIONS_DIR}/mob-session-<id>-agenda.json
   ```
   On exit 2, show the error and re-ask the offending question. Show the md agenda and ask via AskUserQuestion: **Confirm** -- Recommended when the times and the driver order look right. / **Adjust** -- Recommended when any phase or the order is off; I ask again. Loop until confirmed.

5. **State and timer.** Create the state file (see "Session state" above), then start **one** timer process -- never a second one:
   ```bash
   python .claude/skills/mob/mob_timer.py run --agenda ${MOB_SESSIONS_DIR}/mob-session-<id>-agenda.json --log ${MOB_SESSIONS_DIR}/mob-session-<id>-timer.jsonl --rebase-now
   ```
   Default: launch it through Claude Code's Monitor tool and relay each line (`HH:MM | PHASE | text`) to the group. If Monitor is unavailable or `--no-timer` was given, ask the facilitator to run the same command in a separate terminal, preferably projected. Tell the group that relayed announcements may lag while a question or a tool is in progress; `status` is the source of truth. Once the log has its `started` record, copy its `pid` to `timer_pid` in the state file. The session is now in OPENING: introduce the roles and the first driver.

6. **PLAN.** Run `status`; record the transition. Run `/plan "<goal>. The plan must fit in <build-min> min of BUILD, in small independent steps." --plan` (not `--light`: it produces a proposal without steps, which `/implement` cannot execute). Note the plan ID printed by the `/plan` post-skill and save it as `plan_id` in the state file.

7. **BUILD.** Run `status`; record the transition. Run `/implement <plan_id> --manual --skip-docs` (`--manual` so the driver conducts each step; `--skip-docs` so the documentation question does not interrupt the session -- the `update-documentation` pending entry is filed instead). At each step boundary, run `status`; if a rotation is due, announce the new driver, update `driver_index`, then continue.
   At the 5-min BUILD warning (or at the first step boundary after it), ask via AskUserQuestion:
   - **Use the reserve** -- offered only when the agenda's `reserve` > 0. Recommended when the current step is nearly done and RESERVE minutes remain. NOT recommended when REFLECT would be cut short.
   - **Shorten REFLECT by N min** -- offered only when `reserve` is 0. Recommended when the current step is nearly done; NOT recommended when REFLECT is already short.
   - **Stop BUILD** -- Recommended when the remaining steps will not fit; protecting REFLECT is the point of the timebox.
   Stopping: finish the step in progress, then tell `/implement`, via the conversation context, to stop with reason `session mob-session-<id>`. It follows the `/implement` Manual Mode step 9 partial stop (no `# DONE`, the `implement` pending entry stays open, `PARTIAL: N/M steps; stopped by session mob-session-<id>` in the plan summary, completed work committed). Copy the unchecked steps to `pending` in the state file.

8. **REFLECT.** Run `status`; record the transition. Run `/reflect`. In its Step A, the facilitator chooses **A specific artifact by ID** and gives `plan-<plan_id>`. In its Step C, the facilitator types each participant's words on its own line, prefixed with the participant's label from the record (`P1: ...`, `Ana: ...`); `/reflect` records them verbatim. Save the reflection ID as `reflection_id`. When research data was declared without consent confirmation, remind the facilitator before Step C: no identifiable lines.

9. **Close and write the record.** Run `status`. If `timer` is `running`, stop it with `kill -TERM <timer_pid>` (the log receives `ended`, reason `terminated`); `stale` means it is already gone. Set `state` in the state file (`completed`). Write `${MOB_SESSIONS_DIR}/mob-session-<id>-<slug>.md`:

   ```markdown
   # Mob Session <id> | <YYYY-MM-DD HH:MM UTC> | <short title>

   **State**: completed | interrupted

   ## Goal
   ## Participants        (labels only, in driver order)
   ## Consent             (research data: yes/no; facilitator's TCLE confirmation and date; no documents attached)
   ## Planned vs actual agenda
   ## Rotations
   ## Artifacts           (plan, reflection, commit SHAs)
   ## Pending             (unchecked plan steps, pending entries left open)
   ```

   Planned vs actual: one row per phase -- planned start/end from the timer log's `phase_start`/`phase_end` `scheduled` fields (rebased agenda), actual start/end from the state file `transitions`, and the delta in minutes. Rotations: the log's `driver_change` records (`scheduled`, `previous_driver` -> `driver`) and whether each happened at the next step boundary. Add the timer's final record (`ended` reason, or `interrupted`).

10. Run `/post-skill <id>`.

## Explicit rules

- **Overrun**: when `status` shows the agenda has moved past the phase the group is still in, ask via AskUserQuestion: **Use the reserve** (only when `reserve` > 0) -- Recommended when RESERVE minutes remain and the current phase is close to done. / **Shorten the next phase** -- Recommended when the reserve is spent or REFLECT must stay intact. Record the choice in the state file; the timer keeps the original agenda, so tell the group how far behind its announcements the group is.
- **Abandonment**: if the group stops early, stop the timer with `kill -TERM <timer_pid>` (unless `status.timer` is already `ended`, `interrupted` or `stale`), let any running chained skill apply its own stop rule (`/implement` partial stop), write the record with `**State**: interrupted` and what was left in Pending, and run `/post-skill <id>`.
- **Context compaction**: re-read the state file and run `status` before doing anything else.
- Never write participant names in the goal, titles or commit messages, nor -- when pseudonyms were chosen -- in any of the four session files (record, agenda `drivers`, timer log, state file); never store the name->pseudonym map anywhere in the repository.
