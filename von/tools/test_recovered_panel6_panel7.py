#!/usr/bin/env python3
"""Test the adjacent 0x1fa80 and 0x1fad0 panel transfer contracts."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Panel6(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "source_helper", "fill_helper", "column", "row", "width", "height")]


class Panel7(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("helper", "source", "column", "row", "width", "height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-panel6-7-") as directory:
        library = Path(directory) / "panel6-7.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        ROOT / "von/i960/recovered_panel6_source_fill_route.c",
                        ROOT / "von/i960/recovered_panel7_transfer.c", "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))

        panel6 = Panel6()
        panel6_fn = recovered.recovered_panel6_source_fill_plan
        panel6_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Panel6)]
        panel6_fn(1, 14, ctypes.byref(panel6))
        assert (panel6.source, panel6.source_helper, panel6.fill_helper,
                panel6.column, panel6.row, panel6.width, panel6.height) == (0x2FE099A, 0x1DC90, 0, 8, 10, 45, 5)
        panel6_fn(0, 14, ctypes.byref(panel6))
        assert (panel6.source, panel6.source_helper, panel6.fill_helper) == (0, 0, 0x1DF00)

        panel7 = Panel7()
        panel7_fn = recovered.recovered_panel7_transfer_plan
        panel7_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Panel7)]
        panel7_fn(12, ctypes.byref(panel7))
        assert (panel7.helper, panel7.source, panel7.column, panel7.row,
                panel7.width, panel7.height) == (0x1DC10, 0x2FE1350, 10, 10, 43, 5)

    print("PASS: 0x1fa80/0x1fad0 panel transfer routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
