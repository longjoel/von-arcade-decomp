#!/usr/bin/env python3
"""Verify the committed 68000 sound command map.

`von/audio-command-map.json` is produced by
`von/tools/extract_audio_command_map.py` from the disassembled sound image.
It resolves every i960 command ID (`0x10xx`-`0x13xx`) through the 68000's
two-level table at `[0x60801c]` to either a sample packet (`0x9a/0x9b/0x9c,
index, param`) or a BGM sequence record. This test pins the schema and a set
of anchors and re-derives the whole map when the image is present.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAPPING = ROOT / "von/audio-command-map.json"
EXTRACTOR = ROOT / "von/tools/extract_audio_command_map.py"
NAMES = ROOT / "von/sound-id-names.json"
IMAGE = ROOT / "von/build/disasm/vonj-audio.bin"

# command -> (name, control, opcode/sample/param or sequence pointer)
ANCHORS = {
    0x1001: ("SDB_bgm_01", 0x00, 0x0080A000),
    0x1008: ("SDB_bgm_08", 0x00, 0x0080A000),
    0x1101: ("SDE_bom_01", 0x80, (0x9A, 0x01, 0x7A)),
    0x1115: ("SDE_hit_13", 0x80, (0x9A, 0x15, 0x7A)),
    0x1200: ("SDE_tem_rifle", 0x80, (0x9B, 0x27, 0x7A)),
    0x1227: ("SDE_new_hit4", 0x80, (0x9B, 0x4E, 0x7A)),
    0x134B: ("SDE_new_voice5", 0x80, (0x9C, 0x42, 0x7F)),
    0x1350: ("SDE_new_voice10", 0x80, (0x9C, 0x47, 0x7F)),
    0x1363: ("SDE_click_0", 0x80, (0x9A, 0x5B, 0x73)),
}


def load_extractor():
    spec = importlib.util.spec_from_file_location(
        "extract_audio_command_map", EXTRACTOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    report = json.loads(MAPPING.read_text())
    assert report["schema"] == "von-audio-command-map/1"
    assert report["pointer"] == 0x0060CA1A
    assert report["command_table"] == 0x0060801C
    levels = {entry["hh"]: entry["max_ll"]
              for entry in report["first_level"]}
    assert levels == {0x10: 34, 0x11: 91, 0x12: 79, 0x13: 102}
    commands = report["commands"]
    assert report["command_count"] == len(commands) == 310

    named = json.loads(NAMES.read_text())["names"]
    for key, (name, control, value) in ANCHORS.items():
        record = commands[f"0x{key:04x}"]
        assert record["name"] == name, (hex(key), record["name"])
        assert record["control"] == control, (hex(key), record["control"])
        if control == 0x00:
            assert record["sequence_pointer"] == value, hex(key)
        else:
            assert (record["opcode"], record["sample"],
                    record["param"]) == value, hex(key)

    # Every named i960 command must resolve, and the two control families
    # must be exactly the BGM (`0x10xx`) and one-shot (`0x11xx`+) sets.
    for key in named:
        command = int(key, 16)
        assert key in commands, key
        control = commands[key]["control"]
        if command >> 8 == 0x10:
            assert control == 0x00, key
        else:
            assert control == 0x80, key

    if IMAGE.is_file():
        extractor = load_extractor()
        derived = extractor.build_map(IMAGE.read_bytes(), named)
        assert derived == report, "committed map differs from the ROM"

    print(f"PASS: {len(commands)} sound commands, {len(ANCHORS)} anchors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
