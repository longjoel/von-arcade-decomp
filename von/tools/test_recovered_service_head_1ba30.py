#!/usr/bin/env python3
"""Validate the recovered 0x1ba30 service head block.

Provenance: synthetic (vonj-maincpu.lst 0x1ba30-0x1ba6c); no
trace-derived vectors. Proves the code matches the reading, not the original.
"""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("setup_call_arg", ctypes.c_uint32),
        ("profile_call_arg", ctypes.c_uint32),
        ("preset_addr", ctypes.c_uint32),
        ("preset_value", ctypes.c_uint32),
        ("bump_addr", ctypes.c_uint32),
        ("bumped_value", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "service-head.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_service_head_1ba30.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_service_head_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    for base in (0x0, 0x1, 0x10, 0xFFFFFFFE, 0xFFFFFFFF):
        plan = Plan()
        plan_fn(base, ctypes.byref(plan))
        assert plan.setup_call_arg == 0, hex(base)
        assert plan.profile_call_arg == 0x1013, hex(base)
        assert (plan.preset_addr, plan.preset_value) == (0x503A04, 0x12C)
        assert plan.bump_addr == 0x503A00
        assert plan.bumped_value == (base + 1) & 0xFFFFFFFF, hex(base)

print("PASS: 0x1ba30 service head block")
