#!/usr/bin/env python3
"""Compare a reconstructed mono WAV against a MAME recording."""

from __future__ import annotations

import argparse
import json
import math
import wave
from array import array
from pathlib import Path


def load(path: Path) -> tuple[list[float], int]:
    with wave.open(str(path), "rb") as wav:
        if wav.getsampwidth() != 2:
            raise ValueError("only 16-bit WAVs are supported")
        raw = array("h", wav.readframes(wav.getnframes()))
        if wav.getnchannels() > 1:
            values = [sum(raw[i:i + wav.getnchannels()]) / wav.getnchannels()
                      for i in range(0, len(raw), wav.getnchannels())]
        else:
            values = list(raw)
        return values, wav.getframerate()


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / max(1, len(values)))


def correlation(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    n = min(len(left), len(right))
    left, right = left[:n], right[:n]
    lm, rm = sum(left) / n, sum(right) / n
    a, b = [x - lm for x in left], [x - rm for x in right]
    denom = math.sqrt(sum(x * x for x in a) * sum(x * x for x in b))
    return sum(x * y for x, y in zip(a, b)) / denom if denom else 0.0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mame", type=Path)
    parser.add_argument("render", type=Path)
    parser.add_argument("--offset-seconds", type=float, required=True)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    mame, rate = load(args.mame)
    render, render_rate = load(args.render)
    if rate != render_rate:
        raise ValueError("recordings must have the same sample rate")
    offset = round(args.offset_seconds * rate)
    reference = mame[offset:offset + len(render)]
    windows = []
    for second in range(0, min(len(reference), len(render)) // rate):
        a = reference[second * rate:(second + 1) * rate]
        b = render[second * rate:(second + 1) * rate]
        windows.append({"second": second, "mame_rms": rms(a),
                        "render_rms": rms(b), "correlation": correlation(a, b)})
    report = {"mame": str(args.mame), "render": str(args.render),
              "offset_seconds": args.offset_seconds, "rate": rate,
              "mame_segment_rms": rms(reference), "render_rms": rms(render),
              "windows": windows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {args.output} ({len(windows)} windows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
