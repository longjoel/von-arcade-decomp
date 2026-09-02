#!/usr/bin/env python3
"""Validate the proven terminal decision layer of SHARC opcode 0x4d."""
import ctypes
import pathlib
import subprocess
import tempfile


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "opcode4d.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2",
        str(pathlib.Path(__file__).parents[1] / "i960" /
            "recovered_sharc_opcode_4d_decision.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    decision = lib.recovered_sharc_opcode_4d_decision
    decision.argtypes = [ctypes.c_float] * 4
    decision.restype = ctypes.c_uint

    assert decision(-1.0, 100.0, 100.0, 0.0) == 1
    assert decision(0.0, 4.0, 1.0, 4.0) == 0
    assert decision(0.0, 5.0, 1.0, 4.0) == 2
    assert decision(0.0, 5.0, 1.0, 5.0) == 0
    nan = float("nan")
    assert decision(0.0, nan, 1.0, 4.0) == 2
    assert decision(0.0, 4.0, nan, 4.0) == 2

print("PASS: SHARC opcode-0x4d terminal decision")
