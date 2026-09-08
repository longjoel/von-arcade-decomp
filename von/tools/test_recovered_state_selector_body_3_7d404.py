#!/usr/bin/env python3
"""Check the state-3 selector body at i960 0x7d404."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_selector_body_3_7d404.c"


class Plan(ctypes.Structure):
    _fields_ = [
        ("route", ctypes.c_uint32),
        ("target", ctypes.c_uint32),
        ("writes_selector", ctypes.c_uint32),
        ("selector_value", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-selector-body-3.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_selector_body_3_7d404
    function.argtypes = [ctypes.c_uint32] * 7 + [ctypes.POINTER(Plan)]
    function.restype = None

    def run(*values):
        plan = Plan()
        function(*values, ctypes.byref(plan))
        return plan

    assert run(0, 1, 1, 1, 1, 1, 2).target == 0x7D644
    plan = run(1, 1, 1, 0, 0, 0, 0)
    assert plan.target == 0x7D4B4
    assert plan.writes_selector == 1 and plan.selector_value == 3
    assert run(1, 0, 1, 1, 1, 1, 2).target == 0x7D5F4
    assert run(1, 0, 1, 0, 0, 1, 2).target == 0x7D654
    assert run(1, 0, 1, 1, 0, 1, 0).target == 0x7D654

print("PASS: 0x7d404 state-3 selector-body vectors")
