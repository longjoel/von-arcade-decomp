#!/usr/bin/env python3
"""Check state-4 result routing at i960 0x7f9b0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_state4_result_route_7f9b0.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "object_state", "global_504d70", "related_184", "current_184",
        "related_172_shifted", "offset", "classifier_input", "classifier_target",
        "result_table", "direct_result", "alternate_result", "selected_result",
        "inner_band_passed", "state4_target", "alternate_target",
        "publication_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-state4-result-route.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_state4_result_route_7f9b0
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int32,
                         ctypes.c_int32, ctypes.c_uint32, ctypes.c_int32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]
    function.restype = None

    for global_value, offset in ((0, -0x1000), (9, 0x1000),
                                 (4, -0x4000), (5, 0x4000)):
        plan = Plan()
        function(4, global_value, 0x12000, 0x8000, 0x170000, 0x100, 6, 7,
                 ctypes.byref(plan))
        assert ctypes.c_int32(plan.offset).value == offset
        assert (plan.result_table, plan.selected_result,
                plan.publication_target) == (0x72630, 6, 0x7fabc)

    plan = Plan()
    function(4, 5, 0, 0, 0x150000, 0, 6, 7, ctypes.byref(plan))
    assert (plan.inner_band_passed, plan.result_table, plan.selected_result) == (
        0, 0x72780, 7)
    plan = Plan()
    function(4, 5, 0, 0, 0x190000, 0, 6, 7, ctypes.byref(plan))
    assert (plan.inner_band_passed, plan.result_table) == (1, 0x72630)

    plan = Plan()
    function(3, 5, 0, 0, 0, 0, 6, 7, ctypes.byref(plan))
    assert (plan.alternate_target, plan.publication_target) == (0x7fac8, 0x7fac8)

print("recovered 0x7f9b0 state-4 result-route vectors: ok")
