#!/usr/bin/env python3
"""Check the state-action table at i960 0x82040."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_action_dispatch_82040.c"


class Plan(ctypes.Structure):
    _fields_ = [("dispatched", ctypes.c_uint32),
                ("target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-action-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_action_dispatch_82040
    function.argtypes = [ctypes.c_uint32]
    function.restype = Plan

    expected = [0x82088, 0x820cc, 0x82120, 0x8218c, 0x82248,
                0x82330, 0x823cc, 0x824b8, 0x82534, 0x825c0]
    for state, target in enumerate(expected):
        result = function(state)
        assert (result.dispatched, result.target) == (1, target)
    assert function(10).dispatched == 0
    assert function(0xffffffff).dispatched == 0

print("recovered 0x82040 state-action dispatch vectors: ok")
