#!/usr/bin/env python3
"""Check the state-31 callback gate at i960 0x7ecc0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_global_callback_gate_7ecc0.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("global_5770f0", "global_gate_passed", "best_response_zero",
                 "callback_target", "callback_selector", "first_continuation",
                 "second_zero_test_passed", "selector_gate_passed",
                 "status_gate_passed", "continues_to_7ed34", "failure_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-global-callback-gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_global_callback_gate_7ecc0
    function.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(10, 1, 0x34, 0, 9, ctypes.byref(plan))
    assert (plan.global_gate_passed, plan.best_response_zero,
            plan.callback_target, plan.callback_selector,
            plan.continues_to_7ed34) == (1, 1, 0x81b30, 0, 1)
    assert plan.first_continuation == 0x7ed08

    plan = Plan()
    function(10, 0, 0x34, 0, 0, ctypes.byref(plan))
    assert (plan.callback_target, plan.callback_selector,
            plan.second_zero_test_passed, plan.failure_target) == (
        0x816d0, 0x34, 0, 0x7f0f8)

    for selector, status in ((1, 0), (0, 1), (3, 9)):
        plan = Plan()
        function(10, 1, 0, selector, status, ctypes.byref(plan))
        assert plan.continues_to_7ed34 == 0

    plan = Plan()
    function(9, 1, 0, 0, 0, ctypes.byref(plan))
    assert plan.global_gate_passed == 0
    assert plan.continues_to_7ed34 == 1

print("recovered 0x7ecc0 global-callback-gate vectors: ok")
