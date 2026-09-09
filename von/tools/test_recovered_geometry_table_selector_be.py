#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Selection(ctypes.Structure):
    _fields_ = [("table_address", ctypes.c_uint32),
                ("selector_offset", ctypes.c_uint32),
                ("normalized_172", ctypes.c_uint32),
                ("normalized_188", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-geometry-table-selector-") as d:
        so = Path(d) / "geometry-table-selector.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_geometry_table_selector_be.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_table_select_be
        fn.argtypes = [ctypes.c_int, ctypes.c_uint32, ctypes.c_uint32,
                       ctypes.c_uint32, ctypes.POINTER(Selection)]
        fn.restype = ctypes.c_int

        result = Selection()
        assert fn(0, 2, 24, 99, ctypes.byref(result)) == 1
        assert (result.selector_offset, result.table_address) == (0x10, 0xbcc70 + 0x10 + 48)
        assert fn(1, 3, 31, 0, ctypes.byref(result)) == 1
        assert (result.selector_offset, result.table_address) == (4, 0xbcd60 + 4 + 72)
        assert fn(2, 0, 31, 1, ctypes.byref(result)) == 1
        assert result.selector_offset == 0xc
        assert fn(0, 1, 31, 7, ctypes.byref(result)) == 1
        assert result.selector_offset == 8
        assert fn(1, 0, 14, 0, ctypes.byref(result)) == 1
        assert result.selector_offset == 0x14
        assert fn(2, 0, 13, 0, ctypes.byref(result)) == 1
        assert result.selector_offset == 0
        assert fn(0, 0, 0xffff, 0, ctypes.byref(result)) == 1
        assert result.selector_offset == 0 and result.normalized_172 == 0xffffffff
        assert fn(3, 0, 24, 0, ctypes.byref(result)) == 0
        print("PASS: shared geometry table selector branches and scaling")


if __name__ == "__main__":
    main()
