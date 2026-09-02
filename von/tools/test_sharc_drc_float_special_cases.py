#!/usr/bin/env python3
"""Guard the candidate DRC floating-point special-case patch."""

import json
from pathlib import Path

from patchset_manifest import resolve


ROOT = Path(__file__).resolve().parents[2]
PATCH = ROOT / "third_party/patches/0028-von-sharc-drc-float-special-cases.patch"
MANIFEST = ROOT / "third_party/patches/patchsets.json"


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
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if PATCH.name not in resolve(manifest, "sharc-precision"):
        raise SystemExit("sharc-precision profile does not install the DRC special-case patch")
    print("PASS: SHARC DRC floating-point special-case patch contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
