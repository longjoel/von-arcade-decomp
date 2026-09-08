#!/usr/bin/env python3
"""Check the counter update at i960 0x848d0."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_counter_update_848d0.c"

class Plan(ctypes.Structure):
    _fields_ = [("writes_509a6c", ctypes.c_uint32),
                ("continues_to_8490c", ctypes.c_uint32),
                ("value_509a6c", ctypes.c_int32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib848d0.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_counter_update_848d0
    function.argtypes = [ctypes.c_int32, ctypes.c_int32]
    function.restype = Plan
    assert (function(0, 0).value_509a6c, function(0, 0).writes_509a6c) == (1, 1)
    assert function(120, 0).value_509a6c == 0
    assert function(-1, 239).continues_to_8490c == 0
    assert function(-1, 240).continues_to_8490c == 1

print("recovered 0x848d0 counter-update vectors: ok")
