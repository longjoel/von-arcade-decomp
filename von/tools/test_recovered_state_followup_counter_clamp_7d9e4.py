#!/usr/bin/env python3
"""Check publication and counter clamping at i960 0x7d9e4."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_counter_clamp_7d9e4.c"


class Plan(ctypes.Structure):
    _fields_ = [("status_value", ctypes.c_uint32),
                ("result_value", ctypes.c_uint32),
                ("status_destination", ctypes.c_uint32),
                ("result_destination", ctypes.c_uint32),
                ("counter_before", ctypes.c_uint32),
                ("counter_after", ctypes.c_uint32),
                ("counter_destination", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-counter.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_counter_clamp_7d9e4
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    for before, after in ((0, 1), (23, 24), (24, 24),
                          (0xfffffffe, 0), (0xffffffff, 0)):
        plan = Plan()
        function(20, 0x12345678, before, ctypes.byref(plan))
        assert (plan.status_value, plan.result_value) == (20, 0x12345678)
        assert plan.counter_after == after
    plan = Plan()
    function(0, 0, 0, ctypes.byref(plan))
    assert (plan.status_destination, plan.result_destination,
            plan.counter_destination) == (0x504DB8, 0x504D94, 0x51C930)

print("PASS: 0x7d9e4 publication/counter-clamp vectors")
