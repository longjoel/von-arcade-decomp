#!/usr/bin/env python3
"""Check result/status routing at i960 0x7d9b4."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_result_select_7d9b4.c"


class Plan(ctypes.Structure):
    _fields_ = [("result_table", ctypes.c_uint32),
                ("result_index", ctypes.c_uint32),
                ("result_value", ctypes.c_uint32),
                ("status_value", ctypes.c_uint32),
                ("used_class_table", ctypes.c_uint32),
                ("used_threshold_table", ctypes.c_uint32),
                ("used_literal_fallback", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-result.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_result_select_7d9b4
    function.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(9, 1, 0, 0x111, 0x222, ctypes.byref(plan))
    assert (plan.result_table, plan.result_index, plan.result_value,
            plan.status_value, plan.used_class_table) == (0x72AB0, 1, 0x111, 40, 1)
    plan = Plan()
    function(9, 0, 1, 0x111, 0x222, ctypes.byref(plan))
    assert (plan.result_table, plan.result_index, plan.result_value, plan.status_value,
            plan.used_threshold_table) == (0x72630, 0, 0x222, 40, 1)
    plan = Plan()
    function(9, 0, 0, 0x111, 0x222, ctypes.byref(plan))
    assert (plan.status_value, plan.used_literal_fallback) == (20, 1)

print("PASS: 0x7d9b4 result/status selector vectors")
