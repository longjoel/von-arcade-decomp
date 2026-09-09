#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("event_count", ctypes.c_uint32), ("first_fifo_value", ctypes.c_uint32),
                ("lookup_word", ctypes.c_uint32), ("second_fifo_value", ctypes.c_uint32),
                ("scaled_index", ctypes.c_uint32), ("lookup_offset", ctypes.c_uint32),
                ("masked_lookup_word", ctypes.c_uint32), ("packet", ctypes.c_uint32 * 5),
                ("packet_count", ctypes.c_uint32), ("fifo_address", ctypes.c_uint32),
                ("lookup_mask", ctypes.c_uint32), ("scale_shift", ctypes.c_uint32),
                ("scale_divisor", ctypes.c_uint32), ("next_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-event-arm3-short-") as d:
        so = Path(d) / "event-arm3-short.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_runtime_event_arm3_short_e9e00.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_runtime_event_arm3_short_e9e00
        fn.argtypes = [ctypes.c_uint32] * 4
        fn.restype = Result
        out = fn(45, 0x12345678, 0x89abcdef, 0xfeedface)
        assert (out.scaled_index, out.lookup_offset, out.masked_lookup_word) == (16384, 0xffffc000, 0xcdef)
        assert list(out.packet) == [29, 0xcdef, 0x43020000, 30, 0xcdef]
        assert (out.packet_count, out.fifo_address, out.lookup_mask,
                out.scale_shift, out.scale_divisor, out.next_target) == (
            5, 0x884000, 0xffff, 14, 45, 0xe9e50)
        print("PASS: 0xe9e00 runtime event arm 3 short path")


if __name__ == "__main__":
    main()
