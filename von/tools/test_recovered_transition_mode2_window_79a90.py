#!/usr/bin/env python3
"""Check the mode-2 timing-window route at i960 0x79a90."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_mode2_window_79a90.c"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32),
                ("initial_status", ctypes.c_uint32),
                ("status", ctypes.c_uint32),
                ("selector", ctypes.c_uint32),
                ("transition", ctypes.c_uint32),
                ("action", ctypes.c_uint32),
                ("target", ctypes.c_uint32)]


def values(plan):
    return (plan.route, plan.initial_status, plan.status, plan.selector,
            plan.transition, plan.action, plan.target)


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libmode2-window.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-Wall", "-Wextra",
                    "-Werror", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_mode2_window_79a90
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32]
    function.restype = Plan

    assert values(function(1, 1, 2, 0, 0, 0x44, 0)) == (
        0, 1, 0, 0x44, 0, 10, 0x78408)
    assert values(function(2, 0, 2, 0, 0, 0x44, 0)) == (
        1, 0, 0, 0x44, 0, 5, 0x783c8)
    assert values(function(3, 0x4, 2, 1, 0, 0, 0x19)) == (
        3, 0, 1, 0x19, 3, 20, 0)
    assert values(function(0, 0, 2, 0, 0, 0x55, 0)) == (
        2, 0, 1, 0x55, 3, 20, 0)
    assert values(function(0, 0, 8, 0, 6, 0, 0)) == (
        2, 0, 1, 0, 3, 20, 0)
    assert values(function(0, 4, 9, 0, 6, 0, 0)) == (
        2, 0, 0, 0, 0, 10, 0)

print("recovered 0x79a90 mode-2-window vectors: ok")
