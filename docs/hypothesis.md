---
diataxis: explanation
freshness: release-bound
last-reviewed: 2026-10-04
---

# The hypothesis (H-008)

This release of open-seja is built around one hypothesis. I call it a hypothesis because I have not measured it
yet, and I want you to be able to see what would make me wrong.

## The hypothesis in plain words

A short cycle -- PLAN, IMPLEMENT, REFLECT -- can be offered as the entry path for working with an agent, without
losing what SEJA's design record protects (validate before you communicate), provided two conditions hold. To install, see the [README](../README.md#install).

1. **A deterministic gate decides each step.** Inside IMPLEMENT, an agent's step
   only counts as done when the gate answers PASS. PASS is a tool result, not a sentence in a prompt.
2. **Reflection runs across the phases, and each phase ends with a mirror.** After PLAN, the plan told to an
   audience (`/communicate`, which turns a plan into a message for a specific audience); after IMPLEMENT, the drift between what was intended and what exists
   (`/explain drift`, which compares what was intended with what the code now does). Both are offered to the designer, never imposed.

The cycle also has a precondition: without `product-design/product-design-as-intended.md` there is no cycle. Run
`/design` first.

## Why a short cycle needs a gate

An agent writes faster than a person can review. If the only validation is `/critique` at the end, the person
reviews everything at once, after the fact. The gate moves validation inside the loop, step by step: lint and types,
tests with branch coverage, complexity weighted by coverage (the CRAP score) on the functions the step touched, and
dependency contracts between modules. A slower run adds mutation testing.

The gate's thresholds only move by a human hand (a ratchet from a baseline). The agent stays in the inner loop;
you stay in the outer loop, owning the constraints.

`/critique` does not go away. It still runs at the end of IMPLEMENT and before `/document` and `/communicate`. What
changes is its role: it stops being the first validation and becomes the measure of what escaped the gate.

## What we measure

| Measure | Where the number comes from |
|---|---|
| Iterations until PASS, per step | the gate result per step (JSON reports in `_output/quality/`) |
| Escape rate: critical `/critique` findings in code from steps that had PASS, divided by steps that had PASS | the `/critique` log against the gate results |
| Intent escapes: drift items (built without intent, intent not built) per plan, in cycles where drift was measured | the `/explain drift` report after IMPLEMENT |
| Mutation survivors per commit, in the slow run | the gate result (`gate.py --full`) |
| Evasion markers added (skip, xfail, no cover, no mutate) without a recorded reason | the gate's ratchet |
| Per-step notes that report a deviation and are cited by the next step ("a note that acts") | per-step notes and the following step; `step_notes.py parse --stats` |
| Mirrors accepted per phase (plan communication, IMPLEMENT drift) | the `/plan` and `/implement` records in the progress file |

Before the first measured cycle, the designer fixes and records the minimum number of plans and the thresholds.
Fixing them after seeing the data would invalidate the measure.

## What would prove it wrong

It would be confirmed by an escape rate below the threshold, stable evasion markers, most deviation notes changing
the next step, and, in cycles where drift was measured, rare intent escapes. It would be refuted by any of these:

1. **The escape rate is above the threshold.** The gate does not take the place of validation.
2. **Evasion markers or mutation survivors grow while the gate stays at PASS.** The agent is optimizing the number,
   and the ratchet does not hold.
3. **Per-step notes change no later step.** Reflection has become a ritual.

There is a fourth condition worth watching: frequent intent escapes with the gate at PASS. The gate proves
correctness, not intent, so the drift mirror would have to become a fixed step instead of an offer.

## How you can help

Run one cycle in a small project, starting from [Your first cycle](quickstart.md#your-first-cycle). One cycle is a
demonstration, not a measurement: the thresholds above are fixed before the first measured cycle, so a single run
cannot confirm or refute anything. I still want to hear about it, labelled as an anecdote.

To tell me how it went, [open an issue](https://github.com/PUC-Behring-AI/open-seja/issues/new) with the output of
`python3 .claude/skills/scripts/step_notes.py parse --stats _output/plans/plan-<id>-progress.md` and a short summary
of the gate results. Nothing is collected automatically: open-seja has no telemetry, and sharing is your decision.

If the cycle fails for you, that is exactly the evidence I want.

## Source

The authoritative text is section 2.8 of the grounding in [`product-design/product-design-as-intended.md`](https://github.com/PUC-Behring-AI/open-seja/blob/dev/product-design/product-design-as-intended.md) §3
(in Portuguese, on the `dev` branch: the distributed `main` does not carry the design record). It sits on H-004 (the workflow agent has an orchestrator), D-001 (the three-phase workflow agent
is the coarse grain of the canonical path), and D-002 (what this release does while the hypothesis is under test).
Terms: "portao" in the source is "gate" here, and BUILD is IMPLEMENT.
