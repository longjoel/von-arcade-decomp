#!/usr/bin/env python3
"""Check the result status tail at i960 0x7fc24."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_result_status_tail_7fc24.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "current_status", "callback_gate", "related_pointer", "normalized_index",
        "table_target", "published_status", "callback_target",
        "callback_argument", "action_destination", "action_value", "target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-result-status-tail.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_result_status_tail_7fc24
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    expected = [(0x7fc24, 1), (0x7fc4c, 2), (0x7fc54, 3),
                (0x7fc64, 4), (0x7fc70, 12), (0x7fc70, 13),
                (0x7fc70, 14), (0x7fc70, 15), (0x7fc70, 16),
                (0x7fc70, 17), (0x7fc34, 2), (0x7fc3c, 3)]
    for index, (target, status) in enumerate(expected):
        plan = Plan()
        function(index + 8, 1, 0xcafe, ctypes.byref(plan))
        assert (plan.table_target, plan.published_status, plan.target) == (
            target, status, 0x7fc90)
        assert (plan.callback_target, plan.callback_argument,
                plan.action_value) == (0x79050, 0xcafe, 30)

    plan = Plan()
    function(7, 0, 0, ctypes.byref(plan))
    assert (plan.normalized_index, plan.table_target,
            plan.published_status, plan.callback_target) == (
        0xffffffff, 0x7fc70, 7, 0)

print("recovered 0x7fc24 result-tail vectors: ok")
