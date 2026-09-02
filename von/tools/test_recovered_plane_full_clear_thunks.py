#!/usr/bin/env python3
"""Validate the 0x22c70/0x22cb0 full-plane clear thunks."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [("destination", ctypes.c_uint32),
                ("word_count", ctypes.c_uint32),
                ("value", ctypes.c_uint32),
                ("return_stub", ctypes.c_uint32),
                ("fill_register_after_return", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "clears.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_plane_full_clear_thunks.c"), "-o", str(so)],
                   check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_plane_full_clear_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    for variant, destination, stub in ((0, 0x01000000, 0x22CA4),
                                        (1, 0x01004000, 0x22CE4)):
        plan = Plan()
        plan_fn(variant, ctypes.byref(plan))
        assert (plan.destination, plan.word_count, plan.value,
                plan.return_stub, plan.fill_register_after_return) == (
            destination, 0xFFF, 0, stub, 0
        )

print("PASS: 0x22c70/0x22cb0 full-plane clear thunks")
