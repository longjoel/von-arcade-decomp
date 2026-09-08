#!/usr/bin/env python3
"""Check the quadword/status tail at i960 0x84018."""

import ctypes
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_quadword_tail_84018.c"

class Plan(ctypes.Structure):
    _fields_ = [("value_504d80", ctypes.c_uint32),
                ("value_504d84", ctypes.c_uint32),
                ("value_504d88", ctypes.c_uint32),
                ("value_504d8c", ctypes.c_uint32),
                ("value_504d90", ctypes.c_uint32)]

with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "lib84018.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_quadword_tail_84018
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan
    result = function(26, 0, 2, 3, 4)
    assert (result.value_504d80, result.value_504d84,
            result.value_504d88, result.value_504d8c, result.value_504d90) == (26, 2, 3, 4, 30)
    assert function(37, 4, 2, 3, 4).value_504d90 == 30
    assert function(36, 4, 2, 3, 4).value_504d90 == 15
    assert function(7, 0, 0xdeadbeef, 9, 11).value_504d84 == 0xdeadbeef

print("recovered 0x84018 quadword-tail vectors: ok")
