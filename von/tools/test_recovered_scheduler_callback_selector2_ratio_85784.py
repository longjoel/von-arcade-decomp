#!/usr/bin/env python3
"""Check selector-2 ratio adjustment at i960 0x85784."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_callback_selector2_ratio_85784.c"

class Plan(ctypes.Structure):
    _fields_ = [("selector", ctypes.c_uint32),
                ("value_504dc0", ctypes.c_int32),
                ("object_ratio", ctypes.c_float),
                ("ratio_above_165", ctypes.c_uint32),
                ("dimensions_match_2_2", ctypes.c_uint32),
                ("adjusts_g1_to_1", ctypes.c_uint32),
                ("branches_to_857e4", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib85784.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_callback_selector2_ratio_85784
    function.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_int16,
                         ctypes.c_int16, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    result = function(2, 149, 5, 2, 2, 2)
    assert (result.object_ratio, result.ratio_above_165,
            result.dimensions_match_2_2, result.adjusts_g1_to_1,
            result.branches_to_857e4) == (2.5, 1, 1, 1, 0)
    assert function(2, 149, 3, 2, 2, 2).adjusts_g1_to_1 == 0
    assert function(2, 150, 5, 2, 2, 2).adjusts_g1_to_1 == 0
    assert function(1, 0, 5, 2, 2, 2).branches_to_857e4 == 1

print("recovered 0x85784 selector-2 vectors: ok")
