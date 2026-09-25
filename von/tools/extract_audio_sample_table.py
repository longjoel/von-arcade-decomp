#!/usr/bin/env python3
"""Extract the 68000 sound driver's static sample descriptor table.

At reset the driver copies a 16-byte-record table from the pointer word at
`0x608000` (value `0x60a010`) into sound RAM at `0x5000`, then walks the
index list at pointer `0x608020` (value `0x60b5c2`) and uploads each selected
sample from the sample region into RAM, patching the table entry with the RAM
destination.

Record layout (big-endian, at `0x60a012 + index*16`):

  +0x00  u32  source pointer (sample region `0x800000+`, or program ROM)
  +0x04  u32  copy length in bytes - 1
  +0x08  u32  end pointer (or end-src when +0x0c is nonzero)
  +0x0c  u32  flag: nonzero switches +0x08 to a length and marks a loop

The i960 `ae HH LL` command resolves to `9a/9b/9c, index, param`; the
engine's sequence record maps that index range to one of these descriptor
indices. This tool exposes the descriptor -> PCM binding; the range-table hop
is documented in von/docs/audio-68000.md.

Python's struct reads the words as stored in the assembled image, which is
the 68000 big-endian view.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "von/build/disasm/vonj-audio.bin"
POINTER_RECORDS = 0x8000   # [0x608000]
POINTER_INDEX = 0x8020     # [0x608020]
RECORD_BASE = 0x60A012
RECORD_SIZE = 16
SAMPLE_BASE = 0x800000
PROGRAM_BASE = 0x600000
PROGRAM_END = 0x680000


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from(">H", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from(">I", data, offset)[0]


def _region(source: int) -> tuple[str, int | None]:
    if SAMPLE_BASE <= source < 0x1000000:
        return "samples", source - SAMPLE_BASE
    if PROGRAM_BASE <= source < PROGRAM_END:
        return "program", source - PROGRAM_BASE
    return "unknown", None


def build_table(data: bytes) -> dict:
    records_pointer = u32(data, POINTER_RECORDS)
    blob_size = u16(data, records_pointer - PROGRAM_BASE)
    base = RECORD_BASE - PROGRAM_BASE

    # The index list at [0x608020] is the eager-upload set; on this ROM it is
    # terminated immediately (0xffff), so the descriptor table is walked until
    # the source leaves the sample/program regions.
    index_pointer = u32(data, POINTER_INDEX)
    ib = index_pointer - PROGRAM_BASE
    list_base = ib + u16(data, ib + 2)
    sentinel = u16(data, list_base)
    indices = []
    if sentinel != 0xFFFF:
        indices = [u16(data, list_base + 2 + i * 2)
                   for i in range(sentinel + 1)]

    descriptors = []
    for index in range(512):
        offset = base + index * RECORD_SIZE
        if offset + RECORD_SIZE > len(data):
            break
        source = u32(data, offset)
        region, region_offset = _region(source)
        if region == "unknown":
            break
        copy_length = u32(data, offset + 4)
        end = u32(data, offset + 8)
        flag = u32(data, offset + 12)
        descriptors.append({
            "index": index,
            "source": source,
            "region": region,
            "offset": region_offset,
            "copy_length": copy_length + 1,
            "end": end,
            "loop_length": (end - source) & 0xFFFFFFFF if flag else 0,
            "loop_flag": flag,
        })
    return {
        "schema": "von-audio-sample-descriptors/1",
        "records_pointer": records_pointer,
        "blob_size": blob_size,
        "record_base": RECORD_BASE,
        "record_size": RECORD_SIZE,
        "index_pointer": index_pointer,
        "index_list_base": list_base + PROGRAM_BASE,
        "index_count": len(indices),
        "indices": indices,
        "max_index": len(descriptors) - 1,
        "descriptors": descriptors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("-o", "--output", type=Path,
                        default=ROOT / "von/audio-sample-descriptors.json")
    parser.add_argument("--extract", type=Path, metavar="DIR",
                        help="also write PCM8 WAVs for each descriptor")
    parser.add_argument("--sample-roms", nargs=2, type=Path,
                        default=[ROOT / "von/artifacts/mpr-18652.32",
                                 ROOT / "von/artifacts/mpr-18653.34"])
    args = parser.parse_args()
    if not args.image.is_file():
        parser.error(f"missing image: {args.image} (run ./vonctl disasm audio)")
    report = build_table(args.image.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {args.output} ({len(report['descriptors'])} descriptors, "
          f"{report['index_count']} index entries)")

    if args.extract:
        import wave
        samples = b"".join(
            _swap_words(path.read_bytes()) for path in args.sample_roms)
        program = args.image.read_bytes()
        args.extract.mkdir(parents=True, exist_ok=True)
        written = 0
        for descriptor in report["descriptors"]:
            source = descriptor["source"]
            length = descriptor["copy_length"]
            if descriptor["region"] == "samples":
                raw = samples[descriptor["offset"]:descriptor["offset"] + length]
            elif descriptor["region"] == "program":
                raw = program[descriptor["offset"]:descriptor["offset"] + length]
            else:
                continue
            if len(raw) < 2:
                continue
            pcm = b"".join(
                int((value - 256 if value >= 128 else value) << 8)
                .to_bytes(2, "little", signed=True) for value in raw)
            name = args.extract / f"{descriptor['index']:04d}-{source:08x}.wav"
            with wave.open(str(name), "wb") as out:
                out.setnchannels(1)
                out.setsampwidth(2)
                out.setframerate(44100)
                out.writeframes(pcm)
            written += 1
        print(f"wrote {written} descriptor WAVs to {args.extract}")
    return 0


def _swap_words(data: bytes) -> bytes:
    return b"".join(data[i + 1:i + 2] + data[i:i + 1]
                    for i in range(0, len(data), 2))


if __name__ == "__main__":
    raise SystemExit(main())
