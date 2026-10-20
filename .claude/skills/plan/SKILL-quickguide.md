**What it does**: Creates a step-by-step plan for your next feature, bug fix, or improvement. You describe what you want; before writing the steps, the agent plays a language game with you: it tells short scenes of what you asked working (and of what it should not do), and you accept, refuse or fix each one. What you accepted becomes the plan's requirements and use cases, what you refused becomes what it will not do, and your corrections are quoted as you said them. The agent then retells the plan in first person, you approve it, and every step that tests a requirement says so in a `Covers:` line (plan format v3). Three modes: **standard** (single plan, default), **lightweight** (`--light`, quick proposal), and **roadmap** (`--roadmap`, full product roadmap with dependency-aware execution waves).

**Examples**:
> `/plan Add a tagging feature so users can organize their tasks by topic`
> Creates a plan with steps covering data model, UI components, and search integration. Each step lists files to change, verification criteria, and dependencies.

> `/plan --light Fix the date picker timezone offset bug`
> Generates a lightweight proposal -- a shorter, less formal plan suitable for small fixes.

> `/plan --framing metacomm I want users to feel confident that their data is saved`
> Frames the brief as a designer's metacommunication message (I/you phrasing), preserving the user-experience perspective in the plan.

> `/plan --roadmap Build a complete task management application`
> Reads project design specs, decomposes into work items, groups into dependency-aware waves (foundation, services/API, frontend, cross-cutting, testing), and generates individual plans for each item.

> `/plan --roadmap --from-spec specs/roadmap-spec.md`
> Generates a roadmap from a pre-filled spec file instead of interactive prompts.

> `/plan --roadmap --auto`
> Auto-generates a roadmap from project reference files without manual input.

> `/plan --roadmap --auto --only-unimplemented`
> Scopes the roadmap to REQ items that lack a `STATUS: implemented` / `established` marker -- useful on established projects for covering only the open-item delta.

> `/plan --review deep`
> Overrides the complexity-gated review depth to force a deep review (all 16 perspectives).

**Short game**: a task with no code (docs, chore, research) and each item of a roadmap get a two-scene game that fills only the intention. `--light` proposals skip the game.

**When to use**: You have a clear idea of what you want to build or fix and want a structured plan before any code changes happen. If you omit both `--plan` and `--roadmap`, the agent auto-detects the best mode from your brief (>=3 entities or >=2 architectural layers suggests roadmap; single bug/file suggests single plan) and asks for confirmation before proceeding. Use `--framing metacomm` when describing the change from the user's perspective. Use `--light` for quick proposals that don't need full step metadata.

**Next step**: `/implement` to execute the plan (or the first roadmap item) once you have reviewed it.
