#!/usr/bin/env python3
"""Regression checks for Model 2 texture-bank selection and sheet decoding.

The oracle is a direct transcription of MAME's ``model2_renderer::get_texel``
(model2rd.ipp:18) and the bank select at model2_v.cpp:590. No ROMs are needed:
banks are synthesized, and the hex-dump parser is checked against raw bytes.
"""

from __future__ import annotations

import struct
import tempfile
import zlib
from pathlib import Path

from model2_texture import (BANK_BIT, load_banks, load_sheet, bank_index,
                            select_sheet, texel, texel_index, texture_size,
                            texture_uv, tile_png)


def check(name: str, condition: bool) -> None:
    if not condition:
        raise SystemExit(f"FAILED: {name}")


def mame_get_texel(sheet: bytes, base_x: int, base_y: int, x: int, y: int) -> int:
    x2 = base_x + x
    y2 = base_y + y
    if x2 >= 1024:
        x2 -= 1024
        y2 ^= 1024
    offset = ((y2 // 2) * 512) + (x2 // 2)
    word = int.from_bytes(sheet[(offset >> 1) * 4:(offset >> 1) * 4 + 4], "little")
    if offset & 1:
        word >>= 16
    if (y & 1) == 0:
        word >>= 8
    if (x & 1) == 0:
        word >>= 4
    return word & 0x0F


def grayscale_pixels(png: bytes) -> tuple[int, int, bytes]:
    width = height = None
    idat = bytearray()
    pos = 8
    while pos < len(png):
        length = struct.unpack(">I", png[pos:pos + 4])[0]
        kind = png[pos + 4:pos + 8]
        payload = png[pos + 8:pos + 8 + length]
        pos += 12 + length
        if kind == b"IHDR":
            width, height = struct.unpack(">II", payload[:8])
        elif kind == b"IDAT":
            idat.extend(payload)
    raw = zlib.decompress(bytes(idat))
    pixels = bytearray()
    for row in range(height):
        pixels.extend(raw[row * (width + 1) + 1:row * (width + 1) + 1 + width])
    return width, height, bytes(pixels)


def main() -> int:
    # A deterministic non-trivial sheet.
    sheet0 = bytes(((x * 7 + y * 13) & 0xFF) for y in range(1024) for x in range(512))
    sheet0 = sheet0.ljust(1 << 20, b"\x00")[:1 << 20]
    sheet1 = bytes((v ^ 0x5A) for v in sheet0)
    banks = {0: sheet0, 1: sheet1}

    # Bank select is bit 12 of the third header word (model2_v.cpp:590).
    check("bank bit clear -> RAM0", bank_index((0x40C9, 0, 0x09CB, 0x7440)) == 0)
    check("bank bit set -> RAM1", bank_index((0x40C9, 0, 0x19CB, 0x7440)) == 1)
    check("select_sheet RAM0", select_sheet((0, 0, 0, 0), banks) is sheet0)
    check("select_sheet RAM1", select_sheet((0, 0, 0x1000, 0), banks) is sheet1)
    check("BANK_BIT", BANK_BIT == 0x1000)

    # texel_index must equal MAME's get_texel over the whole folded sheet,
    # including the x >= 1024 right-half fold and both address halves.
    # MAME calls get_texel(tex_x, tex_y, u, v) with a 32-aligned (even) origin and
    # local 0/1 offsets; texel_index takes the combined sheet coordinate.
    probes = [(0, 0), (2, 4), (32, 0), (96, 192), (1022, 16), (1024, 16),
              (2046, 1022), (1500, 700), (700, 1500), (510, 510), (1024, 1024)]
    for bx, by in probes:
        for x, y in ((0, 0), (1, 0), (0, 1), (1, 1)):
            check(f"get_texel {bx},{by}+{x},{y}",
                  texel_index(sheet0, bx + x, by + y) == mame_get_texel(sheet0, bx, by, x, y))
            check(f"get_texel bank1 {bx},{by}+{x},{y}",
                  texel_index(sheet1, bx + x, by + y) == mame_get_texel(sheet1, bx, by, x, y))
    check("texel gray scale", texel(sheet0, 10, 12) == texel_index(sheet0, 10, 12) * 17)

    # tile_png must crop from the header-selected bank, not the other one.
    def stamp(header, value):
        w, h, ox, oy, _ = texture_size(header)
        return w, h, ox, oy

    header0 = (0x40C9, 0, 0x0001, 0x7440)   # 64x64, origin (32,0), RAM0
    header1 = (0x40C9, 0, 0x1001, 0x7440)   # same but RAM1
    # Paint index 7 across the tile region in RAM1 only.
    w, h, ox, oy = stamp(header1, 7)
    patched = bytearray(sheet1)
    for y in range(oy, oy + h):
        for x in range(ox, ox + w):
            from texture_tile_png import pack_texel_index
            pack_texel_index(patched, x, y, 7)
    banks1 = {0: sheet0, 1: bytes(patched)}
    png0 = tile_png(header0, banks1)
    png1 = tile_png(header1, banks1)
    check("tile png dims", grayscale_pixels(png1)[:2] == (64, 64))
    check("tile png reads selected bank", set(grayscale_pixels(png1)[2]) == {7 * 17})
    check("tile png other bank differs", set(grayscale_pixels(png0)[2]) != {7 * 17})

    # load_sheet must accept raw .bin and MAME .hex dumps identically.
    with tempfile.TemporaryDirectory(prefix="von-banks-") as directory:
        root = Path(directory)
        raw = root / "bank0.bin"
        raw.write_bytes(sheet0)
        text = root / "bank1.hex"
        with text.open("w") as handle:
            handle.write("# address=11200000 words=80000\n")
            for index in range(0, (1 << 20) // 2):
                word = sheet0[index * 2] | (sheet0[index * 2 + 1] << 8)
                handle.write(f"{index:06x} {word:04x}\n")
        check("load_sheet bin", load_sheet(raw) == sheet0)
        check("load_sheet hex", load_sheet(text) == sheet0)
        loaded = load_banks(raw, text)
        check("load_banks keys", set(loaded) == {0, 1})

    check("uv scale unchanged", texture_uv(512, 256, (0x40C9, 0, 0x09CB, 0x7440)) == (1.0, 0.5))

    print("PASS: Model 2 texture bank select, sheet fold, and hex loading")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
