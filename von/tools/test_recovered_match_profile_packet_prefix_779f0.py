#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Input(ctypes.Structure):
    _fields_ = [("selected_index", ctypes.c_uint32),
                ("converted_table_word0", ctypes.c_uint32),
                ("converted_table_word2", ctypes.c_uint32),
                ("object_word8", ctypes.c_uint32),
                ("object_word10", ctypes.c_uint32)]


class Result(ctypes.Structure):
    _fields_ = [("table_base", ctypes.c_uint32),
                ("record_stride", ctypes.c_uint32),
                ("record_offset", ctypes.c_uint32),
                ("command31_words", ctypes.c_uint32 * 5),
                ("command31_word_count", ctypes.c_uint32),
                ("next_command", ctypes.c_uint32),
                ("fifo_destination", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-profile-packet-") as d:
        so = Path(d) / "profile-packet.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_match_profile_packet_prefix_779f0.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_match_profile_packet_prefix_779f0
        fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Result)]
        value = Input(7, 0x11111111, 0x22222222, 0x33333333, 0x44444444)
        out = Result()
        fn(ctypes.byref(value), ctypes.byref(out))
        assert (out.table_base, out.record_stride, out.record_offset,
                list(out.command31_words), out.command31_word_count,
                out.next_command, out.fifo_destination) == (
            0x505060, 6, 42,
            [31, 0x11111111, 0x33333333, 0x22222222, 0x44444444],
            5, 29, 0x884000)
        print("PASS: 0x779f0 selected-profile command-31 packet prefix")


if __name__ == "__main__":
    main()
