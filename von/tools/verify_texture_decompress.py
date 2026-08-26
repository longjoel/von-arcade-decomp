#!/usr/bin/env python3
"""Compare the recovered 0x27e50 decoder with original MAME texture dumps."""

from __future__ import annotations

import argparse
from pathlib import Path


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


def decompress(source: bytes, format_table: bytes) -> tuple[list[int], list[int]]:
    header = int.from_bytes(source[:4], "big")
    words = header >> 1
    source_index = 4
    ring = bytearray(0x1000)
    write_index = 0xfee
    flags = 0
    primary: list[int] = []
    secondary: list[int] = []

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
        if output_index < 0x60000 or not helper_bank(output_index):
            primary.append(output_word)
            secondary.append(0)
        else:
            primary.append(0)
            secondary.append(output_word)
    return primary, secondary


def load_dump(path: Path) -> list[int]:
    return [int(line.split()[1], 16) for line in path.read_text().splitlines()
            if line and not line.startswith("#")]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom-dir", type=Path, default=Path("von/artifacts"))
    parser.add_argument("--maincpu", type=Path,
                        default=Path("von/build/disasm/vonj-maincpu.bin"))
    parser.add_argument("--dump-dir", type=Path, default=Path("von/build/disasm"))
    args = parser.parse_args()
    main_data = assemble_main_data(args.rom_dir)
    format_table = args.maincpu.read_bytes()[0x27c50:0x27e50]
    first, _ = decompress(main_data[0xc00008:], format_table)
    second, _ = decompress(main_data[0xc77438:], format_table)
    actual_first = load_dump(args.dump_dir / "texture-11000000.hex")
    actual_second = load_dump(args.dump_dir / "texture-11200000.hex")
    for name, wanted, actual in (
        ("0x11000000", first, actual_first),
        ("0x11200000", second, actual_second),
    ):
        if wanted == actual:
            print(f"{name}: match {len(actual)} halfwords")
        else:
            for index, (expected, got) in enumerate(zip(wanted, actual)):
                if expected != got:
                    print(f"{name}: mismatch at 0x{index:x}: "
                          f"expected {expected:04x}, got {got:04x}")
                    return 1
            print(f"{name}: length mismatch")
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
