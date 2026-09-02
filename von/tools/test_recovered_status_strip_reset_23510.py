#!/usr/bin/env python3
"""Validate the recovered 0x23510 status-strip reset plan."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("upload_helper", ctypes.c_uint32),
        ("upload_source", ctypes.c_uint32),
        ("upload_row_count", ctypes.c_uint32),
        ("upload_width", ctypes.c_uint32),
        ("upload_height", ctypes.c_uint32),
        ("clear_destination", ctypes.c_uint32),
        ("clear_halfword_count", ctypes.c_uint32),
        ("clear_value", ctypes.c_uint32),
        ("cleared_state_count", ctypes.c_uint32),
        ("cleared_state_address", ctypes.c_uint32 * 2),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "strip-reset.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_status_strip_reset_23510.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_status_strip_reset_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(0, ctypes.byref(plan))
    assert (plan.upload_helper, plan.upload_source, plan.upload_row_count,
            plan.upload_width, plan.upload_height) == (0x1DFD0, 0, 31, 64, 4)
    assert (plan.clear_destination, plan.clear_halfword_count,
            plan.clear_value) == (0x0100C000, 0xFFF, 0)
    assert list(plan.cleared_state_address) == [0x504D26, 0x504D24]

    plan_fn(0xFFFFFFFF, ctypes.byref(plan))
    assert plan.upload_row_count == 30

print("PASS: 0x23510 status-strip reset")
