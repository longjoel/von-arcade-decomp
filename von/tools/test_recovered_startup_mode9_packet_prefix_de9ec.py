#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Input(ctypes.Structure):
    _fields_ = [("status_pair_0", ctypes.c_uint32),
                ("status_pair_1", ctypes.c_uint32),
                ("status_word", ctypes.c_uint32),
                ("geometry_pair_0", ctypes.c_uint32),
                ("geometry_pair_1", ctypes.c_uint32),
                ("geometry_word", ctypes.c_uint32)]


class Result(ctypes.Structure):
    _fields_ = [("packet_words", ctypes.c_uint32 * 10),
                ("packet_word_count", ctypes.c_uint32),
                ("fifo_destination", ctypes.c_uint32),
                ("first_command", ctypes.c_uint32),
                ("second_command", ctypes.c_uint32),
                ("constant_word", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-mode9-packet-") as d:
        so = Path(d) / "mode9-packet.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_startup_mode9_packet_prefix_de9ec.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_startup_mode9_packet_prefix_de9ec
        fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Result)]
        value = Input(1, 2, 3, 4, 5, 6)
        out = Result()
        fn(ctypes.byref(value), ctypes.byref(out))
        assert list(out.packet_words) == [38, 1, 2, 3, 0x428c0000,
                                           0, 39, 4, 5, 6]
        assert (out.packet_word_count, out.fifo_destination,
                out.first_command, out.second_command,
                out.constant_word) == (10, 0x884000, 38, 39, 0x428c0000)
        print("PASS: 0xde9ec mode-9 two-command packet prefix")


if __name__ == "__main__":
    main()
