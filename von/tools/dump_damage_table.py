#!/usr/bin/env python3
"""Dump the recovered ordnance/hit damage table from the i960 program image.

Evidence chain (all KNOWN):
  * The startup initializer at i960 ``0xbd618`` copies ``0x334`` words from ROM
    ``0x13a728`` to runtime ``0x565ed0``.
  * The hit applier at ``0xbe0f0`` (and ``0xbe170``) indexes it by the hitting
    projectile's type byte (``ldob (g1)``) with a 16-byte stride and stores the
    first word -- a float -- to the defender's ``object+0x4a``:
        ``g4 = *(float*)&table[type*16]; cvtzri g4; stos g4,0x4a(g2)``.
  * ``0x33334``/``0x33364`` scale that raw value (``object+0x4a * global /
    10000``) and the damage-scaling routine at ``0x33420`` applies the
    profile percent (``+0x63c/640``) before ``0x33838`` does ``health -= r4``.

So each 4-word record is ``{float damage, float knockback/impulse,
int param2, int param3}``.  The record index is the projectile type byte; the
weapon -> type mapping is not yet decoded.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dump_motion_tables import load_maincpu, _ROM_DIR  # noqa: E402

TABLE_ROM = 0x13a728
TABLE_WORDS = 0x334
RECORD_WORDS = 4


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rom-dir", type=Path, default=_ROM_DIR)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    mc = load_maincpu(args.rom_dir)
    records = []
    for r in range(TABLE_WORDS // RECORD_WORDS):
        w = struct.unpack_from("<4I", mc, TABLE_ROM + r * 16)
        damage = struct.unpack("<f", struct.pack("<I", w[0]))[0]
        impulse = struct.unpack("<f", struct.pack("<I", w[1]))[0]
        records.append({"index": r, "damage": round(damage, 3),
                        "impulse": round(impulse, 4),
                        "param2": w[2], "param3": w[3]})
    payload = {"source_rom": f"0x{TABLE_ROM:05x}",
               "runtime": "0x565ed0", "record_words": RECORD_WORDS,
               "records": records}
    encoded = json.dumps(payload, indent=1)
    if args.out:
        args.out.write_text(encoded + "\n")
        print(f"wrote {args.out}")
    else:
        print(encoded)
    damages = sorted({r["damage"] for r in records})
    print(f"{len(records)} records; {len(damages)} distinct damage values")
    print("damage range:", damages[0], "..", damages[-1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
