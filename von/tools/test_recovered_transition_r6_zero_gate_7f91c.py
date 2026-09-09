#!/usr/bin/env python3
"""Check the r6 zero gate at i960 0x7f91c."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_r6_zero_gate_7f91c.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "r6_compare_equal_zero", "equality_gate_passed", "target",
        "return_target", "arithmetic_route_target")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-r6-zero-gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_r6_zero_gate_7f91c
    function.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]
    function.restype = None

    for value, target in ((1, 0x7f934), (0, 0x7f938)):
        plan = Plan()
        function(value, ctypes.byref(plan))
        assert (plan.equality_gate_passed, plan.target) == (value, target)
        assert (plan.return_target, plan.arithmetic_route_target) == (0x7f934, 0x7f938)

print("recovered 0x7f91c r6-zero vectors: ok")
