#!/usr/bin/env python3
"""Check the sibling early scheduler gate at i960 0x83310."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_early_gate_83310.c"


class Plan(ctypes.Structure):
    _fields_ = [("terminal", ctypes.c_uint32),
                ("write_504d98", ctypes.c_uint32),
                ("value_504d98", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libscheduler-early-gate-83310.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_early_gate_83310
    function.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_uint32]
    function.restype = Plan

    for related in (19, 20):
        result = function(149, related, 0x1234)
        assert (result.terminal, result.write_504d98,
                result.value_504d98) == (1, 1, 0x1234)
    assert function(150, 19, 0x1234).terminal == 0
    assert function(149, 18, 0x1234).terminal == 0

print("recovered 0x83310 early-gate vectors: ok")
