#!/usr/bin/env python3
"""Compare ordered geometry-parser opcodes from original and C runs."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PATTERN = re.compile(r"vonj_geometry_opcode: .*?opcode=([0-9a-fA-F]+)")


def load(path: Path, limit: int, skip: int = 0) -> list[int]:
    values = []
    for match in PATTERN.finditer(path.read_text(encoding="utf-8", errors="replace")):
        if skip:
            skip -= 1
            continue
        values.append(int(match.group(1), 16))
        if len(values) == limit:
            break
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--reconstructed", type=Path, required=True)
    parser.add_argument("--events", type=int, default=64)
    parser.add_argument("--skip", type=int, default=0,
                        help="skip this many parser opcodes before comparing")
    args = parser.parse_args()
    original = load(args.original, args.events, args.skip)
    reconstructed = load(args.reconstructed, args.events, args.skip)
    if original == reconstructed and len(original) == args.events:
        print(f"geometry parser opcode prefix: PASS ({args.events} ordered opcodes)")
        return 0
    common = 0
    for wanted, got in zip(original, reconstructed):
        if wanted != got:
            break
        common += 1
    print(
        f"geometry parser opcode prefix: FAIL (common={common}, "
        f"original={len(original)}, reconstructed={len(reconstructed)})"
    )
    if common < len(original) and common < len(reconstructed):
        print(f"first divergence: original={original[common]:08x} "
              f"reconstructed={reconstructed[common]:08x}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
