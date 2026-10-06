"""Tests for check_plan_scenarios.py -- PFS-001 to PFS-015 over the golden fixtures.

Invocation: test
Lifecycle: active

Rules: .claude/references/general/plan-from-scenarios.md (PFS-NNN).
Fixtures: fixtures/plan_scenarios/<case>/ (plan.md + esperado.json; `root` points to _raizes/<name>).
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import check_plan_scenarios as cps
import pytest
from check_plan_scenarios import UsageError, check_text, main

_TESTS_DIR = Path(__file__).resolve().parent
_SCRIPTS = _TESTS_DIR.parent
_FIXTURES = _TESTS_DIR / "fixtures" / "plan_scenarios"
_DOC = _TESTS_DIR.parents[2] / "references" / "general" / "plan-from-scenarios.md"
_REGISTRY = _SCRIPTS / "check_plugin_registry.json"

CASES = sorted(p.parent.relative_to(_FIXTURES).as_posix()
               for p in [*_FIXTURES.glob("*/esperado.json"), *_FIXTURES.glob("ref-*/*/esperado.json")])
SLUG = "contas-da-semana"


def _expected(case: str) -> dict:
    return json.loads((_FIXTURES / case / "esperado.json").read_text(encoding="utf-8"))


def _root(case: str) -> Path:
    rel = _expected(case)["root"]
    return _FIXTURES / rel if rel else _FIXTURES


def _stub(case: str):
    status = _expected(case)["status"]

    def fn(root: Path, slug: str) -> dict:
        assert status is not None, "the scenario status must not be asked for in this case"
        return {"schema_version": 1, "status": status, "reasons": [], "reqs": []}

    return fn


def _run_case(case: str) -> cps.Report:
    text = (_FIXTURES / case / "plan.md").read_text(encoding="utf-8")
    return check_text(text, _root(case), file="plan.md", status_fn=_stub(case))


def _triples(report: cps.Report) -> list[list]:
    return sorted(([f.rule, f.severity, f.line] for f in report.findings), key=lambda t: (t[2], t[0]))


# ---------------------------------------------------------------------------
# Golden fixtures
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case", CASES)
def test_golden_findings_and_exit_code(case: str) -> None:
    report, expected = _run_case(case), _expected(case)
    assert _triples(report) == sorted(expected["findings"], key=lambda t: (t[2], t[0]))
    assert cps.exit_code(report, strict=False) == expected["exit_code"]


@pytest.mark.parametrize("case", CASES)
def test_golden_matrix(case: str) -> None:
    report, expected = _run_case(case), _expected(case)
    if expected["matrix"] is None:
        assert report.matrix is None
    else:
        assert {row["scenario"]: row["steps"] for row in report.matrix} == expected["matrix"]


def test_every_checkable_rule_has_a_firing_and_a_clean_case() -> None:
    fired = {f[0] for case in CASES for f in _expected(case)["findings"]}
    documented = set(re.findall(r"^### (PFS-\d+)", _DOC.read_text(encoding="utf-8"), re.MULTILINE))
    assert documented == set(cps.RULES)
    assert fired == set(cps.RULES) - {"PFS-015"}  # PFS-015 is "what I do not do"
    clean = [c for c in CASES if _expected(c)["exit_code"] == 0 and not _expected(c)["findings"]]
    assert {"v1-real-1", "v2-completo", "v2-skipped"} <= set(clean)


# ---------------------------------------------------------------------------
# Behavior named by the plan (step 4, Tests:)
# ---------------------------------------------------------------------------


def test_v1_plan_exits_zero_without_reading_the_body() -> None:
    report = _run_case("v1-corpo-quebrado")
    assert report.unverified and report.findings == []
    assert cps.exit_code(report, strict=True) == 0


def test_step_with_tests_and_no_scenarios_returns_pfs_006_with_the_step_number() -> None:
    report = _run_case("pfs-006-sem-campo-com-testes")
    [finding] = [f for f in report.findings if f.rule == "PFS-006"]
    assert "passo 4" in finding.message and finding.severity == "error"


def test_scenario_without_step_returns_pfs_009_with_the_key() -> None:
    report = _run_case("pfs-009-cenario-sem-step")
    [finding] = [f for f in report.findings if f.rule == "PFS-009"]
    assert "A lista abre logo com muitas contas" in finding.message


def test_unknown_key_returns_pfs_005_and_old_plan_returns_pfs_011() -> None:
    assert {f.rule for f in _run_case("pfs-005-renomeado").findings} == {"PFS-005", "PFS-009"}
    report = _run_case("pfs-011-stale")
    assert [f.rule for f in report.findings] == ["PFS-011"]
    assert "desatualizados" in report.findings[0].message
    assert cps.exit_code(report, strict=False) == 1


def test_complete_plan_has_every_scenario_in_exactly_one_step() -> None:
    report = _run_case("v2-completo")
    assert all(len(row["steps"]) == 1 for row in report.matrix)
    assert [len(s["scenarios"]) for s in report.steps] == [0, 1, 2, 1, 0]


def test_outline_is_one_key() -> None:
    report = _run_case("v2-outline")
    keys = [k for s in report.steps for k in s["scenarios"]]
    assert sum("A lista abre logo" in k for k in keys) == 1


def test_na_with_tests_is_info_and_strict_makes_it_fail() -> None:
    report = _run_case("pfs-006-na-com-testes")
    assert cps.exit_code(report, strict=False) == 0
    assert cps.exit_code(report, strict=True) == 1


def test_unknown_version_is_a_fatal_finding_with_exit_2() -> None:
    report = _run_case("pfs-001-versao-3")
    assert cps.exit_code(report, strict=False) == 2


# ---------------------------------------------------------------------------
# Reference runs (plan-000012 step 7; simulated) and the real validator
# ---------------------------------------------------------------------------

_REF_A = "ref-a-feature-com-codigo"
_REF_B = "ref-b-sem-codigo"
_REF_C = "ref-c-cenarios-reaprovados"


@pytest.mark.parametrize("case", [c for c in CASES if _expected(c)["status"] is not None])
def test_real_check_specify_gives_the_status_the_stub_gives(case: str) -> None:
    real = cps.scenario_status(_root(case), SLUG)
    assert real["status"] == _expected(case)["status"]


def test_run_a_draft_is_refused_then_one_fix_passes() -> None:
    draft, final = _run_case(f"{_REF_A}/01-rascunho"), _run_case(f"{_REF_A}/02-final")
    assert {f.rule for f in draft.findings} == {"PFS-006", "PFS-009"} and cps.exit_code(draft, strict=False) == 1
    assert final.findings == [] and all(len(r["steps"]) == 1 for r in final.matrix)


def test_run_b_skip_passes_and_the_variant_with_a_test_is_refused() -> None:
    assert _run_case(f"{_REF_B}/01-final").findings == []
    refused = _run_case(f"{_REF_B}/02-variante-recusada")
    assert [f.rule for f in refused.findings] == ["PFS-013"] and "specify foi pulada" in refused.findings[0].message


def test_run_c_reapproval_invalidates_the_plan_until_it_is_updated() -> None:
    stale, old, updated = (_run_case(f"{_REF_C}/{n}") for n in
                           ("01-feature-editado-sem-reaprovar", "02-reaprovado-plano-velho", "03-plano-atualizado"))
    assert [f.rule for f in stale.findings] == ["PFS-011"]
    assert {f.rule for f in old.findings} == {"PFS-005", "PFS-009", "PFS-012"}
    assert updated.findings == [] and cps.exit_code(updated, strict=False) == 0


def test_calibration_of_the_reference_run_a() -> None:
    """Friction baseline for the pilot: N/A share of the steps and steps per scenario."""
    final = _run_case(f"{_REF_A}/02-final")
    na_share = sum(1 for s in final.steps if s["scenarios_na"]) / len(final.steps)
    owned = sum(len(s["scenarios"]) for s in final.steps)
    assert na_share == 0.4 and owned / len(final.matrix) == 1.0


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("reason,ok", [("", False), ("n/a", False), ("TBD", False), ("x y", False), ("...", False),
                                       ("tabela usada pelo cenário", True)])
def test_reason_ok(reason: str, ok: bool) -> None:
    assert cps.reason_ok(reason) is ok


def test_parse_header_is_free_order_and_stops_at_the_first_section() -> None:
    text = "# T\n\n> bloco\nSpecify: approved (rev 3)\nplan_format_version: 2\nFeature: a-b\n\n## Seção\nFeature: x\n"
    head = cps.parse_header(text)
    assert head.version == "2" and head.features == [(6, "a-b")] and head.specifies == [(4, "approved (rev 3)")]


def test_parse_steps_ignores_fenced_examples_and_other_sections() -> None:
    text = ("# T\nplan_format_version: 2\n\n## Steps\n\n```\n### Step 9: exemplo\n```\n\n### Step 1: Real\n"
            "- **Tests**: N/A (x)\n- **Scenarios**: N/A (a b c)\n\n## Review\n### Step 2: fora\n")
    steps = cps.parse_steps(text)
    assert [s.n for s in steps] == [1] and steps[0].scen == "N/A (a b c)"


def test_parse_accepts_the_colon_inside_the_bold() -> None:
    steps = cps.parse_steps("## Steps\n### Step 1: A\n- **Tests:** N/A (x)\n- **Scenarios:** N/A (um motivo bom)\n")
    assert steps[0].tests == "N/A (x)" and steps[0].scen == "N/A (um motivo bom)"


def test_lock_key_with_backtick_cannot_be_cited(tmp_path: Path) -> None:
    root = tmp_path / "p"
    shutil.copytree(_FIXTURES / "_raizes" / "aprovada", root)
    lock_path = root / "features" / SLUG / "scenarios.lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    lock["index"].append(f"{SLUG}/{SLUG}.feature::Nome com `crase`")
    lock_path.write_text(json.dumps(lock), encoding="utf-8")
    text = (_FIXTURES / "v2-completo" / "plan.md").read_text(encoding="utf-8")
    report = check_text(text, root, status_fn=lambda r, s: {"status": "approved"})
    assert {"PFS-004", "PFS-009"} <= {f.rule for f in report.findings}


# ---------------------------------------------------------------------------
# CLI, I/O and the scenario validator
# ---------------------------------------------------------------------------


def _cli(capsys, *args: str) -> tuple[int, str, str]:
    code = main(list(args))
    out = capsys.readouterr()
    return code, out.out, out.err


def test_cli_real_validator_approved_plan_exits_zero(capsys) -> None:
    code, out, _ = _cli(capsys, str(_FIXTURES / "v2-completo" / "plan.md"), "--root", str(_FIXTURES / "_raizes" / "aprovada"))
    assert code == 0 and "estado dos cenários: approved" in out


def test_cli_real_validator_stale_plan_exits_one(capsys) -> None:
    code, out, _ = _cli(capsys, str(_FIXTURES / "pfs-011-stale" / "plan.md"), "--root", str(_FIXTURES / "_raizes" / "stale"))
    assert code == 1 and "PFS-011" in out and "refaça a specify" in out


def test_cli_status_cmd_stub_replaces_the_real_validator(capsys, tmp_path: Path) -> None:
    stub = tmp_path / "stub.py"
    stub.write_text('import json,sys\nprint(json.dumps({"schema_version": 1, "status": "stale", "reasons": ["feature"]}))\n',
                    encoding="utf-8")
    code, out, _ = _cli(capsys, str(_FIXTURES / "v2-completo" / "plan.md"), "--root", str(_FIXTURES / "_raizes" / "aprovada"),
                        "--status-cmd", f"{sys.executable} {stub} {{root}} {{slug}}")
    assert code == 1 and "estado: stale; feature" in out


def test_cli_missing_validator_exits_2_with_the_message(capsys) -> None:
    code, _, err = _cli(capsys, str(_FIXTURES / "v2-completo" / "plan.md"), "--root", str(_FIXTURES / "_raizes" / "aprovada"),
                        "--status-cmd", "/nao/existe/check_specify.py")
    assert code == 2 and "validador de cenários não encontrado" in err and "Traceback" not in err


def test_missing_validator_does_not_matter_for_v1_or_skipped_plans(capsys) -> None:
    for case in ("v1-real-1", "v2-skipped"):
        code, _, _ = _cli(capsys, str(_FIXTURES / case / "plan.md"), "--status-cmd", "/nao/existe")
        assert code == 0


def test_validator_with_unknown_schema_exits_2(tmp_path: Path) -> None:
    stub = tmp_path / "stub.py"
    stub.write_text('print(\'{"schema_version": 9, "status": "approved"}\')\n', encoding="utf-8")
    with pytest.raises(UsageError):
        cps.scenario_status(_FIXTURES, SLUG, f"{sys.executable} {stub}")


def test_cli_json_has_schema_version_matrix_and_steps(capsys) -> None:
    code, out, _ = _cli(capsys, str(_FIXTURES / "v2-completo" / "plan.md"), "--root", str(_FIXTURES / "_raizes" / "aprovada"), "--json")
    data = json.loads(out)
    assert code == 0 and data["schema_version"] == 1 and data["version"] == 2 and data["feature"] == SLUG
    assert len(data["matrix"]) == 4 and [s["n"] for s in data["steps"]] == [1, 2, 3, 4, 5]
    assert data["steps"][0]["tests_na"] is True and data["steps"][1]["tests_na"] is False


def test_cli_table_lists_scenario_and_steps(capsys) -> None:
    code, out, _ = _cli(capsys, str(_FIXTURES / "pfs-010-dois-donos" / "plan.md"), "--root", str(_FIXTURES / "_raizes" / "aprovada"),
                        "--table")
    assert out.startswith("## Cobertura de cenários") and "| 2, 5 |" in out and code in (0, 1)


def test_two_runs_give_identical_output(capsys) -> None:
    args = (str(_FIXTURES / "pfs-014-nenhum-step" / "plan.md"), "--root", str(_FIXTURES / "_raizes" / "aprovada"), "--json")
    first = _cli(capsys, *args)
    second = _cli(capsys, *args)
    assert first == second


def test_utf8_bom_plan_is_read(tmp_path: Path, capsys) -> None:
    plan = tmp_path / "plan.md"
    plan.write_bytes(b"\xef\xbb\xbf" + (_FIXTURES / "v2-skipped" / "plan.md").read_bytes())
    code, _, _ = _cli(capsys, str(plan), "--root", str(tmp_path))
    assert code == 0


def test_unreadable_plan_exits_2_without_traceback(tmp_path: Path, capsys) -> None:
    bad = tmp_path / "plan.md"
    bad.write_bytes(b"# T\n\xff\xfe\xfa\n")
    code, _, err = _cli(capsys, str(bad), "--root", str(tmp_path))
    assert code == 2 and "Traceback" not in err
    code, _, err = _cli(capsys, str(tmp_path / "nao-existe.md"), "--root", str(tmp_path))
    assert code == 2 and "Traceback" not in err


def test_missing_root_exits_2(capsys) -> None:
    code, _, err = _cli(capsys, "--root", "/nao/existe")
    assert code == 2 and "pasta não encontrada" in err


def test_checker_never_writes(capsys) -> None:
    def digest() -> str:
        h = hashlib.sha256()
        for p in sorted(_FIXTURES.rglob("*")):
            if p.is_file():
                h.update(p.as_posix().encode() + p.read_bytes())
        return h.hexdigest()

    before = digest()
    for case in CASES:
        _cli(capsys, str(_FIXTURES / case / "plan.md"), "--root", str(_root(case)))
    assert digest() == before


# ---------------------------------------------------------------------------
# Scan mode (what run_all_checks.py runs: no arguments, cwd = project root)
# ---------------------------------------------------------------------------


def _project(tmp_path: Path, plans: dict[str, str], *, features: bool = True) -> Path:
    root = tmp_path / "proj"
    (root / "_output" / "plans").mkdir(parents=True)
    if features:
        shutil.copytree(_FIXTURES / "_raizes" / "aprovada" / "features", root / "features")
    for name, text in plans.items():
        (root / "_output" / "plans" / name).write_text(text, encoding="utf-8")
    return root


def _read(case: str) -> str:
    return (_FIXTURES / case / "plan.md").read_text(encoding="utf-8")


def test_scan_without_plans_or_with_only_v1_exits_zero(tmp_path: Path, capsys) -> None:
    root = _project(tmp_path, {"plan-000001-a.md": _read("v1-real-1"), "plan-000001-progress.md": "lixo"}, features=False)
    code, out, _ = _cli(capsys, "--root", str(root))
    assert code == 0 and "nada a verificar" in out
    root2 = tmp_path / "vazio"
    root2.mkdir()
    assert _cli(capsys, "--root", str(root2))[0] == 0


def test_scan_valid_v2_exits_zero_and_invalid_v2_exits_one(tmp_path: Path, capsys) -> None:
    root = _project(tmp_path, {"plan-000900-ok.md": _read("v2-completo")})
    assert _cli(capsys, "--root", str(root))[0] == 0
    (root / "_output" / "plans" / "plan-000901-ruim.md").write_text(_read("pfs-009-cenario-sem-step"), encoding="utf-8")
    code, out, _ = _cli(capsys, "--root", str(root))
    assert code == 1 and "plan-000901-ruim.md" in out and "PFS-009" in out


def test_scan_ignores_a_done_plan_even_if_its_scenarios_went_stale(tmp_path: Path, capsys) -> None:
    done = "# DONE | 2026-10-06 | Plan 000900 | x\n" + _read("pfs-009-cenario-sem-step").split("\n", 1)[1]
    root = _project(tmp_path, {"plan-000900-x.md": done})
    assert _cli(capsys, "--root", str(root))[0] == 0


def _as_orchestrator(root: Path) -> subprocess.CompletedProcess:
    """How run_all_checks.py runs a check: the script alone, no arguments, cwd = project root."""
    return subprocess.run([sys.executable, str(_SCRIPTS / "check_plan_scenarios.py")], cwd=root,
                          capture_output=True, text=True, check=False)


def test_orchestrator_style_run_is_skipped_ok_or_failed(tmp_path: Path) -> None:
    only_v1 = _project(tmp_path / "a", {"plan-000001-a.md": _read("v1-real-1")}, features=False)
    done = _as_orchestrator(only_v1)
    assert done.returncode == 0 and "nada a verificar" in done.stdout  # "pulado"
    valid = _project(tmp_path / "b", {"plan-000900-ok.md": _read("v2-completo")})
    assert _as_orchestrator(valid).returncode == 0  # "ok"
    broken = _project(tmp_path / "c", {"plan-000900-ok.md": _read("pfs-009-cenario-sem-step")})
    bad = _as_orchestrator(broken)
    assert bad.returncode == 1 and "PFS-009" in bad.stdout  # "falhou", with the rule name


# ---------------------------------------------------------------------------
# Registry and doc
# ---------------------------------------------------------------------------


def test_registered_in_the_plugin_registry_at_the_end() -> None:
    entries = json.loads(_REGISTRY.read_text(encoding="utf-8"))
    assert entries[-1]["script"] == "check_plan_scenarios.py"


def test_script_header_declares_invocation_and_lifecycle() -> None:
    doc = cps.__doc__ or ""
    assert re.search(r"^Invocation:\s*\S", doc, re.MULTILINE) and re.search(r"^Lifecycle:\s*active", doc, re.MULTILINE)
    assert (_SCRIPTS / "check_plan_scenarios.py").read_text(encoding="utf-8").startswith("#!/usr/bin/env python3\n# designer:")
