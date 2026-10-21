#!/usr/bin/env python3
# designer: When /plan writes a plan in format v3, I check that what you
#   asked, what I understood and what proves it are all in the plan: the
#   intention, every requirement with its use case, my retelling with what I
#   will not do, your words, and a step that tests each requirement. I tell
#   you which requirement was left without a use case or a test before any
#   code is written.
"""
check_plan_intent.py -- Check the plan v3 shape (D-006, PIC rules).

Invocation: agent-invoked, hook-ci
Lifecycle: active

Rules (``.claude/references/general/plan-intent-and-cases.md``):
  PIC-002  the five sections exist and are not empty
  PIC-003  ``## Intenção`` has the four lines
  PIC-004  requirements: valid ``REQ-<slug>-NNN`` (lowercase slug), unique,
           one sentence, ``Para que:`` and an origin
  PIC-005  every requirement has a use case; every use case cites one
  PIC-006  ``## Retradução`` has "O que eu não vou fazer" (error) and an
           ``Aprovação:`` line (warning: the check runs before approval)
  PIC-007  every ``A<n>``/``F<n>`` origin exists in ``## Nas suas palavras``
  PIC-008  ``Covers:`` only on steps with non-N/A ``Tests:``, only citing
           requirements of the plan, never inside ``Traces:``; every
           requirement covered by at least one step

Plans in v1, v2 or without a version have nothing to check (exit 0).

``--phase game`` is the check /plan runs after each round of the language game,
before the retelling and the steps exist: it skips ``## Retradução`` (PIC-002,
PIC-006) and every step rule (PIC-008). The default ``--phase plan`` checks all.

Exit codes: 0 = no errors (warnings allowed), 1 = errors found, 2 = usage error.

Usage
-----
    python .claude/skills/scripts/check_plan_intent.py            # scan PLANS_DIR
    python .claude/skills/scripts/check_plan_intent.py <plan.md>
    python .claude/skills/scripts/check_plan_intent.py <plan.md> --json
    python .claude/skills/scripts/check_plan_intent.py <plan.md> --phase game

CHECK_PLUGIN_MANIFEST:
  name: Plan Intent (v3)
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
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

SCHEMA_VERSION = 1
PLAN_FORMAT_VERSION = 3
SECTIONS = ("Intenção", "Requisitos", "Casos de uso", "Retradução", "Nas suas palavras")
PHASES = ("plan", "game")
INTENT_LINES = ("Objetivo", "O que você vê no fim", "Não faz", "Pronto quando")
NO_CODE_PREFIX = "nenhum ("  # e.g. "nenhum (tarefa sem código)", "nenhum (jogo curto, item de roadmap)"

_VERSION_RE = re.compile(r"^plan_format_version:\s*(\d+)\s*$")
_H2_RE = re.compile(r"^##\s+(.+?)\s*$")
_STEP_RE = re.compile(r"^###\s+Step\s+\d+")
# Any REQ-like token, to catch malformed plan IDs; plan IDs are lowercase.
_ANY_REQ_RE = re.compile(r"REQ-[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*-\d{3}")
_PLAN_REQ_RE = re.compile(r"REQ-[a-z0-9]+(?:-[a-z0-9]+)*-\d{3}")
_REQ_LINE_RE = re.compile(r"^-\s+(REQ-[A-Za-z0-9-]+?-\d{3})(\s*\(restrição\))?\s*:\s*(.*)$")
_ORIGIN_RE = re.compile(r"\(([^()]*)\)\s*$")
_ORIGIN_TOKEN_RE = re.compile(r"\b([AF]\d+)\b|\bteto\b")
_WORDS_INDEX_RE = re.compile(r"^-?\s*\**([AF]\d+)\**\b")
_FIELD_RE = re.compile(r"^-\s+\*\*(Tests|Covers|Traces)\*\*:\s*(.*)$")


def _finding(severity: str, rule: str, message: str, line: int | None = None) -> dict:
    return {"severity": severity, "rule": rule, "message": message, "line": line}


def plan_version(lines: list[str]) -> int | None:
    for raw in lines[:10]:
        m = _VERSION_RE.match(raw.strip())
        if m:
            return int(m.group(1))
    return None


def split_sections(lines: list[str]) -> dict[str, tuple[int, list[str]]]:
    """Map each H2 title to (1-based line of the heading, body lines)."""
    sections: dict[str, tuple[int, list[str]]] = {}
    current: str | None = None
    for i, raw in enumerate(lines, start=1):
        m = _H2_RE.match(raw)
        if m:
            current = m.group(1)
            sections[current] = (i, [])
        elif current is not None:
            sections[current][1].append(raw)
    return sections


def _content(body: list[str]) -> list[str]:
    return [b.strip() for b in body if b.strip()]


def _check_sections(sections: dict, findings: list[dict], phase: str) -> None:
    for name in SECTIONS:
        if phase == "game" and name == "Retradução":
            continue
        if name not in sections:
            findings.append(_finding("error", "PIC-002", f"seção ausente: ## {name}"))
        elif not _content(sections[name][1]):
            findings.append(
                _finding("error", "PIC-002", f"seção vazia: ## {name}", sections[name][0])
            )


def _check_intencao(sections: dict, findings: list[dict]) -> None:
    if "Intenção" not in sections:
        return
    start, body = sections["Intenção"]
    text = "\n".join(body)
    for label in INTENT_LINES:
        if not re.search(rf"^-\s+{re.escape(label)}:\s*\S", text, re.MULTILINE):
            findings.append(_finding("error", "PIC-003", f"## Intenção sem a linha '{label}:'", start))


def _no_code(sections: dict, name: str) -> bool:
    content = _content(sections[name][1]) if name in sections else []
    return len(content) == 1 and content[0].startswith(NO_CODE_PREFIX)


def _parse_requirements(sections: dict, findings: list[dict]) -> dict[str, list[str]]:
    """Return {req_id: [origins]} and record PIC-004 findings."""
    reqs: dict[str, list[str]] = {}
    if "Requisitos" not in sections or _no_code(sections, "Requisitos"):
        return reqs
    start, body = sections["Requisitos"]
    for offset, raw in enumerate(body, start=start + 1):
        line = raw.strip()
        m = _REQ_LINE_RE.match(line)
        if not m:
            if line:
                findings.append(
                    _finding("error", "PIC-004", f"linha mal formada em ## Requisitos: {line[:60]}", offset)
                )
            continue
        rid, rest = m.group(1), m.group(3)
        if not _PLAN_REQ_RE.fullmatch(rid):
            findings.append(
                _finding("error", "PIC-004", f"{rid}: ID fora do formato REQ-<slug>-NNN com slug minúsculo", offset)
            )
            continue
        if rid in reqs:
            findings.append(_finding("error", "PIC-004", f"{rid}: ID duplicado", offset))
            continue
        if "Para que:" not in rest:
            findings.append(_finding("error", "PIC-004", f"{rid}: sem 'Para que:'", offset))
        om = _ORIGIN_RE.search(rest)
        origins = _ORIGIN_TOKEN_RE.findall(om.group(1)) if om else []
        if not om or not (origins or "teto" in om.group(1)):
            findings.append(_finding("error", "PIC-004", f"{rid}: sem origem (A<n>, F<n> ou teto)", offset))
        if not rest.split("Para que:")[0].strip(" .()"):
            findings.append(_finding("error", "PIC-004", f"{rid}: sem a frase do requisito", offset))
        reqs[rid] = [o for o in origins if o]
    numbers = sorted(int(rid.rsplit("-", 1)[1]) for rid in reqs)
    if numbers and numbers != list(range(1, len(numbers) + 1)):
        findings.append(
            _finding("error", "PIC-004", "IDs de requisito não são contíguos de 001 a N", start)
        )
    return reqs


def _check_use_cases(sections: dict, reqs: dict, findings: list[dict]) -> None:
    if "Casos de uso" not in sections or _no_code(sections, "Casos de uso"):
        return
    start, body = sections["Casos de uso"]
    seen: set[str] = set()
    for offset, raw in enumerate(body, start=start + 1):
        line = raw.strip()
        cited = _PLAN_REQ_RE.findall(line)
        if line.startswith(("-", "*")) and not cited:
            findings.append(_finding("error", "PIC-005", f"caso de uso sem ID de requisito: {line[:60]}", offset))
        for rid in cited:
            seen.add(rid)
            if rid not in reqs:
                findings.append(
                    _finding("error", "PIC-005", f"caso de uso cita {rid}, que não está em ## Requisitos", offset)
                )
    for rid in reqs:
        if rid not in seen:
            findings.append(_finding("error", "PIC-005", f"{rid}: requisito sem caso de uso", start))


def _check_retelling(sections: dict, findings: list[dict]) -> None:
    if "Retradução" not in sections:
        return
    start, body = sections["Retradução"]
    text = "\n".join(body)
    if "O que eu não vou fazer" not in text:
        findings.append(_finding("error", "PIC-006", "## Retradução sem 'O que eu não vou fazer'", start))
    if not re.search(r"^\s*Aprovação:\s*\S", text, re.MULTILINE):
        findings.append(_finding("warning", "PIC-006", "## Retradução ainda sem a linha 'Aprovação:'", start))


def _check_origins(sections: dict, findings: list[dict]) -> None:
    if "Nas suas palavras" not in sections:
        return
    indexed = {
        m.group(1)
        for raw in sections["Nas suas palavras"][1]
        if (m := _WORDS_INDEX_RE.match(raw.strip()))
    }
    for name in ("Intenção", "Requisitos", "Casos de uso"):
        if name not in sections:
            continue
        start, body = sections[name]
        for offset, raw in enumerate(body, start=start + 1):
            om = _ORIGIN_RE.search(raw.strip())
            if not om:
                continue
            for tok in re.findall(r"\b[AF]\d+\b", om.group(1)):
                if tok not in indexed:
                    findings.append(
                        _finding("error", "PIC-007", f"origem {tok} não está em ## Nas suas palavras", offset)
                    )


def _parse_steps(lines: list[str]) -> list[dict]:
    steps: list[dict] = []
    for i, raw in enumerate(lines, start=1):
        if _STEP_RE.match(raw):
            steps.append({"title": raw.strip("# ").strip(), "line": i, "fields": {}})
        elif steps and _H2_RE.match(raw):
            steps.append({"title": None, "line": i, "fields": {}})  # end of steps
        elif steps and steps[-1]["title"] is not None:
            m = _FIELD_RE.match(raw.strip())
            if m:
                steps[-1]["fields"][m.group(1)] = (m.group(2), i)
    return [s for s in steps if s["title"] is not None]


def _check_covers(lines: list[str], reqs: dict, findings: list[dict]) -> None:
    covered: set[str] = set()
    for step in _parse_steps(lines):
        fields = step["fields"]
        tests = fields.get("Tests", ("", step["line"]))[0].strip()
        tests_na = not tests or tests.upper().startswith("N/A")
        if reqs and not tests_na and "Covers" not in fields:
            findings.append(
                _finding("error", "PIC-008", f"{step['title']}: Tests: sem Covers:", fields["Tests"][1])
            )
        if "Covers" in fields:
            value, line = fields["Covers"]
            if tests_na:
                findings.append(
                    _finding("error", "PIC-008", f"{step['title']}: Covers: num step com Tests: N/A", line)
                )
            for rid in _ANY_REQ_RE.findall(value):
                if rid in reqs:
                    covered.add(rid)
                else:
                    findings.append(
                        _finding("error", "PIC-008", f"{step['title']}: Covers: cita {rid}, que não está em ## Requisitos", line)
                    )
        if "Traces" in fields:
            value, line = fields["Traces"]
            for rid in _PLAN_REQ_RE.findall(value):
                findings.append(
                    _finding("error", "PIC-008", f"{step['title']}: {rid} dentro de Traces:; use Covers:", line)
                )
    for rid in reqs:
        if rid not in covered:
            findings.append(_finding("error", "PIC-008", f"{rid}: nenhum step o cobre com Covers:"))


def check_plan(path: Path, phase: str = "plan") -> dict:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as err:
        return {
            "path": str(path),
            "version": None,
            "skipped": False,
            "findings": [_finding("error", "PIC-001", f"plano ilegível: {err}")],
        }
    version = plan_version(lines)
    result = {"path": str(path), "version": version, "findings": [], "skipped": False}
    if version != PLAN_FORMAT_VERSION:
        result["skipped"] = True
        return result
    findings: list[dict] = result["findings"]
    sections = split_sections(lines)
    _check_sections(sections, findings, phase)
    _check_intencao(sections, findings)
    reqs = _parse_requirements(sections, findings)
    _check_use_cases(sections, reqs, findings)
    if phase != "game":
        _check_retelling(sections, findings)
    _check_origins(sections, findings)
    if phase != "game":
        _check_covers(lines, reqs, findings)
    return result


def _default_plans_dir() -> Path:
    from project_config import REPO_ROOT, get_path

    return get_path("PLANS_DIR") or (REPO_ROOT / "_output" / "plans")


def _is_primary_plan(path: Path) -> bool:
    name = path.name
    return name.startswith("plan-") and not name.endswith("-progress.md") and "-qa-" not in name


def _targets(plan: Path | None) -> list[Path]:
    if plan is not None:
        return [plan]
    plans_dir = _default_plans_dir()
    if not plans_dir.is_dir():
        return []
    return sorted(p for p in plans_dir.glob("plan-*.md") if _is_primary_plan(p))


def run(paths: list[Path], phase: str = "plan") -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "phase": phase,
        "plans": [check_plan(p, phase) for p in paths],
    }


def _print_text(report: dict) -> None:
    checked = [p for p in report["plans"] if not p["skipped"]]
    if not checked:
        print("check_plan_intent: nada a verificar (nenhum plano v3)")
        return
    for plan in checked:
        errors = [f for f in plan["findings"] if f["severity"] == "error"]
        warnings = [f for f in plan["findings"] if f["severity"] == "warning"]
        print(f"{plan['path']}: {len(errors)} error(s), {len(warnings)} warning(s)")
        for f in plan["findings"]:
            where = f":{f['line']}" if f["line"] else ""
            print(f"  [{f['severity'].upper()}] {f['rule']}{where} -- {f['message']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check the plan v3 shape (PIC rules)")
    parser.add_argument("plan", nargs="?", type=Path, help="plan file (default: scan PLANS_DIR)")
    parser.add_argument("--json", action="store_true", help="JSON output with schema_version")
    parser.add_argument(
        "--phase", choices=PHASES, default="plan",
        help="game: during the language game, before the retelling and the steps (default: plan)",
    )
    args = parser.parse_args(argv)
    if args.plan is not None and not args.plan.is_file():
        parser.error(f"plan not found: {args.plan}")

    report = run(_targets(args.plan), args.phase)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        _print_text(report)
    has_error = any(f["severity"] == "error" for p in report["plans"] for f in p["findings"])
    return 1 if has_error else 0


if __name__ == "__main__":
    sys.exit(main())
