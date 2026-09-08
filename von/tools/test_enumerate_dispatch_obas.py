#!/usr/bin/env python3
"""ROM-free tests for the dispatch-table oba enumerator.

Synthetic main_data and geometry images exercise table parsing,
polygon-ROM gating, window bounds, and manifest output. No MAME,
no traces, no private ROMs.
"""

from __future__ import annotations

import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "von/tools"))

from enumerate_dispatch_obas import read_table
import enumerate_dispatch_obas as enumerator


def make_main_data(entries, count=30) -> bytes:
    base = enumerator.TABLE_ADDRESS - enumerator.MAIN_DATA_BASE
    padded = list(entries) + [(0, 0, 0)] * (count - len(entries))
    image = bytearray(base + len(padded) * enumerator.ENTRY_STRIDE)
    for index, words in enumerate(padded):
        struct.pack_into("<3I", image, base + index * 12, *words)
    return bytes(image)


def main() -> int:
    entries = [(0, 0, 0),
               (0x00400C54, 0x00400C54, 0x0084695E),
               (0x00400C58, 0x00400C58, 0x00000010)]
    table = read_table(make_main_data(entries), count=3)
    assert table == entries, table

    import tempfile
    with tempfile.TemporaryDirectory(prefix="von-enum-") as directory:
        out = Path(directory)
        geometry = bytearray(0x4695E * 4 + 16)
        struct.pack_into("<I", geometry, 0x4695E * 4, 0xDEADBEEF)
        (out / "geo.bin").write_bytes(bytes(geometry))

        real_load = enumerator.load_main_data
        enumerator.load_main_data = lambda _rom: make_main_data(entries)
        try:
            argv = ["enumerate",
                    "--rom-dir", str(out),
                    "--geometry-rom", str(out / "geo.bin"),
                    "--output-dir", str(out / "objs"),
                    "--window", "4"]
            sys.argv = [sys.argv[0]] + argv[1:]
            assert enumerator.main() == 0
        finally:
            enumerator.load_main_data = real_load

        manifest = json.loads((out / "objs/manifest.json").read_text())
        assert len(manifest) == 30, len(manifest)
        assert [record["index"] for record in manifest[:3]] == [0, 1, 2]
        assert manifest[0]["polygon_rom"] is False
        assert manifest[0]["file"] is None
        assert manifest[1]["oba"] == "0084695e"
        assert manifest[1]["words"] == 4, manifest[1]
        assert manifest[2]["polygon_rom"] is False, "low oba gated"
        window = (out / "objs/01-oba0084695e.hex").read_text().split()
        assert len(window) == 4 and all(len(w) == 8 for w in window), window
        print("PASS: table parse, gating, windows, manifest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
