#!/usr/bin/env python3
"""Check the five callback accumulators at i960 0x859ec."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_callback_accumulator_update_859ec.c"

class Plan(ctypes.Structure):
    _fields_ = [("handler_index", ctypes.c_uint32),
                ("value_509b90", ctypes.c_int32),
                ("value_503a78", ctypes.c_int32),
                ("current_accumulator", ctypes.c_int32),
                ("divisor", ctypes.c_int32),
                ("quotient", ctypes.c_int32),
                ("unclamped_value", ctypes.c_int32),
                ("updated_accumulator", ctypes.c_int32),
                ("destination_address", ctypes.c_uint32),
                ("clamped", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib859ec.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_callback_accumulator_update_859ec
    function.argtypes = [ctypes.c_uint32, ctypes.c_int32,
                         ctypes.c_int32, ctypes.c_int32]
    function.restype = Plan
    for index in range(5):
        result = function(index, 100, 9, 2)
        assert (result.divisor, result.quotient, result.updated_accumulator,
                result.destination_address, result.clamped) == (10, 10, 12,
                                                                 0x509b24 + index * 4, 0)
    result = function(0, 1000, 9, 9950)
    assert (result.unclamped_value, result.updated_accumulator, result.clamped) == (10050, 10000, 1)
    assert function(5, 100, 9, 0).destination_address == 0

print("recovered 0x859ec accumulator vectors: ok")
