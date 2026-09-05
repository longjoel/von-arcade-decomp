#!/usr/bin/env python3
"""Validate the recovered 0x18438 pair-swap matcher."""
import ctypes
import pathlib
import subprocess
import tempfile


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "pair-match.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_pair_match_18438.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    match_fn = lib.recovered_pair_match
    match_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    match_fn.restype = ctypes.c_uint32

    assert match_fn(0, 1) == 1
    assert match_fn(1, 0) == 1
    assert match_fn(2, 3) == 1
    assert match_fn(3, 2) == 1
    assert match_fn(0, 0) == 0
    assert match_fn(1, 1) == 0
    assert match_fn(0, 2) == 0
    assert match_fn(2, 2) == 0
    assert match_fn(3, 3) == 0
    assert match_fn(4, 5) == 0
    assert match_fn(1, 3) == 0
    assert match_fn(0xFFFFFFFF, 1) == 0

print("PASS: 0x18438 pair-swap matcher")
