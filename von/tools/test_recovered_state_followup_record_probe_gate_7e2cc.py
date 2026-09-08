#!/usr/bin/env python3
"""Check the record-probe gate at i960 0x7e2cc."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_record_probe_gate_7e2cc.c"


class Plan(ctypes.Structure):
    _fields_ = [("global_5770f0", ctypes.c_uint32),
                ("saved_control", ctypes.c_uint32),
                ("saved_selector", ctypes.c_uint32),
                ("saved_action", ctypes.c_uint32),
                ("published_action", ctypes.c_uint32),
                ("record_slot", ctypes.c_uint32),
                ("record_halfword_above_threshold", ctypes.c_uint32),
                ("global_gate_passed", ctypes.c_uint32),
                ("selector_excluded", ctypes.c_uint32),
                ("callback_succeeded", ctypes.c_uint32),
                ("callback_g1", ctypes.c_uint32),
                ("callback_g2", ctypes.c_uint32),
                ("enters_success_route", ctypes.c_uint32),
                ("continues_to_7e33c", ctypes.c_uint32),
                ("callback_target", ctypes.c_uint32),
                ("selector_destination", ctypes.c_uint32),
                ("selector_value", ctypes.c_uint32),
                ("control_destination", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-probe.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_record_probe_gate_7e2cc
    function.argtypes = [ctypes.c_uint32] * 8 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(10, 0x55, 3, 1, 0x12, 0x34, 0x56, 1, ctypes.byref(plan))
    assert (plan.saved_control, plan.saved_selector, plan.saved_action,
            plan.published_action, plan.record_slot,
            plan.record_halfword_above_threshold) == (0x12, 0x34, 0x56,
                                                       0xffffffff, 3, 1)
    assert (plan.global_gate_passed, plan.selector_excluded,
            plan.callback_succeeded, plan.enters_success_route,
            plan.continues_to_7e33c) == (1, 0, 1, 1, 0)
    assert plan.callback_target == 0x816D0
    assert (plan.callback_g1, plan.callback_g2) == (0x55, 3)
    assert (plan.selector_destination, plan.selector_value,
            plan.control_destination, plan.control_value) == (0x504DA0, 0x55, 0x504D9C, 1)
    for args in ((9, 0x55, 3, 1, 0, 0, 0, 1),
                 (10, 0x55, 3, 0, 0, 0, 0, 1),
                 (10, 0xAF, 3, 1, 0, 0, 0, 1),
                 (10, 0xA9, 3, 1, 0, 0, 0, 1),
                 (10, 0x55, 3, 1, 0, 0, 0, 0)):
        plan = Plan()
        function(*args, ctypes.byref(plan))
        assert plan.enters_success_route == 0
        assert plan.continues_to_7e33c == 1

print("PASS: 0x7e2cc record-probe-gate vectors")
