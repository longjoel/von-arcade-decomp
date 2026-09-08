#!/usr/bin/env python3
"""Check the ratio/status prefix at i960 0x83348."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_scheduler_ratio_prefix_83310.c"


class Plan(ctypes.Structure):
    _fields_ = [("value_504e1c", ctypes.c_uint32),
                ("mode_504e30", ctypes.c_uint32),
                ("mode_changed", ctypes.c_uint32),
                ("random_table_dispatch", ctypes.c_uint32),
                ("random_table_target", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libscheduler-ratio-prefix.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_scheduler_ratio_prefix_83310
    function.argtypes = [ctypes.c_double] + [ctypes.c_uint32] * 3
    function.restype = Plan

    result = function(0.9, 0x4, 5, 2)
    assert (result.value_504e1c, result.mode_504e30,
            result.mode_changed, result.random_table_dispatch) == (1, 4, 0, 0)
    result = function(0.95, 0x4, 4, 2)
    assert (result.mode_504e30, result.mode_changed,
            result.random_table_dispatch) == (0, 1, 0)
    result = function(0.95, 0x4, 5, 2)
    assert (result.mode_504e30, result.random_table_target) == (0, 0x833f8)
    assert function(0.95, 0x0, 5, 4).random_table_target == 0x83418
    assert function(float("nan"), 0x4, 5, 0).mode_changed == 1

print("recovered 0x83310 ratio-prefix vectors: ok")
