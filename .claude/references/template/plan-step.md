---
designer_description: "When /plan generates a structured step inside the ## Steps section of a plan file, I'm the canonical step format -- title, self-contained description, Files / References / Depends on / Verify / Tests / Docs / Traces / Scenarios metadata, checkbox -- and the decomposition guidelines that keep each step executable by a fresh subagent without shared context."
---

# Template: Plan Step Format

Canonical shape referenced by: `.claude/skills/plan/SKILL.md` step 3 (Step format section).

## Step shape

Each step must be self-contained -- executable by a subagent with no shared context from prior steps.

```markdown
## Steps

### Step 1: <short imperative title>
<What to do -- a self-contained description that a subagent can execute without reading other steps.
Include enough context that the step makes sense in isolation: what the code should do, not just which file to edit.>
- **Files**: <path> (create|modify|delete), <path> (modify), ...
- **References**: <reference-name>, <reference-name>, ...
- **Depends on**: Step N, Step M *(omit line when no dependencies)*
- **Interface**: <expected public surface for dependency-producing steps (e.g., "exports `UserService` with `find_by_id(id: str) -> User | None`")> | N/A
- **Verify**: <how to know this step succeeded -- e.g., "tests pass", "migration runs forward and backward", "endpoint returns 200">
- **Tests**: <what tests to create or update -- e.g., "Add unit tests for new service method", "Update existing API tests for changed response format"> | N/A (no testable code changes)
- **Docs**: <what documentation to create or update> *(omit line entirely when N/A)*
- **Deploy**: <deployment configuration changes required by this step — new env vars, changed ports, new services, Docker or server-config changes; cover Docker and standalone (Windows / Linux) where they differ> *(omit line entirely when N/A)*
- **Traces**: REQ-xxx, REQ-yyy *(omit line entirely when N/A)*
- **Scenarios**: `<slug>/<file>.feature::<scenario name>`, `<slug>/<file>.feature::<other scenario>` | N/A (<reason>) *(plan_format_version: 2 only)*
- [ ] Done
```

## Decomposition guidelines

- Each step must be completable in one subagent context window (rule of thumb: touches <=5 files). Split larger steps.
- **Files**: every path the step reads, creates, modifies, or deletes. Verify existing files during planning.
- **References**: only `product-design/` files relevant to this step (e.g., `product-design/standards.md § Backend` for Python; `product-design/standards.md § Frontend` for React). Omit irrelevant refs.
- **Depends on**: step numbers whose output this step requires. Omit the field entirely for independent steps (absent = no dependencies). Orchestrators use this to avoid executing before dependencies complete.
- **Interface**: populate for steps that create modules, services, or functions consumed by downstream steps in the same plan. List the expected public surface (function names, class names, exported types with signatures). `N/A` for leaf steps or steps with no downstream consumers within the plan. When present and `Tests:` is non-N/A, auto-mode subagents use this as a type contract when writing the TDD failing test (TDD is triggered by non-N/A `Tests:`, not by `Interface:`).
- **Verify**: a concrete, testable condition. Prefer automated checks ("tests pass", "linter clean") over subjective ones.
- **Tests**: required for FEATURE/FIX/REFACTOR steps that create or modify source code files. `N/A` for doc/config/harness-only steps. When too small to warrant its own tests, indicate which step's tests will cover it. For steps where TDD applies (non-N/A `Tests:` in auto mode), express the test scenario as an observable behavior: "when X, returns Y" rather than a structural assertion ("module exports class Z") or bare test names. This lets the subagent write a meaningful failing test before implementation.
- **Docs**: include for FEATURE/REDESIGN steps that create or modify user-facing code or public APIs. Specify what documentation to create or update (e.g., "Update API reference", "Add contextual help page"). Omit for internal refactors, test-only changes, config.
- **Deploy**: include when the step adds, removes, or changes deployment configuration: new environment variables (name + expected value shape), changed ports, new services or processes, container/image changes, nginx/web-server config, secrets, volume mounts, migration commands that must run before startup. Describe what operators need to configure for Docker and for standalone server (Windows and Linux), noting where they differ. Omit when the step has no deployment impact — only harness scripts, tests, or pure UI changes with no server-side configuration effect.
- **Traces**: include when the step implements a design requirement. Comma-separated REQ IDs from `product-design-as-intended.md` (e.g., `REQ-ENT-001, REQ-PERM-003`). Omit when no REQ markers exist or the step does not trace to one. See `general/shared-definitions.md` for the REQ ID convention.
- Order steps so dependencies flow forward (Step 2 depends on Step 1, not the reverse).
- **Scenarios** (`plan_format_version: 2`): the scenario keys this step **owns** (the step where the scenario becomes a test), each `<slug>/<file>.feature::<scenario name>` between backticks, exactly as in `index` of `features/<slug>/scenarios.lock.json`; never a `@REQ-` tag. `N/A (<reason>)` (at least 3 words) when the step delivers no scenario: infrastructure, migration, config, refactor with prior coverage; then `Tests:` is normally N/A too. Required in every step of a plan with `Specify: approved` (including `Tests: N/A` steps, which use `N/A (<reason>)`; PFS-003); each approved scenario has exactly one owner step. Rules and header: `general/plan-from-scenarios.md` (PFS-001..015); checker: `check_plan_scenarios.py`.
  Example (emenda 000015): a step that owns a scenario has the line `- **Scenarios**: ` followed by the key `contas-da-semana/contas-da-semana.feature::Marcar uma conta como paga` between backticks; an infrastructure step has `- **Scenarios**: N/A (migração sem comportamento observável)`. The key replaces the plan-000007 wording "`@REQ-...` or scenario names" (CYC-028; contract section "Emendas do item 9").

## Format version

- `plan_format_version: 2` has the header lines `Feature: <slug>` and `Specify: approved (rev N)` (or `Specify: skipped -- <reason>` with no `Feature:`) and requires `Scenarios:` in every step of a plan with `Specify: approved` (scenario keys, or `N/A (<reason>)` for a step with no observable behavior). With `Specify: skipped`, no step has non-N/A `Tests:` for observable behavior. New plans are v2 in both cases. A v2 plan that `check_plan_scenarios.py` refuses (step without scenario, scenario without step, old scenarios) is invalid: `/plan` fixes it before saving, `/implement` stops and does not fix it.
- `plan_format_version: 1` (or absent) remains **valid forever**. `/plan` and `/implement` read v1 plans as before; the absence of `Scenarios:` is at most advisory, never blocking.
- Rules and rationale: `general/extended-cycle-contract.md`, section "Compatibilidade" (CYC-018). Fixtures: `.claude/skills/scripts/tests/fixtures/plan_format/`.
