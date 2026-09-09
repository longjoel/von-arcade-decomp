#!/usr/bin/env python3
"""Check the state-4 threshold prefix at i960 0x7f70c."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_state4_threshold_prefix_7f70c.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "related_state", "current_below_407f4000", "current_below_4072c000",
        "outer_state_gate_passed", "outer_timing_gate_passed",
        "selector_destination", "selector_value", "control_destination",
        "control_value", "direct_table_arm", "table_address",
        "common_publication_target", "difference_route_target", "return_target",
        "failure_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-state4-prefix.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_state4_threshold_prefix_7f70c
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(4, 1, 1, ctypes.byref(plan))
    assert (plan.outer_state_gate_passed, plan.outer_timing_gate_passed,
            plan.selector_value, plan.control_value, plan.direct_table_arm,
            plan.table_address, plan.common_publication_target) == (
        1, 1, 4, 0x64, 1, 0x72780, 0x7f7d4)

    plan = Plan()
    function(4, 1, 0, ctypes.byref(plan))
    assert (plan.direct_table_arm, plan.difference_route_target,
            plan.selector_value, plan.control_value) == (0, 0x7f774, 4, 0x64)

    plan = Plan()
    function(4, 0, 1, ctypes.byref(plan))
    assert (plan.return_target, plan.selector_value, plan.control_value) == (
        0x7f7fc, 0, 0)

    plan = Plan()
    function(3, 1, 1, ctypes.byref(plan))
    assert (plan.outer_state_gate_passed, plan.difference_route_target,
            plan.failure_target) == (0, 0, 0x7f800)

print("recovered 0x7f70c state-4 prefix vectors: ok")
