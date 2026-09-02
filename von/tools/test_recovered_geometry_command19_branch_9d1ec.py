#!/usr/bin/env python3
"""Validate the 0x9d1ec command-19 branch variants."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("fifo_address", ctypes.c_uint32),
        ("packet_count", ctypes.c_uint32),
        ("packet", ctypes.c_uint32 * 4),
        ("branch", ctypes.c_uint32),
        ("object_flag_1de", ctypes.c_uint32),
        ("object_138_low", ctypes.c_uint32),
        ("counter_90_before", ctypes.c_int32),
        ("counter_90_after", ctypes.c_int32),
        ("counter_9c", ctypes.c_int32),
        ("frame_value", ctypes.c_uint32),
        ("helper_call_count", ctypes.c_uint32),
        ("helper_arg0", ctypes.c_uint32 * 2),
        ("helper_arg1", ctypes.c_uint32 * 2),
        ("helper_result_arg", ctypes.c_uint32 * 2),
        ("display_call", ctypes.c_uint32),
        ("display_source", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "command19.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2",
        str(pathlib.Path(__file__).parents[1] / "i960" /
            "recovered_geometry_command19_branch_9d1ec.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    build = lib.recovered_geometry_command19_branch_plan
    build.argtypes = [
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan),
    ]

    def run(flag, low, c90, c9c):
        plan = Plan()
        build(flag, low, c90, c9c, 0x12345678, 0x0040068c,
              ctypes.byref(plan))
        return plan

    plan = run(0, 0, 7, 0)
    assert (plan.branch, list(plan.packet), plan.counter_90_after,
            plan.helper_call_count, list(plan.helper_arg0),
            list(plan.helper_arg1), list(plan.helper_result_arg)) == (
        0, [19, 0x3ada740e, 0x3bc49ba6, 0x3f800000],
        0x12345678, 1, [39, 0], [28, 0], [1, 0])

    plan = run(0, 0, 0, 0)
    assert (plan.branch, plan.counter_90_after,
            plan.helper_call_count) == (0, 30, 0)

    plan = run(1, 0, 0, 0)
    assert (plan.branch, plan.packet[2], plan.counter_90_after,
            plan.helper_call_count, plan.display_call) == (
        2, 0x3b03126f, 1, 2, 0x1d210)
    assert (list(plan.helper_arg0), list(plan.helper_arg1),
            list(plan.helper_result_arg)) == ([39, 43], [28, 29], [0, 0])

    # A live countdown uses the 0x3bc49ba6 payload and performs no rearm work.
    plan = run(1, 1, 4, 0)
    assert (plan.branch, plan.packet[2], plan.counter_90_after,
            plan.helper_call_count) == (1, 0x3bc49ba6, 4, 0)
    plan = run(1, 1, 0, 9)
    assert (plan.branch, plan.packet[2], plan.counter_90_after,
            plan.helper_call_count) == (2, 0x3b03126f, 0, 0)

print("PASS: 0x9d1ec command-19 branch")
