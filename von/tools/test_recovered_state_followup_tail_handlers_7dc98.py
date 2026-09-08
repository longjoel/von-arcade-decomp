#!/usr/bin/env python3
"""Check follow-up tails at i960 0x7dc98 and 0x7dca8."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_tail_handlers_7dc98.c"


class Plan(ctypes.Structure):
    _fields_ = [
        ("writes_status", ctypes.c_uint32),
        ("status_destination", ctypes.c_uint32),
        ("status_value", ctypes.c_uint32),
        ("writes_counter", ctypes.c_uint32),
        ("counter_destination", ctypes.c_uint32),
        ("counter_value", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-tails.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_tail_handler_7dc98
    function.argtypes = [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(0x7DC98, 0, 0x1234, ctypes.byref(plan))
    assert (plan.status_destination, plan.status_value) == (0x504D94, 29)
    assert plan.writes_counter == 0

    plan = Plan()
    function(0x7DCA8, 6, 0x12345678, ctypes.byref(plan))
    assert plan.writes_counter == 0

    plan = Plan()
    function(0x7DCA8, 5, 0x12345678, ctypes.byref(plan))
    assert plan.writes_counter == 1
    assert (plan.counter_destination, plan.counter_value) == (0x51C930, 0x12345678)

print("PASS: 0x7dc98/0x7dca8 follow-up-tail vectors")
