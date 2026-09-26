**What it does**: Runs a timed mob programming (ensemble programming) session for a group: **PLAN -> BUILD -> REFLECT** inside a booked slot. Every session starts by asking the slot, the work duration and the per-phase times, then builds a clock agenda (opening, PLAN, BUILD with driver rotations, REFLECT, reserve, closing). A timer script announces each phase change, driver change and end-of-phase warning, and logs the real time of each event. The session chains the existing skills: `/plan --plan` for the goal, `/implement <id> --manual --skip-docs` with the current driver operating the agent, and `/reflect` anchored on that plan, with each participant's words recorded verbatim. At the end I write a session record to `_output/mob-sessions/mob-session-<id>-<slug>.md` with participants (labels only), planned vs actual agenda, rotations, the plan and reflection IDs, and what was left pending.

Roles: the **driver** is the one person at the keyboard and operates the agent (types the instructions and the approvals of each step); the **navigators** guide the driver; the **facilitator** invoked `/mob` and answers the setup questions. The driver changes every `--rotation` minutes of BUILD, only at a step boundary.

If the session will be used as research data, I ask the facilitator to confirm that every participant signed the protocol's consent form; without that confirmation the session runs with initials or pseudonyms only and no identifiable reflection lines. The name->pseudonym map never goes into the repository.

**Examples**:
> `/mob "implement task filter"`
> Asks the slot (1h30 or 2h), the work duration (default 1h15) and the per-phase times (default proportional 20/60/20, i.e. 15/45/15 min), plus the participants and driver order. Shows the agenda for confirmation, starts the timer, and runs PLAN, BUILD and REFLECT.

> `/mob "implement task filter" --duration 60 --slot 120 --build-min 40 --rotation 10`
> Same questions, but the answers 60 min of work, a 120-min slot and 40 min of BUILD come pre-selected; PLAN and REFLECT split the remaining 20 min proportionally, and drivers rotate every 10 min.

> `/mob "implement task filter" --split 10/70/20 --no-timer`
> Pre-selects a 10/70/20 split and does not launch the timer in the background: the facilitator runs it in a separate (preferably projected) terminal.

Flags never skip a question: the skill always asks slot, duration and per-phase times; a flag only moves its value to the pre-selected option. Other flags: `--plan-min N`, `--reflect-min N` (explicit minutes for one phase; the others stay proportional).

**When to use**: A group (class, team, study session) wants to plan, build and reflect together within a fixed end time, with one driver at a time and a record of how the time was actually spent. Not for solo work -- use `/plan` followed by `/implement` instead. Not for long features that will not fit in one BUILD phase: ask for a small goal, or accept that the plan will stop partially and continue later.

**Next step**: `/implement <plan-id>` to finish the steps left pending when BUILD stopped early (the plan is not marked DONE and its pending entry stays open). `/reflect --deep` over the period of several sessions to see how the group's practice evolved.

**See also**: `/reflect` for the reflection conventions used in the REFLECT phase; `/pending` for the entries a session leaves open.
