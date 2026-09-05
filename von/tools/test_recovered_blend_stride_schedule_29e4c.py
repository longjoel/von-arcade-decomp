#!/usr/bin/env python3
"""Validate the 0x29d50 outer-cadence stride schedule."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("mode_addr", ctypes.c_uint32),
        ("outer_iterations", ctypes.c_uint32),
        ("plane_fade", ctypes.c_uint32 * 3),
        ("pass_advance0", ctypes.c_uint32),
        ("pass_advance1", ctypes.c_uint32),
        ("pass_advance2", ctypes.c_uint32),
        ("src0_end", ctypes.c_uint32),
        ("dst0_end", ctypes.c_uint32),
        ("src1_end", ctypes.c_uint32),
        ("dst1_end", ctypes.c_uint32),
        ("src2_end", ctypes.c_uint32),
        ("dst2_end", ctypes.c_uint32),
    ]


def simulate_outer_passes():
    # Body runs first, then addo r15,1 / cmpi 7,r15 / bge back exits
    # once 7 >= r15 fails.
    count = 0
    r15 = 0
    while True:
        count += 1
        r15 += 1
        if not (7 >= r15):
            break
    return count


def simulate_pointers(src0, dst0, src1, dst1, src2, dst2, passes):
    for _ in range(passes):
        src0 += 0x80 + 0x180
        dst0 += 0x80 + 0x180
        src1 += 0x80 + 0x180
        dst1 += 0x80 + 0x180
        src2 += 0x80 + 0x180 + 0x180
        dst2 += 0x80 + 0x180 + 0x180
    mask = 0xFFFFFFFF
    return (src0 & mask, dst0 & mask, src1 & mask,
            dst1 & mask, src2 & mask, dst2 & mask)


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "blend-stride-sched.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_blend_stride_schedule_29e4c.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_blend_stride_schedule_plan
    plan_fn.argtypes = [ctypes.c_uint32] * 7 + [ctypes.POINTER(Plan)]

    assert simulate_outer_passes() == 8

    bank = 3 << 12
    ptrs = (0x01810100 + bank, 0x01810000 + bank,
            0x01814100 + bank, 0x01814000 + bank,
            0x01818100 + bank, 0x01818000 + bank)
    for mode in (0x0, 0x1, 0x2, 0x4, 0x7, 0xFFFFFFFF):
        plan = Plan()
        plan_fn(*ptrs, mode, ctypes.byref(plan))
        assert plan.mode_addr == 0x51A268
        assert plan.outer_iterations == 8
        assert tuple(plan.plane_fade) == ((mode >> 0) & 1,
                                          (mode >> 1) & 1,
                                          (mode >> 2) & 1), hex(mode)
        assert (plan.pass_advance0, plan.pass_advance1,
                plan.pass_advance2) == (0x200, 0x200, 0x380)
        assert (plan.src0_end, plan.dst0_end, plan.src1_end,
                plan.dst1_end, plan.src2_end,
                plan.dst2_end) == simulate_pointers(*ptrs, 8)

print("PASS: 0x29d50 outer-cadence stride schedule")
