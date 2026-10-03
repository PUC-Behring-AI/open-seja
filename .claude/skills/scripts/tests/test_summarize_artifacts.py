"""Tests for summarize_artifacts.py."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from summarize_artifacts import summarize, as_markdown_block, _infer_type  # type: ignore


def test_resolves_plan_id():
    results = summarize(["plan-000295"])
    assert len(results) == 1
    r = results[0]
    assert "error" not in r
    assert r["id"] == "000295"
    assert r["type"] == "plan"
    assert "path" in r
    assert r["path"].endswith(".md")


def test_extracts_header_fields():
    results = summarize(["advisory-000300"])
    assert len(results) == 1
    r = results[0]
    assert "error" not in r
    assert r["id"] == "000300"
    assert r["type"] == "advisory"
    assert r["title"]
    assert r["datetime"]


def test_resolve_prefers_canonical_over_progress_companion():
    """plan-000295 has a -progress.md companion (and a -qa- companion) alongside the
    canonical header file; resolution must pick the header-bearing canonical file,
    not a companion, so the bare id 000295 is returned."""
    results = summarize(["plan-000295"])
    assert len(results) == 1
    r = results[0]
    assert "error" not in r
    assert r["id"] == "000295"
    assert not r["path"].endswith("-progress.md")
    assert "-qa-" not in r["path"]
    assert r["path"].endswith("plan-000295-reflect-skill-telemetry-expansion.md")


def test_resolve_prefers_canonical_over_qa_companion():
    """advisory-000300 has a -qa- companion alongside the canonical header file;
    resolution must pick the canonical file, not the qa companion."""
    results = summarize(["advisory-000300"])
    assert len(results) == 1
    r = results[0]
    assert "error" not in r
    assert r["id"] == "000300"
    assert "-qa-" not in r["path"]
    assert r["path"].endswith("advisory-000300-make-reflect-on-demand-and-less-intrusive.md")


def test_not_found_returns_error():
    results = summarize(["plan-999999"])
    assert len(results) == 1
    r = results[0]
    assert "error" in r
    assert r["id"] == "plan-999999"


def test_as_markdown_block_format():
    summaries = [
        {"id": "000300", "type": "advisory", "path": "_output/advisory-logs/test.md",
         "title": "Test", "datetime": "2026-04-12 01:49 UTC",
         "brief_excerpt": "A brief.", "interpretation_excerpt": "An interpretation."},
        {"id": "plan-999999", "error": "not found"},
    ]
    block = as_markdown_block(summaries)
    assert "[advisory-000300]" in block
    assert "**Brief**" in block
    assert "not found" in block


def test_infer_type_research():
    """Research log paths should map to type 'research' per advisory-000448 rename."""
    path = Path("_output/research-logs/research-000450-example.md")
    assert _infer_type(path) == "research"


def test_infer_type_advisory_preserved():
    """Historical advisory-logs paths still map to type 'advisory'."""
    path = Path("_output/advisory-logs/advisory-000431-example.md")
    assert _infer_type(path) == "advisory"


def test_resolve_path_regex_accepts_research_prefix():
    """The ID-normalisation regex must strip the 'research-' prefix."""
    # Mirrors the regex used inside _resolve_path -- kept in sync with summarize_artifacts.py line ~33.
    _PREFIX_RE = re.compile(r"^(?:plan|advisory|research|reflection|inventory|proposal|check)-")
    assert _PREFIX_RE.match("research-999999-x") is not None
    # Confirm the legacy advisory prefix still matches.
    assert _PREFIX_RE.match("advisory-000431-framework-simplification") is not None


def test_as_markdown_block_research_type():
    """Markdown block renders 'research-<id>' prefix for research-type summaries."""
    summaries = [
        {"id": "000450", "type": "research", "path": "_output/research-logs/research-000450-x.md",
         "title": "A research output", "datetime": "2026-04-19 20:00 UTC",
         "brief_excerpt": "A brief.", "interpretation_excerpt": "An interpretation."},
    ]
    block = as_markdown_block(summaries)
    assert "[research-000450]" in block


# ---------------------------------------------------------------------------
# Plan evidence (step notes, gate, communication, drift)
# ---------------------------------------------------------------------------

import pytest  # noqa: E402

import summarize_artifacts as sa  # type: ignore  # noqa: E402

_PLAN_HEADER = "# Plan 000777 | x | 2026-10-03 10:00 UTC | Evidence plan\n\n## User brief\nA brief.\n"
_NOTE = (
    "### Step {n} -- reflection-on-action | 2026-10-03 10:0{n} UTC | {title}\n"
    "- happened: did thing {n}\n"
    "- deviated: {dev}\n"
    "- less-sure: {ls}\n"
    "- gate: {gate}\n"
)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    out = tmp_path / "_output"
    (out / "plans").mkdir(parents=True)
    monkeypatch.setattr(sa, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(sa, "get_path", lambda name: out)
    return tmp_path


def _write_plan(repo, progress: str | None):
    plans = repo / "_output" / "plans"
    (plans / "plan-000777-evidence.md").write_text(_PLAN_HEADER, encoding="utf-8")
    if progress is not None:
        (plans / "plan-000777-progress.md").write_text(progress, encoding="utf-8")


def _two_notes(repo) -> str:
    gate_dir = repo / "gates"
    gate_dir.mkdir()
    (gate_dir / "s1.json").write_text("{}", encoding="utf-8")
    return (
        "# Progress\n\n"
        + _NOTE.format(n=1, title="One", dev="none", ls="none",
                       gate="PASS (exit 0, attempts 1, gates/s1.json)")
        + "\n"
        + _NOTE.format(n=2, title="Two", dev="used other lib", ls="you should retry X",
                       gate="FAIL (exit 1, attempts 2, gates/missing.json)")
    )


def test_plan_with_notes_reports_deviation_and_gate(repo):
    _write_plan(repo, _two_notes(repo))
    s = summarize(["plan-000777"])[0]
    assert [n["step"] for n in s["step_notes"]] == [1, 2]
    assert s["gate_evidence"]["first_attempt_pass"] == 1
    assert s["gate_evidence"]["total"] == 2
    block = as_markdown_block([s])
    assert "**Step notes**: 2 notes; deviations in steps 2" in block
    assert "1/2 steps PASS on first attempt" in block
    assert "FAIL/ERROR in steps 2" in block
    assert "[gates/s1.json]" in block
    assert "(json missing)" in block


def test_less_sure_is_quoted_and_attributed(repo):
    _write_plan(repo, _two_notes(repo))
    block = as_markdown_block(summarize(["plan-000777"]))
    assert 'step 2, agent recorded (less sure): "you should retry X"' in block
    for line in block.splitlines():
        if "you should" in line:
            assert 'agent recorded (less sure): "' in line
    stripped = re.sub(r'"[^"]*"', "", block)
    for phrase in ("you should", "consider", "we recommend"):
        assert phrase not in stripped.lower()


def test_plan_without_progress_file(repo):
    _write_plan(repo, None)
    s = summarize(["plan-000777"])[0]
    assert s["step_notes"] == []
    block = as_markdown_block([s])
    assert "**Step notes**: no step notes recorded" in block
    assert "not offered" in block


def test_not_run_listed(repo):
    _write_plan(repo, "# P\n\n" + _NOTE.format(n=1, title="One", dev="none", ls="none", gate="not-run"))
    block = as_markdown_block(summarize(["plan-000777"]))
    assert "0/1 steps PASS on first attempt" in block
    assert "not-run in steps 1" in block


def test_research_has_no_plan_evidence(repo):
    d = repo / "_output" / "research-logs"
    d.mkdir()
    (d / "research-000778-x.md").write_text(
        "# Research 000778 | x | 2026-10-03 10:00 UTC | R\n\n## Problem\nP.\n", encoding="utf-8")
    s = summarize(["research-000778"])[0]
    assert "step_notes" not in s
    block = as_markdown_block([s])
    assert "Step notes" not in block and "Gate evidence" not in block
    assert "Communication evidence" not in block


def test_communication_declined_and_drift_with_report(repo):
    rd = repo / "_output" / "research-logs"
    rd.mkdir()
    (rd / "research-000123-x.md").write_text(
        "# Research 000123 | x | 2026-10-03 10:00 UTC | Drift report\n", encoding="utf-8")
    prog = _two_notes(repo) + (
        "\n- communication: declined\n"
        "- drift: _output/research-logs/research-000123-x.md (3 itens)\n"
    )
    _write_plan(repo, prog)
    s = summarize(["plan-000777"])[0]
    assert s["communication_evidence"] == {"status": "declined"}
    assert s["drift_evidence"]["items"] == 3
    block = as_markdown_block([s])
    assert "**Communication evidence**: declined" in block
    assert "**Drift evidence**: 3 items, [" in block
    assert 'report header: "# Research 000123 | x | 2026-10-03 10:00 UTC | Drift report"' in block


def test_communication_path_and_drift_not_measured(repo):
    _write_plan(repo, "# P\n\n- communication: _output/communication/c.md (leadership)\n- drift: not-measured\n")
    block = as_markdown_block(summarize(["plan-000777"]))
    assert "**Communication evidence**: leadership, [_output/communication/c.md]" in block
    assert "**Drift evidence**: not measured" in block


def test_no_record_lines_say_not_offered(repo):
    _write_plan(repo, _two_notes(repo))
    block = as_markdown_block(summarize(["plan-000777"]))
    assert "**Communication evidence**: not offered" in block
    assert "**Drift evidence**: not offered" in block


def test_drift_report_missing_on_disk(repo):
    _write_plan(repo, "# P\n\n- drift: _output/research-logs/gone.md (2 itens)\n")
    block = as_markdown_block(summarize(["plan-000777"]))
    assert "2 items" in block
    assert "(report missing)" in block
