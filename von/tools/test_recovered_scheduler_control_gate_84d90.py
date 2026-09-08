#!/usr/bin/env python3
"""Check the control/ABI gate at i960 0x84d90."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_scheduler_control_gate_84d90.c"

class Plan(ctypes.Structure):
    _fields_ = [("saved_g8", ctypes.c_uint32),
                ("restored_g8", ctypes.c_uint32),
                ("returns_immediately", ctypes.c_uint32),
                ("continues_to_84dc4", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib84d90.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_scheduler_control_gate_84d90
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    assert (function(0x1234, 1).returns_immediately,
            function(0x1234, 1).continues_to_84dc4) == (1, 0)
    result = function(0xdeadbeef, 0)
    assert (result.saved_g8, result.restored_g8,
            result.returns_immediately, result.continues_to_84dc4) == (0xdeadbeef, 0xdeadbeef, 0, 1)

print("recovered 0x84d90 control-gate vectors: ok")
