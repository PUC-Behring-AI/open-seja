#!/usr/bin/env python3
# designer: After you approve the scenarios, /plan writes the plan. Before I
#   show it to you, I check that every step says which approved scenarios it
#   delivers, that no approved scenario is left without a step, and that the
#   scenarios did not change after you approved them. If a step changes
#   behavior and cites no scenario, or a scenario has no step, I say so and the
#   plan is not saved as ready. Old plans, and projects without scenarios, are
#   never blocked.
"""
check_plan_scenarios.py -- Plan v2 scenario coverage checker (PFS-001 to PFS-015).

Invocation: skill-invoked, user-cli, hook-ci
Lifecycle: active

Rules: .claude/references/general/plan-from-scenarios.md (PFS-NNN; CYC-005, CYC-018).
Reads the plan, `features/<slug>/scenarios.lock.json` and, by subprocess, the
output of `check_specify.py --feature <slug> --status --json` (coupled to the
CLI and the versioned lock, never to the internals of the other checkers).
Never writes a file. No LLM, no network, no clock.

| Rule    | What I check                                                          | Severity     |
|---------|-----------------------------------------------------------------------|--------------|
| PFS-001 | v1 or no version: not verified, exit 0; unknown version: exit 2        | fatal        |
| PFS-002 | v2 header: one `Specify:` (approved (rev N) or skipped -- reason),     | error        |
|         | `Feature:` required with approved, forbidden with skipped              |              |
| PFS-003 | approved plan: every step has `Scenarios:`                             | error        |
| PFS-004 | scenario key well formed, between backticks, same slug, no duplicate   | error        |
| PFS-005 | the key is in `index` of the lock                                      | error        |
| PFS-006 | non-N/A `Tests:` and no `Scenarios:` (info: N/A with a reason)         | error / info |
| PFS-007 | `N/A (reason)` with an empty, filler or too short reason               | error        |
| PFS-008 | the owner of a scenario needs a test (`Tests:` not N/A)                | error        |
| PFS-009 | an approved scenario no step cites                                     | error        |
| PFS-010 | one scenario, one owner step                                           | error        |
| PFS-011 | `check_specify.py --status` is `approved`                              | error        |
| PFS-012 | `Specify: approved (rev N)` matches `rev` of the lock                  | error        |
| PFS-013 | skipped plan: every step has `Tests: N/A` (or a justified N/A)         | error / info |
| PFS-014 | approved plan and no step cites a scenario (hint: skipped?)            | info         |
| PFS-015 | not a check: I never change the plan or the lock                       | --           |

Exit codes:
  0 = no error (infos do not fail, except with --strict); v1 and no-v2 scans.
  1 = at least one error (or an info with --strict).
  2 = usage error, unreadable file, unknown plan_format_version, unknown lock
      schema_version, or the scenario validator (check_specify.py) not found.
      Never a traceback. The no-argument scan is fail-closed: an unreadable
      v2 plan or an invalid lock aborts the whole scan with exit 2.

Usage
-----
    python .claude/skills/scripts/check_plan_scenarios.py                 # scan _output/plans/ (v2 plans only)
    python .claude/skills/scripts/check_plan_scenarios.py <plan.md> [--root <dir>] [--json] [--table] [--strict]
    python .claude/skills/scripts/check_plan_scenarios.py <plan.md> --status-cmd "python3 stub.py {root} {slug}"

CHECK_PLUGIN_MANIFEST:
  name: Plan Scenario Coverage
  stack:
    backend: [any]
    frontend: [any]
  scope: plans
  critical: false
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import NamedTuple

SCHEMA_VERSION = 1
LOCK_SCHEMA_VERSION = 1
LOCK_NAME = "scenarios.lock.json"
MIN_REASON_WORDS = 3
FILLER_REASONS = frozenset({"", "n/a", "na", "-", "--", "tbd", "todo", "...", "x", "none", "nenhum"})
STATUSES = ("missing", "draft", "approved", "stale")
VALIDATOR_MISSING = "validador de cenários não encontrado"

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
KEY_RE = re.compile(r"^([a-z0-9]+(?:-[a-z0-9]+)*)/([^/:]+\.feature)::(\S.*)$")
VERSION_RE = re.compile(r"^plan_format_version:\s*(\S+)$")
FEATURE_RE = re.compile(r"^Feature:\s*(.*)$")
SPECIFY_RE = re.compile(r"^Specify:\s*(.*)$")
APPROVED_RE = re.compile(r"^approved \(rev (\d+)\)$")
SKIPPED_RE = re.compile(r"^skipped -- (\S.*)$")
STEP_RE = re.compile(r"^###\s+Step\s+(\d+)\s*:\s*(.*)$")
FIELD_RE = re.compile(r"^\s*-\s*\*\*(Tests|Scenarios)(?::\*\*|\*\*:)\s*(.*?)\s*$")
NA_RE = re.compile(r"^N/A\b", re.IGNORECASE)
NA_REASON_RE = re.compile(r"^N/A\s*\((.*)\)\s*$", re.IGNORECASE | re.DOTALL)
TICKS_RE = re.compile(r"`([^`]*)`")
PLAN_FILE_RE = re.compile(r"^plan-\d{6}-.+\.md$")
CLOSED_TITLE_RE = re.compile(r"^#\s*(DONE|REVOKED|SUPERSEDED)\s*\|")

RULES = tuple(f"PFS-{n:03d}" for n in range(1, 16))
_SEVERITY_WORDS = {"fatal": "erro", "error": "erro", "info": "informação"}


class UsageError(Exception):
    """Exit 2: wrong usage, unreadable file, unknown version or schema, missing validator."""


class Finding(NamedTuple):
    rule: str
    severity: str
    file: str
    line: int
    message: str
    hint: str


class Step(NamedTuple):
    n: int
    title: str
    line: int
    tests: str | None
    tests_line: int
    scen: str | None
    scen_line: int


class Plan(NamedTuple):
    title: str
    version: str | None  # None when the header has no plan_format_version line
    version_line: int
    features: list[tuple[int, str]]
    specifies: list[tuple[int, str]]
    steps: list[Step]


class Report(NamedTuple):
    file: str
    version: int
    feature: str | None
    specify: str | None
    status: str | None
    findings: list[Finding]
    steps: list[dict]
    matrix: list[dict] | None
    unverified: bool


# ---------------------------------------------------------------------------
# Parsing (pure)
# ---------------------------------------------------------------------------


def _is_fence(line: str) -> bool:
    return line.lstrip().startswith("```")


def parse_header(text: str) -> Plan:
    """Header = the lines before the first `## ` section (PFS-001, PFS-002). Steps stay empty."""
    lines = text.splitlines()
    title = lines[0] if lines else ""
    version: str | None = None
    version_line = 1
    features: list[tuple[int, str]] = []
    specifies: list[tuple[int, str]] = []
    in_fence = False
    for number, raw in enumerate(lines[1:], start=2):
        if _is_fence(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if raw.startswith("## "):
            break
        line = raw.strip()
        if (m := VERSION_RE.match(line)) and version is None:
            version, version_line = m.group(1), number
        elif m := FEATURE_RE.match(line):
            features.append((number, m.group(1).strip()))
        elif m := SPECIFY_RE.match(line):
            specifies.append((number, m.group(1).strip()))
    return Plan(title, version, version_line, features, specifies, [])


def _steps_block(lines: list[str]) -> list[tuple[int, str]]:
    """(line number, text) of the lines inside `## Steps`, fences excluded."""
    block: list[tuple[int, str]] = []
    inside = False
    in_fence = False
    for number, raw in enumerate(lines, start=1):
        if _is_fence(raw):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if raw.startswith("## "):
            inside = raw.strip() == "## Steps"
            continue
        if inside:
            block.append((number, raw))
    return block


def parse_steps(text: str) -> list[Step]:
    steps: list[Step] = []
    current: dict | None = None

    def close() -> None:
        if current is not None:
            steps.append(Step(current["n"], current["title"], current["line"], current.get("Tests"),
                              current.get("Tests_line", 0), current.get("Scenarios"), current.get("Scenarios_line", 0)))

    for number, raw in _steps_block(text.splitlines()):
        if m := STEP_RE.match(raw):
            close()
            current = {"n": int(m.group(1)), "title": m.group(2).strip(), "line": number}
        elif current is not None and (f := FIELD_RE.match(raw)) and f.group(1) not in current:
            current[f.group(1)] = f.group(2)
            current[f.group(1) + "_line"] = number
    close()
    return steps


def parse_plan(text: str) -> Plan:
    head = parse_header(text)
    return head._replace(steps=parse_steps(text))


def plan_version(plan: Plan) -> int | None:
    """1 (also when absent) or 2; None for an unknown value."""
    if plan.version is None or plan.version == "1":
        return 1
    return 2 if plan.version == "2" else None


def is_na(value: str | None) -> bool:
    return value is None or bool(NA_RE.match(value.strip())) or not value.strip()


def na_reason(value: str) -> str:
    m = NA_REASON_RE.match(value.strip())
    return m.group(1).strip() if m else ""


def reason_ok(reason: str) -> bool:
    plain = reason.strip().lower()
    return plain not in FILLER_REASONS and len(plain.split()) >= MIN_REASON_WORDS


def parse_scenarios(value: str) -> tuple[list[str], str]:
    """Backtick tokens of a Scenarios value and the text left over outside them."""
    tokens = TICKS_RE.findall(value)
    left = re.sub(r"[,\s]", "", TICKS_RE.sub("", value))
    return tokens, left


# ---------------------------------------------------------------------------
# Rules (pure)
# ---------------------------------------------------------------------------


def _f(rule: str, severity: str, file: str, line: int, message: str, hint: str = "") -> Finding:
    return Finding(rule, severity, file, line, message, hint)


def _check_header(plan: Plan, file: str, root: Path) -> tuple[list[Finding], str | None, str | None]:
    """PFS-002. Returns (findings, mode, slug); mode is None when the header cannot be trusted."""
    out: list[Finding] = []
    if not plan.specifies:
        hint = "Escreva `Specify: approved (rev N)` ou `Specify: skipped -- <motivo>`."
        return [_f("PFS-002", "error", file, 1, "O cabeçalho não diz `Specify:`.", hint)], None, None
    (sline, svalue), extra = plan.specifies[0], plan.specifies[1:]
    out += [_f("PFS-002", "error", file, ln, "O cabeçalho tem `Specify:` mais de uma vez.", "Deixe uma só linha.")
            for ln, _ in extra]
    approved, skipped = APPROVED_RE.match(svalue), SKIPPED_RE.match(svalue)
    if not approved and not skipped:
        hint = "Use `approved (rev N)` ou `skipped -- <motivo>`, com um motivo."
        return out + [_f("PFS-002", "error", file, sline, "O valor de `Specify:` não segue o formato.", hint)], None, None
    if skipped:
        out += [_f("PFS-002", "error", file, ln, "Um plano com `Specify: skipped` não tem `Feature:`.",
                   "Tire a linha `Feature:` ou rode a specify.") for ln, _ in plan.features]
        return out, "skipped", None
    return _check_feature(plan, file, root, out)


def _check_feature(plan: Plan, file: str, root: Path, out: list[Finding]) -> tuple[list[Finding], str | None, str | None]:
    sline = plan.specifies[0][0]
    if not plan.features:
        hint = "Escreva `Feature: <slug>` com o nome da pasta em features/."
        return out + [_f("PFS-002", "error", file, sline, "Com `Specify: approved` falta a linha `Feature:`.", hint)], None, None
    (fline, slug), extra = plan.features[0], plan.features[1:]
    out += [_f("PFS-002", "error", file, ln, "O cabeçalho tem `Feature:` mais de uma vez.", "Um plano, uma feature.")
            for ln, _ in extra]
    if not SLUG_RE.match(slug):
        return out + [_f("PFS-002", "error", file, fline, "O nome em `Feature:` não é um slug.",
                         "Use letras minúsculas, números e hífen.")], None, None
    if not (root / "features" / slug).is_dir():
        return out + [_f("PFS-002", "error", file, fline, f"Não existe a pasta features/{slug}/.",
                         "Rode /plan --grill e a specify antes do plano.")], None, None
    return out, "approved", slug


def _step_keys(step: Step, slug: str, file: str) -> tuple[list[str], list[Finding]]:
    """Well-formed, unique keys of a step (PFS-004) and the findings for the rest."""
    if step.scen is None or is_na(step.scen):
        return [], []
    tokens, left = parse_scenarios(step.scen)
    out: list[Finding] = []
    tag_hint = "Use o nome do cenário entre crases, não a tag @REQ-."
    key_hint = "Escreva `<slug>/<arquivo>.feature::<nome do cenário>` entre crases."
    if not tokens:
        hint = tag_hint if "@REQ-" in step.scen else key_hint
        return [], [_f("PFS-004", "error", file, step.scen_line, f"O passo {step.n} não cita o cenário entre crases.", hint)]
    if left:
        hint = tag_hint if "@REQ-" in left else key_hint
        out.append(_f("PFS-004", "error", file, step.scen_line, f"O passo {step.n} tem texto solto na lista de cenários.", hint))
    keys: list[str] = []
    for token in tokens:
        m = KEY_RE.match(token)
        if token in keys:
            out.append(_f("PFS-004", "error", file, step.scen_line, f"O passo {step.n} cita o cenário \"{token}\" duas vezes.",
                          "Deixe uma citação só."))
        elif not m or m.group(1) != slug:
            out.append(_f("PFS-004", "error", file, step.scen_line, f"A chave \"{token}\" do passo {step.n} não está bem formada.",
                          f"A chave começa com o slug `{slug}/`. {key_hint}"))
        else:
            keys.append(token)
    return keys, out


def _check_na_reason(step: Step, file: str) -> list[Finding]:
    """PFS-007."""
    if step.scen is None or not NA_RE.match(step.scen.strip()):
        return []
    if reason_ok(na_reason(step.scen)):
        return []
    return [_f("PFS-007", "error", file, step.scen_line, f"O passo {step.n} diz N/A sem um motivo que se leia.",
               "Escreva `N/A (<motivo>)` com pelo menos 3 palavras: a que cenário o passo serve.")]


def _check_step_common(step: Step, file: str, mode: str, scen_na: bool) -> list[Finding]:
    """PFS-003, PFS-006, PFS-007, PFS-013 for one step (mode: approved or skipped)."""
    out = _check_na_reason(step, file)
    tests_na = is_na(step.tests)
    if step.scen is None:
        if mode == "approved" and tests_na:
            out.append(_f("PFS-003", "error", file, step.line, f"O passo {step.n} não tem `Scenarios:`.",
                          "Cite os cenários que o passo entrega ou escreva `N/A (<motivo>)`."))
        elif not tests_na:
            out.append(_pfs_no_scenario(step, file, mode))
    elif scen_na and not tests_na and reason_ok(na_reason(step.scen)):
        rule = "PFS-006" if mode == "approved" else "PFS-013"
        out.append(_f(rule, "info", file, step.scen_line,
                      f"O passo {step.n} tem teste e diz que não entrega cenário. Confira o motivo.",
                      "Isto passa, e a ferramenta não julga se o passo muda comportamento."))
    return out


def _pfs_no_scenario(step: Step, file: str, mode: str) -> Finding:
    if mode == "skipped":
        return _f("PFS-013", "error", file, step.tests_line,
                  f"A tarefa muda comportamento no passo {step.n}, mas a specify foi pulada.",
                  "Rode a specify ou justifique o `Tests: N/A`.")
    return _f("PFS-006", "error", file, step.line, f"O passo {step.n} muda comportamento e não cita cenário.",
              "Volte à specify para criar o cenário ou troque o `Tests:` por N/A com justificativa.")


def _cites(steps: list[Step], slug: str, file: str) -> tuple[dict[int, list[str]], list[Finding]]:
    cited: dict[int, list[str]] = {}
    out: list[Finding] = []
    for step in steps:
        keys, found = _step_keys(step, slug, file)
        cited[step.n] = keys
        out += found
    return cited, out


def _check_lock_keys(steps: list[Step], cited: dict[int, list[str]], index: list[str], file: str) -> list[Finding]:
    """PFS-005: a well-formed key that is not in the lock."""
    known = set(index)
    out: list[Finding] = []
    for step in steps:
        for key in cited[step.n]:
            if key not in known:
                out.append(_f("PFS-005", "error", file, step.scen_line, f"O passo {step.n} cita um cenário que não existe: \"{key}\".",
                              "O cenário mudou de nome ou saiu. Veja Mudanças do intent.md."))
    return out


def _check_owners(steps: list[Step], cited: dict[int, list[str]], file: str) -> list[Finding]:
    """PFS-008 (owner needs a test) and PFS-010 (one owner)."""
    out: list[Finding] = []
    owners: dict[str, list[Step]] = {}
    for step in steps:
        if cited[step.n] and is_na(step.tests):
            out.append(_f("PFS-008", "error", file, step.scen_line, f"O passo {step.n} cita cenário e não tem teste.",
                          "O passo dono do cenário precisa de `Tests:`; troque o N/A."))
        for key in cited[step.n]:
            owners.setdefault(key, []).append(step)
    for key, found in owners.items():
        if len(found) > 1:
            nums = " e ".join(str(s.n) for s in found)
            out.append(_f("PFS-010", "error", file, found[-1].scen_line, f"O cenário \"{key}\" tem mais de um passo dono: {nums}.",
                          "Deixe um passo dono; os outros usam `N/A (<motivo>)`."))
    return out


def _check_coverage(index: list[str], cited: dict[int, list[str]], file: str, feature_line: int, specify_line: int) -> list[Finding]:
    """PFS-009 and PFS-014."""
    seen = {key for keys in cited.values() for key in keys}
    out = [_f("PFS-009", "error", file, feature_line, f"Nenhum passo entrega o cenário \"{key}\".",
              "Dê o cenário a um passo ou volte à specify.") for key in index if key not in seen]
    if not any(cited.values()):
        out.append(_f("PFS-014", "info", file, specify_line, "Nenhum passo cita cenário.",
                      "Se a feature nunca teve cenário, o plano é `Specify: skipped -- <motivo>`."))
    return out


def _check_state(plan: Plan, lock: dict | None, status: dict, file: str) -> list[Finding]:
    """PFS-011 and PFS-012."""
    sline = plan.specifies[0][0]
    out: list[Finding] = []
    if status.get("status") != "approved":
        reasons = status.get("reasons") or []
        extra = f" (estado: {status.get('status')}{'; ' + ', '.join(reasons) if reasons else ''})"
        out.append(_f("PFS-011", "error", file, sline, "Os cenários estão desatualizados: refaça a specify." + extra,
                      "Rode /plan --specify e peça nova aprovação antes do plano."))
    m = APPROVED_RE.match(plan.specifies[0][1])
    if lock is not None and m and int(m.group(1)) != lock.get("rev"):
        out.append(_f("PFS-012", "error", file, sline,
                      f"O plano diz rev {m.group(1)} e a última aprovação é rev {lock.get('rev')}.",
                      "O plano é velho em relação à aprovação. Atualize o plano."))
    return out


def _matrix(index: list[str], cited: dict[int, list[str]]) -> list[dict]:
    return [{"scenario": key, "steps": sorted(n for n, keys in cited.items() if key in keys)} for key in index]


def _step_rows(plan: Plan, cited: dict[int, list[str]]) -> list[dict]:
    return [{"n": s.n, "title": s.title, "line": s.line, "tests": s.tests or "", "tests_na": is_na(s.tests),
             "scenarios": cited.get(s.n, []), "scenarios_na": s.scen is not None and bool(NA_RE.match(s.scen.strip())),
             "scenarios_reason": na_reason(s.scen) if s.scen and NA_RE.match(s.scen.strip()) else ""}
            for s in sorted(plan.steps, key=lambda s: s.n)]


def check_plan(plan: Plan, lock: dict | None, status: dict | None, *, file: str = "plan.md",
               root: Path = Path(".")) -> Report:
    """Apply PFS-001 to PFS-014. `lock` and `status` are only used with Specify: approved."""
    version = plan_version(plan)
    if version is None:
        finding = _f("PFS-001", "fatal", file, plan.version_line, f"Não conheço a versão do plano ({plan.version}).",
                     "Use `plan_format_version: 1` ou `2`.")
        return Report(file, 0, None, None, None, [finding], [], None, False)
    if version == 1:
        return Report(file, 1, None, None, None, [], [], None, True)
    findings, mode, slug = _check_header(plan, file, root)
    specify = plan.specifies[0][1] if plan.specifies else None
    if mode is None:
        return _finish(file, slug, specify, None, findings, plan, {}, None)
    if mode == "skipped":
        cited: dict[int, list[str]] = {s.n: [] for s in plan.steps}
        for s in plan.steps:
            findings += _check_skipped_step(s, file)
        return _finish(file, None, specify, None, findings, plan, cited, None)
    assert slug is not None  # approved always has a slug
    return _approved(plan, lock, status, file, slug, specify, findings)


def _check_skipped_step(step: Step, file: str) -> list[Finding]:
    """PFS-007 and PFS-013 for a plan with Specify: skipped (no lock, no feature)."""
    out = _check_na_reason(step, file)
    if step.scen is not None and not NA_RE.match(step.scen.strip()):
        return out + [_f("PFS-013", "error", file, step.scen_line, f"O passo {step.n} cita cenário, mas a specify foi pulada.",
                         "Sem cenário aprovado não há o que citar. Rode a specify ou use `N/A (<motivo>)`.")]
    scen_na = step.scen is not None
    return out + [f for f in _check_step_common(step, file, "skipped", scen_na) if f.rule != "PFS-007"]


def _approved(plan: Plan, lock: dict | None, status: dict | None, file: str, slug: str, specify: str | None,
              findings: list[Finding]) -> Report:
    sline, fline = plan.specifies[0][0], plan.features[0][0]
    status = status or {"status": None}
    index = list(lock.get("index", [])) if lock else []
    cited, found = _cites(plan.steps, slug, file)
    findings += found
    for step in plan.steps:
        findings += _check_step_common(step, file, "approved", step.scen is not None and bool(NA_RE.match(step.scen.strip())))
    findings += _check_owners(plan.steps, cited, file)
    findings += _check_state(plan, lock, status, file)
    if lock is not None:
        if any("`" in key for key in index):
            findings.append(_f("PFS-004", "error", file, fline, "Um cenário aprovado tem crase no nome e não dá para citá-lo.",
                               "Renomeie o cenário na specify, sem crase."))
        findings += _check_lock_keys(plan.steps, cited, index, file)
        findings += _check_coverage(index, cited, file, fline, sline)
    matrix = _matrix(index, cited) if lock is not None else None
    return _finish(file, slug, specify, status.get("status"), findings, plan, cited, matrix)


def _finish(file: str, slug: str | None, specify: str | None, status: str | None, findings: list[Finding],
            plan: Plan, cited: dict[int, list[str]], matrix: list[dict] | None) -> Report:
    ordered = sorted(findings, key=lambda f: (f.line, f.rule, f.message))
    return Report(file, 2, slug, specify, status, ordered, _step_rows(plan, cited), matrix, False)


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        raise UsageError(f"não consegui ler {path.as_posix()}: {exc.__class__.__name__}") from None


def load_lock(root: Path, slug: str) -> dict | None:
    path = root / "features" / slug / LOCK_NAME
    if not path.is_file():
        return None
    try:
        lock = json.loads(read_text(path))
    except json.JSONDecodeError:
        raise UsageError(f"{path.as_posix()} não é um JSON válido") from None
    if not isinstance(lock, dict) or lock.get("schema_version") != LOCK_SCHEMA_VERSION:
        raise UsageError(f"{path.as_posix()} tem schema_version desconhecido")
    return lock


def _status_command(root: Path, slug: str, status_cmd: str | None) -> list[str]:
    if status_cmd:
        return [part.replace("{root}", str(root)).replace("{slug}", slug) for part in shlex.split(status_cmd)]
    script = Path(__file__).resolve().parent / "check_specify.py"
    if not script.is_file():
        raise UsageError(f"{VALIDATOR_MISSING}: {script.as_posix()}")
    return [sys.executable, str(script), str(root), "--feature", slug, "--status", "--json"]


def scenario_status(root: Path, slug: str, status_cmd: str | None = None) -> dict:
    """PFS-011: run `check_specify.py --status --json` as a subprocess and read its JSON."""
    cmd = _status_command(root, slug, status_cmd)
    try:
        done = subprocess.run(cmd, capture_output=True, text=True, timeout=120, check=False)
    except (FileNotFoundError, PermissionError):
        raise UsageError(f"{VALIDATOR_MISSING}: {cmd[0]}") from None
    except subprocess.TimeoutExpired:
        raise UsageError("o validador de cenários demorou demais") from None
    if done.returncode != 0:
        raise UsageError(f"o validador de cenários falhou (saída {done.returncode}): {done.stderr.strip()[:200]}")
    try:
        data = json.loads(done.stdout)
    except json.JSONDecodeError:
        raise UsageError("o validador de cenários não devolveu JSON") from None
    if not isinstance(data, dict) or data.get("schema_version") != 1 or data.get("status") not in STATUSES:
        raise UsageError("o validador de cenários devolveu um formato desconhecido")
    return data


StatusFn = Callable[[Path, str], dict]


def check_text(text: str, root: Path, *, file: str = "plan.md", status_fn: StatusFn | None = None,
               status_cmd: str | None = None) -> Report:
    """Parse and check a plan. The scenario status is only asked for when the plan is v2 approved."""
    plan = parse_plan(text)
    version = plan_version(plan)
    if version != 2:
        return check_plan(plan, None, None, file=file, root=root)
    _, mode, slug = _check_header(plan, file, root)
    if mode != "approved" or slug is None:
        return check_plan(plan, None, None, file=file, root=root)
    status = (status_fn or (lambda r, s: scenario_status(r, s, status_cmd)))(root, slug)
    return check_plan(plan, load_lock(root, slug), status, file=file, root=root)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def blocking(report: Report, strict: bool) -> bool:
    return any(f.severity in ("fatal", "error") or (strict and f.severity == "info") for f in report.findings)


def exit_code(report: Report, strict: bool) -> int:
    if any(f.severity == "fatal" for f in report.findings):
        return 2
    return 1 if blocking(report, strict) else 0


def table(report: Report) -> str:
    rows = report.matrix or []
    lines = ["## Cobertura de cenários", "", "| Cenário | Passo |", "|---|---|"]
    for row in rows:
        steps = ", ".join(str(n) for n in row["steps"]) or "(nenhum)"
        lines.append(f"| {row['scenario']} | {steps} |")
    return "\n".join(lines) + "\n"


def as_json(report: Report) -> dict:
    return {"schema_version": SCHEMA_VERSION, "plan": report.file, "version": report.version, "feature": report.feature,
            "specify": report.specify, "status": report.status, "unverified": report.unverified,
            "findings": [f._asdict() for f in report.findings], "steps": report.steps, "matrix": report.matrix}


def print_report(report: Report) -> None:
    if report.unverified:
        print(f"check_plan_scenarios {report.file}: v1: não verificado")
        return
    for f in report.findings:
        hint = f" Dica: {f.hint}" if f.hint else ""
        print(f"{f.file}:{f.line}: {f.rule} {_SEVERITY_WORDS[f.severity]}: {f.message}{hint}")
    errors = sum(1 for f in report.findings if f.severity in ("fatal", "error"))
    infos = sum(1 for f in report.findings if f.severity == "info")
    status = f"; estado dos cenários: {report.status}" if report.status else ""
    print(f"check_plan_scenarios {report.file}: {errors} {'erro' if errors == 1 else 'erros'}, "
          f"{infos} {'informação' if infos == 1 else 'informações'}{status}")


def _is_open_plan(path: Path, text: str) -> bool:
    first = text.splitlines()[0] if text else ""
    return PLAN_FILE_RE.match(path.name) is not None and not path.name.endswith("-progress.md") \
        and "-qa-" not in path.name and not CLOSED_TITLE_RE.match(first)


def _scan(root: Path, args: argparse.Namespace) -> int:
    plans_dir = root / "_output" / "plans"
    files = sorted(plans_dir.glob("plan-*.md")) if plans_dir.is_dir() else []
    checked = failed = 0
    reports: list[Report] = []
    for path in files:
        text = read_text(path)
        if not _is_open_plan(path, text) or plan_version(parse_header(text)) != 2:
            continue
        report = check_text(text, root, file=path.relative_to(root).as_posix(), status_cmd=args.status_cmd)
        checked += 1
        failed += 1 if blocking(report, args.strict) else 0
        reports.append(report)
        if not args.json:
            print_report(report)
    if args.json:
        print(json.dumps({"schema_version": SCHEMA_VERSION, "plans": [as_json(r) for r in reports]}, ensure_ascii=False, indent=2))
    elif not checked:
        print("check_plan_scenarios: nenhum plano v2 em _output/plans/; nada a verificar.")
    return 1 if failed else 0


def _run(args: argparse.Namespace) -> int:
    root = Path(args.root)
    if not root.is_dir():
        raise UsageError(f"pasta não encontrada: {root}")
    if args.plan is None:
        if args.table:
            raise UsageError("--table pede um plano")
        return _scan(root, args)
    path = Path(args.plan)
    report = check_text(read_text(path), root, file=path.as_posix(), status_cmd=args.status_cmd)
    if args.json:
        print(json.dumps(as_json(report), ensure_ascii=False, indent=2))
    elif args.table:
        print(table(report), end="")
    else:
        print_report(report)
    return exit_code(report, args.strict)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan v2 scenario coverage checker (PFS-001 to PFS-015).")
    parser.add_argument("plan", nargs="?", help="plan file; omit to scan _output/plans/ for v2 plans")
    parser.add_argument("--root", default=".", help="project root with features/ (default: current directory)")
    parser.add_argument("--json", action="store_true", help="one JSON object with schema_version")
    parser.add_argument("--table", action="store_true", help="print the `## Cobertura de cenários` table")
    parser.add_argument("--strict", action="store_true", help="infos also fail (exit 1)")
    parser.add_argument("--status-cmd", dest="status_cmd",
                        help="command that prints the check_specify --status --json output; {root} and {slug} are replaced")
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except UsageError as exc:
        print(f"check_plan_scenarios: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 -- never a raw traceback for the user
        print(f"check_plan_scenarios: erro interno ({type(exc).__name__}): {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
