#!/usr/bin/env python3
# designer: When you want to know whether your plans followed the specify
#   switch, I read every plan of the ledger, the closed ones too, and I sort
#   them: the arm each plan was given (the `Specify default:` line), what it
#   really did (wrote the specification or not), and where it deviated, with
#   the reason you wrote. I count, I never judge. I show the divergence of a
#   plan only where it was frozen at delivery, and I say `não medido`
#   everywhere else. I never add up outcomes into one number.
"""
cycle_adherence.py -- Adherence report for the specify switch (plan-000022, D-011, CYC-035, CYC-036).

Invocation: user-cli, skill-invoked
Lifecycle: active

An instrument of **adherence**, not of outcome. It scans `PLANS_DIR` on its own (every
`plan-*.md`, DONE included; `-progress` files and `-qa-` logs excluded; both file-name forms,
`plan-NNNNNN-<slug>.md` and the ULID form `plan-YYYYMMDD-xxxxxx-<slug>.md`, D-010) and reads the
skip class with `check_plan_scenarios.skip_class` (the single parser, CYC-035).

Groups (every plan file lands in exactly one):

| Group                | Rule                                                                  |
|----------------------|-----------------------------------------------------------------------|
| `revogado`           | first line `# REVOKED |` or `# SUPERSEDED |` (checked first)           |
| `v1`                 | `plan_format_version: 1` or no version line -> outcome `não medido` (Q4) |
| `cabecalho_invalido` | v2 header the checker cannot trust: no or malformed `Specify:`, class   |
|                      | error (PFS-002), unreadable `Specify default:` (bad value or duplicates |
|                      | that disagree), `default off` with arm `on`, `opt-out` with arm `off`,  |
|                      | unknown `plan_format_version`, unreadable file. Never dropped.          |
| `nao_elegivel`       | v2, class `tarefa sem código` (also a skip reason without a class)      |
| `elegivel`           | v2, `approved`, `default off` or `opt-out`                              |

Identity: elegiveis + nao_elegiveis + v1 (`nao_medido`) + revogados + cabecalho_invalido = total.
Among the eligible: assigned arm (ITT) = the plan's `Specify default:` line (absent = `on`);
received treatment (per protocol) = `escada` if `approved`, `sem_escada` if `default off` or
`opt-out`; deviation = arm `on` with `opt-out`, or arm `off` with `approved`.
Proposals in `PROPOSALS_DIR` are counted as `fora_do_ciclo` (the `--light` route), outside the identity.
Outcome per plan: the vector per step only when `features/<slug>/drift/M1.json` exists; elsewhere
`não medido` with the reason. No aggregate outcome number (D-007).
`--since YYYY-MM-DD` filters by the creation date in the plan header (the first date after the
`Plan <id> |` field), never by `features/adoption.json`, which an `off` project never writes.
A plan without a readable date is left out under `--since` and counted in `sem_data`.

Paths: without `--root`, `PLANS_DIR` and `PROPOSALS_DIR` come from `project_config` and features
from the repo root. With `--root PATH`, the template defaults under it: `_output/plans`,
`_output/proposals`, `features/`.

Exit codes:
  0 = report produced (deviations are findings, never a failure).
  2 = usage error (`--since` not a date, `--root` not a folder) or a script error. Never a traceback.

Usage
-----
    python3 .claude/skills/scripts/cycle_adherence.py                       # table in pt-BR
    python3 .claude/skills/scripts/cycle_adherence.py --json                # JSON, schema_version 1
    python3 .claude/skills/scripts/cycle_adherence.py --since 2026-10-07 --root path/to/project
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_plan_scenarios as cps

SCHEMA_VERSION = 1
STEPS = ("D1", "D2", "D3a", "D3b")
NOT_MEASURED = "não medido"
PLAN_NAME_RE = re.compile(r"^plan-(?:\d{6}|\d{8}-[0-9a-z]{6})-.+\.md$")
PROPOSAL_NAME_RE = re.compile(r"^proposal-.+\.md$")
CLOSED_RE = re.compile(r"^#\s*(DONE|REVOKED|SUPERSEDED)\s*\|")
PLAN_FIELD_RE = re.compile(r"\bPlan\s+[0-9A-Za-z-]+\s*\|(.*)")
DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
ELIGIBLE, NOT_ELIGIBLE, V1, REVOKED, INVALID = "elegivel", "nao_elegivel", "v1", "revogado", "cabecalho_invalido"
APPROVED = "approved"

REASON_V1 = "plano v1: o formato não registra a especificação (Q4)"
REASON_NO_CODE = "tarefa sem código: fora da escada por tipo de tarefa"
REASON_REVOKED = "plano revogado ou substituído"
REASON_INVALID = "cabeçalho inválido: o verificador não confia nele"
REASON_NO_LADDER = ("plano sem escada: não há features/<slug>/drift/M1.json; a divergência de um plano sem "
                    "especificação só se mede no piloto com oráculo (drift-control-protocol.md)")


# ---------------------------------------------------------------------------
# Reading one plan (pure)
# ---------------------------------------------------------------------------


def header_date(text: str) -> str | None:
    """The creation date of the header: the first date after `Plan <id> |`, else the first date of line 1."""
    head = [ln for ln in text.splitlines()[:3] if ln.startswith("#")]
    for line in head:
        if (m := PLAN_FIELD_RE.search(line)) and (d := DATE_RE.search(m.group(1))):
            return d.group(1)
    if head and (d := DATE_RE.search(head[0])):
        return d.group(1)
    return None


def closed_state(text: str) -> str:
    first = text.splitlines()[0] if text else ""
    m = CLOSED_RE.match(first)
    return m.group(1) if m else "aberto"


def assigned_arm(plan: cps.Plan) -> str | None:
    """The plan's own `Specify default:` (absent = `on`, CYC-036); None when unreadable."""
    values = [v for _, v in plan.specify_defaults]
    if not values:
        return "on"
    if any(not cps.SPECIFY_DEFAULT_VALUE_RE.match(v) for v in values) or len(set(values)) > 1:
        return None
    return values[0]


def _v2_class(plan: cps.Plan) -> tuple[str | None, str, str]:
    """(class, reason, why-invalid) of a v2 header; class None means `cabecalho_invalido`."""
    if len(plan.specifies) != 1:
        return None, "", "o cabeçalho não tem exatamente uma linha `Specify:`"
    value = plan.specifies[0][1]
    if cps.APPROVED_RE.match(value):
        return APPROVED, "", ""
    if not cps.SKIPPED_RE.match(value):
        return None, "", "o valor de `Specify:` não segue o formato"
    cls, reason = cps.skip_class(value)
    if cls is None:
        return None, reason, "a classe do pulo não segue a forma (PFS-002)"
    return cls, reason, ""


def _base_entry(name: str, text: str) -> dict:
    return {"arquivo": name, "data": header_date(text), "estado": closed_state(text), "grupo": None,
            "versao": None, "classe": None, "motivo": "", "braco": None, "tratamento": None,
            "desvio": False, "feature": None, "desfecho": {"estado": NOT_MEASURED, "razao": ""}}


def _not_measured(entry: dict, group: str, reason: str) -> dict:
    entry["grupo"] = group
    entry["desfecho"] = {"estado": NOT_MEASURED, "razao": reason}
    return entry


def classify(name: str, text: str) -> dict:
    """One plan file -> its row: group, class, arm, treatment, deviation. Outcome is filled later."""
    entry = _base_entry(name, text)
    if entry["estado"] in ("REVOKED", "SUPERSEDED"):
        return _not_measured(entry, REVOKED, REASON_REVOKED)
    plan = cps.parse_header(text)
    version = cps.plan_version(plan)
    entry["versao"] = version
    if version == 1:
        return _not_measured(entry, V1, REASON_V1)
    if version is None:
        return _not_measured(entry, INVALID, f"{REASON_INVALID} (`plan_format_version` desconhecida)")
    cls, reason, why = _v2_class(plan)
    entry["classe"], entry["motivo"] = cls, reason
    if cls is None:
        return _not_measured(entry, INVALID, f"{REASON_INVALID} ({why})")
    if cls == cps.NO_CODE:
        return _not_measured(entry, NOT_ELIGIBLE, REASON_NO_CODE)
    return _eligible(entry, plan, cls)


def _eligible(entry: dict, plan: cps.Plan, cls: str) -> dict:
    arm = assigned_arm(plan)
    if arm is None:
        return _not_measured(entry, INVALID, f"{REASON_INVALID} (`Specify default:` ilegível)")
    if (cls, arm) in ((cps.DEFAULT_OFF, "on"), (cps.OPT_OUT, "off")):
        return _not_measured(entry, INVALID, f"{REASON_INVALID} (`{cls}` com o braço `{arm}`, PFS-002)")
    entry.update(grupo=ELIGIBLE, braco=arm, tratamento="escada" if cls == APPROVED else "sem_escada",
                 desvio=(cls, arm) in ((cps.OPT_OUT, "on"), (APPROVED, "off")))
    if cls == APPROVED and plan.features:
        entry["feature"] = plan.features[0][1]
    return entry


# ---------------------------------------------------------------------------
# Outcome (reads features/<slug>/drift/M1.json only)
# ---------------------------------------------------------------------------


def outcome(entry: dict, root: Path) -> dict:
    if entry["grupo"] != ELIGIBLE:
        return entry["desfecho"]
    if entry["tratamento"] != "escada":
        return {"estado": NOT_MEASURED, "razao": REASON_NO_LADDER}
    slug = entry["feature"]
    if not slug or not cps.SLUG_RE.match(slug):
        return {"estado": NOT_MEASURED, "razao": "plano aprovado sem `Feature:` legível"}
    rel = f"features/{slug}/drift/M1.json"
    path = root / rel
    if not path.is_file():
        return {"estado": NOT_MEASURED, "razao": f"{rel} não existe: o M1 não foi congelado"}
    try:
        degraus = json.loads(path.read_text(encoding="utf-8"))["report"]["degraus"]
        vector = {s: {"D": degraus[s].get("D"), "razao_nm": list(degraus[s].get("razao_nm", []))}
                  for s in STEPS if s in degraus}
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return {"estado": NOT_MEASURED, "razao": f"{rel} ilegível"}
    return {"estado": "medido", "fonte": rel, "vetor": vector}


# ---------------------------------------------------------------------------
# Scan and aggregate counts (never aggregates outcomes)
# ---------------------------------------------------------------------------


def plan_files(plans_dir: Path) -> list[Path]:
    if not plans_dir.is_dir():
        return []
    return sorted(p for p in plans_dir.iterdir()
                  if p.is_file() and PLAN_NAME_RE.match(p.name)
                  and not p.name.endswith("-progress.md") and "-qa-" not in p.name)


def proposal_files(proposals_dir: Path | None) -> list[Path]:
    if proposals_dir is None or not proposals_dir.is_dir():
        return []
    return sorted(p for p in proposals_dir.iterdir() if p.is_file() and PROPOSAL_NAME_RE.match(p.name))


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _keep(date: str | None, since: str | None) -> bool:
    return since is None or (date is not None and date >= since)


def _arm_block(rows: list[dict], key: str, value: str, split: str, parts: tuple[str, str]) -> dict:
    chosen = [r for r in rows if r[key] == value]
    block = {"n": len(chosen), "planos": [r["arquivo"] for r in chosen]}
    for part in parts:
        block[part] = sum(1 for r in chosen if r[split] == part)
    block["desvios"] = sum(1 for r in chosen if r["desvio"])
    return block


def _deviation_reason(row: dict) -> str:
    if row["classe"] == cps.OPT_OUT:
        return row["motivo"]
    return "o plano ligou a especificação num projeto que a desliga (`--with-specify`, sem motivo registrado)"


def summarize(rows: list[dict], proposals: list[str], sem_data: int) -> dict:
    count = {g: sum(1 for r in rows if r["grupo"] == g) for g in (ELIGIBLE, NOT_ELIGIBLE, V1, REVOKED, INVALID)}
    eligible = [r for r in rows if r["grupo"] == ELIGIBLE]
    deviations = [r for r in eligible if r["desvio"]]
    total = len(rows)
    return {
        "schema_version": SCHEMA_VERSION,
        "planos": rows,
        "itt": {arm: _arm_block(eligible, "braco", arm, "tratamento", ("escada", "sem_escada")) for arm in ("on", "off")},
        "por_protocolo": {t: _arm_block(eligible, "tratamento", t, "braco", ("on", "off"))
                          for t in ("escada", "sem_escada")},
        "desvio": {"n": len(deviations), "elegiveis": len(eligible),
                   "motivos": [{"arquivo": r["arquivo"], "braco": r["braco"], "classe": r["classe"],
                                "motivo": _deviation_reason(r)} for r in deviations]},
        "total": total,
        "elegiveis": count[ELIGIBLE],
        "nao_elegiveis": count[NOT_ELIGIBLE],
        "nao_medido": count[V1],
        "revogados": count[REVOKED],
        "cabecalho_invalido": count[INVALID],
        "fora_do_ciclo": len(proposals),
        "propostas": proposals,
        "sem_data": sem_data,
        "identidade": {"ok": sum(count.values()) == total,
                       "conta": "elegiveis + nao_elegiveis + nao_medido + revogados + cabecalho_invalido = total"},
    }


def build_report(plans_dir: Path, proposals_dir: Path | None, root: Path, *, since: str | None = None) -> dict:
    rows: list[dict] = []
    sem_data = 0
    for path in plan_files(plans_dir):
        text = _read(path)
        if text is None:
            entry = _not_measured(_base_entry(path.name, ""), INVALID, f"{REASON_INVALID} (arquivo ilegível)")
        else:
            entry = classify(path.name, text)
        if not _keep(entry["data"], since):
            sem_data += entry["data"] is None
            continue
        entry["desfecho"] = outcome(entry, root)
        rows.append(entry)
    proposals = []
    for path in proposal_files(proposals_dir):
        text = _read(path) or ""
        if _keep(header_date(text), since):
            proposals.append(path.name)
    return summarize(rows, proposals, sem_data)


# ---------------------------------------------------------------------------
# Rendering (pt-BR)
# ---------------------------------------------------------------------------


def _fmt_outcome(desfecho: dict) -> str:
    if desfecho["estado"] != "medido":
        return f"não medido ({desfecho['razao']})"
    parts = []
    for step, cell in desfecho["vetor"].items():
        value = cell["D"]
        shown = NOT_MEASURED if value is None else (f"{value:.2f}" if isinstance(value, float) else str(value))
        parts.append(f"{step} {shown}")
    return f"{', '.join(parts)} ({desfecho['fonte']})"


def render_table(report: dict) -> str:
    lines = ["Aderência ao interruptor da especificação (D-011). Este relatório mede aderência, não desfecho.", "",
             "| Plano | Data | Estado | Grupo | Classe | Braço | Tratamento | Desvio | Desfecho |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in report["planos"]:
        lines.append(f"| {r['arquivo']} | {r['data'] or '-'} | {r['estado']} | {r['grupo']} | {r['classe'] or '-'} "
                     f"| {r['braco'] or '-'} | {r['tratamento'] or '-'} | {'sim' if r['desvio'] else 'não'} "
                     f"| {_fmt_outcome(r['desfecho'])} |")
    itt, pp, dev = report["itt"], report["por_protocolo"], report["desvio"]
    lines += [
        "",
        (f"Total de planos: {report['total']} = {report['elegiveis']} elegíveis + {report['nao_elegiveis']} "
         f"não elegíveis + {report['nao_medido']} v1 (não medido) + {report['revogados']} revogados ou "
         f"substituídos + {report['cabecalho_invalido']} com cabeçalho inválido."),
        (f"Por intenção de tratar: braço on {itt['on']['n']} (escada {itt['on']['escada']}, sem escada "
         f"{itt['on']['sem_escada']}); braço off {itt['off']['n']} (escada {itt['off']['escada']}, sem escada "
         f"{itt['off']['sem_escada']})."),
        (f"Por protocolo: escada {pp['escada']['n']} (on {pp['escada']['on']}, off {pp['escada']['off']}); "
         f"sem escada {pp['sem_escada']['n']} (on {pp['sem_escada']['on']}, off {pp['sem_escada']['off']})."),
        f"Planos com desvio do braço: {dev['n']} de {dev['elegiveis']} elegíveis.",
    ]
    lines += [f"- {m['arquivo']} (braço {m['braco']}, {m['classe']}): {m['motivo']}" for m in dev["motivos"]]
    lines.append(f"Fora do ciclo (proposals, rota --light): {report['fora_do_ciclo']}.")
    if report["sem_data"]:
        lines.append(f"Planos sem data legível deixados de fora pelo --since: {report['sem_data']}.")
    lines.append("Nenhum número agregado de desfecho: a divergência só aparece por plano, onde o M1 foi congelado.")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _since(value: str | None) -> str | None:
    if value is None:
        return None
    try:
        return datetime.date.fromisoformat(value).isoformat()
    except ValueError:
        raise ValueError(f"--since deve ser uma data AAAA-MM-DD, recebi {value!r}") from None


def _paths(root_arg: str | None) -> tuple[Path, Path | None, Path]:
    if root_arg is not None:
        root = Path(root_arg)
        if not root.is_dir():
            raise ValueError(f"--root {root}: não é uma pasta")
        return root / "_output" / "plans", root / "_output" / "proposals", root
    import project_config as pc

    plans = pc.get_path("PLANS_DIR") or pc.REPO_ROOT / "_output" / "plans"
    return plans, pc.get_path("PROPOSALS_DIR"), pc.REPO_ROOT


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="cycle_adherence.py",
                                 description="Adherence to the specify switch (D-011): ITT, per protocol, deviations.")
    ap.add_argument("--json", action="store_true", help="the report as JSON (schema_version 1)")
    ap.add_argument("--since", help="only plans whose header date is on or after YYYY-MM-DD")
    ap.add_argument("--root", help="project root (default: this repository, paths from project_config)")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        since = _since(args.since)
        plans_dir, proposals_dir, root = _paths(args.root)
        report = build_report(plans_dir, proposals_dir, root, since=since)
    except ValueError as exc:
        print(f"cycle_adherence: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"cycle_adherence: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_table(report), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
