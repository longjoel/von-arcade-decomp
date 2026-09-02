#!/usr/bin/env python3
"""Guard the candidate DRC floating-point special-case patch."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "third_party/patches/0028-von-sharc-drc-float-special-cases.patch"
PREPARE = ROOT / "scripts/prepare-mame.sh"


def main() -> int:
    patch = PATCH.read_text(encoding="utf-8")
    for fragment in (
        "case 0x82",
        "FLOAT_CANONICAL_NAN",
        "case 0xc1",
        "logb_zero",
        "logb_nan",
        "FLOAT_INFINITY",
        "ASTAT_AV",
        "ASTAT_AI",
        "ASTAT_AF",
        "UML_OR(block, STKY, STKY, AIS)",
        "FLOAT_EXPONENT_MASK | FLOAT_MANTISSA_MASK",
    ):
        if fragment not in patch:
            raise SystemExit(f"DRC special-case patch missing {fragment}")
    if "SHARC_DRC_FLOAT_SPECIAL_CASES_PATCH_FILE" not in PREPARE.read_text(encoding="utf-8"):
        raise SystemExit("prepare-mame.sh does not install the DRC special-case patch")
    print("PASS: SHARC DRC floating-point special-case patch contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
