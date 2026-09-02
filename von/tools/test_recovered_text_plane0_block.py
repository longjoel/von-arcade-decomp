#!/usr/bin/env python3
"""Test the 0x1dc10 plain tile-plane address and attribute plan."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_plane0_block.c"


class Cell(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source_byte_offset", "destination_byte_address", "source_word_or_mask")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-plane0-block-") as directory:
        library = Path(directory) / "plane0-block.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_text_plane0_cell_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.POINTER(Cell)]
        plan_fn.restype = ctypes.c_uint32
        plan = Cell()
        assert plan_fn(3, 2, 4, 3, 1, 2, 0x0123, ctypes.byref(plan)) == 1
        assert (plan.source_byte_offset, plan.destination_byte_address,
                plan.source_word_or_mask) == (12, 0x0100018A, 0x8123)
        assert plan_fn(3, 2, 4, 3, 0, 4, 0, ctypes.byref(plan)) == 0

    print("PASS: 0x1dc10 plain tile-plane block plan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
