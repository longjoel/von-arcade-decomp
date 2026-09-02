#!/usr/bin/env python3
"""Guard the reproducible MAME trace hook for the shared SHARC reducer."""

import json
from pathlib import Path

from patchset_manifest import resolve


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "third_party/patches/0023-von-sharc-reduction-tracing.patch"
MANIFEST = ROOT / "third_party/patches/patchsets.json"


def main() -> int:
    patch = PATCH.read_text(encoding="utf-8")
    for fragment in (
        "vonj_sharc_reduction_trace_count",
        "vonj_sharc_reduction:",
        "0x00020dca",
        "0x00020ddf",
        "dm_read32(0x0003030c)",
    ):
        if fragment not in patch:
            raise SystemExit(f"reduction trace patch missing {fragment}")
    profile = resolve(json.loads(MANIFEST.read_text(encoding="utf-8")), "sharc-diagnostics")
    if PATCH.name in profile or "0034-von-sharc-runtime-diagnostics.patch" not in profile:
        raise SystemExit("historical reduction tracing was not superseded by runtime diagnostics")
    print("PASS: shared SHARC reduction trace patch contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
