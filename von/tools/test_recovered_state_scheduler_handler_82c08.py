#!/usr/bin/env python3
"""Check scheduler table handler 6 at i960 0x82c08."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_handler_82c08.c"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32),
                ("state_504d7c", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libscheduler-handler-6.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_handler_82c08
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan

    assert (function(0, 4).route, function(0, 4).state_504d7c) == (0, 7)
    assert (function(1, 4).route, function(1, 4).state_504d7c) == (1, 4)
    assert (function(0xffffffff, 9).route, function(0xffffffff, 9).state_504d7c) == (1, 9)

print("recovered 0x82c08 scheduler-handler vectors: ok")
