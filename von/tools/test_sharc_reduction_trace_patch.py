#!/usr/bin/env python3
"""Guard the reproducible MAME trace hook for the shared SHARC reducer."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "third_party/patches/0023-von-sharc-reduction-tracing.patch"
PREPARE = ROOT / "scripts/prepare-mame.sh"


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
    if "SHARC_REDUCTION_TRACE_PATCH_FILE" not in PREPARE.read_text(encoding="utf-8"):
        raise SystemExit("prepare-mame.sh does not install the reduction trace patch")
    print("PASS: shared SHARC reduction trace patch contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
