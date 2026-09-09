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
        ((0, 0, 0, 0), (1, 0, 0, 1, 0, 0)),
        ((1, 0, 1, 1), (1, 1, 1, 0, 1, 0)),
        ((1, 1, 1, 1), (1, 1, 0, 0, 0, 1)),
        ((0, 0, 1, 1), (1, 0, 1, 0, 1, 0)),
    ):
        plan = Plan()
        fn(*values, ctypes.byref(plan))
        actual = tuple(getattr(plan, name) for name, _ in Plan._fields_)
        if actual != expected:
            raise SystemExit("0x2440 wrapper plan mismatch")

    class Detailed(ctypes.Structure):
        _fields_ = [(name, ctypes.c_uint32) for name in (
            "input_initializer_called", "initial_primary_signature_checked",
            "initial_alternate_crc_checked", "initial_alternate_signature_checked",
            "initial_pair_compare_called", "failure_latch_cleared",
            "post_primary_crc_checked", "post_primary_byte_compare_checked",
            "post_alternate_crc_checked", "post_alternate_byte_compare_checked",
            "post_pair_compare_called", "record_copy_called",
            "first_table_validation_passed", "second_table_validation_passed",
            "reverse_table_copy_called", "table_recovery_initializer_called",
            "table_success_initializer_called",
            "table_copy_called", "startup_validation_fallback_called",
            "final_service_called")]

    detailed = lib.recovered_io_self_test_wrapper_detailed_plan
    detailed.argtypes = [ctypes.c_uint32] * 14 + [ctypes.POINTER(Detailed)]
    result = Detailed()
    detailed(*(1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1), ctypes.byref(result))
    actual = tuple(getattr(result, name) for name, _ in Detailed._fields_)
    assert actual == (1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0,
                      1, 1, 0, 0, 1, 1, 1, 1)

    detailed(*(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), ctypes.byref(result))
    actual = tuple(getattr(result, name) for name, _ in Detailed._fields_)
    assert actual == (1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0,
                      0, 0, 1, 1, 0, 1, 1, 1)

    detailed(*(0, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1), ctypes.byref(result))
    actual = tuple(getattr(result, name) for name, _ in Detailed._fields_)
    assert actual[:6] == (1, 0, 1, 1, 0, 1)

print("PASS: 0x2440 I/O self-test wrapper plan")
