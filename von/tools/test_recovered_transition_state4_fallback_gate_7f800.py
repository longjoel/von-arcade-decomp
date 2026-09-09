#!/usr/bin/env python3
"""Check the state-4 fallback gate at i960 0x7f800."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_state4_fallback_gate_7f800.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "related_state", "current_below_407f4000", "r6_compare_equal_zero",
        "related_172_shifted", "control_504e48", "state_gate_passed",
        "timing_gate_passed", "floating_gate_passed", "lower_band_passed",
        "upper_gap_passed", "halfword_gate_passed", "control_gate_passed",
        "admission_passed", "target", "failure_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-state4-fallback.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_state4_fallback_gate_7f800
    function.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(Plan)]
    function.restype = None

    for shifted in (0x160000, 0x160001, 0x180001):
        plan = Plan()
        function(4, 1, 1, shifted, 2, ctypes.byref(plan))
        if shifted == 0x160001:
            assert plan.admission_passed == 0
        else:
            assert (plan.admission_passed, plan.target) == (1, 0x7f878)

    for values in ((3, 1, 1, 0x160000, 2), (4, 0, 1, 0x160000, 2),
                   (4, 1, 0, 0x160000, 2), (4, 1, 1, 0x160000, 1)):
        plan = Plan()
        function(*values, ctypes.byref(plan))
        assert plan.admission_passed == 0
        assert plan.target == plan.failure_target == 0x7f91c

print("recovered 0x7f800 fallback-gate vectors: ok")
