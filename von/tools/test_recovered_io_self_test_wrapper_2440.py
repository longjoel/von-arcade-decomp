#!/usr/bin/env python3
"""Validate the pure control plan for the i960 0x2440 wrapper."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "input_initializer_called", "first_record_signature_checked",
        "second_record_signature_checked", "failure_latch_cleared",
        "record_copy_called", "device_ready")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "wrapper.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_io_self_test_wrapper_2440.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    fn = lib.recovered_io_self_test_wrapper_plan
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Plan)]
    for values, expected in (
        ((0, 0, 0, 0), (1, 0, 0, 0, 0, 0)),
        ((1, 0, 1, 1), (1, 1, 1, 0, 1, 0)),
        ((1, 1, 1, 1), (1, 1, 0, 0, 0, 1)),
    ):
        plan = Plan()
        fn(*values, ctypes.byref(plan))
        actual = tuple(getattr(plan, name) for name, _ in Plan._fields_)
        if actual != expected:
            raise SystemExit("0x2440 wrapper plan mismatch")

print("PASS: 0x2440 I/O self-test wrapper plan")
