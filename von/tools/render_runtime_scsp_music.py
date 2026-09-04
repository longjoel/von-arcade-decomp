#!/usr/bin/env python3
"""Render a provisional track from runtime SCSP key-on descriptors.

This reconstructs note timing, pitch, and first-order SCSP routing from the
register trace. It remains a forensic first pass: DSP routing and the SCSP
envelope generator are approximated, and the output is mono.
"""

from __future__ import annotations

import argparse
import json
import math
import wave
from pathlib import Path


# These are the timing tables used by MAME's SCSP EG implementation. Values
# are milliseconds; the first two entries represent effectively infinite
# times. Keeping them here makes the offline render use the same rate model
# as the reference recording instead of a generic fade.
AR_TIMES = (100000, 100000, 8100, 6900, 6000, 4800, 4000, 3400, 3000, 2400,
            2000, 1700, 1500, 1200, 1000, 860, 760, 600, 500, 430, 380,
            300, 250, 220, 190, 150, 130, 110, 95, 76, 63, 55, 47, 38,
            31, 27, 24, 19, 15, 13, 12, 9.4, 7.9, 6.8, 6.0, 4.7, 3.8,
            3.4, 3.0, 2.4, 2.0, 1.8, 1.6, 1.3, 1.1, .93, .85, .65, .53,
            .44, .40, .35, 0, 0)
DR_TIMES = (100000, 100000, 118200, 101300, 88600, 70900, 59100, 50700,
            44300, 35500, 29600, 25300, 22200, 17700, 14800, 12700, 11100,
            8900, 7400, 6300, 5500, 4400, 3700, 3200, 2800, 2200, 1800,
            1600, 1400, 1100, 920, 790, 690, 550, 460, 390, 340, 270, 230,
            200, 170, 140, 110, 98, 85, 68, 57, 49, 43, 34, 28, 25, 22,
            18, 14, 12, 11, 8.5, 7.1, 6.1, 5.4, 4.3, 3.6, 3.1)


def swap_words(data: bytes) -> bytes:
    return b"".join(data[i + 1:i + 2] + data[i:i + 1]
                    for i in range(0, len(data), 2))


def scsp_ratio(octave: int, fns: int) -> float:
    # Matches the fixed-point Step() calculation in MAME's SCSP device.
    exponent = (octave ^ 8) - 8 + 12 - 10
    fn = fns + 1024
    if exponent >= 0:
        fn <<= exponent
    else:
        fn >>= -exponent
    return fn / float(1 << 12)


def render_pitch(entry: dict, frame: int, rate: int, source_position: float,
                 update_index: int, ratio: float) -> tuple[float, int, float, float]:
    """Advance through the live OCT/FNS writes for one voice."""
    absolute_time = entry["time"] + frame / rate
    updates = entry.get("pitch_updates", [])
    while update_index < len(updates) and updates[update_index]["time"] <= absolute_time:
        update = updates[update_index]
        ratio = scsp_ratio(update["oct"], update["fns"])
        update_index += 1
    return source_position, update_index, ratio, source_position + ratio


def pcm8(data: bytes) -> list[float]:
    return [((value - 256 if value >= 128 else value) / 128.0) for value in data]


def tl_gain(value: int) -> float:
    db = sum(amount for bit, amount in enumerate((-.4, -.8, -1.5, -3.0, -6.0, -12.0, -24.0, -48.0))
             if value & (1 << bit))
    return 10 ** (db / 20.0)


def sdl_gain(value: int) -> float:
    return (0.0, 10 ** (-36 / 20), 10 ** (-30 / 20), 10 ** (-24 / 20),
            10 ** (-18 / 20), 10 ** (-12 / 20), 10 ** (-6 / 20), 1.0)[value & 7]


def pan_gain(value: int) -> float:
    if value & 0x0f == 0x0f:
        return 0.0
    db = sum(amount for bit, amount in enumerate((3.0, 6.0, 12.0, 24.0))
             if value & (1 << bit))
    return 10 ** (-db / 20.0)


def envelope_gain(entry: dict, frame: int, rate: int) -> float:
    """Approximate MAME EG_Update for a newly keyed voice."""
    octave = (entry["oct"] ^ 8) - 8
    base = octave + 2 * entry.get("krs", 0) + ((entry["fns"] >> 9) & 1)
    ar_index = max(0, min(63, base + 2 * entry.get("ar", 0)))
    d1_index = max(0, min(63, base + 2 * entry.get("d1r", 0)))
    d2_index = max(0, min(63, base + 2 * entry.get("d2r", 0)))
    # MAME starts at EG volume 0x17f and advances once per output sample.
    attack_ms = AR_TIMES[ar_index]
    attack = 383.0 / 1023.0 if attack_ms >= 99999 else min(
        1.0, 383.0 / 1023.0 + frame / max(1.0, attack_ms * rate / 1000.0))
    if attack < 1.0:
        return attack if not entry.get("eghold") else 1.0
    # D1R/D2R=0 is the SCSP hold case. For nonzero rates, approximate the
    # linear EG volume update followed by MAME's 3 dB/32-step table.
    d1_ms = DR_TIMES[d1_index]
    d2_ms = DR_TIMES[d2_index]
    d1_frames = 0 if d1_ms >= 99999 else d1_ms * rate / 1000.0
    if d1_frames and frame < d1_frames:
        volume = 1.0 - frame / d1_frames * (1.0 - (1.0 - entry.get("dl", 0) / 31.0))
        return max(0.0, volume)
    if entry.get("d2r", 0) == 0 or d2_ms >= 99999:
        return max(0.0, 1.0 - entry.get("dl", 0) / 31.0 * 0.0)
    decay_frame = frame - d1_frames
    return max(0.0, (1.0 - entry.get("dl", 0) / 31.0) *
               (1.0 - decay_frame / max(1.0, d2_ms * rate / 1000.0)))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    parser.add_argument("sample_roms", nargs=2, type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--rate", type=int, default=44100)
    parser.add_argument("--tail", type=float, default=1.0)
    parser.add_argument("--gain", type=float, default=0.55)
    args = parser.parse_args()
    if args.rate <= 0 or args.tail < 0 or args.gain <= 0:
        parser.error("invalid rate, tail, or gain")

    report = json.loads(args.catalog.read_text())
    entries = [entry for entry in report["entries"] if entry.get("status") == "extracted"]
    if not entries:
        raise ValueError("catalog contains no extracted runtime entries")
    sample = swap_words(b"".join(path.read_bytes() for path in args.sample_roms))
    entries.sort(key=lambda entry: entry["time"])
    start_time = min(entry["time"] for entry in entries)
    end_time = max(entry["time"] for entry in entries) + args.tail
    next_by_slot = {}
    for index, entry in enumerate(entries):
        for later in entries[index + 1:]:
            if later["slot"] == entry["slot"]:
                next_by_slot[id(entry)] = later["time"]
                break
    output = [0.0] * max(1, math.ceil((end_time - start_time) * args.rate))
    rendered = 0
    for entry in entries:
        raw = sample[entry["start"]:entry["end"]]
        if not raw or not entry["pcm8"]:
            continue
        source = pcm8(raw)
        ratio = scsp_ratio(entry["oct"], entry["fns"])
        if ratio <= 0:
            continue
        position = round((entry["time"] - start_time) * args.rate)
        if entry.get("loop"):
            note_end = next_by_slot.get(id(entry), entry["time"] + args.tail)
            frames = max(1, round((note_end - entry["time"]) * args.rate))
        else:
            frames = max(1, round(len(source) / ratio))
        disdl = entry.get("disdl", 0)
        imxl = entry.get("imxl", 0)
        dipan = entry.get("dipan", 0)
        tl = entry["tl"]
        state_updates = entry.get("state_updates", [])
        state_index = 0
        update_index = 0
        source_position = 0.0
        for frame in range(frames):
            destination = position + frame
            if destination >= len(output):
                break
            absolute_time = entry["time"] + frame / args.rate
            while state_index < len(state_updates) and state_updates[state_index]["time"] <= absolute_time:
                update = state_updates[state_index]
                if update["reg"] == 0x0c:
                    tl = update["value"] & 0xff
                elif update["reg"] == 0x14:
                    imxl = update["value"] & 0x07
                elif update["reg"] == 0x16:
                    disdl = (update["value"] >> 13) & 0x07
                    dipan = (update["value"] >> 8) & 0x1f
                state_index += 1
            if disdl == 0 and imxl == 0:
                level = 0.0
            else:
                route_gain = sdl_gain(disdl) if disdl else 0.20
                level = args.gain * tl_gain(tl) * route_gain * pan_gain(dipan)
            source_position, update_index, ratio, next_position = render_pitch(
                entry, frame, args.rate, source_position, update_index, ratio)
            if entry.get("loop"):
                source_position %= len(source)
            elif source_position >= len(source):
                break
            left = min(len(source) - 1, int(source_position))
            right = min(len(source) - 1, left + 1)
            fraction = source_position - left
            value = source[left] * (1 - fraction) + source[right] * fraction
            value *= envelope_gain(entry, frame, args.rate)
            # Small ramps avoid clicks where independent SCSP voices overlap.
            ramp = min(1.0, frame / max(1, args.rate * 0.003),
                       (frames - frame) / max(1, args.rate * 0.008))
            output[destination] += value * level * ramp
            source_position = next_position
        rendered += 1

    pcm = bytearray()
    for value in output:
        value = max(-1.0, min(1.0, value))
        pcm += int(round(value * 32767)).to_bytes(2, "little", signed=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(args.output), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(args.rate)
        wav.writeframes(pcm)
    metadata = {"source_catalog": str(args.catalog), "rate": args.rate,
                "start_time": start_time, "end_time": end_time,
                "duration_seconds": len(output) / args.rate,
                "rendered_events": rendered, "status": "provisional",
                "notes": ["Mono forensic render from runtime key-on timing, live OCT/FNS writes, and routing.",
                          "TL/SDL/pan attenuation and first-order envelope behavior follow MAME.",
                          "DSP-routed voices still use a placeholder mix gain; exact SHARC effects are not rendered."]}
    args.output.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"wrote {args.output} ({len(output)} frames, {rendered} events)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
