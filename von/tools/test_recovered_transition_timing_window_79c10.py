#!/usr/bin/env python3
"""Check the timing-window exits at i960 0x79c10."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_timing_window_79c10.c"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32),
                ("status", ctypes.c_uint32),
                ("selector", ctypes.c_uint32),
                ("action", ctypes.c_uint32),
                ("target", ctypes.c_uint32)]


def values(plan):
    return plan.route, plan.status, plan.selector, plan.action, plan.target


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtiming-window.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-Wall", "-Wextra",
                    "-Werror", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_timing_window_79c10
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan

    assert values(function(0, 0x12)) == (0, 0, 0, 10, 0x78408)
    assert values(function(1, 0x12)) == (1, 0, 0, 0, 0x783c8)
    assert values(function(2, 0x3456)) == (2, 1, 0x3456, 10, 0x78408)

print("recovered 0x79c10 timing-window vectors: ok")
