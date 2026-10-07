#!/usr/bin/env python3
# designer: When a skill gives birth to a plan, a research report, or any other
#   artifact, I'm the one place that says what an artifact ID looks like. I mint
#   a ULID on your machine without asking anyone, turn it into the short ID you
#   see in file names (date plus six characters), and hand every other script
#   the same pattern so old six-digit IDs and new ones are read the same way.
#   I record who created the artifact only as a pseudonymous token, never your name.
"""
artifact_id -- ULID generator, visible ID and shared ID grammar for SEJA artifacts.

Invocation: library
Lifecycle: active

The identity of an artifact is a ULID (26 chars, Crockford base32: 48-bit
millisecond timestamp + 80 random bits) generated locally, without
coordination (D-010). The visible ID is ``YYYYMMDD-<last 6 chars, lowercase>``,
with the date derived from the ULID itself, so ``id`` is a pure function of
``uid``. Legacy artifacts keep their six-digit IDs; the grammar is additive:
``ARTIFACT_ID`` matches both formats and has no capture groups, so callers can
embed it inside their own patterns.

Usage from sibling scripts:
    from artifact_id import ARTIFACT_ID, ARTIFACT_ID_RE, new_ulid, visible_id

    uid = new_ulid()
    vid = visible_id(uid)              # e.g. "20261007-k3m9qz"
    pattern = re.compile(rf"plan-({ARTIFACT_ID})-")
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import time
from datetime import datetime, timezone

_CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_DECODE = {c: i for i, c in enumerate(_CROCKFORD)}
_ULID_RE = re.compile(r"^[0-9A-HJKMNP-TV-Z]{26}$")

LEGACY_ID = r"\d{6}"
ULID_ID = r"\d{8}-[0-9a-z]{6}"
ARTIFACT_ID = rf"(?:{LEGACY_ID}|{ULID_ID})"
ARTIFACT_ID_RE = re.compile(rf"^{ARTIFACT_ID}$")

_LEGACY_RE = re.compile(rf"^{LEGACY_ID}$")
_ULID_ID_RE = re.compile(rf"^{ULID_ID}$")

BIRTH_SCHEMA_VERSION = 1


def _encode(value: int, length: int) -> str:
    chars = []
    for _ in range(length):
        chars.append(_CROCKFORD[value & 31])
        value >>= 5
    return "".join(reversed(chars))


def new_ulid() -> str:
    """Return a new 26-char ULID (uppercase Crockford base32)."""
    ms = time.time_ns() // 1_000_000
    rand = int.from_bytes(os.urandom(10), "big")
    return _encode(ms & ((1 << 48) - 1), 10) + _encode(rand, 16)


def ulid_timestamp(ulid: str) -> datetime:
    """Decode the timestamp (first 10 chars) of a ULID as an aware UTC datetime."""
    if not _ULID_RE.match(ulid):
        raise ValueError(f"not a ULID: {ulid!r}")
    ms = 0
    for ch in ulid[:10]:
        ms = (ms << 5) | _DECODE[ch]
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def visible_id(ulid: str) -> str:
    """Return the visible ID ``YYYYMMDD-<last 6 chars lowercase>`` of a ULID."""
    return f"{ulid_timestamp(ulid):%Y%m%d}-{ulid[-6:].lower()}"


def normalize_id(raw: str) -> str:
    """Zero-pad purely numeric IDs of up to 6 digits; return anything else unchanged."""
    if raw.isdigit() and len(raw) <= 6:
        return raw.zfill(6)
    return raw


def is_legacy_id(s: str) -> bool:
    return bool(_LEGACY_RE.match(s))


def is_ulid_id(s: str) -> bool:
    return bool(_ULID_ID_RE.match(s))


def _token(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def default_author() -> str:
    """Pseudonymous author token: sha256(git user.email)[:12], else sha256($USER)[:12].

    Never uses ``git config user.name`` (constitution C2). Returns ``"unknown"``
    when neither source is available.
    """
    try:
        proc = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        email = proc.stdout.strip() if proc.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        email = ""
    if email:
        return _token(email)
    user = os.environ.get("USER") or os.environ.get("USERNAME") or ""
    if user:
        return _token(user)
    return "unknown"


def birth_record(
    type_: str,
    title: str,
    author: str | None,
    origin: str | None,
) -> dict:
    """Build the birth record of a new artifact (schema_version 1)."""
    uid = new_ulid()
    return {
        "schema_version": BIRTH_SCHEMA_VERSION,
        "uid": uid,
        "id": visible_id(uid),
        "type": type_,
        "title": title,
        "author": author if author else default_author(),
        "ts_utc": ulid_timestamp(uid).isoformat(),
        "origin": origin,
    }
