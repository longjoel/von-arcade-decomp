#!/usr/bin/env python3
"""Check the sibling timing-window route at i960 0x79cc0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_timing_window_variant_79cc0.c"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32),
                ("action", ctypes.c_uint32),
                ("target", ctypes.c_uint32),
                ("transition", ctypes.c_uint32)]


def values(plan):
    return plan.route, plan.action, plan.target, plan.transition


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtiming-window-variant.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-Wall", "-Wextra",
                    "-Werror", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_timing_window_variant_79cc0
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan

    assert values(function(1, 0, 0, 0, 0)) == (0, 10, 0x78408, 0)
    assert values(function(0, 1, 0, 0, 0)) == (1, 5, 0x783c8, 0)
    assert values(function(0, 0, 2, 0, 0)) == (2, 10, 0x78488, 0)
    assert values(function(0, 0, 4, 0, 0)) == (3, 5, 0x78448, 0)
    assert values(function(0, 0, 5, 1, 7)) == (4, 10, 0x78408, 2)
    assert values(function(0, 0, 5, 0, 7)) == (4, 10, 0x78408, 1)

print("recovered 0x79cc0 timing-window vectors: ok")
