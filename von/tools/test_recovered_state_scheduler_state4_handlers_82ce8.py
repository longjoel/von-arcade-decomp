#!/usr/bin/env python3
"""Check state-4 scheduler handlers at i960 0x82ce8 and 0x82d04."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_state4_handlers_82ce8.c"


class Plan(ctypes.Structure):
    _fields_ = [("handled", ctypes.c_uint32),
                ("value_504d98", ctypes.c_uint32),
                ("write_504d80", ctypes.c_uint32),
                ("value_504d80", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libscheduler-state4.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_state4_handler
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan

    assert (function(0x82CE8, 4).value_504d98,
            function(0x82CE8, 4).value_504d80) == (3, 28)
    assert function(0x82CE8, 3).value_504d98 == 2
    assert function(0x82CE8, 3).write_504d80 == 0
    assert function(0x82D04, 4).value_504d98 == 2
    assert function(0x82D04, 3).value_504d98 == 3
    assert function(0x82CB0, 4).handled == 0

print("recovered 0x82ce8/0x82d04 state-4 vectors: ok")
