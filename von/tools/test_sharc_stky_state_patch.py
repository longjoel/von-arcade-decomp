#!/usr/bin/env python3
"""Contract for the fork's SHARC STKY architectural-state exposure."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SHARC = ROOT / "mame/src/devices/cpu/sharc/sharc.cpp"


def main() -> int:
    source = SHARC.read_text(encoding="utf-8")
    for fragment in (
        "SHARC_STKY",
        '"STKY"',
        "m_core->stky",
        '.formatstr("%08X")',
    ):
        if fragment not in source:
            raise SystemExit(f"STKY state exposure missing {fragment}")
    print("PASS: SHARC STKY architectural-state contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
