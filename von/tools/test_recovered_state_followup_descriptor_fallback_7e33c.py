#!/usr/bin/env python3
"""Check the 0x7e390 fallback tail at i960 0x7e33c."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_descriptor_fallback_7e33c.c"


class Plan(ctypes.Structure):
    _fields_ = [("helper_target", ctypes.c_uint32),
                ("helper_result", ctypes.c_uint32),
                ("restored_control", ctypes.c_uint32),
                ("restored_selector", ctypes.c_uint32),
                ("restored_action", ctypes.c_uint32),
                ("writes_status", ctypes.c_uint32),
                ("status_destination", ctypes.c_uint32),
                ("status_value", ctypes.c_uint32),
                ("control_destination", ctypes.c_uint32),
                ("selector_destination", ctypes.c_uint32),
                ("action_destination", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-descriptor.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_descriptor_fallback_7e33c
    function.argtypes = [ctypes.c_uint32] * 4 + [ctypes.c_int32,
                                                  ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(0, 1, 2, 3, 0, ctypes.byref(plan))
    assert plan.helper_target == 0x7E390
    assert (plan.restored_control, plan.restored_selector,
            plan.restored_action) == (1, 2, 3)
    assert (plan.control_destination, plan.selector_destination,
            plan.action_destination) == (0x504D9C, 0x504DA0, 0x504DB4)
    plan = Plan()
    function(1, 1, 2, 3, -16, ctypes.byref(plan))
    assert (plan.writes_status, plan.status_destination,
            plan.status_value) == (1, 0x504D94, 4)
    plan = Plan()
    function(1, 1, 2, 3, -15, ctypes.byref(plan))
    assert plan.writes_status == 0

print("PASS: 0x7e33c descriptor-fallback vectors")
