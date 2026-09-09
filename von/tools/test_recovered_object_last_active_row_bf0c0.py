#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    with tempfile.TemporaryDirectory(prefix="von-last-active-row-") as d:
        so = Path(d) / "last-active-row.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_object_last_active_row_bf0c0.c")], check=True)
        fn = ctypes.CDLL(str(so)).recovered_object_last_active_row_bf0c0
        fn.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32,
                       ctypes.POINTER(ctypes.c_uint32)]
        rows = (ctypes.c_uint8 * 32)(*[1, 0, 2, 0, 0, 3] + [0] * 26)
        result = ctypes.c_uint32()
        assert fn(rows, 6, ctypes.byref(result)) == 1 and result.value == 5
        assert fn(rows, 3, ctypes.byref(result)) == 1 and result.value == 2
        assert fn(rows, 0, ctypes.byref(result)) == 1 and result.value == 0xffffffff
        assert fn(rows, 33, ctypes.byref(result)) == 0
        print("PASS: 0xbf0c0 reverse last-active-row search")


if __name__ == "__main__":
    main()
