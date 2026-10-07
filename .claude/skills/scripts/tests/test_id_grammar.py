"""ID grammar of the core parsers (plan-000019 Step 5; extended in Step 7).

Each parser must keep reading legacy six-digit IDs and read a new
``YYYYMMDD-xxxxxx`` ID whole, never truncated to its first six digits.
"""
from __future__ import annotations

from pathlib import Path

import check_docs
import check_plan_coverage
import generate_decision_digest
import generate_pending_roadmap
import pending
import reflect_deep_scope
import reflect_stuck_loops
import step_notes
import summarize_artifacts
import update_cross_refs

NEW = "20261007-k3m9qz"


def _plan(tmp_path: Path, name: str) -> Path:
    d = tmp_path / "plans"
    d.mkdir(exist_ok=True)
    p = d / name
    p.write_text("# Plan\n\n- **Traces**: REQ-ENT-001\n", encoding="utf-8")
    return d


class TestCheckPlanCoverage:
    def test_legacy_id(self, tmp_path):
        d = _plan(tmp_path, "plan-000007-foo.md")
        assert check_plan_coverage.extract_traces(d) == {"REQ-ENT-001": ["000007"]}

    def test_new_id_whole(self, tmp_path):
        d = _plan(tmp_path, f"plan-{NEW}-foo.md")
        assert check_plan_coverage.extract_traces(d) == {"REQ-ENT-001": [NEW]}


class TestUpdateCrossRefs:
    def test_source_new_id(self):
        lines = ["# Plan", f"source: plan-{NEW} -- motivo"]
        assert update_cross_refs._extract_source(lines) == ("plan", NEW)

    def test_source_legacy_id(self):
        assert update_cross_refs._extract_source(["source: research-000569"]) == (
            "research",
            "000569",
        )

    def test_token_from_new_path(self):
        assert update_cross_refs._artifact_token_from_path(
            Path(f"research-{NEW}-topic.md")
        ) == ("research", NEW)

    def test_token_rejects_short_id(self):
        assert update_cross_refs._artifact_token_from_path(Path("plan-0007-x.md")) is None

    def test_index_row_new_id(self):
        row = f"| Plan | plan | {NEW} | 2026-10-07 | t | [plan-{NEW}-x.md](plans/plan-{NEW}-x.md) |"
        m = update_cross_refs._INDEX_ROW_RE.match(row)
        assert m and m.group(2) == NEW


class TestStepNotes:
    def test_progress_path_new_id(self, tmp_path):
        assert step_notes.progress_path(NEW, tmp_path).name == f"plan-{NEW}-progress.md"

    def test_progress_path_legacy_padding(self, tmp_path):
        assert step_notes.progress_path("19", tmp_path).name == "plan-000019-progress.md"


class TestSummarizeArtifacts:
    def test_header_new_id(self):
        m = summarize_artifacts._HEADER_RE.match(
            f"# Plan {NEW} | FEATURE-O | 2026-10-07 19:00 UTC | t | Review: standard"
        )
        assert m and m.group(1) == NEW

    def test_header_metacomm(self):
        m = summarize_artifacts._HEADER_RE.match(
            "# Plan 000007 | FEATURE-O | METACOMM | 2026-10-05 02:00 UTC | t | Review: standard"
        )
        assert m
        assert (m.group(1), m.group(2), m.group(3), m.group(4)) == (
            "000007",
            "FEATURE-O",
            "2026-10-05 02:00 UTC",
            "t",
        )

    def test_header_two_line_done(self):
        lines = [
            "# DONE | 2026-10-06 16:59 UTC |",
            "# Plan 000007 | FEATURE-O | METACOMM | 2026-10-05 02:00 UTC | t | Review: standard",
        ]
        m = summarize_artifacts._HEADER_RE.match(summarize_artifacts._header_line(lines))
        assert m and (m.group(1), m.group(4)) == ("000007", "t")

    def test_header_line_single_line_unchanged(self):
        assert summarize_artifacts._header_line(["# Plan 000001 | X | d | t"]) == (
            "# Plan 000001 | X | d | t"
        )
        assert summarize_artifacts._header_line([]) == ""

    def test_plan_evidence_progress_name_new_id(self, tmp_path):
        plan = tmp_path / f"plan-{NEW}-foo.md"
        plan.write_text("# Plan\n", encoding="utf-8")
        (tmp_path / f"plan-{NEW}-progress.md").write_text(
            "### Step 1 -- reflection-on-action | 2026-10-07 19:00 UTC | t\n"
            "- happened: x\n- deviated: y\n- less-sure: z\n- gate: not-installed\n",
            encoding="utf-8",
        )
        ev = summarize_artifacts._plan_evidence(plan)
        assert len(ev["step_notes"]) == 1


class TestPending:
    def test_plan_file_present_new_id(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pending, "get_path", lambda key, *a: tmp_path)
        assert pending._plan_file_present(f"plan-{NEW}") is False
        (tmp_path / f"plan-{NEW}-x.md").write_text("# Plan\n", encoding="utf-8")
        assert pending._plan_file_present(f"plan-{NEW}") is True

    def test_roadmap_id_new(self):
        assert pending._ROADMAP_ID_RE.match(f"roadmap-{NEW}").group(1) == NEW
        assert pending._ROADMAP_ID_RE.match("roadmap-0007") is None


# --- Step 6: peripheral parsers -------------------------------------------


class TestCheckDocs:
    def test_skill_citation(self):
        rx = check_docs._SKILL_CITATION_RE
        assert rx.search("see plan-000007 here").group(1) == "plan-000007"
        assert rx.search(f"see advisory-{NEW}.").group(1) == f"advisory-{NEW}"
        assert rx.search("see plan-0007 here") is None

    def test_script_citation_drift(self):
        rx = check_docs._SCRIPT_CITATION_DRIFT_RE
        assert rx.search(f"# research-{NEW}").group(0) == f"research-{NEW}"
        assert rx.search("# plan-000007").group(0) == "plan-000007"
        assert check_docs._SCRIPT_TRANSITION_ANCHOR_RE.search(f"TRANSITION (plan-{NEW})")


class TestDecisionDigest:
    def test_advisory_header_new_id(self):
        line = f"# Advisory {NEW} | X | 2026-10-07 10:00 UTC | titulo"
        m = generate_decision_digest._ADVISORY_HEADER_RE.search(line)
        assert m and m.group(1) == NEW
        legacy = "# Research 000018 | X | 2026-10-06 10:00 UTC | t"
        assert generate_decision_digest._RESEARCH_HEADER_RE.search(legacy).group(1) == "000018"


class TestPendingRoadmap:
    def test_plan_id_new_whole(self):
        rx = generate_pending_roadmap._PLAN_ID_RE
        assert rx.search(f"source: plan-{NEW}").group(1) == NEW
        assert rx.search("plan-000007-x").group(1) == "000007"
        assert rx.search("plan-0007") is None

    def test_header_metacomm(self):
        text = "# Plan 000007 | FEATURE-O | METACOMM | 2026-10-05 02:00 UTC | t | Review: standard\n"
        assert generate_pending_roadmap._parse_plan_header(text) == ("t", "other")

    def test_header_new_id_done_line(self):
        text = f"# DONE | 2026-10-07 |\n# Plan {NEW} | FEATURE-B | 2026-10-07 02:00 UTC | t | Review: standard\n"
        assert generate_pending_roadmap._parse_plan_header(text) == ("t", "backend")


class TestReflect:
    def test_stuck_loops_brief_map_new_id(self, tmp_path):
        b = tmp_path / "briefs.md"
        b.write_text(f"STARTED | 2026-10-07 10:00 UTC | plan | {NEW} | fazer x\n", encoding="utf-8")
        assert reflect_stuck_loops._load_briefs_map(b) == {NEW: "fazer x"}

    def test_deep_scope_plan_id(self):
        assert reflect_deep_scope._extract_plan_id(f"PLAN | {NEW} | x") == NEW
        assert reflect_deep_scope._extract_plan_id("PLAN | 000007") == "000007"
        assert reflect_deep_scope._extract_plan_id("PLAN | 0007") is None


# --- Step 7: full matrix (legacy same as before, new whole, short rejected) --


SHORT = "0007"


class TestCheckPlanCoverageShort:
    def test_short_id_not_extracted(self, tmp_path):
        d = _plan(tmp_path, f"plan-{SHORT}-foo.md")
        # No ID matches: the stem is used as the plan key, as before.
        assert check_plan_coverage.extract_traces(d) == {
            "REQ-ENT-001": [f"plan-{SHORT}-foo"]
        }


class TestUpdateCrossRefsMatrix:
    def test_source_short_id_rejected(self):
        assert update_cross_refs._extract_source([f"source: plan-{SHORT} -- x"]) is None

    def test_token_from_legacy_path(self):
        assert update_cross_refs._artifact_token_from_path(
            Path("plan-000007-foo.md")
        ) == ("plan", "000007")

    @staticmethod
    def _ledger(tmp_path, monkeypatch, source_id: str) -> Path:
        out = tmp_path / "_output"
        (out / "plans").mkdir(parents=True)
        (out / "research-logs").mkdir()
        src = out / "plans" / f"plan-{source_id}-origem.md"
        src.write_text(f"# Plan {source_id} | X | d | t\n\n## Steps\n", encoding="utf-8")
        (out / "INDEX.md").write_text(
            "| Type | Prefix | ID | Date | Title | File |\n"
            "|---|---|---|---|---|---|\n"
            f"| Plan | plan | {source_id} | 2026-10-07 | t "
            f"| [plan-{source_id}-origem.md](plans/plan-{source_id}-origem.md) |\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(update_cross_refs, "OUTPUT_DIR", out)
        monkeypatch.setattr(update_cross_refs, "INDEX_FILE", out / "INDEX.md")
        monkeypatch.setattr(update_cross_refs, "REPO_ROOT", tmp_path)
        return src

    def test_spawned_propagates_from_new_format_source(self, tmp_path, monkeypatch):
        src = self._ledger(tmp_path, monkeypatch, NEW)
        child_id = "20261007-a1b2c3"
        child = tmp_path / "_output" / "research-logs" / f"research-{child_id}-x.md"
        child.write_text(f"# Research\nsource: plan-{NEW} -- motivo\n", encoding="utf-8")
        assert update_cross_refs.run(child) == 0
        assert f"spawned: research-{child_id}" in src.read_text(encoding="utf-8")

    def test_spawned_propagates_from_legacy_source(self, tmp_path, monkeypatch):
        src = self._ledger(tmp_path, monkeypatch, "000007")
        child = tmp_path / "_output" / "research-logs" / "research-000020-x.md"
        child.write_text("# Research\nsource: plan-000007 -- motivo\n", encoding="utf-8")
        assert update_cross_refs.run(child) == 0
        assert "spawned: research-000020" in src.read_text(encoding="utf-8")


class TestSummarizeArtifactsMatrix:
    def test_header_legacy(self):
        m = summarize_artifacts._HEADER_RE.match(
            "# Plan 000007 | FEATURE-O | 2026-10-05 02:00 UTC | t | Review: standard"
        )
        assert m and m.group(1) == "000007"

    def test_header_short_id_rejected(self):
        assert summarize_artifacts._HEADER_RE.match(
            f"# Plan {SHORT} | FEATURE-O | 2026-10-05 02:00 UTC | t"
        ) is None


class TestPendingMatrix:
    def test_plan_id_re(self):
        assert pending._PLAN_ID_RE.match("plan-000007").group(1) == "000007"
        assert pending._PLAN_ID_RE.match(f"plan-{NEW}").group(1) == NEW
        assert pending._PLAN_ID_RE.match(f"plan-{SHORT}") is None

    def test_plan_file_present_legacy(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pending, "get_path", lambda key, *a: tmp_path)
        assert pending._plan_file_present("plan-000007") is False
        (tmp_path / "plan-000007-x.md").write_text("# Plan\n", encoding="utf-8")
        assert pending._plan_file_present("plan-000007") is True

    def test_plan_file_present_ignores_progress_companion_new_id(self, tmp_path, monkeypatch):
        monkeypatch.setattr(pending, "get_path", lambda key, *a: tmp_path)
        (tmp_path / f"plan-{NEW}-progress.md").write_text("# P\n", encoding="utf-8")
        assert pending._plan_file_present(f"plan-{NEW}") is False


class TestCheckDocsMatrix:
    def test_script_citation_drift_short_rejected(self):
        assert check_docs._SCRIPT_CITATION_DRIFT_RE.search(f"# plan-{SHORT}") is None
        assert check_docs._SCRIPT_TRANSITION_ANCHOR_RE.search(f"TRANSITION (plan-{SHORT})") is None


class TestDecisionDigestMatrix:
    def test_advisory_header_legacy_and_short(self):
        rx = generate_decision_digest._ADVISORY_HEADER_RE
        legacy = "# Advisory 000058 | X | 2026-10-07 10:00 UTC | titulo"
        assert rx.search(legacy).group(1) == "000058"
        assert rx.search(f"# Advisory {SHORT} | X | 2026-10-07 10:00 UTC | t") is None
        assert generate_decision_digest._RESEARCH_HEADER_RE.search(
            f"# Research {NEW} | X | 2026-10-07 10:00 UTC | t"
        ).group(1) == NEW


class TestPendingRoadmapMatrix:
    def test_header_metacomm_groups(self):
        m = generate_pending_roadmap._PLAN_HEADER_RE.match(
            "# Plan 000007 | FEATURE-O | METACOMM | 2026-10-05 02:00 UTC | t | Review: standard"
        )
        assert m and (m.group(1), m.group(2)) == ("FEATURE-O", "t")

    def test_header_short_id_untitled(self):
        assert generate_pending_roadmap._parse_plan_header(
            f"# Plan {SHORT} | FEATURE-B | 2026-10-07 02:00 UTC | t | x\n"
        ) == ("(untitled)", "other")


class TestReflectMatrix:
    def test_stuck_loops_legacy_and_short(self, tmp_path):
        b = tmp_path / "briefs.md"
        b.write_text(
            "STARTED | 2026-10-07 10:00 UTC | plan | 000007 | fazer y\n"
            f"STARTED | 2026-10-07 10:00 UTC | plan | {SHORT} | fazer z\n",
            encoding="utf-8",
        )
        assert reflect_stuck_loops._load_briefs_map(b) == {"000007": "fazer y"}
