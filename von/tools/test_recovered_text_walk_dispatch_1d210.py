#!/usr/bin/env python3
"""Validate the recovered 0x1d210 fixed-callee text walker routes."""
import ctypes
import pathlib
import subprocess
import tempfile


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "walk-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_text_walk_dispatch_1d210.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    lib.recovered_text_walk_route_count.restype = ctypes.c_uint32
    lib.recovered_text_walk_callee.argtypes = [ctypes.c_uint32]
    lib.recovered_text_walk_callee.restype = ctypes.c_uint32

    assert lib.recovered_text_walk_route_count() == 3
    assert lib.recovered_text_walk_callee(0x1D210) == 0x1D090
    assert lib.recovered_text_walk_callee(0x1D230) == 0x1CF40
    assert lib.recovered_text_walk_callee(0x1D250) == 0x1CFE0
    assert lib.recovered_text_walk_callee(0x1D1B0) == 0
    assert lib.recovered_text_walk_callee(0) == 0

print("PASS: 0x1d210 text walker routes")
