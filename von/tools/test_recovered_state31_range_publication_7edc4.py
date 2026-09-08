#!/usr/bin/env python3
"""Check the state-31 range/publication arm at i960 0x7edc4."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_range_publication_7edc4.c"


class Plan(ctypes.Structure):
    _fields_ = [("related_state_64", ctypes.c_uint32),
                ("related_172", ctypes.c_int16),
                ("scaled_related_172", ctypes.c_uint32),
                ("bypasses_range", ctypes.c_uint32),
                ("range_passed", ctypes.c_uint32),
                ("status_value", ctypes.c_uint32),
                ("selector_value", ctypes.c_uint32),
                ("action_value", ctypes.c_uint32),
                ("control_value", ctypes.c_uint32),
                ("continuation_value", ctypes.c_uint32),
                ("continuation_target", ctypes.c_uint32),
                ("status_destination", ctypes.c_uint32),
                ("selector_destination", ctypes.c_uint32),
                ("action_destination", ctypes.c_uint32),
                ("control_destination", ctypes.c_uint32),
                ("continuation_destination", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-range-publication.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_range_publication_7edc4
    function.argtypes = [ctypes.c_uint32, ctypes.c_int16,
                         ctypes.c_uint32, ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(3, 0x16, 0x55, ctypes.byref(plan))
    assert (plan.scaled_related_172, plan.bypasses_range,
            plan.range_passed, plan.status_value) == (0x160000, 0, 1, 0x55)
    assert (plan.selector_value, plan.action_value, plan.control_value,
            plan.continuation_value, plan.continuation_target) == (
        3, 20, 3, 0x64, 0x7efd8)

    plan = Plan()
    function(3, 0x15, 0x55, ctypes.byref(plan))
    assert (plan.range_passed, plan.status_value) == (0, 23)
    plan = Plan()
    function(3, 0x19, 0x55, ctypes.byref(plan))
    assert (plan.range_passed, plan.status_value) == (1, 0x55)
    plan = Plan()
    function(4, -0x4000, 0x55, ctypes.byref(plan))
    assert (plan.bypasses_range, plan.range_passed, plan.status_value) == (1, 1, 0x55)

print("recovered 0x7edc4 range-publication vectors: ok")
