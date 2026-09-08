#!/usr/bin/env python3
"""Check the scheduler initializer at i960 0x84240."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_initializer_84240.c"

class Plan(ctypes.Structure):
    _fields_ = [("callback_target", ctypes.c_uint32),
                ("callback_g14", ctypes.c_uint32),
                ("value_504e1c", ctypes.c_uint32),
                ("value_504d80", ctypes.c_uint32),
                ("value_504d8c", ctypes.c_uint32),
                ("value_504d90", ctypes.c_uint32),
                ("value_504d9c", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib84240.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_initializer_84240
    function.restype = Plan
    result = function()
    assert (result.callback_target, result.callback_g14,
            result.value_504e1c, result.value_504d80,
            result.value_504d8c, result.value_504d90,
            result.value_504d9c) == (0x84290, 0, 1, 43, 0, 15, 7)

print("recovered 0x84240 initializer vectors: ok")
