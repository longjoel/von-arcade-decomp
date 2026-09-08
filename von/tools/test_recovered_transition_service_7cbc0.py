#!/usr/bin/env python3
"""Check the bounded transition service at i960 0x7cbc0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_service_7cbc0.c"


class State(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32),
                ("selector", ctypes.c_uint32),
                ("status", ctypes.c_uint32),
                ("transition", ctypes.c_uint32),
                ("action", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-service.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_service_7cbc0
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.POINTER(State)]
    function.restype = None

    result = State()
    function(0, 1, 4, 0x1234, ctypes.byref(result))
    assert (result.route, result.selector, result.status,
            result.transition, result.action) == (0, 0, 0, 0, 0)

    function(1, 0, 4, 0x1234, ctypes.byref(result))
    assert (result.route, result.selector, result.status,
            result.transition, result.action) == (1, 0x1234, 0, 0, 10)

    function(1, 1, 2, 0x5678, ctypes.byref(result))
    assert (result.route, result.selector, result.status,
            result.transition, result.action) == (1, 0x5678, 1, 2, 25)

    function(1, 1, 4, 0x5678, ctypes.byref(result))
    assert (result.route, result.selector, result.status,
            result.transition, result.action) == (1, 0x5678, 1, 3, 25)

print("recovered 0x7cbc0 transition-service vectors: ok")
