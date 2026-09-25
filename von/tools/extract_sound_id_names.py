#!/usr/bin/env python3
"""Extract the i960 sound-ID -> asset-name table.

The i960 program image carries several packed tables whose records are a
16-bit sound command word followed by a NUL-terminated ASCII asset name
(0x22-byte stride in the largest tables). The names are the 68000 sound
driver's stream/asset labels: `SDE_*` for effects/voices and `SDB_*` for
the shell BGM/select/win/lose family.

This exposes the mapping without claiming that a name identifies a specific
SCSP sample; sample identity still needs descriptor validation.

The default source is the assembled original maincpu image
(`von/build/disasm/vonj-maincpu.bin`, built by `./vonctl disasm i960`).
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path


PREFIXES = ("SDE_", "SDB_")


def read_records(data: bytes) -> list[dict]:
    records = []
    seen = set()
    for offset in range(0, len(data) - 4, 2):
        command = struct.unpack_from("<H", data, offset)[0]
        if not 0x1000 <= command <= 0x13FF:
            continue
        start = offset + 2
        end = start
        while end < offset + 2 + 0x1E and 32 <= data[end] < 127:
            end += 1
        if end - start < 4 or end >= len(data) or data[end] != 0:
            continue
        raw = data[start:end]
        name = raw.decode("ascii", "strict")
        if not name.startswith(PREFIXES):
            continue
        if not all(ch.isalnum() or ch == "_" for ch in name):
            continue
        if offset in seen:
            continue
        seen.add(offset)
        records.append({"offset": offset, "command": command, "name": name})
    records.sort(key=lambda record: (record["command"], record["offset"]))
    return records


STAGE_TABLE = 0x195E0
STAGE_STRIDE = 8
STAGE_COUNT = 10
ROUND_TABLE = 0x19480
ROUND_COUNT = 10


def stage_intro(data: bytes, names: dict[str, str]) -> dict:
    records = []
    for selector in range(STAGE_COUNT):
        offset = STAGE_TABLE + selector * STAGE_STRIDE
        bgm = struct.unpack_from("<H", data, offset)[0]
        announce = struct.unpack_from("<H", data, offset + 4)[0]
        records.append({
            "selector": selector,
            "bgm": bgm,
            "bgm_name": names.get(f"0x{bgm:04x}"),
            "announce": announce,
            "announce_name": names.get(f"0x{announce:04x}"),
        })
    rounds = []
    for index in range(ROUND_COUNT):
        command = struct.unpack_from("<H", data,
                                     ROUND_TABLE + index * 2)[0]
        rounds.append({
            "index": index,
            "command": command,
            "name": names.get(f"0x{command:04x}"),
        })
    return {
        "selector_table": STAGE_TABLE,
        "selector_stride": STAGE_STRIDE,
        "records": records,
        "round_table": ROUND_TABLE,
        "rounds": rounds,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    default_image = Path(__file__).resolve().parents[2] / (
        "von/build/disasm/vonj-maincpu.bin")
    parser.add_argument("image", nargs="?", type=Path, default=default_image,
                        help="assembled i960 maincpu image")
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()
    if not args.image.is_file():
        parser.error(f"missing image: {args.image} (run ./vonctl disasm i960)")
    data = args.image.read_bytes()
    records = read_records(data)
    names: dict[str, str] = {}
    duplicates: list[dict] = []
    for record in records:
        key = f"0x{record['command']:04x}"
        if key in names:
            duplicates.append({"command": record["command"],
                               "first": names[key],
                               "later": record["name"],
                               "offset": record["offset"]})
            continue
        names[key] = record["name"]
    report = {
        "schema": "von-sound-id-names/2",
        "source": str(args.image),
        "image_bytes": len(data),
        "record_count": len(records),
        "unique_command_count": len(names),
        "names": names,
        "records": records,
        "duplicates": duplicates,
        "stage_intro": stage_intro(data, names),
    }
    encoded = json.dumps(report, indent=2, sort_keys=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
        print(f"wrote {args.output} "
              f"({report['record_count']} records, "
              f"{report['unique_command_count']} commands)")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
