#!/usr/bin/env python3
"""Check callback global admission at i960 0x855b8."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_callback_global_gate_855b8.c"

class Plan(ctypes.Structure):
    _fields_ = [("global_flag", ctypes.c_uint32),
                ("value_504dc0", ctypes.c_int32),
                ("value_503a14", ctypes.c_int32),
                ("value_503a18", ctypes.c_int32),
                ("frame_quotient", ctypes.c_int32),
                ("frame_target", ctypes.c_int32),
                ("target_difference", ctypes.c_int32),
                ("exits_to_85678", ctypes.c_uint32),
                ("continues_to_object_ratio", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib855b8.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_callback_global_gate_855b8
    function.argtypes = [ctypes.c_uint32, ctypes.c_int32,
                         ctypes.c_int32, ctypes.c_int32]
    function.restype = Plan
    result = function(0, 149, 96, 3)
    assert (result.frame_quotient, result.frame_target,
            result.target_difference, result.exits_to_85678,
            result.continues_to_object_ratio) == (2, 3, 0, 0, 1)
    assert function(1, 0, 0, 0).exits_to_85678 == 1
    assert function(0, 150, 0, 0).exits_to_85678 == 1
    assert function(0, 0, 0, 23).exits_to_85678 == 1
    assert function(0, 0, 0, 20).continues_to_object_ratio == 1

print("recovered 0x855b8 global-gate vectors: ok")
