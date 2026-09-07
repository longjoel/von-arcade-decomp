#!/usr/bin/env python3
"""Verify the recovered 0x75fe4 stage-row copy against live goldens.

Address math: 0x72050 + 72 * idx (lda (g4)[g4*8] then lda
0x72050[g4*8]). Table content read live from ROM
(von/build/probe_rom_rows.lua). Row identities verified whole-row
against spawn RAM dumps: faithful S3 = row 4 (attempts 1 and 3
identical), faithful S4 = row 2, warped S4-in-slot-1 = row 0.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_stage_row_copy_75fe4.c"

# (idx, expected RAM row from spawn dumps)
ROWS = {
    4: [0x00FA0032, 0x0000012C, 0x0000001E, 0x00000002, 0x00646000,
        0x000A0046, 0x00050014, 0x00C80028, 0x005F005F, 0x0064000F,
        0x0000012C, 0x00000014, 0x0046001E, 0x00960046, 0x00820190,
        0x00000320, 0x0000001E, 0x00000000],
    2: [0x00C80064, 0x0000015E, 0x0000001E, 0x00000003, 0x00646000,
        0x000A0046, 0x00050014, 0x00C80028, 0x00640064, 0x0064000F,
        0x0000012C, 0x00000005, 0x0046001E, 0x00960046, 0x006400FA,
        0x00000320, 0x0000001E, 0x00000000],
    0: [0x00C80032, 0x0000012C, 0x0000001E, 0x00000003, 0x00646580,
        0x000A0046, 0x00050014, 0x00C80028, 0x005A005A, 0x00640019,
        0x0000012C, 0x0000001E, 0x0046001E, 0x00960046, 0x00FA004B,
        0x00000320, 0x0000000A, 0x00000000],
}


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-stage-row-") as directory:
        library = Path(directory) / "stage-row.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
             str(SOURCE), "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        lib.stage_row_address.argtypes = [ctypes.c_uint32]
        lib.stage_row_address.restype = ctypes.c_uint32
        lib.stage_row_lookup.argtypes = [ctypes.c_uint32]
        lib.stage_row_lookup.restype = ctypes.POINTER(ctypes.c_uint32)
        lib.stage_row_copy.argtypes = [
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32)]
        lib.stage_row_copy.restype = None

        for idx in range(8):
            assert lib.stage_row_address(idx) == 0x72050 + idx * 72, idx
        assert not lib.stage_row_lookup(8), "out of range"

        for idx, expected in ROWS.items():
            src = lib.stage_row_lookup(idx)
            assert src, idx
            dst = (ctypes.c_uint32 * 18)()
            lib.stage_row_copy(src, dst)
            assert list(dst) == expected, f"row {idx} copy"
        print("PASS: row addresses, table rows 0/2/4 match spawn dumps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
