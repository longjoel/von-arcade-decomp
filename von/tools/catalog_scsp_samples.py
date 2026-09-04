#!/usr/bin/env python3
"""Create a ROM-only SCSP sample catalog and individual WAVs.

This deliberately separates extraction from naming.  Headerless SCSP PCM has
no embedded names, so automatic names are ``candidate-XXXX``.  Exact start/end
values can be supplied in a JSON file (the same values used by the SCSP voice
descriptors); those entries are emitted losslessly and marked authoritative.
Without a descriptor file, long silent gaps are only candidate boundaries and
are marked heuristic in the catalog.
"""

from __future__ import annotations

import argparse
import json
import math
import wave
from pathlib import Path


def swap_words(data: bytes) -> bytes:
    if len(data) % 2:
        raise ValueError("SCSP ROM must contain an even number of bytes")
    return b"".join(data[i + 1:i + 2] + data[i:i + 1]
                    for i in range(0, len(data), 2))


def samples(data: bytes) -> list[int]:
    return [int.from_bytes(data[i:i + 2], "little", signed=True)
            for i in range(0, len(data), 2)]


def pcm8_samples(data: bytes) -> list[int]:
    return [value - 256 if value >= 128 else value for value in data]


def pcm8_to_pcm16(data: bytes) -> bytes:
    return b"".join(
        ((value - 256 if value >= 128 else value) << 8).to_bytes(
            2, "little", signed=True
        )
        for value in data
    )


def write_wav(path: Path, pcm: bytes, rate: int) -> None:
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(pcm)


def heuristic_ranges(values: list[int], threshold: int, gap: int,
                     minimum: int, bytes_per_frame: int) -> list[tuple[int, int]]:
    """Find non-silent byte ranges; intentionally returns candidates only."""
    quiet = 0
    start = None
    result = []
    for index, value in enumerate(values):
        if abs(value) <= threshold:
            quiet += 1
        else:
            if start is None:
                start = index - quiet
            quiet = 0
        if start is not None and quiet >= gap:
            end = index - quiet + 1
            if end - start >= minimum:
                result.append((start * bytes_per_frame, end * bytes_per_frame))
            start = None
            quiet = 0
    if start is not None and len(values) - start >= minimum:
        result.append((start * bytes_per_frame, len(values) * bytes_per_frame))
    return result


def descriptor_ranges(path: Path, size: int) -> list[dict]:
    raw = json.loads(path.read_text())
    entries = raw["samples"] if isinstance(raw, dict) else raw
    result = []
    for number, entry in enumerate(entries):
        start = int(entry["start"], 0) if isinstance(entry["start"], str) else int(entry["start"])
        end = int(entry["end"], 0) if isinstance(entry["end"], str) else int(entry["end"])
        if not (0 <= start < end <= size):
            raise ValueError(f"descriptor {number} is outside sample ROM: {start:#x}..{end:#x}")
        result.append({**entry, "start": start, "end": end,
                       "confidence": "authoritative"})
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("roms", nargs=2, type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True,
                        help="directory for catalog.json and per-sample WAVs")
    parser.add_argument("--descriptors", type=Path,
                        help="JSON with samples:[{name,start,end,...}]")
    # 45.1584 MHz SCSP clock / 512 clocks per output sample.
    parser.add_argument("--rate", type=int, default=88200)
    parser.add_argument("--format", choices=("pcm8", "pcm16"), default="pcm8")
    parser.add_argument("--quiet-threshold", type=int, default=16)
    parser.add_argument("--quiet-gap", type=int, default=2205,
                        help="quiet PCM frames needed for heuristic splitting")
    parser.add_argument("--minimum-frames", type=int, default=2205)
    parser.add_argument("--no-word-swap", action="store_true")
    args = parser.parse_args()
    if args.rate <= 0 or args.quiet_threshold < 0 or args.quiet_gap <= 0:
        parser.error("invalid rate/threshold/gap")

    physical = b"".join(path.read_bytes() for path in args.roms)
    logical = physical if args.no_word_swap else swap_words(physical)
    frame_values = pcm8_samples(logical) if args.format == "pcm8" else samples(logical)
    frame_bytes = 1 if args.format == "pcm8" else 2
    entries = descriptor_ranges(args.descriptors, len(logical)) if args.descriptors else [
        {"start": start, "end": end, "confidence": "heuristic"}
        for start, end in heuristic_ranges(frame_values, args.quiet_threshold,
                                            args.quiet_gap, args.minimum_frames,
                                            frame_bytes)
    ]
    args.output.mkdir(parents=True, exist_ok=True)
    catalog = {"format": "scsp-" + args.format, "rate": args.rate,
               "rom_bytes": len(logical), "entries": []}
    for ordinal, entry in enumerate(entries):
        start, end = entry["start"], entry["end"]
        pcm = logical[start:end]
        wav_pcm = pcm8_to_pcm16(pcm) if args.format == "pcm8" else pcm
        stem = entry.get("name", f"candidate-{ordinal:04d}")
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in stem)
        wav = f"{ordinal:04d}-{safe}.wav"
        write_wav(args.output / wav, wav_pcm, args.rate)
        frames = len(pcm) // frame_bytes
        values = pcm8_samples(pcm) if args.format == "pcm8" else samples(pcm)
        rms = math.sqrt(sum(value * value for value in values) / len(values)) if values else 0.0
        catalog["entries"].append({**entry, "name": stem, "start": start, "end": end,
                                   "length_bytes": end - start, "frames": frames,
                                   "duration_seconds": frames / args.rate,
                                   "peak": max((abs(value) for value in values), default=0),
                                   "rms": round(rms, 3), "wav": wav})
    (args.output / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n")
    print(f"wrote {args.output / 'catalog.json'} ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
