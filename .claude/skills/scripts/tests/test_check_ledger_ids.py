"""Tests for check_ledger_ids.py (plan-000019 Step 8): duplicate and orphan IDs in the ledger."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from artifact_id import _encode, visible_id

SCRIPT = Path(__file__).resolve().parent.parent / "check_ledger_ids.py"
CLEAN = Path(__file__).resolve().parent / "fixtures" / "ledger_ids" / "clean"


def _ulid_at(dt: datetime, tail: str = "K3M9QZ") -> str:
    ms = int(dt.timestamp() * 1000)
    return _encode(ms, 10) + "0" * (16 - len(tail)) + tail


def _record(uid: str, **overrides) -> dict:
    rec = {
        "schema_version": 1,
        "uid": uid,
        "id": visible_id(uid),
        "type": "plan",
        "title": "t",
        "author": "abc123",
        "ts_utc": datetime.fromtimestamp(
            int(_ms(uid)) / 1000, tz=timezone.utc
        ).isoformat(),
        "origin": None,
    }
    rec.update(overrides)
    return rec


def _ms(uid: str) -> int:
    from artifact_id import ulid_timestamp

    return int(ulid_timestamp(uid).timestamp() * 1000)


def _write_record(out: Path, rec: dict, name: str | None = None) -> Path:
    ids = out / "ids"
    ids.mkdir(parents=True, exist_ok=True)
    p = ids / f"{name or rec['uid']}.json"
    p.write_text(json.dumps(rec), encoding="utf-8")
    return p


def _touch(path: Path, text: str = "# x\n") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _run(out: Path, *args: str, design: Path | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPT), "--output-dir", str(out), *args]
    if design is not None:
        cmd += ["--design-file", str(design)]
    return subprocess.run(
        cmd, capture_output=True, text=True, check=False, env=dict(os.environ)
    )


@pytest.fixture
def ledger(tmp_path: Path) -> Path:
    out = tmp_path / "_output"
    (out / "plans").mkdir(parents=True)
    return out


# --- (1) duplicate artifact ID -------------------------------------------------


def test_duplicate_plan_id_returns_1_and_lists_both_paths(ledger: Path) -> None:
    a = _touch(ledger / "plans" / "plan-000007-a.md")
    b = _touch(ledger / "plans" / "plan-000007-b.md")
    r = _run(ledger)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "000007" in r.stdout
    assert str(a.relative_to(ledger)) in r.stdout
    assert str(b.relative_to(ledger)) in r.stdout


def test_duplicate_across_types_is_also_duplicate(ledger: Path) -> None:
    _touch(ledger / "plans" / "plan-000021-a.md")
    _touch(ledger / "communication" / "2026-10-07" / "communication-000021-b.md")
    assert _run(ledger).returncode == 1


def test_duplicate_new_format_id(ledger: Path) -> None:
    _touch(ledger / "plans" / "plan-20261007-k3m9qz-a.md")
    _touch(ledger / "research-logs" / "research-20261007-k3m9qz-b.md")
    assert _run(ledger).returncode == 1


def test_companions_do_not_count_as_duplicates(ledger: Path) -> None:
    _touch(ledger / "plans" / "plan-000007-a.md")
    _touch(ledger / "plans" / "plan-000007-qa-a.md")
    _touch(ledger / "plans" / "plan-000007-progress.md")
    _touch(ledger / "reflections" / "reflection-000017-x.md")
    _touch(ledger / "reflections" / "reflection-000017-qa-x.md")
    r = _run(ledger)
    assert r.returncode == 0, r.stdout


def test_legacy_id_does_not_match_prefix_of_new_id(ledger: Path) -> None:
    # 20261007-k3m9qz must not be read as legacy 202610.
    _touch(ledger / "plans" / "plan-20261007-k3m9qz-a.md")
    _touch(ledger / "plans" / "plan-202610-b.md")
    assert _run(ledger).returncode == 0


# --- (2) orphan birth record ---------------------------------------------------


def test_orphan_record_older_than_threshold_warns_then_fails_strict(ledger: Path) -> None:
    uid = _ulid_at(datetime.now(timezone.utc) - timedelta(days=10))
    _write_record(ledger, _record(uid))
    r = _run(ledger)
    assert r.returncode == 0, r.stdout
    assert "orphan" in r.stdout.lower()
    assert visible_id(uid) in r.stdout
    assert _run(ledger, "--strict").returncode == 1


def test_recent_orphan_is_silent(ledger: Path) -> None:
    uid = _ulid_at(datetime.now(timezone.utc) - timedelta(days=1))
    _write_record(ledger, _record(uid))
    r = _run(ledger, "--strict")
    assert r.returncode == 0
    assert "orphan" not in r.stdout.lower()


def test_orphan_days_option(ledger: Path) -> None:
    uid = _ulid_at(datetime.now(timezone.utc) - timedelta(days=3))
    _write_record(ledger, _record(uid))
    assert _run(ledger, "--strict", "--orphan-days", "2").returncode == 1
    assert _run(ledger, "--strict", "--orphan-days", "5").returncode == 0


def test_record_with_artifact_is_not_orphan(ledger: Path) -> None:
    uid = _ulid_at(datetime.now(timezone.utc) - timedelta(days=30))
    _write_record(ledger, _record(uid))
    _touch(ledger / "plans" / f"plan-{visible_id(uid)}-x.md")
    assert _run(ledger, "--strict").returncode == 0


# --- (3) duplicate pa- ---------------------------------------------------------


def _pending(out: Path, *records: dict) -> None:
    (out / "pending.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in records), encoding="utf-8"
    )


def test_pa_created_twice_returns_1(ledger: Path) -> None:
    _pending(
        ledger,
        {"id": "pa-000012", "created_at": "2026-10-01T00:00:00Z", "status": "pending"},
        {"id": "pa-000012", "created_at": "2026-10-02T00:00:00Z", "status": "pending"},
    )
    r = _run(ledger)
    assert r.returncode == 1
    assert "pa-000012" in r.stdout


def test_pa_created_then_updated_returns_0(ledger: Path) -> None:
    _pending(
        ledger,
        {"id": "pa-000012", "created_at": "2026-10-01T00:00:00Z", "status": "pending"},
        {"id": "pa-000012", "status": "done", "closed_at": "2026-10-02T00:00:00Z"},
    )
    assert _run(ledger).returncode == 0


# --- (4) duplicate D-NNN -------------------------------------------------------


_DESIGN = """\
# DESIGN INTENT

## 3. Concepts

### D-005: not in Decisions, ignored

## Decisions

### D-004: four

### D-005: five

{extra}
## CHANGELOG

### D-004: not in Decisions either
"""


def test_duplicate_decision_heading_returns_1(ledger: Path, tmp_path: Path) -> None:
    design = _touch(tmp_path / "d.md", _DESIGN.format(extra="### D-005: five again\n"))
    r = _run(ledger, design=design)
    assert r.returncode == 1
    assert "D-005" in r.stdout


def test_decision_headings_outside_section_ignored(ledger: Path, tmp_path: Path) -> None:
    design = _touch(tmp_path / "d.md", _DESIGN.format(extra=""))
    assert _run(ledger, design=design).returncode == 0


def test_default_design_file_is_sibling_product_design(ledger: Path) -> None:
    _touch(
        ledger.parent / "product-design" / "product-design-as-intended.md",
        _DESIGN.format(extra="### D-005: dup\n"),
    )
    assert _run(ledger).returncode == 1


# --- (5) duplicate uid, (6) incoherent id ---------------------------------------


def test_duplicate_uid_returns_1(ledger: Path) -> None:
    uid = _ulid_at(datetime.now(timezone.utc))
    _touch(ledger / "plans" / f"plan-{visible_id(uid)}-x.md")
    _write_record(ledger, _record(uid))
    _write_record(ledger, _record(uid), name="copy")
    r = _run(ledger)
    assert r.returncode == 1
    assert uid in r.stdout


def test_incoherent_id_returns_1(ledger: Path) -> None:
    uid = _ulid_at(datetime.now(timezone.utc))
    _touch(ledger / "plans" / "plan-20200101-aaaaaa-x.md")
    _write_record(ledger, _record(uid, id="20200101-aaaaaa"))
    r = _run(ledger)
    assert r.returncode == 1
    assert "20200101-aaaaaa" in r.stdout


def test_unreadable_record_returns_1(ledger: Path) -> None:
    (ledger / "ids").mkdir()
    (ledger / "ids" / "broken.json").write_text("{not json", encoding="utf-8")
    assert _run(ledger).returncode == 1


# --- shell behaviour -------------------------------------------------------------


def test_missing_output_dir_returns_0_without_output(tmp_path: Path) -> None:
    r = _run(tmp_path / "nope")
    assert r.returncode == 0
    assert r.stdout == ""
    r = _run(tmp_path / "nope", "--json")
    assert r.returncode == 0
    assert r.stdout == ""


def test_usage_error_returns_2(ledger: Path) -> None:
    assert _run(ledger, "--orphan-days", "abc").returncode == 2


def test_clean_fixture_returns_0_and_json_has_empty_lists(tmp_path: Path) -> None:
    root = tmp_path / "clean"
    shutil.copytree(CLEAN, root)
    out = root / "_output"
    r = _run(out, "--strict")
    assert r.returncode == 0, r.stdout
    r = _run(out, "--json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["schema_version"] == 1
    assert data["errors"] == []
    assert data["warnings"] == []


def test_json_reports_errors(ledger: Path) -> None:
    _touch(ledger / "plans" / "plan-000007-a.md")
    _touch(ledger / "plans" / "plan-000007-b.md")
    r = _run(ledger, "--json")
    assert r.returncode == 1
    data = json.loads(r.stdout)
    assert data["schema_version"] == 1
    assert [e["kind"] for e in data["errors"]] == ["duplicate-id"]
    assert sorted(data["errors"][0]["paths"]) == [
        "plans/plan-000007-a.md",
        "plans/plan-000007-b.md",
    ]


def test_deterministic_output(ledger: Path) -> None:
    _touch(ledger / "plans" / "plan-000007-b.md")
    _touch(ledger / "plans" / "plan-000007-a.md")
    _touch(ledger / "plans" / "plan-000008-a.md")
    _touch(ledger / "research-logs" / "research-000008-b.md")
    first = _run(ledger).stdout
    time.sleep(0.01)
    assert _run(ledger).stdout == first
