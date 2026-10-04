# open-seja

> **Attribution.** open-seja is a derivative of
> [SEJA -- Semiotic Engineering Journeys with Agents](https://github.com/simonedjb/seja),
> Copyright (c) 2025-2026 Simone Diniz Junqueira Barbosa, licensed under
> [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). This version has been modified:
> an `npx` installer (`npm/`, not yet published), a Python quality gate template with a critical plugin, the `/mob` timed mob-programming skill, per-step reflection notes feeding `/reflect`, and related harness adjustments. See [`CHANGELOG.md`](CHANGELOG.md) for the full list. The material is provided as-is,
> without warranties (Section 5 of the license), and may be used for non-commercial purposes only.
> The name `open-seja` is used with the trademark holder's permission; see [`TRADEMARKS.md`](TRADEMARKS.md).

open-seja gives Claude Code a short cycle -- plan, implement, reflect -- in which each implementation step must pass a deterministic quality gate (lint, types, tests) before it counts as done. It is an open-access distribution of SEJA (Semiotic Engineering Journeys with Agents).

## Install

```bash
git clone git@github.com:PUC-Behring-AI/open-seja my-project
cd my-project
claude
```

Then, inside Claude Code:

```text
/seja-setup --here
```

You need git, the [`claude` CLI](https://claude.com/claude-code) installed and authenticated, and read access to this
repository (it is shared with members of the PUC-Behring-AI organization). `/seja-setup --here` turns the clone into
your project: it asks about your stack, offers the quality gate, and asks what to do with the git history. Choose
**Re-init fresh** unless you need open-seja's history, and do not push open-seja's history to a remote outside the
organization.

An `npx open-seja` installer exists in [`npm/`](npm/README.md) but is not published yet.

Two conditions apply. The quality gate currently supports Python projects (it brings pytest with it) and is offered when your backend is Python; you commit its configuration yourself once, after recording its baseline. For other stacks the cycle runs without it. And you run `/design` once, before the first plan, to record your intent. [Your first cycle](docs/quickstart.md#your-first-cycle) walks through both.

## The cycle

This release proposes a short cycle for working with an agent: PLAN, IMPLEMENT, REFLECT. It is the shortest path through the fuller SEJA lifecycle described under "About SEJA" below.

```text
  PLAN ---------> IMPLEMENT ---------------> (done)
                  each step: write -> gate PASS?
                  end: /critique
  ~~~~~~~~~~~~~~~~~~~ REFLECT (runs across all phases) ~~~~~~~~~~~~~~~~~~~
```

In words: you plan a change, and the agent implements it step by step. A step only counts as done when a deterministic quality gate (lint, types, tests, coverage, complexity) answers PASS; the agent's own say-so is not enough.
`/critique` still runs at the end of IMPLEMENT and measures what slipped past the gate.
Reflection is not a final phase: the agent leaves a short note at each step, and `/reflect` reads those notes together with the gate results.

## This is a hypothesis

I do not claim this cycle works. It is a hypothesis (H-008, the identifier used in the design record), and [`docs/hypothesis.md`](docs/hypothesis.md) says what would confirm it, what would refute it, and how you can send evidence if you try it.

## Where to go next

- [Your first cycle](docs/quickstart.md#your-first-cycle) -- a small guided run in your own project.
- [`docs/hypothesis.md`](docs/hypothesis.md) -- the hypothesis, the measures, and the refutation conditions.
- [`CHANGELOG.md`](CHANGELOG.md) -- what this release adds to SEJA.

## About SEJA

<!-- upstream:begin -->
Everything below is the upstream SEJA documentation. If you installed with `git clone` and `/seja-setup --here`, you do not need its clone options: start at [Your first cycle](docs/quickstart.md#your-first-cycle), then come back here for the concepts.

SEJA is an agent harness grounded in semiotic engineering. It gives an
agent-driven project a shared memory of intent, conventions, and
implementation state, so that people and agents can reflect on what the
system is communicating, decide together what to change, and keep that
decision trail durable. It is for designers, developers, and small teams
who want agent assistance without losing craft, context, or
accountability.

*We (SEJA creators and Claude Code) built this harness to make the communication between people and agents explicit, reviewable, and accountable.*

The harness grew out of work by Clarisse Sieckenius de Souza, Gabriel DJ
Barbosa, and Simone DJ Barbosa on redesigning an academic discussion forum
with agentic tooling. It is grounded in semiotic engineering and in Schön's
concepts of reflection-in-action, reflection-on-action, and reflection-on-
practice.

What you get once SEJA is installed in a project:

- A small set of human-authored design artifacts that capture intent,
  conventions, and the current state of the system.
- Agent-authored artifacts that track implementation state and decisions,
  kept in sync with source through lifecycle markers and quality gates.
- A planning and review loop that turns vague requests into reviewable
  plans, executes them against project conventions, and records the result.

### Pick your path

Two questions decide how you adopt SEJA: are you starting a new product or
working inside an existing one, and do you want the harness files to live
next to the source code or in a separate workspace repo? The matrix below
maps each combination to the right how-to guide.

|                | Collocated                                                                                 | Workspace                                                                                              |
|----------------|--------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| **Greenfield** | New product, harness lives next to source. [Guide](docs/how-to/greenfield-collocated.md) | New product, harness lives in a separate workspace repo. [Guide](docs/how-to/greenfield-workspace.md) |
| **Brownfield** | Existing codebase, harness added in place. [Guide](docs/how-to/brownfield-collocated.md) | Existing codebase, harness kept in a side workspace. [Guide](docs/how-to/brownfield-workspace.md)    |

You can also clone SEJA directly into your project folder (e.g. `git clone git@github.com:PUC-Behring-AI/open-seja my-project`) and run `/seja-setup --here` to finalise setup in place without copying harness files. This is the most common entry point for the collocated patterns; the four how-to guides above describe the same flow in detail.

`/seja-setup --here` finalises SEJA setup inside a directory where you have already cloned SEJA (no file copying -- it detects the current state, prompts about git history and harness-dev artefact cleanup, and pins `.seja-version` from the clone's tag). Pass `--version vX.Y.Z` to `/seja-setup` in either install or `--upgrade` mode to pin to a specific harness release; the resolved version is recorded in `.seja-version` for later upgrades. See the walkthrough at [docs/how-to/greenfield-collocated.md#option-b-clone-directly-into-the-project-folder](docs/how-to/greenfield-collocated.md#option-b-clone-directly-into-the-project-folder).

If you are unsure, skim the quickstart first, then re-read this table. The
collocated pattern is the simplest starting point for solo and small-team
work; the workspace pattern keeps design history in its own repo and is a
better fit for teams who want to add SEJA alongside an existing product
without touching its source tree.

### Read the docs

Three entry points cover everything most readers need. Start at the top and
move down as your questions get more detailed. Once you are through the
quickstart, the Skills overview in [docs/concepts.md](docs/concepts.md) also
covers how the lifecycle enters through `/research` (or `/explain`) from your
second iteration onward, after the one-shot `/seja-setup` scaffold + `/design`
intent-definition bootstrap. `/seja-setup <target>` produces a bootable
project scaffold in a single invocation (stack-populated `conventions.md`,
`CLAUDE.md`, rules, and smoke-test infra); `/design` afterward focuses on
design intent (personas, metacomm, entities, permissions, standards,
constitution) and amends `CLAUDE.md` rather than regenerating it.

- [docs/quickstart.md](docs/quickstart.md) -- 20-minute worked example; read it after [Your first cycle](docs/quickstart.md#your-first-cycle). Walks through a tiny project end to end so you can see the harness in motion before committing to a pattern.
- [docs/concepts.md](docs/concepts.md) -- sign system, profile x pattern matrix, and the Harness lifecycle chapter. Read this once the quickstart makes sense and you want to know why each artifact exists.
- [docs/foundations.md](docs/foundations.md) -- theoretical primer on semiotic engineering and reflective practice, the two research traditions SEJA draws on.
- [docs/foundations-assessment.md](docs/foundations-assessment.md) -- correspondence assessment mapping semiotic engineering constructs onto SEJA artifacts and workflows.
- [docs/how-to/](docs/how-to/) -- full how-to set covering the four profile x pattern entry points plus cross-cutting tasks like planning, quality gates, team handoffs, and harness upgrades.
- [docs/troubleshooting.md](docs/troubleshooting.md) -- symptom lookup table for diagnosing common issues when running the harness.

#### Advanced / complete harness file list

- [docs/reference/harness-reference.md](docs/reference/harness-reference.md) -- complete inventory of every skill, agent, rule, script, and reference file in the harness. This file is auto-generated from the harness source and is intended as a lookup table, not a tutorial.
- [docs/reference/glossary.md](docs/reference/glossary.md) -- canonical SEJA terminology lookup.
- [docs/reference/agents.md](docs/reference/agents.md) -- 16 agents catalog (9 evaluator, 7 generator) with purpose, invoking skill, and output.
- [docs/reference/perspectives.md](docs/reference/perspectives.md) -- 16 review perspectives catalog.
- [docs/reference/skills.md](docs/reference/skills.md) -- skills catalog organized by category.

### License

Licensed under [CC-BY-NC-4.0](https://creativecommons.org/licenses/by-nc/4.0/) (Creative Commons Attribution-NonCommercial 4.0 International).

You may use, copy, adapt, and share this work for **noncommercial purposes only**, provided that you give appropriate credit and indicate any changes made.

**Commercial use is not permitted under this license.** For commercial licensing inquiries, contact <simonedjb@gmail.com>.

Full terms are in [LICENSE](./LICENSE).

### Attribution

If you reuse or adapt this harness, please credit the original as:

> Based on the SEJA Design and Development Harness by Simone Diniz Junqueira Barbosa

and link back to this repository.

### Trademark notice

The project name, logo, and brand elements are not licensed for general use except as required for factual attribution. See [TRADEMARKS.md](./TRADEMARKS.md).
<!-- upstream:end -->
