#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("left_word_8", ctypes.c_uint32), ("left_word_10", ctypes.c_uint32),
                ("right_word_8", ctypes.c_uint32), ("right_word_10", ctypes.c_uint32),
                ("event_count", ctypes.c_uint32), ("fifo_response", ctypes.c_uint32),
                ("delta_word_10", ctypes.c_uint32), ("delta_word_8", ctypes.c_uint32),
                ("packet", ctypes.c_uint32 * 3), ("packet_count", ctypes.c_uint32),
                ("state_3e4", ctypes.c_uint32), ("state_address", ctypes.c_uint32),
                ("fifo_address", ctypes.c_uint32), ("threshold", ctypes.c_uint32),
                ("extended_path", ctypes.c_uint32), ("short_path_target", ctypes.c_uint32),
                ("extended_path_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-event-arm4-") as d:
        so = Path(d) / "event-arm4.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_runtime_event_arm4_prefix_ea1a0.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_runtime_event_arm4_prefix_ea1a0
        fn.argtypes = [ctypes.c_uint32] * 6
        fn.restype = Result
        out = fn(0x100, 0x220, 0x180, 0x1a0, 44, 0x12345678)
        assert (out.delta_word_10, out.delta_word_8, out.state_3e4,
                out.threshold, out.extended_path) == (0xffffff80, 0xffffff80, 0x12345678, 44, 0)
        assert list(out.packet) == [10, 0xffffff80, 0xffffff80]
        out = fn(0, 0, 0, 0, 45, 7)
        assert out.extended_path == 1
        assert (out.short_path_target, out.extended_path_target,
                out.state_address, out.fifo_address) == (0xea1f8, 0xea2b8, 0x5783e4, 0x884000)
        print("PASS: 0xea1a0 runtime event arm 4 prefix")


if __name__ == "__main__":
    main()
