#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("derived_value", ctypes.c_uint32), ("state_3e8", ctypes.c_uint32),
                ("state_3e8_address", ctypes.c_uint32), ("state_base_address", ctypes.c_uint32),
                ("packet", ctypes.c_uint32 * 4), ("packet_count", ctypes.c_uint32),
                ("fifo_address", ctypes.c_uint32), ("store_state", ctypes.c_uint32),
                ("next_target", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-event-prepare-") as d:
        so = Path(d) / "event-prepare.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_geometry_runtime_event_prepare_ea6fc.c")], check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_geometry_runtime_event_prepare_ea6fc
        fn.argtypes = [ctypes.c_uint32]
        fn.restype = Result
        out = fn(0x12345678)
        assert out.state_3e8 == 0x12345678
        assert list(out.packet) == [20, 0x5783e8, 21, 0xffa87c1c]
        assert (out.packet_count, out.state_3e8_address, out.state_base_address,
                out.fifo_address, out.store_state, out.next_target) == (
            4, 0x5783e8, 0x5783e4, 0x884000, 1, 0xea9a0)
        print("PASS: 0xea6fc runtime event preparation")


if __name__ == "__main__":
    main()
