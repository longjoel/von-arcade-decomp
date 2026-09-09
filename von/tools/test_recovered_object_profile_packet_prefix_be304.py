#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Input(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "linked_halfword_2", "linked_field_64", "linked_field_172",
        "linked_word_14", "linked_word_18", "linked_word_1c",
        "profile_word_0", "profile_word_4", "profile_word_8", "profile_word_c")]


class Result(ctypes.Structure):
    _fields_ = [("accepted", ctypes.c_uint32), ("profile_index", ctypes.c_uint32),
                ("scale_bits", ctypes.c_uint32),
                ("fifo_word", ctypes.c_uint32 * 8),
                ("fifo_count", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-profile-packet-prefix-") as d:
        so = Path(d) / "profile-packet-prefix.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_object_profile_packet_prefix_be304.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_object_profile_packet_prefix_be304
        fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Result)]
        value = Input(0, 7, 14, 0x11111111, 0x22222222, 0x33333333,
                      0x44444444, 0x3f800000, 0x55555555, 0x66666666)
        result = Result()
        fn(ctypes.byref(value), ctypes.byref(result))
        assert result.accepted and result.profile_index == 7
        assert result.scale_bits == 0x3f000000
        assert list(result.fifo_word) == [70, 0x11111111, 0x22222222, 0x33333333,
                                          0x3f000000, 0x55555555, 0x44444444, 0x66666666]
        assert result.fifo_count == 8
        value.linked_halfword_2 = 1
        fn(ctypes.byref(value), ctypes.byref(result))
        assert not result.accepted and result.fifo_count == 0
        print("PASS: 0xbe304 profile packet prefix gate and ordering")


if __name__ == "__main__":
    main()
