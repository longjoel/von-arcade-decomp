#!/usr/bin/env python3
"""Test the bounded geometry float-to-log exponent conversion contract."""

from verify_geometry_buffer import conversion, raw_logb


def main() -> int:
    cases = (
        (0x00000000, -10000, 0),
        (0x80000000, -10000, 0),
        (0x3F800000, 0, 128),
        (0x40000000, 1, 128),
        (0xBF800000, 0, 128),
        (0x007FFFFF, -127, 1),
        (0x00000001, -149, 0),
        (0x7F800000, 128, 128),
    )
    for bits, expected_logb, expected_conversion in cases:
        if raw_logb(bits) != expected_logb:
            raise SystemExit(f"raw logb mismatch for 0x{bits:08x}")
        if conversion(bits) != expected_conversion:
            raise SystemExit(f"conversion mismatch for 0x{bits:08x}")
    print("PASS: geometry float conversion boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
