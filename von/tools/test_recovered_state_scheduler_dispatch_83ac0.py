#!/usr/bin/env python3
"""Check the state/timing dispatcher at i960 0x83ac0."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_dispatch_83ac0.c"

class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32), ("terminal", ctypes.c_uint32),
                ("write_504d80", ctypes.c_uint32), ("value_504d80", ctypes.c_uint32),
                ("write_504d98", ctypes.c_uint32), ("value_504d98", ctypes.c_uint32),
                ("write_504e1c", ctypes.c_uint32), ("value_504d8c", ctypes.c_uint32),
                ("value_504d90", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib83ac0.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_dispatch_83ac0
    function.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_uint32,
                         ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
                         ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    assert function(149, 19, 5, 0, 100, 0, 0, 77).value_504d98 == 77
    assert function(150, 19, 5, 99, 100, 0, 0, 77).route == 1
    assert function(150, 19, 5, -1, -2, 0, 0, 77).value_504d80 == 18
    assert function(150, 0, 5, 100, 100, 2, 0, 77).route == 4
    assert function(150, 0, 5, 100, 100, 3, 0, 77).value_504d80 == 26
    assert function(150, 0, 4, 100, 100, 4, 0x2, 77).value_504d80 == 26
    assert function(150, 0, 4, 100, 100, -1, 0x4, 77).value_504d80 == 28
    result = function(150, 0, 4, 100, 100, 4, 0, 77)
    assert (result.value_504d80, result.value_504d8c, result.value_504d90) == (21, 77, 15)

print("recovered 0x83ac0 scheduler-dispatch vectors: ok")
