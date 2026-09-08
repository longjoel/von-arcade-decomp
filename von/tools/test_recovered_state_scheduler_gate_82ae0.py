#!/usr/bin/env python3
"""Check the recoverable gate at i960 0x82ae0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_gate_82ae0.c"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32),
                ("ran_timing_selector", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libscheduler-gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_gate_82ae0
    function.argtypes = [ctypes.c_uint32] * 6
    function.restype = Plan

    base = (10, 20, 4, 5, 3, 0)
    assert (function(*base).route, function(*base).ran_timing_selector) == (1, 1)
    assert function(21, 20, 4, 5, 3, 0).route == 0
    assert function(10, 20, 3, 5, 3, 0).route == 0
    assert function(10, 20, 4, 6, 3, 0).route == 0
    assert function(10, 20, 4, 5, 8, 5).route == 2
    assert function(10, 20, 4, 5, 8, 4).route == 0
    assert function(10, 20, 4, 5, 7, 5).route == 1

print("recovered 0x82ae0 scheduler-gate vectors: ok")
