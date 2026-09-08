#!/usr/bin/env python3
"""Check the pure timing/override route at i960 0x78dec."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_packet_timing_route_78dec.c"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32),
                ("status", ctypes.c_uint32),
                ("transition", ctypes.c_uint32),
                ("action", ctypes.c_uint32),
                ("action_target", ctypes.c_uint32),
                ("selector_value", ctypes.c_uint32)]


def values(plan):
    return (plan.route, plan.status, plan.transition, plan.action,
            plan.action_target, plan.selector_value)


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libgeometry-packet-timing.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-Wall", "-Wextra",
                    "-Werror", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_geometry_packet_timing_route_78dec
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan

    result = function(0, 0, 2, 0, 0, 19)
    assert values(result) == (0, 1, 2, 25, 0, 19)

    result = function(0, 0, 4, 1, 0, 19)
    assert values(result) == (0, 1, 3, 25, 0, 23)

    result = function(1, 1, 2, 0, 0, 0)
    assert values(result) == (1, 0, 0, 10, 0x78408, 0)

    result = function(1, 2, 2, 0, 0, 0)
    assert values(result) == (2, 0, 0, 5, 0x783c8, 0)

    result = function(1, 0, 2, 0, 2, 0)
    assert values(result) == (3, 0, 0, 5, 0, 13)

    result = function(1, 0, 4, 1, 8, 19)
    assert values(result) == (4, 1, 3, 25, 0, 23)

print("recovered 0x78dec geometry-packet timing vectors: ok")
