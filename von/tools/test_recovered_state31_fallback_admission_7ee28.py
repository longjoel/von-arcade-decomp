#!/usr/bin/env python3
"""Check deterministic fallback admission at i960 0x7ee28."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_fallback_admission_7ee28.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("timing_nonnegative", "object_state_64", "related_state_64",
                 "selector_504e4c", "object_state_gate_passed",
                 "related_state_gate_passed", "selector_gate_passed", "admitted",
                 "success_target", "failure_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-fallback-admission.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_fallback_admission_7ee28
    function.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(1, 3, 5, 2, ctypes.byref(plan))
    assert (plan.object_state_gate_passed, plan.related_state_gate_passed,
            plan.selector_gate_passed, plan.admitted,
            plan.success_target, plan.failure_target) == (1, 1, 1, 1,
                                                           0x7ee8c, 0)

    for args in ((0, 3, 5, 2), (1, 2, 5, 2), (1, 3, 7, 2),
                 (1, 3, 6, 1)):
        plan = Plan()
        function(*args, ctypes.byref(plan))
        assert plan.admitted == 0
        assert plan.failure_target == 0x7f0bc

print("recovered 0x7ee28 fallback-admission vectors: ok")
