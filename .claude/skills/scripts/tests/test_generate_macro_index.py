"""Tests for generate_macro_index.py -- unified artifact index generator."""
from __future__ import annotations

import json
from pathlib import Path

import generate_macro_index as gen
import pytest

FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "generate_macro_index"


# ---------------------------------------------------------------------------
# Reflection header extraction
# ---------------------------------------------------------------------------


def test_extract_reflection_header(tmp_path, monkeypatch):
    """A reflection file with the canonical header is recognized as type 'Reflection'."""
    output_dir = tmp_path / "_output"
    reflections_dir = output_dir / "reflections"
    reflections_dir.mkdir(parents=True)

    stub = reflections_dir / "reflection-999999-smoke-stub.md"
    stub.write_text(
        "# Reflection 999999 | 2026-04-11 22:45 UTC | Smoke stub\n"
        "\n"
        "Stub body for test fixture.\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(gen, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(gen, "INDEX_FILE", output_dir / "INDEX.md")

    entry = gen.extract_artifact(stub)
    assert entry is not None, "extract_artifact returned None for reflection file"
    assert entry["type"] == "Reflection"
    assert entry["id"] == "999999"
    assert entry["title"] == "Smoke stub"
    assert entry["date"] == "2026-04-11 22:45 UTC"
    assert entry["status"] == ""
    assert entry["file"].replace("\\", "/") == "reflections/reflection-999999-smoke-stub.md"


def test_generate_index_includes_reflection(tmp_path, monkeypatch):
    """Running generate_index over a tmp OUTPUT_DIR with a reflection produces an INDEX row."""
    output_dir = tmp_path / "_output"
    reflections_dir = output_dir / "reflections"
    reflections_dir.mkdir(parents=True)

    stub = reflections_dir / "reflection-999999-smoke-stub.md"
    stub.write_text(
        "# Reflection 999999 | 2026-04-11 22:45 UTC | Smoke stub\n",
        encoding="utf-8",
    )

    index_file = output_dir / "INDEX.md"
    monkeypatch.setattr(gen, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gen, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(gen, "INDEX_FILE", index_file)

    count = gen.generate_index(verbose=False)
    assert count >= 1

    content = index_file.read_text(encoding="utf-8")
    assert "| Reflection |" in content, "Reflection type row missing from INDEX"
    assert "999999" in content
    assert "Smoke stub" in content
    assert "reflections/reflection-999999-smoke-stub.md" in content.replace("\\", "/")


def test_generate_index_skips_missing_reflections_dir(tmp_path, monkeypatch):
    """If OUTPUT_DIR has no reflections/ subdir, the generator still runs cleanly."""
    output_dir = tmp_path / "_output"
    output_dir.mkdir()
    # intentionally: no reflections/ subdir

    index_file = output_dir / "INDEX.md"
    monkeypatch.setattr(gen, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gen, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(gen, "INDEX_FILE", index_file)

    count = gen.generate_index(verbose=False)
    # Count may be 0 (no artifacts at all); the point is no exception was raised.
    assert count == 0
    content = index_file.read_text(encoding="utf-8")
    assert "# Artifact Index" in content


# ---------------------------------------------------------------------------
# Mob Session header extraction
# ---------------------------------------------------------------------------


def test_extract_mob_session_header(tmp_path, monkeypatch):
    """A mob-session record with the canonical header is recognized as type 'Mob Session'."""
    output_dir = tmp_path / "_output"
    mob_dir = output_dir / "mob-sessions"
    mob_dir.mkdir(parents=True)

    record = mob_dir / "mob-session-000001-x.md"
    record.write_text(
        "# Mob Session 000001 | 2026-09-26 14:00 UTC | Filtro de tarefas\n"
        "\n"
        "## Objetivo\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(gen, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(gen, "INDEX_FILE", output_dir / "INDEX.md")

    entry = gen.extract_artifact(record)
    assert entry is not None
    assert entry["type"] == "Mob Session"
    assert entry["id"] == "000001"
    assert entry["title"] == "Filtro de tarefas"
    assert entry["date"] == "2026-09-26 14:00 UTC"
    assert entry["file"].replace("\\", "/") == "mob-sessions/mob-session-000001-x.md"


def test_generate_index_includes_mob_session_and_skips_siblings(tmp_path, monkeypatch):
    """generate_index lists the mob-session record once; agenda/timer/state siblings are not indexed."""
    output_dir = tmp_path / "_output"
    mob_dir = output_dir / "mob-sessions"
    mob_dir.mkdir(parents=True)

    (mob_dir / "mob-session-000001-x.md").write_text(
        "# Mob Session 000001 | 2026-09-26 14:00 UTC | Filtro de tarefas\n",
        encoding="utf-8",
    )
    (mob_dir / "mob-session-000001-agenda.json").write_text("{}", encoding="utf-8")
    (mob_dir / "mob-session-000001-timer.jsonl").write_text("{}\n", encoding="utf-8")
    (mob_dir / "mob-session-000001-state.json").write_text("{}", encoding="utf-8")

    index_file = output_dir / "INDEX.md"
    monkeypatch.setattr(gen, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gen, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(gen, "INDEX_FILE", index_file)

    count = gen.generate_index(verbose=False)
    assert count == 1

    content = index_file.read_text(encoding="utf-8").replace("\\", "/")
    assert (
        "| 2026-09-26 14:00 UTC | Mob Session | 000001 | Filtro de tarefas |" in content
    )
    assert "mob-sessions/mob-session-000001-x.md" in content
    for sibling in ("agenda.json", "timer.jsonl", "state.json"):
        assert sibling not in content


# ---------------------------------------------------------------------------
# plan-000019 Step 3: INDEX.md fully derived; both ID formats
# ---------------------------------------------------------------------------

NEW_ID = "20261007-k3m9qz"


def _setup(tmp_path, monkeypatch):
    output_dir = tmp_path / "_output"
    output_dir.mkdir()
    index_file = output_dir / "INDEX.md"
    monkeypatch.setattr(gen, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(gen, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(gen, "INDEX_FILE", index_file)
    return output_dir, index_file


def _write_birth(output_dir, vid, type_="plan", title="novo-plano"):
    ids_dir = output_dir / "ids"
    ids_dir.mkdir(exist_ok=True)
    record = {
        "schema_version": 1,
        "uid": "01K6ZZZZZZZZZZZZZZZZK3M9QZ",
        "id": vid,
        "type": type_,
        "title": title,
        "author": "abcdef012345",
        "ts_utc": "2026-10-07T18:53:12.345000+00:00",
        "origin": None,
    }
    (ids_dir / f"{record['uid']}.json").write_text(json.dumps(record), encoding="utf-8")


def test_reserved_row_from_ids_dir_when_artifact_missing(tmp_path, monkeypatch):
    output_dir, index_file = _setup(tmp_path, monkeypatch)
    _write_birth(output_dir, NEW_ID)
    gen.generate_index()
    content = index_file.read_text(encoding="utf-8")
    assert (
        f"| 2026-10-07 18:53 UTC | RESERVED | {NEW_ID} | plan: novo-plano | RESERVED |  |"
        in content
    )


def test_reserved_row_absent_when_artifact_exists(tmp_path, monkeypatch):
    output_dir, index_file = _setup(tmp_path, monkeypatch)
    _write_birth(output_dir, NEW_ID)
    plans = output_dir / "plans"
    plans.mkdir()
    (plans / f"plan-{NEW_ID}-novo-plano.md").write_text(
        f"# Plan {NEW_ID} | FEATURE-O | 2026-10-07 18:53 UTC | novo plano | Review: light\n",
        encoding="utf-8",
    )
    gen.generate_index()
    content = index_file.read_text(encoding="utf-8")
    assert "RESERVED" not in content
    assert f"| Plan | {NEW_ID} | novo plano | OPEN |" in content


def test_plan_header_with_new_id_is_plan(tmp_path, monkeypatch):
    output_dir, _ = _setup(tmp_path, monkeypatch)
    fp = output_dir / f"plan-{NEW_ID}-t.md"
    fp.write_text(
        f"# Plan {NEW_ID} | FEATURE-O | 2026-10-07 10:00 UTC | t | Review: light\n",
        encoding="utf-8",
    )
    entry = gen.extract_artifact(fp)
    assert entry["type"] == "Plan"
    assert entry["id"] == NEW_ID
    assert entry["status"] == "OPEN"


@pytest.mark.parametrize(
    "header,status",
    [
        ("# Plan 000015 | FEATURE-O | METACOMM | 2026-10-05 12:55 UTC | wiring | Review: deep", "OPEN"),
        (f"# Plan {NEW_ID} | FEATURE-O | METACOMM | 2026-10-05 12:55 UTC | wiring | Review: deep", "OPEN"),
        ("# DONE | 2026-10-06 16:59 UTC | Plan 000007 | FEATURE-O | METACOMM | 2026-10-05 02:00 UTC | wiring", "DONE"),
        ("# Plan 000007 | DONE | FEATURE-O | METACOMM | 2026-10-05 02:00 UTC | wiring", "DONE"),
    ],
)
def test_plan_header_with_metacomm_is_plan(tmp_path, monkeypatch, header, status):
    output_dir, _ = _setup(tmp_path, monkeypatch)
    fp = output_dir / "plan-x.md"
    fp.write_text(header + "\n", encoding="utf-8")
    entry = gen.extract_artifact(fp)
    assert entry["type"] == "Plan"
    assert entry["id"] in {"000015", "000007", NEW_ID}
    assert entry["title"] == "wiring"
    assert entry["status"] == status


def test_two_line_done_marker_is_plan(tmp_path, monkeypatch):
    """/implement marks DONE on its own line above the plan H1."""
    output_dir, _ = _setup(tmp_path, monkeypatch)
    fp = output_dir / "plan-000007-x.md"
    fp.write_text(
        "# DONE | 2026-10-06 16:59 UTC |\n"
        "# Plan 000007 | FEATURE-O | METACOMM | 2026-10-05 02:00 UTC | contrato | Review: standard\n",
        encoding="utf-8",
    )
    entry = gen.extract_artifact(fp)
    assert entry["type"] == "Plan"
    assert entry["id"] == "000007"
    assert entry["status"] == "DONE"
    assert entry["title"] == "contrato"


def test_companion_qa_of_new_plan_is_not_plan(tmp_path, monkeypatch):
    output_dir, _ = _setup(tmp_path, monkeypatch)
    fp = output_dir / f"plan-{NEW_ID}-qa-x.md"
    fp.write_text(
        f"# Plan {NEW_ID} | FEATURE-O | 2026-10-07 10:00 UTC | x | Review: light\n",
        encoding="utf-8",
    )
    entry = gen.extract_artifact(fp)
    assert entry["type"] == "Plan QA"


def test_qa_log_with_new_parent_id(tmp_path, monkeypatch):
    output_dir, _ = _setup(tmp_path, monkeypatch)
    fp = output_dir / f"plan-{NEW_ID}-qa-x.md"
    fp.write_text(
        f"# QA Log | Plan {NEW_ID} | 2026-10-07 10:00 UTC | x\n", encoding="utf-8"
    )
    entry = gen.extract_artifact(fp)
    assert entry["type"] == "QA Log"
    assert entry["id"] == NEW_ID
    fp.write_text(f"# QA Log | Plan {NEW_ID} | sem data\n", encoding="utf-8")
    entry = gen.extract_artifact(fp)
    assert entry["type"] == "QA Log"
    assert entry["id"] == NEW_ID


def test_old_reserved_rows_are_not_preserved(tmp_path, monkeypatch):
    _, index_file = _setup(tmp_path, monkeypatch)
    index_file.write_text(
        "| Date | Type | ID | Title | Status | File |\n"
        "|------|------|----|-------|--------|------|\n"
        "| 2026-08-27 00:52 UTC | RESERVED | 000003 | qa: o-que-e-o-seja | RESERVED |  |\n",
        encoding="utf-8",
    )
    gen.generate_index()
    assert "000003" not in index_file.read_text(encoding="utf-8")


def test_finalize_is_deprecated_noop(tmp_path, monkeypatch, capsys):
    _, index_file = _setup(tmp_path, monkeypatch)
    monkeypatch.setattr("sys.argv", ["generate_macro_index.py", "--finalize", "000007"])
    try:
        gen.main()
    except SystemExit as exc:
        assert exc.code in (0, None)
    err = capsys.readouterr().err
    assert "deprecated" in err
    assert not index_file.exists()
