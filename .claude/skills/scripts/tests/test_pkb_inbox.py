"""Tests for pkb_inbox.py (init)."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = SCRIPTS_DIR / "pkb_inbox.py"

sys.path.insert(0, str(SCRIPTS_DIR))

import pkb_inbox  # noqa: E402

TEMPLATE_ROOT = SCRIPTS_DIR.parent.parent / "references" / "template" / "pkb"


def _hashes(root: Path) -> dict[str, str]:
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def test_init_with_skills_creates_layer(tmp_path):
    result = pkb_inbox.init_layer(tmp_path, TEMPLATE_ROOT, True, False)
    assert (tmp_path / "inbox" / "README.md").is_file()
    assert len(list((tmp_path / "Templates").glob("*.md"))) == 6
    assert (tmp_path / ".claude" / "skills" / "daily-log" / "SKILL.md").is_file()
    assert (tmp_path / "inbox" / ".gitkeep").is_file()
    assert any((tmp_path / "logs").glob("*/.gitkeep"))
    assert result["created"] and result["skipped"] == []


def test_init_without_skills_leaves_claude_untouched(tmp_path):
    pkb_inbox.init_layer(tmp_path, TEMPLATE_ROOT, False, False)
    assert not (tmp_path / ".claude").exists()
    assert (tmp_path / "Objetivos.md").is_file()


def test_init_is_idempotent(tmp_path):
    pkb_inbox.init_layer(tmp_path, TEMPLATE_ROOT, True, False)
    before = _hashes(tmp_path)
    second = pkb_inbox.init_layer(tmp_path, TEMPLATE_ROOT, True, False)
    assert second["created"] == []
    assert second["skipped"]
    assert _hashes(tmp_path) == before


def test_init_preserves_existing_content(tmp_path):
    (tmp_path / "inbox").mkdir()
    (tmp_path / "inbox" / "README.md").write_text("meu texto\n", encoding="utf-8")
    result = pkb_inbox.init_layer(tmp_path, TEMPLATE_ROOT, False, False)
    assert (tmp_path / "inbox" / "README.md").read_text(encoding="utf-8") == "meu texto\n"
    assert "inbox/README.md" in result["skipped"]


def test_dry_run_creates_nothing(tmp_path):
    result = pkb_inbox.init_layer(tmp_path, TEMPLATE_ROOT, True, True)
    assert result["created"]
    assert list(tmp_path.iterdir()) == []


def test_cli_json_and_usage(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "init", "--target", str(tmp_path), "--json"],
        capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert data["schema_version"] == 1
    assert "CLAUDE.md" in proc.stderr
    bad = subprocess.run([sys.executable, str(SCRIPT_PATH)], capture_output=True, text=True)
    assert bad.returncode == 2


def test_cli_missing_target_is_error(tmp_path):
    proc = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "init", "--target", str(tmp_path / "nope")],
        capture_output=True, text=True,
    )
    assert proc.returncode == 1


def test_pkb_dir_from_target_conventions(tmp_path):
    (tmp_path / "product-design").mkdir()
    (tmp_path / "product-design" / "conventions.md").write_text(
        "| `PKB_DIR` | `captura` | x |\n", encoding="utf-8")
    pkb_inbox.init_layer(tmp_path, TEMPLATE_ROOT, False, False)
    assert (tmp_path / "captura" / "README.md").is_file()
    assert not (tmp_path / "inbox").exists()


# ---------------------------------------------------------------------------
# capture
# ---------------------------------------------------------------------------

PLAN_TEXT = (
    "# Plan 000099 | FEATURE-X | 2026-10-07 | t\n\n## User brief\n\n"
    '"Quero um inbox automatico"\n\n## Agent interpretation\n\nx\n'
)


def _trace_row(n, text, skill="plan X", session="s1", emitter="user"):
    return {"evt_id": f"qa-{n:06d}", "session_id": session, "emitter": emitter,
            "message": text, "led_to_skill": skill,
            "timestamp": f"2026-10-07T10:0{n}:00+00:00"}


def _project(tmp_path, rows, *, readme=True, pkb_dir="inbox", plan=PLAN_TEXT):
    (tmp_path / "product-design").mkdir()
    (tmp_path / "product-design" / "conventions.md").write_text(
        f"| `PKB_DIR` | `{pkb_dir}` | x |\n", encoding="utf-8")
    (tmp_path / "_output").mkdir()
    (tmp_path / "_output" / "conversation-trace.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    (tmp_path / "inbox").mkdir()
    if readme:
        (tmp_path / "inbox" / "README.md").write_text("r", encoding="utf-8")
    art = tmp_path / "_output" / "plans"
    art.mkdir()
    (art / "plan-000099-x.md").write_text(plan, encoding="utf-8")
    return tmp_path


def _capture(root, **kw):
    args = dict(skill="plan X", artifact="_output/plans/plan-000099-x.md",
                session_id="s1", brief=None, repo_root=root)
    args.update(kw)
    return pkb_inbox.capture(**args)


def test_capture_equal_to_brief_after_normalization(tmp_path):
    rows = [_trace_row(1, "> QUERO   um inbox"), _trace_row(2, "automatico."),
            _trace_row(3, "outra skill", skill="implement Z")]
    root = _project(tmp_path, rows)
    result = _capture(root)
    note = (root / result["path"]).read_text(encoding="utf-8")
    assert result["as_expressed_igual_ao_brief"] is True
    assert "as_expressed_igual_ao_brief: true" in note
    assert note.count("\n> ") == 2
    assert "outra skill" not in note
    assert result["fonte"] == ["qa-000001", "qa-000002"]


def test_capture_differs_when_words_change(tmp_path):
    root = _project(tmp_path, [_trace_row(1, "Quero um inbox automatico e live")])
    assert _capture(root)["as_expressed_igual_ao_brief"] is False


def test_capture_masks_secret_in_brief(tmp_path):
    root = _project(tmp_path, [_trace_row(1, "oi")])
    result = _capture(root, brief='use api_key = "abcd1234efgh5678"')
    note = (root / result["path"]).read_text(encoding="utf-8")
    assert "[MASKED:" in note and "mascarado: true" in note
    assert "abcd1234efgh5678" not in note


def test_capture_skips_without_readme(tmp_path):
    root = _project(tmp_path, [_trace_row(1, "x")], readme=False)
    result = _capture(root)
    assert result == {"skipped": "no-pkb-layer"}
    assert list((root / "inbox").iterdir()) == []


def test_capture_skips_when_pkb_dir_empty(tmp_path):
    root = _project(tmp_path, [_trace_row(1, "x")], pkb_dir="")
    assert _capture(root) == {"skipped": "no-pkb-layer"}
    assert not list((root / "inbox").glob("2026*"))


def test_capture_without_session_uses_briefs(tmp_path):
    root = _project(tmp_path, [_trace_row(1, "x", session="other")])
    result = _capture(root, brief="Quero um inbox automatico")
    note = (root / result["path"]).read_text(encoding="utf-8")
    assert result["fonte"] == "briefs"
    assert "fonte: briefs" in note
    assert result["as_expressed_igual_ao_brief"] is True


def test_capture_appends_never_overwrites(tmp_path):
    root = _project(tmp_path, [_trace_row(1, "primeira fala")])
    first = _capture(root)
    path = root / first["path"]
    before = path.read_text(encoding="utf-8")
    second = _capture(root)
    after = path.read_text(encoding="utf-8")
    assert second["path"] == first["path"]
    assert after.startswith(before) and len(after) > len(before)


# ---- digest ---------------------------------------------------------------

def _note(root, name, skill, artefato, data, line):
    (root / "inbox" / name).write_text(
        f"---\norigem: usuario\ntipo: transitoria\ndata: {data}\nskill: {skill}\n"
        f"artefato: {artefato}\nfonte: briefs\n---\n\n> **--:--** {line}\n",
        encoding="utf-8")


def _digest_project(tmp_path):
    root = _project(tmp_path, [])
    _note(root, "2026-10-05-plan-a.md", "plan", "_output/plans/plan-000001-a.md", "2026-10-05", "primeira fala")
    _note(root, "2026-10-06-plan-b.md", "plan", "_output/plans/plan-000002-b.md", "2026-10-06", "segunda fala")
    _note(root, "2026-10-07-plan-c.md", "plan", "_output/plans/plan-000003-c.md", "2026-10-07", "terceira fala")
    comm = root / "_output" / "communication" / "2026-10-07"
    comm.mkdir(parents=True)
    (comm / "communication-000007-ACD.md").write_text(
        "# Communication 000007\n\n> **Fonte**: `_output/plans/plan-000002-b.md`\n", encoding="utf-8")
    return root


def test_digest_lists_notes_and_links_only_cited_artifact(tmp_path):
    root = _digest_project(tmp_path)
    result = pkb_inbox.digest(root)
    text = (root / "inbox" / "_live.md").read_text(encoding="utf-8")
    assert result["count"] == 3 and result["linked_communications"] == 1
    assert text.startswith(pkb_inbox.LIVE_HEADER)
    assert text.index("primeira fala") < text.index("segunda fala") < text.index("terceira fala")
    rows = [r for r in text.splitlines() if r.startswith("| 2026")]
    assert len(rows) == 3
    assert "communication-000007-ACD.md" in rows[1]
    assert "communication-" not in rows[0] and "communication-" not in rows[2]


def test_digest_is_deterministic(tmp_path):
    root = _digest_project(tmp_path)
    pkb_inbox.digest(root)
    first = (root / "inbox" / "_live.md").read_bytes()
    pkb_inbox.digest(root)
    assert (root / "inbox" / "_live.md").read_bytes() == first


def test_digest_without_notes(tmp_path):
    root = _project(tmp_path, [])
    result = pkb_inbox.digest(root)
    text = (root / "inbox" / "_live.md").read_text(encoding="utf-8")
    assert result["count"] == 0
    assert text.startswith(pkb_inbox.LIVE_HEADER) and "nenhuma captura ainda" in text


def test_digest_refuses_foreign_live_file(tmp_path):
    root = _project(tmp_path, [])
    live = root / "inbox" / "_live.md"
    live.write_text("meu conteudo\n", encoding="utf-8")
    before = hashlib.sha256(live.read_bytes()).hexdigest()
    proc = subprocess.run([sys.executable, str(SCRIPT_PATH), "digest", "--target", str(root)],
                          capture_output=True, text=True, check=False)
    assert proc.returncode == 1
    assert "nao foi gerado por mim" in proc.stderr
    assert hashlib.sha256(live.read_bytes()).hexdigest() == before


def test_digest_skips_without_layer(tmp_path):
    root = _project(tmp_path, [], readme=False)
    assert pkb_inbox.digest(root) == {"skipped": "no-pkb-layer"}
    assert not (root / "inbox" / "_live.md").exists()
