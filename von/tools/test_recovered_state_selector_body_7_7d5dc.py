#!/usr/bin/env python3
"""Check the state-7 selector body at i960 0x7d5dc."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_selector_body_7_7d5dc.c"


class Plan(ctypes.Structure):
    _fields_ = [
        ("target", ctypes.c_uint32),
        ("writes_selector", ctypes.c_uint32),
        ("selector_value", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-selector-body-7.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_selector_body_7_7d5dc
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.POINTER(Plan)]
    function.restype = None

    def run(mode_bits, control):
        plan = Plan()
        function(mode_bits, control, ctypes.byref(plan))
        return plan

    assert run(0, 1).target == 0x7D654
    assert run(2, 0).target == 0x7D654
    plan = run(2, 1)
    assert plan.target == 0x7D5F4
    assert plan.writes_selector == 1 and plan.selector_value == 2

print("PASS: 0x7d5dc state-7 selector-body vectors")
