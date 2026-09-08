#!/usr/bin/env python3
"""Check scheduler table handler 19 at i960 0x82c6c."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_handler_82c6c.c"


class Plan(ctypes.Structure):
    _fields_ = [("write_504d98", ctypes.c_uint32),
                ("value_504d98", ctypes.c_uint32),
                ("write_504d80", ctypes.c_uint32),
                ("value_504d80", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libscheduler-handler-19.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_handler_82c6c
    function.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_uint32]
    function.restype = Plan

    result = function(3, 0, 0)
    assert (result.write_504d98, result.value_504d98,
            result.write_504d80) == (1, 2, 0)
    assert function(4, 0x78000, 0).value_504d80 == 8
    assert function(4, 0x78001, 0).value_504d98 == 3
    assert function(4, 0x78001, 1).value_504d80 == 28
    assert function(4, 0x78001, 2).value_504d80 == 5

print("recovered 0x82c6c scheduler-handler vectors: ok")
