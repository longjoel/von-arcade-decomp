#!/usr/bin/env python3
"""Verify the 68000 sound-ROM extractor and sequence-table resolver.

Builds a synthetic `epr-18670.31`-shaped image (a word-swapped 512 KiB part)
so the test needs no ROMs: `extract_audio.py` must recover the reset vector
and pointer block, and `analyze_sound_rom.py` must resolve the sequence table
from `[0x608004]` (default `--table-offset 0x8004`) rather than the adjacent
voice pointer at `0x8008`.
"""

from __future__ import annotations

import json
import struct
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXTRACT = ROOT / "von/tools/extract_audio.py"
ANALYZE = ROOT / "von/tools/analyze_sound_rom.py"
IMAGE_SIZE = 0x80000
RESET_SP = 0x00005000
RESET_PC = 0x00601200
SEQ_PTR = 0x0060B5E0
VOICE_PTR = 0x00609DA8
SEQ_END = 0x0060CA1A
SEQ_MAX_ID = 1


def word_swap(data: bytes) -> bytes:
    return b"".join(data[i + 1:i + 2] + data[i:i + 1]
                    for i in range(0, len(data), 2))


def build_swapped() -> bytes:
    image = bytearray(IMAGE_SIZE)
    struct.pack_into(">II", image, 0, RESET_SP, RESET_PC)
    struct.pack_into(">I", image, 0x8004, SEQ_PTR)
    struct.pack_into(">I", image, 0x8008, VOICE_PTR)
    struct.pack_into(">I", image, 0x801C, SEQ_END)
    base = SEQ_PTR - 0x600000
    struct.pack_into(">H", image, base, SEQ_MAX_ID)
    struct.pack_into(">H", image, base + 2, 0x0010)
    struct.pack_into(">H", image, base + 4, 0x0020)
    image[base + 0x10:base + 0x18] = bytes(range(8))
    struct.pack_into(">H", image, VOICE_PTR - 0x600000, 1)
    return bytes(image)


def run(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(command, capture_output=True, text=True)


def main() -> int:
    swapped = build_swapped()
    physical = word_swap(swapped)
    with tempfile.TemporaryDirectory(prefix="von-audio-") as directory:
        rom = Path(directory) / "epr-18670.31"
        out = Path(directory) / "vonj-audio.bin"
        rom.write_bytes(physical)

        result = run([sys.executable, str(EXTRACT), "--rom", str(rom),
                      "--output", str(out)])
        assert result.returncode == 0, result.stderr
        assert out.read_bytes() == swapped, "extractor did not word-swap"

        # A wrong reset vector must be rejected, not silently written.
        broken = Path(directory) / "broken.31"
        bad = bytearray(physical)
        struct.pack_into(">II", bad, 0, RESET_SP, 0x00601204)
        broken.write_bytes(word_swap(bytes(bad)))
        assert run([sys.executable, str(EXTRACT), "--rom", str(broken),
                    "--output", str(Path(directory) / "x.bin")]).returncode != 0

        report_path = Path(directory) / "seq.json"
        result = run([sys.executable, str(ANALYZE), str(out),
                      "--no-word-swap", "-o", str(report_path)])
        assert result.returncode == 0, result.stderr
        report = json.loads(report_path.read_text())

    table = report["dispatch_table"]
    assert table["cpu_address"] == SEQ_PTR, hex(table["cpu_address"])
    assert table["maximum_event_id"] == SEQ_MAX_ID
    streams = {stream["id"]: stream for stream in report["streams"]}
    assert set(streams) == {0, 1}  # ids 0..max
    assert streams[0]["cpu_address"] == SEQ_PTR + 0x10
    assert streams[1]["cpu_address"] == SEQ_PTR + 0x20
    assert report["voice_sequence_table"]["cpu_address"] == VOICE_PTR

    print("PASS: reset vector, word swap, and sequence-table resolver")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
