#!/usr/bin/env python3
"""Check state-31 classifier offset routing at i960 0x7ee90."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_classifier_route_7ee90.c"
RUNTIME_SOURCE = ROOT / "von/i960/recovered_runtime_math.c"


class Plan(ctypes.Structure):
    _fields_ = [("entry_condition_passed", ctypes.c_uint32),
                ("global_504d70", ctypes.c_uint32),
                ("high_global_arm", ctypes.c_uint32),
                ("related_state_64", ctypes.c_uint32),
                ("object_state_64", ctypes.c_uint32),
                ("classifier_offset", ctypes.c_int32),
                ("classifier_input", ctypes.c_uint32),
                ("classifier_band", ctypes.c_uint32),
                ("result_table", ctypes.c_uint32),
                ("publication_target", ctypes.c_uint32),
                ("callback_target", ctypes.c_uint32),
                ("action_value", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32),
                ("continuation_value", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-classifier-route.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    str(RUNTIME_SOURCE), "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_classifier_route_7ee90
    function.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(1, 4, 6, 1, ctypes.byref(plan))
    assert (plan.high_global_arm, plan.classifier_offset,
            plan.classifier_input) == (0, -0x1800, 0x503564)
    assert plan.classifier_band == 2

    plan = Plan()
    function(1, 5, 6, 1, ctypes.byref(plan))
    assert (plan.high_global_arm, plan.classifier_offset,
            plan.classifier_input) == (1, 0x1800, 0x506564)
    assert plan.classifier_band == 4

    for args, offset in (((1, 4, 6, 2), -0x800),
                         ((1, 4, 5, 2), -0xc00),
                         ((1, 5, 5, 3), 0x1800),
                         ((1, 5, 5, 2), 0x2800)):
        plan = Plan()
        function(*args, ctypes.byref(plan))
        assert plan.classifier_offset == offset
        assert (plan.result_table, plan.publication_target,
                plan.callback_target, plan.action_value,
                plan.control_value, plan.continuation_value) == (
            0x72780, 0x7efb0, 0x79050, 30, 3, 0x64)

print("recovered 0x7ee90 classifier-route vectors: ok")
