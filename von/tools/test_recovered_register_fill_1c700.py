#!/usr/bin/env python3
"""Validate the recovered 0x1c700 register-fill schedule.

Provenance: synthetic (vonj-maincpu.lst 0x1c700-0x1c72c); no
trace-derived vectors. Proves the code matches the reading, not the original.
"""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [("iterations", ctypes.c_uint32),
                ("dst_end", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "register-fill.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_register_fill_1c700.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_register_fill_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    for dst in (0x0, 0x1000, 0x1C72C, 0xFFFFF000):
        plan = Plan()
        plan_fn(dst, ctypes.byref(plan))
        assert plan.iterations == 4096, hex(dst)
        assert plan.dst_end == (dst + 8192) & 0xFFFFFFFF, hex(dst)

print("PASS: 0x1c700 register-fill schedule")
