"""Quality gate core for Python projects (stdlib only).

Pure functions: CRAP score, radon/coverage join, touched functions from a
git diff, CRAP ratchet, marker ratchet and exit code. The executor
(CLI, subprocess orchestration) is layered on top of this core.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set

# Exit categories, lowest failing one wins (1 always precedes).
CAT_CONFIG = 1
CAT_STATIC = 2
CAT_TESTS = 3
CAT_CRAP = 4
CAT_ARCH = 5
CAT_MUTATION = 6
CAT_MARKERS = 7

JOIN_MISS_LIMIT = 0.05
_EPS = 1e-9


@dataclass
class Finding:
    category: int
    key: str
    message: str
    value: Optional[float] = None
    limit: Optional[float] = None
    severity: str = "error"  # "error" or "warning"


@dataclass
class FunctionMetric:
    file: str
    qualname: str
    lineno: int
    endline: int
    cc: int
    cov: float
    crap: float
    joined: bool = True

    @property
    def key(self) -> str:
        return make_key(self.file, self.qualname)


def make_key(file: str, qualname: str) -> str:
    return "%s::%s" % (file, qualname)


def crap(cc: int, cov: float) -> float:
    """CRAP = cc^2 * (1 - cov)^3 + cc."""
    return cc ** 2 * (1.0 - cov) ** 3 + cc


def _norm(path: str, root: str) -> str:
    absolute = path if os.path.isabs(path) else os.path.join(root, path)
    return os.path.relpath(os.path.abspath(absolute), os.path.abspath(root)).replace(os.sep, "/")


def _flatten(entry: dict, prefix: str) -> Iterable[tuple]:
    """Yield (qualname, entry) for a radon entry and its closures."""
    qual = prefix + entry["name"]
    yield qual, entry
    for child in entry.get("closures", []) or []:
        for item in _flatten(child, qual + "."):
            yield item


def _radon_functions(entries: List[dict]) -> Iterable[tuple]:
    for entry in entries:
        etype = entry.get("type")
        if etype == "class":
            # The class itself is ignored; its methods are scored on their own.
            for meth in entry.get("methods", []) or []:
                for item in _flatten(meth, entry["name"] + "."):
                    yield item
            continue
        prefix = entry["classname"] + "." if entry.get("classname") else ""
        for item in _flatten(entry, prefix):
            yield item


def _region_cov(region: Optional[dict]) -> tuple:
    """Return (cov, found) for a coverage `functions` region."""
    if region is None:
        return 0.0, False
    summ = region.get("summary", {})
    denom = summ.get("num_statements", 0) + summ.get("num_branches", 0)
    if denom == 0:
        return 1.0, True
    num = summ.get("covered_lines", 0) + summ.get("covered_branches", 0)
    return num / float(denom), True


def join_metrics(radon_json: dict, coverage_json: dict, root: str = ".") -> Dict[str, FunctionMetric]:
    """Join radon cc with per-function coverage (coverage >= 7.5)."""
    cov_files = {
        _norm(path, root): data for path, data in (coverage_json.get("files") or {}).items()
    }
    metrics: Dict[str, FunctionMetric] = {}
    for path, entries in radon_json.items():
        if isinstance(entries, dict):  # radon error payload for a file
            continue
        rel = _norm(path, root)
        functions = (cov_files.get(rel) or {}).get("functions") or {}
        for qual, entry in _radon_functions(entries):
            cov, found = _region_cov(functions.get(qual))
            cc = int(entry["complexity"])
            metric = FunctionMetric(
                file=rel,
                qualname=qual,
                lineno=int(entry["lineno"]),
                endline=int(entry.get("endline") or entry["lineno"]),
                cc=cc,
                cov=cov,
                crap=crap(cc, cov),
                joined=found,
            )
            metrics[metric.key] = metric
    return metrics


def join_findings(metrics: Dict[str, FunctionMetric]) -> List[Finding]:
    """Category 1 `join-miss` when more than 5% of functions lack a coverage region."""
    if not metrics:
        return []
    missed = [m for m in metrics.values() if not m.joined]
    ratio = len(missed) / float(len(metrics))
    if ratio > JOIN_MISS_LIMIT:
        return [Finding(CAT_CONFIG, "join-miss",
                        "%d of %d functions have no coverage region" % (len(missed), len(metrics)),
                        ratio, JOIN_MISS_LIMIT)]
    return []


_FILE_RE = re.compile(r"^\+\+\+ (?:b/)?(.+?)\s*$")
_HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def touched_functions(diff_text: str, untracked: Iterable[str],
                      metrics: Dict[str, FunctionMetric]) -> Set[str]:
    """Keys of functions touched by a `git diff -U0` plus untracked files.

    An added/changed hunk `+c,d` touches functions containing lines c..c+d-1;
    a removal-only hunk (d == 0) touches the function containing line c.
    Untracked files touch all of their functions.
    """
    by_file: Dict[str, List[FunctionMetric]] = {}
    for metric in metrics.values():
        by_file.setdefault(metric.file, []).append(metric)
    touched: Set[str] = set()
    for path in untracked:
        for metric in by_file.get(path.replace(os.sep, "/"), []):
            touched.add(metric.key)
    current: Optional[str] = None
    for line in diff_text.splitlines():
        fm = _FILE_RE.match(line)
        if fm:
            current = None if fm.group(1) == "/dev/null" else fm.group(1)
            continue
        hm = _HUNK_RE.match(line)
        if hm and current:
            start = int(hm.group(1))
            count = 1 if hm.group(2) is None else int(hm.group(2))
            last = start + count - 1 if count > 0 else start
            for metric in by_file.get(current, []):
                if metric.lineno <= last and start <= metric.endline:
                    touched.add(metric.key)
    return touched


def evaluate_crap(metrics: Dict[str, FunctionMetric], baseline: dict, touched: Set[str],
                  max_touched: float, max_abs: float) -> List[Finding]:
    """Apply the CRAP ratchet. Category 4 findings, plus `over-ceiling` warnings."""
    base = (baseline or {}).get("functions", {})
    findings: List[Finding] = []
    for key in sorted(metrics):
        value = metrics[key].crap
        entry = base.get(key)
        if key in touched or entry is None:
            if value > max_touched + _EPS:
                why = "touched" if key in touched else "new"
                findings.append(Finding(CAT_CRAP, key,
                                        "CRAP(%s)=%.2f > %s (%s function)" % (key, value, max_touched, why),
                                        value, max_touched))
            continue
        base_crap = float(entry["crap"])
        if value > base_crap + _EPS:
            findings.append(Finding(CAT_CRAP, key,
                                    "CRAP(%s)=%.2f rose above baseline %.2f" % (key, value, base_crap),
                                    value, base_crap))
        elif base_crap > max_abs and value > max_abs + _EPS:
            findings.append(Finding(CAT_CRAP, key + "#over-ceiling",
                                    "CRAP(%s)=%.2f above ceiling %s (legacy baseline %.2f)"
                                    % (key, value, max_abs, base_crap),
                                    value, max_abs, severity="warning"))
    return findings


def ratchet_markers(counts_now: dict, counts_base: dict) -> List[Finding]:
    """Evasion markers (skip, xfail, no cover, no mutate).

    Counts are `{kind: {"total": n, "unjustified": m}}`; markers lacking
    `reason=`/`reason:`/`equivalent:` must not exceed the baseline.
    """
    findings: List[Finding] = []
    for kind in sorted(counts_now):
        now = counts_now[kind].get("unjustified", 0)
        base = (counts_base or {}).get(kind, {}).get("unjustified", 0)
        if now > base:
            findings.append(Finding(CAT_MARKERS, kind,
                                    "%d new '%s' marker(s) without reason/equivalent" % (now - base, kind),
                                    now, base))
    return findings


def exit_code(findings: Iterable[Finding]) -> int:
    """0 PASS; 1 precedes; otherwise the lowest failing category 2..7. Warnings ignored."""
    cats = {f.category for f in findings if f.severity != "warning"}
    if CAT_CONFIG in cats:
        return CAT_CONFIG
    failing = [c for c in cats if CAT_STATIC <= c <= CAT_MARKERS]
    return min(failing) if failing else 0
