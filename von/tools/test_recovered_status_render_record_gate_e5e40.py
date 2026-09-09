#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [("record_word_plus4", ctypes.c_uint32),
                ("route", ctypes.c_uint32),
                ("selected_helper", ctypes.c_uint32),
                ("selected_asset", ctypes.c_uint32),
                ("record_base", ctypes.c_uint32),
                ("record_offset", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-status-record-") as d:
        so = Path(d) / "status-record.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-o", str(so),
                        str(ROOT / "von/i960/recovered_status_render_record_gate_e5e40.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_status_render_record_gate_e5e40
        fn.argtypes = [ctypes.c_uint32]
        fn.restype = Result
        fallback = fn(0xffffffff)
        assert (fallback.route, fallback.selected_helper,
                fallback.selected_asset) == (0, 0xe3a00, 0xe3b50)
        numeric = fn(7)
        assert (numeric.route, numeric.selected_helper,
                numeric.selected_asset) == (1, 0xe3a10, 0)
        assert (numeric.record_base, numeric.record_offset) == (0x578410, 4)
        print("PASS: 0xe5e40 status-render record sentinel gate")


if __name__ == "__main__":
    main()
