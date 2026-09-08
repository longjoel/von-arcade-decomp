#!/usr/bin/env python3
"""Check the service handler at i960 0x82f6c."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_service_handler_82f6c.c"


class Plan(ctypes.Structure):
    _fields_ = [("accepted", ctypes.c_uint32),
                ("downstream_value", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-service-handler-82f6c.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_service_handler_82f6c
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan

    assert (function(4, 3).accepted, function(4, 3).downstream_value) == (1, 2)
    assert function(3, 3).accepted == 0
    assert function(4, 2).accepted == 0
    assert function(0, 0xffffffff).accepted == 0

print("recovered 0x82f6c service-handler vectors: ok")
