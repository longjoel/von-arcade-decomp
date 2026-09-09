#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("record_word_8", ctypes.c_uint32), ("record_word_10", ctypes.c_uint32),
                ("state_3f0", ctypes.c_uint32), ("state_3f4", ctypes.c_uint32),
                ("state_3f8", ctypes.c_uint32), ("first_fifo_response", ctypes.c_uint32),
                ("second_fifo_response", ctypes.c_uint32), ("delta_word_10", ctypes.c_uint32),
                ("delta_word_8", ctypes.c_uint32), ("first_packet", ctypes.c_uint32 * 3),
                ("second_packet", ctypes.c_uint32 * 7), ("first_packet_count", ctypes.c_uint32),
                ("second_packet_count", ctypes.c_uint32), ("state_3e4", ctypes.c_uint32),
                ("fifo_address", ctypes.c_uint32), ("delta_command", ctypes.c_uint32),
                ("paired_value_command", ctypes.c_uint32), ("continuation_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-event-finalize-") as d:
        so = Path(d) / "event-finalize.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_runtime_event_common_finalize_ea0b0.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_runtime_event_common_finalize_ea0b0
        fn.argtypes = [ctypes.c_uint32] * 7
        fn.restype = Result
        out = fn(0x180, 0x1a0, 0x20, 0x100, 0x120, 0x55, 0xaa)
        assert (out.delta_word_10, out.delta_word_8, out.state_3e4) == (0x80, 0x80, 0x55)
        assert list(out.first_packet) == [10, 0x80, 0x80]
        assert list(out.second_packet) == [31, 0x100, 0x180, 0, 0, 0x120, 0x1a0]
        assert (out.first_packet_count, out.second_packet_count,
                out.fifo_address, out.delta_command, out.paired_value_command,
                out.continuation_target) == (3, 7, 0x884000, 10, 31, 0xea6fc)
        print("PASS: 0xea0b0 runtime event common finalizer")


if __name__ == "__main__":
    main()
