#!/usr/bin/env python3
"""Check modulo-8 service handlers at i960 0x82ed4 and 0x82f10."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_service_mod8_handlers_82ed4.c"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32),
                ("downstream_value", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-service-mod8.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_service_mod8_handler
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan

    assert function(0x82ED4, 2, 3).downstream_value == 3
    assert function(0x82ED4, 1, 2).route == 0
    assert function(0x82ED4, 6, 0).downstream_value == 4
    assert function(0x82ED4, 5, 3).route == 0
    assert function(0x82F10, 4, 3).downstream_value == 3
    assert function(0x82F10, 5, 3).downstream_value == 3
    assert function(0x82F10, 7, 3).downstream_value == 6
    assert function(0x82F10, 7, 2).route == 0
    assert function(0x82F10, 0, 3).route == 0

print("recovered 0x82ed4/0x82f10 modulo-8 vectors: ok")
