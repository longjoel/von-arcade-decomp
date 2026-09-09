#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("state_3e4", ctypes.c_uint32), ("state_3e8", ctypes.c_uint32),
                ("state_3f0", ctypes.c_uint32), ("state_3f4", ctypes.c_uint32),
                ("state_3f8", ctypes.c_uint32), ("fifo_word", ctypes.c_uint32 * 4),
                ("fifo_count", ctypes.c_uint32), ("snapshot_504b98", ctypes.c_uint32),
                ("snapshot_504b9c", ctypes.c_uint32), ("snapshot_504ba0", ctypes.c_uint32),
                ("snapshot_504ba8", ctypes.c_uint32), ("snapshot_504baa", ctypes.c_uint32),
                ("derived_504d28", ctypes.c_uint32), ("derived_5770f4", ctypes.c_uint32),
                ("fifo_address", ctypes.c_uint32), ("snapshot_base", ctypes.c_uint32),
                ("derived_504d28_address", ctypes.c_uint32),
                ("derived_5770f4_address", ctypes.c_uint32),
                ("opcode", ctypes.c_uint32), ("return_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-event-final-") as d:
        so = Path(d) / "event-final.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_runtime_event_finalize_ea9a0.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_runtime_event_finalize_ea9a0
        fn.argtypes = [ctypes.c_uint32] * 5
        fn.restype = Result
        out = fn(0x12345, 0xabcdef01, 0x10000000, 0x40000000, 0x20000000)
        assert list(out.fifo_word) == [18, 0xc0000000, 0x90000000, 0xa0000000]
        assert (out.snapshot_504b98, out.snapshot_504b9c, out.snapshot_504ba0,
                out.snapshot_504ba8, out.snapshot_504baa) == (
            0x40000000, 0x10000000, 0x20000000, 0xef01, 0x2345)
        assert (out.derived_504d28, out.derived_5770f4, out.fifo_count,
                out.fifo_address, out.snapshot_base, out.derived_504d28_address,
                out.derived_5770f4_address, out.opcode, out.return_target) == (
            0x34, 0, 4, 0x884000, 0x504b98, 0x504d28, 0x5770f4,
            18, 0xeaa50)
        print("PASS: 0xea9a0 runtime event finalizer")


if __name__ == "__main__":
    main()
