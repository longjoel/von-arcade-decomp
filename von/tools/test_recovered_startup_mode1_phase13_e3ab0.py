#!/usr/bin/env python3
"""Vectors for the mode-1 phase-13 arm at i960 0xe3ab0.

The entry vector (device byte 1, sub-state 0, phase 13) and the 0xe3b70
dispatch come from the original input-free attract probe in
von/tools/probe_e3ab0.py. The other dispatch arms follow the listing branch
ladder (sub-state 1 -> 0xe3dc0, 2 -> 0xe3f30) and the cycle-consistent clamp.
"""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
E3B70, E3DC0, E3F30 = 1, 2, 3


class Result(ctypes.Structure):
    _fields_ = [
        ("phase", ctypes.c_uint32),
        ("substate", ctypes.c_uint32),
        ("dispatched", ctypes.c_uint32),
        ("device_status", ctypes.c_uint32),
        ("early", ctypes.c_uint32),
    ]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        so = pathlib.Path(tmp) / "e3ab0.so"
        subprocess.run([
            "cc", "-shared", "-fPIC", "-O2", "-o", str(so),
            str(ROOT / "von/i960/recovered_startup_mode1_phase13_e3ab0.c"),
        ], check=True)
        fn = ctypes.CDLL(str(so)).recovered_startup_mode1_phase13_run_e3ab0
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                       ctypes.POINTER(Result)]

        def run(phase, dev, sub):
            out = Result()
            fn(phase, dev, sub, ctypes.byref(out))
            return out

        # Observed attract entry: dev 1, sub-state 0 -> 0xe3b70, sub-state 1.
        observed = run(13, 1, 0)
        assert observed.dispatched == E3B70, observed.dispatched
        assert observed.substate == 1, observed.substate
        assert observed.phase == 13 and observed.early == 0

        # Device byte zero advances the phase by two and does not dispatch.
        idle = run(5, 0, 2)
        assert idle.phase == 7 and idle.early == 1
        assert idle.dispatched == 0 and idle.substate == 2

        # Sub-state 1 -> 0xe3dc0, 2 -> 0xe3f30; higher wraps to 0 -> 0xe3b70.
        assert run(0, 1, 1).dispatched == E3DC0
        assert run(0, 1, 1).substate == 2
        assert run(0, 1, 2).dispatched == E3F30
        assert run(0, 1, 2).substate == 3
        wrapped = run(0, 1, 3)
        assert wrapped.dispatched == E3B70 and wrapped.substate == 1

    print("PASS: original 0xe3ab0 mode-1 phase-13 arm vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
