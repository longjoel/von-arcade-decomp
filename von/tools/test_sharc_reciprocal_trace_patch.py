#!/usr/bin/env python3
"""Guard the reproducible runtime trace hook for SHARC 0x03/0x04 services."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "third_party/patches/0026-von-sharc-reciprocal-tracing.patch"
PREPARE = ROOT / "scripts/prepare-mame.sh"


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
    if "SHARC_RECIPROCAL_TRACE_PATCH_FILE" not in PREPARE.read_text(encoding="utf-8"):
        raise SystemExit("prepare-mame.sh does not install the reciprocal trace patch")
    print("PASS: SHARC reciprocal-service trace patch contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
