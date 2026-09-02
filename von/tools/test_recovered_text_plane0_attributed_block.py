#!/usr/bin/env python3
"""Test the explicit-position 0x1dd10 attributed block plan."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_plane0_attributed_block.c"


class Cell(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source_byte_offset", "destination_byte_address", "source_word_or_mask")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-attributed-block-") as directory:
        library = Path(directory) / "attributed-block.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_text_plane0_attributed_cell_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.POINTER(Cell)]
        plan_fn.restype = ctypes.c_uint32
        plan = Cell()
        assert plan_fn(1, 14, 3, 2, 1, 2, 0x0123, ctypes.byref(plan)) == 1
        assert (plan.source_byte_offset, plan.destination_byte_address,
                plan.source_word_or_mask) == (10, 0x01000786, 0xc123)
        assert plan_fn(1, 14, 3, 2, 2, 0, 0, ctypes.byref(plan)) == 0

    print("PASS: 0x1dd10 attributed tile-plane block plan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
