#!/usr/bin/env python3
"""Extract structured per-fighter attribute JSON directly from the Virtual-On ROMs.

No MAME, no traces. This pulls everything we can currently decode offline and
writes one richly-structured JSON per fighter.

Decoded from ROM:
  identity   roster index, name, family prefix, profile pointer,
             fighter id (0x19450) and voice/sound id (0x19480)
  model      polygon parts [tpa, tha, oba] from the main_data model tables,
             plus the six-slot pose markers that interrupt the table
  motion     per-fighter keyframe clips (header/data/frames/parts/bytes,
             optional raw records) scanned from the profile blob at +0x70
  weapons    the 10-entry weapon record table at 0x20b50 (asset pointer,
             names, fields, model designation) matched to the fighter id
  profile    the profile sub-table directory (pointer/count pairs)

Not yet decoded from ROM (kept as structured `pending` blocks):
  stats      per-fighter movement/health tuning
  skeleton   the animation parent tree (the ROM uses a six-bone pose system,
             not a flat parent array; see von/i960/motion-emitter-findings.md)

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

# Roster order == i960 name table order == VonRoster order.
ROSTER = [
    ("TEMJIN", 0x9E), ("VIPER2", 0xA1), ("BELGDOR", 0xA4), ("RAIDEN", 0x9F),
    ("DORKAS", 0xA6), ("FEIYEN", 0xA8), ("APHARMD", 0xA7), ("BAL-BAS-BOW", 0xAD),
    ("JAGUARANDI", None), ("Z-GRADT", None),
]

IDENT_TABLE = 0x19450      # 10 u32 fighter ids, roster order
SOUND_TABLE = 0x19480      # 8 u16 voice/sound ids
WEAPON_TABLE = 0x20B50     # 10 x 0x68 weapon records
WEAPON_STRIDE = 0x68
WEAPON_COUNT = 10
MODEL_REGION_START = 0xBED81C
MODEL_REGION_WORDS = 6000


def is_sep(entry) -> bool:
    return entry[0] == "part" and entry[1] == 0 and entry[2] == 0 and entry[3] == 0xFFFFFFFF


def model_tables(main_data: bytes) -> dict[int, dict]:
    """Return {family_prefix: {"parts": [...], "markers": [...]}}.

    Keeps the longest segment per family and preserves the marker sequence
    (the six-slot pose system) with the index of the part that follows it.
    """
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

    best: dict[int, dict] = {}
    for seg in segments:
        parts = [e[1:] for e in seg if e[0] == "part"]
        if len(parts) < 3:
            continue
        prefix = Counter((p[2] >> 16) & 0xFF for p in parts).most_common(1)[0][0]
        markers = []
        part_index = 0
        for entry in seg:
            if entry[0] == "marker":
                markers.append({"slot": entry[1], "before_part": part_index})
            elif entry[0] == "part":
                part_index += 1
        if prefix not in best or len(parts) > len(best[prefix]["parts"]):
            best[prefix] = {"parts": parts, "markers": markers}
    return best


def printable_strings(blob: bytes) -> list[str]:
    out = []
    for chunk in blob.split(b"\0"):
        text = chunk.decode("ascii", "replace").strip()
        if text and all(32 <= ord(c) < 127 for c in text):
            out.append(text)
    return out


def weapon_records(maincpu: bytes) -> list[dict]:
    records = []
    for index in range(WEAPON_COUNT):
        base = WEAPON_TABLE + index * WEAPON_STRIDE
        blob = maincpu[base:base + WEAPON_STRIDE]
        words = list(struct.unpack_from(f"<{WEAPON_STRIDE // 4}I", blob))
        records.append({
            "index": index,
            "asset": f"0x{words[0]:08x}",
            "names": printable_strings(blob[4:52]),
            "model": printable_strings(blob[88:104])[0] if printable_strings(blob[88:104]) else None,
            "fields": words[13:19],
            "sub_asset": f"0x{words[19]:08x}",
            "extra": words[20:22],
            "fighter_id": f"0x{words[25]:04x}",
        })
    return records


def profile_directory(maincpu: bytes, base: int, ptrs: list) -> list[dict]:
    higher = [p for p in ptrs + [PROFILE_TABLE] if p > base]
    limit = min(higher) if higher else PROFILE_TABLE
    entries = []
    offset = 0
    while offset + 8 <= limit - base:
        pointer, count = struct.unpack_from("<II", maincpu, base + offset)
        if pointer and count:
            entries.append({"offset": offset, "pointer": f"0x{pointer:08x}", "count": count})
        offset += 8
    return entries


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
                    "frames": frames, "parts": parts, "bytes": frames * parts * 12}
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


def parse_roster(maincpu: bytes) -> list[dict]:
    ptrs = list(struct.unpack_from("<10I", maincpu, PROFILE_TABLE))
    out = []
    for index, (name, prefix) in enumerate(ROSTER):
        raw = maincpu[NAME_TABLE + index * NAME_STRIDE:NAME_TABLE + (index + 1) * NAME_STRIDE]
        rom_name = raw.split(b"\0", 1)[0].decode("ascii", "replace")
        out.append({
            "index": index,
            "name": rom_name,
            "family": f"0x{prefix:04x}" if prefix is not None else None,
            "profile": ptrs[index],
            "fighter_id": struct.unpack_from("<I", maincpu, IDENT_TABLE + index * 4)[0],
        })
    return out


def extract(rom_dir: Path, out_dir: Path, trees_dir: Path,
            include_motion_records: bool = False, record_limit: int = 4) -> list[dict]:
    maincpu = load_maincpu(rom_dir)
    main_data = load_main_data(rom_dir)
    ptrs = list(struct.unpack_from("<10I", maincpu, PROFILE_TABLE))
    tables = model_tables(main_data)
    weapons = weapon_records(maincpu)
    weapons_by_id = {w["fighter_id"]: w for w in weapons}
    sounds = [struct.unpack_from("<H", maincpu, SOUND_TABLE + i * 2)[0] for i in range(8)]
    out_dir.mkdir(parents=True, exist_ok=True)

    docs = []
    for entry in parse_roster(maincpu):
        prefix = int(entry["family"], 16) if entry["family"] else None
        table = tables.get(prefix, {"parts": [], "markers": []})
        parts = table["parts"]
        fid = f"0x{entry['fighter_id']:04x}"
        doc = {
            "schema": 2,
            "generator": "extract_fighter.py",
            "source": "ROM (offline)",
            "identity": {
                "index": entry["index"],
                "name": entry["name"],
                "family": entry["family"],
                "profile": f"0x{entry['profile']:08x}",
                "fighter_id": fid,
                "sound_ids": [f"0x{s:04x}" for s in sounds],
            },
            "model": {
                "parts": [{"tpa": f"0x{p[0]:08x}", "tha": f"0x{p[1]:08x}",
                           "oba": f"0x{p[2]:08x}"} for p in parts],
                "pose_markers": table["markers"],
            },
            "motion": {
                "clips": motion_clips(maincpu, main_data, entry["profile"], ptrs,
                                      include_motion_records, record_limit),
            },
            "weapons": weapons_by_id.get(fid),
            "profile": {
                "subtables": profile_directory(maincpu, entry["profile"], ptrs),
            },
            "skeleton": find_tree(trees_dir, entry["name"]),
            "stats": {"pending": True,
                      "note": "per-fighter movement/health tuning not yet ROM-decoded"},
            "skeleton_note": ("ROM uses a six-bone pose system (model markers), "
                              "not a flat parent array; override used when authored"),
        }
        doc["motion"]["clip_count"] = len(doc["motion"]["clips"])
        doc["motion"]["total_frames"] = sum(c["frames"] for c in doc["motion"]["clips"])

        out = out_dir / f"{entry['name']}.json"
        out.write_text(json.dumps(doc, indent=1) + "\n")
        wname = (weapons_by_id.get(fid) or {}).get("names") or []
        print(f"{entry['name']:11s} family={entry['family'] or '-':>6s} "
              f"parts={len(parts):2d} markers={len(table['markers'])} "
              f"clips={doc['motion']['clip_count']:3d} weapon={wname[0] if wname else '-'}")
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
