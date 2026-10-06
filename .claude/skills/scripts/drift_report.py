#!/usr/bin/env python3
# designer: When you reflect on a feature, I show where its intent got lost, one
#   step of the ladder at a time: requirement to scenario, scenario to test,
#   test to code. I count what each step covers and what it does not, and I
#   say what I could not measure and why, next to the numbers. I compare the
#   state at delivery with the state now. I only describe what happened. I
#   never block, never judge whether a scenario captures a requirement, and
#   never tell you what to do.
"""
drift_report.py -- Divergence report per step of the ladder (DRP-001 to DRP-019).

Invocation: skill-invoked, user-cli
Lifecycle: active

Rules: .claude/references/general/drift-report.md (DRP-NNN) and
.claude/references/general/drift-metric.md (DRM-NNN). Standard library only; no
LLM, no network. Three separate layers:

  1. `load_matrix`   joins the sources of `features/<slug>/` into a matrix.
  2. `compute_report` pure function: matrix -> vector (D1, D2, D3a, D3b).
  3. `render_*`      fixed-sentence renderers (power dev, citizen, HTML).

| Rule    | What it settles                                                      |
|---------|----------------------------------------------------------------------|
| DRP-001 | sources, paths, what a missing source means (not measured, never error) |
| DRP-002 | derived columns, scenario key, Scenario Outline = worst row            |
| DRP-003 | `check_specify.py --status` is always consulted (stale -> D1 not measured) |
| DRP-004 | not-measured codes (NM-*) and their sentences                          |
| DRP-005 | D = descobertos / (cobertos + descobertos); zero denominator = "n/a"   |
| DRP-006 | populations and states per step; chain of a requirement                |
| DRP-007 | M1, M2 and the delta                                                   |
| DRP-008 | snapshots (atomic write, M1 never overwritten)                         |
| DRP-009 | semantic audit apart from D (audit.json, deterministic sample)         |
| DRP-010 | retranslation after the code, side by side                             |
| DRP-011 | readings outside D (orphans, closed ladder, D0, no-fail evidence)      |
| DRP-012 | proof label on every item                                              |
| DRP-013 | two registers: power dev (full) and citizen (no technical number)      |
| DRP-014 | reverse reading after the adoption mark                                |
| DRP-015 | report format, highlight, regenerated as-coded                         |
| DRP-016 | non-prescriptive wording                                               |
| DRP-017 | degradation and compatibility                                          |
| DRP-018 | anti-gaming                                                            |
| DRP-019 | what the report never does                                             |

Source -> column -> reason (DRP-001):

| Source                                   | Column            | If missing                  |
|------------------------------------------|-------------------|-----------------------------|
| check_features --matrix --json           | REQ, scenario     | no features/: not applicable |
| check_specify --feature s --status --json| scenario_status   | approval not verified        |
| runner/cucumber.json                     | test_result       | NM-SEM-RUNNER                |
| gate.json                                | full, baseline    | NM-SEM-GATE                  |
| drift/red-reason.json                    | red_reason_ok     | NM-SEM-REGISTRO-VERMELHO     |
| drift/coverage.json                      | touched_*         | NM-SEM-COBERTURA / -BASE-DIFF|
| check_intent --d0                        | D0                | NM-SEM-INDICE-BRIEF          |

Exit codes:
  0 = report produced (even with high divergence; the gate blocks, not this script).
  2 = usage error, unreadable or invalid input, M1 already frozen. Never a traceback.

Usage
-----
    python .claude/skills/scripts/drift_report.py --feature <slug> [--plan <plano.md>] --moment M2 --compare --md
    python .claude/skills/scripts/drift_report.py --feature <slug> --freeze --moment M1 --at 2026-10-06T18:00:00Z
    python .claude/skills/scripts/drift_report.py --feature <slug> --audit-sample
    python .claude/skills/scripts/drift_report.py [raiz] --json | --md | --citizen | --html
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
STEPS = ("D1", "D2", "D3a", "D3b")
MAX_SENTENCE_WORDS = 25
MAX_SENTENCES_PER_PARAGRAPH = 6
SMALL_SAMPLE = 8
AUDIT_PCT = 30

#: DRM-009 / DRP-004, in catalog order.
NM_CATALOG = (
    "NM-INTENCAO-NAO-APROVADA",
    "NM-SPECIFY-PULADA",
    "NM-CENARIOS-STALE",
    "NM-SEM-ADAPTADOR-RUNNER",
    "NM-SEM-RUNNER",
    "NM-SEM-ADAPTADOR-GATE",
    "NM-SEM-GATE",
    "NM-SEM-REGISTRO-VERMELHO",
    "NM-SEM-COBERTURA",
    "NM-SEM-BASE-DIFF",
    "NM-SEM-M1",
    "NM-SEM-INDICE-BRIEF",
    "NM-SEM-RETRADUCAO-POS-CODIGO",
    "NM-SEM-MARCA-ADOCAO",
)

NM_SENTENCE = {
    "NM-INTENCAO-NAO-APROVADA": "Eu não medi: você ainda não aprovou os requisitos.",
    "NM-SPECIFY-PULADA": "Eu não medi: esta tarefa não teve cenários.",
    "NM-CENARIOS-STALE": "Eu não medi: os cenários mudaram depois da aprovação.",
    "NM-SEM-ADAPTADOR-RUNNER": "Eu não medi: esta stack ainda não tem executor de cenários.",
    "NM-SEM-RUNNER": "Eu não medi: não achei o relatório dos testes.",
    "NM-SEM-ADAPTADOR-GATE": "Eu não medi: esta stack ainda não tem portão.",
    "NM-SEM-GATE": "Eu não medi: o portão não rodou por inteiro.",
    "NM-SEM-REGISTRO-VERMELHO": "Eu não medi: não há registro de que o teste falhou pelo motivo certo.",
    "NM-SEM-COBERTURA": "Eu não medi: não há cobertura só dos testes de cenário.",
    "NM-SEM-BASE-DIFF": "Eu não medi: não sei onde a feature começou.",
    "NM-SEM-M1": "Eu não medi a mudança: o estado da entrega não foi congelado.",
    "NM-SEM-INDICE-BRIEF": "Eu não medi o que sobrou do pedido: as frases do pedido não foram indexadas.",
    "NM-SEM-RETRADUCAO-POS-CODIGO": "Eu não medi: ainda não escrevi o que entendi depois do código.",
    "NM-SEM-MARCA-ADOCAO": "Eu não medi o que ficou sem feature: não sei desde quando o projeto usa features.",
}

#: DRP-016. Checked case-insensitively against every rendered text.
FORBIDDEN_PHRASES = (
    "deveria", "considere", "recomendamos", "você deve", "voce deve",
    "you should", "consider", "we recommend",
)

PROOF = {"D1": "arquivo", "D2": "ferramenta", "D3a": "ferramenta", "D3b": "ferramenta"}

RED_STATES = ("failed", "error", "undefined")
UNCOVERED_D2 = ("absent", "skipped", "xfail")


class DriftInputError(Exception):
    """An input file exists but cannot be read or is invalid (exit 2)."""

    def __init__(self, arquivo: str, motivo: str):
        super().__init__(f"{arquivo}: {motivo}")
        self.arquivo = arquivo
        self.motivo = motivo


class HtmlUnavailable(Exception):
    """Kept for the interface of the plan; the HTML renderer is built in."""


# ---------------------------------------------------------------------------
# Layer 2 -- pure calculator (no I/O, no LLM, no clock)
# ---------------------------------------------------------------------------


def format_d(num: int, den: int) -> float | str:
    """D = num / den with 4 decimals; zero denominator is "n/a", never 0 (DRP-005)."""
    return round(num / den, 4) if den else "n/a"


def _order(reasons: list[str]) -> list[str]:
    seen = set(reasons)
    return [code for code in NM_CATALOG if code in seen]


def _deg(cob: int, desc: int, nm: int, reasons: list[str]) -> dict[str, Any]:
    return {
        "n": cob + desc + nm,
        "cobertos": cob,
        "descobertos": desc,
        "nao_medidos": nm,
        "D": format_d(desc, cob + desc),
        "razao_nm": _order(reasons),
    }


def _gate_reason(gate: dict | None, *, need_full: bool) -> str | None:
    if gate is None:
        return "NM-SEM-GATE"
    if gate.get("adaptador") is False:
        return "NM-SEM-ADAPTADOR-GATE"
    if need_full and gate.get("full") is None:
        return "NM-SEM-GATE"
    return None


def _not_applicable(matrix: dict, razao: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "feature": matrix.get("feature"),
        "momento": matrix.get("momento"),
        "nao_aplicavel": True,
        "razao_nm": razao,
    }
    if matrix.get("motivo"):
        out["motivo"] = matrix["motivo"]
    return out


def analyze(matrix: dict) -> dict[str, Any]:
    """Everything the calculator knows: the DRM-007 report plus per-item states.

    Returns {"report": <DRM-007 dict>, "states": {...}} or the not-applicable
    short report under "report" with empty states.
    """
    intent_status = (matrix.get("intent") or {}).get("status")
    if matrix.get("nao_aplicavel"):
        return {"report": _not_applicable(matrix, list(matrix.get("razao_nm", []))), "states": {}}
    if intent_status == "skipped":
        return {"report": _not_applicable(matrix, ["NM-SPECIFY-PULADA"]), "states": {}}

    reqs: list[str] = list(matrix.get("reqs", []))
    retired = set(matrix.get("reqs_retirados", []))
    scenarios: list[dict] = list(matrix.get("scenarios", []))
    req_set = set(reqs)
    known = req_set | retired
    runner = matrix.get("runner") or {"adaptador": True, "relatorio": True}
    gate = matrix.get("gate")
    flags: dict[str, bool] = {}

    # --- D1 (DRM-002; DRP-003)
    if intent_status != "approved":
        d1_reason = "NM-INTENCAO-NAO-APROVADA"
    elif matrix.get("scenarios_status", "approved") != "approved":
        d1_reason = "NM-CENARIOS-STALE"
    else:
        d1_reason = ""
    tagged = {t for s in scenarios for t in s.get("tags", [])}
    d1_state = {r: ("nm" if d1_reason else ("cob" if r in tagged else "desc")) for r in reqs}

    # --- scenarios inside D (valid tag) and outside (orphan, no tag)
    in_d = [s for s in scenarios if any(t in req_set for t in s.get("tags", []))]
    sem_tag = [s for s in scenarios if not s.get("tags")]
    orfaos = [s for s in scenarios if any(t not in known for t in s.get("tags", []))]

    # --- D2 (DRM-003)
    d2_state: dict[str, str] = {}
    d2_reason: dict[str, list[str]] = {}
    for s in in_d:
        sid = s["id"]
        if runner.get("adaptador") is False:
            d2_state[sid], d2_reason[sid] = "nm", ["NM-SEM-ADAPTADOR-RUNNER"]
        elif runner.get("relatorio") is False:
            d2_state[sid], d2_reason[sid] = "nm", ["NM-SEM-RUNNER"]
        elif s.get("disabled") or s.get("test_result") in UNCOVERED_D2:
            d2_state[sid], d2_reason[sid] = "desc", []
        else:
            d2_state[sid], d2_reason[sid] = "cob", []

    # --- D3a (DRM-004, DRP-006 items 3 and 4)
    full = (gate or {}).get("full") if gate else None
    baseline = (gate or {}).get("baseline_moved") if gate else None
    gate_reason = _gate_reason(gate, need_full=True)
    d3a_state: dict[str, str] = {}
    d3a_reason: dict[str, list[str]] = {}
    for s in in_d:
        sid = s["id"]
        if d2_state[sid] == "desc":
            continue
        if d2_state[sid] == "nm":
            reasons = list(d2_reason[sid]) + ([gate_reason] if gate_reason else [])
            d3a_state[sid], d3a_reason[sid] = "nm", reasons
            continue
        red = s.get("red_reason_ok")
        if s.get("test_result") in RED_STATES or full == "FAIL":
            d3a_state[sid], d3a_reason[sid] = "desc", []
        elif full == "PASS_WITH_BASELINE" or baseline is True:
            d3a_state[sid], d3a_reason[sid] = "desc", []
            flags["baseline aceito"] = True
        elif red is False:
            d3a_state[sid], d3a_reason[sid] = "desc", []
        else:
            reasons = [gate_reason] if gate_reason else []
            if red is None:
                reasons.append("NM-SEM-REGISTRO-VERMELHO")
                flags["D3a sem prova de vermelho"] = True
            if reasons:
                d3a_state[sid], d3a_reason[sid] = "nm", reasons
            else:
                d3a_state[sid], d3a_reason[sid] = "cob", []
                if gate is not None and baseline is None:
                    flags["baseline não verificado"] = True

    # --- D3b (DRM-005)
    touched = matrix.get("touched")
    gate_b = _gate_reason(gate, need_full=False)
    if touched is None or touched.get("total") is None:
        d3b = _deg(0, 0, 0, ([gate_b] if gate_b else []) + ["NM-SEM-BASE-DIFF"])
    else:
        total, unc = touched["total"], touched.get("uncovered")
        reasons = ([gate_b] if gate_b else []) + (["NM-SEM-COBERTURA"] if unc is None else [])
        if reasons:
            d3b = _deg(0, 0, total, reasons)
        else:
            d3b = _deg(total - unc, unc, 0, [])

    def tally(state: dict[str, str], reason: dict[str, list[str]]) -> dict[str, Any]:
        cob = sum(1 for v in state.values() if v == "cob")
        desc = sum(1 for v in state.values() if v == "desc")
        nm_ids = [k for k, v in state.items() if v == "nm"]
        reasons = [x for k in nm_ids for x in reason.get(k, [])]
        return _deg(cob, desc, len(nm_ids), reasons)

    degraus = {
        "D1": _deg(
            sum(1 for v in d1_state.values() if v == "cob"),
            sum(1 for v in d1_state.values() if v == "desc"),
            sum(1 for v in d1_state.values() if v == "nm"),
            [d1_reason] if d1_reason else [],
        ),
        "D2": tally(d2_state, d2_reason),
        "D3a": tally(d3a_state, d3a_reason),
        "D3b": d3b,
    }

    # --- chain of a requirement (DRP-006 item 6)
    by_req: dict[str, list[str]] = {r: [] for r in reqs}
    for s in in_d:
        for t in s.get("tags", []):
            if t in by_req:
                by_req[t].append(s["id"])
    complete = 0
    undecided: list[str] = []
    for r, ids in by_req.items():
        if not ids:
            continue
        marks = [(d2_state[i], d3a_state.get(i)) for i in ids]
        if all(a == "cob" and b == "cob" for a, b in marks):
            complete += 1
        elif not any(a == "desc" or b == "desc" for a, b in marks):
            undecided.append(r)

    # --- readings outside D (DRM-008)
    oracle = matrix.get("oraculo")
    o1: dict[str, Any] | None = None
    if oracle:
        o1 = {"n": oracle["n"], "falham": oracle["falham"], "O1": format_d(oracle["falham"], oracle["n"])}
    audit_no = any(a.get("adequado") == "nao" for a in matrix.get("auditoria", []))
    d_zero = all(degraus[s]["D"] == 0 for s in ("D1", "D2", "D3a"))
    o1_positive = bool(o1) and isinstance(o1["O1"], float) and o1["O1"] > 0
    leituras = {
        "cadeia_completa": complete,
        "cenarios_orfaos": len(orfaos),
        "cenarios_sem_tag": len(sem_tag),
        "escada_fechou_sem_capturar": bool(d_zero and (o1_positive or audit_no)),
        "o1": o1,
        "d0": matrix.get("d0") or {"estado": "nao_medido", "razao_nm": ["NM-SEM-INDICE-BRIEF"]},
    }

    # --- caveats (DRP-018 and friends)
    ressalvas: list[str] = []
    if 0 < len(reqs) < SMALL_SAMPLE:
        ressalvas.append("amostra pequena")
    for text in ("D3a sem prova de vermelho", "baseline aceito", "baseline não verificado"):
        if flags.get(text):
            ressalvas.append(text)
    ressalvas += [r for r in matrix.get("ressalvas", []) if r not in ressalvas]

    report = {
        "schema_version": SCHEMA_VERSION,
        "feature": matrix["feature"],
        "momento": matrix["momento"],
        "degraus": degraus,
        "leituras": leituras,
        "ressalvas": ressalvas,
    }
    states = {
        "D1": d1_state, "D2": d2_state, "D3a": d3a_state, "by_req": by_req,
        "undecided": undecided, "in_d": [s["id"] for s in in_d], "orfaos": [s["id"] for s in orfaos],
        "sem_tag": [s["id"] for s in sem_tag],
    }
    return {"report": report, "states": states}


def compute_report(matrix: dict) -> dict[str, Any]:
    """Pure function: matrix -> the DRM-007 report (vector per step). No I/O, no LLM."""
    return analyze(matrix)["report"]


# ---------------------------------------------------------------------------
# Layer 1 -- loader (sources -> matrix). Missing source = not measured, never error.
# ---------------------------------------------------------------------------

_SCRIPTS_DIR = Path(__file__).resolve().parent
_ID_ANY = r"REQ-[a-z0-9]+(?:-[a-z0-9]+)*-\d{3}"
_STEP_WORDS = ("given", "when", "then", "and", "but", "dado", "quando", "então", "e", "mas", "*")
_SCENARIO_STOP = ("@", "scenario", "cenário", "cenario", "esquema", "examples", "exemplos",
                  "rule", "regra", "feature", "funcionalidade", "background", "contexto")
_DISABLED_TAGS = ("skip", "wip", "ignore")
_CUCUMBER_PRIORITY = ("error", "failed", "undefined", "skipped", "passed")

RunFn = Callable[[list[str]], tuple[int, str, str]]
StatusFn = Callable[[Path, str], "str | None"]


def read_text(path: Path) -> str:
    """UTF-8 (BOM tolerated). Unreadable -> DriftInputError, never a traceback."""
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        raise DriftInputError(str(path), f"não consegui ler ({type(exc).__name__})") from exc


def read_json(path: Path) -> Any:
    text = read_text(path)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise DriftInputError(str(path), f"JSON inválido (linha {exc.lineno})") from exc


def sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise DriftInputError(str(path), "não consegui ler") from exc


def run_script(argv: list[str], timeout: int = 60) -> tuple[int, str, str]:
    """Run a sibling script with the current interpreter: list of args, no shell."""
    try:
        done = subprocess.run(
            [sys.executable, *argv], capture_output=True, text=True, timeout=timeout, check=False, encoding="utf-8")
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 2, "", f"{type(exc).__name__}: {exc}"
    return done.returncode, done.stdout, done.stderr


def _frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    out: dict[str, str] = {}
    if not lines or lines[0].strip() != "---":
        return out
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out


def _sections(text: str) -> dict[str, list[str]]:
    """Level-2 sections by lowercase title; fenced blocks do not start a section."""
    out: dict[str, list[str]] = {}
    cur: list[str] | None = None
    fence = False
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fence = not fence
        if not fence and line.startswith("## "):
            cur = out.setdefault(line[3:].strip().lower(), [])
            continue
        if cur is not None:
            cur.append(line)
    return out


def _cells(line: str) -> list[str]:
    parts = [c.strip() for c in line.strip().strip("|").split("|")]
    return parts


def _table(lines: list[str]) -> list[dict[str, str]]:
    rows = [ln for ln in lines if ln.strip().startswith("|")]
    if len(rows) < 2:
        return []
    head = [h.lower() for h in _cells(rows[0])]
    out = []
    for ln in rows[2:]:
        cells = _cells(ln)
        out.append({head[i]: cells[i] for i in range(min(len(head), len(cells)))})
    return out


def parse_intent(text: str) -> dict[str, Any]:
    """The few parts of intent.md the report shows (DRP-010, DRP-011, DRP-014)."""
    fm = _frontmatter(text)
    sec = _sections(text)
    phrases: dict[str, str] = {}
    for line in sec.get("nas suas palavras", []):
        m = re.match(r'^\s*-\s*([FA]\d+)\b[^:]*:\s*"?(.*?)"?\s*$', line)
        if m:
            phrases[m.group(1)] = m.group(2)
    reqs: dict[str, dict[str, Any]] = {}
    for row in _table(sec.get("requisitos", [])):
        rid = row.get("req", "").strip("` ")
        if not re.fullmatch(_ID_ANY, rid):
            continue
        refs = re.findall(r"\bF\d+\b", row.get("nas suas palavras", ""))
        reqs[rid] = {"texto": row.get("requisito") or row.get("texto", ""), "frases": refs,
                     "estado": row.get("estado", "ativo") or "ativo"}
    retr: dict[str, str] = {}
    for line in sec.get("retradução", []):
        m = re.match(rf"^\s*-\s+(.*)\s\(({_ID_ANY})\)\s*$", line)
        if m:
            retr[m.group(2)] = m.group(1).strip()
    scope = [ln for ln in sec.get("fora do escopo", []) if re.match(r"^\s*-\s+\S", ln)]
    serve = [s.strip() for s in fm.get("serve", "").strip("[]").split(",") if s.strip()]
    return {"status": fm.get("status", ""), "serve": serve, "frases": phrases, "reqs": reqs,
            "retraducao": retr, "fora_escopo": len(scope)}


def parse_post_code(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(rf"^\s*-\s+(.*)\s\(({_ID_ANY})\)\s*$", line)
        if m:
            out[m.group(2)] = m.group(1).strip()
    return out


def _plan_header(plan: Path) -> dict[str, Any]:
    lines = read_text(plan).splitlines()
    head = []
    for ln in lines[1:]:
        if ln.startswith("## "):
            break
        head.append(ln)
    version, specify = 1, ""
    for ln in head:
        m = re.match(r"^plan_format_version:\s*(\d+)", ln)
        if m:
            version = int(m.group(1))
        m = re.match(r"^Specify:\s*(.*)$", ln)
        if m and not specify:
            specify = m.group(1).strip()
    return {"version": version, "skipped": specify.startswith("skipped")}


def _count_steps(feature_file: Path, line: int) -> int:
    try:
        lines = feature_file.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeDecodeError):
        return 0
    n = 0
    for ln in lines[line:]:
        s = ln.strip()
        if not s:
            continue
        low = s.lower()
        if low.startswith(_SCENARIO_STOP):
            break
        if low.split(" ", 1)[0] in _STEP_WORDS:
            n += 1
    return n


def scenario_key(uri: str, name: str) -> str:
    """`<slug>/<file>::<name>` from the last two components of the report uri (CYC-027)."""
    parts = [p for p in uri.replace("\\", "/").split("/") if p]
    return f"{'/'.join(parts[-2:])}::{name}"


def _element_state(element: dict, n_steps: int, tags: list[str]) -> str:
    """Cucumber JSON element -> DRM-003 state (gherkin-spec-format.md section 8)."""
    names = {t.lstrip("@").lower() for t in tags}
    names |= {str(t.get("name", "")).lstrip("@").lower() for t in element.get("tags", [])}
    if "xfail" in names:
        return "xfail"
    steps = element.get("steps", [])
    statuses = [s.get("result", {}).get("status") for s in steps]
    failed = [s for s in steps if s.get("result", {}).get("status") == "failed"]
    if failed:
        message = failed[0]["result"].get("error_message", "")
        return "failed" if "AssertionError" in message else "error"
    if "ambiguous" in statuses:
        return "error"
    if "undefined" in statuses or "pending" in statuses:
        return "undefined"
    if statuses and all(s == "skipped" for s in statuses):
        return "skipped"
    if len(statuses) < n_steps:
        return "undefined"
    return "passed"


def runner_states(report: Any, expected: dict[str, dict]) -> tuple[dict[str, str], list[str]]:
    """State of every expected scenario key, and the keys the runner ran that no scenario owns."""
    rows: dict[str, list[str]] = {}
    orphans: list[str] = []
    if not isinstance(report, list):
        raise DriftInputError("cucumber.json", "o relatório deveria ser uma lista de features")
    for feature in report:
        for element in feature.get("elements", []):
            key = scenario_key(feature.get("uri", ""), element.get("name", ""))
            info = expected.get(key)
            if info is None:
                if key not in orphans:
                    orphans.append(key)
                continue
            rows.setdefault(key, []).append(_element_state(element, info["steps"], info["tags"]))
    states: dict[str, str] = {}
    for key, info in expected.items():
        if key not in rows:
            states[key] = "skipped" if {t.lower() for t in info["tags"]} & set(_DISABLED_TAGS) else "absent"
        elif "xfail" in rows[key]:
            states[key] = "xfail"
        else:
            states[key] = min(rows[key], key=_CUCUMBER_PRIORITY.index)
    return states, orphans


def default_status(root: Path, slug: str, *, scripts_dir: Path | None = None, run_fn: RunFn | None = None) -> str | None:
    """`check_specify.py --feature <slug> --status --json` -> approved|stale|draft|missing (DRP-003).

    None when check_specify.py does not exist (the caller adds the caveat).
    """
    script = (scripts_dir or _SCRIPTS_DIR) / "check_specify.py"
    if not script.is_file():
        return None
    rc, out, err = (run_fn or run_script)([str(script), str(root), "--feature", slug, "--status", "--json"])
    try:
        status = json.loads(out)["status"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise DriftInputError("check_specify.py", f"saída inválida (exit {rc}): {err.strip()[:80]}") from exc
    if status not in ("approved", "stale", "draft", "missing"):
        raise DriftInputError("check_specify.py", f"estado desconhecido: {status}")
    return status


def _matrix_from_features(root: Path, slug: str, scripts_dir: Path, run_fn: RunFn) -> dict[str, Any]:
    script = scripts_dir / "check_features.py"
    if not script.is_file():
        raise DriftInputError("check_features.py", "não achei o validador de features")
    rc, out, err = run_fn([str(script), str(root), "--feature", slug, "--json", "--matrix"])
    if rc not in (0, 1):
        raise DriftInputError("check_features.py", f"exit {rc}: {err.strip()[:80]}")
    try:
        return json.loads(out)
    except json.JSONDecodeError as exc:
        raise DriftInputError("check_features.py", "saída não é JSON") from exc


def _gate(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    raw = read_json(path)
    if not isinstance(raw, dict):
        raise DriftInputError(str(path), "deveria ser um objeto")
    full_raw = raw.get("full")
    full: str | None
    if full_raw is None:
        full = None
    else:
        category = full_raw.get("category") if isinstance(full_raw, dict) else str(full_raw)
        code = full_raw.get("exit_code") if isinstance(full_raw, dict) else None
        if category == "PASS_WITH_BASELINE":
            full = "PASS_WITH_BASELINE"
        elif category == "PASS" or code == 0:
            full = "PASS"
        else:
            full = "FAIL"
    out: dict[str, Any] = {"full": full, "baseline_moved": raw.get("baseline_moved")}
    if raw.get("adapter") is False:
        out["adaptador"] = False
    return out


def _source_files(fdir: Path) -> list[Path]:
    names = ["scenarios.lock.json", "intent.md", *sorted(p.name for p in fdir.glob("*.feature")), "gate.json",
             "runner/cucumber.json", "drift/red-reason.json", "drift/coverage.json", "drift/audit.json",
             "drift/oracle-result.json", "drift/retraducao-pos-codigo.md"]
    return [fdir / n for n in names if (fdir / n).is_file()]


def read_audit(path: Path) -> list[dict[str, Any]]:
    """audit.json -> items; a value outside {sim, parcial, nao} is an error naming the REQ (DRP-009)."""
    raw = read_json(path)
    items = raw.get("itens") if isinstance(raw, dict) else None
    if not isinstance(items, list):
        raise DriftInputError(str(path), "falta a lista `itens`")
    out = []
    for item in items:
        req = item.get("req", "?") if isinstance(item, dict) else "?"
        if not isinstance(item, dict) or item.get("adequado") not in ("sim", "parcial", "nao"):
            raise DriftInputError(str(path), f"{req}: `adequado` deve ser sim, parcial ou nao")
        if item.get("por", "humano") not in ("humano", "juiz"):
            raise DriftInputError(str(path), f"{req}: `por` deve ser humano ou juiz")
        out.append({"req": req, "adequado": item["adequado"], "por": item.get("por", "humano"),
                    "objeto": item.get("objeto", "cenario"), "nota": item.get("nota", "")})
    return out


def _reverse_reading(root: Path) -> dict[str, Any]:
    """DRP-014: intentions born after the adoption mark that no approved feature serves."""
    mark = root / "features" / "adoption.json"
    intended = root / "product-design" / "product-design-as-intended.md"
    if not mark.is_file() or not intended.is_file():
        return {"estado": "nao_medido", "ids": [], "razao_nm": ["NM-SEM-MARCA-ADOCAO"]}
    adopted = str(read_json(mark).get("adopted_at", ""))
    born: dict[str, str] = {}
    for line in read_text(intended).splitlines():
        m = re.match(r"^(\d{4}-\d{2}-\d{2})\s*\|\s*([A-Z0-9-]+)\s*\|\s*added\b", line)
        if m and re.fullmatch(r"REQ-[A-Z0-9]+-\d{3}|JM-TB-\d{3}", m.group(2)):
            born.setdefault(m.group(2), m.group(1))
    served: set[str] = set()
    for intent in sorted((root / "features").glob("*/intent.md")):
        info = parse_intent(read_text(intent))
        if info["status"] == "approved":
            served |= set(info["serve"])
    ids = sorted(i for i, d in born.items() if d >= adopted and i not in served)
    return {"estado": "medido", "ids": ids, "razao_nm": []}


def _na(slug: str, moment: str, motivo: str, razao: list[str] | None = None) -> dict[str, Any]:
    return {"feature": slug, "momento": moment, "nao_aplicavel": True, "motivo": motivo, "razao_nm": razao or []}


def load_matrix(
    root: Path, slug: str, *, plan: Path | None = None, moment: str = "M2",
    status_fn: StatusFn | None = None, run_fn: RunFn | None = None, scripts_dir: Path | None = None,
) -> dict[str, Any]:
    """Join the sources of `features/<slug>/` into the matrix `compute_report` reads (DRP-001)."""
    root = Path(root)
    scripts = Path(scripts_dir) if scripts_dir else _SCRIPTS_DIR
    run = run_fn or run_script
    if plan is not None:
        head = _plan_header(Path(plan))
        if head["version"] < 2:
            return _na(slug, moment, "plano-v1")
        if head["skipped"]:
            return {"feature": slug, "momento": moment, "intent": {"status": "skipped"}}
    if not (root / "features").is_dir():
        return _na(slug, moment, "sem-features")
    fdir = root / "features" / slug
    if not fdir.is_dir():
        return _na(slug, moment, "feature-sem-pasta")

    data = _matrix_from_features(root, slug, scripts, run)
    fmat = (data.get("matrix") or {}).get(slug)
    if fmat is None:
        return _na(slug, moment, "feature-sem-matriz")
    intent_info = parse_intent(read_text(fdir / "intent.md")) if (fdir / "intent.md").is_file() else parse_intent("")

    # requirements and scenarios from the matrix; one scenario may sit under several requirements
    reqs: list[str] = []
    retired: list[str] = []
    by_key: dict[str, dict[str, Any]] = {}
    for rid in sorted(fmat.get("reqs", {})):
        entry = fmat["reqs"][rid]
        (retired if entry.get("state") == "retirado" else reqs).append(rid)
        for sc in entry.get("scenarios", []):
            item = by_key.setdefault(sc["key"], {"id": sc["key"], "tags": [], "name": sc.get("name", ""),
                                                 "file": sc.get("file", ""), "line": sc.get("line", 0),
                                                 "disabled": bool(sc.get("disabled")),
                                                 "nao_faz": bool(sc.get("nao_faz"))})
            item["tags"].append(rid)
    for finding in data.get("findings", []):  # scenarios the matrix does not list under a requirement
        if finding.get("rule") in ("GHK-002", "GHK-004") and finding.get("scenario"):
            where = f"{finding.get('file')}:{finding.get('line')}"
            by_key.setdefault(where, {"id": where, "tags": [] if finding["rule"] == "GHK-002" else ["REQ-?-000"],
                                      "name": finding["scenario"], "file": finding.get("file", ""),
                                      "line": finding.get("line", 0), "disabled": False, "nao_faz": False})

    # DRP-003: the approval is always asked of check_specify, never read from the frontmatter
    ressalvas: list[str] = []
    asked = (status_fn or (lambda r, s: default_status(r, s, scripts_dir=scripts, run_fn=run)))(root, slug)
    if asked is None:
        scen_status = "approved"
        ressalvas.append("aprovação não verificada")
    else:
        scen_status = asked
        extra = {"stale": "cenários desatualizados", "draft": "cenários não aprovados",
                 "missing": "sem cenários aprovados"}.get(asked)
        if extra:
            ressalvas.append(extra)

    # runner
    adapter_file = fdir / "runner" / "adapter.json"
    runner = {"adaptador": True, "relatorio": False}
    if adapter_file.is_file() and read_json(adapter_file).get("adapter") is False:
        runner["adaptador"] = False
    report_file = fdir / "runner" / "cucumber.json"
    states: dict[str, str] = {}
    orphan_tests: list[str] = []
    if report_file.is_file():
        runner["relatorio"] = True
        expected = {}
        for key, sc in by_key.items():
            if "/" not in key or "::" not in key:
                continue
            steps = _count_steps(root / sc["file"], sc["line"]) if sc["file"] else 0
            expected[key] = {"steps": steps, "tags": ["skip"] if sc["disabled"] else []}
        try:
            states, orphan_tests = runner_states(read_json(report_file), expected)
        except DriftInputError as exc:
            raise DriftInputError(str(report_file), exc.motivo) from exc

    red_file = fdir / "drift" / "red-reason.json"
    red = read_json(red_file).get("scenarios", {}) if red_file.is_file() else {}
    scenarios = []
    for key, sc in by_key.items():
        scenarios.append({"id": key, "tags": sc["tags"], "test_result": states.get(key, "absent"),
                          "red_reason_ok": red.get(key), "disabled": sc["disabled"], "nao_faz": sc["nao_faz"],
                          "name": sc["name"]})

    cov_file = fdir / "drift" / "coverage.json"
    touched = None
    if cov_file.is_file():
        cov = read_json(cov_file)
        touched = {"total": cov.get("touched_total") if cov.get("base") else None,
                   "uncovered": cov.get("touched_uncovered")}
    oracle_file = fdir / "drift" / "oracle-result.json"
    oracle = None
    if oracle_file.is_file():
        raw = read_json(oracle_file)
        oracle = {"n": raw.get("n", 0), "falham": raw.get("falham", 0)}
    audit_file = fdir / "drift" / "audit.json"
    audit = read_audit(audit_file) if audit_file.is_file() else []

    d0: dict[str, Any] | None = None
    check_intent = scripts / "check_intent.py"
    if check_intent.is_file() and (fdir / "intent.md").is_file():
        rc, out, _ = run([str(check_intent), str(fdir / "intent.md"), "--d0"])
        try:
            d0 = json.loads(out)["d0"] if rc == 0 else None
        except (json.JSONDecodeError, KeyError, TypeError):
            d0 = None

    step_owner: dict[str, int] | None = None
    check_plan = scripts / "check_plan_scenarios.py"
    if plan is not None and check_plan.is_file():  # informative column; never part of the vector
        rc, out, _ = run([str(check_plan), str(plan), "--root", str(root), "--json"])
        try:
            parsed = json.loads(out) if rc in (0, 1) else {}
            step_owner = {k: s["n"] for s in parsed.get("steps", []) for k in s.get("scenarios", [])}
        except (json.JSONDecodeError, KeyError, TypeError):
            step_owner = None

    post_file = fdir / "drift" / "retraducao-pos-codigo.md"
    post = parse_post_code(read_text(post_file)) if post_file.is_file() else None
    entradas = {p.relative_to(root).as_posix(): sha256_file(p) for p in _source_files(fdir)}
    matrix: dict[str, Any] = {
        "feature": slug, "momento": moment,
        "intent": {"status": intent_info["status"] or fmat.get("status", "")},
        "scenarios_status": scen_status, "runner": runner, "gate": _gate(fdir / "gate.json"),
        "reqs": reqs, "reqs_retirados": retired, "scenarios": scenarios, "touched": touched,
        "oraculo": oracle, "auditoria": audit, "ressalvas": ressalvas,
        "extras": {"intent": intent_info, "post_codigo": post, "testes_orfaos": orphan_tests,
                   "entradas": entradas, "reversa": _reverse_reading(root),
                   "step_dono": step_owner},
    }
    if d0 is not None:
        matrix["d0"] = d0
    return matrix


# ---------------------------------------------------------------------------
# Report assembly: compute_report + what lives beside the vector (DRP-015)
# ---------------------------------------------------------------------------


def _audit_block(matrix: dict, reqs: list[str]) -> dict[str, Any]:
    items = matrix.get("auditoria", [])
    count = {k: sum(1 for i in items if i.get("adequado") == k) for k in ("sim", "parcial", "nao")}
    done = {i.get("req") for i in items if i.get("objeto", "cenario") == "cenario"}
    return {**count, "nao_auditados": [r for r in reqs if r not in done]}


def _retranslation_block(matrix: dict, reqs: list[str]) -> dict[str, Any]:
    extras = matrix.get("extras", {})
    intent = extras.get("intent", {"reqs": {}, "frases": {}, "retraducao": {}})
    post = extras.get("post_codigo")
    items = []
    for r in reqs:
        info = intent["reqs"].get(r, {})
        asked = [intent["frases"].get(f, "") for f in info.get("frases", []) if f in intent["frases"]]
        items.append({"req": r, "texto": info.get("texto", ""), "pedido": asked, "antes": intent["retraducao"].get(r, ""),
                      "depois": (post or {}).get(r, "")})
    if post is None:
        return {"estado": "nao_medido", "razao_nm": ["NM-SEM-RETRADUCAO-POS-CODIGO"], "itens": items}
    return {"estado": "medido", "razao_nm": [], "itens": items}


_TEST_WORD = {"passed": "passou", "failed": "falhou", "error": "deu erro", "undefined": "sem passo definido",
              "skipped": "pulado", "xfail": "falha esperada", "absent": "sem teste"}


def _as_coded_rows(matrix: dict, states: dict) -> list[dict[str, Any]]:
    """The as-coded of the feature, regenerated from the matrix (DRP-015): never edited by hand."""
    intent = matrix.get("extras", {}).get("intent", {"reqs": {}})
    rows = []
    for req in matrix.get("reqs", []):
        scs = [s for s in matrix.get("scenarios", []) if req in s.get("tags", [])]
        rows.append({
            "req": req, "texto": intent["reqs"].get(req, {}).get("texto", ""),
            "cenarios": [{"nome": s.get("name", s["id"]),
                          "teste": "desativado" if s.get("disabled") else _TEST_WORD.get(s.get("test_result"), "sem teste"),
                          "conferido": {"cob": "sim", "desc": "não", "nm": "não medido"}.get(
                              states["D3a"].get(s["id"]), "não se aplica")} for s in scs],
        })
    return rows


def build_report(matrix: dict, *, as_coded: bool = False) -> dict[str, Any]:
    """`compute_report` plus the blocks that sit beside the vector, never inside it (DRP-015)."""
    analysis = analyze(matrix)
    core = analysis["report"]
    if core.get("nao_aplicavel"):
        return core
    states = analysis["states"]
    extras = matrix.get("extras", {})
    reqs = list(matrix.get("reqs", []))
    names = {s["id"]: s.get("name", s["id"]) for s in matrix.get("scenarios", [])}
    intent = extras.get("intent", {"reqs": {}, "frases": {}})
    degraus = {k: {**v, "prova": PROOF[k]} for k, v in core["degraus"].items()}
    scope_items = (extras.get("intent") or {}).get("fora_escopo", 0)
    n_nao_faz = sum(1 for s in matrix.get("scenarios", []) if s.get("nao_faz"))
    leituras = dict(core["leituras"])
    d0 = dict(leituras["d0"])
    if d0.get("estado") == "medido":
        phrases = intent.get("frases", {})
        d0["residuo"] = [{**r, "texto": phrases.get(r.get("frase"), "")} for r in d0.get("residuo", [])]
    leituras["d0"] = d0
    leituras["cadeia_indeterminada"] = len(states["undecided"])
    leituras["testes_orfaos"] = len(extras.get("testes_orfaos", []))
    leituras["nao_faz"] = {"itens": scope_items, "cenarios": n_nao_faz, "sem_evidencia": max(0, scope_items - n_nao_faz)}
    leituras["intencao_sem_feature"] = extras.get(
        "reversa", {"estado": "nao_medido", "ids": [], "razao_nm": ["NM-SEM-MARCA-ADOCAO"]})
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION, "feature": core["feature"], "momento": core["momento"],
        "degraus": degraus, "leituras": leituras, "ressalvas": core["ressalvas"],
        "itens": {
            "reqs_descobertos": [{"req": r, "texto": intent["reqs"].get(r, {}).get("texto", "")}
                                 for r, v in states["D1"].items() if v == "desc"],
            "cenarios_descobertos": {
                "D2": [{"chave": k, "nome": names.get(k, k)} for k, v in states["D2"].items() if v == "desc"],
                "D3a": [{"chave": k, "nome": names.get(k, k)} for k, v in states["D3a"].items() if v == "desc"],
            },
        },
        "auditoria": _audit_block(matrix, reqs),
        "retraducao": _retranslation_block(matrix, reqs),
        "delta": None,
        "entradas": dict(sorted(extras.get("entradas", {}).items())),
    }
    if as_coded:
        report["as_coded"] = _as_coded_rows(matrix, states)
    return report


def _degree_side(deg: dict) -> dict[str, Any]:
    return {"num": deg["descobertos"], "den": deg["cobertos"] + deg["descobertos"], "D": deg["D"]}


def compare(m1: dict | None, m2: dict) -> dict[str, Any]:
    """M2 - M1 (DRP-007): numerator and denominator of both sides; the change only when both D are numbers."""
    if m1 is None:
        return {"estado": "nao_medido", "razao_nm": ["NM-SEM-M1"]}
    old = m1.get("report", {}).get("degraus", {})
    out: dict[str, Any] = {"estado": "medido", "razao_nm": [], "m1_em": m1.get("at")}
    for step in STEPS:
        if step not in old or step not in m2["degraus"]:
            continue
        a, b = _degree_side(old[step]), _degree_side(m2["degraus"][step])
        both = isinstance(a["D"], (int, float)) and isinstance(b["D"], (int, float))
        out[step] = {
            "m1": a, "m2": b,
            "mudanca": round(b["D"] - a["D"], 4) if both else None,
            "denominador": (f"o denominador mudou de {a['den']} para {b['den']}"
                            if a["den"] and b["den"] and a["den"] != b["den"] else None),
        }
    before = m1.get("entradas", {})
    now = m2.get("entradas", {})
    out["mudou"] = sorted(k for k in set(before) | set(now) if before.get(k) != now.get(k))
    return out


def snapshot(report: dict, at: str) -> dict[str, Any]:
    """The frozen form of a report (DRP-008): the report, the hash of every input, the given time."""
    body = {k: v for k, v in report.items() if k not in ("delta", "entradas")}
    return {"schema_version": SCHEMA_VERSION, "feature": report["feature"], "momento": report["momento"],
            "at": at, "report": body, "entradas": report.get("entradas", {})}


def snapshot_path(root: Path, slug: str, moment: str, at: str) -> Path:
    name = "M1.json" if moment == "M1" else f"M2-{at[:10]}.json"
    return Path(root) / "features" / slug / "drift" / name


def load_snapshot(root: Path, slug: str, moment: str = "M1") -> dict | None:
    path = snapshot_path(root, slug, moment, "")
    if moment != "M1" or not path.is_file():
        return None
    data = read_json(path)
    if not isinstance(data, dict) or "report" not in data:
        raise DriftInputError(str(path), "não é um instantâneo")
    return data


def freeze(report: dict, root: Path, slug: str, moment: str, at: str) -> Path:
    """Write the snapshot atomically; an existing M1 is never overwritten (DRP-008)."""
    if report.get("nao_aplicavel"):
        raise DriftInputError(slug, "não há o que congelar: relatório não aplicável")
    path = snapshot_path(root, slug, moment, at)
    if moment == "M1" and path.exists():
        raise FileExistsError(f"{path}: o M1 já foi congelado e não se sobrescreve")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(snapshot(report, at), ensure_ascii=False, indent=2) + "\n"
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".snap-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return path


def audit_sample(reqs: list[str], slug: str, pct: int = AUDIT_PCT) -> list[str]:
    """Deterministic blind sample (DRP-009): order by sha1(slug:req), take ceil(pct%)."""
    ordered = sorted(reqs, key=lambda r: hashlib.sha1(f"{slug}:{r}".encode()).hexdigest())
    return ordered[: -(-len(reqs) * pct // 100)]


def generate(
    root: Path, slug: str, *, plan: Path | None = None, moment: str = "M2", compare_m1: bool = False,
    status_fn: StatusFn | None = None, run_fn: RunFn | None = None, scripts_dir: Path | None = None,
    as_coded: bool = False,
) -> dict[str, Any]:
    """load_matrix -> build_report, with the M2 - M1 delta when asked (the whole pipeline of one feature)."""
    matrix = load_matrix(root, slug, plan=plan, moment=moment, status_fn=status_fn, run_fn=run_fn,
                         scripts_dir=scripts_dir)
    report = build_report(matrix, as_coded=as_coded)
    if compare_m1 and moment == "M2" and not report.get("nao_aplicavel"):
        report["delta"] = compare(load_snapshot(root, slug, "M1"), report)
    return report


# ---------------------------------------------------------------------------
# Layer 3 -- renderers: fixed sentences, no LLM (DRP-012, DRP-013, DRP-016)
# ---------------------------------------------------------------------------

STEP_LABEL = {"D1": "D1 intenção para cenário", "D2": "D2 cenário para teste",
              "D3a": "D3a teste para código (verdade)", "D3b": "D3b teste para código (excesso)"}
STEP_FACT = {
    "D1": "{d} de {n} requisitos sem cenário",
    "D2": "{d} de {n} cenários sem teste executado",
    "D3a": "{d} de {n} cenários com teste que não passa no código entregue",
    "D3b": "{d} de {n} linhas ou ramos tocados sem cenário que os exercite (código sem cenário: excesso)",
}
NA_LINES = {
    "sem-features": "Não aplicável: este projeto não tem features.",
    "plano-v1": "Não aplicável: este plano é do formato antigo.",
    "feature-sem-pasta": "Não aplicável: esta feature não tem pasta.",
    "feature-sem-matriz": "Não aplicável: esta feature não tem matriz.",
    "specify-pulado": "Não aplicável: esta tarefa não teve cenários.",
}
CAVEAT_TEXT = {
    "amostra pequena": "Poucos requisitos: os números valem como contagem, não como tendência.",
    "D3a sem prova de vermelho": "Não há prova de que o teste falhou antes do código, pelo motivo certo.",
    "baseline aceito": "Um limite de qualidade foi relaxado para o portão passar.",
    "baseline não verificado": "Eu não conferi se algum limite de qualidade foi relaxado.",
    "cenários desatualizados": "Os cenários mudaram depois da aprovação.",
    "cenários não aprovados": "Os cenários ainda não foram aprovados.",
    "sem cenários aprovados": "Ainda não há cenários aprovados.",
    "aprovação não verificada": "Eu não conferi se a aprovação dos cenários ainda vale.",
}
CITIZEN_CAVEAT = {
    "amostra pequena": "Foram poucos requisitos para tirar uma conclusão.",
    "D3a sem prova de vermelho": "Eu não tenho prova de que o teste falhou antes do código, pelo motivo certo.",
    "baseline aceito": "Um limite de qualidade foi relaxado para o teste passar.",
    "baseline não verificado": "Eu não conferi se algum limite de qualidade foi relaxado.",
    "cenários desatualizados": "Os cenários mudaram depois da aprovação.",
    "cenários não aprovados": "Os cenários ainda não foram aprovados.",
    "sem cenários aprovados": "Ainda não há cenários aprovados.",
    "aprovação não verificada": "Eu não conferi se a aprovação dos cenários ainda vale.",
}
_UNITS = ("zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze",
          "treze", "quatorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove")
_TENS = {2: "vinte", 3: "trinta", 4: "quarenta", 5: "cinquenta", 6: "sessenta", 7: "setenta", 8: "oitenta",
         9: "noventa"}


def words(n: int) -> str:
    """A count in words (masculine), for the citizen register; 100 or more is "muitos"."""
    if n < 20:
        return _UNITS[n]
    if n < 100:
        tens, unit = divmod(n, 10)
        return _TENS[tens] + (f" e {_UNITS[unit]}" if unit else "")
    return "muitos"


def check_voice(text: str) -> list[str]:
    """Voice limits (DRP-013): sentence <= 25 words, paragraph <= 6 sentences. Table rows are skipped."""
    problems = []
    for block in re.split(r"\n\s*\n", text):
        lines = [ln for ln in block.splitlines() if ln.strip() and not ln.lstrip().startswith(("|", "#"))]
        sentences = [s for ln in lines for s in re.split(r"(?<=[.!?])\s+", re.sub(r'"[^"]*"', "Q", re.sub(r"^\s*[-*]\s+", "", ln))) if s.strip()]
        if len(sentences) > MAX_SENTENCES_PER_PARAGRAPH and not any(ln.lstrip().startswith("-") for ln in lines):
            problems.append(f"parágrafo com {len(sentences)} frases: {sentences[0][:40]}")
        for s in sentences:
            if len(s.split()) > MAX_SENTENCE_WORDS:
                problems.append(f"frase com {len(s.split())} palavras: {s[:40]}")
    return problems


def _fd(value: Any) -> str:
    return f"{value:.2f}" if isinstance(value, (int, float)) else "n/a"


def _na_line(report: dict) -> str:
    motivo = report.get("motivo") or ""
    if not motivo and "NM-SPECIFY-PULADA" in report.get("razao_nm", []):
        motivo = "specify-pulado"
    return NA_LINES.get(motivo, "Não aplicável: não há o que medir aqui.")


def highlight(report: dict) -> str:
    """The step with the largest D, by text; a tie is said as a tie; never a sum (DRP-015)."""
    numeric = {s: report["degraus"][s] for s in STEPS if isinstance(report["degraus"][s]["D"], (int, float))}
    if not numeric:
        return "Nenhum degrau tinha itens para medir."
    top = max(d["D"] for d in numeric.values())
    if top == 0:
        return "Nenhum degrau tem divergência medida."
    winners = [s for s, d in numeric.items() if d["D"] == top]
    if len(winners) > 1:
        return f"Empate entre {' e '.join(winners)}."
    d = numeric[winners[0]]
    fact = STEP_FACT[winners[0]].format(d=d["descobertos"], n=d["cobertos"] + d["descobertos"])
    return f"O maior D está em {winners[0]}: {fact}."


def _nm_cell(deg: dict) -> str:
    if not deg["nao_medidos"] and not deg["razao_nm"]:
        return "0"
    return f"{deg['nao_medidos']} ({', '.join(deg['razao_nm'])})" if deg["razao_nm"] else str(deg["nao_medidos"])


def render_markdown(report: dict, *, at: str | None = None) -> str:
    """Power dev register: the whole vector, with proof labels and what was not measured (DRP-013)."""
    if report.get("nao_aplicavel"):
        return _na_line(report) + "\n"
    delta = report.get("delta") or {}
    measured = delta.get("estado") == "medido"
    out = [f"## Divergência por degrau ({report['feature']}, {report['momento']})", ""]
    out += ["| Degrau | n | Cobertos | Descobertos | Não medido (razão) | D | M1 | M2 | Mudança | Prova |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for step in STEPS:
        d = report["degraus"][step]
        m1 = m2 = chg = "-"
        if report["momento"] == "M1":
            m1 = _fd(d["D"])
        else:
            m2 = _fd(d["D"])
            if measured and step in delta:
                m1 = _fd(delta[step]["m1"]["D"])
                chg = f"{delta[step]['mudanca']:+.2f}" if delta[step]["mudanca"] is not None else "n/a"
        out.append(f"| {STEP_LABEL[step]} | {d['n']} | {d['cobertos']} | {d['descobertos']} | {_nm_cell(d)} "
                   f"| {_fd(d['D'])} | {m1} | {m2} | {chg} | prova: {d['prova']} |")
    out += ["", highlight(report), ""]
    nm_codes = [c for s in STEPS for c in report["degraus"][s]["razao_nm"]]
    for code in dict.fromkeys(nm_codes):
        out.append(f"- {NM_SENTENCE[code]}")
    if nm_codes:
        out.append("")
    if report["momento"] == "M2":
        if measured:
            for step in STEPS:
                if step in delta and delta[step]["denominador"]:
                    out.append(f"- {step}: {delta[step]['denominador']}.")
            if delta.get("mudou"):
                out.append("- Mudaram depois da entrega: " + ", ".join(delta["mudou"]) + ".")
            out.append("")
        elif delta:
            out += [NM_SENTENCE["NM-SEM-M1"], ""]
    items = report["itens"]
    if items["reqs_descobertos"]:
        out += ["Requisitos sem cenário: " + ", ".join(i["req"] for i in items["reqs_descobertos"]) + ".", ""]
    for step in ("D2", "D3a"):
        if items["cenarios_descobertos"][step]:
            label = "sem teste executado" if step == "D2" else "com teste que não passa no código entregue"
            out += [f"Cenários {label} ({step}):", ""]
            out += [f"- {i['nome']}" for i in items["cenarios_descobertos"][step]]
            out.append("")
    lei = report["leituras"]
    out += ["Leituras fora do D:", ""]
    if lei["cadeia_indeterminada"]:
        out.append(f"- Cadeia completa: {lei['cadeia_completa']} requisitos; {lei['cadeia_indeterminada']} "
                   "requisitos não medidos (falta teste ou portão).")
    else:
        out.append(f"- Cadeia completa: {lei['cadeia_completa']} requisitos.")
    for key, label in (("cenarios_orfaos", "Cenários com tag de requisito inexistente"),
                       ("cenarios_sem_tag", "Cenários sem tag"), ("testes_orfaos", "Testes sem cenário")):
        if lei[key]:
            out.append(f"- {label}: {lei[key]}.")
    if lei["escada_fechou_sem_capturar"]:
        out.append("- A escada fechou sem capturar a intenção: D1, D2 e D3a são zero e a auditoria ou o oráculo discorda.")
    nf = lei["nao_faz"]
    if nf["itens"]:
        out.append(f"- Fora do escopo: {nf['itens']} itens e {nf['cenarios']} cenários @nao-faz; "
                   f"{nf['sem_evidencia']} sem evidência (contagem por total, prova: arquivo).")
    d0 = lei["d0"]
    if d0["estado"] == "medido":
        left = ", ".join(r["frase"] for r in d0["residuo"]) or "nenhuma"
        out.append(f"- Do pedido: {d0['frases']} frases; sem requisito e sem fora do escopo: {left} (prova: arquivo).")
    else:
        out.append(f"- {NM_SENTENCE[d0['razao_nm'][0]]}")
    rev = lei["intencao_sem_feature"]
    if rev["estado"] == "medido":
        out.append("- Intenção nascida depois da adoção e sem feature: " + (", ".join(rev["ids"]) or "nenhuma") + ".")
    else:
        out.append(f"- {NM_SENTENCE['NM-SEM-MARCA-ADOCAO']}")
    if lei["o1"]:
        out.append(f"- Oráculo: {lei['o1']['falham']} de {lei['o1']['n']} falham (O1 {_fd(lei['o1']['O1'])}).")
    out.append("")
    aud = report["auditoria"]
    out += [(f"Auditoria (prova: humano): sim {aud['sim']}, parcial {aud['parcial']}, não {aud['nao']}; "
             f"sem auditar: {', '.join(aud['nao_auditados']) or 'nenhum'}. A auditoria não entra no D."), ""]
    retr = report["retraducao"]
    if retr["estado"] == "medido":
        out += ["Retradução depois do código, lado a lado (prova: humano julga):", "",
                "| Requisito | Você pediu | Eu entendi antes do código | Eu entendi depois do código |", "|---|---|---|---|"]
        for i in retr["itens"]:
            out.append(f"| {i['req']} | {' / '.join(i['pedido']) or '-'} | {i['antes'] or '-'} | {i['depois'] or '-'} |")
        out.append("")
    else:
        out += [NM_SENTENCE["NM-SEM-RETRADUCAO-POS-CODIGO"], ""]
    if report["ressalvas"]:
        out += ["Ressalvas:", ""] + [f"- {CAVEAT_TEXT.get(r, r)}" for r in report["ressalvas"]] + [""]
    if "as_coded" in report:
        out += ["### Como ficou (regenerado da matriz)", "", "| Requisito | Cenário | Teste | Conferido |", "|---|---|---|---|"]
        for row in report["as_coded"]:
            if not row["cenarios"]:
                out.append(f"| {row['req']} | sem cenário | - | - |")
            for sc in row["cenarios"]:
                out.append(f"| {row['req']} | {sc['nome']} | {sc['teste']} | {sc['conferido']} |")
        out.append("")
    out += ["O que o D não vê: o que o pedido pediu e nunca virou requisito.",
            "Ele também não vê o cenário que tem a tag e não captura o requisito.",
            "Ele não vê o porquê, o modelo e a preferência de forma.", ""]
    when = f"M1 {delta['m1_em']} e M2 {at}" if measured and delta.get("m1_em") and at else (f"{report['momento']} {at}" if at else report["momento"])
    out.append(f"Medido em {when}. Fontes: {', '.join(report['entradas']) or 'nenhuma lida'}.")
    return "\n".join(out) + "\n"


def render_citizen(report: dict) -> str:
    """Citizen register (DRP-013): counts in words, absences by name, no D, no percent, no tool word."""
    if report.get("nao_aplicavel"):
        return _na_line(report) + "\n"
    deg, items, lei = report["degraus"], report["itens"], report["leituras"]
    out = [f"## O que ficou entre o seu pedido e o que existe ({report['feature']})", "",
           "Eu comparei o que você pediu com o que ficou pronto. Eu só descrevo; a decisão é sua.", ""]

    def absence(step: str, template: str, one: str) -> str | None:
        """Only an absence enters the citizen register; what only confirms does not (D-004, CYC-014)."""
        d = deg[step]
        den = d["cobertos"] + d["descobertos"]
        if not d["descobertos"]:
            return None
        head = words(d["descobertos"]).capitalize()
        return (one if d["descobertos"] == 1 else template).format(k=head, n=words(den))

    found = False
    s1 = absence("D1", "{k} de {n} requisitos não têm cenário.", "{k} de {n} requisitos não tem cenário.")
    if s1:
        found = True
        out += [s1, ""] + [f'- "{i["texto"] or i["req"]}"' for i in items["reqs_descobertos"]] + [""]
    s2 = absence("D2", "{k} de {n} cenários não têm teste que rodou.", "{k} de {n} cenários não tem teste que rodou.")
    if s2:
        found = True
        out += [s2, ""] + [f'- "{i["nome"]}"' for i in items["cenarios_descobertos"]["D2"]] + [""]
    s3 = absence("D3a", "{k} de {n} cenários com teste não mostraram o comportamento pedido.",
                 "{k} de {n} cenários com teste não mostrou o comportamento pedido.")
    if s3:
        found = True
        out += [s3, ""] + [f'- "{i["nome"]}"' for i in items["cenarios_descobertos"]["D3a"]] + [""]
    if deg["D3b"]["descobertos"]:
        found = True
        out += ["Parte do código que mudou não tem nenhum cenário que a confira.", ""]
    nm_codes = list(dict.fromkeys(c for s in STEPS for c in deg[s]["razao_nm"]))
    if nm_codes:
        out += [NM_SENTENCE[c] for c in nm_codes] + [""]
    if not found and not nm_codes:
        out += ["Eu não achei nada que falte entre o seu pedido e o que existe, no que eu medi.", ""]
    delta = report.get("delta") or {}
    if report["momento"] == "M2" and delta:
        if delta.get("estado") != "medido":
            out += [NM_SENTENCE["NM-SEM-M1"], ""]
        else:
            moved = []
            more = {"D1": "mais requisitos ficaram sem cenário", "D2": "mais cenários ficaram sem teste",
                    "D3a": "mais cenários deixaram de passar", "D3b": "mais código ficou sem cenário que o confira"}
            less = {"D1": "menos requisitos ficaram sem cenário", "D2": "menos cenários ficaram sem teste",
                    "D3a": "menos cenários deixaram de passar", "D3b": "menos código ficou sem cenário que o confira"}
            for step in STEPS:
                chg = delta.get(step, {}).get("mudanca")
                if chg:
                    moved.append(f"Depois da entrega, {(more if chg > 0 else less)[step]}.")
            out += moved + ([""] if moved else [])
    if lei["d0"]["estado"] != "medido":
        out += [NM_SENTENCE["NM-SEM-INDICE-BRIEF"], ""]
    elif lei["d0"]["residuo"]:
        out += ["Estas frases do seu pedido não viraram requisito nem fora do escopo:", ""]
        out += [f'- "{r.get("texto") or r["frase"]}"' for r in lei["d0"]["residuo"]] + [""]
    n_nf = lei["nao_faz"]["sem_evidencia"]
    if n_nf:
        what = "um item" if n_nf == 1 else f"{words(n_nf)} itens"
        out += [f"Eu disse que não faria {what}. Nenhum cenário prova que eu não o faço."
                if n_nf == 1 else f"Eu disse que não faria {what}. Nenhum cenário prova que eu não os faço.", ""]
    aud = report["auditoria"]
    if aud["nao"]:
        out += ["Há requisitos em que o cenário não captura o que você pediu. Peça para ver quais.", ""]
    retr = report["retraducao"]
    if retr["estado"] == "medido":
        out += ["Eu escrevi o que entendi depois do código. Para cada requisito, diga: é isso, ou não é isso.", ""]
        for i in retr["itens"]:
            if not i["depois"]:
                continue
            out += [f'Requisito: "{i.get("texto") or i["req"]}"', ""]
            out += [f'- Você pediu: "{" / ".join(i["pedido"]) or "sem frase ligada"}"',
                    f'- Eu entendi antes do código: "{i["antes"] or "sem texto"}"',
                    f'- Eu entendi depois do código: "{i["depois"]}"', ""]
    else:
        out += [NM_SENTENCE["NM-SEM-RETRADUCAO-POS-CODIGO"], ""]
    for r in report["ressalvas"]:
        out += [CITIZEN_CAVEAT.get(r, r), ""]
    return "\n".join(out).rstrip() + "\n"


_HTML_CSS = """:root{--bg:#fff;--fg:#1c1c1c;--mut:#555;--bar:#2b6cb0;--trk:#e2e8f0;--line:#cbd5e0}
@media (prefers-color-scheme:dark){:root{--bg:#171717;--fg:#eee;--mut:#aaa;--bar:#63b3ed;--trk:#333;--line:#444}}
body{background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,sans-serif;max-width:56rem;margin:0 auto;padding:1rem}
table{border-collapse:collapse;width:100%}th,td{border:1px solid var(--line);padding:.35rem .5rem;text-align:left;vertical-align:top}
.bar{background:var(--trk);height:.7rem;border-radius:.35rem;min-width:6rem}.bar>i{display:block;height:100%;background:var(--bar);border-radius:.35rem}
details{margin:.6rem 0}summary{cursor:pointer;font-weight:600}.mut{color:var(--mut)}"""


def render_html(report: dict, *, citizen: bool = False) -> str:
    """One self-contained file, no external resource, every text escaped; the number is also in the text."""
    esc = html.escape
    title = f"Divergência por degrau ({report.get('feature', '')}, {report.get('momento', '')})"
    body = [f"<h1>{esc(title)}</h1>"]
    if report.get("nao_aplicavel"):
        body.append(f"<p>{esc(_na_line(report))}</p>")
    elif citizen:
        for para in render_citizen(report).split("\n\n")[1:]:
            lines = [ln for ln in para.splitlines() if ln.strip()]
            if lines and all(ln.startswith("- ") for ln in lines):
                body.append("<ul>" + "".join(f"<li>{esc(ln[2:])}</li>" for ln in lines) + "</ul>")
            elif lines:
                body.append("<p>" + "<br>".join(esc(ln) for ln in lines) + "</p>")
    else:
        body.append(f"<p>{esc(highlight(report))}</p>")
        body.append("<table><tr><th>Degrau</th><th>Barra</th><th>Descobertos</th><th>Não medido (razão)</th><th>D</th><th>Prova</th></tr>")
        for step in STEPS:
            d = report["degraus"][step]
            den = d["cobertos"] + d["descobertos"]
            width = round(100 * d["descobertos"] / den) if den else 0
            text = f"{d['descobertos']} de {den}" if den else "sem itens medidos"
            body.append(f"<tr><td>{esc(STEP_LABEL[step])}</td><td><div class='bar'><i style='width:{width}%'></i></div>"
                        f"<span class='mut'>{esc(text)}</span></td><td>{d['descobertos']}</td><td>{esc(_nm_cell(d))}</td>"
                        f"<td>{esc(_fd(d['D']))}</td><td>{esc(d['prova'])}</td></tr>")
        body.append("</table>")
        md = render_markdown(report)
        body.append(f"<details><summary>Relatório completo</summary><pre>{esc(md)}</pre></details>")
    return ("<!doctype html>\n<html lang='pt-BR'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{esc(title)}</title><style>{_HTML_CSS}</style></head><body>" + "\n".join(body) + "</body></html>\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _slugs(root: Path, feature: str | None) -> list[str]:
    if feature:
        return [feature]
    base = root / "features"
    return sorted(p.name for p in base.iterdir() if p.is_dir()) if base.is_dir() else []


EXAMPLES = """examples:
  drift_report.py --feature task-list --moment M1 --freeze --at 2026-10-06T18:00:00Z   # write features/task-list/drift/M1.json
  drift_report.py --feature task-list --plan plan.md --moment M2 --compare --md         # report with the M2 - M1 delta
  drift_report.py --feature task-list --citizen                                         # words only, no technical number
  drift_report.py --feature task-list --json                                            # JSON, schema_version 1
  drift_report.py --feature task-list --html --out out/                                 # self-contained HTML file
  drift_report.py --feature task-list --audit-sample                                    # REQs for the blind audit
  drift_report.py --feature task-list --md --as-coded                                   # add the table regenerated from the matrix
  drift_report.py                                                                       # every feature, alphabetical order
"""


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="drift_report.py", description="Divergence report per step of the ladder (DRP-001 to DRP-019).",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=EXAMPLES)
    ap.add_argument("root", nargs="?", default=".", help="project root (default: current directory)")
    ap.add_argument("--feature", help="slug of features/<slug>/; omit to report every feature in alphabetical order")
    ap.add_argument("--plan", help="plan file (a v1 plan or Specify: skipped is reported as not applicable)")
    ap.add_argument("--moment", choices=("M1", "M2"), default="M2", help="M1 = end of IMPLEMENT, M2 = REFLECT")
    ap.add_argument("--freeze", action="store_true", help="write the snapshot (M1.json refuses to overwrite); needs --at")
    ap.add_argument("--compare", action="store_true", help="add the M2 - M1 delta")
    ap.add_argument("--audit-sample", action="store_true", help="list the REQs of the blind audit sample and stop")
    ap.add_argument("--json", action="store_true", help="the report as JSON (schema_version 1)")
    ap.add_argument("--md", action="store_true", help="the report in Markdown, power dev register (default)")
    ap.add_argument("--citizen", action="store_true", help="the report in the citizen register: no technical number")
    ap.add_argument("--html", action="store_true", help="the report as a self-contained HTML file")
    ap.add_argument("--as-coded", action="store_true", help="add the as-coded table regenerated from the matrix")
    ap.add_argument("--out", help="folder for --html (default features/<slug>/drift/)")
    ap.add_argument("--at", help="UTC time of the snapshot (ISO), given by the caller; the script never reads the clock")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print(f"drift_report: {root}: não é uma pasta", file=sys.stderr)
        return 2
    if args.freeze and not args.at:
        print("drift_report: --freeze pede --at <UTC ISO>", file=sys.stderr)
        return 2
    plan = Path(args.plan) if args.plan else None
    slugs = _slugs(root, args.feature)
    try:
        if not slugs:
            report = {"schema_version": SCHEMA_VERSION, "nao_aplicavel": True, "motivo": "sem-features", "razao_nm": []}
            print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else NA_LINES["sem-features"])
            return 0
        reports = []
        for slug in slugs:
            report = generate(root, slug, plan=plan, moment=args.moment, compare_m1=args.compare, as_coded=args.as_coded)
            if args.audit_sample:
                active = [p["req"] for p in report.get("retraducao", {}).get("itens", [])]
                print("\n".join(audit_sample(active, slug)))
                continue
            if args.freeze:
                if report.get("nao_aplicavel"):
                    print(NA_LINES.get(report.get("motivo", ""), NA_LINES["sem-features"]))
                    continue
                print(f"Congelei {args.moment}: {freeze(report, root, slug, args.moment, args.at)}")
                continue
            reports.append(report)
    except DriftInputError as exc:
        print(f"drift_report: {exc}", file=sys.stderr)
        return 2
    except FileExistsError as exc:
        print(f"drift_report: {exc}", file=sys.stderr)
        return 2
    if args.audit_sample or args.freeze:
        return 0
    if args.json:
        body = reports[0] if len(reports) == 1 else {"schema_version": SCHEMA_VERSION, "relatorios": reports}
        print(json.dumps(body, ensure_ascii=False, indent=2))
        return 0
    chosen_md = args.md or not (args.citizen or args.html)
    chunks = []
    for report in reports:
        if args.as_coded and not report.get("nao_aplicavel"):
            pass  # as_coded rows are already in the report: generate(as_coded=True)
        if chosen_md:
            chunks.append(render_markdown(report, at=args.at))
        if args.citizen:
            chunks.append(render_citizen(report))
        if args.html:
            if report.get("nao_aplicavel"):
                chunks.append(_na_line(report) + "\n")
                continue
            folder = Path(args.out) if args.out else root / "features" / report["feature"] / "drift"
            folder.mkdir(parents=True, exist_ok=True)
            target = folder / f"{report['feature']}-{report['momento']}.html"
            target.write_text(render_html(report, citizen=args.citizen), encoding="utf-8")
            print(f"HTML: {target}", file=sys.stderr)
    print("\n".join(chunks), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
