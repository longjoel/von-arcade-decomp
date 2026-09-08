#!/usr/bin/env python3
"""Check the state-handler table at i960 0x82800."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_handler_dispatch_82800.c"


class Plan(ctypes.Structure):
    _fields_ = [("dispatched", ctypes.c_uint32),
                ("target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-handler-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_handler_dispatch_82800
    function.argtypes = [ctypes.c_uint32]
    function.restype = Plan

    expected = [0x82840, 0x82874, 0x8288C, 0x828A4, 0x828BC,
                0x828D4, 0x828F0, 0x8293C, 0x828E8, 0x82950]
    for selector, target in enumerate(expected):
        result = function(selector)
        assert (result.dispatched, result.target) == (1, target)
    assert function(10).dispatched == 0
    assert function(0xFFFFFFFF).dispatched == 0

print("recovered 0x82800 state-handler dispatch vectors: ok")
