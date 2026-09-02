#!/usr/bin/env python3
"""Guard the reproducible runtime trace hook for SHARC 0x03/0x04 services."""

import json
from pathlib import Path

from patchset_manifest import resolve


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "third_party/patches/0026-von-sharc-reciprocal-tracing.patch"
MANIFEST = ROOT / "third_party/patches/patchsets.json"


def main() -> int:
    patch = PATCH.read_text(encoding="utf-8")
    for fragment in (
        "vonj_sharc_reciprocal_trace_count",
        "vonj_sharc_reciprocal:",
        "0x0002014b",
        "0x0002016c",
        "m_core->r[12].r",
    ):
        if fragment not in patch:
            raise SystemExit(f"reciprocal trace patch missing {fragment}")
    profile = resolve(json.loads(MANIFEST.read_text(encoding="utf-8")), "sharc-diagnostics")
    if PATCH.name in profile or "0034-von-sharc-runtime-diagnostics.patch" not in profile:
        raise SystemExit("historical reciprocal tracing was not superseded by runtime diagnostics")
    print("PASS: SHARC reciprocal-service trace patch contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
