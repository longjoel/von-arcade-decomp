#!/usr/bin/env python3
"""Check fallback result routing at i960 0x7fe24."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_fallback_result_route_7fe24.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "global_counter", "global_504d70", "related_184", "current_184",
        "difference_input", "offset", "counter_shortcut",
        "negative_global_arm", "positive_global_arm", "classifier_result",
        "direct_table_result", "result_table", "selected_result",
        "action_destination", "action_value", "status_destination",
        "published_status", "callback_gate", "callback_target",
        "callback_argument", "target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-fallback-result.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_fallback_result_route_7fe24
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int32,
                         ctypes.c_int32, ctypes.c_int32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(0x2bc, 9, 0x12000, 0x8000, 6, 0x33, 1, 0xcafe,
             ctypes.byref(plan))
    assert (plan.counter_shortcut, plan.result_table, plan.selected_result,
            plan.callback_target, plan.callback_argument) == (
        1, 0x72720, 0x33, 0x79050, 0xcafe)

    for global_value, offset in ((0, -0x6580), (3, -0x6580),
                                 (4, 0x6580), (9, 0x6580)):
        plan = Plan()
        function(0x2bd, global_value, 0x12000, 0x8000, 7, 0, 0, 0,
                 ctypes.byref(plan))
        assert (ctypes.c_int32(plan.offset).value,
                ctypes.c_int32(plan.difference_input).value,
                plan.result_table, plan.selected_result, plan.target) == (
            offset, 0x12000 - (0x8000 + offset), 0x72780, 7, 0x7fed0)

print("recovered 0x7fe24 fallback-route vectors: ok")
