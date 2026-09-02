#!/usr/bin/env python3
"""Guard the generic MAME SHARC STKY state exposure patch."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "third_party/patches/0029-von-sharc-expose-stky-state.patch"
PREPARE = ROOT / "scripts/prepare-mame.sh"


def main() -> int:
    patch = PATCH.read_text(encoding="utf-8")
    for fragment in (
        "SHARC_STKY",
        '"STKY"',
        "m_core->stky",
        '.formatstr("%08X")',
    ):
        if fragment not in patch:
            raise SystemExit(f"STKY state patch missing {fragment}")
    if "SHARC_STKY_STATE_PATCH_FILE" not in PREPARE.read_text(encoding="utf-8"):
        raise SystemExit("prepare-mame.sh does not install the STKY state patch")
    print("PASS: SHARC STKY architectural-state patch contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
