#!/usr/bin/env python3
"""Vectors for the mode-1 phase-10 arm at i960 0xd24b0.

The observed vector comes from the original input-free attract probe
(von/tools/probe_mode1_handlers.py): phase 10 -> 11, 0x5770f0 3 -> 13,
0x503ab4 0x64 -> 0x73, 0x503ab8 stable at 0x258.
"""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [
        ("phase", ctypes.c_uint32),
        ("selector", ctypes.c_uint32),
        ("mode_a", ctypes.c_uint32),
        ("mode_b", ctypes.c_uint32),
        ("cleared", ctypes.c_uint32),
    ]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        so = pathlib.Path(tmp) / "d24b0.so"
        subprocess.run([
            "cc", "-shared", "-fPIC", "-O2", "-o", str(so),
            str(ROOT / "von/i960/recovered_startup_mode1_phase10_d24b0.c"),
        ], check=True)
        fn = ctypes.CDLL(str(so)).recovered_startup_mode1_phase10_run_d24b0
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]

        def run(phase):
            out = Result()
            fn(phase, ctypes.byref(out))
            return out

        observed = run(10)
        assert observed.phase == 11, observed.phase
        assert observed.selector == 13, observed.selector
        assert observed.mode_a == 0x73, hex(observed.mode_a)
        assert observed.mode_b == 0x258, hex(observed.mode_b)
        assert observed.cleared == 0

        wrapped = run(0xffffffff)
        assert wrapped.phase == 0
        assert wrapped.selector == 13 and wrapped.mode_a == 0x73

    print("PASS: original 0xd24b0 mode-1 phase-10 arm vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
