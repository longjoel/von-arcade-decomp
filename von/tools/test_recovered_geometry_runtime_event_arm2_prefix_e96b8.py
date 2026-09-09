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
                ("phase_before", ctypes.c_uint32), ("delta_word_10", ctypes.c_uint32),
                ("delta_word_8", ctypes.c_uint32), ("packet", ctypes.c_uint32 * 6),
                ("packet_count", ctypes.c_uint32), ("phase_after", ctypes.c_uint32),
                ("phase_address", ctypes.c_uint32), ("left_record_base", ctypes.c_uint32),
                ("right_record_base", ctypes.c_uint32), ("fifo_address", ctypes.c_uint32),
                ("delta_command", ctypes.c_uint32), ("paired_value_command", ctypes.c_uint32),
                ("next_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-event-arm2-") as d:
        so = Path(d) / "event-arm2.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_runtime_event_arm2_prefix_e96b8.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_runtime_event_arm2_prefix_e96b8
        fn.argtypes = [ctypes.c_uint32] * 5
        fn.restype = Result
        out = fn(0x100, 0x220, 0x180, 0x1a0, 7)
        assert (out.delta_word_10, out.delta_word_8, out.phase_after) == (0xffffff80, 0x80, 8)
        assert list(out.packet) == [10, 0xffffff80, 0x80, 31, 0x180, 0x100]
        assert (out.packet_count, out.phase_address, out.left_record_base,
                out.right_record_base, out.fifo_address, out.delta_command,
                out.paired_value_command, out.next_target) == (
            6, 0x5783e6, 0x5040d0, 0x503ad0, 0x884000, 10, 31, 0xe974c)
        print("PASS: 0xe96b8 runtime event arm 2 prefix")


if __name__ == "__main__":
    main()
