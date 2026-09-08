#!/usr/bin/env python3
"""Check the object ratio prefix at i960 0x8490c."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_object_ratio_prefix_8490c.c"

class Plan(ctypes.Structure):
    _fields_ = [("rejected_nonzero_190", ctypes.c_uint32),
                ("source", ctypes.c_uint32),
                ("quotient", ctypes.c_int32),
                ("scaled_value", ctypes.c_int32),
                ("zero_product_exit", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib8490c.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_object_ratio_prefix_8490c
    function.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
                         ctypes.c_int32, ctypes.c_int32]
    function.restype = Plan
    assert function(1, 11, 500, 900, 2).rejected_nonzero_190 == 1
    result = function(0, 11, 500, 900, 2)
    assert (result.source, result.quotient, result.scaled_value) == (1, 5, 10)
    assert function(0, 14, 500, 900, 2).scaled_value == 18
    assert function(0, 10, 500, 900, 2).source == 0
    assert function(0, 11, 99, 900, 0).zero_product_exit == 1

print("recovered 0x8490c object-ratio vectors: ok")
