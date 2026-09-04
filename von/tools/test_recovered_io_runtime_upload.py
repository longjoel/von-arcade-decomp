#!/usr/bin/env python3
"""Fixture tests for the pure 0x29d0/0x25d0/0x2990 protocol handoff."""
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class Result(ctypes.Structure):
    _fields_ = [("gated", ctypes.c_uint32), ("callback_arg", ctypes.c_uint32),
                ("callback_result", ctypes.c_uint32), ("normalized_latch", ctypes.c_uint32),
                ("upload_result", ctypes.c_uint32)]

def main():
    with tempfile.TemporaryDirectory() as d:
        so = Path(d) / "io-runtime.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_io.c"),
                        str(ROOT / "von/i960/recovered_io_runtime_upload.c"), "-o", so], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_io_runtime_upload_plan
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                       ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint16,
                       ctypes.c_uint16, ctypes.POINTER(ctypes.c_ubyte),
                       ctypes.POINTER(Result)]
        fn.restype = ctypes.c_uint32
        out = (ctypes.c_ubyte * 34)(); result = Result()
        if fn(0, 7, 9, 64, 1, 3, 0x8000, out, result) != 0 or result.gated:
            raise SystemExit("bit-10-disabled path was not gated")
        if fn(1 << 10, 7, 9, 64, 1, 3, 0x8000, out, result) != 1:
            raise SystemExit("enabled path did not complete")
        if result.normalized_latch != 1 << 10 or result.upload_result != 34:
            raise SystemExit("latch/upload result mismatch")
        if fn(1 << 10, 0, 0, 3, 1, 3, 0, out, result) != 1 or result.upload_result:
            raise SystemExit("limit boundary was not rejected")
        if fn(1 << 10, 0, 0, 64, 0, 3, 0, out, result) != 1 or result.upload_result:
            raise SystemExit("upload-enable boundary was not rejected")

if __name__ == "__main__":
    main()
