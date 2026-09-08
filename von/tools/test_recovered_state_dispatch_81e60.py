#!/usr/bin/env python3
"""Check the state dispatcher at i960 0x81e60."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_dispatch_81e60.c"


class Plan(ctypes.Structure):
    _fields_ = [("startup_call_84d90", ctypes.c_uint32),
                ("dispatched", ctypes.c_uint32),
                ("target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-dispatch-81e60.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_dispatch_81e60
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int16,
                         ctypes.c_uint32]
    function.restype = Plan

    result = function(4, 10, 0, 0)
    assert (result.startup_call_84d90, result.dispatched,
            result.target) == (1, 1, 0x81edc)
    assert function(0, 0, 0, 9).target == 0x81f48
    assert function(4, 10, 1, 0).dispatched == 0
    assert function(4, 10, 0, 10).dispatched == 0

print("recovered 0x81e60 state-dispatch vectors: ok")
