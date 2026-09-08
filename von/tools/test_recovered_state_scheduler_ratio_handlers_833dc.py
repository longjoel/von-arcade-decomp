#!/usr/bin/env python3
"""Check ratio-table handlers at i960 0x833dc-0x83428."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_ratio_handlers_833dc.c"


class Plan(ctypes.Structure):
    _fields_ = [("handled", ctypes.c_uint32),
                ("status_write", ctypes.c_uint32),
                ("value_504d80", ctypes.c_uint32),
                ("calls_79d60", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libscheduler-ratio-handlers.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_ratio_handler_833dc
    function.argtypes = [ctypes.c_uint32]
    function.restype = Plan

    assert (function(0x833DC).handled, function(0x833DC).calls_79d60) == (1, 1)
    for entry in (0x833E8, 0x833F8):
        result = function(entry)
        assert (result.status_write, result.value_504d80) == (1, 28)
    assert function(0x83408).value_504d80 == 26
    assert function(0x83418).value_504d80 == 21
    assert function(0x83428).handled == 0

print("recovered 0x833dc ratio-handler vectors: ok")
