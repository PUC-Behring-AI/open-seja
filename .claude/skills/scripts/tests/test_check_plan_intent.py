"""Tests for check_plan_intent.py (plan-20261020-688kjs Step 9): the plan v3 shape (PIC rules)."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import check_plan_intent
import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "check_plan_intent.py"
FIX = Path(__file__).resolve().parent / "fixtures" / "plan_intent"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False
    )


def _errors(path: Path) -> list[dict]:
    return [f for f in check_plan_intent.check_plan(path)["findings"] if f["severity"] == "error"]


def _write(tmp_path: Path, name: str, text: str) -> Path:
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_complete_v3_plan_passes_and_json_has_schema_version() -> None:
    proc = _run(str(FIX / "v3_completo.md"), "--json")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    data = json.loads(proc.stdout)
    assert data["schema_version"] == 1
    assert data["plans"][0]["version"] == 3
    assert not [f for f in data["plans"][0]["findings"] if f["severity"] == "error"]


def test_requirement_without_use_case_exits_1_and_cites_it() -> None:
    proc = _run(str(FIX / "v3_req_sem_caso.md"))
    assert proc.returncode == 1
    assert "REQ-contas-002" in proc.stdout


def test_covers_citing_missing_requirement_exits_1() -> None:
    proc = _run(str(FIX / "v3_covers_inexistente.md"))
    assert proc.returncode == 1
    assert "REQ-contas-009" in proc.stdout


def test_empty_use_case_section_exits_1() -> None:
    proc = _run(str(FIX / "v3_casos_vazio.md"))
    assert proc.returncode == 1
    assert "Casos de uso" in proc.stdout


@pytest.mark.parametrize("name", ["v1_plano.md", "v2_plano.md"])
def test_v1_and_v2_plans_have_nothing_to_check(name: str) -> None:
    proc = _run(str(FIX / name))
    assert proc.returncode == 0
    assert "nada a verificar" in proc.stdout


def test_no_argument_scans_plans_dir_with_only_v1_and_v2(tmp_path, monkeypatch, capsys) -> None:
    shutil.copy(FIX / "v1_plano.md", tmp_path / "plan-000042-algo.md")
    shutil.copy(FIX / "v2_plano.md", tmp_path / "plan-000043-algo.md")
    monkeypatch.setattr(check_plan_intent, "_default_plans_dir", lambda: tmp_path)
    assert check_plan_intent.main([]) == 0
    assert "nada a verificar" in capsys.readouterr().out


def test_no_argument_scan_fails_on_a_broken_v3_and_skips_companions(tmp_path, monkeypatch) -> None:
    shutil.copy(FIX / "v3_req_sem_caso.md", tmp_path / "plan-20261020-k3m9qz-contas.md")
    shutil.copy(FIX / "v3_casos_vazio.md", tmp_path / "plan-20261020-k3m9qz-progress.md")
    monkeypatch.setattr(check_plan_intent, "_default_plans_dir", lambda: tmp_path)
    report = check_plan_intent.run(check_plan_intent._targets(None))
    assert [Path(p["path"]).name for p in report["plans"]] == ["plan-20261020-k3m9qz-contas.md"]
    assert check_plan_intent.main([]) == 1


def test_missing_plans_dir_exits_0(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(check_plan_intent, "_default_plans_dir", lambda: tmp_path / "nope")
    assert check_plan_intent.main([]) == 0


def test_missing_section_is_an_error(tmp_path) -> None:
    text = (FIX / "v3_completo.md").read_text(encoding="utf-8")
    a, b = text.index("## Retradução"), text.index("## Nas suas palavras")
    p = _write(tmp_path, "p.md", text[:a] + text[b:])
    assert any("Retradução" in f["message"] for f in _errors(p))


def test_retelling_without_what_i_will_not_do_is_an_error(tmp_path) -> None:
    text = (FIX / "v3_completo.md").read_text(encoding="utf-8")
    p = _write(tmp_path, "p.md", text.replace("O que eu não vou fazer: enviar comprovantes por e-mail.\n", ""))
    assert any(f["rule"] == "PIC-006" for f in _errors(p))


def test_missing_approval_line_is_only_a_warning(tmp_path) -> None:
    text = (FIX / "v3_completo.md").read_text(encoding="utf-8")
    p = _write(tmp_path, "p.md", text.replace("Aprovação: aprovado em 2026-10-20\n", ""))
    findings = check_plan_intent.check_plan(p)["findings"]
    assert not [f for f in findings if f["severity"] == "error"]
    assert any(f["rule"] == "PIC-006" and f["severity"] == "warning" for f in findings)


def test_intent_needs_four_lines(tmp_path) -> None:
    text = (FIX / "v3_completo.md").read_text(encoding="utf-8")
    p = _write(tmp_path, "p.md", text.replace("- Pronto quando:", "- Quase:"))
    assert any(f["rule"] == "PIC-003" and "Pronto quando" in f["message"] for f in _errors(p))


def test_requirement_not_covered_by_any_step_is_an_error(tmp_path) -> None:
    text = (FIX / "v3_completo.md").read_text(encoding="utf-8")
    p = _write(tmp_path, "p.md", text.replace("- **Covers**: REQ-contas-002\n", ""))
    errs = _errors(p)
    assert any(f["rule"] == "PIC-008" and "REQ-contas-002" in f["message"] for f in errs)


def test_covers_on_step_with_tests_na_is_an_error(tmp_path) -> None:
    text = (FIX / "v3_completo.md").read_text(encoding="utf-8")
    p = _write(
        tmp_path,
        "p.md",
        text.replace("- **Tests**: N/A (documentação)\n", "- **Tests**: N/A (documentação)\n- **Covers**: REQ-contas-001\n"),
    )
    assert any(f["rule"] == "PIC-008" and "N/A" in f["message"] for f in _errors(p))


def test_plan_requirement_inside_traces_is_an_error(tmp_path) -> None:
    text = (FIX / "v3_completo.md").read_text(encoding="utf-8")
    p = _write(tmp_path, "p.md", text.replace("- **Traces**: REQ-MC-011\n", "- **Traces**: REQ-MC-011, REQ-contas-001\n"))
    assert any(f["rule"] == "PIC-008" and "Traces" in f["message"] for f in _errors(p))


def test_requirement_without_para_que_or_origin_is_an_error(tmp_path) -> None:
    text = (FIX / "v3_completo.md").read_text(encoding="utf-8")
    p = _write(
        tmp_path,
        "p.md",
        text.replace(
            "- REQ-contas-002: Você vê um aviso três dias antes do vencimento. Para que: você não paga multa. (A2)",
            "- REQ-contas-002: Você vê um aviso três dias antes do vencimento.",
        ),
    )
    rules = {f["rule"] for f in _errors(p) if "REQ-contas-002" in f["message"]}
    assert "PIC-004" in rules


def test_duplicate_requirement_id_is_an_error(tmp_path) -> None:
    text = (FIX / "v3_completo.md").read_text(encoding="utf-8")
    p = _write(tmp_path, "p.md", text.replace("- REQ-contas-002:", "- REQ-contas-001:", 1))
    assert any(f["rule"] == "PIC-004" and "duplicado" in f["message"] for f in _errors(p))


def test_origin_not_in_your_words_is_an_error(tmp_path) -> None:
    text = (FIX / "v3_completo.md").read_text(encoding="utf-8")
    p = _write(tmp_path, "p.md", text.replace("Para que: você não paga multa. (A2)", "Para que: você não paga multa. (A7)"))
    assert any(f["rule"] == "PIC-007" and "A7" in f["message"] for f in _errors(p))


def test_uppercase_slug_is_not_a_plan_requirement(tmp_path) -> None:
    text = (FIX / "v3_completo.md").read_text(encoding="utf-8")
    p = _write(tmp_path, "p.md", text.replace("- REQ-contas-002:", "- REQ-CONTAS-002:"))
    assert any(f["rule"] == "PIC-004" for f in _errors(p))


def test_usage_error_exits_2(tmp_path) -> None:
    proc = _run(str(tmp_path / "does-not-exist.md"))
    assert proc.returncode == 2


def test_registered_in_plugin_registry() -> None:
    reg = json.loads((SCRIPT.parent / "check_plugin_registry.json").read_text(encoding="utf-8"))
    assert any(e["script"] == "check_plan_intent.py" for e in reg)
