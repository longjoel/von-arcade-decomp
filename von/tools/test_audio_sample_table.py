#!/usr/bin/env python3
"""Verify the committed 68000 sample descriptor table.

`von/audio-sample-descriptors.json` is produced by
`von/tools/extract_audio_sample_table.py` from the disassembled sound image.
Each 16-byte record binds a descriptor index to a source pointer in the
8 MiB sample region and a byte length; the 68k uploads that range into SCSP
sound RAM before keying the voice. This test pins the schema, the anchors,
and the address invariants and re-derives the table when the image is present.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAPPING = ROOT / "von/audio-sample-descriptors.json"
EXTRACTOR = ROOT / "von/tools/extract_audio_sample_table.py"
IMAGE = ROOT / "von/build/disasm/vonj-audio.bin"
SAMPLE_BASE = 0x800000
SAMPLE_SIZE = 0x800000

ANCHORS = {
    0x00: (0x800000, 13821, 0),
    0x01: (0x8035FE, 11415, 0),
    0x15: (0x86DC44, 51647, 37786),
    0x27: (0x8EBD7C, 20087, 13668),
    0x42: (0x95F75E, 18041, 0),
    0x47: (0x96C03E, 1331, 0),
}


def load_extractor():
    spec = importlib.util.spec_from_file_location(
        "extract_audio_sample_table", EXTRACTOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    report = json.loads(MAPPING.read_text())
    assert report["schema"] == "von-audio-sample-descriptors/1"
    assert report["records_pointer"] == 0x0060A010
    assert report["record_base"] == 0x0060A012
    descriptors = report["descriptors"]
    assert len(descriptors) == 347, len(descriptors)
    by_index = {d["index"]: d for d in descriptors}
    assert len(by_index) == len(descriptors)

    for index, (source, length, loop) in ANCHORS.items():
        record = by_index[index]
        assert record["source"] == source, (hex(index), hex(record["source"]))
        assert record["copy_length"] == length, hex(index)
        assert record["loop_length"] == loop, hex(index)

    for record in descriptors:
        assert record["region"] == "samples", record["index"]
        assert SAMPLE_BASE <= record["source"] < SAMPLE_BASE + SAMPLE_SIZE
        assert record["copy_length"] > 0
        assert record["offset"] + record["copy_length"] <= SAMPLE_SIZE

    if IMAGE.is_file():
        extractor = load_extractor()
        assert extractor.build_table(IMAGE.read_bytes()) == report, \
            "committed table differs from the ROM"

    print(f"PASS: {len(descriptors)} sample descriptors, {len(ANCHORS)} anchors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
