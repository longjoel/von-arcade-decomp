#!/usr/bin/env python3
"""Check the early scheduler gate at i960 0x83110."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_early_gate_83110.c"


class Plan(ctypes.Structure):
    _fields_ = [("terminal", ctypes.c_uint32),
                ("write_504d98", ctypes.c_uint32),
                ("value_504d98", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libscheduler-early-gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_early_gate_83110
    function.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_uint32]
    function.restype = Plan

    for related in (19, 20):
        result = function(149, related, 77)
        assert (result.terminal, result.write_504d98,
                result.value_504d98) == (1, 1, 77)
        assert function(150, related, 77).terminal == 0
    assert function(149, 18, 77).terminal == 0
    assert function(149, 21, 77).terminal == 0
    assert function(-1, 19, 77).value_504d98 == 77

print("recovered 0x83110 early-gate vectors: ok")
