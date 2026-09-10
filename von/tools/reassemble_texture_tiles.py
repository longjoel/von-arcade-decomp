#!/usr/bin/env python3
"""Rebuild texture bank files from indexed-PNG tiles.

Reads a tiles.json manifest plus its PNGs, blits each tile's indices back
into the named bank at its recorded origin, and writes rebuilt banks. By
default every rebuilt bank must be byte-identical to its source, proving a
lossless round trip; pass --expect-modified with the files you repainted to
allow exactly those tiles' bytes to differ. The PLTE RGB values are never
read: only indices round-trip.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from texture_tile_png import blit_tile, parse_indexed_png


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tiles", type=Path, required=True,
                        help="tiles.json manifest written by extract_texture_tiles.py")
    parser.add_argument("--tile-dir", type=Path, default=None,
                        help="directory holding the tile PNGs (default: manifest parent)")
    parser.add_argument("--bank-dir", type=Path, required=True,
                        help="directory holding the source bank files named by the manifest")
    parser.add_argument("--output-dir", type=Path, required=True,
                        help="directory receiving the rebuilt bank files")
    parser.add_argument("--expect-modified", action="append", default=[],
                        help="tile file allowed to change bank bytes (repeatable)")
    args = parser.parse_args()

    manifest = json.loads(args.tiles.read_text(encoding="utf-8"))
    tile_dir = args.tile_dir or args.tiles.parent
    args.output_dir.mkdir(parents=True, exist_ok=True)

    banks: dict[str, bytearray] = {}
    changed: dict[str, list[str]] = {}
    for entry in manifest.get("tiles", []):
        name = entry["bank"]
        if name not in banks:
            banks[name] = bytearray((args.bank_dir / name).read_bytes())
            changed[name] = []
        tile = parse_indexed_png((tile_dir / entry["file"]).read_bytes())
        if (tile["width"], tile["height"]) != (entry["width"], entry["height"]):
            raise SystemExit(
                f"{entry['file']}: resized tiles need header edits "
                f"(manifest {entry['width']}x{entry['height']}, "
                f"PNG {tile['width']}x{tile['height']})")
        if blit_tile(banks[name], entry["x"], entry["y"],
                     entry["width"], entry["height"], tile["indices"]):
            changed[name].append(entry["file"])

    expected = set(args.expect_modified)
    report: dict = {"ok": True, "banks": {}, "changed": [], "unexpected": []}
    for name, rebuilt in banks.items():
        original = (args.bank_dir / name).read_bytes()
        (args.output_dir / name).write_bytes(bytes(rebuilt))
        changed_here = changed[name]
        report["changed"].extend(changed_here)
        unexpected = [f for f in changed_here if f not in expected]
        report["unexpected"].extend(unexpected)
        report["banks"][name] = {"identical": bytes(rebuilt) == original,
                                 "changed_tiles": changed_here}
    report["ok"] = not report["unexpected"]
    print(json.dumps(report, indent=2))
    if report["unexpected"]:
        raise SystemExit(f"unexpected bank changes from: {sorted(set(report['unexpected']))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
