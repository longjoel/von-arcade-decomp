#!/usr/bin/env python3
"""Model 2 texture fetch: banks, sheets, texels, and palette-rendered tiles.

The Model 2 renders every textured polygon from one of two texture RAMs,
selected solely by bit 12 of the texture header's third word:

    model2_v.cpp:590
    extra.texsheet[0] = (poly->texheader[2] & 0x1000) ? m_textureram1 : m_textureram0;

Each RAM is a 2048x1024 4bpp sheet stored folded as 1024x2048; MAME's
``get_texel`` (model2rd.ipp:18) folds the logical right half onto Y bit 10:

    if (x2 >= 1024) { x2 -= 1024; y2 ^= 1024; }

The i960 decompresses a source into whichever RAM each word routes to, so the
live content of each RAM is scene-dependent: bank0 generally holds the shared
title/UI atlas and bank1 holds the current stage's textures. Exporters must use
the RAM state that was live while the geometry was drawn, which is captured with
``scripts/trace-texture-buffers.sh`` or ``probe_stage_binding.lua`` and stored as
either a raw ``.bin`` sheet or a MAME ``.hex`` dump.

Selecting the wrong bank, or ignoring the bit as the old exporters did, samples
an unrelated sheet (the "random texture" / missing skybox failure).
"""

from __future__ import annotations

import struct
import zlib

BANK_BIT = 0x1000
SHEET_BYTES = 1 << 20          # 2048x1024 logical sheet, 4bpp, folded to 1024x2048
DEFAULT_BANK0 = "von/build/disasm/texture-pipeline/bank0-primary.bin"
DEFAULT_BANK1 = "von/build/disasm/texture-pipeline/bank1-primary.bin"


def parse_hex_dump(path) -> bytes:
    """Read a ``index hex16`` RAM dump (trace_texture_buffers.lua) into bytes."""
    words: list[int] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) == 2:
            words.append(int(parts[1], 16))
    return b"".join(struct.pack("<H", word) for word in words)


def load_sheet(path) -> bytes:
    """Load one texture RAM as a 1 MiB sheet, from a raw ``.bin`` or MAME ``.hex``."""
    if str(path).endswith(".hex"):
        data = parse_hex_dump(path)
    else:
        data = path.read_bytes()
    if len(data) < SHEET_BYTES:
        data = data.ljust(SHEET_BYTES, b"\x00")
    return data[:SHEET_BYTES]


def load_banks(bank0, bank1) -> dict[int, bytes]:
    """Load the two texture RAMs the renderer can select between."""
    return {0: load_sheet(bank0), 1: load_sheet(bank1)}


def bank_index(header) -> int:
    """The texture RAM a polygon draws from (MAME model2_v.cpp:590)."""
    return 1 if header[2] & BANK_BIT else 0


def select_sheet(header, banks: dict[int, bytes]) -> bytes:
    return banks[bank_index(header)]


def texture_size(header: tuple[int, int, int, int]) -> tuple[int, int, int, int, int]:
    h0, _, h2, h3 = header
    width = 32 << (h0 & 7)
    height = 32 << ((h0 >> 3) & 7)
    origin_x = 32 * (h2 & 0x3f)
    origin_y = 32 * ((h2 >> 6) & 0x1f)
    colorbase = (h3 >> 6) & 0x3ff
    return width, height, origin_x, origin_y, colorbase


def texture_uv(raw_u: int, raw_v: int,
               header: tuple[int, int, int, int]) -> tuple[float, float]:
    """Convert Model 2 1/8-texel UVs into tile-local glTF coordinates.

    The header origin is deliberately not added: exported images are cropped to
    that tile, so glTF coordinates are tile-local.
    """
    width, height, _, _, _ = texture_size(header)
    return raw_u / 8.0 / width, raw_v / 8.0 / height


def texture_sampler(header: tuple[int, int, int, int]) -> tuple[int, int]:
    """glTF wrap modes matching Model 2's regular-texture flags."""
    flags = header[0]

    def axis(wrap_bit: int, mirror_bit: int) -> int:
        if flags & (1 << mirror_bit):
            return 33648  # MIRRORED_REPEAT
        if flags & (1 << wrap_bit):
            return 10497  # REPEAT
        return 33071  # CLAMP_TO_EDGE

    return axis(6, 8), axis(7, 9)


def texture_sheet_xy(x: int, y: int) -> tuple[int, int]:
    """Map a logical 2048x1024 sheet coordinate to folded 1024x2048 storage.

    Mirrors ``model2rd.ipp``: only X triggers the fold. X is expected to be in
    0..2047 and Y in 0..2047, as the hardware masks ``tex_x``/``tex_y`` before
    the fetch; this helper is the inverse used by the tile editor.
    """
    if x >= 1024:
        x -= 1024
        y ^= 1024
    return x, y


def texel_index(sheet: bytes, x: int, y: int) -> int:
    """One 4bpp texel index, mirroring MAME ``model2_renderer::get_texel``.

    ``x``/``y`` are the combined sheet coordinate (tile origin + local offset).
    MAME folds the right half into the 1024x2048 storage by the combined X only;
    it does not clamp Y, so neither do we.
    """
    x2, y2 = x, y
    if x2 >= 1024:
        x2 -= 1024
        y2 ^= 1024
    offset = (y2 // 2) * 512 + (x2 // 2)
    word = int.from_bytes(sheet[(offset >> 1) * 4:(offset >> 1) * 4 + 4], "little")
    if offset & 1:
        word >>= 16
    if (y & 1) == 0:
        word >>= 8
    if (x & 1) == 0:
        word >>= 4
    return word & 0x0f


def texel(sheet: bytes, x: int, y: int) -> int:
    """Backward-compatible texel reader returning the gray-scaled value."""
    return texel_index(sheet, x, y) * 17


def png_gray(width: int, height: int, pixels: bytes) -> bytes:
    def chunk(name: bytes, payload: bytes) -> bytes:
        return (struct.pack(">I", len(payload)) + name + payload +
                struct.pack(">I", zlib.crc32(name + payload) & 0xffffffff))

    rows = b"".join(b"\x00" + pixels[row * width:(row + 1) * width]
                    for row in range(height))
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b""))


def png_rgb(width: int, height: int, pixels: bytes) -> bytes:
    def chunk(name: bytes, payload: bytes) -> bytes:
        return (struct.pack(">I", len(payload)) + name + payload +
                struct.pack(">I", zlib.crc32(name + payload) & 0xffffffff))

    row_size = width * 3
    rows = b"".join(b"\x00" + pixels[row * row_size:(row + 1) * row_size]
                    for row in range(height))
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b""))


def tile_png(header: tuple[int, int, int, int], banks: dict[int, bytes],
             palette_state=None) -> bytes | None:
    """Crop one tile from the header-selected RAM and encode it as PNG.

    Without a captured ``palette_state`` the tile is written as a grayscale ramp
    (indices * 17). With one, each 4bpp index is resolved through the palette,
    color-translation, and luma tables via ``render_texture_palette.palette_rgb``.
    """
    width, height, origin_x, origin_y, colorbase = texture_size(header)
    if width > 2048 or height > 1024:
        return None
    sheet = select_sheet(header, banks)
    indices = bytes(texel_index(sheet, origin_x + x, origin_y + y)
                    for y in range(height) for x in range(width))
    if palette_state is None:
        return png_gray(width, height, bytes(index * 17 for index in indices))
    from render_texture_palette import palette_rgb
    palette, colorxlat, luma = palette_state
    pixels = bytes(channel
                   for index in indices
                   for channel in palette_rgb(index, colorbase, palette, colorxlat, luma))
    return png_rgb(width, height, pixels)
