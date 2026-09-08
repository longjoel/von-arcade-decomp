#!/usr/bin/env python3
"""Check the early gate at i960 0x83cc0."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_early_gate_83cc0.c"

class Plan(ctypes.Structure):
    _fields_ = [("terminal", ctypes.c_uint32),
                ("write_504d98", ctypes.c_uint32),
                ("value_504d98", ctypes.c_uint32),
                ("continues", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib83cc0-gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_early_gate_83cc0
    function.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_uint32]
    function.restype = Plan
    assert (function(149, 19, 77).terminal,
            function(149, 19, 77).value_504d98) == (1, 77)
    assert function(150, 19, 77).continues == 1
    assert function(149, 18, 77).continues == 1
    assert function(-1, 20, 0xdeadbeef).value_504d98 == 0xdeadbeef

print("recovered 0x83cc0 early-gate vectors: ok")
