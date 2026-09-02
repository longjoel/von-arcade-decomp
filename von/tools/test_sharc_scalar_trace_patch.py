#!/usr/bin/env python3
"""Guard the reproducible runtime trace hook for SHARC scalar services."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "third_party/patches/0025-von-sharc-scalar-tracing.patch"
PREPARE = ROOT / "scripts/prepare-mame.sh"


def main() -> int:
    patch = PATCH.read_text(encoding="utf-8")
    for fragment in (
        "vonj_sharc_scalar_trace_count",
        "vonj_sharc_scalar:",
        "0x00020133",
        "0x0002014a",
        "m_core->r[4].r",
    ):
        if fragment not in patch:
            raise SystemExit(f"scalar trace patch missing {fragment}")
    if "SHARC_SCALAR_TRACE_PATCH_FILE" not in PREPARE.read_text(encoding="utf-8"):
        raise SystemExit("prepare-mame.sh does not install the scalar trace patch")
    print("PASS: SHARC scalar-service trace patch contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
