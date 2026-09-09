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
                ("target", ctypes.c_uint32),
                ("handler_value_74", ctypes.c_uint32),
                ("handler_object_pointer", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-service-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_service_dispatch_82db0
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan

    expected = [0x82DF8, 0x82E0C, 0x82E40, 0x82E64, 0x82EA0,
                0x82ED4, 0x82F10, 0x82F6C, 0x82F84]
    for state, target in enumerate(expected):
        result = function(state, 0x7000 + state, 0x100000 + state)
        assert (result.route, result.target, result.handler_value_74,
                result.handler_object_pointer) == (0, target, 0x7000 + state,
                                                    0x100000 + state)
    high = function(9, 0x1234, 0x2000)
    assert (high.route, high.target, high.handler_value_74,
            high.handler_object_pointer) == (1, 0x82F90, 0x1234, 0x2000)
    high = function(0xFFFFFFFF, 0x5678, 0x3000)
    assert high.route == 1 and high.handler_object_pointer == 0x3000

print("recovered 0x82db0 state-service vectors: ok")
