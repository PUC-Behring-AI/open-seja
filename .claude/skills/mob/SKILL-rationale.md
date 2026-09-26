---
designer_description: "When you are maintaining /mob and need the backstory -- why it is a skill of its own, why the driver operates the agent, why the chained calls use exactly these flags, why the timer is a script with a log and a status command, and what the consent condition protects -- I am the sibling file that holds the rationale so SKILL.md can stay tight on execution instructions."
---

# Rationale -- /mob

Maintainer-only context for `mob/SKILL.md`. NOT loaded at runtime (no entry in `metadata.references`; the sync tool and call-graph generator both ignore this file). Edit both files when rationale changes.

Origin: plan-000059 of the Doutourado project ("skill /mob no open-seja (mob programming PLAN-BUILD-REFLECT, duracao ajustavel)"). The canonical governance record is the **Mob session skill (/mob)** entry under `### Architectural Decisions` in `.claude/references/general/harness-governance.md`; this file does not repeat it at length.

## Why a skill of its own (3 of 4)

The governance test asks a new skill to meet 3 of 4 criteria. `/mob` meets (a) distinct intent -- conducting a group session against a wall clock, (c) incompatible topology -- it orchestrates three different skills under a clock, and (d) its own output -- the session record. It does not meet (b): its references overlap with `/reflect`'s. The rejected alternatives recorded in the governance entry, in short:

- **A mode of `/implement` or `/reflect`** -- PLAN and REFLECT would depend on a skill that does not own them.
- **A prose-only timer** ("warn every 10 min") -- the agent has no reliable clock between turns.
- **One commit per session** (chained skills suffixed, as in the roadmap modes) -- a live session can be interrupted; per-artifact commits keep what was done, and the record links it all afterwards.
- **Implementing it first in the Doutourado project** -- the designer chose open-seja as the target.

Revisit if `/mob` ever comes to orchestrate a single skill only.

## Orchestrate, do not duplicate

`/mob` calls `/plan`, `/implement` and `/reflect` as they are, and never rewrites their instructions. Each one runs its own pre-skill/post-skill cycle and commits its own artifact. The only channel from `/mob` into a chained skill is the conversation context (`parent_skill: mob (session mob-session-<id>)`, and the stop reason for a partial `/implement`), the same channel `--roadmap` and `skip_qa_log` already use. This is the "orchestrator that calls skills" pattern that H-004 of `product-design/seja-as-intended.md` hypothesizes (textual citation: that file lives on the `seja-intention-docs` branch): what assists the group is the composition, and the orchestrator decides it.

## Why `/plan --plan`, not `--light`

`--light` produces a proposal without numbered steps. `/implement` executes plan steps, so a proposal would leave BUILD with nothing to run. The goal is sent with a size hint ("must fit in N min of BUILD, in small independent steps") so the plan is cut to the timebox instead of the timebox being stretched to the plan. An early draft of plan-000059 used `--light`; the review caught it.

## Why `/implement --manual --skip-docs`

- **`--manual`**: the default auto mode dispatches each step to a subagent and leaves no one at the keyboard. In manual mode steps run in the current context with a confirmation per step, which is what gives the driver something to do and gives the rotation a natural boundary.
- **`--skip-docs`**: the documentation prompt at the end of `/implement` would interrupt the session just before REFLECT. With the flag, an `update-documentation` pending entry is filed instead and handled after the session.

## Driver role and the open question

In v1 the **driver operates the agent**: types the instructions and approvals of each step, while navigators decide what to ask and what to accept. Rotation happens at step boundaries, never mid-step, because a step is the smallest unit `/implement --manual` completes and commits; a rotation that falls due mid-step waits.

**Open question** (from plan-000059): a mode in which the human driver writes the code and the agent only navigates and records. That mode is closer to the `apprentice` preset of seja-twist (Doutourado D-004), where the learner writes the code and the agent tutors. If wanted, it becomes a flag in a later version (e.g. `--build agent|human`); it was left out of v1 because it changes what BUILD chains (not `/implement`) and what the record measures.

## Why the timer is a script, a log and a `status` command

- **Script** (`mob_timer.py`, reading the agenda from `mob_schedule.py`): agenda arithmetic and wall-clock waits are deterministic work; the skill body only orchestrates. Both scripts have tests.
- **Log** (`mob-session-<id>-timer.jsonl`): the real time of every announcement is kept, so the record can compare planned against actual.
- **`status` as the source of truth**: the timer's lines reach the group through Claude Code's Monitor tool, and relayed lines lag while a question or a tool call is in progress. After a context compaction the agent also loses any remembered time. So the skill runs `status` (with the same `--log`, to keep the rebase offset) before every transition and every overrun decision, and never trusts remembered times. `status.state` comes from the clock alone; `status.timer` says whether the process is alive.
- **Transitions in the state file**: the timer only knows the agenda's scheduled events, not when the group actually moved. The state file carries a `transitions` list stamped from `status.now`, and "actual" in the record comes from it.
- **One timer per session**: two processes would announce the same events twice and write two logs.

## Partial stop contract with `/implement`

A timebox protects REFLECT: when BUILD runs out, the group stops building rather than skipping reflection. That needed a contract `/implement` did not have (it used to mark a plan DONE unconditionally). plan-000059 added the **partial stop** to `/implement` Manual Mode step 9, with the matching change to post-skill 2g.iv: when execution stops with unchecked steps, the plan is not marked `# DONE`, the `implement` pending entry stays open, the roadmap status update is skipped, the summary gets `PARTIAL: N/M steps; stopped by <reason>`, and completed work is still committed. `/mob` passes `session mob-session-<id>` as the reason and copies the unchecked steps to the record's Pending section, so `/implement <plan-id>` can pick them up later.

## Consent condition for research data

Mob sessions may be studied (e.g. the TWIST edition that motivated seja-twist, D-004, under an ethics protocol). A session record, a plan, a reflection with verbatim lines and the commit messages all go into git history, which is hard to scrub. Hence:

- The skill asks whether the session is research data, and if so asks the facilitator to confirm that every participant signed the consent form (TCLE). Without confirmation the session runs with initials or pseudonyms only and no identifiable reflection lines.
- Pseudonyms (`P1`, `P2`, ...) are the default labels; the name->pseudonym map is kept outside the repository.
- Participant names never go into goals, titles, commit messages or the state file.

The skill records only the facilitator's confirmation and its date, never the consent documents themselves.

## Relation to Schon's three reflection registers

Section 1.2.4 of `product-design/seja-as-intended.md` (textual citation; `seja-intention-docs` branch) maps Schon's (1983) registers onto the harness: reflection-in-action (the short rationale on every AskUserQuestion option), reflection-on-action (the note at the end of `/implement`, `/plan`, `/design`, `/document`) and reflection-on-practice (`/reflect`, recording the designer's words verbatim). `/mob` extends the third register from one designer to a group: the REFLECT phase anchors `/reflect` on the session's plan and records each participant's words verbatim, labelled per participant. It also adds a timebox to reflection-on-action -- REFLECT happens right after BUILD, within the same slot, while the experience is still fresh -- and the planned-vs-actual agenda gives the group a concrete fact to reflect on.

## References

- plan-000059 (Doutourado): `_output/plans/plan-000059-skill-mob-open-seja-plan-build-reflect.md` in the Doutourado repository.
- `.claude/references/general/harness-governance.md` -- **Mob session skill (/mob)** entry.
- `mob_schedule.py`, `mob_timer.py` and their tests in this directory.
- `/implement` SKILL.md, Manual Mode step 9 (partial stop); post-skill SKILL.md step 2g.iv.
