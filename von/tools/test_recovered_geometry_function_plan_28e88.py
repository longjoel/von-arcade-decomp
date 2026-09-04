#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def main():
    with tempfile.TemporaryDirectory() as d:
        so = Path(d) / "function.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_geometry_function_plan_28e88.c"), "-o", so], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_function_plan_28e88
        fn.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
                       ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32]
        fn.restype = ctypes.c_uint32
        source = (ctypes.c_uint32 * 3)(0x12345678, 0x0000ffff, 0xdeadbeef)
        output = (ctypes.c_uint32 * 8)()
        assert fn(source, 0x12345678, 3, output, 8) == 8
        assert list(output) == [0x404, 0x805678, 3, 0x5678, 0xffff, 0xbeef, 0x1010, 0]
        short = (ctypes.c_uint32 * 2)()
        assert fn(source, 0, 3, short, 2) == 8
        assert list(short) == [0x404, 0x800000]

if __name__ == "__main__":
    main()
