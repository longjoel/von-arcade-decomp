#!/usr/bin/env python3
"""Test the 0x1fdf0 and 0x1fe60 panel route contracts."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_panel11_panel12_routes.c"


class Panel11(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("first_source", "first_helper", "second_source", "second_helper",
                 "column", "row", "width", "height")]


class Panel12(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("source", "source_helper", "fill_helper",
                 "column_comes_from_current_position", "row_comes_from_current_position",
                 "width", "height")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-panel11-12-") as directory:
        library = Path(directory) / "panel11-12.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan11 = Panel11()
        fn11 = recovered.recovered_panel11_plan
        fn11.argtypes = [ctypes.POINTER(Panel11)]
        fn11(ctypes.byref(plan11))
        assert (plan11.first_source, plan11.first_helper, plan11.second_source,
                plan11.second_helper, plan11.column, plan11.row,
                plan11.width, plan11.height) == (0x2FD892E, 0x1DC90, 0x2FD894A,
                                                 0x1DC10, 20, 20, 7, 2)

        plan12 = Panel12()
        fn12 = recovered.recovered_panel12_plan
        fn12.argtypes = [ctypes.c_uint32, ctypes.POINTER(Panel12)]
        fn12(1, ctypes.byref(plan12))
        assert (plan12.source, plan12.source_helper, plan12.fill_helper,
                plan12.column_comes_from_current_position,
                plan12.row_comes_from_current_position, plan12.width,
                plan12.height) == (0x2FE0CB0, 0x1DC10, 0, 1, 1, 20, 2)
        fn12(0, ctypes.byref(plan12))
        assert (plan12.source, plan12.source_helper, plan12.fill_helper) == (0, 0, 0x1DF00)

    print("PASS: 0x1fdf0/0x1fe60 panel routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
