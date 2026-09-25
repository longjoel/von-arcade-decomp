#!/usr/bin/env python3
"""Verify the Godot audio manifest builder.

The manifest is a pure transform of the committed command and clip maps, so
this test needs no ROMs. It pins the schema, coverage, category split, loop
flags, and the BGM placeholder entries.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "von/tools/export_audio_manifest.py"
CLIPS = ROOT / "von/audio-clip-map.json"
COMMANDS = ROOT / "von/audio-command-map.json"


def load_tool():
    spec = importlib.util.spec_from_file_location("export_audio_manifest", TOOL)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    clips = json.loads(CLIPS.read_text())["clips"]
    commands = json.loads(COMMANDS.read_text())["commands"]
    tool = load_tool()
    manifest = tool.build_manifest(clips, commands)

    assert manifest["schema"] == "von-godot-audio/1"
    entries = manifest["commands"]
    assert len(entries) == 310, len(entries)

    # One-shot effects resolve to a clip; the 0x10xx BGM family is metadata.
    assert entries["0x1115"]["file"] == "SDE_hit_13.wav"
    assert entries["0x1115"]["category"] == "sfx"
    assert entries["0x134b"]["category"] == "voice"
    assert entries["0x1108"]["loop"] is True
    assert entries["0x1109"]["stops"] == ["0x1107", "0x1108"]
    assert entries["0x1002"]["file"] is None  # unused arena BGM id
    assert entries["0x1002"]["category"] == "bgm"
    # The select-screen BGM is an offline render and loops.
    assert entries["0x100b"]["file"] == "music_select.wav"
    assert entries["0x100b"]["loop"] is True
    assert entries["0x100c"]["file"] == "music_select.wav"
    assert entries["0x101b"]["file"] == "music_attract.wav"
    # All ten arena BGMs are offline renders (selector -> file).
    assert entries["0x1001"]["file"] == "music_arena03.wav"
    assert entries["0x1004"]["file"] == "music_arena09.wav"
    assert entries["0x1006"]["file"] == "music_arena01.wav"
    assert entries["0x1008"]["file"] == "music_arena07.wav"
    assert entries["0x1009"]["file"] == "music_arena02.wav"
    assert entries["0x100a"]["file"] == "music_arena00.wav"
    assert entries["0x1016"]["file"] == "music_arena04.wav"
    assert entries["0x1017"]["file"] == "music_arena05.wav"
    assert entries["0x1018"]["file"] == "music_arena08.wav"
    assert entries["0x1019"]["file"] == "music_arena06.wav"

    # Baked SCSP pitch/gain: jump/rifle play at OCT 15/FNS 0 (0.5x) and -12 dB;
    # the voice family at DISDL 4 (-6 dB).
    assert abs(entries["0x1117"]["pitch"] - 0.5) < 0.001
    assert abs(entries["0x1117"]["gain_db"] + 12.0) < 0.1
    assert abs(entries["0x1200"]["pitch"] - 0.5) < 0.001
    assert abs(entries["0x134b"]["gain_db"] + 6.0) < 0.1
    assert entries["0x1101"]["pitch"] < 0.4  # OCT 14/FNS 0x157

    # The EG attack ramp starts near silence and reaches full level; a full
    # scale impulse at frame 0 must be strongly attenuated.
    shaped = tool._eg_attack([32767, 32767, 32767], 55.0)
    assert shaped[0] < 100 and shaped[0] < shaped[1] <= shaped[2] <= 32767

    for key, entry in entries.items():
        assert entry["category"] in ("sfx", "voice", "bgm"), key
        if entry["category"] in ("sfx", "voice"):
            assert key in clips, key
            assert entry["file"], key
        elif entry["file"] is not None:
            assert key in tool.BGM_FILES, key

    print(f"PASS: {len(entries)} manifest entries, "
          f"{sum(1 for e in entries.values() if e['file'])} clips")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
