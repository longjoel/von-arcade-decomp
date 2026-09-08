#!/usr/bin/env python3
"""Check the common scheduler tail at i960 0x82d74."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_tail_82d74.c"


class Plan(ctypes.Structure):
    _fields_ = [("value_504d80", ctypes.c_uint32),
                ("value_504d84", ctypes.c_uint32),
                ("value_504d88", ctypes.c_uint32),
                ("value_504d8c", ctypes.c_uint32),
                ("write_504d90", ctypes.c_uint32),
                ("value_504d90", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libscheduler-tail.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_tail_82d74
    function.argtypes = [ctypes.c_uint32] * 4
    function.restype = Plan

    for status in range(7):
        result = function(status, 9, 10, 11)
        assert (result.value_504d80, result.value_504d84,
                result.write_504d90, result.value_504d90) == (status, 0, 1, 15)
    assert function(7, 9, 10, 11).write_504d90 == 0
    assert function(8, 9, 10, 11).value_504d90 == 15
    assert function(9, 9, 10, 11).write_504d90 == 0

print("recovered 0x82d74 scheduler-tail vectors: ok")
