#!/usr/bin/env python3
"""Validate the 0x29e68 blend inner-loop schedule."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("iterations", ctypes.c_uint32),
        ("stores", ctypes.c_uint32),
        ("pointer_advance", ctypes.c_uint32),
        ("src_end", ctypes.c_uint32),
        ("dst_end", ctypes.c_uint32),
    ]


def simulate_trip_count():
    # Body runs first, then addo r6,1 / cmpi 31,r6 / bge back exits
    # once 31 >= r6 fails.
    count = 0
    r6 = 0
    while True:
        count += 1
        r6 += 1
        if not (31 >= r6):
            break
    return count


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "blend-loop-sched.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_blend_loop_schedule_29e68.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_blend_loop_schedule_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.POINTER(Plan)]

    # The trip count below is re-derived from the branch shape,
    # not copied from the C unit under test.
    assert simulate_trip_count() == 32

    for src, dst in ((0x01814100, 0x01814000),
                     (0x01814100 + (5 << 12), 0x01814000 + (5 << 12)),
                     (0x00000000, 0x00000000)):
        plan = Plan()
        plan_fn(src, dst, ctypes.byref(plan))
        assert plan.iterations == 32, hex(src)
        assert plan.stores == 32
        assert plan.pointer_advance == 0x80
        assert plan.src_end == (src + 0x80) & 0xFFFFFFFF
        assert plan.dst_end == (dst + 0x80) & 0xFFFFFFFF

print("PASS: 0x29e68 blend inner-loop schedule")
