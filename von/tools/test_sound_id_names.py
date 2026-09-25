#!/usr/bin/env python3
"""Verify the committed sound-ID -> asset-name map.

`von/sound-id-names.json` is produced by
`von/tools/extract_sound_id_names.py` from the assembled i960 image. This
test pins the schema, the naming families, and a set of anchors whose
meaning is cross-checked against the action bindings in
`von/i960/recovered_audio_actions.c` and the runtime-observed queue. When
the assembled image is present it re-derives every record and requires an
exact match, so the committed map cannot drift from the ROM.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAPPING = ROOT / "von/sound-id-names.json"
EXTRACTOR = ROOT / "von/tools/extract_sound_id_names.py"
IMAGE = ROOT / "von/build/disasm/vonj-maincpu.bin"

# Anchors that connect the map to the recovered action bindings and the
# runtime stage script. Each is a confirmed static or trace reading.
ANCHORS = {
    0x1101: "SDE_bom_01",
    0x1108: "SDE_dash_01_loop",   # profile move-enter field
    0x1115: "SDE_hit_13",         # 25-site hit/reaction voice
    0x1117: "SDE_jump_01",        # profile jump field (SDE bank)
    0x1118: "SDE_jump_02",
    0x1119: "SDE_jump_03",
    0x1111: "SDE_type_05",        # play-setup command 0x190d8
    0x114c: "SDE_charging_weapon1",
    0x1200: "SDE_tem_rifle",      # profile weapon field (SDE bank)
    0x1228: "SDE_2_tem_rifle",    # profile weapon field (SDE_2 bank)
    0x133f: "SDE_new_noise2",     # stage-intro noise at script offset -110
    0x1341: "SDE_frame_01",
    0x134b: "SDE_new_voice5",     # observed per-stage "AE 13 4b"
    0x1350: "SDE_new_voice10",    # observed stage-1 FIGHT call
    0x1366: "SDE_click_3",
    0x1008: "SDB_bgm_08",         # stage-1 BGM in the 0x195e0 pair table
}


def load_extractor():
    spec = importlib.util.spec_from_file_location("extract_sound_id_names",
                                                  EXTRACTOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    report = json.loads(MAPPING.read_text())
    assert report["schema"] == "von-sound-id-names/2"
    names = {int(key, 16): value for key, value in report["names"].items()}
    assert report["unique_command_count"] == len(names)

    # Stage intro pairs (BGM, announce voice) and round announcements. The
    # observed arcade route uses selectors 7, 0, 2, 3, 4 for stages 1-5,
    # which is why the raw script IDs are not in stage order.
    intro = {record["selector"]: record
             for record in report["stage_intro"]["records"]}
    assert len(intro) == 10
    assert intro[7]["bgm_name"] == "SDB_bgm_08"
    assert intro[7]["announce_name"] == "SDE_new_voice10"
    assert intro[0]["bgm_name"] == "SDB_bgm_10"
    assert intro[0]["announce_name"] == "SDE_new_voice11"
    for record in intro.values():
        assert record["bgm_name"].startswith("SDB_bgm_")
        assert record["announce_name"].startswith("SDE_new_voice")
    for index, round_ in enumerate(report["stage_intro"]["rounds"]):
        assert round_["index"] == index
        assert round_["name"] == f"SDE_round_{index + 1:02d}"

    for command, value in ANCHORS.items():
        assert names.get(command) == value, (
            f"{command:#06x}: {names.get(command)!r} != {value!r}")
    for key, value in names.items():
        assert 0x1000 <= key <= 0x13FF, hex(key)
        assert value.startswith(("SDE_", "SDB_")), value

    # Structural coverage: the action bindings and stage tables must be
    # fully named.
    for command in (0x1108, 0x112c, 0x1117, 0x113b, 0x1200, 0x1228,
                    0x1001, 0x1019, 0x134b, 0x1359):
        assert command in names, hex(command)

    if IMAGE.is_file():
        extractor = load_extractor()
        derived = extractor.read_records(IMAGE.read_bytes())
        derived_names = {}
        for record in derived:
            derived_names.setdefault(record["command"], record["name"])
        assert derived_names == names, "committed map differs from the ROM"
        assert len(derived) == report["record_count"]
        assert extractor.stage_intro(IMAGE.read_bytes(), report["names"]) \
            == report["stage_intro"], "stage tables differ from the ROM"

    print(f"PASS: {len(names)} sound-ID names across "
          f"{len(ANCHORS)} anchors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
