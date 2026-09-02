#!/usr/bin/env python3
"""Guard the bounded interpreter-side architectural angle trace patch."""

import json
from pathlib import Path

from patchset_manifest import resolve


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "third_party/patches/0030-von-sharc-interpreter-angle-boundary-tracing.patch"
MANIFEST = ROOT / "third_party/patches/patchsets.json"


def main() -> int:
    patch = PATCH.read_text(encoding="utf-8")
    for fragment in (
        "vonj_sharc_interpreter_angle:",
        "m_core->astat",
        "m_core->stky",
        "0x00020285",
        "0x00020d68",
        "< 512",
    ):
        if fragment not in patch:
            raise SystemExit(f"interpreter angle trace patch missing {fragment}")
    profile = resolve(json.loads(MANIFEST.read_text(encoding="utf-8")), "sharc-diagnostics")
    if PATCH.name in profile or "0034-von-sharc-runtime-diagnostics.patch" not in profile:
        raise SystemExit("historical interpreter angle tracing was not superseded by runtime diagnostics")
    print("PASS: SHARC interpreter angle-boundary trace patch contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
