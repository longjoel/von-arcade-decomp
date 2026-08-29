#!/usr/bin/env python3
"""Compare recovered 0x27e50 writes with an original MAME write trace."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


def assemble_main_data(rom_dir: Path) -> bytes:
    image = bytearray(0x1000000)
    for name_a, name_b, base in (
        ("mpr-18648.11", "mpr-18649.12", 0x000000),
        ("mpr-18650.9", "mpr-18651.10", 0x800000),
    ):
        low = (rom_dir / name_a).read_bytes()
        high = (rom_dir / name_b).read_bytes()
        for index in range(0, len(low), 2):
            target = base + index * 2
            image[target:target + 2] = low[index:index + 2]
            image[target + 2:target + 4] = high[index:index + 2]
    return bytes(image)


def decompress(source: bytes, format_table: bytes, *, include_routes: bool = False):
    header = int.from_bytes(source[:4], "big")
    words = header >> 1
    source_index = 4
    ring = bytearray(0x1000)
    write_index = 0xfee
    flags = 0
    primary: list[int] = []
    secondary: list[int] = []
    secondary_routes: list[bool] = []

    def helper_bank(index: int) -> bool:
        low = format_table[index & 0x1ff]
        high = format_table[(index >> 8) & 0x1fe]
        return (
            low == 1 or high == 1
            or (high == 3 and low >= 3)
            or (low == 3 and high >= 4)
            or (high == 5 and low >= 5)
            or (low == 5 and high >= 6)
            or (high == 7 and low >= 7)
            or (low == 7 and high >= 8)
            or (high == 9 and low >= 9)
            or (low == 9 and high >= 10)
        )

    decoded = bytearray()
    while len(decoded) < words * 2:
        flags >>= 1
        if not flags & 0x100:
            flags = source[source_index] | 0xff00
            source_index += 1
        if flags & 1:
            values = (source[source_index],)
            source_index += 1
        else:
            low = source[source_index]
            high = source[source_index + 1]
            source_index += 2
            copy_offset = ((high & 0xf0) << 4) | low
            values = (ring[(copy_offset + copy_index) & 0xfff]
                      for copy_index in range((high & 0x0f) + 3))
        for value in values:
            if len(decoded) == words * 2:
                break
            decoded.append(value)
            ring[write_index] = value
            write_index = (write_index + 1) & 0xfff
    for output_index in range(words):
        output_word = decoded[output_index * 2] | (decoded[output_index * 2 + 1] << 8)
        use_secondary = output_index >= 0x60000 and helper_bank(output_index)
        secondary_routes.append(use_secondary)
        if not use_secondary:
            primary.append(output_word)
            secondary.append(0)
        else:
            primary.append(0)
            secondary.append(output_word)
    if include_routes:
        return primary, secondary, secondary_routes
    return primary, secondary


WRITE_PATTERN = re.compile(
    r"vonj_texture_write: pc=([0-9a-f]+) address=([0-9a-f]+) data=([0-9a-f]+)"
)


def load_write_trace(path: Path) -> list[tuple[int, int]]:
    writes = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = WRITE_PATTERN.search(line)
        if match:
            writes.append((int(match.group(2), 16), int(match.group(3), 16)))
    return writes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom-dir", type=Path, default=Path("von/artifacts"))
    parser.add_argument("--maincpu", type=Path,
                        default=Path("von/build/disasm/vonj-maincpu.bin"))
    parser.add_argument(
        "--write-trace",
        type=Path,
        default=Path("von/build/disasm/vonj-texture-buffers.trace"),
        help="MAME trace produced by the debug texture-write patch",
    )
    args = parser.parse_args()
    main_data = assemble_main_data(args.rom_dir)
    format_table = args.maincpu.read_bytes()[0x27c50:0x27e50]
    first_primary, first_secondary, first_routes = decompress(
        main_data[0xc00008:], format_table, include_routes=True
    )
    expected = [
        (
            (0x11200000 if first_routes[index] else 0x11000000) + index * 2,
            first_secondary[index] if first_routes[index] else first_primary[index],
        )
        for index in range(len(first_primary))
    ]
    actual = load_write_trace(args.write_trace)
    if not actual:
        print(
            f"error: no vonj_texture_write records in {args.write_trace}; "
            "rebuild MAME with VON_MAME_PATCH_SET=debug",
            file=sys.stderr,
        )
        return 1
    for index, (wanted, got) in enumerate(zip(expected, actual)):
        if wanted != got:
            print(
                f"mismatch at write {index}: expected address={wanted[0]:08x} "
                f"data={wanted[1]:04x}, got address={got[0]:08x} data={got[1]:04x}"
            )
            return 1
    if len(actual) > len(expected):
        print(f"error: trace has {len(actual)} writes, decoder has {len(expected)}", file=sys.stderr)
        return 1
    print(f"match: {len(actual)} traced decoder writes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
