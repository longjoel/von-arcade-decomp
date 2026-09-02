#!/usr/bin/env python3
"""Validate the mirrored 0x9d59c command-19 branch."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("fifo_address", ctypes.c_uint32),
        ("initial_packet_count", ctypes.c_uint32),
        ("initial_packet", ctypes.c_uint32 * 4),
        ("packet_count", ctypes.c_uint32),
        ("packet", ctypes.c_uint32 * 4),
        ("branch", ctypes.c_uint32),
        ("object_flag_1dd", ctypes.c_uint32),
        ("object_139_low", ctypes.c_uint32),
        ("counter_94_before", ctypes.c_int32),
        ("counter_94_after", ctypes.c_int32),
        ("counter_a0", ctypes.c_int32),
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
            "recovered_geometry_command19_branch_9d59c.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    build = lib.recovered_geometry_command19_mirror_plan
    build.argtypes = [
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int32, ctypes.c_int32,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan),
    ]

    def run(flag, low, c94, ca0):
        plan = Plan()
        build(flag, low, c94, ca0, 0x12345678, 0x0040069c,
              ctypes.byref(plan))
        return plan

    plan = run(0, 0, 7, 0)
    assert (plan.fifo_address, plan.initial_packet_count,
            list(plan.initial_packet), plan.packet_count,
            list(plan.packet), plan.branch, plan.counter_94_after,
            plan.helper_call_count, list(plan.helper_arg0),
            list(plan.helper_arg1), list(plan.helper_result_arg)) == (
        0x884000, 4, [19, 0xbe962fc9, 0xbdf92c60, 0x3f800000], 4,
        [19, 0x3ada740e, 0x3bc49ba6, 0x3f800000], 0,
        0x12345678, 1, [7, 0], [28, 0], [1, 0])

    plan = run(1, 0, 0, 0)
    assert (plan.branch, plan.packet[2], plan.counter_94_after,
            plan.helper_call_count, plan.display_call) == (
        2, 0x3b03126f, 1, 2, 0x1d210)
    assert (list(plan.helper_arg0), list(plan.helper_arg1),
            list(plan.helper_result_arg)) == ([7, 9], [28, 29], [0, 0])

    plan = run(1, 1, 5, 0)
    assert (plan.branch, plan.packet[2], plan.counter_94_after,
            plan.helper_call_count) == (1, 0x3bc49ba6, 5, 0)
    plan = run(0, 0, 0, 0)
    assert (plan.branch, plan.counter_94_after,
            plan.helper_call_count) == (0, 30, 0)

print("PASS: 0x9d59c mirrored command-19 branch")
