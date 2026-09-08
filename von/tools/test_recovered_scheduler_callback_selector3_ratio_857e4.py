#!/usr/bin/env python3
"""Check selector-3 ratio adjustment at i960 0x857e4."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_callback_selector3_ratio_857e4.c"

class Plan(ctypes.Structure):
    _fields_ = [("selector", ctypes.c_uint32),
                ("value_504dbc", ctypes.c_int32),
                ("object_ratio", ctypes.c_float),
                ("ratio_above_165", ctypes.c_uint32),
                ("dimensions_match_2_1", ctypes.c_uint32),
                ("adjusts_g1_to_1", ctypes.c_uint32),
                ("branches_to_85844", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib857e4.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_callback_selector3_ratio_857e4
    function.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_int16,
                         ctypes.c_int16, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    result = function(3, 32, 5, 2, 2, 1)
    assert (result.object_ratio, result.ratio_above_165,
            result.dimensions_match_2_1, result.adjusts_g1_to_1,
            result.branches_to_85844) == (2.5, 1, 1, 1, 0)
    assert function(3, 33, 5, 2, 2, 1).adjusts_g1_to_1 == 0
    assert function(3, 32, 3, 2, 2, 1).adjusts_g1_to_1 == 0
    assert function(2, 0, 5, 2, 2, 1).branches_to_85844 == 1

print("recovered 0x857e4 selector-3 vectors: ok")
