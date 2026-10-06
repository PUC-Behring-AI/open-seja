#!/usr/bin/env python3
# designer: When I build a step from your approved scenarios, I use these checks so that
#   every move is a tool's answer and not my sentence: the test failed for the right
#   reason, nobody touched the frozen tests, each role stayed in its lane, the quality
#   baseline did not move, and what was built is recorded where the drift report reads it.
"""
build_checks -- deterministic checks of the test-first branch of /implement (ITF-001..025).

Invocation: skill-invoked (/implement), agent-invoked
Lifecycle: active

Rules: .claude/references/general/implement-test-first.md. Standard library only; no LLM, no
network, no clock outside --at. Pure functions (red_check, green_check, check_skeleton,
check_scope, uncovered, baseline_state, crap_findings, record, next_phase, route, export_files,
demo_text) are separated from the CLI and the I/O.

Exit codes: 0 ok, 1 finding (or refusal), 2 usage error, unreadable or missing input.

Usage:
    python3 .claude/skills/scripts/build_checks.py route <plan.md> [--pipeline] [--json]
    python3 .claude/skills/scripts/build_checks.py install-plugin <project>
    python3 .claude/skills/scripts/build_checks.py skeleton <file.py>...
    python3 .claude/skills/scripts/build_checks.py red-check (--report <json> | --cucumber <json> [--junit <xml>])
        --owned <key>... [--root <dir>] [--files <src>...] [--coverage <json>] [--baseline <json>]
        [--skeleton <file>...] [--at <UTC>] [--json]
    python3 .claude/skills/scripts/build_checks.py green-check --report <json> --owned <key>... [--json]
    python3 .claude/skills/scripts/build_checks.py freeze --root <dir> (--write <snap.json> <file>... | --check <snap.json>)
    python3 .claude/skills/scripts/build_checks.py scope --root <dir> --role <tester|coder|cleaner|hardener>
        --base <rev> [--frozen <snap.json>] [--json]
    python3 .claude/skills/scripts/build_checks.py crap --radon <json> --coverage <json> --files <src>... [--target 8]
    python3 .claude/skills/scripts/build_checks.py uncovered --root <dir> --base <rev> --coverage <json> [--final]
    python3 .claude/skills/scripts/build_checks.py baseline --root <dir> --base <rev> [--file quality-baseline.json]
    python3 .claude/skills/scripts/build_checks.py record --root <dir> --feature <slug> --step <N> --from <json>
        --at <UTC> [--plan plan-<id>]
    python3 .claude/skills/scripts/build_checks.py status --root <dir> --feature <slug> --step <N> [--pipeline]
    python3 .claude/skills/scripts/build_checks.py export --root <dir> --feature <slug> [--cucumber <json>]
    python3 .claude/skills/scripts/build_checks.py demo --root <dir> --feature <slug> [--questions <json>]
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_plan_scenarios as cps

# the citizen register's technical-token list
from check_specify import QUOTED, TECH_TOKENS

SCHEMA_VERSION = 1
CRAP_TARGET_TOUCHED = 8.0
CRAP_TARGET_FLOOR = 6.0
PIPELINE_MAX_TRIES = 3
PIPELINE_MAX_INVOCATIONS = 10
PRIORITY = ("error", "failed", "xpassed", "skipped", "xfailed", "passed")  # worst first
CATEGORY = {0: "PASS", 1: "CONFIG", 2: "STATIC", 3: "TESTS", 4: "CRAP", 5: "ARCH", 6: "MUTATION", 7: "MARKERS"}
DRM_RESULT = {"xfailed": "xfail", "xpassed": "xfail", "missing": "absent"}  # runner names -> DRM-006 test_result
REFUSAL_V1 = "`--pipeline` é do plano v2; este plano roda como antes."
ROLES = ("tester", "coder", "cleaner", "hardener")
PLUGIN_SOURCE = (Path(__file__).resolve().parents[2] / "references" / "template" / "bdd" / "python"
                 / "scenario_report.py.example")
PLUGIN_LINE = 'pytest_plugins = ["scenario_report"]'
PLUGIN_STAMP = ".scenario_report.sha256"
PRAGMA_RE = re.compile(r"#\s*pragma:\s*no mutate\s+#\s*equivalent:\s*\S")
KEYWORD_TYPES = {
    "given": "given", "dado": "given", "dada": "given", "dados": "given", "dadas": "given",
    "when": "when", "quando": "when",
    "then": "then", "então": "then", "entao": "then",
    "and": None, "but": None, "e": None, "mas": None, "*": None,
}
TYPE_WORD = {"given": "Dado", "when": "Quando", "then": "Então", None: "algum passo"}
KIND_WORD = {"given": "Dado", "when": "Quando", "then": "Então", "and": "E", "but": "Mas", "star": "*"}

_LEGACY = ["implement", "write-tests", "verify", "gate-fast", "note", "commit"]
_TDD = ["test-red", "implement-green", "verify", "gate-fast", "note", "commit"]
_TEST_FIRST_HEAD = ["pre", "red", "red-check", "freeze", "record-red", "green", "scope", "freeze-check",
                    "green-check", "gate-fast"]
_TEST_FIRST_TAIL = ["record", "note", "commit"]
_V2_END = ["full", "uncovered", "record-feature", "export", "demo", "freeze-m1", "quality-gate", "done"]


class BuildError(Exception):
    """Exit 2: usage error, unreadable or missing input."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _f(rule: str, severity: str, message: str, hint: str = "", *, scenario: str | None = None,
       file: str | None = None, line: int | None = None) -> dict:
    return {"rule": rule, "severity": severity, "scenario": scenario, "file": file, "line": line,
            "message": message, "hint": hint}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_text(path: Path) -> str:
    try:
        return Path(path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as err:
        raise BuildError(f"não consegui ler {path}: {err.__class__.__name__}") from err


def read_json(path: Path):
    text = read_text(path)
    try:
        return json.loads(text)
    except ValueError as err:
        raise BuildError(f"{path} não é JSON válido") from err


def dump_json(data) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _norm(path: str) -> str:
    p = str(path).replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def _errors(findings: list[dict]) -> list[dict]:
    return [f for f in findings if f["severity"] == "error"]


def _key_from_uri(uri: str, name: str) -> str:
    parts = [p for p in _norm(uri).split("/") if p]
    slug = parts[-2] if len(parts) >= 2 else ""
    return f"{slug}/{parts[-1] if parts else ''}::{name}"


# ---------------------------------------------------------------------------
# ITF-004 skeleton
# ---------------------------------------------------------------------------


def _neutral(stmt: ast.stmt) -> bool:
    if isinstance(stmt, ast.Pass):
        return True
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
        return True  # docstring or `...`
    if isinstance(stmt, ast.Return):
        value = stmt.value
        if value is None or isinstance(value, ast.Constant):
            return True
        return isinstance(value, (ast.List, ast.Dict, ast.Tuple, ast.Set)) and not _children(value)
    if isinstance(stmt, ast.Raise) and stmt.cause is None:
        exc = stmt.exc
        if isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
            return True
        if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name) and exc.func.id == "NotImplementedError":
            return all(isinstance(a, ast.Constant) for a in exc.args) and not exc.keywords
    return False


def _children(node: ast.AST) -> list:
    if isinstance(node, ast.Dict):
        return list(node.keys) + list(node.values)
    return list(getattr(node, "elts", []))


def check_skeleton_source(text: str, file: str) -> list[dict]:
    try:
        tree = ast.parse(text)
    except SyntaxError as err:
        return [_f("ITF-004", "error", f"Não consegui ler {file}: erro de sintaxe.", "Corrija a sintaxe do esqueleto.",
                   file=file, line=err.lineno)]
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for stmt in node.body:
                if not _neutral(stmt):
                    findings.append(_f("ITF-004", "error", f"A função {node.name} tem lógica no vermelho.",
                                       "No vermelho o corpo é só pass, ..., docstring, return de literal ou "
                                       "raise NotImplementedError.", file=file, line=stmt.lineno))
    return sorted(findings, key=lambda f: (f["file"], f["line"]))


def check_skeleton(paths) -> list[dict]:
    """ITF-004 over the files that exist (a code file the Tester did not create yet has nothing to check)."""
    findings: list[dict] = []
    for path in paths:
        if not Path(path).is_file():
            continue
        findings.extend(check_skeleton_source(read_text(Path(path)), _norm(str(path))))
    return findings


# ---------------------------------------------------------------------------
# ITF-005 red-check (R1..R8), ITF-006 red record
# ---------------------------------------------------------------------------

_R1_HINTS = {
    "error": "O teste não chegou à asserção: corrija o import, a fixture ou a sintaxe e rode de novo.",
    "undefined": "Falta a definição de um passo: escreva a definição do passo e rode de novo.",
    "passed": "O teste já passa sem o código: ou o teste não afirma o comportamento, ou outro step já o entregou.",
    "skipped": "O teste está desligado: tire o skip; skip não conta como vermelho.",
    "xfailed": "O teste está marcado como xfail: tire a marca; xfail não conta como vermelho.",
    "xpassed": "O teste está marcado como xfail: tire a marca; xfail não conta como vermelho.",
    "missing": "O cenário não apareceu no relatório: confira a chave e a coleta do teste.",
}


def _is_const_fail(stmt: ast.stmt) -> bool:
    if isinstance(stmt, ast.Assert):
        test = stmt.test
        if isinstance(test, ast.Constant):
            return not test.value
        if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not) and isinstance(test.operand, ast.Constant):
            return bool(test.operand.value)
        return False
    if isinstance(stmt, ast.Raise):
        exc = stmt.exc
        name = exc.func if isinstance(exc, ast.Call) else exc
        return isinstance(name, ast.Name) and name.id == "AssertionError"
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
        func = stmt.value.func
        return isinstance(func, ast.Attribute) and func.attr == "fail" and \
            isinstance(func.value, ast.Name) and func.value.id == "pytest"
    return False


def constant_assertion(root: Path, step_func: dict) -> bool | None:
    """True when the step function body fails unconditionally (R4); None when it cannot be read."""
    try:
        tree = ast.parse(read_text(Path(root) / step_func["file"]))
    except (BuildError, SyntaxError, KeyError):
        return None
    best = None
    for node in ast.walk(tree):
        target = step_func.get("line", 0)
        if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == step_func.get("name")
                and (best is None or abs(node.lineno - target) < abs(best.lineno - target))):
            best = node
    if best is None:
        return None
    return any(_is_const_fail(stmt) for stmt in best.body)


def _body_lines(text: str) -> set[int]:
    lines: set[int] = set()
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str) and len(body) > 1:
                body = body[1:]
            for stmt in body:
                lines.update(range(stmt.lineno, (stmt.end_lineno or stmt.lineno) + 1))
    return lines


def _coverage_file(coverage: dict, rel: str) -> dict | None:
    files = coverage.get("files") or {}
    rel = _norm(rel)
    for name, data in files.items():
        name = _norm(name)
        if name == rel or name.endswith("/" + rel):
            return data
    return None


def _exercised(root: Path, source_files, coverage: dict) -> bool:
    for rel in source_files:
        data = _coverage_file(coverage, rel)
        if not data:
            continue
        try:
            body = _body_lines(read_text(Path(root) / rel))
        except (BuildError, SyntaxError):
            continue
        if body & set(data.get("executed_lines") or []):
            return True
    return False


def _row_ok(row: dict) -> bool:
    return row.get("outcome") == "failed" and row.get("exception") == "AssertionError" and \
        row.get("failing_step_type") == "then"


def _check_plain(key: str, rec: dict, root: Path | None, findings: list[dict]) -> None:
    outcome = rec.get("outcome")
    if outcome != "failed":
        kind = "undefined" if rec.get("undefined") else outcome
        findings.append(_f("R1", "error", f"O cenário {key} não ficou vermelho: o resultado foi {kind}.",
                           _R1_HINTS.get(kind, _R1_HINTS["error"]), scenario=key))
        return
    if rec.get("exception") != "AssertionError":
        findings.append(_f("R2", "error", f"O cenário {key} falhou por {rec.get('exception')}, não por asserção.",
                           "Corrija o erro até a falha ser a asserção do cenário.", scenario=key))
    if rec.get("failing_step_type") != "then":
        word = TYPE_WORD.get(rec.get("failing_step_type"), "algum passo")
        findings.append(_f("R3", "error", f"O cenário {key} falhou no passo {word}, não no Então.",
                           "Falha no Dado ou no Quando é montagem quebrada: o teste deve falhar no Então.",
                           scenario=key))
    func = rec.get("step_func")
    if not func or root is None:
        findings.append(_f("R4", "info", f"Não verifiquei a asserção do cenário {key}: sem o local da função.",
                           "Use o relatório do plugin para R4 ser verificada.", scenario=key))
        return
    const = constant_assertion(root, func)
    if const:
        findings.append(_f("R4", "error", f"A asserção do cenário {key} falha sempre, sem olhar o comportamento.",
                           "Troque assert False ou raise sem condição por uma asserção sobre o resultado.",
                           scenario=key, file=func.get("file"), line=func.get("line")))
    elif const is None:
        findings.append(_f("R4", "info", f"Não consegui ler a função do passo do cenário {key}.", "", scenario=key))


def _check_outline(key: str, rec: dict, root: Path | None, findings: list[dict]) -> None:
    rows = rec.get("rows") or []
    errors = [r for r in rows if r.get("outcome") == "error"]
    if errors:
        findings.append(_f("R8", "error", f"Uma linha dos exemplos de {key} deu erro.",
                           "Corrija a linha com erro; nenhuma linha pode dar erro no vermelho.", scenario=key))
        return
    good = [r for r in rows if _row_ok(r)]
    if not good:
        _check_plain(key, rec, root, findings)
        return
    _check_plain(key, dict(rec, outcome="failed", exception="AssertionError", failing_step_type="then",
                           step_func=good[0].get("step_func") or rec.get("step_func")), root, findings)


def _suite_findings(report: dict, owned: set[str], baseline: dict | None) -> list[dict]:
    findings = []
    now_s = report.get("scenarios") or {}
    now_t = report.get("tests") or {}
    if baseline is not None:
        before = [(k, v.get("outcome"), now_s.get(k, {}).get("outcome", "missing"))
                  for k, v in (baseline.get("scenarios") or {}).items() if k not in owned]
        before += [(k, v, now_t.get(k, "missing")) for k, v in (baseline.get("tests") or {}).items()]
        broken = sorted(k for k, was, now in before if was == "passed" and now != "passed")
    else:
        broken = sorted([k for k, v in now_s.items() if k not in owned and v.get("outcome") in ("failed", "error")]
                        + [k for k, v in now_t.items() if v in ("failed", "error")])
    for k in broken:
        findings.append(_f("R6", "error", f"O teste {k}, que não é deste step, deixou de passar.",
                           "O vermelho é só dos cenários do step: o resto da suíte fica como estava.", scenario=k))
    return findings


def _red_record(key: str, rec: dict | None, ok: bool, at: str | None, skeleton: list[str], report_path: str | None) -> dict:
    rec = rec or {}
    rows = rec.get("rows")
    return {
        "ts": at, "outcome": rec.get("outcome", "missing"), "reason_ok": ok, "exception": rec.get("exception"),
        "failing_step_type": rec.get("failing_step_type"),
        "rows_total": len(rows) if rows else None,
        "rows_failed": sum(1 for r in rows if _row_ok(r)) if rows else None,
        "rows_green_in_red": sum(1 for r in rows if r.get("outcome") == "passed") if rows else None,
        "skeleton_files": skeleton, "report": report_path, "already_green": rec.get("outcome") == "passed",
    }


def _failure_message(recs: dict) -> str:
    for key in sorted(recs):
        rec = recs[key] or {}
        if rec.get("outcome") in ("failed", "error"):
            word = TYPE_WORD.get(rec.get("failing_step_type"), "algum passo")
            return (f"O teste falhou no passo {word}: {rec.get('reason') or rec.get('failing_step') or ''} "
                    f"({rec.get('exception')}).").replace(":  (", ": (")
    return ""


def red_check(report: dict, owned, *, root: Path | None = None, source_files=(), coverage: dict | None = None,
              baseline: dict | None = None, skeleton_files=(), at: str | None = None,
              report_path: str | None = None) -> dict:
    owned = list(dict.fromkeys(owned))
    scenarios = report.get("scenarios") or {}
    collect_errors = report.get("collect_errors") or []
    findings: list[dict] = []
    recs: dict[str, dict | None] = {}
    for key in owned:
        rec = scenarios.get(key)
        if rec is None:
            rec = ({"outcome": "error", "exception": "CollectError",
                    "reason": collect_errors[0].get("reason", "")} if collect_errors else {"outcome": "missing"})
        recs[key] = rec
        if rec.get("rows"):
            _check_outline(key, rec, root, findings)
        else:
            _check_plain(key, rec, root, findings)
    skeleton = [_norm(str(p)) for p in skeleton_files]
    for sk in check_skeleton(skeleton_files):
        findings.append(dict(sk, rule="R5"))
    findings.extend(_suite_findings(report, set(owned), baseline))
    if source_files and coverage is not None and root is not None and not _exercised(root, source_files, coverage):
        findings.append(_f("R7", "error", "A rodada vermelha não executou nenhuma linha do código do step.",
                           "O teste deve chamar o código do step (o esqueleto), não só montar dados.",
                           file=", ".join(_norm(s) for s in source_files)))
    global_error = any(f["severity"] == "error" and f["rule"] in ("R5", "R6", "R7") for f in findings)
    out = {}
    for key in owned:
        own_error = any(f["severity"] == "error" and f["scenario"] == key for f in findings)
        out[key] = _red_record(key, recs[key], not own_error and not global_error, at, skeleton, report_path)
    errors = _errors(findings)
    return {"schema_version": SCHEMA_VERSION, "ok": not errors, "findings": findings, "scenarios": out,
            "escalate": any(r["already_green"] for r in out.values()), "message": _failure_message(recs)}


# ---------------------------------------------------------------------------
# Cucumber JSON + JUnit -> report (CYC-027)
# ---------------------------------------------------------------------------


def _python_name(name: str) -> str:
    """pytest-bdd test name of a scenario (make_python_name)."""
    s = re.sub(r"\W", "", name.replace(" ", "_"))
    return "test_" + re.sub(r"^\d+_*", "", s).lower()


def _element_record(element: dict, n_steps: int | None) -> dict:
    tags = {t.get("name", "").lstrip("@").lower() for t in element.get("tags", [])}
    steps = element.get("steps", [])
    prev = None
    rec = {"outcome": "passed", "exception": None, "failing_step_type": None, "failing_step": None,
           "step_func": None, "reason": "", "undefined": False}
    for step in steps:
        kind = KEYWORD_TYPES.get(step.get("keyword", "").strip().lower())
        prev = kind or prev
        status = step.get("result", {}).get("status")
        if status == "failed":
            message = step["result"].get("error_message", "")
            names = re.findall(r"\b([A-Z]\w*(?:Error|Exception))\b", message)
            exc = "AssertionError" if "AssertionError" in message else (names[-1] if names else "Error")
            rec.update(outcome="failed" if exc == "AssertionError" else "error", exception=exc,
                       failing_step_type=prev, failing_step=step.get("name"),
                       reason=message.strip().splitlines()[0][:200] if message.strip() else "")
            break
        if status in ("undefined", "pending", "ambiguous"):
            rec.update(outcome="error", exception="StepDefinitionNotFoundError", failing_step_type=prev,
                       failing_step=step.get("name"), undefined=status != "ambiguous")
            break
    else:
        statuses = [s.get("result", {}).get("status") for s in steps]
        if statuses and all(s == "skipped" for s in statuses):
            rec["outcome"] = "skipped"
        elif n_steps is not None and len(steps) < n_steps:
            rec.update(outcome="error", exception="StepDefinitionNotFoundError", undefined=True)
    if "xfail" in tags:
        rec["outcome"] = "xpassed" if rec["outcome"] == "passed" else "xfailed"
    return rec


def _junit_cases(junit: str) -> dict[str, list[str]]:
    try:
        root = ET.fromstring(junit)
    except ET.ParseError as err:
        raise BuildError("JUnit XML inválido") from err
    cases: dict[str, list[str]] = {}
    for case in root.iter("testcase"):
        base = case.get("name", "").split("[", 1)[0]
        if case.find("skipped") is not None:
            state = "skipped"
        elif case.find("failure") is not None or case.find("error") is not None:
            node = case.find("failure") if case.find("failure") is not None else case.find("error")
            text = (node.get("message", "") + " " + (node.text or "")) if node is not None else ""
            state = "undefined" if "StepDefinitionNotFoundError" in text else (
                "failed" if "AssertionError" in text else "error")
        else:
            state = "passed"
        cases.setdefault(base, []).append(state)
    return cases


def report_from_cucumber(cucumber, junit: str | None = None, expected: dict | None = None) -> dict:
    """Build a scenario report from the Cucumber JSON (and the JUnit of the same run)."""
    expected = expected or {}
    grouped: dict[str, list[dict]] = {}
    files: dict[str, str] = {}
    for feature in cucumber or []:
        uri = feature.get("uri", "")
        for element in feature.get("elements", []):
            key = _key_from_uri(uri, element.get("name", ""))
            files[key] = "features/" + _norm(uri)
            grouped.setdefault(key, []).append(_element_record(element, expected.get(key)))
    scenarios = {}
    for key, recs in grouped.items():
        reqs = []
        if len(recs) == 1:
            rec = dict(recs[0], rows=None)
        else:
            worst = min(recs, key=lambda r: PRIORITY.index(r["outcome"]))
            rows = [{"index": i, "outcome": r["outcome"], "exception": r["exception"],
                     "failing_step_type": r["failing_step_type"], "step_func": None} for i, r in enumerate(recs)]
            rec = dict(worst, rows=rows)
        scenarios[key] = dict(rec, scenario_key=key, feature_file=files[key], req=reqs, duration=0.0)
    if junit:
        cases = _junit_cases(junit)
        for key in expected:
            if key in scenarios:
                continue
            states = cases.get(_python_name(key.split("::", 1)[1]))
            if not states:
                continue
            state = min(("error" if s == "undefined" else s for s in states), key=PRIORITY.index)
            scenarios[key] = {"scenario_key": key, "feature_file": None, "req": [], "outcome": state,
                              "exception": "StepDefinitionNotFoundError" if "undefined" in states else None,
                              "failing_step_type": None, "failing_step": None, "step_func": None, "reason": "",
                              "undefined": "undefined" in states, "duration": 0.0, "rows": None}
    return {"schema_version": SCHEMA_VERSION, "generated_at": None, "pytest_bdd_version": None,
            "scenarios": dict(sorted(scenarios.items())), "tests": {}}


# ---------------------------------------------------------------------------
# ITF-009 green-check
# ---------------------------------------------------------------------------


def green_check(report: dict, owned) -> dict:
    scenarios = report.get("scenarios") or {}
    findings, final = [], {}
    for key in dict.fromkeys(owned):
        outcome = (scenarios.get(key) or {}).get("outcome", "missing")
        if (scenarios.get(key) or {}).get("undefined"):
            outcome = "undefined"
        final[key] = {"test_result": DRM_RESULT.get(outcome, outcome)}  # DRM-006 vocabulary
        if outcome != "passed":
            findings.append(_f("ITF-009", "error", f"O cenário {key} não está verde: o resultado foi {outcome}.",
                               "Só passed conta como verde; skip, xfail e erro não contam.", scenario=key))
    return {"schema_version": SCHEMA_VERSION, "ok": not findings, "findings": findings, "final": final}


# ---------------------------------------------------------------------------
# ITF-007 freeze
# ---------------------------------------------------------------------------


def freeze_snapshot(root: Path, files) -> dict:
    out = {}
    for rel in files:
        path = Path(root) / rel
        try:
            out[_norm(rel)] = _sha(path.read_bytes())
        except OSError as err:
            raise BuildError(f"não consegui ler {rel}") from err
    return {"schema_version": SCHEMA_VERSION, "files": dict(sorted(out.items()))}


def freeze_compare(root: Path, snapshot: dict) -> list[dict]:
    findings = []
    for rel, digest in sorted((snapshot.get("files") or {}).items()):
        path = Path(root) / rel
        current = _sha(path.read_bytes()) if path.is_file() else None
        if current != digest:
            findings.append(_f("ITF-007", "error", f"O arquivo congelado {rel} mudou depois do vermelho.",
                               "Teste e .feature congelados não mudam; desfaça a mudança.", file=rel))
    return findings


# ---------------------------------------------------------------------------
# ITF-008 scope
# ---------------------------------------------------------------------------


def classify(path: str) -> str:
    p = _norm(path)
    name = p.rsplit("/", 1)[-1]
    parts = p.split("/")
    if (name in ("gate.py", "quality-baseline.json") or p.startswith((".claude/hooks/", ".claude/settings"))
            or p == "product-design/conventions.md"):
        return "forbidden"
    if p.startswith("features/"):
        if len(parts) >= 3 and (parts[2] == "gate.json" or parts[2] in ("runner", "drift")):
            return "record"  # written by /implement through build_checks, not by a role
        return "feature"
    if "tests" in parts[:-1] or name.startswith("test_") or name.endswith("_test.py") or name == "conftest.py":
        return "test"
    if name.endswith(".py"):
        return "source"
    return "other"


_ALLOWED = {"tester": {"test", "source"}, "coder": {"test", "source", "other"}, "cleaner": {"source"},
            "hardener": {"test", "source"}}
_ROLE_HINT = {
    "tester": "O Tester só escreve testes, definições de passo, conftest e esqueleto.",
    "coder": "O Coder não toca .feature nem testes congelados.",
    "cleaner": "O Cleaner só muda código-fonte, nunca testes.",
    "hardener": "O Hardener só escreve testes novos e linhas de pragma com motivo.",
}


def check_scope(role: str, changes, frozen, added=None, removed=None) -> list[dict]:
    if role not in ROLES:
        raise ValueError(f"papel desconhecido: {role}")
    added = added or {}
    removed = removed or {}
    frozen = {_norm(f) for f in frozen}
    findings = []
    for _status, path in changes:
        p = _norm(path)
        kind = classify(p)
        if kind == "record":
            continue
        if kind == "forbidden":
            findings.append(_f("ITF-008", "error", f"{p} é do humano: nenhum papel o muda.",
                               "Portão, hooks, settings, baseline e linhas GATE_* só mudam por mão humana.", file=p))
            continue
        if p in frozen and role != "tester" and kind != "feature":
            findings.append(_f("ITF-007", "error", f"O arquivo congelado {p} mudou.",
                               "Teste e .feature congelados não mudam; desfaça a mudança.", file=p))
            continue
        if kind not in _ALLOWED[role]:
            findings.append(_f("ITF-008", "error", f"O papel {role} mudou {p}, fora do seu escopo.",
                               _ROLE_HINT[role], file=p))
            continue
        if role == "hardener" and kind == "source":
            lines = added.get(p, [])
            bad = [ln for ln in lines if not PRAGMA_RE.search(ln)]
            codes = {ln.split("#", 1)[0].strip() for ln in lines}
            lost = [ln for ln in removed.get(p, []) if ln.split("#", 1)[0].strip() not in codes]
            if bad or lost or not lines:
                findings.append(_f("ITF-008", "error", f"O Hardener mudou código em {p} além do pragma.",
                                   "Só vale acrescentar `# pragma: no mutate  # equivalent: <motivo>` a uma linha.",
                                   file=p))
    return sorted(findings, key=lambda f: (f["file"], f["rule"]))


# ---------------------------------------------------------------------------
# ITF-018 uncovered
# ---------------------------------------------------------------------------

_HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def parse_diff_added(diff: str) -> dict[str, set[int]]:
    added: dict[str, set[int]] = {}
    current: str | None = None
    line_no = 0
    for raw in diff.splitlines():
        if raw.startswith("+++ "):
            target = raw[4:].strip()
            current = None if target == "/dev/null" else _norm(target.removeprefix("b/"))
            continue
        if raw.startswith(("--- ", "diff --git")):
            continue
        m = _HUNK_RE.match(raw)
        if m:
            line_no = int(m.group(1))
            continue
        if current is None:
            continue
        if raw.startswith("+"):
            added.setdefault(current, set()).add(line_no)
            line_no += 1
        elif raw.startswith(" "):
            line_no += 1
    return added


def uncovered(added: dict, coverage: dict, *, provisional: bool = True, base: str | None = None) -> dict:
    items = []
    n_touched = 0
    for path in sorted(added):
        data = _coverage_file(coverage, path)
        if not data:
            continue
        lines = set(added[path])
        missing = set(data.get("missing_lines") or [])
        executable = set(data.get("executed_lines") or []) | missing
        n_touched += len(lines & executable)
        items += [{"file": path, "line": n, "kind": "line"} for n in sorted(lines & missing)]
        branches = [tuple(b) for b in (data.get("executed_branches") or []) + (data.get("missing_branches") or [])]
        n_touched += sum(1 for src, _dst in branches if src in lines)
        items += [{"file": path, "line": src, "kind": "branch"}
                  for src, _dst in sorted(tuple(b) for b in (data.get("missing_branches") or [])) if src in lines]
    items.sort(key=lambda i: (i["file"], i["line"], i["kind"]))
    return {"schema_version": SCHEMA_VERSION, "base": base, "n_touched": n_touched, "n_uncovered": len(items),
            "items": items, "provisional": provisional}


# ---------------------------------------------------------------------------
# ITF-017 baseline
# ---------------------------------------------------------------------------


def baseline_state(before: bytes | None, after: bytes | None, known: bool = True) -> dict:
    if not known:
        return {"moved": None, "sha_before": None, "sha_after": None}
    sb = _sha(before) if before is not None else None
    sa = _sha(after) if after is not None else None
    return {"moved": sb != sa, "sha_before": sb, "sha_after": sa}


# ---------------------------------------------------------------------------
# ITF-010 crap (same formula as the gate; the target is the Cleaner's, not the gate's)
# ---------------------------------------------------------------------------


def _radon_functions(entries):
    def flatten(entry, prefix):
        qual = prefix + entry["name"]
        yield qual, entry
        for child in entry.get("closures", []) or []:
            yield from flatten(child, qual + ".")

    for entry in entries:
        if entry.get("type") == "class":
            for meth in entry.get("methods", []) or []:
                yield from flatten(meth, entry["name"] + ".")
            continue
        prefix = entry["classname"] + "." if entry.get("classname") else ""
        yield from flatten(entry, prefix)


def crap_findings(radon: dict, coverage: dict, files, target: float = CRAP_TARGET_TOUCHED) -> list[dict]:
    if target < CRAP_TARGET_FLOOR:
        raise ValueError(f"alvo {target} abaixo do piso {CRAP_TARGET_FLOOR}")
    wanted = {_norm(f) for f in files}
    found = []
    for path, entries in (radon or {}).items():
        rel = _norm(path)
        if rel not in wanted or not isinstance(entries, list):
            continue
        functions = (_coverage_file(coverage, rel) or {}).get("functions") or {}
        for qual, entry in _radon_functions(entries):
            summ = (functions.get(qual) or {}).get("summary")
            if summ is None:
                cov = 0.0
            else:
                denom = summ.get("num_statements", 0) + summ.get("num_branches", 0)
                cov = 1.0 if denom == 0 else (summ.get("covered_lines", 0) + summ.get("covered_branches", 0)) / denom
            cc = int(entry.get("complexity", 1))
            value = round(cc ** 2 * (1.0 - cov) ** 3 + cc, 2)
            if value > target:
                found.append({"key": f"{rel}::{qual}", "file": rel, "function": qual, "cc": cc,
                              "cov": round(cov, 4), "crap": value, "target": target})
    return sorted(found, key=lambda f: f["key"])


# ---------------------------------------------------------------------------
# ITF-015 record, ITF-020 status
# ---------------------------------------------------------------------------


def _merge(dst: dict, src: dict) -> dict:
    for key, value in src.items():
        if isinstance(value, dict) and isinstance(dst.get(key), dict):
            _merge(dst[key], value)
        else:
            dst[key] = copy.deepcopy(value)
    return dst


def _gate_entry(result: dict, baseline_moved: bool | None) -> dict:
    code = int(result.get("exit_code", 1))
    category = CATEGORY.get(code, "CONFIG")
    if code == 0 and baseline_moved:
        category = "PASS_WITH_BASELINE"
    return {"exit_code": code, "category": category, "ref": result.get("ref")}


def record(gate: dict, step: int, payload: dict, at: str, plan: str | None = None) -> dict:
    out = copy.deepcopy(gate or {})
    out.setdefault("schema_version", 1)
    out.setdefault("fast", None)
    out.setdefault("full", None)
    if "baseline_moved" in payload:
        out["baseline_moved"] = payload["baseline_moved"]
    moved = out.get("baseline_moved")
    if payload.get("fast") is not None:
        out["fast"] = _gate_entry(payload["fast"], moved)
    if payload.get("full") is not None:
        out["full"] = _gate_entry(payload["full"], moved)
    build = out.setdefault("build", {})
    build["schema_version"] = SCHEMA_VERSION
    if plan:
        build["plan"] = plan
    build.setdefault("scenarios", {})
    build.setdefault("steps", {})
    build.setdefault("feature", {})
    if payload.get("step"):
        _merge(build["steps"].setdefault(str(step), {}), payload["step"])
    for key, data in (payload.get("scenarios") or {}).items():
        entry = build["scenarios"].setdefault(key, {})
        _merge(entry, data)
        if step:
            entry["step"] = step
    if payload.get("feature"):
        _merge(build["feature"], payload["feature"])
    out["ts"] = at
    return out


def next_phase(gate: dict, step: int, pipeline: bool = False) -> str:
    st = ((gate or {}).get("build") or {}).get("steps", {}).get(str(step)) or {}
    status = st.get("status")
    if status in ("PASS", "PASS_WITH_BASELINE"):
        return "DONE"
    if status == "ESCALATED":
        return "ESCALATED"
    phases = st.get("phases") or {}

    def done(name: str) -> bool:
        ph = phases.get(name) or {}
        return bool(ph.get("ok") or ph.get("skipped"))

    for name in ("red", "green") + (("clean", "hard") if pipeline else ()):
        if not done(name):
            return name.upper()
    return "REC"


# ---------------------------------------------------------------------------
# ITF-001, ITF-003, ITF-021 route
# ---------------------------------------------------------------------------


def _base_actions(tests: str | None) -> list[str]:
    return list(_LEGACY if cps.is_na(tests) else _TDD)


def route(text: str, pipeline: bool = False) -> dict:
    plan = cps.parse_plan(text)
    out = {"schema_version": SCHEMA_VERSION, "version": None, "pipeline": pipeline, "refusal": None,
           "fallback": None, "preamble": [], "steps": [], "end": []}
    if plan.version is None:
        out["fallback"] = "manual"
        return out
    if plan.version not in ("1", "2"):
        out["refusal"] = f"plan_format_version {plan.version} não suportada"
        return out
    out["version"] = int(plan.version)
    if plan.version == "1":
        if pipeline:
            out["refusal"] = REFUSAL_V1
            return out
        out["preamble"] = ["version-check"]
        out["steps"] = [{"n": s.n, "title": s.title, "mode": "legacy" if cps.is_na(s.tests) else "tdd",
                         "actions": _base_actions(s.tests), "reason": None, "scenarios": []} for s in plan.steps]
        out["end"] = ["quality-gate", "done"]
        return out
    skipped = any(value.startswith("skipped") for _line, value in plan.specifies)
    out["preamble"] = ["version-check", "check-plan-scenarios"] + ([] if skipped else ["check-specify-status"])
    for s in plan.steps:
        keys = cps.parse_scenarios(s.scen)[0] if s.scen and not cps.is_na(s.scen) else []
        if keys and not skipped and not cps.is_na(s.tests):
            actions = _TEST_FIRST_HEAD + (["clean", "hard"] if pipeline else []) + _TEST_FIRST_TAIL
            out["steps"].append({"n": s.n, "title": s.title, "mode": "test-first", "actions": list(actions),
                                 "reason": None, "scenarios": keys})
            continue
        actions = _base_actions(s.tests)
        actions.insert(actions.index("note"), "record")
        reason = cps.na_reason(s.scen) if s.scen else ("Specify: skipped" if skipped else "")
        out["steps"].append({"n": s.n, "title": s.title, "mode": "no-scenario", "actions": actions,
                             "reason": reason, "scenarios": []})
    out["end"] = list(_V2_END) if not skipped else ["quality-gate", "done"]
    return out


# ---------------------------------------------------------------------------
# ITF-023 export, ITF-024 demo
# ---------------------------------------------------------------------------


def export_files(gate: dict, slug: str, cucumber=None) -> dict[str, str]:
    build = gate.get("build") or {}
    base = f"features/{slug}"
    red = {k: v["red"]["reason_ok"] for k, v in sorted((build.get("scenarios") or {}).items())
           if isinstance(v.get("red"), dict) and v["red"].get("reason_ok") is not None}
    files = {f"{base}/drift/red-reason.json": dump_json({"schema_version": SCHEMA_VERSION, "scenarios": red})}
    feature = build.get("feature") or {}
    if "touched_total" in feature:
        files[f"{base}/drift/coverage.json"] = dump_json({
            "schema_version": SCHEMA_VERSION, "base": feature.get("base"),
            "touched_total": feature.get("touched_total"), "touched_uncovered": feature.get("touched_uncovered")})
    if cucumber is not None:
        files[f"{base}/runner/cucumber.json"] = dump_json(cucumber)
    out = copy.deepcopy(gate)
    if "baseline_moved" in feature:
        out["baseline_moved"] = feature["baseline_moved"]
    files[f"{base}/gate.json"] = dump_json(out)
    return files


def _state(entry: dict) -> str:
    final = (entry.get("final") or {}).get("test_result")
    red_ok = (entry.get("red") or {}).get("reason_ok")
    if final == "passed" and red_ok:
        return "demonstrado"
    if (final is not None and final != "passed") or red_ok is False:
        return "não demonstrado"
    return "não medido"


_STATE_SENTENCE = {
    "demonstrado": "Eu vi o teste falhar antes do código e passar depois.",
    "não demonstrado": "Eu não consegui mostrar este cenário: o teste não falhou antes do código ou não passou depois.",
    "não medido": "Eu não tenho registro de que o teste falhou antes do código. Eu não medi.",
}


_TECH_EXTRA = re.compile(r"\b(?:linhas?|line)\s+\d|\.py\b|:\d+\b")


def split_questions(questions) -> tuple[list[str], list[str]]:
    """(citizen, technical): a question with a technical token must not reach the citizen register."""
    ok: list[str] = []
    technical: list[str] = []
    for q in questions or []:
        bad = TECH_TOKENS.search(QUOTED.sub("", q)) or _TECH_EXTRA.search(q)
        (technical if bad else ok).append(q)
    return ok, technical


def demo_text(gate: dict, steps: dict, questions) -> str:
    questions, _technical = split_questions(questions)
    scenarios = (gate.get("build") or {}).get("scenarios") or {}
    keys = sorted(set(scenarios) | set(steps))
    lines = ["# O que eu construí e mostrei", "",
             "Para cada cenário que você aprovou, eu conto o que ele pede e o que eu vi.", ""]
    for key in keys:
        name = key.split("::", 1)[-1]
        state = _state(scenarios.get(key) or {})
        lines += [f"## {name}", "", "O cenário pede:", ""]
        lines += [f"- {text}" for text in steps.get(key, [])]
        lines += ["", f"Estado: {state}. {_STATE_SENTENCE[state]}", ""]
    if questions:
        lines += ["## Perguntas para você", "",
                  "Eu mudei o código de propósito e nenhum cenário percebeu. Diga se isso importa.", ""]
        lines += [f"- {q}" for q in questions]
        lines.append("")
    return "\n".join(lines)


def feature_steps(root: Path, slug: str) -> dict[str, list[str]]:
    """Narration of each scenario of features/<slug>/ (keyword + text, in the file's language)."""
    import check_features as cf

    out: dict[str, list[str]] = {}
    for path in sorted((Path(root) / "features" / slug).glob("*.feature")):
        feature = cf.parse_feature(read_text(path))
        for sc in feature.scenarios:
            words = [f"{KIND_WORD.get(st.kind, '')} {st.text}".strip() for st in sc.steps]
            out[cf.scenario_key(slug, str(path), sc.name)] = words
    return out


# ---------------------------------------------------------------------------
# install-plugin (ITF-016)
# ---------------------------------------------------------------------------


def install_plugin(project: Path, source: Path = PLUGIN_SOURCE) -> tuple[int, str]:
    """Copy the plugin to <project>/tests/scenario_report.py and load it from tests/conftest.py.

    Idempotent. Refuses (1) to overwrite a copy edited by hand since the last install.
    """
    try:
        new = source.read_bytes()
    except OSError as err:
        raise BuildError(f"plugin template not readable: {source}") from err
    tests = project / "tests"
    tests.mkdir(parents=True, exist_ok=True)
    target = tests / "scenario_report.py"
    stamp = tests / PLUGIN_STAMP
    if target.exists():
        current = target.read_bytes()
        recorded = stamp.read_text(encoding="utf-8").strip() if stamp.exists() else None
        if _sha(current) != _sha(new) and _sha(current) != recorded:
            return 1, f"{target}: copia editada a mao; nao sobrescrevi. Apague-a para reinstalar."
    target.write_bytes(new)
    stamp.write_text(_sha(new) + "\n", encoding="utf-8")
    conftest = tests / "conftest.py"
    text = conftest.read_text(encoding="utf-8-sig") if conftest.exists() else ""
    if PLUGIN_LINE not in text:
        prefix = text if not text or text.endswith("\n") else text + "\n"
        conftest.write_text(prefix + PLUGIN_LINE + "\n", encoding="utf-8")
    return 0, f"{target} ({_sha(new)[:12]})"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


SUBPROCESS_TIMEOUT = 60  # seconds; a hung git or tool becomes exit 2, not a stuck run


def _run(cmd, **kw):
    """subprocess.run with a timeout; TimeoutExpired becomes BuildError (exit 2, no traceback)."""
    kw.setdefault("timeout", SUBPROCESS_TIMEOUT)
    kw.setdefault("check", False)
    try:
        return subprocess.run(cmd, check=kw.pop("check"), **kw)
    except subprocess.TimeoutExpired as err:
        raise BuildError(f"{cmd[0]} passou de {kw['timeout']} s e foi interrompido") from err


def snapshot_tree(root: Path) -> str:
    """Tree id of the working tree (tracked + untracked, not ignored) without touching the real index.

    Copies the index to a temp file, runs `git add -A` and `git write-tree` with GIT_INDEX_FILE on it.
    """
    import shutil

    root = Path(root)
    index = Path(_git(root, "rev-parse", "--path-format=absolute", "--git-path", "index").strip())
    fd, tmp_name = tempfile.mkstemp(prefix="seja-index-")
    os.close(fd)
    tmp = Path(tmp_name)
    try:
        if index.exists():
            shutil.copyfile(index, tmp)
        else:
            tmp.unlink()
        env = {**os.environ, "GIT_INDEX_FILE": str(tmp)}
        for args in (["add", "-A"], ["write-tree"]):
            res = _run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False, env=env)
            if res.returncode != 0:
                raise BuildError(f"git {' '.join(args)} falhou: {res.stderr.strip()[:200]}")
        return res.stdout.strip()
    finally:
        tmp.unlink(missing_ok=True)


def _git(root: Path, *args: str) -> str:
    res = _run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    if res.returncode != 0:
        raise BuildError(f"git {' '.join(args)} falhou: {res.stderr.strip()[:200]}")
    return res.stdout


def _changes(root: Path, base: str) -> list[tuple[str, str]]:
    out = []
    for line in _git(root, "diff", "--name-status", "--no-renames", base).splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status, path = parts[0], parts[-1]
        if status == "D" and (Path(root) / path).is_file():
            # a file of a `git write-tree` snapshot that is untracked again: unchanged or modified, not deleted
            if _same_as_base(root, base, path):
                continue
            status = "M"
        out.append((status, path))
    for path in _git(root, "ls-files", "--others", "--exclude-standard").splitlines():
        path = path.strip()
        if path and not any(p == path for _s, p in out) and not _same_as_base(root, base, path):
            out.append(("A", path))
    return out


def _same_as_base(root: Path, base: str, path: str) -> bool:
    """An untracked file that the base (a commit or a `git write-tree` snapshot) already has, unchanged."""
    res = _run(["git", "-C", str(root), "rev-parse", "--verify", "-q", f"{base}:{path}"],
                         capture_output=True, text=True, check=False)
    if res.returncode != 0:
        return False
    now = _run(["git", "-C", str(root), "hash-object", "--", path], capture_output=True, text=True,
                         check=False)
    return now.returncode == 0 and now.stdout.strip() == res.stdout.strip()


def _diff_lines(root: Path, base: str, path: str) -> tuple[list[str], list[str]]:
    added, removed = [], []
    tracked = _git(root, "ls-files", "--", path).strip()
    if not tracked:
        return read_text(Path(root) / path).splitlines(), []
    for line in _git(root, "diff", "-U0", base, "--", path).splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])
        elif line.startswith("-") and not line.startswith("---"):
            removed.append(line[1:])
    return added, removed


def _print(result: dict, as_json: bool, summary: str = "") -> None:
    if as_json:
        sys.stdout.write(dump_json(result))
        return
    for f in result.get("findings", []):
        where = f" ({f['file']}{':' + str(f['line']) if f.get('line') else ''})" if f.get("file") else ""
        hint = f" Dica: {f['hint']}" if f.get("hint") else ""
        print(f"{f['rule']} {f['severity']}: {f['message']}{where}{hint}")
    if summary:
        print(summary)


def _write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=path.suffix)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, path)


def _gate_path(root: Path, slug: str) -> Path:
    return Path(root) / "features" / slug / "gate.json"


def _load_gate(root: Path, slug: str) -> dict:
    path = _gate_path(root, slug)
    return read_json(path) if path.is_file() else {}


def _cmd_route(a) -> int:
    result = route(read_text(a.plan), pipeline=a.pipeline)
    if result["refusal"]:
        print(result["refusal"], file=sys.stderr)
        return 1 if result["refusal"] == REFUSAL_V1 else 2
    if a.json:
        sys.stdout.write(dump_json(result))
    else:
        for s in result["steps"]:
            print(f"step {s['n']}: {s['mode']}" + (f" ({s['reason']})" if s["reason"] else ""))
    return 0


def _cmd_red(a) -> int:
    if a.report:
        report = read_json(a.report)
    elif a.cucumber:
        report = report_from_cucumber(read_json(a.cucumber), read_text(a.junit) if a.junit else None)
    else:
        raise BuildError("dê --report ou --cucumber")
    result = red_check(report, a.owned, root=a.root, source_files=a.files or (),
                       coverage=read_json(a.coverage) if a.coverage else None,
                       baseline=read_json(a.baseline) if a.baseline else None,
                       skeleton_files=a.skeleton or (), at=a.at,
                       report_path=_norm(str(a.report or a.cucumber)))
    _print(result, a.json, "vermelho pelo motivo certo" if result["ok"] else "vermelho recusado")
    return 0 if result["ok"] else 1


def _cmd_green(a) -> int:
    result = green_check(read_json(a.report), a.owned)
    _print(result, a.json, "verde" if result["ok"] else "não verde")
    return 0 if result["ok"] else 1


def _cmd_skeleton(a) -> int:
    findings = check_skeleton(a.files)
    _print({"schema_version": SCHEMA_VERSION, "findings": findings}, a.json)
    return 1 if findings else 0


def _cmd_freeze(a) -> int:
    if a.write:
        if not a.files:
            raise BuildError("freeze --write precisa de arquivos")
        _write_atomic(Path(a.write), dump_json(freeze_snapshot(a.root, a.files)))
        return 0
    if not a.check:
        raise BuildError("dê --write ou --check")
    findings = freeze_compare(a.root, read_json(a.check))
    _print({"findings": findings}, a.json)
    return 1 if findings else 0


def _cmd_scope(a) -> int:
    changes = _changes(a.root, a.base)
    frozen = set((read_json(a.frozen).get("files") or {}).keys()) if a.frozen else set()
    added, removed = {}, {}
    if a.role == "hardener":
        for _st, path in changes:
            if classify(path) == "source":
                added[_norm(path)], removed[_norm(path)] = _diff_lines(a.root, a.base, path)
    findings = check_scope(a.role, changes, frozen, added, removed)
    _print({"schema_version": SCHEMA_VERSION, "role": a.role, "findings": findings}, a.json)
    return 1 if findings else 0


def _cmd_crap(a) -> int:
    try:
        found = crap_findings(read_json(a.radon), read_json(a.coverage), a.files, a.target)
    except ValueError as err:
        raise BuildError(str(err)) from err
    result = {"schema_version": SCHEMA_VERSION, "target": a.target, "findings": found}
    if a.json:
        sys.stdout.write(dump_json(result))
    else:
        for f in found:
            print(f"CRAP({f['key']})={f['crap']} (CC={f['cc']}, cov={f['cov']}) > {a.target:g}: dividir")
    return 0


def _cmd_uncovered(a) -> int:
    diff = read_text(a.diff) if a.diff else _git(a.root, "diff", "-U0", a.base)
    added = parse_diff_added(diff)
    for path in _git(a.root, "ls-files", "--others", "--exclude-standard").splitlines():
        p = Path(a.root) / path
        if path.endswith(".py") and p.is_file():
            added[_norm(path)] = set(range(1, len(read_text(p).splitlines()) + 1))
    result = uncovered(added, read_json(a.coverage), provisional=not a.final, base=a.base)
    if a.json:
        sys.stdout.write(dump_json(result))
    else:
        print(f"tocadas {result['n_touched']}, sem cenário {result['n_uncovered']}"
              + (" (provisório)" if result["provisional"] else ""))
    return 0


def _cmd_baseline(a) -> int:
    try:
        shown = _run(["git", "-C", str(a.root), "show", f"{a.base}:{a.file}"], capture_output=True,
                               check=False)
        known = _run(["git", "-C", str(a.root), "rev-parse", "--verify", a.base], capture_output=True,
                               check=False).returncode == 0
    except OSError:
        known, shown = False, None
    before = shown.stdout if (shown is not None and shown.returncode == 0) else None
    path = Path(a.root) / a.file
    after = path.read_bytes() if path.is_file() else None
    result = dict(baseline_state(before, after, known=known), schema_version=SCHEMA_VERSION)
    if a.json:
        sys.stdout.write(dump_json(result))
    else:
        print(f"baseline_moved: {json.dumps(result['moved'])}")
    return 0


def _cmd_record(a) -> int:
    payload = read_json(a.source)
    gate = record(_load_gate(a.root, a.feature), a.step, payload, a.at, plan=a.plan)
    _write_atomic(_gate_path(a.root, a.feature), dump_json(gate))
    return 0


def _cmd_status(a) -> int:
    print(next_phase(_load_gate(a.root, a.feature), a.step, pipeline=a.pipeline))
    return 0


def _cmd_export(a) -> int:
    gate = _load_gate(a.root, a.feature)
    if not gate:
        raise BuildError(f"features/{a.feature}/gate.json não existe")
    files = export_files(gate, a.feature, read_json(a.cucumber) if a.cucumber else None)
    for rel, text in files.items():
        _write_atomic(Path(a.root) / rel, text)
        print(rel)
    return 0


def _cmd_demo(a) -> int:
    questions = read_json(a.questions) if a.questions else []
    text = demo_text(_load_gate(a.root, a.feature), feature_steps(a.root, a.feature), questions)
    _ok, technical = split_questions(questions)
    if technical:
        note = ("# Perguntas do Hardener fora do registro do citizen\n\n"
                "Pergunta com termo técnico, fora do registro do citizen:\n\n"
                + "".join(f"- {q}\n" for q in technical))
        print(note, file=sys.stderr)
        if a.out:
            _write_atomic(Path(a.out).with_suffix(".power-dev.md"), note)
    if a.out:
        _write_atomic(Path(a.out), text)
        print(a.out)
    else:
        sys.stdout.write(text)
    return 0


def _cmd_snapshot(a) -> int:
    print(snapshot_tree(a.root))
    return 0


def _cmd_install(a) -> int:
    code, message = install_plugin(a.project)
    print(message, file=sys.stderr if code else sys.stdout)
    return code


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="build_checks.py", description="Checks of the test-first branch (ITF).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, func, help_text, json_flag=True):
        p = sub.add_parser(name, help=help_text)
        p.set_defaults(func=func)
        if json_flag:
            p.add_argument("--json", action="store_true")
        return p

    p = add("route", _cmd_route, "classify the steps of a plan (ITF-001, ITF-003)")
    p.add_argument("plan", type=Path)
    p.add_argument("--pipeline", action="store_true")
    p = add("snapshot", _cmd_snapshot, "tree id of the working tree, index untouched (phase base)", json_flag=False)
    p.add_argument("--root", type=Path, default=Path("."))
    p = add("install-plugin", _cmd_install, "copy the runner report plugin (ITF-016)", json_flag=False)
    p.add_argument("project", type=Path)
    p = add("skeleton", _cmd_skeleton, "neutral skeleton (ITF-004)")
    p.add_argument("files", nargs="+", type=Path)
    p = add("red-check", _cmd_red, "red for the right reason (ITF-005)")
    p.add_argument("--report", type=Path)
    p.add_argument("--cucumber", type=Path)
    p.add_argument("--junit", type=Path)
    p.add_argument("--owned", nargs="+", required=True)
    p.add_argument("--root", type=Path)
    p.add_argument("--files", nargs="*")
    p.add_argument("--coverage", type=Path)
    p.add_argument("--baseline", type=Path)
    p.add_argument("--skeleton", nargs="*", type=Path)
    p.add_argument("--at")
    p = add("green-check", _cmd_green, "owned scenarios exactly passed (ITF-009)")
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--owned", nargs="+", required=True)
    p = add("freeze", _cmd_freeze, "write or check the hashes of the frozen files (ITF-007)")
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--write")
    p.add_argument("--check", type=Path)
    p.add_argument("files", nargs="*")
    p = add("scope", _cmd_scope, "files changed by a role (ITF-008)")
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--role", choices=ROLES, required=True)
    p.add_argument("--base", required=True)
    p.add_argument("--frozen", type=Path)
    p = add("crap", _cmd_crap, "touched functions above the Cleaner target (ITF-010)")
    p.add_argument("--radon", type=Path, required=True)
    p.add_argument("--coverage", type=Path, required=True)
    p.add_argument("--files", nargs="+", required=True)
    p.add_argument("--target", type=float, default=CRAP_TARGET_TOUCHED)
    p = add("uncovered", _cmd_uncovered, "touched lines no scenario test runs (ITF-018)")
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--base", required=True)
    p.add_argument("--coverage", type=Path, required=True)
    p.add_argument("--diff", type=Path)
    p.add_argument("--final", action="store_true")
    p = add("baseline", _cmd_baseline, "did quality-baseline.json move (ITF-017)")
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--base", required=True)
    p.add_argument("--file", default="quality-baseline.json")
    p = add("record", _cmd_record, "write features/<slug>/gate.json (ITF-015)", json_flag=False)
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--feature", required=True)
    p.add_argument("--step", type=int, required=True)
    p.add_argument("--from", dest="source", type=Path, required=True)
    p.add_argument("--at", required=True)
    p.add_argument("--plan")
    p = add("status", _cmd_status, "next phase of a step (ITF-020)", json_flag=False)
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--feature", required=True)
    p.add_argument("--step", type=int, required=True)
    p.add_argument("--pipeline", action="store_true")
    p = add("export", _cmd_export, "files read by the drift report (ITF-023)", json_flag=False)
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--feature", required=True)
    p.add_argument("--cucumber", type=Path)
    p = add("demo", _cmd_demo, "per-scenario demonstration for the citizen (ITF-024)", json_flag=False)
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--feature", required=True)
    p.add_argument("--questions", type=Path)
    p.add_argument("--out")
    return ap


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code else 0
    try:
        return args.func(args)
    except (BuildError, OSError) as err:
        print(f"build_checks: {err}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
