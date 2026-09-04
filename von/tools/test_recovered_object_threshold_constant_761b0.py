#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def main():
    with tempfile.TemporaryDirectory() as d:
        so = Path(d) / "threshold.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_object_threshold_constant_761b0.c"), "-o", so], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_object_threshold_constant_761b0
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        fn.restype = ctypes.c_uint32
        for value, expected in ((0x4f, 0x45000000), (0x50, 0x45000000),
                                (0x54, 0x45000000), (0x55, 0x45800000),
                                (0x59, 0x45800000), (0x5a, 0x46000000),
                                (0x5e, 0x46000000), (0x5f, 0x46800000),
                                (0x6d, 0x46800000), (0x77, 0x46800000)):
            selector = ctypes.c_uint32(0)
            assert fn(value, ctypes.byref(selector)) == expected
            assert selector.value == 29

if __name__ == "__main__":
    main()
