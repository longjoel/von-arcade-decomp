#!/usr/bin/env python3
"""Check the state-8 action route at i960 0x78790."""

import ctypes
import pathlib
import struct
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state8_action_route_78790.c"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_int),
                ("status_write", ctypes.c_uint32)]


def bits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate8-route.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-lm", "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state8_action_route_78790
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan

    result = function(bits(4.0), bits(5.0), 0, 5)
    assert (result.route, result.status_write) == (2, 0)
    result = function(bits(6.0), bits(5.0), 0, 5)
    assert (result.route, result.status_write) == (1, 0)
    result = function(bits(6.0), bits(5.0), 1, 4)
    assert (result.route, result.status_write) == (3, 0)
    result = function(bits(6.0), bits(5.0), 1, 5)
    assert (result.route, result.status_write) == (4, 0)
    result = function(bits(float("nan")), bits(5.0), 1, 5)
    assert (result.route, result.status_write) == (0, 1)

print("recovered 0x78790 state-8 action vectors: ok")
