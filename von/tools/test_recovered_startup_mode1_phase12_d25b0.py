#!/usr/bin/env python3
"""Vectors for the mode-1 phase-12 dispatcher at i960 0xd25b0.

Observed attract entry (von/tools/probe_mode1_handlers.py): selector 0, so the
arm dispatches 0xd0970.
"""
import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
D0970, D0E60, D13B0, D1BE0 = 1, 2, 3, 4


class Result(ctypes.Structure):
    _fields_ = [("dispatched", ctypes.c_uint32)]


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        so = pathlib.Path(tmp) / "d25b0.so"
        subprocess.run([
            "cc", "-shared", "-fPIC", "-O2", "-o", str(so),
            str(ROOT / "von/i960/recovered_startup_mode1_phase12_d25b0.c"),
        ], check=True)
        fn = ctypes.CDLL(str(so)).recovered_startup_mode1_phase12_run_d25b0
        fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Result)]

        def run(selector):
            out = Result()
            fn(selector, ctypes.byref(out))
            return out

        assert run(0).dispatched == D0970
        assert run(1).dispatched == D0E60
        assert run(2).dispatched == D13B0
        assert run(3).dispatched == D1BE0
        assert run(0xffffffff).dispatched == D1BE0

    print("PASS: original 0xd25b0 mode-1 phase-12 dispatcher vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
