#!/usr/bin/env python3
"""Test the explicit-position 0x1df70 tile-plane fill plan."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_plane0_fill.c"


class Cell(ctypes.Structure):
    _fields_ = [("destination_byte_address", ctypes.c_uint32), ("value", ctypes.c_uint32)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-plane0-fill-") as directory:
        library = Path(directory) / "plane0-fill.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_text_plane0_fill_cell_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.POINTER(Cell)]
        plan_fn.restype = ctypes.c_uint32
        plan = Cell()
        assert plan_fn(1, 14, 3, 2, 1, 2, 0xc123, ctypes.byref(plan)) == 1
        assert (plan.destination_byte_address, plan.value) == (0x01000786, 0xc123)
        assert plan_fn(1, 14, 3, 2, 2, 0, 0, ctypes.byref(plan)) == 0

    print("PASS: 0x1df70 plain tile-plane fill plan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
