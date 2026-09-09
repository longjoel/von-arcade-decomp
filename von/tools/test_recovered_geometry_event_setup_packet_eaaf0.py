#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("fifo_response", ctypes.c_uint32), ("auxiliary_word", ctypes.c_uint32),
                ("packet", ctypes.c_uint32 * 7), ("packet_count", ctypes.c_uint32),
                ("fifo_address", ctypes.c_uint32), ("auxiliary_address", ctypes.c_uint32),
                ("left_word_8_address", ctypes.c_uint32), ("right_word_8_address", ctypes.c_uint32),
                ("left_word_10_address", ctypes.c_uint32), ("right_word_10_address", ctypes.c_uint32),
                ("opcode", ctypes.c_uint32), ("next_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-event-setup-packet-") as d:
        so = Path(d) / "event-setup-packet.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_event_setup_packet_eaaf0.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_event_setup_packet_eaaf0
        fn.argtypes = [ctypes.c_uint32] * 2
        fn.restype = Result
        out = fn(0x1234, 0x5678)
        assert list(out.packet) == [31, 0x503ad8, 0x5040d8, 0, 0, 0x503ae0, 0x5040e0]
        assert (out.packet_count, out.fifo_address, out.auxiliary_address,
                out.left_word_8_address, out.right_word_8_address,
                out.left_word_10_address, out.right_word_10_address,
                out.opcode, out.next_target) == (
            7, 0x884000, 0x503adc, 0x503ad8, 0x5040d8,
            0x503ae0, 0x5040e0, 31, 0xeab48)
        print("PASS: 0xeaaf0 event setup packet")


if __name__ == "__main__":
    main()
