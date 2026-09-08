#!/usr/bin/env python3
"""Check callback dimension finalization at i960 0x85844."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_callback_finalize_85844.c"

class Plan(ctypes.Structure):
    _fields_ = [("value_g1", ctypes.c_uint32),
                ("value_g2", ctypes.c_uint32),
                ("value_g3", ctypes.c_uint32),
                ("value_g13", ctypes.c_uint32),
                ("value_504dac", ctypes.c_uint32),
                ("value_504db0", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib85844.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_callback_finalize_85844
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    result = function(2, 2, 16, 16, 1, 9)
    assert (result.value_504dac, result.value_504db0) == (2 | (1 << 5), 2 | (1 << 4))
    result = function(1, 1, 8, 8, 0, 0)
    assert (result.value_504dac, result.value_504db0) == (1 | (1 << 3), 1 | (1 << 3))
    result = function(2, 3, 16, 8, 0, 0)
    assert (result.value_504dac, result.value_504db0) == (4 | (1 << 5), 1 | (1 << 3))

print("recovered 0x85844 callback-finalize vectors: ok")
