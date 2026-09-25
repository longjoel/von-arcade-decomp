#!/usr/bin/env python3
"""Vectors for the mode-1 phase-5 arm at i960 0x2dc50.

Observed on the original attract probe (von/tools/probe_mode1_handlers.py):
phase 5 -> 6, 0x503a80 = 4, 0x503ab0 = 0xff, 0x51aaf4 = 0x870, the three
0x51aaf8/0x51aafc/0x51ab00 words = 1, 0x503a9c = 5, 0x5770f0 = 3.
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
        ("status_a80", ctypes.c_uint32),
        ("status_ab0", ctypes.c_uint32),
        ("rng_a98", ctypes.c_uint32),
        ("rng_a9c", ctypes.c_uint32),
        ("audio_f4", ctypes.c_uint32),
        ("audio_f8", ctypes.c_uint32),
        ("audio_fc", ctypes.c_uint32),
        ("audio_00", ctypes.c_uint32),
        ("cleared", ctypes.c_uint32),
    ]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        so = pathlib.Path(tmp) / "2dc50.so"
        subprocess.run([
            "cc", "-shared", "-fPIC", "-O2", "-o", str(so),
            str(ROOT / "von/i960/recovered_startup_mode1_phase5_2dc50.c"),
        ], check=True)
        fn = ctypes.CDLL(str(so)).recovered_startup_mode1_phase5_run_2dc50
        fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Result)]

        def run(phase, r1, r2, r3):
            out = Result()
            fn(phase, r1, r2, r3, ctypes.byref(out))
            return out

        observed = run(5, 0, 5, 3)
        assert observed.phase == 6, observed.phase
        assert observed.status_a80 == 4 and observed.status_ab0 == 0xff
        assert observed.rng_a9c == 5 and observed.selector == 3
        assert observed.audio_f4 == 0x870
        assert observed.audio_f8 == observed.audio_fc == observed.audio_00 == 1
        assert observed.cleared == 0

        # Raw random values are masked with 7.
        masked = run(0, 0xff, 0x1e, 0x2a)
        assert masked.rng_a98 == 7 and masked.rng_a9c == 6 and masked.selector == 2
        assert run(0xffffffff, 0, 0, 0).phase == 0

    print("PASS: original 0x2dc50 mode-1 phase-5 arm vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
