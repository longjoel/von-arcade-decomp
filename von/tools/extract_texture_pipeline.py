#!/usr/bin/env python3
"""Extract Virtual-On's texture ROM and decompressed texture RAM banks."""

from __future__ import annotations

import argparse
from pathlib import Path

from verify_texture_decompress import assemble_main_data, decompress


def assemble_texture_rom(rom_dir: Path) -> bytes:
    image = bytearray(0x1000000)
    for name, base in (
        ("mpr-18660.27", 0x000000),
        ("mpr-18658.25", 0x000002),
        ("mpr-18661.28", 0x800000),
        ("mpr-18659.26", 0x800002),
    ):
        data = (rom_dir / name).read_bytes()
        for index in range(0, len(data), 2):
            image[base + index * 2:base + index * 2 + 2] = data[index:index + 2]
    return bytes(image)


def words_to_bytes(words: list[int]) -> bytes:
    output = bytearray()
    for word in words:
        output.extend((word & 0xff, word >> 8))
    return bytes(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom-dir", type=Path, default=Path("von/artifacts"))
    parser.add_argument("--maincpu", type=Path,
                        default=Path("von/build/disasm/vonj-maincpu.bin"))
    parser.add_argument("--output-dir", type=Path,
                        default=Path("von/build/disasm/texture-pipeline"))
    args = parser.parse_args()

    main_data = assemble_main_data(args.rom_dir)
    format_table = args.maincpu.read_bytes()[0x27c50:0x27e50]
    primary0, secondary0 = decompress(main_data[0xc00008:], format_table)
    primary1, secondary1 = decompress(main_data[0xc77438:], format_table)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "texture-rom.bin").write_bytes(
        assemble_texture_rom(args.rom_dir))
    (args.output_dir / "bank0-primary.bin").write_bytes(words_to_bytes(primary0))
    (args.output_dir / "bank0-secondary.bin").write_bytes(words_to_bytes(secondary0))
    (args.output_dir / "bank1-primary.bin").write_bytes(words_to_bytes(primary1))
    (args.output_dir / "bank1-secondary.bin").write_bytes(words_to_bytes(secondary1))
    print(f"wrote texture pipeline artifacts to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
