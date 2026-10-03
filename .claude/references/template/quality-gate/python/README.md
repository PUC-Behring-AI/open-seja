# Quality gate (Python)

A deterministic quality gate for Python projects. It is one stdlib-only script,
`gate.py`, that runs the checks below in a fixed order and exits with a code
that tells you which category failed. Agents and humans run the same command.

Run it from the project root (it reads `pyproject.toml` and writes
`quality-baseline.json` in the current directory):

```bash
python gate.py --init-baseline   # once: record the current state
python gate.py --fast            # default level
python gate.py --full            # --fast plus mutation testing
```

Python 3.11+ is needed to read `pyproject.toml` (`tomllib`); on older versions
install `tomli`. The thresholds in `[tool.seja-gate]` are the single source of
truth; no other file repeats them.

## What each stage checks

Stages run in this order and the gate stops at the first failing stage.

| Order | Stage | Tool | What it verifies | Exit |
|---|---|---|---|---|
| 1 | config | gate.py | pyproject, package, baseline, tools present, `diff_base` resolvable, coverage fresh | 1 |
| 2 | static | `ruff check`, `ruff format --check`, `pyright` | lint, formatting, types | 2 |
| 3 | tests | AST lint of tests, `pytest` (with branch coverage, 30 s per-test timeout) | no empty/assert-free tests; suite green | 3 |
| 4 | CRAP | `radon` + `coverage.json` | complexity and coverage per function (see below) | 4 |
| 5 | architecture | `lint-imports` | import contracts (only when contracts are configured) | 5 |
| 6 | mutation | `mutmut` (`--full` only) | surviving mutants in the touched functions | 6 |
| 7 | markers | gate.py | `skip`, `xfail`, `no cover`, `no mutate` markers do not grow without a reason | 7 |

The mutation stage runs last in time but keeps category 6, so the numbering is
by failure category, not by execution order.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | PASS |
| 1 | Config or tooling problem (no baseline, missing tools, stale coverage, unresolved `diff_base`, join misses, timeout) |
| 2 | Static analysis failed (ruff, pyright) |
| 3 | Tests failed or a test lint finding |
| 4 | CRAP ratchet violated |
| 5 | Import contract broken |
| 6 | Surviving mutants (`--full`) |
| 7 | Marker ratchet violated |

Code 1 always wins; otherwise the lowest failing category is returned.
`--json` prints a `version: 1` object on stdout with `status`
(`PASS|FAIL|ERROR`), `exit_code`, `stages` and `findings`. A copy is written as
`gate-<UTC timestamp>.json` to `--out-dir`, else `$SEJA_QUALITY_DIR`, else
`_output/quality/`. Findings with `severity: warning` never change the exit code.

## CRAP

```
CRAP = cc^2 * (1 - cov)^3 + cc
```

`cc` is the cyclomatic complexity from radon; `cov` is the function's coverage
(`(covered_lines + covered_branches) / (statements + branches)`, from
`coverage.json`, coverage >= 7.5). A function with no statements counts as
fully covered. Example: `cc=5, cov=0` gives 30.

Two numbers, two audiences:

- **30** is the classic human threshold (Savoia and Evans): above it a function
  is considered hard to change safely. It is the ceiling (`crap_max_abs`).
- **6-10** is the number for agents. An agent writes code fast and does not feel
  the cost of a tangled function, so the bar for code it touches is much
  tighter: a function touched in the diff must stay at or below
  `crap_max_touched`.

The ramp for `crap_max_touched` is **10 -> 8 -> 6**: start at 10 so the first
adoption is not a wall, lower it to 8 and then 6 as the code base is cleaned up.
Changing the value is a human edit to `pyproject.toml`.

Rules:

- A function touched by the diff (against `git merge-base HEAD <diff_base>`;
  untracked files count as fully touched), or one absent from the baseline,
  must have CRAP <= `crap_max_touched`.
- An untouched function must not get worse than its baseline.
- Nothing may newly cross the ceiling `crap_max_abs` (30). Legacy functions
  already above 30 in the baseline only produce an `over-ceiling` warning.

## Mutation testing and equivalent mutants

`--full` runs `mutmut` only on the touched functions (or on all functions of
the files given with `--files`) and fails on survivors in them, and when the
total of survivors exceeds the baseline.

Some mutants cannot be killed because they do not change behavior. Annotate the
line and state why, on the same line:

```python
x = compute()  # pragma: no mutate  # equivalent: <reason>
```

The marker ratchet counts markers by kind; a marker without a reason
(`reason=`, `reason:` or `equivalent:`) is "unjustified" and may not exceed the
baseline count.

## Baseline

`quality-baseline.json` records the per-function CRAP, the marker counts and the
surviving-mutant total. Commit it.

- `--init-baseline` writes it only when it does not exist (no-op otherwise).
- `--accept-baseline --yes` overwrites it. **Only a human moves the baseline.**
  Agents must not run it; without `--yes` the gate refuses. Use it deliberately,
  for example after a reviewed refactor, and commit the diff.

## Configuration

Copy the blocks from `pyproject-dev.example.toml` into `pyproject.toml`:

| Key (`[tool.seja-gate]`) | Default | Meaning |
|---|---|---|
| `package` | the single directory under `src/` | importable package to measure |
| `diff_base` | `origin/main` | ref used to decide which functions were touched |
| `crap_max_touched` | 10 | ceiling for touched or new functions (ramp 10 -> 8 -> 6) |
| `crap_max_abs` | 30 | absolute ceiling nothing may newly cross |
| `env_passthrough` | `[]` | secret-looking env vars the tools may still see |

The child processes run with `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`,
`CLAUDE_CODE_OAUTH_TOKEN` and any `*_API_KEY`, `*_TOKEN`, `*_SECRET` variable
removed, unless listed in `env_passthrough`.

`importlinter.example.toml` has three commented contracts to adapt (layers,
framework isolation, single owner of the vector store). If `[tool.importlinter]`
or `.importlinter` exists, stage 5 runs.

## Tool versions

The dev group pins major ranges: `coverage[toml]>=7.5,<8`, `radon>=6,<7`,
`mutmut>=3,<4`. The exact versions validated with this gate are not yet
recorded, because no pilot run has been done; `uv.lock` pins whatever you
install, so commit it.

## Cost

- `--fast`: target <= 90 s on a typical sub-project (not yet measured). Dominated
  by the test suite.
- `--full`: minutes to tens of minutes, proportional to the touched functions
  (mutmut timeout 3600 s per run). Run it before merging, not on every edit.

## Proposed amendment to the constitution (Q1)

Current Q1 text, in projects that have this principle:

> Sub-project code changes ship only after `uv run pytest` passes, with `ruff`
> and `pyright` clean.

Proposed:

> Sub-project code changes ship only after `pytest`, `ruff`, `pyright` and
> `gate --fast` (`python gate.py --fast`) are green, run from within that
> sub-project.

Amending the constitution requires explicit owner approval; this is a proposal
only.
