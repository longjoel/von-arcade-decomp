#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [
        ("encoded_count", ctypes.c_uint32), ("source_count", ctypes.c_uint32),
        ("output_count", ctypes.c_uint32), ("source_advance", ctypes.c_uint32),
        ("destination_advance", ctypes.c_uint32), ("continuation_target", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="von-byte-expand-") as d:
        so = Path(d) / "byte-expand.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_runtime_byte_expand_eae60.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_runtime_byte_expand_eae60
        fn.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8),
                       ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                       ctypes.POINTER(Result)]
        fn.restype = ctypes.c_int
        source = (ctypes.c_uint8 * 4)(0x11, 0x22, 0x80, 0xff)
        destination = (ctypes.c_uint8 * 8)(*([0xaa] * 8))
        out = Result()
        assert fn(source, destination, 8, 8, 0x123456, ctypes.byref(out)) == 1
        assert list(destination) == [0x11, 0, 0x22, 0, 0x80, 0, 0xff, 0]
        assert (out.encoded_count, out.source_count, out.output_count,
                out.source_advance, out.destination_advance, out.continuation_target) == (
            8, 4, 8, 4, 8, 0x123456)
        assert fn(source, destination, 7, 6, 0x123456, ctypes.byref(out)) == 1
        assert (out.source_count, out.output_count) == (3, 6)
        assert fn(source, destination, 8, 7, 0x123456, ctypes.byref(out)) == 0
        print("PASS: 0xeae60 runtime byte expansion")


if __name__ == "__main__":
    main()
