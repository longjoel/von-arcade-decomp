#!/usr/bin/env python3
"""Check the DRC compound FMUL+ABS exceptional-value contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "third_party/mame-master/src/devices/cpu/sharc/sharcdrc.cpp"


def main() -> int:
    text = SOURCE.read_text()
    start = text.index("case 0x1d:          // Fm = F3-0 * F7-4,   Fa = ABS F11-8")
    end = text.index("case 0x1e:", start)
    body = text[start:end]
    required = (
        "UML_TEST(block, I0, FLOAT_MANTISSA_MASK)",
        "UML_MOV(block, I0, FLOAT_CANONICAL_NAN)",
        "UML_OR(block, STKY, STKY, AIS)",
        "UML_MOV(block, ASTAT_AS, 0)",
        "UML_MOV(block, ASTAT_AI, I2)",
        "UML_LABEL(block, abs_done)",
    )
    missing = [fragment for fragment in required if fragment not in body]
    if missing:
        raise SystemExit("DRC ABS special-case contract missing: " + ", ".join(missing))
    print("PASS: SHARC DRC compound ABS special-case contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
