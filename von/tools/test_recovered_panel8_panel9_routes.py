#!/usr/bin/env python3
"""Test the 0x1fb10 and 0x1fb50 panel route contracts."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_panel8_panel9_routes.c"


class Panel8(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in ("helper", "source", "column", "row", "width", "height")]


class Panel9(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "source_helper", "fill_helper", "column", "row", "width", "height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-panel8-9-") as directory:
        library = Path(directory) / "panel8-9.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        panel8 = Panel8()
        fn8 = recovered.recovered_panel8_plan
        fn8.argtypes = [ctypes.c_uint32, ctypes.POINTER(Panel8)]
        fn8(17, ctypes.byref(panel8))
        assert (panel8.helper, panel8.source, panel8.column, panel8.row,
                panel8.width, panel8.height) == (0x1DC90, 0x2FE1170, 7, 10, 48, 5)

        panel9 = Panel9()
        fn9 = recovered.recovered_panel9_plan
        fn9.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Panel9)]
        fn9(1, 22, ctypes.byref(panel9))
        assert (panel9.source, panel9.source_helper, panel9.fill_helper,
                panel9.column, panel9.row, panel9.width, panel9.height) == (0x2FE0D42, 0x1DC10, 0, 5, 10, 53, 5)
        fn9(0, 22, ctypes.byref(panel9))
        assert (panel9.source, panel9.source_helper, panel9.fill_helper) == (0, 0, 0x1DF00)

    print("PASS: 0x1fb10/0x1fb50 panel routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
