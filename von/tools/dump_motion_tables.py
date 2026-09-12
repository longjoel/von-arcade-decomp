#!/usr/bin/env python3
"""Dump Virtual-On per-fighter keyframe motion tables from maincpu ROM.

Evidence chain (all KNOWN, verified against the listing):

  * Program table 0x19360 holds 10 per-fighter profile pointers, followed
    by the roster names at 0x19390 (16-byte stride).  The object initializer
    at 0x27550 takes the profile pointer (``g6 = 0x19360[idx*4]``) and files
    it at object+0x6c; the motion code reaches it through [0x51ab14].
  * Each profile is a blob in the i960 program image.  From +0x70 it holds a
    run of paired motion-table pointers (body 15-part and skeleton 8-part).
  * A motion table header is two words: ``[data_ptr, (frames << 16) | parts]``.
    ``0x8dd40`` reads the frame count from +0x4, the part count from +0x6,
    strides ``12 * frame * parts`` into ``data_ptr``, and emits six 16-bit
    values per part (``ldos`` at +0, +2, +4, +6, +8, +10).

Each record is therefore six signed 16-bit words: three translation-ish
components and three Q15 direction components.  Exact matrix semantics are
not yet pinned down (see docs); this tool dumps the raw records plus metadata.
"""

from __future__ import annotations

import argparse
import base64
import json
import struct
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROM_DIR = _HERE.parent / "artifacts"

PROFILE_TABLE = 0x19360
NAME_TABLE = 0x19390
NAME_STRIDE = 0x10
MAIN_DATA_BASE = 0x02000000
MAIN_DATA_END = 0x03000000


def load_maincpu(rom_dir: Path) -> bytes:
    rom_size = 0x80000
    region = bytearray(0x200000)

    def pair(target, low, high, base):
        for i in range(rom_size // 2):
            target[base + i * 4:base + i * 4 + 2] = low[i * 2:i * 2 + 2]
            target[base + i * 4 + 2:base + i * 4 + 4] = high[i * 2:i * 2 + 2]

    pair(region, (rom_dir / "epr-18664b.15").read_bytes(),
         (rom_dir / "epr-18665b.16").read_bytes(), 0x000000)
    pair(region, (rom_dir / "epr-18666.13").read_bytes(),
         (rom_dir / "epr-18667.14").read_bytes(), 0x100000)
    return bytes(region)


def load_main_data(rom_dir: Path) -> bytes:
    image = bytearray(0x2000000)

    def pair(target, low, high, base):
        for i in range(len(low) // 2):
            target[base + i * 4:base + i * 4 + 2] = low[i * 2:i * 2 + 2]
            target[base + i * 4 + 2:base + i * 4 + 4] = high[i * 2:i * 2 + 2]

    pair(image, (rom_dir / "mpr-18648.11").read_bytes(),
         (rom_dir / "mpr-18649.12").read_bytes(), 0x000000)
    pair(image, (rom_dir / "mpr-18650.9").read_bytes(),
         (rom_dir / "mpr-18651.10").read_bytes(), 0x800000)
    return bytes(image)


def is_main_data(value: int) -> bool:
    return MAIN_DATA_BASE <= value < MAIN_DATA_END


def motion_header(mmcp: bytes, md: bytes, header: int):
    """Return (data, frames, parts) if `header` is a valid motion table."""
    if not is_main_data(header):
        return None
    data = struct.unpack_from("<I", md, header - MAIN_DATA_BASE)[0]
    if not is_main_data(data):
        return None
    frames, parts = struct.unpack_from("<HH", md, header + 4 - MAIN_DATA_BASE)
    if not (1 <= frames <= 256 and 1 <= parts <= 256):
        return None
    size = frames * parts * 12
    if not (size <= header - data <= size + 64):
        return None
    return data, frames, parts


def extract_records(md: bytes, data: int, frames: int, parts: int) -> bytes:
    return md[data - MAIN_DATA_BASE:data - MAIN_DATA_BASE + frames * parts * 12]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rom-dir", type=Path, default=_ROM_DIR)
    ap.add_argument("--out-dir", type=Path,
                    default=_HERE.parents[1] / "build" / "motion-tables")
    ap.add_argument("--summary-only", action="store_true")
    args = ap.parse_args()

    mc = load_maincpu(args.rom_dir)
    md = load_main_data(args.rom_dir)
    ptrs = list(struct.unpack_from("<10I", mc, PROFILE_TABLE))
    names = []
    for i in range(10):
        raw = mc[NAME_TABLE + i * NAME_STRIDE:NAME_TABLE + i * NAME_STRIDE + NAME_STRIDE]
        names.append(raw.split(b"\0", 1)[0].decode("ascii", "replace"))

    if not args.summary_only:
        args.out_dir.mkdir(parents=True, exist_ok=True)

    print(f"{'fighter':11s} {'profile':>8s} {'clips':>6s} {'frames':>7s} "
          f"{'15p':>5s} {'8p':>5s} {'bytes':>10s}")
    grand = 0
    for i, (name, base) in enumerate(zip(names, ptrs)):
        higher = [p for p in ptrs + [PROFILE_TABLE] if p > base]
        limit = min(higher) if higher else PROFILE_TABLE
        motions = []
        offset = 0x70
        while offset + 4 <= limit - base:
            header = struct.unpack_from("<I", mc, base + offset)[0]
            found = motion_header(mc, md, header)
            if found:
                data, frames, parts = found
                motions.append({
                    "offset": offset,
                    "header": header,
                    "data": data,
                    "frames": frames,
                    "parts": parts,
                })
            offset += 4
        clip_bytes = sum(m["frames"] * m["parts"] * 12 for m in motions)
        grand += clip_bytes
        n15 = sum(1 for m in motions if m["parts"] == 15)
        n8 = sum(1 for m in motions if m["parts"] == 8)
        print(f"{name:11s} 0x{base:06x} {len(motions):6d} "
              f"{sum(m['frames'] for m in motions):7d} {n15:5d} {n8:5d} "
              f"{clip_bytes:10d}")

        if not args.summary_only:
            for m in motions:
                raw = extract_records(md, m["data"], m["frames"], m["parts"])
                m["records_b64"] = base64.b64encode(raw).decode("ascii")
            payload = {
                "fighter": name,
                "profile_bus": f"0x{base:08x}",
                "clips": motions,
            }
            (args.out_dir / f"{name.lower()}.json").write_text(
                json.dumps(payload, separators=(",", ":")))

    print(f"{'TOTAL':11s} {'':8s} {'':6s} {'':7s} {'':5s} {'':5s} {grand:10d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
