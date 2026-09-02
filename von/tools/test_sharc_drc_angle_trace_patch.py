#!/usr/bin/env python3
"""Guard the bounded DRC angle-service state trace patch."""

import json
from pathlib import Path

from patchset_manifest import resolve


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "third_party/patches/0027-von-sharc-drc-angle-tracing.patch"
MANIFEST = ROOT / "third_party/patches/patchsets.json"


def main() -> int:
    patch = PATCH.read_text(encoding="utf-8")
    for fragment in (
        "trace_angle_path",
        "vonj_sharc_drc_angle:",
        "0x00020285",
        "0x00020289",
        "0x00020d68",
        "0x00020dbd",
        "save_fast_iregs(block)",
    ):
        if fragment not in patch:
            raise SystemExit(f"DRC angle trace patch missing {fragment}")
    profile = resolve(json.loads(MANIFEST.read_text(encoding="utf-8")), "sharc-diagnostics")
    if PATCH.name in profile or "0034-von-sharc-runtime-diagnostics.patch" not in profile:
        raise SystemExit("historical DRC angle tracing was not superseded by runtime diagnostics")
    print("PASS: SHARC DRC angle-path trace patch contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
