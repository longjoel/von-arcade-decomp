#!/usr/bin/env python3
"""Verify the committed 68000 command -> sample-clip map.

`von/audio-clip-map.json` is produced by
`von/tools/extract_audio_clip_map.py` from the assembled sound image plus the
command and descriptor maps. It closes the chain
`i960 command ID -> 68000 packet -> effect track -> descriptor -> PCM clip`.
This test pins the channel/track assignment, a set of anchors, and full
coverage, and re-derives the map when the image is present.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAPPING = ROOT / "von/audio-clip-map.json"
EXTRACTOR = ROOT / "von/tools/extract_audio_clip_map.py"
COMMANDS = ROOT / "von/audio-command-map.json"
DESCRIPTORS = ROOT / "von/audio-sample-descriptors.json"
IMAGE = ROOT / "von/build/disasm/vonj-audio.bin"

# command -> (name, nibble, track, descriptor, offset, length)
ANCHORS = {
    0x1101: ("SDE_bom_01", 0x0A, 0x39, 0x00A1, 0x4007DC, 25461),
    0x1115: ("SDE_hit_13", 0x0A, 0x39, 0x00B5, 0x468B84, 37381),
    0x1200: ("SDE_tem_rifle", 0x0B, 0x3A, 0x00C2, 0x4CEBB6, 12299),
    0x134B: ("SDE_new_voice5", 0x0C, 0x3B, 0x0142, 0x759E64, 16385),
    0x1350: ("SDE_new_voice10", 0x0C, 0x3B, 0x0147, 0x76F0A2, 26213),
    0x1363: ("SDE_click_0", 0x0A, 0x39, 0x00EB, 0x5FEE7E, 1101),
}

NIBBLE_TRACK = {"0x0a": 0x39, "0x0b": 0x3a, "0x0c": 0x3b,
                "0x0d": 0x3b, "0x0e": 0x3b, "0x0f": 0x3b}


def load_extractor():
    spec = importlib.util.spec_from_file_location(
        "extract_audio_clip_map", EXTRACTOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    report = json.loads(MAPPING.read_text())
    assert report["schema"] == "von-audio-clip-map/2"
    assert report["channel_table"] == 0x00608081
    assert report["sequence_table"] == 0x0060B5E0
    assert report["nibble_track"] == NIBBLE_TRACK, report["nibble_track"]
    assert report["unresolved"] == []
    assert report["clip_count"] == len(report["clips"]) == 275

    for key, (name, nibble, track, descriptor, offset, length) in ANCHORS.items():
        clip = report["clips"][f"0x{key:04x}"]
        assert clip["name"] == name, (hex(key), clip["name"])
        assert clip["nibble"] == nibble and clip["track"] == track
        assert clip["descriptor"] == descriptor, hex(key)
        assert clip["offset"] == offset and clip["length"] == length, hex(key)
        assert clip["region"] == "samples"
        assert clip["pitch_scale"] > 0.0 and clip["gain_db"] <= 0.0, hex(key)
        assert clip["ar"] == 31 and clip["attack_ms"] == 55.0, hex(key)

    for key, clip in report["clips"].items():
        assert clip["region"] in ("samples", "program"), key
        assert clip["length"] > 0, key
        assert clip["track"] in (0x39, 0x3A, 0x3B), key

    if IMAGE.is_file():
        extractor = load_extractor()
        commands = json.loads(COMMANDS.read_text())["commands"]
        records = json.loads(DESCRIPTORS.read_text())["descriptors"]
        descriptors = {record["index"]: record for record in records}
        assert extractor.build_clip_map(
            IMAGE.read_bytes(), commands, descriptors) == report, \
            "committed clip map differs from the ROM"

    print(f"PASS: {len(report['clips'])} command clips, "
          f"{len(ANCHORS)} anchors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
