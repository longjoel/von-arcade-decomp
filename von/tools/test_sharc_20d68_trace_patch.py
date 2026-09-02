#!/usr/bin/env python3
"""Guard the reproducible runtime trace hook for SHARC helper 0x20d68."""

import json
from pathlib import Path

from patchset_manifest import resolve


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "third_party/patches/0024-von-sharc-20d68-tracing.patch"
MANIFEST = ROOT / "third_party/patches/patchsets.json"


def main() -> int:
    patch = PATCH.read_text(encoding="utf-8")
    for fragment in (
        "vonj_sharc_20d68_trace_count",
        "vonj_sharc_20d68:",
        "0x00020d68",
        "0x00020dbd",
        "dm_read32(0x00030300)",
        "dm_read32(0x0003030b)",
    ):
        if fragment not in patch:
            raise SystemExit(f"20d68 trace patch missing {fragment}")
    profile = resolve(json.loads(MANIFEST.read_text(encoding="utf-8")), "sharc-diagnostics")
    if PATCH.name in profile or "0034-von-sharc-runtime-diagnostics.patch" not in profile:
        raise SystemExit("historical 20d68 tracing was not superseded by runtime diagnostics")
    print("PASS: SHARC helper-0x20d68 trace patch contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
