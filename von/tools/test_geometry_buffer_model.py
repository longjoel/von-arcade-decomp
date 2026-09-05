#!/usr/bin/env python3
"""Test the deterministic geometry buffer and four-batch contract."""

from verify_geometry_buffer import expected


def main() -> int:
    values = expected()
    if len(values) != 0x2000:
        raise SystemExit(f"geometry buffer length mismatch: {len(values)}")
    if values[:4] != [0, 0, 0, 0]:
        raise SystemExit("geometry buffer initial words mismatch")
    if values[-2:] != [0x7F7F7F7F, 0x7F7F7F7F]:
        raise SystemExit("geometry buffer terminal words mismatch")
    for batch in range(4):
        if len(values[batch * 0x800:(batch + 1) * 0x800]) != 0x800:
            raise SystemExit(f"geometry batch {batch} length mismatch")
    print("PASS: geometry buffer and four-batch model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
