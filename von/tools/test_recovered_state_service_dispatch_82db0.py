#!/usr/bin/env python3
"""Check the state-service dispatcher at i960 0x82db0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_service_dispatch_82db0.c"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32),
                ("target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-service-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_service_dispatch_82db0
    function.argtypes = [ctypes.c_uint32]
    function.restype = Plan

    expected = [0x82DF8, 0x82E0C, 0x82E40, 0x82E64, 0x82EA0,
                0x82ED4, 0x82F10, 0x82F6C, 0x82F84]
    for state, target in enumerate(expected):
        result = function(state)
        assert (result.route, result.target) == (0, target)
    assert (function(9).route, function(9).target) == (1, 0x82F90)
    assert function(0xFFFFFFFF).route == 1

print("recovered 0x82db0 state-service vectors: ok")
