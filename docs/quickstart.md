---
diataxis: tutorial
freshness: release-bound
last-reviewed: 2026-10-04
---

# Quickstart

This page gets you from zero to a running SEJA project in about 20
minutes, with no prior SEJA knowledge required. For the full
narrated version of this flow, with harness callouts and role
sidebars, see [how-to/greenfield-collocated.md](how-to/greenfield-collocated.md).

Installation and upgrades share a single entry point: `/seja-setup`
is the unified install/upgrade command and dispatches by project
state -- it installs the harness when the target is empty, and
upgrades harness files in place when it detects an existing
SEJA project.

## The three commands

Run these in order. Each is explained in the worked example below.
Nothing else needs to happen on this first screen: you can start
typing now and read the "why" afterwards. Once you have a project,
[Your first cycle](#your-first-cycle) is the next stop.

From a terminal, clone the harness into a new folder and open Claude Code
there (you need read access to the repository; it is shared with members
of the PUC-Behring-AI organization):

```bash
git clone git@github.com:PUC-Behring-AI/open-seja my-project
cd my-project
claude
```

Inside Claude Code, the three steps are:

```bash
/seja-setup --here
```

```bash
/design
```

```bash
/seja-setup --upgrade
```

## Worked example: my-project

We will walk you through a concrete run so you see a real result
before you leave this page. The project is a small personal task
tracker. The domain is "personal tasks and reminders". The stack
is Python plus SQLite. The mode is greenfield (new project, no
prior code to migrate).

### Step 1: `/seja-setup my-project`

This example shows the other install path: running Claude Code in a checkout of open-seja and copying the harness
into a separate folder. If you cloned straight into `my-project/` as above, your Step 1 is `/seja-setup --here`
instead; the rest of the example is the same.

From an empty parent directory, you run:

```bash
/seja-setup my-project
```

You will see SEJA copy its harness files into `my-project/.claude/`
and `my-project/.claude/references/`. When the setup finishes, you have a
new SEJA-ready project directory containing the skills, rules, and
reference scaffolding the harness needs to operate. You then run
`cd my-project` and move on to the next command.

### Step 2: `/design`

From inside `my-project`, you run:

```bash
/design
```

You will be asked a short sequence of questions about your project.
For this worked example, you answer them as if you are building a
personal task tracker: the project name is `my-project`, the domain
is `personal tasks and reminders`, the stack is `Python + SQLite`,
and the mode is `greenfield`. SEJA then generates four project
files under `product-design/`, customized with your answers.

To confirm the files exist, you run:

```bash
ls product-design/
```

You should see four markdown files listed. If you see them, the
design step worked and you can move on.

### Step 3: `/seja-setup --upgrade`

You do not need to run this on day one. It is here so you know
how to keep the harness fresh later, once a newer version of
SEJA has been published. When you do run it, you type:

```bash
/seja-setup --upgrade
```

SEJA pulls the latest harness files from the foundational repo
without touching anything under `product-design/` or `_output/`.
Your design decisions and your plan and execution history stay
exactly where you left them. You can run `/seja-setup --upgrade` as
often as you like; it is non-destructive by construction.

If you want to pin to a specific SEJA release for reproducibility,
`/seja-setup` accepts `--version <tag>` (e.g. `v0.1.0`) in both
install and upgrade modes; see [how-to/upgrade.md -- Pinning to a specific release](how-to/upgrade.md#pinning-to-a-specific-release).

## What just happened

You now have a SEJA project with four files under `product-design/`:

- `conventions.md` captures your project directory layout and the
  harness variables the agents read at the start of every skill.
- `constitution.md` holds the immutable principles for this project,
  read-only for the harnessed agents after you approve it.
- `standards.md` captures your engineering standards for backend,
  frontend, testing, and i18n, so the agents know what "good" means
  in your codebase.
- `product-design-as-intended.md` is your working design intent, the
  file you will edit by hand as the project evolves and the file
  every planning session reads first.

The harness reads these four files at the start of every skill
invocation. You do not need to memorize the whole file inventory
yet: you have a running project, and that is enough for now.

## Your first cycle

Once the project has its four design files, you can try the cycle this release proposes: PLAN, IMPLEMENT, REFLECT
(see [the hypothesis](hypothesis.md)). It takes one small change and roughly an hour end to end, most of it in
`/design` if you have not run it yet. It shows you the quality gate and the reflection notes working in your own
project.

1. **Install, with the gate.** Clone the harness (`git clone git@github.com:PUC-Behring-AI/open-seja my-project`),
   open Claude Code in `my-project/` and run `/seja-setup --here` (or `/seja-setup` in an existing project). There is
   no menu: `/seja-setup --here` goes straight to questions about your stack, then asks whether to install the
   quality gate, what to do with the git history (choose **Re-init fresh** and type `confirm`; the history is
   open-seja's, not yours) and which harness files to tidy up (the defaults move `docs/` to `docs/seja/` and rename
   `README.md` and `CHANGELOG.md`). The gate is offered when your backend is Python; for a new, empty project, tell
   `/seja-setup` the stack is Python with no frontend. Accept the gate. Setup makes its initial commit, then adds the
   gate's commands to `product-design/conventions.md` and leaves that change for you to commit (step 2). You should
   now see `gate.py` in the project root. Setup does not create the Python project itself, so give the gate something
   to measure: a `pyproject.toml` with the blocks from
   `.claude/references/template/quality-gate/python/pyproject-dev.example.toml` (set `package` to your package
   name), one package under `src/` (for example `src/my_project/__init__.py`) or in your backend folder, a `tests/`
   folder, and the tools the gate runs (`uv add --dev ruff pyright pytest pytest-cov pytest-timeout
   "coverage[toml]>=7.5,<8" "radon>=6,<7" "mutmut>=3,<4" import-linter`). If the project is not Python, skip the
   gate: the cycle still works, and the `gate` field of each step note reads `not-installed`.
2. **Record the baseline and commit the gate.** From the project root, run `uv run python gate.py --init-baseline`
   once. The gate now remembers the current state, and from here on thresholds only move when you accept it. Then
   commit the gate's configuration yourself: `git add -A && git commit -m "chore: quality gate baseline"`. Agents are
   not allowed to commit changes to the gate's commands, so until this commit exists every agent commit, including
   the ones `/design`, `/plan` and `/implement` make, is refused. If `gate.py` is missing, the gate was not
   installed: re-run `/seja-setup` and choose the gate.
3. **Record your intent.** Run `/design` (skip it if you already ran it in the worked example). It asks a short
   sequence of questions about your project and writes `product-design/product-design-as-intended.md`; a plan needs
   that file.
4. **Plan a small change.** Run `/plan` with something tiny, for example "add a function `slugify(title)` with a
   test". You get a numbered plan, reviewed before anything is written.
5. **Implement it.** Run `/implement <plan-id>`. For each step you will see the gate run on the files the step
   touched, up to three attempts, and a step only counts as done on PASS. Each step also leaves a short note in
   `_output/plans/plan-<id>-progress.md`, shown to you as it is written: what happened, what deviated, what the agent
   is less sure about, with the gate result of that step. A note looks like this:

   ```text
   ### Step 2 -- reflection-on-action | 2026-10-04 14:10 UTC | Add slugify
   - happened: added slugify() and a test for accents and spaces
   - deviated: none
   - less-sure: behavior for empty strings
   - gate: PASS (exit 0, attempts 1, _output/quality/plan-000001-step-2-try-1.json)
   ```

6. **Reflect.** Run `/reflect` on the plan. It reads the notes and the gate evidence before it asks you anything, and
   it records your answer in your own words.

### What you just tested

You ran the gate and reflection-note half of H-008. The other half -- the mirrors, `/communicate` for the plan and
`/explain drift` after implementing -- is offered by `/plan` and `/implement` and was not part of this first cycle;
try them on a second one. To see how the cycle did, run `python3 .claude/skills/scripts/step_notes.py parse --stats
_output/plans/plan-<id>-progress.md` and look at the gate reports under `_output/quality/`. [The hypothesis
page](hypothesis.md) says what the numbers mean, and how to send them to me if you choose to.

## The canonical loop: what happens on iteration 2 and beyond

Once the project is designed, every subsequent change follows the
same seven-step loop. Walk through it once here so you recognise
the shape when you meet it in a real change. Check comes before
document and communicate -- validate before you communicate.

1. **`/research`** (or **`/explain`** as the alternative entry) --
   investigate what you are about to change. Start here on every
   iteration-2+ change, before you touch any intent or plan. Use
   `/research` for Q&A and recommendations; use `/explain` when
   you need a deeper narrative on behavior, code, data model, or
   architecture.

2. **`/design`** | **`/plan`** -- branch based on what research
   surfaced. Run `/design` when the intent itself needs to change
   (new decision, revised journey, updated standard). Run `/plan`
   when the intent is stable and you only need a plan to implement
   against it.

3. **`/implement`** -- execute the plan. SEJA runs the numbered
   steps, tracking progress and handling errors as it goes.

4. **`/critique`** -- validate before you communicate. Run the
   appropriate mode (`validate`, `review`, `preflight`, `smoke`,
   or `health`) to confirm the change is sound. This gate is
   deliberately placed before documentation so you never document
   something that fails its own checks.

5. **`/document`** | **`/communicate`** -- record the change and,
   when appropriate, share it. `/document` updates user and
   developer documentation based on the plan's Docs fields or
   auto-detected changes. `/communicate` generates tailored
   stakeholder material for a specific audience.

6. **`/reflect`** -- close the cycle. `/reflect` surfaces patterns
   across recent skill runs and anchors a short reflection on the
   artifacts you just produced. This is the cycle-closing step; it
   is what turns a sequence of commands into learning you can reuse
   on the next iteration.

When specs and as-coded state fall out of alignment, run
`/explain drift` to compare them and surface what needs to
change; it feeds back into `/design` or `/plan` naturally.

## Now read concepts.md

You are ready for the conceptual model. The rest of the public
docs assume you have run the three commands above and want to
understand what SEJA is doing under the hood. Read
[concepts.md](concepts.md) next. It walks you through the harness
lifecycle, the sign system, and the profile-by-pattern matrix, so
you can decide which how-to to read first when you plan your first
real feature.
