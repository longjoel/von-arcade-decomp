#!/usr/bin/env python3
"""Validate the recovered 0x29d50 upload-select prologue.

Provenance: synthetic (vonj-maincpu.lst 0x29d50-0x29dbc); no
trace-derived vectors. Proves the code matches the reading, not the original.
"""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("counter_addr", ctypes.c_uint32),
        ("mode_addr", ctypes.c_uint32),
        ("active", ctypes.c_int32),
        ("old_counter", ctypes.c_int32),
        ("next_counter", ctypes.c_int32),
        ("src0_addr", ctypes.c_uint32),
        ("dst0_addr", ctypes.c_uint32),
        ("src1_addr", ctypes.c_uint32),
        ("dst1_addr", ctypes.c_uint32),
        ("src2_addr", ctypes.c_uint32),
        ("dst2_addr", ctypes.c_uint32),
        ("mode", ctypes.c_uint32),
        ("direct_path", ctypes.c_int32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "upload-select.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_upload_select_29d50.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_upload_select_plan
    plan_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32,
                        ctypes.POINTER(Plan)]

    def run(counter, mode):
        plan = Plan()
        plan_fn(counter, mode, ctypes.byref(plan))
        return plan

    # Below-threshold counters return early with no bank selected.
    for counter in (0, 1, 2, -5):
        plan = run(counter, 0)
        assert plan.active == 0, counter
        assert plan.next_counter == counter, counter
        assert (plan.src0_addr, plan.dst0_addr, plan.src1_addr,
                plan.dst1_addr, plan.src2_addr,
                plan.dst2_addr) == (0, 0, 0, 0, 0, 0), counter
        assert (plan.counter_addr, plan.mode_addr) == (0x51A264, 0x51A268)

    # Threshold counter selects the 4KB bank and bumps the counter.
    plan = run(3, 0)
    assert plan.active == 1
    assert plan.next_counter == 4
    assert plan.src0_addr == 0x1810100 + (3 << 12)
    assert plan.dst0_addr == 0x1810000 + (3 << 12)
    assert plan.src1_addr == 0x1814100 + (3 << 12)
    assert plan.dst1_addr == 0x1814000 + (3 << 12)
    assert plan.src2_addr == 0x1818100 + (3 << 12)
    assert plan.dst2_addr == 0x1818000 + (3 << 12)
    assert plan.direct_path == 1

    # Nonzero mode word takes the bit-selected blend path.
    plan = run(5, 0x03)
    assert plan.active == 1
    assert plan.next_counter == 6
    assert plan.src0_addr == 0x1810100 + (5 << 12)
    assert plan.direct_path == 0
    assert plan.mode == 0x03

print("PASS: 0x29d50 upload-select prologue")
