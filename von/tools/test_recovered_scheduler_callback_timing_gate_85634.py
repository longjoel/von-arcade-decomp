#!/usr/bin/env python3
"""Check the callback timing gate at i960 0x85634."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_callback_timing_gate_85634.c"

class Plan(ctypes.Structure):
    _fields_ = [("value_503a14", ctypes.c_int32),
                ("value_503a18", ctypes.c_int32),
                ("frame_quotient", ctypes.c_int32),
                ("frame_target", ctypes.c_int32),
                ("target_difference", ctypes.c_int32),
                ("value_5024e8", ctypes.c_uint32),
                ("remainder_300", ctypes.c_uint32),
                ("exits_to_85678", ctypes.c_uint32),
                ("forces_dimensions_1_1", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib85634.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_callback_timing_gate_85634
    function.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_uint32]
    function.restype = Plan
    result = function(96, 3, 191)
    assert (result.frame_quotient, result.frame_target,
            result.target_difference, result.remainder_300,
            result.exits_to_85678, result.forces_dimensions_1_1) == (2, 3, 0, 191, 0, 1)
    assert function(96, 23, 191).exits_to_85678 == 1
    assert function(96, 3, 90).exits_to_85678 == 1
    assert function(96, 3, 91).forces_dimensions_1_1 == 1

print("recovered 0x85634 timing-gate vectors: ok")
