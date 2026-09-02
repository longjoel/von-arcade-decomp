#!/usr/bin/env python3
"""Guard the reproducible runtime trace hook for SHARC helper 0x20d68."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "third_party/patches/0024-von-sharc-20d68-tracing.patch"
PREPARE = ROOT / "scripts/prepare-mame.sh"


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
    if "SHARC_20D68_TRACE_PATCH_FILE" not in PREPARE.read_text(encoding="utf-8"):
        raise SystemExit("prepare-mame.sh does not install the 20d68 trace patch")
    print("PASS: SHARC helper-0x20d68 trace patch contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
