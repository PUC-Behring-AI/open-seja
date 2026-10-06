"""Tests for check_specify.py -- SPC-001 to SPC-018 over the golden fixtures.

Invocation: test
Lifecycle: active

Rules: .claude/references/general/specify-phase.md (SPC-NNN).
Fixtures: fixtures/specify/<case>/ (esperado.json per case; each case is a project root).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import check_specify
from check_specify import compute_status, main

_TESTS_DIR = Path(__file__).resolve().parent
_SCRIPTS = _TESTS_DIR.parent
_FIXTURES = _TESTS_DIR / "fixtures" / "specify"
_SPEC = _TESTS_DIR.parents[2] / "references" / "general" / "specify-phase.md"
_REGISTRY = _SCRIPTS / "check_plugin_registry.json"

CASES = sorted(p.name for p in _FIXTURES.iterdir() if p.is_dir() and (p / "esperado.json").is_file())
SLUG = "contas-da-semana"
AT = "2026-10-06T15:00Z"


def _expected(case: str) -> dict:
    return json.loads((_FIXTURES / case / "esperado.json").read_text(encoding="utf-8"))


def _copy(case: str, tmp_path: Path) -> Path:
    root = tmp_path / case
    shutil.copytree(_FIXTURES / case, root)
    return root


def _snapshot(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted((root / "features").rglob("*")) if p.is_file()}


def _run(root: Path, args: list[str], capsys) -> tuple[int, str]:
    code = main([str(root), *args])
    return code, capsys.readouterr().out


def _run_json(root: Path, args: list[str], capsys) -> tuple[int, dict]:
    code, out = _run(root, [*args, "--json"], capsys)
    return code, json.loads(out) if out.strip() else {}


@pytest.fixture
def no_validator(monkeypatch):
    monkeypatch.setattr(check_specify, "_cf", None)


# ---------------------------------------------------------------------------
# Golden cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case", CASES)
def test_golden_case(case: str, tmp_path: Path, capsys, monkeypatch) -> None:
    exp = _expected(case)
    if exp.get("simulate_missing_validator"):
        monkeypatch.setattr(check_specify, "_cf", None)
    root = _copy(case, tmp_path)
    before = _snapshot(root) if (root / "features").is_dir() else {}
    code, report = _run_json(root, exp["args"], capsys)
    assert code == exp["exit_code"], report
    if exp.get("unchanged"):
        assert _snapshot(root) == before
    if "--feature" not in exp["args"] or exp["exit_code"] == 2:
        return
    found = sorted([f["rule"], f["severity"], f["file"], f["line"]] for f in report["findings"])
    assert found == sorted(exp.get("findings", [])), report["findings"]
    if "status" in exp:
        assert report["status"] == exp["status"]
    if "reasons" in exp:
        assert report["reasons"] == exp["reasons"]
    if "reqs" in exp:
        assert report["reqs"] == exp["reqs"]
    if "intent_final" in exp:
        assert (root / "features" / SLUG / "intent.md").read_bytes() == (root / exp["intent_final"]).read_bytes()
        assert (root / "features" / SLUG / "scenarios.lock.json").read_bytes() == (root / exp["lock_final"]).read_bytes()


def test_every_checkable_rule_has_a_firing_case() -> None:
    fired = {f[0] for case in CASES for f in _expected(case).get("findings", [])}
    assert {"SPC-001", "SPC-003", "SPC-004", "SPC-007", "SPC-008", "SPC-011", "SPC-012", "SPC-017",
            "SPC-018"} <= fired


# ---------------------------------------------------------------------------
# SPC-010: approval record
# ---------------------------------------------------------------------------

APPROVE = ["--feature", SLUG, "--approve", "--at", AT, "--by", "usuario", "--contract-by", "usuario"]


def test_approve_twice_gives_identical_bytes(tmp_path: Path, capsys) -> None:
    root = _copy("ok-completo", tmp_path)
    assert _run(root, APPROVE, capsys)[0] == 0
    first = _snapshot(root)
    assert _run(root, APPROVE, capsys)[0] == 0
    assert _snapshot(root) == first


def test_approve_touches_only_the_frontmatter(tmp_path: Path, capsys) -> None:
    root = _copy("ok-completo", tmp_path)
    intent = root / "features" / SLUG / "intent.md"
    before = intent.read_text(encoding="utf-8")
    assert _run(root, APPROVE, capsys)[0] == 0
    after = intent.read_text(encoding="utf-8")
    body_before = before.split("---\n", 2)[2]
    body_after = after.split("---\n", 2)[2]
    assert body_before == body_after
    head = after.split("---\n", 2)[1]
    for key in ("scenarios: approved", f"scenarios_approved_at: {AT}", "scenarios_approved_by: usuario",
                "scenarios_contract_by: usuario", "scenarios_rev: 1"):
        assert key in head
    lock = json.loads((root / "features" / SLUG / "scenarios.lock.json").read_text(encoding="utf-8"))
    assert {"basis", "index", "files", "retraducao", "schema_version"} <= set(lock)


def test_approve_then_status_is_approved(tmp_path: Path, capsys) -> None:
    root = _copy("ok-completo", tmp_path)
    assert _run(root, APPROVE, capsys)[0] == 0
    assert compute_status(root, SLUG).status == "approved"


def test_approve_keeps_crlf_and_bom(tmp_path: Path, capsys) -> None:
    root = _copy("ok-completo", tmp_path)
    intent = root / "features" / SLUG / "intent.md"
    text = intent.read_text(encoding="utf-8")
    intent.write_bytes(b"\xef\xbb\xbf" + text.replace("\n", "\r\n").encode("utf-8"))
    assert _run(root, APPROVE, capsys)[0] == 0
    raw = intent.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    assert b"scenarios: approved\r\n" in raw
    assert raw.count(b"\r\n") == raw.count(b"\n")


@pytest.mark.parametrize("drop", ["--at", "--by", "--contract-by"])
def test_approve_requires_at_by_and_contract(drop: str, tmp_path: Path, capsys) -> None:
    root = _copy("ok-completo", tmp_path)
    args = list(APPROVE)
    i = args.index(drop)
    del args[i:i + 2]
    before = _snapshot(root)
    assert _run(root, args, capsys)[0] == 2
    assert _snapshot(root) == before


def test_approve_rejects_bad_timestamp(tmp_path: Path, capsys) -> None:
    root = _copy("ok-completo", tmp_path)
    args = [a if a != AT else "ontem" for a in APPROVE]
    assert _run(root, args, capsys)[0] == 2


def test_approve_with_warning_writes_nothing(tmp_path: Path, capsys) -> None:
    root = _copy("spc-007-26-palavras", tmp_path)
    before = _snapshot(root)
    assert _run(root, APPROVE, capsys)[0] == 1
    assert _snapshot(root) == before


def test_missing_validator_says_so(tmp_path: Path, capsys, no_validator) -> None:
    root = _copy("ok-completo", tmp_path)
    assert main([str(root), "--feature", SLUG]) == 2
    assert "validador de cenários não encontrado" in capsys.readouterr().err


def test_status_works_without_validator(tmp_path: Path, capsys, no_validator) -> None:
    root = _copy("spc-013-aprovado", tmp_path)
    code, report = _run_json(root, ["--feature", SLUG, "--status"], capsys)
    assert code == 0 and report["status"] == "approved"


# ---------------------------------------------------------------------------
# SPC-013: status transitions after an approval made by the tool itself
# ---------------------------------------------------------------------------


def test_editing_feature_after_approval_makes_it_stale(tmp_path: Path, capsys) -> None:
    root = _copy("ok-completo", tmp_path)
    assert _run(root, APPROVE, capsys)[0] == 0
    feature = root / "features" / SLUG / f"{SLUG}.feature"
    feature.write_text(feature.read_text(encoding="utf-8").replace("opção de desfazer", "botão de desfazer"),
                       encoding="utf-8")
    result = compute_status(root, SLUG)
    assert (result.status, result.reasons) == ("stale", ["feature"])


def test_new_rev_names_the_requirement(tmp_path: Path, capsys) -> None:
    root = _copy("spc-013-rev-subiu", tmp_path)
    result = compute_status(root, SLUG)
    assert result.status == "stale" and result.reqs == ["REQ-contas-da-semana-002"]


def test_unknown_lock_schema_exits_2(tmp_path: Path, capsys) -> None:
    root = _copy("spc-013-aprovado", tmp_path)
    lock = root / "features" / SLUG / "scenarios.lock.json"
    data = json.loads(lock.read_text(encoding="utf-8"))
    data["schema_version"] = 99
    lock.write_text(json.dumps(data), encoding="utf-8")
    assert main([str(root), "--feature", SLUG, "--status"]) == 2
    assert "schema_version" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# CLI robustness and determinism
# ---------------------------------------------------------------------------


def test_root_without_features_exits_0(tmp_path: Path, capsys) -> None:
    code, out = _run(tmp_path, [], capsys)
    assert code == 0 and "nada a verificar" in out


def test_feature_without_folder_refuses(tmp_path: Path, capsys) -> None:
    assert main([str(tmp_path), "--feature", "nao-existe"]) == 2
    assert "/plan --grill" in capsys.readouterr().err


@pytest.mark.parametrize("slug", ["../fora", "Maiuscula", "a/b"])
def test_bad_slug_exits_2(slug: str, tmp_path: Path, capsys) -> None:
    assert main([str(tmp_path), "--feature", slug]) == 2


def test_unreadable_intent_exits_2_without_traceback(tmp_path: Path) -> None:
    root = _copy("ok-completo", tmp_path)
    (root / "features" / SLUG / "intent.md").write_bytes(b"\xff\xfe\x00 nao e utf-8 \xff")
    proc = subprocess.run([sys.executable, str(_SCRIPTS / "check_specify.py"), str(root), "--feature", SLUG],
                          capture_output=True, text=True, check=False)
    assert proc.returncode == 2
    assert "Traceback" not in proc.stderr


def test_bom_intent_is_read(tmp_path: Path, capsys) -> None:
    root = _copy("ok-completo", tmp_path)
    intent = root / "features" / SLUG / "intent.md"
    intent.write_bytes(b"\xef\xbb\xbf" + intent.read_bytes())
    _code, report = _run_json(root, ["--feature", SLUG], capsys)
    assert not [f for f in report["findings"] if f["rule"] == "SPC-001"], report


def test_output_is_deterministic(tmp_path: Path, capsys) -> None:
    root = _copy("spc-017-req-sem-exemplo", tmp_path)
    first = _run(root, ["--feature", SLUG], capsys)
    second = _run(root, ["--feature", SLUG], capsys)
    assert first == second


def test_text_line_has_file_line_rule_and_hint(tmp_path: Path, capsys) -> None:
    root = _copy("spc-004-sem-numero", tmp_path)
    code, out = _run(root, ["--feature", SLUG], capsys)
    assert code == 1
    assert re.search(r"^features/contas-da-semana/contas-da-semana\.feature:\d+: SPC-004 erro: .+ Dica: .+$",
                     out, re.MULTILINE), out


def test_voice_caveat_travels_with_the_result(tmp_path: Path, capsys) -> None:
    root = _copy("ok-completo", tmp_path)
    _code, report = _run_json(root, ["--feature", SLUG], capsys)
    assert report["ressalvas"] == check_specify.ressalvas()


def test_constants_come_from_check_intent() -> None:
    import check_intent
    assert check_specify.MAX_SENTENCE_WORDS == check_intent.MAX_SENTENCE_WORDS
    assert check_specify.SPECIFY_MAX_ROUNDS == 3


# ---------------------------------------------------------------------------
# Spec, header and registry
# ---------------------------------------------------------------------------


def _spec_blocks() -> list[str]:
    return re.findall(r"```gherkin\n(.*?)```", _SPEC.read_text(encoding="utf-8"), re.DOTALL)


@pytest.mark.parametrize("lang", ["pt", "en"])
def test_spec_good_examples_pass_check_features_strict(lang: str, tmp_path: Path) -> None:
    blocks = _spec_blocks()
    assert len(blocks) == 4
    chosen = [b for b in blocks if ("@REQ-weekly-bills" in b) == (lang == "en")]
    case, slug = ("ok-en", "weekly-bills") if lang == "en" else ("ok-completo", SLUG)
    root = _copy(case, tmp_path)
    folder = root / "features" / slug
    for old in folder.glob("*.feature"):
        old.unlink()
    for n, block in enumerate(chosen, 1):
        (folder / f"example-{n}.feature").write_text(block, encoding="utf-8")
    proc = subprocess.run([sys.executable, str(_SCRIPTS / "check_features.py"), str(root), "--feature", slug,
                           "--strict"], capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_spec_lists_all_rules_with_who_and_criterion() -> None:
    text = _SPEC.read_text(encoding="utf-8")
    rules = re.findall(r"^### (SPC-\d{3}) ", text, re.MULTILINE)
    assert rules == [f"SPC-{n:03d}" for n in range(1, 19)]
    for block in re.split(r"^### SPC-", text, flags=re.MULTILINE)[1:]:
        assert "**Quem decide**" in block and "**Critério de aceitação**" in block


def test_header_and_registry() -> None:
    source = (_SCRIPTS / "check_specify.py").read_text(encoding="utf-8")
    assert source.startswith("#!/usr/bin/env python3\n# designer:")
    assert re.search(r"^Invocation: .*skill-invoked", source, re.MULTILINE)
    assert re.search(r"^Lifecycle: active$", source, re.MULTILINE)
    names = [entry["script"] for entry in json.loads(_REGISTRY.read_text(encoding="utf-8"))]
    assert "check_specify.py" in names
