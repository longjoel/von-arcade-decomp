#!/usr/bin/env python3
"""Check the packet/result boundary of i960 handler 0x7dc04."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_followup_geometry_handler_7dc04.c"


class Plan(ctypes.Structure):
    _fields_ = [
        ("command", ctypes.c_uint32),
        ("negated_field_10", ctypes.c_int32),
        ("negated_field_8", ctypes.c_int32),
        ("fifo_destination", ctypes.c_uint32),
        ("response_low16", ctypes.c_uint32),
        ("object_field_184_low16", ctypes.c_uint32),
        ("classifier_input", ctypes.c_uint32),
        ("result_table", ctypes.c_uint32),
        ("result_value", ctypes.c_uint32),
        ("counter_destination", ctypes.c_uint32),
        ("counter_value", ctypes.c_uint32),
        ("selector_destination", ctypes.c_uint32),
        ("selector_value", ctypes.c_uint32),
        ("status_destination", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-followup-geometry.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_followup_geometry_handler_7dc04
    function.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
                         ctypes.c_uint32, ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(-12, 34, 0xdeadbeef, 0x12345678, 0xabcdef01, 0x44, 9,
             ctypes.byref(plan))
    assert (plan.command, plan.negated_field_10, plan.negated_field_8) == (10, 12, -34)
    assert (plan.fifo_destination, plan.response_low16) == (0x884000, 0xbeef)
    assert plan.object_field_184_low16 == 0x5678
    assert (plan.result_table, plan.result_value) == (0x72B10, 0x44)
    assert (plan.counter_destination, plan.counter_value) == (0x504DB8, 40)
    assert (plan.selector_destination, plan.selector_value) == (0x504D98, 23)
    assert plan.status_destination == 0x504D94

print("PASS: 0x7dc04 follow-up geometry handler boundary")
