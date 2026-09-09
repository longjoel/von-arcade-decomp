#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Input(ctypes.Structure):
    _fields_ = [("command31_response", ctypes.c_uint32),
                ("converted_record_word4", ctypes.c_uint32)]


class Result(ctypes.Structure):
    _fields_ = [("masked_response_lane", ctypes.c_uint32),
                ("command29_words", ctypes.c_uint32 * 3),
                ("command30_words", ctypes.c_uint32 * 3),
                ("command_word_count", ctypes.c_uint32),
                ("fifo_destination", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-profile-2930-") as d:
        so = Path(d) / "profile-2930.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_match_profile_command29_30_77a64.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_match_profile_command29_30_77a64
        fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Result)]
        value = Input(0xfffff234, 0x41200000)
        out = Result()
        fn(ctypes.byref(value), ctypes.byref(out))
        assert out.masked_response_lane == 0x2234
        assert list(out.command29_words) == [29, 0x2234, 0x41200000]
        assert list(out.command30_words) == [30, 0x2234, 0x41200000]
        assert (out.command_word_count, out.fifo_destination) == (3, 0x884000)
        print("PASS: 0x77a64 command-29/30 masked request pair")


if __name__ == "__main__":
    main()
