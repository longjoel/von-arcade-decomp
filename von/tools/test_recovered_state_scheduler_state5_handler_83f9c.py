#!/usr/bin/env python3
"""Check the state-5 handler at i960 0x83f9c."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_state5_handler_83f9c.c"

class Plan(ctypes.Structure):
    _fields_ = [("write_504e1c", ctypes.c_uint32),
                ("value_504e1c", ctypes.c_uint32),
                ("write_504d80", ctypes.c_uint32),
                ("value_504d80", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib83f9c.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_state5_handler_83f9c
    function.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    function.restype = Plan
    assert function(0x2, 1, 0, 100).value_504d80 == 26
    assert function(0x2, 0, 0, 100).value_504d80 == 37
    assert function(0x4, 0, 101, 100).value_504d80 == 39
    assert function(0x4, 0, 100, 100).value_504d80 == 37
    assert function(0x0, 1, 1000, -1000).value_504d80 == 37

print("recovered 0x83f9c state-5 vectors: ok")
