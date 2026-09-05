#!/usr/bin/env python3
"""Validate the recovered 0x183b8 port-word classifier."""
import ctypes
import pathlib
import subprocess
import tempfile


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "port-classify.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_port_classify_183b8.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    classify_fn = lib.recovered_port_classify
    classify_fn.argtypes = [ctypes.c_uint32] * 3
    classify_fn.restype = ctypes.c_uint32

    assert classify_fn(0x1000, 0x5000, 0x1000) == 3
    assert classify_fn(0x3FFE, 0x5000, 0x1000) == 3
    assert classify_fn(0x3FFF, 0x4000, 0x1000) == 0
    assert classify_fn(0xFFFF, 0x4001, 0x3FFE) == 2
    assert classify_fn(0xFFFF, 0x4001, 0x3FFF) == 1
    assert classify_fn(0xFFFF, 0xFFFF, 0xFFFF) == 1

print("PASS: 0x183b8 port-word classifier")
