#!/usr/bin/env python3
"""Export a traced mode-3 polygon-ROM object as a raw OBJ mesh."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


def words(data: bytes, index: int, count: int) -> list[int]:
    start = index * 4
    return [int.from_bytes(data[pos:pos + 4], "little")
            for pos in range(start, min(start + count * 4, len(data)), 4)]


def point(values: list[int], cursor: int) -> tuple[tuple[float, float, float], int]:
    result = tuple(struct.unpack("<f", value.to_bytes(4, "little"))[0]
                   for value in values[cursor:cursor + 3])
    return result, cursor + 3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path,
                        default=Path("von/build/disasm/geometry-rom.bin"))
    parser.add_argument("--oba", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--words", type=int, default=0x4000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    values = words(args.rom.read_bytes(), args.oba & 0x3fffff, args.words)
    cursor = 0
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, list[int]]] = []

    p0, cursor = point(values, cursor)
    p1, cursor = point(values, cursor)
    while cursor < len(values):
        attr = values[cursor]
        cursor += 1
        if (attr & 3) == 0 or cursor + 6 > len(values):
            break
        cursor += 3  # normal, ignored by mode 3
        p2, cursor = point(values, cursor)
        if attr & 1:
            p3, cursor = point(values, cursor)
        else:
            cursor += 3  # reserved point for triangle records
            p3 = p2

        start = len(vertices) + 1
        if attr & 1:
            vertices.extend((p0, p1, p2, p3))
            faces.append((attr, [start, start + 1, start + 2, start + 3]))
        else:
            vertices.extend((p0, p1, p2))
            faces.append((attr, [start, start + 1, start + 2]))

        link = (attr >> 8) & 3
        if link in (0, 2):
            p0, p1 = p2, p3
        elif link == 1:
            p1 = p2
        else:
            p0 = p3

    args.output.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# oba=0x{args.oba:08x} records={len(faces)} words={cursor}", "o vonj_object"]
    lines.extend(f"v {x:.8g} {y:.8g} {z:.8g}" for x, y, z in vertices)
    for attr, face in faces:
        lines.append(f"# attr=0x{attr:08x} header_offset={(attr >> 12) & 0x1f}")
        lines.append("f " + " ".join(map(str, face)))
    args.output.write_text("\n".join(lines) + "\n")
    print(f"wrote {len(faces)} faces and {len(vertices)} vertices to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
