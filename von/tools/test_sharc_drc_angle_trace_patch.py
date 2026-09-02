#!/usr/bin/env python3
"""Guard the bounded DRC angle-service state trace patch."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "third_party/patches/0027-von-sharc-drc-angle-tracing.patch"
PREPARE = ROOT / "scripts/prepare-mame.sh"


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
    if "SHARC_DRC_ANGLE_TRACE_PATCH_FILE" not in PREPARE.read_text(encoding="utf-8"):
        raise SystemExit("prepare-mame.sh does not install the DRC angle trace patch")
    print("PASS: SHARC DRC angle-path trace patch contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
