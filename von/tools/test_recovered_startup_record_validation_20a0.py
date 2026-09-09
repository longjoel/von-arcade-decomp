#!/usr/bin/env python3
"""Validate the 0x20a0 startup record validation control plans."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "input_initializer_called", "primary_signature_checked",
        "alternate_crc_checked", "alternate_signature_checked",
        "record_pair_compare_called", "failure_latch_cleared",
        "record_fragments_copied", "primary_crc_recomputed",
        "input_post_service_called", "returned_latch",
        "copy_fragment_count")]
    _fields_ += [("copy_lengths", ctypes.c_uint32 * 4),
                 ("copy_destinations", ctypes.c_uint32 * 4),
                 ("copy_sources", ctypes.c_uint32 * 4)]


class RetryPlan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "input_initializer_called", "primary_signature_checked",
        "alternate_crc_checked", "alternate_signature_checked",
        "record_pair_compare_called", "returned_latch")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "validation.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_startup_record_validation_20a0.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    fn = lib.recovered_startup_record_validation_plan
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(Plan)]
    retry = lib.recovered_startup_record_retry_plan
    retry.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(RetryPlan)]

    plan = Plan()
    fn(0, 0, 0, 0, ctypes.byref(plan))
    assert (plan.primary_signature_checked, plan.alternate_crc_checked,
            plan.failure_latch_cleared, plan.record_fragments_copied,
            plan.copy_fragment_count) == (0, 1, 1, 0, 0)
    assert tuple(plan.copy_lengths) == (4, 4, 20, 14)
    assert tuple(plan.copy_destinations) == (0x502400, 0x502404, 0x502410, 0x502424)
    assert tuple(plan.copy_sources) == (0x2030, 0x2098, 0x1d00016, 0x1d0002a)

    fn(1, 0, 0, 0, ctypes.byref(plan))
    assert (plan.alternate_crc_checked, plan.alternate_signature_checked,
            plan.failure_latch_cleared, plan.record_pair_compare_called) == (1, 0, 1, 0)
    fn(1, 0, 1, 1, ctypes.byref(plan))
    assert (plan.alternate_signature_checked, plan.record_pair_compare_called,
            plan.failure_latch_cleared) == (1, 1, 0)
    fn(0, 0, 1, 1, ctypes.byref(plan))
    assert (plan.alternate_crc_checked, plan.alternate_signature_checked,
            plan.failure_latch_cleared, plan.record_pair_compare_called,
            plan.record_fragments_copied) == (1, 1, 0, 1, 1)

    retry_plan = RetryPlan()
    retry(1, 1, 1, 1, ctypes.byref(retry_plan))
    assert tuple(getattr(retry_plan, name) for name, _ in RetryPlan._fields_) == (1, 1, 0, 0, 0, 1)
    retry(1, 0, 1, 1, ctypes.byref(retry_plan))
    assert tuple(getattr(retry_plan, name) for name, _ in RetryPlan._fields_) == (1, 1, 1, 1, 1, 1)

print("PASS: 0x20a0 startup record validation plans")
