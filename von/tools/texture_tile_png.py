#!/usr/bin/env python3
"""Indexed-PNG intermediate for Model 2 texture tiles (stdlib only).

Tile pixels are 4-bit indices into a 16-entry palette that is applied at
runtime, so the intermediate must preserve indices exactly: painting in RGB
and re-quantizing on rebuild can silently alter untouched pixels. This
module writes 4-bit indexed PNGs (color type 3) with a 16-entry PLTE for
viewing and ``von:`` tEXt chunks carrying the reassembly provenance
(header words, origin, bank, sheet, colorbase, sampler). Reassembly reads
indices back and ignores the PLTE RGB values.

The nibble packing mirrors ``export_geometry_textured_gltf.texel``; see
``pack_texel_index`` for the inverse mapping.
"""

from __future__ import annotations

import struct
import zlib

PLTE_GRAY: tuple[tuple[int, int, int], ...] = tuple((i * 17, i * 17, i * 17) for i in range(16))

METADATA_PREFIX = "von:"


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def indexed_png(
    width: int,
    height: int,
    indices: bytes,
    palette: tuple[tuple[int, int, int], ...] = PLTE_GRAY,
    metadata: dict[str, str] | None = None,
) -> bytes:
    """Encode one byte per texel (values 0-15) as a 4-bit indexed PNG."""
    if width <= 0 or height <= 0:
        raise ValueError("tile dimensions must be positive")
    if len(indices) != width * height:
        raise ValueError("indices do not match tile dimensions")
    if any(i > 15 for i in indices):
        raise ValueError("indices must fit in 4 bits")
    if len(palette) != 16 or any(len(c) != 3 or any(v < 0 or v > 255 for v in c) for c in palette):
        raise ValueError("palette must hold 16 RGB triples")
    header = struct.pack(">IIBBBBB", width, height, 4, 3, 0, 0, 0)
    out = [b"\x89PNG\r\n\x1a\n", _chunk(b"IHDR", header)]
    out.append(_chunk(b"PLTE", b"".join(bytes(c) for c in palette)))
    for key in sorted((metadata or {})):
        if not key.startswith(METADATA_PREFIX):
            raise ValueError(f"metadata keys must start with {METADATA_PREFIX!r}")
        text = f"{key}\0{(metadata or {})[key]}".encode("latin-1")
        out.append(_chunk(b"tEXt", text))
    stride = (width + 1) // 2
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        row = indices[y * width:(y + 1) * width]
        for x in range(0, width, 2):
            high = row[x] << 4
            low = row[x + 1] if x + 1 < width else 0
            raw.append(high | low)
    out.append(_chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
    out.append(_chunk(b"IEND", b""))
    return b"".join(out)


def parse_indexed_png(data: bytes) -> dict:
    """Decode a 4-bit indexed PNG written by :func:`indexed_png`.

    Returns width, height, per-texel ``indices`` bytes, the 16-entry
    ``palette`` list, and the ``metadata`` dict. Only filter type 0 rows
    are supported, which is all this module ever writes.
    """
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    pos, width, height, palette, metadata, idat = 8, None, None, None, {}, bytearray()
    seen_iend = False
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        kind, payload = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + length]
        want = struct.unpack(">I", data[pos + 8 + length:pos + 12 + length])[0]
        if zlib.crc32(kind + payload) & 0xFFFFFFFF != want:
            raise ValueError(f"bad CRC in {kind!r}")
        pos += 12 + length
        if kind == b"IHDR":
            width, height, depth, color, _, _, _ = struct.unpack(">IIBBBBB", payload)
            if depth != 4 or color != 3:
                raise ValueError("only 4-bit indexed PNGs are supported")
        elif kind == b"PLTE":
            if len(payload) != 48:
                raise ValueError("PLTE must hold 16 entries")
            palette = [tuple(payload[i:i + 3]) for i in range(0, 48, 3)]
        elif kind == b"tEXt":
            keyword, _, text = payload.partition(b"\x00")
            metadata[keyword.decode("latin-1")] = text.decode("latin-1")
        elif kind == b"IDAT":
            idat.extend(payload)
        elif kind == b"IEND":
            seen_iend = True
            break
    if width is None or palette is None or not seen_iend:
        raise ValueError("PNG is missing IHDR, PLTE, or IEND")
    raw = zlib.decompress(bytes(idat))
    stride = (width + 1) // 2
    if len(raw) != height * (stride + 1):
        raise ValueError("IDAT size does not match dimensions")
    indices = bytearray()
    for y in range(height):
        row = raw[y * (stride + 1):(y + 1) * (stride + 1)]
        if row[0] != 0:
            raise ValueError("only filter type 0 rows are supported")
        for x in range(width):
            byte = row[1 + x // 2]
            indices.append((byte >> 4) & 0xF if x % 2 == 0 else byte & 0xF)
    return {"width": width, "height": height, "indices": bytes(indices),
            "palette": palette, "metadata": metadata}


def _sheet_xy(x: int, y: int) -> tuple[int, int]:
    """Mirror of export_geometry_textured_gltf.texture_sheet_xy."""
    x &= 2047
    y &= 1023
    if x >= 1024:
        x -= 1024
        y ^= 1024
    return x, y


def pack_texel_index(bank: bytearray, x: int, y: int, index: int) -> bool:
    """Write one 4-bit texel index, inverting texel()'s nibble packing.

    Returns True when a nibble actually changed.
    """
    if not 0 <= index <= 15:
        raise ValueError("index must fit in 4 bits")
    local_x, local_y = x & 1, y & 1
    sx, sy = _sheet_xy(x, y)
    offset = (sy // 2) * 512 + (sx // 2)
    shift = (16 if offset & 1 else 0) + (0 if local_y else 8) + (0 if local_x else 4)
    at = (offset >> 1) * 4
    if at + 4 > len(bank):
        raise ValueError(f"texel ({x},{y}) is outside the bank")
    word = int.from_bytes(bank[at:at + 4], "little")
    updated = (word & ~(0xF << shift)) | (index << shift)
    bank[at:at + 4] = updated.to_bytes(4, "little")
    return updated != word


def blit_tile(bank: bytearray, x0: int, y0: int, width: int, height: int, indices: bytes) -> list[int]:
    """Blit per-texel indices into bank storage; returns changed texel offsets."""
    if len(indices) != width * height:
        raise ValueError("indices do not match tile dimensions")
    changed: list[int] = []
    for y in range(height):
        for x in range(width):
            if pack_texel_index(bank, x0 + x, y0 + y, indices[y * width + x]):
                changed.append(y * width + x)
    return changed
