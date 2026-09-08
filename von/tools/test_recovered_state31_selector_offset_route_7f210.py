#!/usr/bin/env python3
"""Check selector/state classifier offsets at i960 0x7f210."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_selector_offset_route_7f210.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "object_state", "related_state", "selector", "selector_minus_3",
        "positive_selector_arm", "base_offset", "classifier_offset",
        "classifier_input", "target", "classifier_table")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-selector-offset.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_selector_offset_route_7f210
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    vectors = ((6, 0, 3, 0x1000), (6, 0, 4, 0x1000),
               (6, 0, 5, 0x1000), (5, 5, 3, 0x1000),
               (5, 6, 3, 0x3000), (3, 6, 3, 0x1800),
               (5, 6, 5, 0x3000), (1, 4, 3, 0x1800))
    for object_state, related_state, selector, base in vectors:
        plan = Plan()
        function(object_state, related_state, selector, ctypes.byref(plan))
        assert (plan.base_offset, plan.target, plan.classifier_table) == (
            base, 0x7f31c, 0x72780)

    for selector in (0, 1, 2, 3, 4):
        plan = Plan()
        function(6, 0, selector, ctypes.byref(plan))
        assert plan.positive_selector_arm == (1 if selector < 3 else 0)
        assert ctypes.c_int32(plan.classifier_offset).value == (
            0x1000 if selector < 3 else -0x1000)

    plan = Plan()
    function(6, 0, 5, ctypes.byref(plan))
    assert (plan.positive_selector_arm,
            ctypes.c_int32(plan.classifier_offset).value) == (1, 0x1000)

print("recovered 0x7f210 selector-offset vectors: ok")
