#!/usr/bin/env python3
"""Check converted-threshold/status dispatch at i960 0x7f364."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_threshold_status_dispatch_7f364.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "current_status", "normalized_index", "below_converted_threshold",
        "control_value", "callback_gate", "threshold_gate_passed",
        "table_target", "published_status", "control_destination",
        "callback_target", "callback_argument", "action_destination",
        "action_value", "target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-threshold-status.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_threshold_status_dispatch_7f364
    function.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(Plan)]
    function.restype = None

    expected = [(0x7f3dc, 1), (0x7f404, 2), (0x7f40c, 3),
                (0x7f41c, 4), (0x7f428, 12), (0x7f428, 13),
                (0x7f428, 14), (0x7f428, 15), (0x7f428, 16),
                (0x7f428, 17), (0x7f3ec, 2), (0x7f3f4, 3)]
    for index, (target, status) in enumerate(expected):
        plan = Plan()
        function(index + 8, 1, 0x55, 1, 0xcafe, ctypes.byref(plan))
        assert (plan.table_target, plan.published_status, plan.target,
                plan.control_value, plan.control_destination) == (
            target, status, 0x7f448, 0x55, 0x504da0)
        assert (plan.callback_target, plan.callback_argument,
                plan.action_destination, plan.action_value) == (
            0x79050, 0xcafe, 0x504db8, 30)

    plan = Plan()
    function(8, 0, 0x66, 1, 0, ctypes.byref(plan))
    assert (plan.threshold_gate_passed, plan.control_value,
            plan.callback_target, plan.action_value, plan.target) == (
        0, 0x66, 0, 0, 0x7f448)

    plan = Plan()
    function(7, 1, 0, 0, 0, ctypes.byref(plan))
    assert (plan.normalized_index, plan.table_target,
            plan.published_status) == (0xffffffff, 0x7f428, 7)

print("recovered 0x7f364 threshold-status vectors: ok")
