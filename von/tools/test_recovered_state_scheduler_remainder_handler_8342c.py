#!/usr/bin/env python3
"""Check the remainder/mode handler at i960 0x8342c."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_remainder_handler_8342c.c"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32),
                ("value_504d80", ctypes.c_uint32),
                ("value_504d8c", ctypes.c_uint32),
                ("value_504d90", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libscheduler-remainder-handler.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_remainder_handler_8342c
    function.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan

    result = function(5, 0, 77)
    assert (result.route, result.value_504d80,
            result.value_504d8c, result.value_504d90) == (1, 21, 77, 15)
    assert function(4, 0x2, 77).value_504d80 == 26
    assert function(1, 0x4, 77).value_504d80 == 28
    assert function(-1, 0x4, 77).route == 0
    assert function(0, 0x4, 77).route == 0
    assert function(4, 0, 77).route == 0
    assert function(2, 0, 77).route == 0

print("recovered 0x8342c remainder-handler vectors: ok")
