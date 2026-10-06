# Skill body length calibration baseline

Authoritative post-plan-000458 baseline for the `skill-body-length` plugin in
`check_docs.py`. Generated at plan-000458 step 3. Step 11 verification checks
against this table; future compression/expansion PRs should update it in step.

## Per-tier thresholds

| Tier | Body-line ceiling |
|---|---|
| light | 150 |
| standard | 300 |
| heavy | 500 |

Thresholds are calibrated against the plan-000451 post-compression baseline and
are NOT to be adjusted without a documented rationale -- calibration = adjust
the world, not the lint (see plan-000458 step 1).

## Per-skill baseline (post-plan-000458 step 3)

Body line count is the agent-facing body from the first heading after
`## Arguments` through EOF, as reported by
`python .claude/skills/critique/check_docs.py --plugins skill-body-length --verbose`.

| Skill | Tier | Body lines | Threshold | Delta | Status |
|---|---|---|---|---|---|
| check | heavy | 326 | 500 | -174 | PASS |
| communicate | standard | 104 | 300 | -196 | PASS (1 inlined-template WARN, step-11 follow-up candidate) |
| design | standard | 323 | 300 | +23 | WAIVER |
| document | standard | 149 | 300 | -151 | PASS (1 citation WARN, address via steps 8-9) |
| explain | standard | 259 | 300 | -41 | PASS |
| help | light | 71 | 150 | -79 | PASS |
| implement | heavy | 199 | 500 | -301 | PASS |
| mob | heavy | 96 | 500 | -404 | PASS (added with `/mob`) |
| onboard | standard | 129 | 300 | -171 | PASS |
| pending | light | 56 | 150 | -94 | PASS |
| plan | heavy | 423 | 500 | -77 | PASS |
| post-skill | standard | 216 | 300 | -84 | PASS |
| pre-skill | standard | 185 | 300 | -115 | PASS |
| qa-log | light | 55 | 150 | -95 | PASS (1 citation WARN, address via steps 8-9) |
| reflect | standard | 136 | 300 | -164 | PASS |
| research | standard | 114 | 300 | -186 | PASS |
| seja-setup | standard | 306 | 300 | +6 | WAIVER |

Total: 16 skills. Zero length-threshold WARNINGs (2 waivers, 14 PASS). The 4
remaining WARNINGs (1 inlined-template, 3 citations) are out of scope for step 3
and are addressed in later plan-000458 steps.

## Waiver registry

Waiver comments live in the body of the waived SKILL.md (below the first body
heading, per the plugin's detection rule). Suppressed signals: length threshold
only.

| Skill | Body lines | Tier | Waiver reason |
|---|---|---|---|
| design | 323 | standard | Project-setup flow is load-bearing; further compression risks losing execution fidelity; revisit after Common Steps mode factoring lands. |
| seja-setup | 306 | standard | State-dispatch across 5 mode variants (install/finalise/workspace/demo/upgrade) is load-bearing; re-tiered from `light` in plan-000458 step 3; revisit once the 5-mode surface can be factored via Common Steps. |

## Decisions logged in step 3

- `seja-setup`: re-tiered `metadata.context_budget` from `light` to `standard`.
  Rationale: `light` was inherited from before the skill grew its 5-mode
  dispatch surface; references list is empty (`references: []`) and no
  `eager_references`, so `standard` (not `heavy`) matches the reference-load
  rule in plan-000458 step 3. At 306 body lines the skill sits +6 over the
  `standard` threshold, covered by a waiver that documents the load-bearing
  dispatch surface and points at Common Steps factoring as the follow-up.
- `design`: waivered rather than compressed. The body is execution-dense
  (tables, per-mode step lists, registry columns) and a 25-line editorial pass
  would have risked losing fidelity. The waiver points at Common Steps mode
  factoring as the follow-up.

## Follow-ups surfaced but deferred

- `communicate/SKILL.md:60` carries a 22-line inlined code fence. Candidate for
  extraction to `.claude/references/template/`. Not in plan-000458 scope (no Common
  Steps factoring planned for `/communicate`). File a separate plan when the
  next compression sweep runs.
- 3 citation WARNs (`document`, `qa-log`, `seja-setup`) remain. These are
  addressed by the SKILL-rationale.md sibling pattern adopted in plan-000458
  steps 7-9.

## Re-measure after the default cycle (plan-000015 step 7, 2026-10-06)

Measured on `dev` after plans 000007-000014 (grill, specify, plan v2, test-first,
drift report) edited `plan`, `_internal/plan/standard`, `implement`, `reflect`,
`explain` and `_internal/explain/drift`. Same command as above. No limit was
raised and no new waiver was added; the tables above stay as the plan-000458
record.

| Skill | Tier | Body lines | Threshold | Delta | Status |
|---|---|---|---|---|---|
| communicate | standard | 104 | 300 | -196 | PASS |
| critique | heavy | 226 | 500 | -274 | PASS |
| design | standard | 109 | 300 | -191 | PASS (waiver no longer needed) |
| document | standard | 100 | 300 | -200 | PASS |
| explain | standard | 65 | 300 | -235 | PASS |
| help | light | 70 | 150 | -80 | PASS |
| implement | heavy | 254 | 500 | -246 | PASS |
| mob | heavy | 100 | 500 | -400 | PASS |
| onboard | standard | 129 | 300 | -171 | PASS |
| pending | light | 142 | 150 | -8 | PASS (95% of the tier; not touched by the cycle) |
| plan | heavy | 72 | 500 | -428 | PASS |
| post-skill | standard | 221 | 300 | -79 | PASS |
| pre-skill | standard | 79 | 300 | -221 | PASS |
| publish | light | 0 | 150 | -150 | PASS |
| qa-log | light | 55 | 150 | -95 | PASS |
| reflect | standard | 248 | 300 | -52 | PASS (83%) |
| research | standard | 143 | 300 | -157 | PASS |
| seja-setup | standard | 85 | 300 | -215 | PASS (waiver no longer needed) |

Not measured by the plugin (internal skills): `_internal/plan/standard/SKILL.md`
(141 lines in the file) and `_internal/explain/drift/SKILL.md` (156). The detail of
each phase lives in the normative references (`grill-phase.md`,
`specify-phase.md`, `plan-from-scenarios.md`, `implement-test-first.md`,
`drift-report.md`); the SKILL.md files keep one pointer line each. Order of the
edits: `extended-cycle-contract.md`, section "Emendas do item 9".

Follow-up: `pending` sits at 142/150 (95%) without any cycle change; the next
plan that touches it should move text to a reference first.
