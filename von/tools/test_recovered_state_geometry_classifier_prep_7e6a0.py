#!/usr/bin/env python3
"""Check classifier argument preparation at i960 0x7e6a0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_geometry_classifier_prep_7e6a0.c"
RUNTIME_SOURCE = ROOT / "von/i960/recovered_runtime_math.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("object_response_delta", "classifier_g0", "classifier_g1",
                 "classifier_g2", "classifier_g6", "classifier_r5",
                 "classifier_r6", "classifier_r7", "classifier_r8",
                 "classifier_target", "classifier_band")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-geometry-classifier-prep.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    str(RUNTIME_SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_geometry_classifier_prep_7e6a0
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint16] + [
        ctypes.c_uint32] * 8 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(0x12345678, 0xfff0,
             0x100, 0x200, 0x300, 0x400, 0x500, 0x600, 0x700, 0x800,
             ctypes.byref(plan))
    assert plan.object_response_delta == 0x5688
    assert plan.classifier_g0 == 0x5688
    assert (plan.classifier_g1, plan.classifier_g2, plan.classifier_g6) == (
        0x500, 0x300, 0x700)
    assert (plan.classifier_r5, plan.classifier_r6,
            plan.classifier_r7, plan.classifier_r8) == (
        0x300, 0xffffff00, 0xffffff00, 0x100)
    assert plan.classifier_target == 0x73508
    assert plan.classifier_band == 3

    plan = Plan()
    function(0, 0x8000, 0, 0, 0, 0, 0, 0, 0, 0, ctypes.byref(plan))
    assert plan.classifier_g0 == 0xffff8000
    assert plan.classifier_band == 5

print("recovered 0x7e6a0 classifier-prep vectors: ok")
