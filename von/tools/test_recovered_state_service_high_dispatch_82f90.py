#!/usr/bin/env python3
"""Check high-state normalization and dispatch at i960 0x82f90."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_service_high_dispatch_82f90.c"


class Plan(ctypes.Structure):
    _fields_ = [("remainder", ctypes.c_int32),
                ("dispatched", ctypes.c_uint32),
                ("target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-service-high-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_service_high_dispatch_82f90
    function.argtypes = [ctypes.c_int32]
    function.restype = Plan

    expected = [0x82FDC, 0x82FF4, 0x8300C, 0x83024,
                0x8303C, 0x83050, 0x83058, 0x8307C]
    for value, target in enumerate(expected[:4]):
        result = function(value)
        assert (result.remainder, result.dispatched, result.target) == (value, 1, target)
    assert function(4).remainder == 0
    assert function(4).target == expected[0]
    assert (function(8).remainder, function(8).target) == (0, expected[0])
    assert function(-1).remainder == -1
    assert function(-1).dispatched == 0

print("recovered 0x82f90 high-dispatch vectors: ok")
