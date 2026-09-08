#!/usr/bin/env python3
"""Check the object gate at i960 0x855f8."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_callback_object_gate_855f8.c"

class Plan(ctypes.Structure):
    _fields_ = [("object_1d0", ctypes.c_int32),
                ("object_1d8", ctypes.c_int32),
                ("shifted_1d8", ctypes.c_int32),
                ("target_difference", ctypes.c_int32),
                ("value_5024e8", ctypes.c_uint32),
                ("remainder_300", ctypes.c_uint32),
                ("ratio_rejected", ctypes.c_uint32),
                ("remainder_checked", ctypes.c_uint32),
                ("forces_dimensions_1_1", ctypes.c_uint32),
                ("continues_to_85634", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib855f8.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_callback_object_gate_855f8
    function.argtypes = [ctypes.c_int32, ctypes.c_int32,
                         ctypes.c_int32, ctypes.c_uint32]
    function.restype = Plan
    result = function(10, 20, 30, 345)
    assert (result.shifted_1d8, result.remainder_300,
            result.ratio_rejected, result.remainder_checked,
            result.forces_dimensions_1_1, result.continues_to_85634) == (5, 45, 0, 0, 0, 1)
    result = function(10, 20, 46, 346)
    assert (result.remainder_300, result.remainder_checked,
            result.forces_dimensions_1_1) == (46, 1, 1)
    assert function(5, 20, 0, 0).ratio_rejected == 1
    assert function(10, 40, 0, 0).ratio_rejected == 1

print("recovered 0x855f8 object-gate vectors: ok")
