#!/usr/bin/env python3
"""Extract individual 4bpp texture tiles referenced by a MAME trace.

Each ``vonj_texture_command`` line carries the four texture-header words in
``tex=`` and the selected texture RAM in ``sheet=`` (0 or 1). Tiles are cropped
from the header-selected RAM exactly as the hardware ``get_texel`` would.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from model2_texture import (DEFAULT_BANK0, DEFAULT_BANK1, load_banks,
                            texture_size, texel_index)

from texture_tile_png import indexed_png


COMMAND = re.compile(
    r"vonj_texture_command: (?:time=[0-9.e+-]+ )?uv=([0-9a-f]+) header=([0-9a-f]+) "
    r"tex=([0-9a-f]+),([0-9a-f]+),([0-9a-f]+),([0-9a-f]+) "
    r"attr=([0-9a-f]+) colorbase=([0-9a-f]+) sheet=(\d+) "
    r"size=(\d+)x(\d+) origin=(\d+),(\d+)"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path,
                        default=Path("von/build/disasm/vonj-gameplay-texture.trace"))
    parser.add_argument("--bank0", type=Path, default=Path(DEFAULT_BANK0),
                        help="texture RAM 0 sheet (.bin or MAME .hex dump)")
    parser.add_argument("--bank1", type=Path, default=Path(DEFAULT_BANK1),
                        help="texture RAM 1 sheet (.bin or MAME .hex dump)")
    parser.add_argument("--output-dir", type=Path,
                        default=Path("von/build/disasm/texture-pipeline/tiles"))
    parser.add_argument("--limit", type=int, default=128)
    parser.add_argument("--format", choices=("pgm", "png"), default="pgm",
                        help="pgm keeps the legacy grayscale output; png writes "
                             "4-bit indexed PNGs with von: provenance chunks")
    args = parser.parse_args()

    banks = load_banks(args.bank0, args.bank1)
    bank_names = {0: args.bank0.name, 1: args.bank1.name}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    seen: set[tuple[int, int, int, int, int, int]] = set()
    rows: list[tuple[str, int, int, int, int, int]] = []
    manifest: list[dict] = []

    for match in COMMAND.finditer(args.trace.read_text()):
        groups = match.groups()
        header = tuple(int(groups[i], 16) for i in (2, 3, 4, 5))
        colorbase = int(groups[7], 16)
        bank = int(groups[8])
        width, height, _, _, _ = texture_size(header)
        origin_x, origin_y = map(int, groups[11:13])
        key = (header[0], header[2], width, height, origin_x, origin_y)
        if key in seen or width > 256 or height > 256 or bank not in banks:
            continue
        seen.add(key)
        x0 = origin_x & 2047
        y0 = origin_y & 1023
        sheet = banks[bank]
        indices = bytes(
            texel_index(sheet, x0 + x, y0 + y)
            for y in range(height) for x in range(width)
        )
        stem = f"{len(rows):03d}-cb{colorbase:03x}-{width}x{height}-at{x0:04x}_{y0:03x}"
        if args.format == "png":
            name = stem + ".png"
            metadata = {
                "von:header": "0x%04x_%04x_%04x_%04x" % header,
                "von:origin": f"{x0},{y0}",
                "von:size": f"{width}x{height}",
                "von:bank": bank_names[bank],
                "von:sheet": str(bank),
                "von:colorbase": f"{colorbase:#x}",
                "von:source": args.trace.name,
            }
            (args.output_dir / name).write_bytes(indexed_png(width, height, indices, metadata=metadata))
        else:
            name = stem + ".pgm"
            pixels = bytes(index * 17 for index in indices)
            (args.output_dir / name).write_bytes(
                f"P5\n{width} {height}\n255\n".encode() + pixels)
        rows.append((name, colorbase, width, height, x0, y0))
        manifest.append({"file": name, "header": list(header),
                         "header_hex": "0x%04x_%04x_%04x_%04x" % header,
                         "x": x0, "y": y0, "width": width, "height": height,
                         "colorbase": colorbase, "bank": bank_names[bank], "sheet": bank})
        if len(rows) >= args.limit:
            break

    (args.output_dir / "index.tsv").write_text(
        "file\tcolorbase\twidth\theight\tx\ty\n" +
        "\n".join("\t".join(map(str, row)) for row in rows) + "\n")
    (args.output_dir / "tiles.json").write_text(
        json.dumps({"version": 1, "format": args.format, "tiles": manifest}, indent=2) + "\n")
    print(f"extracted {len(rows)} texture tiles to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
