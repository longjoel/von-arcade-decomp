#!/usr/bin/env python3
"""Guard the bounded interpreter-side architectural angle trace patch."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "third_party/patches/0030-von-sharc-interpreter-angle-boundary-tracing.patch"
PREPARE = ROOT / "scripts/prepare-mame.sh"


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
    if "SHARC_INTERPRETER_ANGLE_TRACE_PATCH_FILE" not in PREPARE.read_text(encoding="utf-8"):
        raise SystemExit("prepare-mame.sh does not install the interpreter angle trace patch")
    print("PASS: SHARC interpreter angle-boundary trace patch contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
