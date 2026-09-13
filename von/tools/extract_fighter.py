#!/usr/bin/env python3
"""Extract per-fighter attribute JSON directly from the Virtual-On ROMs.

No MAME, no traces: this pulls the roster (names + profile pointers), each
fighter's polygon part list ([tpa, tha, oba]) from the main_data model tables,
and the per-fighter keyframe motion tables out of the i960 program image. One
JSON is written per fighter.

What is ROM-sourced here:
  * name, roster index, family prefix                          (maincpu 0x19390)
  * profile pointer                                            (maincpu 0x19360)
  * model parts: tpa / tha / oba (+ subgroup markers)          (main_data model tables)
  * motion clips: header / data / frames / parts / raw records (profile blobs, +0x70 run)
  * silhouette skeleton override, if authored (von/rigs/*.json)

What is NOT yet decoded from ROM (left null with a note):
  * per-fighter gameplay stats (speed, jump, dash, health, weapon tuning)
  * weapon mounts / effect families (currently trace-derived; see
    von/i960/weapon-family-map.md)
  * the animation skeleton parent tree (currently inferred from captures or
    hand-authored)

Usage:
    python3 von/tools/extract_fighter.py --out-dir von/build/fighters
"""
from __future__ import annotations

import argparse
import base64
import json
import struct
import sys
from collections import Counter
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from decode_model_part_table import load_main_data, decode_records  # noqa: E402
from dump_motion_tables import (load_maincpu, motion_header,  # noqa: E402
                                PROFILE_TABLE, NAME_TABLE, NAME_STRIDE)

# Roster order is the i960 name table order / VonRoster order.
ROSTER = [
    ("TEMJIN", 0x9E), ("VIPER2", 0xA1), ("BELGDOR", 0xA4), ("RAIDEN", 0x9F),
    ("DORKAS", 0xA6), ("FEIYEN", 0xA8), ("APHARMD", 0xA7), ("BAL-BAS-BOW", 0xAD),
    ("JAGUARANDI", None), ("Z-GRADT", None),
]

# main_data model-table region (see decode_model_part_table.py).
MODEL_REGION_START = 0xBED81C
MODEL_REGION_WORDS = 6000


def is_sep(entry) -> bool:
    return entry[0] == "part" and entry[1] == 0 and entry[2] == 0 and entry[3] == 0xFFFFFFFF


def model_tables(main_data: bytes) -> dict[int, list]:
    """Return {family_prefix: [(tpa, tha, oba), ...]} (largest segment each)."""
    words = list(struct.unpack_from(f"<{MODEL_REGION_WORDS}I", main_data, MODEL_REGION_START))
    segments, cur = [], []
    for entry in decode_records(words):
        if is_sep(entry):
            if cur:
                segments.append(cur)
            cur = []
        else:
            cur.append(entry)
    if cur:
        segments.append(cur)

    best: dict[int, list] = {}
    for seg in segments:
        parts = [e[1:] for e in seg if e[0] == "part"]
        if len(parts) < 3:
            continue
        prefix = Counter((p[2] >> 16) & 0xFF for p in parts).most_common(1)[0][0]
        if prefix not in best or len(parts) > len(best[prefix]):
            best[prefix] = parts
    return best


def motion_clips(maincpu: bytes, main_data: bytes, base: int, ptrs: list,
                 include_records: bool, record_limit: int) -> list:
    higher = [p for p in ptrs + [PROFILE_TABLE] if p > base]
    limit = min(higher) if higher else PROFILE_TABLE
    clips = []
    offset = 0x70
    while offset + 4 <= limit - base:
        header = struct.unpack_from("<I", maincpu, base + offset)[0]
        found = motion_header(maincpu, main_data, header)
        if found:
            data, frames, parts = found
            clip = {"offset": offset, "header": header, "data": data,
                    "frames": frames, "parts": parts,
                    "bytes": frames * parts * 12}
            if include_records and len(clips) < record_limit:
                raw = main_data[data - 0x02000000:data - 0x02000000 + frames * parts * 12]
                clip["records_b64"] = base64.b64encode(raw).decode("ascii")
            clips.append(clip)
        offset += 4
    return clips


def find_tree(trees_dir: Path, name: str):
    for candidate in (trees_dir / f"{name}.json",
                      trees_dir / f"{name.title().replace('-', '')}.json"):
        if candidate.is_file():
            return json.loads(candidate.read_text())
    return None


def extract(rom_dir: Path, out_dir: Path, trees_dir: Path,
            include_motion_records: bool = False, record_limit: int = 4) -> list[dict]:
    """Decode every fighter and write one JSON per fighter. Return the docs."""
    maincpu = load_maincpu(rom_dir)
    main_data = load_main_data(rom_dir)
    ptrs = list(struct.unpack_from("<10I", maincpu, PROFILE_TABLE))
    tables = model_tables(main_data)
    out_dir.mkdir(parents=True, exist_ok=True)

    docs = []
    for index, (name, prefix) in enumerate(ROSTER):
        raw = maincpu[NAME_TABLE + index * NAME_STRIDE:NAME_TABLE + (index + 1) * NAME_STRIDE]
        rom_name = raw.split(b"\0", 1)[0].decode("ascii", "replace")
        parts = tables.get(prefix, []) if prefix is not None else []
        doc = {
            "schema": 1,
            "generator": "extract_fighter.py",
            "source": "ROM (offline)",
            "index": index,
            "name": rom_name,
            "family": f"0x{prefix:04x}" if prefix is not None else None,
            "profile": f"0x{ptrs[index]:08x}",
            "parts": [{"tpa": f"0x{p[0]:08x}", "tha": f"0x{p[1]:08x}",
                       "oba": f"0x{p[2]:08x}"} for p in parts],
            "skeleton": find_tree(trees_dir, name),
            "motion": motion_clips(maincpu, main_data, ptrs[index], ptrs,
                                   include_motion_records, record_limit),
            "weapons": None,
            "stats": None,
            "notes": ("weapons/stats/skeleton are not fully ROM-decoded yet; "
                      "skeleton here is a hand-authored override when present"),
        }
        out = out_dir / f"{name}.json"
        out.write_text(json.dumps(doc, indent=1) + "\n")
        clips = len(doc["motion"]) if doc["motion"] else 0
        frames = sum(c["frames"] for c in doc["motion"]) if doc["motion"] else 0
        print(f"{name:11s} family={doc['family'] or '-':>6s} parts={len(parts):2d} "
              f"clips={clips:3d} frames={frames:5d} skeleton={'yes' if doc['skeleton'] else 'no '} "
              f"-> {out.name}")
        docs.append(doc)
    return docs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rom-dir", type=Path, default=_HERE.parent / "artifacts")
    ap.add_argument("--out-dir", type=Path, default=_HERE.parent / "build" / "fighters")
    ap.add_argument("--trees-dir", type=Path, default=_HERE.parent / "rigs")
    ap.add_argument("--include-motion-records", action="store_true",
                    help="embed raw keyframe bytes (base64) for the first clips")
    ap.add_argument("--record-limit", type=int, default=4)
    args = ap.parse_args()

    docs = extract(args.rom_dir, args.out_dir, args.trees_dir,
                   args.include_motion_records, args.record_limit)
    print(f"wrote {len(docs)} fighter files to {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
