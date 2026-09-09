#!/usr/bin/env python3
import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Input(ctypes.Structure):
    _fields_ = [("response_first", ctypes.c_uint32),
                ("response_second", ctypes.c_uint32),
                ("response_gate", ctypes.c_uint32)]


class Result(ctypes.Structure):
    _fields_ = [("frame_pair", ctypes.c_uint32 * 2),
                ("gate_is_zero", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32),
                ("frame_output_offset", ctypes.c_uint32),
                ("frame_aux_offset", ctypes.c_uint32)]


def main():
    with tempfile.TemporaryDirectory(prefix="von-mode9-response-") as d:
        so = Path(d) / "mode9-response.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        "-I", str(ROOT / "von/i960"), "-o", str(so),
                        str(ROOT / "von/i960/recovered_startup_mode9_response_gate_dea6c.c")],
                       check=True)
        lib = ctypes.CDLL(str(so))
        fn = lib.recovered_startup_mode9_response_gate_dea6c
        fn.argtypes = [ctypes.POINTER(Input), ctypes.POINTER(Result)]
        out = Result()
        fn(ctypes.byref(Input(0x11111111, 0x22222222, 0)), ctypes.byref(out))
        assert (list(out.frame_pair), out.gate_is_zero, out.continuation,
                out.frame_output_offset, out.frame_aux_offset) == \
            ([0x11111111, 0x22222222], 1, 0xdead0, 0x40, 0x44)
        fn(ctypes.byref(Input(1, 2, 3)), ctypes.byref(out))
        assert not out.gate_is_zero and out.continuation == 0xdea94
        print("PASS: 0xdea6c mode-9 response publication and gate")


if __name__ == "__main__":
    main()
