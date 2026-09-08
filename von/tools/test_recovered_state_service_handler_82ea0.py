#!/usr/bin/env python3
"""Check the service handler at i960 0x82ea0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_service_handler_82ea0.c"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32),
                ("downstream_value", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-service-handler-82ea0.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_service_handler_82ea0
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan

    assert (function(4, 3).route, function(4, 3).downstream_value) == (1, 3)
    assert (function(5, 3).route, function(5, 3).downstream_value) == (2, 6)
    assert function(4, 2).route == 0
    assert function(5, 2).route == 0
    assert function(0, 3).route == 0
    assert function(6, 3).route == 0

print("recovered 0x82ea0 service-handler vectors: ok")
