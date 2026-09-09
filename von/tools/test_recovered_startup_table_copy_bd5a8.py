#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("fifo_word", ctypes.c_uint32),
                ("startup_cursor", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-startup-table-copy-") as d:
        so = Path(d) / "startup-table-copy.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        str(ROOT / "von/i960/recovered_startup_table_copy_bd5a8.c"),
                        "-o", str(so)], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_startup_table_copy_bd5a8
        u32 = ctypes.c_uint32
        fn.argtypes = [ctypes.POINTER(u32), ctypes.POINTER(u32),
                       ctypes.POINTER(u32), ctypes.POINTER(u32),
                       ctypes.POINTER(u32), ctypes.POINTER(u32),
                       ctypes.POINTER(u32), ctypes.POINTER(u32),
                       ctypes.POINTER(Result)]
        sizes = (39, 0x99b, 0x333, 0x3fff)
        sources = [(u32 * size)(*[(i * 17 + 3) & 0xffffffff for i in range(size)])
                   for size in sizes]
        destinations = [(u32 * size)(*([0xa5a5a5a5] * size)) for size in sizes]
        result = Result()
        fn(sources[0], destinations[0], sources[1], destinations[1],
           sources[2], destinations[2], sources[3], destinations[3],
           ctypes.byref(result))
        for source, destination in zip(sources, destinations):
            assert list(destination) == list(source)
        assert (result.fifo_word, result.startup_cursor) == (0x44, 0xffffffff)
        print("PASS: startup ROM table copies and publication")


if __name__ == "__main__":
    main()
