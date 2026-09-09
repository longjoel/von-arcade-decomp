#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("queue_flag", ctypes.c_uint32),
                ("computed_offset", ctypes.c_uint32),
                ("suffix_word_count", ctypes.c_uint32),
                ("suffix_words", ctypes.c_uint32 * 5),
                ("fifo_address", ctypes.c_uint32),
                ("control_read_address", ctypes.c_uint32),
                ("control_write_address", ctypes.c_uint32),
                ("common_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-object-packet-tail-") as d:
        so = Path(d) / "object-packet-tail.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_object_packet_tail_e7454.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_object_packet_tail_e7454
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        fn.restype = Result
        empty = fn(1, 0x120)
        assert (empty.suffix_word_count, list(empty.suffix_words)) == (0, [0] * 5)
        suffix = fn(0, 0x120)
        assert (suffix.suffix_word_count, list(suffix.suffix_words)) == \
            (5, [19, 0x3f800000, 0x3f800000, 0x41200000, 0x13b])
        assert (suffix.fifo_address, suffix.control_read_address,
                suffix.control_write_address, suffix.common_target) == \
            (0x884000, 0x802008, 0x801008, 0xe7490)
        print("PASS: 0xe7454 object packet common-tail prefix")


if __name__ == "__main__":
    main()
