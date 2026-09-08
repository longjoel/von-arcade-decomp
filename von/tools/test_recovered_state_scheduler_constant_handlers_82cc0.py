#!/usr/bin/env python3
"""Check constant scheduler handlers at i960 0x82cc0-0x82ce8."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_constant_handlers_82cc0.c"


class Plan(ctypes.Structure):
    _fields_ = [("handled", ctypes.c_uint32),
                ("value_504d98", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libscheduler-constant-handlers.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_constant_handler_82cc0
    function.argtypes = [ctypes.c_uint32]
    function.restype = Plan

    expected = {0x82CC0: 3, 0x82CC8: 1, 0x82CD0: 13,
                0x82CD8: 14, 0x82CE0: 15}
    for entry, value in expected.items():
        result = function(entry)
        assert (result.handled, result.value_504d98) == (1, value)
    assert function(0x82CB0).handled == 0
    assert function(0x82CE8).handled == 0

print("recovered 0x82cc0 constant-handler vectors: ok")
