"""Tests for cycle_adherence.py -- adherence to the specify switch (plan-000022, D-011, CYC-036).

Invocation: test
Lifecycle: active

The ledger is built in tmp_path: one plan of each class in both arms, one deviation in each
arm, a DONE, a REVOKED, a SUPERSEDED, two v1, a ULID-named plan (D-010), a plan without
`Specify default:` (read as `on`), two malformed headers, a progress file and a QA log
(both ignored) and one proposal (`fora do ciclo`).
"""

from __future__ import annotations

import json
from pathlib import Path

import cycle_adherence as ca
import pytest


def _v2(title: str, specify: str, *, default: str | None = None, feature: str | None = None) -> str:
    lines = [title, "plan_format_version: 2"]
    if default is not None:
        lines.append(f"Specify default: {default}")
    lines.append(f"Specify: {specify}")
    if feature is not None:
        lines.append(f"Feature: {feature}")
    return "\n".join(lines) + "\n\n## User brief\n\n> texto\n\n## Steps\n\n### Step 1: algo\n- **Tests**: N/A\n"


PLANS = {
    # eligible, arm on
    "plan-000101-approved-on.md": _v2("# Plan 000101 | FEATURE | 2026-10-01 10:00 UTC | a", "approved (rev 1)",
                                      default="on", feature="alpha"),
    "plan-000103-optout-on.md": _v2("# Plan 000103 | FEATURE | 2026-10-02 10:00 UTC | c",
                                    "skipped -- opt-out: protótipo rápido para validar a ideia", default="on"),
    "plan-000107-sem-linha-default.md": _v2("# Plan 000107 | FEATURE | 2026-10-03 10:00 UTC | g", "approved (rev 2)",
                                            feature="gamma"),
    "plan-000108-done.md": "# DONE | 2026-09-30 10:00 UTC |\n"
    + _v2("# Plan 000108 | FEATURE | 2026-09-01 12:00 UTC | d", "approved (rev 1)", default="on", feature="delta"),
    # eligible, arm off
    "plan-000102-approved-off.md": _v2("# Plan 000102 | FEATURE | 2026-10-01 11:00 UTC | b", "approved (rev 1)",
                                       default="off", feature="beta"),
    "plan-000104-defaultoff-off.md": _v2("# Plan 000104 | FEATURE | 2026-10-04 10:00 UTC | e",
                                         "skipped -- default off", default="off"),
    "plan-20261006-q8zrj4-ulid-default-off.md": _v2("# Plan 20261006-q8zrj4 | FEATURE | 2026-10-06 09:00 UTC | u",
                                                    "skipped -- default off: prototipação", default="off"),
    # not eligible, one in each arm
    "plan-000105-sem-codigo-on.md": _v2("# Plan 000105 | DOCUMENT | 2026-10-05 10:00 UTC | f",
                                        "skipped -- tarefa sem código: só documentação", default="on"),
    "plan-000106-sem-codigo-off.md": _v2("# Plan 000106 | DOCUMENT | 2026-10-05 11:00 UTC | h",
                                         "skipped -- plano de harness sem código", default="off"),
    # v1 (explicit and absent version)
    "plan-000110-v1.md": "# Plan 000110 | FEATURE | 2026-09-10 10:00 UTC | v1\nplan_format_version: 1\n\n## Steps\n",
    "plan-000111-sem-versao.md": "# Plan 000111 | FEATURE | 2026-09-11 10:00 | antigo\n\n## Steps\n",
    # revoked and superseded
    "plan-000109-revogado.md": "# REVOKED | 2026-10-02 10:00 UTC | Plan 000109 | FEATURE | 2026-09-20 10:00 UTC | r\n"
    "plan_format_version: 2\nSpecify default: on\nSpecify: approved (rev 1)\nFeature: rho\n\n## Steps\n",
    "plan-000112-substituido.md": "# SUPERSEDED | 2026-10-02 10:00 UTC | Plan 000112 | FEATURE | 2026-09-21 10:00 | s\n"
    "plan_format_version: 1\n\n## Steps\n",
    # malformed headers
    "plan-000113-opt-out-sem-motivo.md": _v2("# Plan 000113 | FEATURE | 2026-10-05 12:00 UTC | m",
                                             "skipped -- opt-out", default="on"),
    "plan-000114-default-ilegivel.md": _v2("# Plan 000114 | FEATURE | 2026-10-05 13:00 UTC | n",
                                           "approved (rev 1)", default="talvez", feature="nu"),
}
IGNORED = {
    "plan-000101-progress.md": "# Progress -- Plan 000101\n",
    "plan-000101-qa-approved-on.md": "# QA Log | Plan 000101 | 2026-10-01 10:00 UTC | a\n",
    "notas.md": "# not a plan\n",
}
M1 = {"schema_version": 1, "feature": "alpha", "momento": "M1", "at": "2026-10-02T10:00:00Z",
      "report": {"degraus": {"D1": {"D": 0.0, "razao_nm": []}, "D2": {"D": 0.25, "razao_nm": []},
                             "D3a": {"D": "n/a", "razao_nm": []},
                             "D3b": {"D": None, "razao_nm": ["NM-SEM-COBERTURA"]}}},
      "entradas": {}}


@pytest.fixture
def ledger(tmp_path: Path) -> Path:
    plans = tmp_path / "_output" / "plans"
    plans.mkdir(parents=True)
    for name, text in {**PLANS, **IGNORED}.items():
        (plans / name).write_text(text, encoding="utf-8")
    proposals = tmp_path / "_output" / "proposals"
    proposals.mkdir()
    (proposals / "proposal-000001-ajuste-leve.md").write_text(
        "# Proposal 000001 | 2026-10-03 10:00 UTC | ajuste leve\n", encoding="utf-8")
    drift = tmp_path / "features" / "alpha" / "drift"
    drift.mkdir(parents=True)
    (drift / "M1.json").write_text(json.dumps(M1), encoding="utf-8")
    return tmp_path


def _run(root: Path, *extra: str) -> dict:
    return ca.build_report(root / "_output" / "plans", root / "_output" / "proposals", root,
                           since=extra[0] if extra else None)


def _by_file(report: dict) -> dict[str, dict]:
    return {p["arquivo"]: p for p in report["planos"]}


def test_scan_takes_every_plan_and_skips_progress_and_qa(ledger):
    report = _run(ledger)
    assert sorted(_by_file(report)) == sorted(PLANS)
    assert report["total"] == len(PLANS) == 15


def test_count_identity(ledger):
    r = _run(ledger)
    assert r["elegiveis"] + r["nao_elegiveis"] + r["nao_medido"] + r["revogados"] + r["cabecalho_invalido"] == r["total"]
    assert (r["elegiveis"], r["nao_elegiveis"], r["nao_medido"], r["revogados"], r["cabecalho_invalido"]) == (7, 2, 2, 2, 2)
    itt = r["itt"]["on"]["n"] + r["itt"]["off"]["n"]
    pp = r["por_protocolo"]["escada"]["n"] + r["por_protocolo"]["sem_escada"]["n"]
    assert itt == pp == r["elegiveis"] == 7
    assert r["identidade"]["ok"] is True


def test_itt_and_per_protocol_arms(ledger):
    r = _run(ledger)
    assert r["itt"]["on"]["n"] == 4 and r["itt"]["off"]["n"] == 3
    assert r["itt"]["on"]["escada"] == 3 and r["itt"]["on"]["sem_escada"] == 1
    assert r["itt"]["off"]["escada"] == 1 and r["itt"]["off"]["sem_escada"] == 2
    assert r["por_protocolo"]["escada"]["n"] == 4 and r["por_protocolo"]["sem_escada"]["n"] == 3
    assert r["por_protocolo"]["escada"]["on"] == 3 and r["por_protocolo"]["escada"]["off"] == 1


def test_one_deviation_in_each_arm(ledger):
    r = _run(ledger)
    assert r["desvio"]["n"] == 2 and r["desvio"]["elegiveis"] == 7
    motivos = {m["arquivo"]: m for m in r["desvio"]["motivos"]}
    assert set(motivos) == {"plan-000103-optout-on.md", "plan-000102-approved-off.md"}
    assert motivos["plan-000103-optout-on.md"]["braco"] == "on"
    assert motivos["plan-000103-optout-on.md"]["motivo"] == "protótipo rápido para validar a ideia"
    assert motivos["plan-000102-approved-off.md"]["braco"] == "off"
    assert motivos["plan-000102-approved-off.md"]["classe"] == "approved"


def test_plan_without_default_line_is_arm_on(ledger):
    p = _by_file(_run(ledger))["plan-000107-sem-linha-default.md"]
    assert (p["grupo"], p["braco"], p["tratamento"], p["desvio"]) == ("elegivel", "on", "escada", False)


def test_done_is_counted_and_ulid_is_accepted(ledger):
    plans = _by_file(_run(ledger))
    done = plans["plan-000108-done.md"]
    assert (done["estado"], done["grupo"], done["data"]) == ("DONE", "elegivel", "2026-09-01")
    ulid = plans["plan-20261006-q8zrj4-ulid-default-off.md"]
    assert (ulid["grupo"], ulid["classe"], ulid["braco"], ulid["tratamento"]) == ("elegivel", "default off", "off",
                                                                                   "sem_escada")


def test_v1_revoked_not_eligible_and_invalid(ledger):
    plans = _by_file(_run(ledger))
    for name in ("plan-000110-v1.md", "plan-000111-sem-versao.md"):
        assert plans[name]["grupo"] == "v1"
        assert plans[name]["desfecho"]["estado"] == "não medido"
    assert plans["plan-000109-revogado.md"]["grupo"] == "revogado"
    assert plans["plan-000112-substituido.md"]["estado"] == "SUPERSEDED"
    assert plans["plan-000105-sem-codigo-on.md"]["grupo"] == "nao_elegivel"
    assert plans["plan-000106-sem-codigo-off.md"]["classe"] == "tarefa sem código"
    for name in ("plan-000113-opt-out-sem-motivo.md", "plan-000114-default-ilegivel.md"):
        assert plans[name]["grupo"] == "cabecalho_invalido"
        assert plans[name]["braco"] is None and plans[name]["desfecho"]["estado"] == "não medido"


def test_proposal_is_out_of_the_cycle(ledger):
    r = _run(ledger)
    assert r["fora_do_ciclo"] == 1
    assert r["propostas"] == ["proposal-000001-ajuste-leve.md"]


def test_outcome_only_with_frozen_m1(ledger):
    plans = _by_file(_run(ledger))
    measured = plans["plan-000101-approved-on.md"]["desfecho"]
    assert measured["estado"] == "medido"
    assert measured["fonte"] == "features/alpha/drift/M1.json"
    assert measured["vetor"]["D2"]["D"] == 0.25 and measured["vetor"]["D3b"]["razao_nm"] == ["NM-SEM-COBERTURA"]
    beta = plans["plan-000102-approved-off.md"]["desfecho"]
    assert beta["estado"] == "não medido" and "M1.json" in beta["razao"]
    skipped = plans["plan-000104-defaultoff-off.md"]["desfecho"]
    assert skipped["estado"] == "não medido" and skipped["razao"]


def test_no_aggregate_outcome_number(ledger):
    r = _run(ledger)
    for block in (r["itt"]["on"], r["itt"]["off"], r["por_protocolo"]["escada"], r["por_protocolo"]["sem_escada"]):
        assert not any(key.startswith("D") for key in block)


def test_since_filters_by_header_date(ledger):
    r = _run(ledger, "2026-10-01")
    names = set(_by_file(r))
    assert "plan-000108-done.md" not in names  # created 2026-09-01, closed 2026-09-30
    assert "plan-000110-v1.md" not in names
    assert "plan-000101-approved-on.md" in names and "plan-20261006-q8zrj4-ulid-default-off.md" in names
    assert r["elegiveis"] + r["nao_elegiveis"] + r["nao_medido"] + r["revogados"] + r["cabecalho_invalido"] == r["total"]
    assert r["total"] == 10 and r["elegiveis"] == 6 and r["revogados"] == 0
    assert r["fora_do_ciclo"] == 1


def test_cli_json(ledger, capsys):
    assert ca.main(["--json", "--root", str(ledger)]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["schema_version"] == ca.SCHEMA_VERSION
    for key in ("planos", "itt", "por_protocolo", "desvio", "nao_elegiveis", "nao_medido", "fora_do_ciclo",
                "revogados", "cabecalho_invalido"):
        assert key in data


def test_cli_table_is_pt_br(ledger, capsys):
    assert ca.main(["--root", str(ledger)]) == 0
    out = capsys.readouterr().out
    assert "não medido" in out and "elegíveis" in out and "desvio" in out
    assert "plan-20261006-q8zrj4-ulid-default-off.md" in out


@pytest.mark.parametrize("argv", [["--since", "2026-13-01"], ["--since", "ontem"]])
def test_cli_bad_since_exits_2(ledger, argv, capsys):
    assert ca.main([*argv, "--root", str(ledger)]) == 2
    assert "--since" in capsys.readouterr().err


def test_cli_root_not_a_folder_exits_2(tmp_path, capsys):
    assert ca.main(["--root", str(tmp_path / "nada")]) == 2


def test_empty_root_reports_zero(tmp_path, capsys):
    assert ca.main(["--json", "--root", str(tmp_path)]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["total"] == 0 and data["identidade"]["ok"] is True
