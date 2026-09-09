#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("prior_phase", ctypes.c_uint32), ("record_word_184", ctypes.c_uint32),
                ("record_word_8", ctypes.c_uint32), ("record_word_10", ctypes.c_uint32),
                ("record_word_c", ctypes.c_uint32), ("fifo_geometry_value", ctypes.c_uint32),
                ("fifo_completion_value", ctypes.c_uint32), ("adjusted_record_base", ctypes.c_uint32),
                ("phase_plus_0x100", ctypes.c_uint32), ("masked_geometry_word", ctypes.c_uint32),
                ("negated_word_c", ctypes.c_uint32), ("packet", ctypes.c_uint32 * 6),
                ("packet_count", ctypes.c_uint32), ("state_3e4", ctypes.c_uint32),
                ("state_3e6", ctypes.c_uint32), ("state_3e8", ctypes.c_uint32),
                ("state_3ec", ctypes.c_uint32), ("state_3f4", ctypes.c_uint32),
                ("state_3f8", ctypes.c_uint32), ("state_address_base", ctypes.c_uint32),
                ("fifo_address", ctypes.c_uint32), ("continuation_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-event-arm0-") as d:
        so = Path(d) / "event-arm0.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_runtime_event_arm0_e9470.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_runtime_event_arm0_e9470
        fn.argtypes = [ctypes.c_uint32] * 7
        fn.restype = Result
        out = fn(0x120, 0x5000, 0x20, 0x1000, 0x30, 0x400, 0x40)
        assert (out.adjusted_record_base, out.phase_plus_0x100,
                out.masked_geometry_word, out.negated_word_c) == (0x8000, 0x220, 0x8220, 0xffffffd0)
        assert list(out.packet) == [29, 0x8220, 0x43020000, 30, 0x8220, 0x43020000]
        assert (out.state_3e4, out.state_3e6, out.state_3e8, out.state_3ec,
                out.state_3f4, out.state_3f8, out.state_address_base,
                out.fifo_address, out.continuation_target) == (
            0x8220, 0x220, 0, 0x43020000, 0x420, 0xfc0, 0x5783e4,
            0x884000, 0xea720)
        print("PASS: 0xe9470 runtime event arm 0")


if __name__ == "__main__":
    main()
