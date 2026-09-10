#!/usr/bin/env python3
"""Test indexed-PNG tile intermediates and bank reassembly."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from export_geometry_textured_gltf import texel
from texture_tile_png import blit_tile, indexed_png, parse_indexed_png


def check(name: str, condition: bool) -> None:
    if not condition:
        raise SystemExit(f"FAILED: {name}")


def tile_bytes(width: int, height: int, seed: int = 0) -> bytes:
    return bytes((x * 7 + y * 13 + seed) % 16 for y in range(height) for x in range(width))


def main() -> int:
    # PNG round trip, including odd widths (nibble padding) and metadata.
    for width, height in ((4, 4), (5, 3), (32, 32)):
        indices = tile_bytes(width, height)
        meta = {"von:header": "0x40000c", "von:origin": "0,0", "von:size": f"{width}x{height}",
                "von:bank": "bank0-primary.bin", "von:sheet": "0",
                "von:colorbase": "0x9", "von:source": "select.trace"}
        blob = indexed_png(width, height, indices, metadata=meta)
        back = parse_indexed_png(blob)
        check(f"round trip {width}x{height}", back["indices"] == indices)
        check(f"dims {width}x{height}", (back["width"], back["height"]) == (width, height))
        check("metadata", back["metadata"] == meta)
        check("gray plte", back["palette"][5] == (85, 85, 85))
    custom = tuple((i * 16, 255 - i * 16, i) for i in range(16))
    back = parse_indexed_png(indexed_png(2, 2, b"\x00\x01\x02\x03", palette=custom))
    check("custom plte", back["palette"][1] == (16, 239, 1))
    check("indices exact", back["indices"] == b"\x00\x01\x02\x03")

    for bad in (lambda: indexed_png(0, 4, b""),
                lambda: indexed_png(2, 2, b"\x00\x01"),
                lambda: indexed_png(2, 2, b"\x00\x01\x02\x10"),
                lambda: indexed_png(2, 2, b"\x00\x01\x02\x03", metadata={"header": "x"}),
                lambda: parse_indexed_png(b"nope"),
                lambda: parse_indexed_png(indexed_png(2, 2, b"\x00\x01\x02\x03")[:-4] + b"zzzz")):
        try:
            bad()
        except ValueError:
            pass
        else:
            raise SystemExit("FAILED: expected ValueError")

    # pack/unpack round trip against the real texel() reader, covering odd
    # coords, bank halves, and the x >= 1024 sheet wrap.
    bank = bytearray(1 << 20)
    regions = [(0, 0, 8, 8), (1, 3, 7, 5), (1022, 1022, 6, 6), (1500, 700, 4, 4)]
    for sequence, (x0, y0, width, height) in enumerate(regions):
        indices = tile_bytes(width, height, sequence)
        changed = blit_tile(bank, x0, y0, width, height, indices)
        check("blit touches bytes", changed)
        for y in range(height):
            for x in range(width):
                check(f"texel inverse {x0 + x},{y0 + y}",
                      texel(bytes(bank), x0 + x, y0 + y) // 17 == indices[y * width + x])
    fresh = bytearray(1 << 20)
    blit_tile(fresh, 0, 0, 8, 8, tile_bytes(8, 8, 0))
    check("reblit is a no-op", blit_tile(fresh, 0, 0, 8, 8, tile_bytes(8, 8, 0)) == [])

    with tempfile.TemporaryDirectory(prefix="von-tilepng-") as directory:
        root = Path(directory)
        bank_file = root / "bank0-primary.bin"
        bank_file.write_bytes(bytes(1 << 15))
        trace = root / "select.trace"
        trace.write_text(
            "vonj_texture_command: time=1.0 uv=1234 header=40 "
            "tex=0000,0000,0000,0000 attr=0000 colorbase=0009 sheet=0 "
            "size=32x32 origin=2048,1024\n"
            "vonj_texture_command: time=2.0 uv=1234 header=44 "
            "tex=0000,0000,0000,0000 attr=0000 colorbase=0009 sheet=1 "
            "size=32x32 origin=2048,1024\n")
        tiles = root / "tiles"
        run = subprocess.run(
            [sys.executable, "von/tools/extract_texture_tiles.py", "--trace", str(trace),
             "--bank", str(bank_file), "--output-dir", str(tiles),
             "--format", "png", "--limit", "4"],
            capture_output=True, text=True, cwd=Path.cwd())
        check("extractor png exit", run.returncode == 0)
        names = sorted(p.name for p in tiles.glob("*.png"))
        check("one sheet-0 tile", len(names) == 1)
        manifest = json.loads((tiles / "tiles.json").read_text())
        check("manifest bank", manifest["tiles"][0]["bank"] == "bank0-primary.bin")
        check("index rows", len((tiles / "index.tsv").read_text().strip().splitlines()) == 2)

        # Unmodified round trip: rebuilt banks must be bit-identical.
        rebuilt = root / "rebuilt"
        run = subprocess.run(
            [sys.executable, "von/tools/reassemble_texture_tiles.py", "--tiles", str(tiles / "tiles.json"),
             "--bank-dir", str(root), "--output-dir", str(rebuilt)],
            capture_output=True, text=True, cwd=Path.cwd())
        check("reassemble exit", run.returncode == 0)
        check("bit-identical", (rebuilt / "bank0-primary.bin").read_bytes() == bank_file.read_bytes())

        # Repainted tile without declaration must fail loudly.
        tile = parse_indexed_png((tiles / names[0]).read_bytes())
        edited = bytearray(tile["indices"])
        edited[0] ^= 0xF
        (tiles / names[0]).write_bytes(
            indexed_png(tile["width"], tile["height"], bytes(edited), metadata=tile["metadata"]))
        run = subprocess.run(
            [sys.executable, "von/tools/reassemble_texture_tiles.py", "--tiles", str(tiles / "tiles.json"),
             "--bank-dir", str(root), "--output-dir", str(rebuilt)],
            capture_output=True, text=True, cwd=Path.cwd())
        check("undeclared edit fails", run.returncode != 0 and names[0] in run.stdout)
        run = subprocess.run(
            [sys.executable, "von/tools/reassemble_texture_tiles.py", "--tiles", str(tiles / "tiles.json"),
             "--bank-dir", str(root), "--output-dir", str(rebuilt),
             "--expect-modified", names[0]],
            capture_output=True, text=True, cwd=Path.cwd())
        check("declared edit passes", run.returncode == 0)
        check("edit landed", (rebuilt / "bank0-primary.bin").read_bytes() != bank_file.read_bytes())

    print("PASS: indexed-PNG tile intermediates and bank reassembly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
