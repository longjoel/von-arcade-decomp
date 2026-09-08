#!/usr/bin/env python3
"""Check the branch-specific transition route at i960 0x80710."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_route_80710.c"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_int),
                ("band_index", ctypes.c_uint32),
                ("adjusted_current", ctypes.c_int32),
                ("raw_difference", ctypes.c_int32),
                ("status_504db8", ctypes.c_uint32),
                ("threshold_call_82800", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-route-80710.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_route_80710
    function.argtypes = [ctypes.c_int32, ctypes.c_int16, ctypes.c_int16,
                         ctypes.c_float, ctypes.c_float]
    function.restype = Plan

    result = function(1, 100, 100, 5.0, 4.0)
    assert (result.route, result.adjusted_current,
            result.raw_difference, result.band_index,
            result.status_504db8, result.threshold_call_82800) == (
                1, 100 - 0x6800, 0x6800, 4, 10, 1)
    result = function(9, 100, 100, 4.0, 4.0)
    assert (result.adjusted_current, result.raw_difference,
            result.band_index, result.threshold_call_82800) == (
                100 + 0x6800, -0x6800, 5, 0)
    assert function(10, 100, 100, 1.0, 0.0).route == 0

print("recovered 0x80710 transition-route vectors: ok")
