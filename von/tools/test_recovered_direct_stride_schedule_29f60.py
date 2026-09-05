#!/usr/bin/env python3
"""Validate the mode-0 direct-path dispatch and stride schedule.

Provenance: synthetic (vonj-maincpu.lst 0x29f60/0x29fe0/0x2a00c/0x2a094
sites); no trace-derived vectors. Proves the code matches the reading,
not the original.
"""
import ctypes
import pathlib
import subprocess
import tempfile

M32 = 0x100000000


class Plan(ctypes.Structure):
    _fields_ = [
        ("fade_addr", ctypes.c_uint32),
        ("use_fade_form", ctypes.c_int32),
        ("factor", ctypes.c_uint32),
        ("outer_iterations", ctypes.c_uint32),
        ("pass_advance", ctypes.c_uint32),
        ("src0_end", ctypes.c_uint32),
        ("dst0_end", ctypes.c_uint32),
        ("src1_end", ctypes.c_uint32),
        ("dst1_end", ctypes.c_uint32),
        ("src2_end", ctypes.c_uint32),
        ("dst2_end", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "direct-stride-sched.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_direct_stride_schedule_29f60.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_direct_stride_schedule_plan
    plan_fn.argtypes = ([ctypes.c_int32] + [ctypes.c_uint32] * 6 +
                        [ctypes.POINTER(Plan)])

    bank = 3 << 12
    ptrs = (0x01810100 + bank, 0x01810000 + bank,
            0x01814100 + bank, 0x01814000 + bank,
            0x01818100 + bank, 0x01818000 + bank)

    for fade in (-0x80000000, -256, -1, 0, 1, 0x50, 0x100, 0x7FFFFFFF):
        plan = Plan()
        plan_fn(fade, *ptrs, ctypes.byref(plan))
        assert plan.fade_addr == 0x51A260
        assert plan.outer_iterations == 8
        assert plan.pass_advance == 0x200
        if fade <= 0:
            assert plan.use_fade_form == 1, fade
            assert plan.factor == fade % M32, fade
        else:
            assert plan.use_fade_form == 0, fade
            assert plan.factor == (fade + 0x100) % M32, fade
        # Uniform 0x200 strides put every pair exactly one bank ahead.
        for end, start in ((plan.src0_end, ptrs[0]),
                           (plan.dst0_end, ptrs[1]),
                           (plan.src1_end, ptrs[2]),
                           (plan.dst1_end, ptrs[3]),
                           (plan.src2_end, ptrs[4]),
                           (plan.dst2_end, ptrs[5])):
            assert end == (start + 0x1000) % M32, (fade, hex(start))

print("PASS: mode-0 direct-path dispatch and stride schedule")
