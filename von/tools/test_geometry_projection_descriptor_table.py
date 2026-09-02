#!/usr/bin/env python3
"""Validate the populated projection-mask descriptor records in the ROM image."""

from __future__ import annotations

import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ROM = ROOT / "von/build/disasm/vonj-maincpu.bin"
GEOMETRY_ROM = ROOT / "von/build/disasm/geometry-rom.bin"
BASE = 0x9B8D0
GEOMETRY_ROM_BASE = 0x2F00000
MASK_GRID_WORDS = 0x240


def main() -> int:
    with ROM.open("rb") as stream:
        stream.seek(BASE)
        records = [struct.unpack("<5I", stream.read(20)) for _ in range(8)]

    expected = [
        (0x00000008, 0x02FB8F50, 0x0009B4D0, 0x00000004, 0x0009B7E0),
        (0x00000007, 0x02FB9850, 0x0009B550, 0x00000000, 0x00000000),
        (0x00000009, 0x00143884, 0x0009B670, 0x00000000, 0x00000000),
        (0x00000000, 0x00000000, 0x00000000, 0x00000008, 0x0009B810),
        (0x00000004, 0x02FBB350, 0x0009B5C0, 0x00000000, 0x00000000),
        (0x00000007, 0x02FBBC50, 0x0009B600, 0x00000000, 0x00000000),
        (0x00000008, 0x02FBCE50, 0x0009B700, 0x00000008, 0x0009B870),
        (0x00000006, 0x02FBD750, 0x0009B780, 0x00000000, 0x00000000),
    ]
    if records != expected:
        raise SystemExit(f"projection descriptor table changed: {records!r}")

    populated = [mode for mode, record in enumerate(records) if record[0] != 0]
    if populated != [0, 1, 2, 4, 5, 6, 7]:
        raise SystemExit(f"unexpected populated projection modes: {populated}")

    # Each descriptor's third word points at 16-byte [x, y, z, tag] records.
    point_blocks = {
        0: (0x9B4D0, 8, [0, 4, 2, 3, 4, 5, 6, 7]),
        1: (0x9B550, 7, [8, 8, 8, 8, 8, 8, 9]),
        2: (0x9B670, 9, list(range(0x13, 0x1C))),
        4: (0x9B5C0, 8, [0x0A, 0x0B, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F]),
        5: (0x9B600, 7, list(range(0x0C, 0x13))),
        6: (0x9B700, 8, list(range(0x1C, 0x24))),
        7: (0x9B780, 6, list(range(0x24, 0x2A))),
    }
    with ROM.open("rb") as stream:
        for mode, (address, count, expected_tags) in point_blocks.items():
            stream.seek(address)
            points = [struct.unpack("<4I", stream.read(16)) for _ in range(count)]
            tags = [point[3] for point in points]
            if tags != expected_tags:
                raise SystemExit(f"mode {mode} point tags changed: {tags}")
            if any(len(point) != 4 for point in points):
                raise SystemExit(f"mode {mode} point record width changed")

    mask_blocks = {
        0: (0x2FB8F50, [0xB5A00000, 0xC0510CD3, 0xC0624630, 0x3FAD2EC0,
                        0x31000601, 0x3F21207E, 0x3F44556B, 0xBE00334A]),
        1: (0x2FB9850, [0x3F60C92D, 0xBEF04D10, 0xB4800000, 0xC093D21B,
                        0x3FF4EADA, 0x3F3B739D, 0xC093D21B]),
        2: (0x00143884, [0x3CBD4AF0, 0xBFA91E60, 0x3E206836, 0x3E43714A,
                        0xBFB1BDC0, 0x3E442FE5, 0x78D9F901, 0x3EBECA84,
                        0x3F6D8FDE]),
        4: (0x2FBB350, [0x3E881EA0, 0xBFAD2EC2, 0xC093D21B, 0xBFAD2ECB,
                        0xBFE2462B, 0xC093D21B, 0xBF3B73A8, 0x31800701]),
        5: (0x2FBBC50, [0x3F66B506, 0x39800701, 0x3D6C1D6A, 0x3F7491C2,
                        0xBE9460ED, 0xB3C00000, 0xC09CECF7]),
        6: (0x2FBCE50, [0x3FF4EADB, 0xC093D21B, 0x80000000, 0x3FE24630,
                        0xC093D21B, 0xBF3B738D, 0x29800701, 0xBE9460ED]),
        7: (0x2FBD750, [0x39800701, 0x3E281972, 0x3F7491C1, 0x3E7B942A,
                        0xBF309356, 0xC09CECF7]),
    }
    # 0x9baa0 forms index = x_div * 3 + y_div and compares it against
    # 0x23f. The pointed-to data is therefore a 576-word grid (0x900
    # bytes), not merely the short prefix above. Pin the far edge too;
    # otherwise a valid-looking prefix could be followed by a wrong table
    # base or a truncated extraction.
    expected_grid_tails = {
        0: [0xC08508FF, 0x40243FE5, 0x41000601, 0xBDBF31F3],
        1: [0x4031C84F, 0x408508FF, 0x80000000, 0x40243FE4],
        2: [0xBE895958, 0xBE99D415, 0xBFB3ABEA, 0xBE8B1420],
        4: [0xC09CECF7, 0x3F309358, 0xBEBF1FC6, 0xC09CECF7],
        5: [0xBD63603F, 0x3F7EB809, 0xBDAA256A, 0x3EBF1FBF],
        6: [0xBF79B731, 0xBEBF1FB7, 0xC09CECF7, 0xBF66B508],
        7: [0x3F60C92E, 0xBE881E98, 0xBFFB6C24, 0xC08508FF],
    }
    with GEOMETRY_ROM.open("rb") as stream:
        for mode, (address, expected_words) in mask_blocks.items():
            # Most tables use the 0x2f00000 geometry address window; mode 2
            # references the same ROM through its low address window.
            offset = address - GEOMETRY_ROM_BASE if address >= GEOMETRY_ROM_BASE else address
            stream.seek(offset)
            words = list(struct.unpack("<%dI" % len(expected_words),
                                       stream.read(4 * len(expected_words))))
            if words != expected_words:
                raise SystemExit(f"mode {mode} mask table changed: {words}")

            stream.seek(offset + 4 * (MASK_GRID_WORDS - 4))
            tail = list(struct.unpack("<4I", stream.read(16)))
            if tail != expected_grid_tails[mode]:
                raise SystemExit(f"mode {mode} mask grid tail changed: {tail}")

            stream.seek(offset + 4 * MASK_GRID_WORDS)
            if len(stream.read(4)) != 4:
                raise SystemExit(f"mode {mode} mask grid is truncated")

    print("PASS: projection descriptors, point blocks, and 576-word mask grids")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
