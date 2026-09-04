#!/usr/bin/env python3
"""Turn Virtual-On's SCSP sample ROMs into playable PCM WAV files.

The Model 2 SCSP sample region is a pair of 16-bit ROMs loaded as one logical
8 MiB region.  MAME's ROM_LOAD16_WORD_SWAP makes the byte order explicit; this
tool applies that same per-word swap.  The ROM bus width does not determine the
voice format: SCSP voices can be PCM8 or PCM16, selected by the sound program.
The result is a forensic raw-region render, not a claim that the whole ROM is
one continuous sample.  The sound program's SCSP start/end registers determine
the individual clips during playback.
"""

from __future__ import annotations

import argparse
import wave
from pathlib import Path


def word_swap(data: bytes) -> bytes:
    if len(data) & 1:
        raise ValueError("sample ROM size must be even")
    out = bytearray(len(data))
    for offset in range(0, len(data), 2):
        out[offset] = data[offset + 1]
        out[offset + 1] = data[offset]
    return bytes(out)


def pcm8_to_pcm16(data: bytes) -> bytes:
    """Expand signed SCSP PCM8 samples to signed little-endian PCM16."""
    return b"".join(
        ((value - 256 if value >= 128 else value) << 8).to_bytes(
            2, "little", signed=True
        )
        for value in data
    )


def write_wav(path: Path, data: bytes, rate: int) -> None:
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("roms", nargs=2, type=Path,
                        help="mpr-18652.32 and mpr-18653.34, in load order")
    parser.add_argument("-o", "--output", type=Path, required=True,
                        help="output WAV path")
    # Model 2 SCSP clock is 45.1584 MHz; the chip emits one sample every 512
    # clocks, i.e. 88.2 kHz.  44.1 kHz makes the raw ROM render play 2x fast.
    parser.add_argument("--rate", type=int, default=88200)
    parser.add_argument("--format", choices=("pcm8", "pcm16"), default="pcm16",
                        help="SCSP voice format; ROM bus width does not decide this")
    parser.add_argument("--no-word-swap", action="store_true",
                        help="render physical ROM byte order for comparison")
    args = parser.parse_args()
    if args.rate <= 0:
        parser.error("--rate must be positive")

    data = b"".join(path.read_bytes() for path in args.roms)
    if not args.no_word_swap:
        data = word_swap(data)
    if args.format == "pcm8":
        data = pcm8_to_pcm16(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_wav(args.output, data, args.rate)
    duration = len(data) / (2 * args.rate)
    print(f"wrote {args.output} ({len(data):,} bytes, {duration:.2f}s mono PCM)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
