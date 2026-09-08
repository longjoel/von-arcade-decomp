#!/usr/bin/env python3
"""Check scheduler handler 32 at i960 0x82d18."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_handler_82d18.c"


class Plan(ctypes.Structure):
    _fields_ = [("write_504d98", ctypes.c_uint32),
                ("value_504d98", ctypes.c_uint32),
                ("write_504d80", ctypes.c_uint32),
                ("value_504d80", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libscheduler-handler-32.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_handler_82d18
    function.argtypes = [ctypes.c_uint32]
    function.restype = Plan

    assert (function(8).write_504d98, function(8).value_504d98,
            function(8).value_504d80) == (1, 3, 20)
    assert (function(7).write_504d98, function(7).value_504d80) == (0, 8)
    assert function(0xffffffff).value_504d80 == 8

print("recovered 0x82d18 scheduler-handler vectors: ok")
