#!/usr/bin/env python3
"""Check the state-4 global route at i960 0x7f878."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_state4_global_route_7f878.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "global_504d70", "related_184", "current_184", "difference_input",
        "direct_table_value", "classifier_result", "global_negative_arm",
        "global_direct_arm", "global_positive_arm", "result_from_table",
        "status_destination", "published_status", "callback_target",
        "callback_argument", "action_destination", "action_value",
        "control_destination", "control_value", "selector_destination",
        "selector_value", "target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-state4-global-route.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_state4_global_route_7f878
    function.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32,
                         ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.POINTER(Plan)]
    function.restype = None

    for global_value, expected_arm, expected_bias in ((0, "negative", -0x5000),
                                                       (1, "negative", -0x5000),
                                                       (2, "direct", 0x5000),
                                                       (7, "direct", 0x5000),
                                                       (8, "positive", 0x5000)):
        plan = Plan()
        function(global_value, 0x12000, 0x8000, 6, 0x33, 0x64, 0xcafe,
                 ctypes.byref(plan))
        assert ctypes.c_int32(plan.difference_input).value == 0x12000 - (0x8000 + expected_bias)
        assert plan.result_from_table == (0x33 if expected_arm == "direct" else 6)
        assert (plan.callback_target, plan.callback_argument,
                plan.action_value, plan.control_value, plan.selector_value,
                plan.target) == (0x79050, 0xcafe, 30, 0x64, 4, 0x7f918)

print("recovered 0x7f878 global-route vectors: ok")
