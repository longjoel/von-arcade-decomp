#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def main():
    with tempfile.TemporaryDirectory() as d:
        so = Path(d) / "descriptor.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_object_state_descriptor_75f00.c"), "-o", so], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_object_state_descriptor_75f00
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32,
                       ctypes.POINTER(ctypes.c_uint32)]
        fn.restype = ctypes.c_uint32
        table = (ctypes.c_uint32 * (18 * 3))(*range(18 * 3))
        output = (ctypes.c_uint32 * 18)()
        assert fn(1, table, 3, output) == 1
        assert list(output) == list(range(18, 36))
        assert fn(2, table, 3, output) == 1
        assert list(output) == list(range(36, 54))
        assert fn(3, table, 3, output) == 0

if __name__ == "__main__":
    main()
