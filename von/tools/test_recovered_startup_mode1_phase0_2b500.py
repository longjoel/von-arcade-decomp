#!/usr/bin/env python3
"""Vectors for the mode-1 phase-0 arm at i960 0x2b500.

Observed on the original attract probe (von/tools/probe_mode1_handlers.py):
phase 0 -> 1, with 0x51aac4, 0x503aac and 0x51c850 all zero.
"""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]


class Result(ctypes.Structure):
    _fields_ = [
        ("phase", ctypes.c_uint32),
        ("clear_a", ctypes.c_uint32),
        ("clear_b", ctypes.c_uint32),
        ("work", ctypes.c_uint32),
    ]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        so = pathlib.Path(tmp) / "2b500.so"
        subprocess.run([
            "cc", "-shared", "-fPIC", "-O2", "-o", str(so),
            str(ROOT / "von/i960/recovered_startup_mode1_phase0_2b500.c"),
        ], check=True)
        fn = ctypes.CDLL(str(so)).recovered_startup_mode1_phase0_run_2b500
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Result)]

        def run(phase, g0):
            out = Result()
            fn(phase, g0, ctypes.byref(out))
            return out

        observed = run(0, 0)
        assert observed.phase == 1
        assert observed.clear_a == observed.clear_b == observed.work == 0

        other = run(0xffffffff, 0x1234)
        assert other.phase == 0 and other.work == 0x1234

    print("PASS: original 0x2b500 mode-1 phase-0 arm vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
