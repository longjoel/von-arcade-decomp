#!/usr/bin/env python3
"""Validate the recovered 0x1c618 window-clear schedule.

Provenance: synthetic (vonj-maincpu.lst 0x1c618-0x1cf0); no
trace-derived vectors. Proves the code matches the reading, not the original.
"""
import ctypes
import pathlib
import subprocess
import tempfile


class Run(ctypes.Structure):
    _fields_ = [("base", ctypes.c_uint32),
                ("halfwords", ctypes.c_uint32)]


class Plan(ctypes.Structure):
    _fields_ = [
        ("half_slot_base", ctypes.c_uint32),
        ("half_slots", ctypes.c_uint32),
        ("word_slot_base", ctypes.c_uint32),
        ("word_slots", ctypes.c_uint32),
        ("fills", Run * 4),
        ("total_halfwords", ctypes.c_uint32),
    ]


def countdown(initial):
    # setbit count, then body-first subo/stos/cmpi/bg: exactly
    # `initial` stores before the greater-than test fails at zero.
    stores = 0
    remaining = initial
    while True:
        remaining -= 1
        stores += 1
        if remaining <= 0:
            break
    return stores


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "window-clear.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_window_clear_1c618.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_window_clear_plan
    plan_fn.argtypes = [ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(ctypes.byref(plan))
    assert (plan.half_slot_base, plan.half_slots) == (0x504D24, 8)
    assert (plan.word_slot_base, plan.word_slots) == (0x504D34, 2)
    assert [(r.base, r.halfwords) for r in plan.fills] == [
        (0x1000000, 16384), (0x100C000, 4096),
        (0x1008000, 2048), (0x100A000, 8)]
    for initial in (16384, 4096, 2048, 8):
        assert countdown(initial) == initial
    assert plan.total_halfwords == 8 + 16384 + 4096 + 2048 + 8

print("PASS: 0x1c618 window-clear schedule")
