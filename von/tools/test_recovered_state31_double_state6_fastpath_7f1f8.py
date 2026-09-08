#!/usr/bin/env python3
"""Check the paired state-6 fast path at i960 0x7f1f8."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state31_double_state6_fastpath_7f1f8.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "object_state", "related_state", "paired_state6", "target",
        "fast_target", "alternate_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate31-state6-fastpath.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state31_double_state6_fastpath_7f1f8
    function.argtypes = [ctypes.c_uint32] * 2 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(6, 6, ctypes.byref(plan))
    assert (plan.paired_state6, plan.target) == (1, 0x7f31c)

    for object_state, related_state in ((6, 5), (5, 6), (0, 0), (3, 7)):
        plan = Plan()
        function(object_state, related_state, ctypes.byref(plan))
        assert (plan.paired_state6, plan.target) == (0, 0x7f210)

print("recovered 0x7f1f8 state-6 fast-path vectors: ok")
