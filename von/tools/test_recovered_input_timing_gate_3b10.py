#!/usr/bin/env python3
"""Validate the 0x3b10 input timing gate."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "counter_step", "limit_check_passed", "status34_checked",
        "status34_nonzero", "status_a4_bit4_checked", "status_a4_bit4_set",
        "accepted", "field38_subtracted", "field38_after",
        "table_copy_called", "service_called", "service_argument",
        "table_copy_helper", "service_helper", "return_address")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "timing-gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_input_timing_gate_3b10.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    fn = lib.recovered_input_timing_gate_3b10
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Plan)]
    for args, expected in (
        ((5, 6, 0, 0x10), (6, 1, 0, 0, 1, 1, 1, 0, 6, 0, 1, 0x111c, 0x2330, 0x2a580, 0x3b94)),
        ((5, 5, 0, 0x10), (6, 0, 1, 0, 0, 0, 0, 0, 5, 0, 0, 0x111c, 0x2330, 0x2a580, 0x3b98)),
        ((5, 5, 1, 0), (6, 0, 1, 1, 1, 0, 0, 0, 5, 0, 0, 0x111c, 0x2330, 0x2a580, 0x3b98)),
        ((0xffff, 7, 1, 0x10), (0, 1, 0, 1, 1, 1, 1, 1, 7, 1, 1, 0x111c, 0x2330, 0x2a580, 0x3b94)),
    ):
        result = Plan()
        fn(*args, ctypes.byref(result))
        actual = tuple(getattr(result, name) for name, _ in Plan._fields_)
        assert actual == expected, (args, actual, expected)

print("PASS: 0x3b10 input timing gate")
