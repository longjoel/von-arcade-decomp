#!/usr/bin/env python3
"""Exhaustively test recovered text/tile control and glyph boundaries."""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

from verify_texture_decompress import assemble_main_data


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text.c"
MEMORY_SOURCE = ROOT / "von/i960/recovered_memory.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-text-control-") as directory:
        library = Path(directory) / "text-control.so"
        subprocess.run(
            [
                os.environ.get("CC", "cc"),
                "-shared",
                "-fPIC",
                "-O2",
                SOURCE,
                MEMORY_SOURCE,
                "-o",
                library,
            ],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        recovered.recovered_text_tile_control_bus.argtypes = [
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        recovered.recovered_text_tile_control_bus.restype = ctypes.c_uint32
        recovered.recovered_text_string_font_mode.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte),
        ]
        recovered.recovered_text_string_font_mode.restype = ctypes.c_uint32
        recovered.recovered_text_glyph_address_plan.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        recovered.recovered_text_glyph_address_plan.restype = ctypes.c_uint32
        recovered.recovered_text_glyph_tile_plan.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        recovered.recovered_text_glyph_tile_plan.restype = ctypes.c_uint32
        recovered.recovered_text_glyph_next_column.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        recovered.recovered_text_glyph_next_column.restype = ctypes.c_uint32

        vectors = 0
        for value in range(0x10000):
            address = ctypes.c_uint32()
            actual = recovered.recovered_text_tile_control_bus(value, ctypes.byref(address))
            if actual != value or address.value != 0x01800000:
                raise SystemExit(
                    f"tile-control mismatch value=0x{value:04x}: "
                    f"address=0x{address.value:08x}, value=0x{actual:08x}"
                )
            vectors += 1

        mode_vectors = 0
        for first in range(0x100):
            for second in range(0x100):
                text = (ctypes.c_ubyte * 3)(first, second, 0)
                expected = 0 if first != 0 and 0x61 <= second <= 0x7A else 1
                actual = recovered.recovered_text_string_font_mode(text)
                if actual != expected:
                    raise SystemExit(
                        f"font-mode mismatch first=0x{first:02x} "
                        f"second=0x{second:02x}: {actual} != {expected}"
                    )
                mode_vectors += 1

        glyph_vectors = 0
        for character in range(0x100):
            for font_mode in range(8):
                for column in (0, 1, 31, 61, 62):
                    for row in (0, 1, 46, 47, 63):
                        normalized = ctypes.c_uint32()
                        bank = ctypes.c_uint32()
                        descriptor = ctypes.c_uint32()
                        tile_first = ctypes.c_uint32()
                        tile_second = ctypes.c_uint32()
                        valid = recovered.recovered_text_glyph_address_plan(
                            character,
                            font_mode,
                            column,
                            row,
                            ctypes.byref(normalized),
                            ctypes.byref(bank),
                            ctypes.byref(descriptor),
                            ctypes.byref(tile_first),
                            ctypes.byref(tile_second),
                        )
                        character7 = character & 0x7F
                        expected_normalized = (
                            character7 - 0x20 if character7 >= 0x20 else 0
                        )
                        expected_bank = font_mode & 3
                        expected_descriptor = (
                            (0x02EA11D0, 0x02EA14D0, 0x02EA17D0, 0x02EA1AD0)[
                                expected_bank
                            ]
                            + (expected_normalized << 3)
                        )
                        expected_tile = 0x01000000 + (
                            ((row << 6) + column) << 1
                        )
                        expected = (
                            1,
                            expected_normalized,
                            expected_bank,
                            expected_descriptor,
                            expected_tile,
                            expected_tile + 0x80,
                        )
                        actual = (
                            valid,
                            normalized.value,
                            bank.value,
                            descriptor.value,
                            tile_first.value,
                            tile_second.value,
                        )
                        if actual != expected:
                            raise SystemExit(
                                f"glyph plan mismatch character=0x{character:02x} "
                                f"mode={font_mode} column={column} row={row}: "
                                f"{actual!r} != {expected!r}"
                            )
                        glyph_vectors += 1

        main_data = assemble_main_data(ROOT / "von/artifacts")
        descriptor_vectors = 0
        for bank, base in enumerate((
            0x02EA11D0,
            0x02EA14D0,
            0x02EA17D0,
            0x02EA1AD0,
        )):
            for index in range(96):
                descriptor = base + index * 8
                offset = descriptor - 0x02000000
                glyph_data = int.from_bytes(main_data[offset:offset + 4], "little")
                width = int.from_bytes(main_data[offset + 4:offset + 8], "little")
                if not 0x02000000 <= glyph_data < 0x03000000 or width not in (1, 2):
                    raise SystemExit(
                        f"invalid glyph descriptor bank={bank} index={index}: "
                        f"data=0x{glyph_data:08x} width={width}"
                    )
                for plane in range(2):
                    for entry in range(width):
                        word_address = ctypes.c_uint32()
                        tile_address = ctypes.c_uint32()
                        valid = recovered.recovered_text_glyph_tile_plan(
                            glyph_data,
                            width,
                            12,
                            22,
                            plane,
                            entry,
                            ctypes.byref(word_address),
                            ctypes.byref(tile_address),
                        )
                        expected = (
                            glyph_data + (plane * width + entry) * 2,
                            0x01000000 + (((12 + plane) << 6) + 22 + entry) * 2,
                        )
                        actual = (word_address.value, tile_address.value)
                        if valid != 1 or actual != expected:
                            raise SystemExit(
                                f"glyph tile plan mismatch bank={bank} index={index} "
                                f"plane={plane} entry={entry}: {actual!r} != {expected!r}"
                            )
                        descriptor_vectors += 1
                invalid_word = ctypes.c_uint32()
                invalid_tile = ctypes.c_uint32()
                if recovered.recovered_text_glyph_tile_plan(
                    glyph_data,
                    width,
                    12,
                    22,
                    2,
                    0,
                    ctypes.byref(invalid_word),
                    ctypes.byref(invalid_tile),
                ) != 0:
                    raise SystemExit("accepted invalid glyph plane")

        column_vectors = 0
        for normalized_character in range(96):
            for column in range(64):
                for width in range(4):
                    expected = column + (1 if normalized_character == 0x5C else 0)
                    if expected <= 61:
                        expected += width
                    actual = recovered.recovered_text_glyph_next_column(
                        normalized_character, column, width
                    )
                    if actual != expected:
                        raise SystemExit(
                            f"glyph column mismatch character={normalized_character} "
                            f"column={column} width={width}: {actual} != {expected}"
                        )
                    column_vectors += 1

    print(
        f"PASS: {vectors:,} text/tile control vectors and "
        f"{mode_vectors:,} font-mode prefixes and "
        f"{glyph_vectors:,} glyph address plans and "
        f"{descriptor_vectors:,} descriptor tiles and "
        f"{column_vectors:,} glyph column updates"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
