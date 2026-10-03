"""Tests for step_notes.py (per-step reflection-on-action notes)."""
import json
import re
from pathlib import Path

import pytest

import step_notes

SKILL_MD = Path(__file__).resolve().parents[2] / "implement" / "SKILL.md"


@pytest.fixture
def plans(tmp_path, monkeypatch):
    d = tmp_path / "plans"
    d.mkdir()
    monkeypatch.setattr(step_notes, "_plans_dir", lambda: d)
    monkeypatch.setattr(step_notes, "REPO_ROOT", tmp_path)
    return d


def _gate(tmp_path, status="FAIL", code=4, version=1):
    p = tmp_path / "_output" / "quality" / "gate.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"version": version, "status": status, "exit_code": code}))
    return p


def _append(plan="000099", step=1, title="Do X", happened="Created x.py", deviated="none",
            less_sure="none", **kw):
    kw.setdefault("gate", "not-installed")
    return step_notes.append_note(plan, step, title, happened, deviated, less_sure, **kw)


def test_creates_progress_file_with_header_and_block(plans):
    path = _append()
    text = path.read_text()
    assert path == plans / "plan-000099-progress.md"
    assert text.startswith("# Progress -- Plan 000099\n")
    assert "- happened: Created x.py" in text
    assert "- gate: not-installed" in text
    assert len(step_notes.parse_notes(text)) == 1


def test_second_append_keeps_previous_bytes(plans):
    path = _append()
    before = path.read_bytes()
    _append(step=2, title="Do Y", happened="Edited y.py")
    assert path.read_bytes().startswith(before)
    assert len(step_notes.parse_notes(path.read_text())) == 2


def test_header_matches_implement_skill_verbatim_block(plans):
    skill = SKILL_MD.read_text()
    m = re.search(r"verbatim\):\n\s*```markdown\n(.*?)```", skill, re.S)
    assert m, "Phase 0 step 4 block not found"
    block = "\n".join(ln[3:] if ln.startswith("   ") else ln for ln in m[1].rstrip().splitlines()) + "\n"
    header = _append().read_text().split("### Step", 1)[0].rstrip("\n") + "\n"
    assert header == block.replace("<id>", "000099")


def test_gate_json_line(plans, tmp_path):
    g = _gate(tmp_path)
    path = _append(gate=None, gate_json=g, gate_attempts=2)
    assert "- gate: FAIL (exit 4, attempts 2, _output/quality/gate.json)" in path.read_text()
    n = step_notes.parse_notes(path.read_text())[0]
    assert (n.gate_status, n.gate_exit, n.gate_attempts) == ("FAIL", 4, 2)


@pytest.mark.parametrize("kw", [
    {"happened": ""}, {"happened": "do x!"}, {"deviated": ""}, {"less_sure": " "},
])
def test_refuses_bad_input_and_writes_nothing(plans, kw):
    with pytest.raises(step_notes.StepNotesError):
        _append(**kw)
    assert not list(plans.iterdir())


def test_refuses_missing_or_wrong_version_gate_json(plans, tmp_path):
    with pytest.raises(step_notes.StepNotesError):
        _append(gate=None, gate_json=tmp_path / "nope.json")
    with pytest.raises(step_notes.StepNotesError):
        _append(gate=None, gate_json=_gate(tmp_path, version=2))
    assert not list(plans.iterdir())


def test_cli_exit_2_on_refusal(plans, capsys):
    rc = step_notes.main(["append", "--plan", "99", "--step", "1", "--title", "T",
                          "--happened", "T", "--deviated", "none", "--less-sure", "none",
                          "--gate", "not-run"])
    assert rc == 2
    assert not list(plans.iterdir())


def test_human_verbatim(plans):
    path = _append(human='disse "ok" -- ação rápida')
    assert '- human: "disse "ok" -- ação rápida"' in path.read_text()
    assert step_notes.parse_notes(path.read_text())[0].human == 'disse "ok" -- ação rápida'


def test_parse_ignores_other_sections_and_free_lines(plans):
    path = _append()
    with path.open("a") as fh:
        fh.write("- step 1: free iteration log line\n\n## Other\ntext\n")
    _append(step=2, title="Do Y", happened="Edited y.py")
    notes = step_notes.parse_notes(path.read_text())
    assert [n.step for n in notes] == [1, 2]
    assert notes[0].gate_status == "not-installed"


def test_stats_duplicates_both_none(plans):
    path = _append(happened="Criou X.")
    _append(step=2, title="B", happened="criou x")
    _append(step=3, title="C", happened="Outro", deviated="mudou algo")
    s = step_notes.stats(step_notes.parse_notes(path.read_text()))
    assert s["notes"] == 3 and s["duplicate_happened"] == 1
    assert s["both_none"] == 2 and s["with_deviation"] == 1 and s["with_gate"] == 0


def test_parse_cli_json_stats(plans, capsys):
    path = _append()
    assert step_notes.main(["parse", str(path), "--json", "--stats"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["stats"]["notes"] == 1 and out["notes"][0]["less_sure"] == "none"


def _plan(plans, body):
    p = plans / "plan-000099-demo.md"
    p.write_text(body)
    return p


def test_reflect_bullet_inserts_in_existing_section(plans):
    _append()
    plan = _plan(plans, "# P\n\n## Reflection\n\n- 2026-01-01: old\n\n## Steps\n- [ ] x\n")
    step_notes.reflect_bullet("99", "Step 1 foi limpo.", today="2026-10-03")
    text = plan.read_text()
    assert text == (
        "# P\n\n## Reflection\n\n- 2026-01-01: old\n"
        "- 2026-10-03: Step 1 foi limpo. (notes 1, with deviation 0, with gate 0)\n"
        "\n## Steps\n- [ ] x\n"
    )


def test_reflect_bullet_creates_section_at_eof(plans):
    _append()
    plan = _plan(plans, "# P\n\n## Steps\n- [ ] x\n")
    step_notes.reflect_bullet("99", "Resumo.", today="2026-10-03")
    assert plan.read_text() == (
        "# P\n\n## Steps\n- [ ] x\n\n## Reflection\n\n"
        "- 2026-10-03: Resumo. (notes 1, with deviation 0, with gate 0)\n"
    )
