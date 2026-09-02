#!/usr/bin/env python3
"""Validate the recovered 0x20ae0 hardware-strip clear plan."""
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
    so = pathlib.Path(td) / "clear.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_hardware_strip_clear.c"), "-o", str(so)],
                   check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_hardware_strip_clear_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    for mode, value in ((0, 0), (1, 0xffff), (0xffffffff, 0xffff)):
        plan = Plan()
        plan_fn(mode, ctypes.byref(plan))
        assert (plan.destination, plan.word_count, plan.value,
                plan.return_stub, plan.fill_register_after_return) == (
                    0x0100d000, 0x5ff, value, 0x20b48, 0)

print("PASS: 0x20ae0 hardware-strip clear")
