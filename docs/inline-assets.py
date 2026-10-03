#!/usr/bin/env python3
"""Inline local image assets into an HTML file as data URIs.

Artifacts published to claude.ai run under a strict CSP that blocks every
external host, so a page destined for publication must be self-contained.
The versioned sources under docs/ keep relative <img src="..."> paths instead:
they stay small, they diff cleanly, and they open correctly in a browser.

Run this to produce the publishable copy:

    python3 docs/inline-assets.py docs/revisao-anax-2026-08-26.html /tmp/out.html

Then publish the output. The versioned source stays untouched.
"""

import base64
import mimetypes
import re
import sys
from pathlib import Path

ASSET_SRC = re.compile(r'src="(?!data:|https?:)([^"]+)"')


def inline(src_path: Path, out_path: Path) -> None:
    html = src_path.read_text(encoding="utf-8")
    base = src_path.parent
    inlined = 0

    def swap(match: re.Match[str]) -> str:
        nonlocal inlined
        asset = base / match.group(1)
        if not asset.is_file():
            print(f"WARNING: asset not found, left as-is: {match.group(1)}")
            return match.group(0)
        mime = mimetypes.guess_type(asset.name)[0] or "application/octet-stream"
        payload = base64.b64encode(asset.read_bytes()).decode("ascii")
        inlined += 1
        return f'src="data:{mime};base64,{payload}"'

    out_path.write_text(ASSET_SRC.sub(swap, html), encoding="utf-8")
    size_mb = out_path.stat().st_size / 1048576
    print(f"Inlined {inlined} asset(s) -> {out_path} ({size_mb:.2f} MB)")
    if size_mb > 16:
        print("WARNING: exceeds the 16 MB artifact limit")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    inline(Path(sys.argv[1]), Path(sys.argv[2]))
