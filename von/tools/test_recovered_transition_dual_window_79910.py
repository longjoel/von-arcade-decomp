#!/usr/bin/env python3
"""Check the dual-window route at i960 0x79910."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_dual_window_79910.c"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_uint32),
                ("status", ctypes.c_uint32),
                ("selector", ctypes.c_uint32),
                ("transition", ctypes.c_uint32),
                ("action", ctypes.c_uint32),
                ("target", ctypes.c_uint32)]


def values(plan):
    return (plan.route, plan.status, plan.selector, plan.transition,
            plan.action, plan.target)


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libdual-window.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-Wall", "-Wextra",
                    "-Werror", str(SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_dual_window_79910
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32]
    function.restype = Plan

    assert values(function(3, 4, 2, 1, 0, 0x44, 0x19)) == (
        0, 1, 0x19, 3, 20, 0)
    assert values(function(3, 4, 2, 0, 0, 0x44, 0x19)) == (
        3, 0, 0x44, 0, 10, 0)
    assert values(function(1, 4, 2, 0, 0, 0x44, 0)) == (
        1, 0, 0x44, 0, 10, 0x78408)
    assert values(function(2, 4, 2, 0, 0, 0x44, 0)) == (
        2, 0, 0x44, 0, 5, 0x783c8)
    assert values(function(0, 0, 2, 0, 0, 0x55, 0)) == (
        3, 1, 0x55, 3, 20, 0)
    assert values(function(0, 4, 8, 0, 6, 0x55, 0)) == (
        3, 1, 0x55, 3, 20, 0)
    assert values(function(0, 4, 9, 0, 6, 0x55, 0)) == (
        3, 0, 0x55, 0, 10, 0)
    assert values(function(0, 4, 9, 1, 99, 0x55, 0)) == (
        3, 1, 0x55, 3, 20, 0)

print("recovered 0x79910 dual-window vectors: ok")
