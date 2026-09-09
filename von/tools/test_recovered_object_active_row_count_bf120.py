#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    with tempfile.TemporaryDirectory(prefix="von-active-row-count-") as d:
        so = Path(d) / "active-row-count.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_object_active_row_count_bf120.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_object_active_row_count_bf120
        fn.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32,
                       ctypes.POINTER(ctypes.c_uint32)]
        rows = (ctypes.c_uint8 * 32)(*[0, 2, 0, 1, 0, 0, 0xff] + [0] * 25)
        result = ctypes.c_uint32()
        assert fn(rows, 7, ctypes.byref(result)) == 1 and result.value == 3
        assert fn(rows, 0, ctypes.byref(result)) == 1 and result.value == 0
        assert fn(rows, 33, ctypes.byref(result)) == 0
        print("PASS: 0xbf120 reverse-stride active-row count")


if __name__ == "__main__":
    main()
