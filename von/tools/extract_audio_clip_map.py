#!/usr/bin/env python3
"""Join the 68000 command table to concrete sample clips.

The i960 sends `ae HH LL`; the 68000 command table resolves it to an inline
sample packet `OP SAMPLE PARAM`. The four-bit low nibble of `OP` selects a
record in the effect-channel table at `0x608081` (six 16-byte records), whose
`+1` field is the nibble and whose `+2` field is a track index into the
relocated sequence table at `0x60b5e0`/RAM `0x9000`. Each track record holds a
`[lo, hi]` sample range and 12-byte entries; `entry[0]` is the descriptor
index used by the lazy sample loader.

This tool walks that chain for every one-shot command in
`von/audio-command-map.json`, joins the descriptor to a sample-region byte
range from `von/audio-sample-descriptors.json`, and writes
`von/audio-clip-map.json`.

With `--extract DIR` it also writes a PCM8 WAV per resolved command, named
`<command>-<name>-<descriptor>.wav`, for auditioning.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "von/build/disasm/vonj-audio.bin"
DEFAULT_COMMANDS = ROOT / "von/audio-command-map.json"
DEFAULT_DESCRIPTORS = ROOT / "von/audio-sample-descriptors.json"
DEFAULT_OUTPUT = ROOT / "von/audio-clip-map.json"

CHANNEL_TABLE = 0x608081
CHANNEL_RECORDS = 6
CHANNEL_SIZE = 16
SEQUENCE_TABLE = 0x60B5E0
SAMPLE_BASE = 0x800000
PROGRAM_BASE = 0x600000
FNS_TABLE = 0x605CA4  # FNS table indexed by the note/entry field
# MAME's direct-send-level table (DISDL 0..7), in dB.
SDLT = (0.0, -36.0, -30.0, -24.0, -18.0, -12.0, -6.0, 0.0)
# MAME EG envelope times (ms), indexed by AR/RR (0 = effectively infinite).
AR_TIMES = (100000.0, 100000.0, 8100.0, 6900.0, 6000.0, 4800.0, 4000.0,
            3400.0, 3000.0, 2400.0, 2000.0, 1700.0, 1500.0, 1200.0, 1000.0,
            860.0, 760.0, 600.0, 500.0, 430.0, 380.0, 300.0, 250.0, 220.0,
            190.0, 150.0, 130.0, 110.0, 95.0, 76.0, 63.0, 55.0, 47.0, 38.0,
            31.0, 27.0, 24.0, 19.0, 15.0, 13.0, 12.0, 9.4, 7.9, 6.8, 6.0,
            4.7, 3.8, 3.4, 3.0, 2.4, 2.0, 1.8, 1.6, 1.3, 1.1, 0.93,
            0.85, 0.65, 0.53, 0.44, 0.40, 0.35, 0.0, 0.0)


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from(">H", data, offset)[0]


def channel_tracks(data: bytes) -> dict[int, int]:
    mapping = {}
    for index in range(CHANNEL_RECORDS):
        record = CHANNEL_TABLE - PROGRAM_BASE + index * CHANNEL_SIZE
        mapping[data[record + 1]] = data[record + 2]
    return mapping


def fns_table(image: bytes) -> list[int]:
    base = FNS_TABLE - PROGRAM_BASE
    return [u16(image, base + i * 2) for i in range(0x200)]


def scsp_pitch_register(field: int, fns: list[int]) -> int:
    """Port of the 0x602710 pitch routine from the track entry's +2 field."""
    d6 = (field >> 8) & 0xFF
    d5 = field & 0xFF
    if (d6 & 0xF) == 0 and (d5 & 0x80):
        d6 = (d6 + 0xFC) & 0xFF
    d6 = (d6 << 7) & 0xFFFF
    d2 = (((d6 >> 3) & 0xF0) + d5) & 0xFF
    d2 = (d2 << 1) & 0xFFFF
    return ((d6 & 0x7800) | fns[d2 // 2]) & 0xFFFF


def scsp_pitch_scale(pitch: int) -> tuple[int, int, float]:
    """OCT/FNS -> playback rate relative to the SCSP 44.1 kHz output."""
    octave = (pitch >> 11) & 0xF
    fns = pitch & 0x3FF
    exponent = (octave ^ 8) - 6  # (OCT^8)-8 + SHIFT-10, SHIFT=12
    fn = fns + (1 << 10)
    fn = fn << exponent if exponent >= 0 else fn >> -exponent
    return octave, fns, fn / 4096.0


def scsp_gain_db(disdl: int) -> float:
    """MAME pan-table level: 4 * TL(0 dB) * fSDL(DISDL)."""
    import math
    if disdl == 0:
        return -120.0
    return 20.0 * math.log10(4.0 * 10.0 ** (SDLT[disdl] / 20.0))


def track_ranges(data: bytes, track: int, fns: list[int]) -> dict[int, dict]:
    base = SEQUENCE_TABLE - PROGRAM_BASE + u16(
        data, SEQUENCE_TABLE - PROGRAM_BASE + 2 + track * 2)
    low = data[base + 2]
    high = data[base + 3]
    entries = {}
    for i in range(high - low + 1):
        entry = base + 4 + i * 12
        field = u16(data, entry + 2)
        pitch = scsp_pitch_register(field, fns)
        octave, fns_bits, scale = scsp_pitch_scale(pitch)
        disdl = (data[entry + 4] >> 5) & 0x7
        eg = struct.unpack_from(">I", data, entry + 8)[0]
        data4 = (eg >> 16) & 0xFFFF
        data5 = eg & 0xFFFF
        ar = data4 & 0x1F
        entries[low + i] = {
            "descriptor": u16(data, entry),
            "field": field,
            "pitch": pitch,
            "octave": octave,
            "fns": fns_bits,
            "pitch_scale": scale,
            "disdl": disdl,
            "dipan": data[entry + 4] & 0x1F,
            "gain_db": scsp_gain_db(disdl),
            # EG registers (data[4]=AR/EGHOLD/D1R/D2R, data[5]=KRS/DL/RR).
            "ar": ar,
            "d1r": (data4 >> 6) & 0x1F,
            "d2r": (data4 >> 11) & 0x1F,
            "eg_hold": (data4 >> 5) & 0x1,
            "dl": (data5 >> 5) & 0x1F,
            "rr": data5 & 0x1F,
            "attack_ms": AR_TIMES[ar],
        }
    return entries


def build_clip_map(image: bytes, commands: dict, descriptors: dict) -> dict:
    nibble_track = channel_tracks(image)
    fns = fns_table(image)
    ranges = {nibble: track_ranges(image, track, fns)
              for nibble, track in nibble_track.items()}
    clips = {}
    unresolved = []
    for key, command in commands.items():
        if not command.get("control", 0) & 0x80:
            continue
        if "sample" not in command:
            continue
        nibble = command["opcode"] & 0x0F
        range_entry = ranges.get(nibble, {}).get(command["sample"])
        descriptor = range_entry["descriptor"] if range_entry else None
        record = descriptors.get(descriptor)
        name = command.get("name")
        if descriptor in (None, 0xFFFF) or record is None:
            unresolved.append({"command": key, "name": name,
                               "opcode": command["opcode"],
                               "sample": command["sample"]})
            continue
        entry = {
            "name": name,
            "opcode": command["opcode"],
            "sample": command["sample"],
            "nibble": nibble,
            "track": nibble_track[nibble],
            "descriptor": descriptor,
            "region": record["region"],
            "offset": record["offset"],
            "length": record["copy_length"],
            "loop_length": record["loop_length"],
            "field": range_entry["field"],
            "pitch_scale": range_entry["pitch_scale"],
            "octave": range_entry["octave"],
            "fns": range_entry["fns"],
            "gain_db": range_entry["gain_db"],
            "disdl": range_entry["disdl"],
            "dipan": range_entry["dipan"],
            "ar": range_entry["ar"],
            "d1r": range_entry["d1r"],
            "d2r": range_entry["d2r"],
            "dl": range_entry["dl"],
            "rr": range_entry["rr"],
            "attack_ms": range_entry["attack_ms"],
        }
        clips[key] = entry
    return {
        "schema": "von-audio-clip-map/2",
        "channel_table": CHANNEL_TABLE,
        "sequence_table": SEQUENCE_TABLE,
        "fns_table": FNS_TABLE,
        "nibble_track": {f"0x{k:02x}": v for k, v in nibble_track.items()},
        "clip_count": len(clips),
        "unresolved": unresolved,
        "clips": clips,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--commands", type=Path, default=DEFAULT_COMMANDS)
    parser.add_argument("--descriptors", type=Path, default=DEFAULT_DESCRIPTORS)
    parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--extract", type=Path, metavar="DIR")
    parser.add_argument("--sample-roms", nargs=2, type=Path,
                        default=[ROOT / "von/artifacts/mpr-18652.32",
                                 ROOT / "von/artifacts/mpr-18653.34"])
    args = parser.parse_args()
    if not args.image.is_file():
        parser.error(f"missing image: {args.image} (run ./vonctl disasm audio)")

    commands = json.loads(args.commands.read_text())["commands"]
    descriptor_records = json.loads(args.descriptors.read_text())["descriptors"]
    descriptors = {record["index"]: record for record in descriptor_records}
    report = build_clip_map(args.image.read_bytes(), commands, descriptors)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {args.output} ({report['clip_count']} clips, "
          f"{len(report['unresolved'])} unresolved)")

    if args.extract:
        import wave
        samples = b"".join(
            _swap_words(path.read_bytes()) for path in args.sample_roms)
        args.extract.mkdir(parents=True, exist_ok=True)
        written = 0
        for key, clip in report["clips"].items():
            if clip["region"] != "samples":
                continue
            raw = samples[clip["offset"]:clip["offset"] + clip["length"]]
            if len(raw) < 2:
                continue
            pcm = b"".join(
                int((value - 256 if value >= 128 else value) << 8)
                .to_bytes(2, "little", signed=True) for value in raw)
            name = clip["name"] or "unnamed"
            out = args.extract / f"{key}-{name}-{clip['descriptor']:04x}.wav"
            with wave.open(str(out), "wb") as handle:
                handle.setnchannels(1)
                handle.setsampwidth(2)
                handle.setframerate(44100)
                handle.writeframes(pcm)
            written += 1
        print(f"wrote {written} clip WAVs to {args.extract}")
    return 0


def _swap_words(data: bytes) -> bytes:
    return b"".join(data[i + 1:i + 2] + data[i:i + 1]
                    for i in range(0, len(data), 2))


if __name__ == "__main__":
    raise SystemExit(main())
