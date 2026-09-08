#!/usr/bin/env python3
"""Check the service handler at i960 0x82e40."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_service_handler_82e40.c"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32),
                ("downstream_value", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-service-handler.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_service_handler_82e40
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan

    assert function(0, 3).route == 0
    assert function(3, 3).route == 0
    assert (function(4, 3).route, function(4, 3).downstream_value) == (1, 2)
    assert (function(4, 2).route, function(4, 2).downstream_value) == (2, 5)
    assert function(4, 0xffffffff).downstream_value == 5

print("recovered 0x82e40 service-handler vectors: ok")
