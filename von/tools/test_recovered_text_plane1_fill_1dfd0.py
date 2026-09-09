#!/usr/bin/env python3
"""Test the plane-1 fill helper recovered at 0x1dfd0."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_plane1_fill_1dfd0.c"


class Cell(ctypes.Structure):
    _fields_ = [("destination_byte_address", ctypes.c_uint32),
                ("value", ctypes.c_uint32)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-plane1-fill-") as directory:
        library = Path(directory) / "plane1-fill.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_text_plane1_fill_cell_plan
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.c_uint32, ctypes.POINTER(Cell)]
        plan_fn.restype = ctypes.c_uint32
        plan = Cell()
        assert plan_fn(3, 7, 4, 2, 1, 2, 0xc123, ctypes.byref(plan)) == 1
        assert (plan.destination_byte_address, plan.value) == (0x0100240a, 0xc123)
        assert plan_fn(3, 7, 4, 2, 2, 0, 0, ctypes.byref(plan)) == 0
        assert plan_fn(3, 7, 0xffffffff, 1, 0, 0, 0, ctypes.byref(plan)) == 0
        assert plan_fn(3, 7, 1, 0xffffffff, 0, 0, 0, ctypes.byref(plan)) == 0

    print("PASS: 0x1dfd0 plane-1 fill plan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
