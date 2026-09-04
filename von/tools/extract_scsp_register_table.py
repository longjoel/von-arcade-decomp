#!/usr/bin/env python3
"""Extract samples described by the sound ROM's SCSP register table."""

from __future__ import annotations

import argparse
import json
import wave
from pathlib import Path


def swap_words(data: bytes) -> bytes:
    return b"".join(data[i + 1:i + 2] + data[i:i + 1]
                    for i in range(0, len(data), 2))


def u16(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset:offset + 2], "big")


def pcm8_to_pcm16(data: bytes) -> bytes:
    out = bytearray()
    for value in data:
        signed = value - 256 if value >= 128 else value
        out += int(signed << 8).to_bytes(2, "little", signed=True)
    return bytes(out)


def write_wav(path: Path, pcm: bytes, rate: int) -> None:
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(pcm)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sound_rom", type=Path, help="epr-18670.31")
    parser.add_argument("sample_roms", nargs=2, type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--table-offset", type=lambda value: int(value, 0), default=0x1100)
    parser.add_argument("--rate", type=int, default=44100)
    parser.add_argument("--render-seconds", type=float, default=1.0,
                        help="minimum WAV duration; use 0 for exact clips")
    parser.add_argument("--repeat", action="store_true",
                        help="repeat the source clip to fill render-seconds")
    parser.add_argument("--format", choices=("auto", "pcm8", "pcm16"),
                        default="auto", help="override the SCSP format for auditioning")
    args = parser.parse_args()
    if args.rate <= 0 or args.render_seconds < 0:
        parser.error("invalid rate or render duration")

    sound = swap_words(args.sound_rom.read_bytes())
    samples = swap_words(b"".join(path.read_bytes() for path in args.sample_roms))
    args.output.mkdir(parents=True, exist_ok=True)
    entries = []
    for index, offset in enumerate(range(args.table_offset, len(sound), 16)):
        if offset + 16 > len(sound):
            break
        words = [u16(sound, offset + i * 2) for i in range(8)]
        if words[0] == 0xffff:
            break
        sa = ((words[0] & 0x000f) << 16) | words[1]
        lsa, lea = words[2], words[3]
        pcm8 = bool(words[0] & 0x0010)
        if args.format != "auto":
            pcm8 = args.format == "pcm8"
        # SCSP compares the byte address against LEA for both formats.  For
        # PCM16 the address advances by two bytes per sample, so LEA/2 is the
        # resulting frame count; LEA is not a sample count.
        end = sa + lea
        if end > len(samples) or end <= sa:
            continue
        raw = samples[sa:end]
        if not pcm8:
            # Logical SCSP PCM16 is big-endian; WAV PCM16 is little-endian.
            pcm = b"".join(raw[i + 1:i + 2] + raw[i:i + 1]
                            for i in range(0, len(raw), 2))
        else:
            pcm = pcm8_to_pcm16(raw)
        wav = f"{index:04d}-scsp-sa-{sa:06x}.wav"
        source_frames = len(pcm) // 2
        render_frames = max(source_frames, round(args.render_seconds * args.rate))
        if args.repeat and source_frames:
            rendered = (pcm * ((render_frames + source_frames - 1) // source_frames))[:render_frames * 2]
        else:
            rendered = pcm + b"\0" * ((render_frames - source_frames) * 2)
        write_wav(args.output / wav, rendered, args.rate)
        entries.append({"index": index, "register_offset": offset,
                        "sa": sa, "lsa": lsa, "lea": lea,
                        "pcm8": pcm8, "start": sa, "end": end,
                        "length_bytes": end - sa, "source_frames": source_frames,
                        "wav_frames": render_frames,
                        "duration_seconds": render_frames / args.rate,
                        "wav": wav})
    report = {"format": "scsp-register-table", "rate": args.rate,
              "sample_rom_bytes": len(samples), "entries": entries}
    (args.output / "catalog.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {args.output / 'catalog.json'} ({len(entries)} tracks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
