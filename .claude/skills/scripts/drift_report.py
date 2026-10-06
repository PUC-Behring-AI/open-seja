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
