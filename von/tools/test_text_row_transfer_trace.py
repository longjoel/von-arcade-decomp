#!/usr/bin/env python3
"""Trace-validate the 0x1bc90 row-transfer plan on a live 48-row upload.

During the 45-second boot capture 48 rows of 0x80 bytes land in the
0x01004000 video plane from work RAM (base 0x02FD2520) through the 0x1bc90
helper family (frames 901-961). The firmware listing shows the loop calling
the 0xf5d40 memcpy per row with the destination in g0 (fixed 0x80 stride)
and the source in g1 (count stride); every width phase reads the g1 side
and writes the g0 side, which pins the transfer direction. No
constant-base caller in the listing uses this source base, so the caller
stays unattributed; rows 17-31 are unique in a 32KB work-RAM window at
+0x80 spacing, which verifies the source stride independently.

This test replays all 48 rows through the compiled plan
(recovered_text_video_row_transfer_plan): each row's predicted source,
destination, and byte count must match the fixture, and every destination
row's bytes must equal its source row's bytes.
"""
import ctypes
import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text.c"
MEMORY_SOURCE = ROOT / "von/i960/recovered_memory.c"
HOST_CONTROL_SOURCE = ROOT / "von/i960/recovered_host_control.c"
FIXTURE = ROOT / "von/i960/text_row_transfer_1f060_fixture.json"


def main() -> int:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    inputs = fixture["inputs"]
    src_base = int(inputs["src_base"], 16)
    dst_base = int(inputs["dst_base"], 16)
    halfwords = inputs["halfwords"]
    rows = fixture["rows"]
    assert inputs["rows"] == len(rows) == 48, "fixture covers the 48-row upload"
    assert halfwords == 0x40
    with tempfile.TemporaryDirectory(prefix="von-text-row-trace-") as directory:
        library = Path(directory) / "text-row-trace.so"
        subprocess.run(
            [
                os.environ.get("CC", "cc"),
                "-shared",
                "-fPIC",
                "-O2",
                SOURCE,
                MEMORY_SOURCE,
                HOST_CONTROL_SOURCE,
                "-o",
                library,
            ],
            check=True,
        )
        recovered = ctypes.CDLL(str(library))
        recovered.recovered_text_video_row_transfer_plan.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        recovered.recovered_text_video_row_transfer_plan.restype = ctypes.c_uint32
        for record in rows:
            row = record["row"]
            call_source = ctypes.c_uint32()
            call_destination = ctypes.c_uint32()
            call_bytes = ctypes.c_uint32()
            valid = recovered.recovered_text_video_row_transfer_plan(
                row,
                src_base,
                dst_base,
                halfwords,
                len(rows),
                ctypes.byref(call_source),
                ctypes.byref(call_destination),
                ctypes.byref(call_bytes),
            )
            expected = (
                int(record["src_addr"], 16),
                int(record["dst_addr"], 16),
                record["bytes"],
            )
            actual = (call_source.value, call_destination.value, call_bytes.value)
            if valid != 1 or actual != expected:
                raise SystemExit(
                    f"row plan mismatch row={row}: {actual!r} != {expected!r}"
                )
            if record["dst"] != record["src"]:
                raise SystemExit(f"row content mismatch row={row}")
    print(f"PASS: {len(rows)} row-transfer rows match the live oracle")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
