#!/usr/bin/env python3
"""Check timing threshold routing at i960 0x7f634."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_timing_threshold_route_7f634.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "lower_threshold_above_current", "current_below_upper_threshold",
        "global_504da4", "global_504dc8", "lower_arm_taken", "upper_arm_taken",
        "upper_globals_passed", "callback_target", "selector_destination",
        "selector_value", "control_destination", "control_value",
        "state_destination", "state_value", "route_mode", "target",
        "failure_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-timing-route.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_timing_threshold_route_7f634
    function.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(1, 0, 0, 0, ctypes.byref(plan))
    assert (plan.lower_arm_taken, plan.callback_target, plan.selector_value,
            plan.control_value, plan.target) == (1, 0x82800, 4, 0x64, 0x7f66c)

    plan = Plan()
    function(0, 1, 1, 1, ctypes.byref(plan))
    assert (plan.upper_arm_taken, plan.upper_globals_passed,
            plan.state_destination, plan.state_value, plan.route_mode,
            plan.target) == (1, 1, 0x504d98, 1, 10, 0x7f8fc)

    for values in ((0, 0, 1, 1), (0, 1, 0, 1), (0, 1, 1, 0)):
        plan = Plan()
        function(*values, ctypes.byref(plan))
        assert plan.target == plan.failure_target == 0x7f6b0

print("recovered 0x7f634 timing-route vectors: ok")
