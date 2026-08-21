#!/usr/bin/env python3
"""Compare the recovered warning tile vector with original and prototype traces."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


TILE_RE = re.compile(r"tile_write: offset=([0-9a-fA-F]+) data=([0-9a-fA-F]+)")
RECORDS = (
    (0x0316, "W A R N I N G"),
    (0x040A, "THIS GAME IS TO BE USED ONLY IN JAPAN."),
    (0x048A, "EXPORT, SALES, DISTRIBUTION AND/OR"),
    (0x050A, "OPERATION OUTSIDE THIS AREA MAY"),
    (0x058A, "CONSTITUTE A VIOLATION OF INTERNATIONAL"),
    (0x060A, "LAWS ON COPYRIGHTS AND/OR INDUSTRIAL"),
    (0x068A, "PROPERTY RIGHTS AND SUBJECT THE"),
    (0x070A, "VIOLATING PARTY TO LEGAL PROCEEDINGS."),
    (0x080A, "                   SEGA ENTERPRISES,LTD."),
)


def expected() -> list[tuple[int, int]]:
    return [(offset + index, 0x8000 | ord(char)) for offset, text in RECORDS for index, char in enumerate(text)]


def read_trace(path: Path) -> list[tuple[int, int]]:
    result = []
    for line in path.read_text(encoding="ascii").splitlines():
        match = TILE_RE.search(line)
        if match:
            result.append((int(match.group(1), 16), int(match.group(2), 16)))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--prototype", type=Path, required=True)
    args = parser.parse_args()

    vector = expected()
    prototype = read_trace(args.prototype)
    if prototype != vector:
        raise SystemExit(f"prototype mismatch: expected {len(vector)} writes, found {len(prototype)}")

    original = read_trace(args.original)
    try:
        start = next(index for index in range(len(original) - len(vector) + 1) if original[index : index + len(vector)] == vector)
    except StopIteration as error:
        raise SystemExit("original trace does not contain the recovered warning vector") from error

    print(f"warning tile vector matches prototype ({len(vector)} writes)")
    print(f"original trace contains the vector at write index {start}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
