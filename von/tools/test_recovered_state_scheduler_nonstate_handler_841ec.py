#!/usr/bin/env python3
"""Check the non-state helper consumer at i960 0x841ec."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_nonstate_handler_841ec.c"

class Plan(ctypes.Structure):
    _fields_ = [("value_504d80", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib841ec.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_nonstate_handler_841ec
    function.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    assert function(3, 0x4, 2).value_504d80 == 33
    assert function(4, 0x4, 2).value_504d80 == 33
    assert function(5, 0x4, 2).value_504d80 == 32
    assert function(2, 0x2, 4).value_504d80 == 37
    assert function(2, 0x0, 0).value_504d80 == 33
    assert function(2, 0x0, 7).value_504d80 == 33

print("recovered 0x841ec non-state-handler vectors: ok")
