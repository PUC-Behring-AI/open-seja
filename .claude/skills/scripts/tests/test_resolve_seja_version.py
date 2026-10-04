"""Tests for resolve_seja_version (plans-000379 and 000380)."""
from __future__ import annotations

import resolve_seja_version as rsv


LS_REMOTE_SAMPLE = "\n".join(
    [
        "abc1230000000000000000000000000000000001\trefs/tags/v0.1.0",
        "abc1230000000000000000000000000000000002\trefs/tags/v0.1.0^{}",
        "abc1230000000000000000000000000000000003\trefs/tags/v0.2.0",
        "abc1230000000000000000000000000000000004\trefs/tags/v0.10.0",
        "abc1230000000000000000000000000000000005\trefs/tags/v1.0.0",
        "abc1230000000000000000000000000000000006\trefs/tags/not-a-semver",
        "abc1230000000000000000000000000000000007\trefs/tags/v0.1.0-rc1",
    ]
)


def test_parse_ls_remote_tags_filters_and_sorts() -> None:
    tags = rsv.parse_ls_remote_tags(LS_REMOTE_SAMPLE)
    assert tags == ["v0.1.0", "v0.2.0", "v0.10.0", "v1.0.0"]


def test_parse_ls_remote_tags_empty() -> None:
    assert rsv.parse_ls_remote_tags("") == []


def test_resolve_version_defaults_to_latest() -> None:
    resolved, warning = rsv.resolve_version(None, ["v0.1.0", "v0.2.0"])
    assert resolved == "v0.2.0"
    assert warning is None


def test_resolve_version_latest_literal() -> None:
    resolved, warning = rsv.resolve_version("latest", ["v0.1.0", "v0.2.0"])
    assert resolved == "v0.2.0"
    assert warning is None


def test_resolve_version_explicit_match() -> None:
    resolved, warning = rsv.resolve_version("v0.1.0", ["v0.1.0", "v0.2.0"])
    assert resolved == "v0.1.0"
    assert warning is None


def test_resolve_version_explicit_miss_warns() -> None:
    resolved, warning = rsv.resolve_version("v9.9.9", ["v0.1.0"])
    assert resolved == "v9.9.9"
    assert warning is not None
    assert "not found" in warning


def test_resolve_version_empty_falls_back_to_head() -> None:
    resolved, warning = rsv.resolve_version(None, [])
    assert resolved == rsv.HEAD_SENTINEL
    assert warning is not None
    assert "HEAD" in warning


def _capture_remote(monkeypatch) -> list[str]:
    seen: list[str] = []

    def fake_fetch(remote: str) -> list[str]:
        seen.append(remote)
        return ["v0.10.0"]

    monkeypatch.setattr(rsv, "fetch_remote_tags", fake_fetch)
    return seen


def test_main_defaults_to_open_seja_remote(monkeypatch, capsys) -> None:
    monkeypatch.delenv("SEJA_REMOTE", raising=False)
    seen = _capture_remote(monkeypatch)
    assert rsv.main([]) == 0
    assert seen == ["git@github.com:PUC-Behring-AI/open-seja.git"]
    assert capsys.readouterr().out.strip() == "v0.10.0"


def test_main_uses_seja_remote_env(monkeypatch) -> None:
    monkeypatch.setenv("SEJA_REMOTE", "https://example.invalid/open-seja")
    seen = _capture_remote(monkeypatch)
    assert rsv.main([]) == 0
    assert seen == ["https://example.invalid/open-seja"]


def test_main_explicit_remote_beats_env(monkeypatch) -> None:
    monkeypatch.setenv("SEJA_REMOTE", "https://example.invalid/from-env")
    seen = _capture_remote(monkeypatch)
    assert rsv.main(["--remote", "https://example.invalid/from-flag"]) == 0
    assert seen == ["https://example.invalid/from-flag"]


def test_main_fetch_failure_prints_hint(monkeypatch, capsys) -> None:
    def failing_fetch(remote: str) -> list[str]:
        raise RuntimeError("git ls-remote failed: Permission denied (publickey)")

    monkeypatch.setattr(rsv, "fetch_remote_tags", failing_fetch)
    assert rsv.main([]) == 2
    err = capsys.readouterr().err
    assert "ERROR:" in err
    assert "SEJA_REMOTE" in err
