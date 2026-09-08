#!/usr/bin/env python3
"""Check the wrapper at i960 0x842d0."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_wrapper_842d0.c"

class Plan(ctypes.Structure):
    _fields_ = [("skipped", ctypes.c_uint32),
                ("call_84330", ctypes.c_uint32),
                ("call_85c00", ctypes.c_uint32),
                ("call_848d0", ctypes.c_uint32),
                ("call_84b10", ctypes.c_uint32),
                ("call_858f0", ctypes.c_uint32),
                ("call_85b00", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib842d0.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_wrapper_842d0
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    assert function(1, 0).skipped == 1
    result = function(0, 0x100)
    assert (result.call_84330, result.call_85c00, result.call_848d0,
            result.call_84b10, result.call_858f0, result.call_85b00) == (1, 1, 1, 1, 1, 1)
    assert function(0, 0x101).call_85b00 == 0

print("recovered 0x842d0 wrapper vectors: ok")
