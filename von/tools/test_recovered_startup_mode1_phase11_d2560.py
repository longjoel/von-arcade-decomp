#!/usr/bin/env python3
"""Vectors for the mode-1 phase-11 dispatcher at i960 0xd2560.

Observed attract entry (von/tools/probe_mode1_handlers.py): selector 0 and a
proceeding guard, dispatching 0xd0820 plus the 0x20460 follow-up.
"""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
D0820, D0D10, D1280, D1AB0 = 1, 2, 3, 4


class Result(ctypes.Structure):
    _fields_ = [
        ("early", ctypes.c_uint32),
        ("dispatched", ctypes.c_uint32),
        ("followup", ctypes.c_uint32),
    ]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        so = pathlib.Path(tmp) / "d2560.so"
        subprocess.run([
            "cc", "-shared", "-fPIC", "-O2", "-o", str(so),
            str(ROOT / "von/i960/recovered_startup_mode1_phase11_d2560.c"),
        ], check=True)
        fn = ctypes.CDLL(str(so)).recovered_startup_mode1_phase11_run_d2560
        fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Result)]

        def run(guard, selector):
            out = Result()
            fn(guard, selector, ctypes.byref(out))
            return out

        observed = run(0, 0)
        assert observed.early == 0 and observed.dispatched == D0820
        assert observed.followup == 1

        assert run(1, 0).early == 1
        assert run(1, 0).followup == 0
        assert run(0, 1).dispatched == D0D10
        assert run(0, 2).dispatched == D1280
        assert run(0, 3).dispatched == D1AB0
        assert run(0, 0xffffffff).dispatched == D1AB0

    print("PASS: original 0xd2560 mode-1 phase-11 dispatcher vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
