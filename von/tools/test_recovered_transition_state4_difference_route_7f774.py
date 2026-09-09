#!/usr/bin/env python3
"""Check the state-4 difference route at i960 0x7f774."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_state4_difference_route_7f774.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "published_status", "related_184", "current_184", "positive_bias_arm",
        "bias", "biased_current", "reverse_difference", "classifier_target",
        "result_table", "common_publication_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-state4-difference.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_state4_difference_route_7f774
    function.argtypes = [ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32,
                         ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(4, 0x12000, 0x8000, ctypes.byref(plan))
    assert (plan.positive_bias_arm, ctypes.c_int32(plan.bias).value,
            ctypes.c_int32(plan.biased_current).value,
            ctypes.c_int32(plan.reverse_difference).value) == (0, -0x5000, 0x3000, 0xf000)

    plan = Plan()
    function(5, 0x12000, 0x8000, ctypes.byref(plan))
    assert (plan.positive_bias_arm, plan.bias, plan.biased_current,
            plan.reverse_difference) == (1, 0x5000, 0xd000, 0x5000)
    assert (plan.classifier_target, plan.result_table,
            plan.common_publication_target) == (0x73508, 0x72780, 0x7f7d4)

print("recovered 0x7f774 difference-route vectors: ok")
