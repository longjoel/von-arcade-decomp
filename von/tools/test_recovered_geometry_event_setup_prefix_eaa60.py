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
                ("setup_packet", ctypes.c_uint32 * 2), ("delta_packet", ctypes.c_uint32 * 3),
                ("setup_packet_count", ctypes.c_uint32), ("delta_packet_count", ctypes.c_uint32),
                ("init_helper", ctypes.c_uint32), ("frame_setup_helper", ctypes.c_uint32),
                ("frame_setup_argument", ctypes.c_uint32), ("fifo_address", ctypes.c_uint32),
                ("left_record_base", ctypes.c_uint32), ("right_record_base", ctypes.c_uint32),
                ("delta_word_10", ctypes.c_uint32), ("delta_word_8", ctypes.c_uint32),
                ("next_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-event-setup-") as d:
        so = Path(d) / "event-setup.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_event_setup_prefix_eaa60.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_event_setup_prefix_eaa60
        fn.argtypes = [ctypes.c_uint32] * 4
        fn.restype = Result
        out = fn(0x100, 0x220, 0x180, 0x1a0)
        assert list(out.setup_packet) == [8, 16]
        assert list(out.delta_packet) == [10, 0xffffff80, 0x80]
        assert (out.setup_packet_count, out.delta_packet_count,
                out.init_helper, out.frame_setup_helper, out.frame_setup_argument,
                out.fifo_address, out.left_record_base, out.right_record_base,
                out.next_target) == (2, 3, 0x295d0, 0x2a990, 0xd000,
                                      0x884000, 0x503ad8, 0x5040d8, 0xeaaf0)
        print("PASS: 0xeaa60 event setup prefix")


if __name__ == "__main__":
    main()
