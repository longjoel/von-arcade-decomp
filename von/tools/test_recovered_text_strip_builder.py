#!/usr/bin/env python3
"""Validate the recovered 0x20a20 text-strip arithmetic."""
import ctypes
import pathlib
import subprocess
import tempfile


class Segment(ctypes.Structure):
    _fields_ = [("repetitions", ctypes.c_uint32),
                ("first_value", ctypes.c_uint32),
                ("second_value", ctypes.c_uint32),
                ("third_value", ctypes.c_uint32)]


class Plan(ctypes.Structure):
    _fields_ = [("destination", ctypes.c_uint32),
                ("amount", ctypes.c_uint32),
                ("segment", Segment * 3)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "strip.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_text_strip_builder.c"), "-o", str(so)],
                   check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_text_strip_plan
    plan_fn.argtypes = [ctypes.c_uint32] * 8 + [ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(5, 24, 3, 0x1111, 0x2222, 0x3333, 7, 0xaaaa,
            ctypes.byref(plan))
    assert (plan.destination, plan.amount) == (0x0100c1c0, 15)
    assert [segment.repetitions for segment in plan.segment] == [4, 15, 4]
    assert (plan.segment[0].first_value, plan.segment[0].second_value,
            plan.segment[0].third_value) == (0xaaaa, 0xaaaa, 0xaaaa)
    assert (plan.segment[1].first_value, plan.segment[1].second_value,
            plan.segment[1].third_value) == (0x1111, 0x2222, 0x3333)
    assert (plan.segment[2].first_value, plan.segment[2].second_value,
            plan.segment[2].third_value) == (0xaaaa, 0xaaaa, 0xaaaa)

    plan_fn(100, 24, 3, 1, 2, 3, 0, 0,
            ctypes.byref(plan))
    assert plan.amount == 24
    assert [segment.repetitions for segment in plan.segment] == [0, 24, 0]

print("PASS: 0x20a20 text-strip builder")
