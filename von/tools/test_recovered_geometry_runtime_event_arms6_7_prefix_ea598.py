#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [
        ("variant", ctypes.c_uint32), ("record_word_184", ctypes.c_uint32),
        ("record_word_8", ctypes.c_uint32), ("record_word_10", ctypes.c_uint32),
        ("record_word_c", ctypes.c_uint32), ("fifo_geometry_value", ctypes.c_uint32),
        ("fifo_completion_value", ctypes.c_uint32), ("adjusted_geometry_word", ctypes.c_uint32),
        ("masked_geometry_word", ctypes.c_uint32), ("packet", ctypes.c_uint32 * 6),
        ("packet_count", ctypes.c_uint32), ("record_word_184_offset", ctypes.c_uint32),
        ("record_word_8_offset", ctypes.c_uint32), ("record_word_10_offset", ctypes.c_uint32),
        ("record_word_c_offset", ctypes.c_uint32), ("fifo_address", ctypes.c_uint32),
        ("geometry_constant", ctypes.c_uint32), ("geometry_command", ctypes.c_uint32),
        ("completion_command", ctypes.c_uint32), ("shared_continuation", ctypes.c_uint32),
    ]


def main():
    with tempfile.TemporaryDirectory(prefix="von-event-arms6-7-") as d:
        so = Path(d) / "event-arms6-7.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_runtime_event_arms6_7_prefix_ea598.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_runtime_event_arms6_7_prefix_ea598
        fn.argtypes = [ctypes.c_uint32] * 7
        fn.restype = Result
        for variant, adjusted, expected in ((0, 0xa000, 0xa000), (1, 0xffffe000, 0xe000)):
            out = fn(variant, 0x4000, 0x20, 0x30, 0x40, 0x1111, 0x2222)
            assert (out.adjusted_geometry_word, out.masked_geometry_word) == (adjusted, expected)
            assert list(out.packet) == [29, expected, 0x430c0000, 30, expected, 0x430c0000]
            assert (out.packet_count, out.record_word_184_offset, out.record_word_8_offset,
                    out.record_word_10_offset, out.record_word_c_offset, out.fifo_address,
                    out.shared_continuation) == (6, 0x184, 8, 0x10, 0xc, 0x884000, 0xea684)
        print("PASS: 0xea598/0xea610 runtime event prefixes")


if __name__ == "__main__":
    main()
