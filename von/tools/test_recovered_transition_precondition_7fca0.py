#!/usr/bin/env python3
"""Check the precondition classifier at i960 0x7fca0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_precondition_7fca0.c"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_int),
                ("accepted", ctypes.c_uint32),
                ("normalized_172", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-precondition.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_precondition_7fca0
    function.argtypes = [ctypes.c_uint16, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan

    assert function(1, 0, 6).route == 2
    assert function(14, 6, 6).route == 2
    assert function(14, 5, 6).accepted == 0
    assert function(0, 0, 6).accepted == 0

    result = function(2, 0, 0)
    assert (result.route, result.accepted, result.normalized_172) == (1, 1, 0x20000)
    assert function(0, 0, 0).accepted == 0

print("recovered 0x7fca0 precondition vectors: ok")
