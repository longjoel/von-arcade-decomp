#!/usr/bin/env python3
"""Export a Godot-ready sound manifest and clips from the decoded audio maps.

Inputs are the committed `von/audio-clip-map.json` (command -> descriptor ->
sample-region range) and `von/audio-command-map.json` (all commands, including
the `0x10xx` BGM family). Output is a directory containing:

  audio_clips.json   command -> {file, name, loop, gain_db, pitch, category}
  <name>.wav         one PCM16 WAV per one-shot clip (unless --no-wav)

The manifest is consumed by `von-godot/scripts/von_audio.gd`; the kernel emits
the command IDs from ABI v7 and the host plays these clips. No 68000/SCSP
emulation is involved.

The default output stages into the sibling Godot repo's ignored
`assets/generated/audio/` tree; override with -o.
"""

from __future__ import annotations

import argparse
import json
import struct
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CLIPS = ROOT / "von/audio-clip-map.json"
DEFAULT_COMMANDS = ROOT / "von/audio-command-map.json"
DEFAULT_OUT = ROOT.parent / "von-godot/assets/generated/audio"
DEFAULT_SAMPLE_ROMS = [ROOT / "von/artifacts/mpr-18652.32",
                       ROOT / "von/artifacts/mpr-18653.34"]
SAMPLE_BASE = 0x800000
# Loop/stop cues inferred from the recovered names. Dash/beam loops start and
# stop; the stop cue silences the named start cues.
LOOP_NAMES = ("_loop",)
STOP_MAP = {
    "0x1109": ["0x1107", "0x1108"],  # dash_03 stops the dash loops
}
# Offline-rendered BGM tracks (von-godot/scripts/render_scsp_audio.sh): select,
# attract, and all ten arena tracks are bit-exact. BGM IDs not listed stay
# metadata-only.
BGM_FILES = {
    "0x100b": "music_select.wav",   # SDB_select1
    "0x100c": "music_select.wav",   # SDB_select3
    "0x101a": "music_attract.wav",  # SDB_title
    "0x101b": "music_attract.wav",  # SDB_demo
    "0x101d": "music_attract.wav",  # SDB_demo01
    # All ten arena BGMs, indexed by the game's arena selector (0x5770f0 ==
    # word1 of 0x194a0[ord*32]). Rendered per ordinal with
    # von/tools/probe_stage_binding.lua; file/mapping is in von/docs/audio.md.
    "0x100a": "music_arena00.wav",  # selector 0 -> SDB_bgm_10
    "0x1006": "music_arena01.wav",  # selector 1 -> SDB_bgm_06
    "0x1009": "music_arena02.wav",  # selector 2 -> SDB_bgm_09
    "0x1001": "music_arena03.wav",  # selector 3 -> SDB_bgm_01
    "0x1016": "music_arena04.wav",  # selector 4 -> SDB_bgm_11
    "0x1017": "music_arena05.wav",  # selector 5 -> SDB_bgm_12
    "0x1019": "music_arena06.wav",  # selector 6 -> SDB_bgm_14
    "0x1008": "music_arena07.wav",  # selector 7 -> SDB_bgm_08
    "0x1018": "music_arena08.wav",  # selector 8 -> SDB_bgm_13
    "0x1004": "music_arena09.wav",  # selector 9 -> SDB_bgm_04
}


def _swap_words(data: bytes) -> bytes:
    return b"".join(data[i + 1:i + 2] + data[i:i + 1]
                    for i in range(0, len(data), 2))


def _eg_attack(samples: list[int], attack_ms: float,
               rate: int = 44100) -> list[int]:
    """Apply the decoded SCSP EG attack ramp (MAME's m_EG_TABLE curve).

    MAME's EG volume ramps linearly from 0 to 0x3ff over the AR time, with
    amplitude 10^(3*(i-0x3ff)/32/20). All effect tracks use AR=31 (55 ms).
    """
    if attack_ms <= 0.0 or attack_ms >= 1000.0 or not samples:
        return samples
    frames = min(len(samples), int(attack_ms / 1000.0 * rate))
    if frames <= 0:
        return samples
    for n in range(frames):
        i = 0x3FF * (n / frames)
        amplitude = 10.0 ** ((3.0 * (i - 0x3FF) / 32.0) / 20.0)
        samples[n] = int(samples[n] * amplitude)
    return samples


def _wav_bytes(raw: bytes, attack_ms: float = 0.0) -> bytes:
    samples = [(value - 256 if value >= 128 else value) << 8 for value in raw]
    samples = _eg_attack(samples, attack_ms)
    pcm = b"".join(int(value).to_bytes(2, "little", signed=True)
                   for value in samples)
    import io
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(44100)
        out.writeframes(pcm)
    return buffer.getvalue()


def build_manifest(clips: dict, commands: dict) -> dict:
    output: dict[str, dict] = {}
    for key, command in commands.items():
        name = command.get("name")
        if command.get("control", 0) == 0:
            # BGM/sequence family: play an offline render when one exists,
            # otherwise metadata only until the track is rendered.
            bgm_file = BGM_FILES.get(key)
            output[key] = {
                "file": bgm_file,
                "name": name,
                "category": "bgm",
                "loop": bgm_file is not None,
                "gain_db": 0.0,
                "pitch": 1.0,
            }
            continue
        clip = clips.get(key)
        if clip is None:
            continue
        base = name or f"cmd_{int(key, 16):04x}"
        entry = {
            "file": f"{base}.wav",
            "name": name,
            "category": "voice" if key.startswith("0x13") else "sfx",
            "loop": bool(name and any(token in name for token in LOOP_NAMES)),
            # Baked SCSP voice parameters (0x602710 pitch + MAME TL/PAN/DISDL).
            "pitch": round(float(clip.get("pitch_scale", 1.0)), 4),
            "gain_db": round(float(clip.get("gain_db", 0.0)), 2),
            "pan": int(clip.get("dipan", 0)),
            "descriptor": clip["descriptor"],
            "track": clip["track"],
        }
        if key in STOP_MAP:
            entry["stops"] = STOP_MAP[key]
        output[key] = entry
    return {
        "schema": "von-godot-audio/1",
        "source": "von/audio-clip-map.json",
        "commands": output,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clips", type=Path, default=DEFAULT_CLIPS)
    parser.add_argument("--commands", type=Path, default=DEFAULT_COMMANDS)
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sample-roms", nargs=2, type=Path,
                        default=DEFAULT_SAMPLE_ROMS)
    parser.add_argument("--no-wav", action="store_true",
                        help="write only audio_clips.json")
    args = parser.parse_args()

    clips = json.loads(args.clips.read_text())["clips"]
    commands = json.loads(args.commands.read_text())["commands"]
    manifest = build_manifest(clips, commands)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "audio_clips.json").write_text(
        json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {args.output / 'audio_clips.json'} "
          f"({len(manifest['commands'])} commands)")

    if not args.no_wav:
        samples = b"".join(
            _swap_words(path.read_bytes()) for path in args.sample_roms)
        written = 0
        for key, entry in manifest["commands"].items():
            # BGM files are offline renders staged separately, not descriptors.
            if not entry.get("file") or key not in clips:
                continue
            clip = clips[key]
            raw = samples[clip["offset"]:clip["offset"] + clip["length"]]
            if len(raw) < 2:
                continue
            (args.output / entry["file"]).write_bytes(
                _wav_bytes(raw, float(clip.get("attack_ms", 0.0))))
            written += 1
        print(f"wrote {written} clip WAVs to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
