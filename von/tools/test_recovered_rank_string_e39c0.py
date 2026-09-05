#!/usr/bin/env python3
"""Validate the recovered 0xe39c0 rank-string emitter plan."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("number_table", ctypes.c_uint32),
        ("suffix_table", ctypes.c_uint32),
        ("entry_stride", ctypes.c_uint32),
        ("number_walker", ctypes.c_uint32),
        ("suffix_walker", ctypes.c_uint32),
        ("number_address", ctypes.c_uint32),
        ("suffix_address", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "rank-string.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_rank_string_e39c0.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_rank_string_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(0, ctypes.byref(plan))
    assert (plan.number_table, plan.suffix_table, plan.entry_stride,
            plan.number_walker, plan.suffix_walker) == (
        0x000E36C0, 0x000E3700, 6, 0x1D1D0, 0x1D1B0
    )
    assert (plan.number_address, plan.suffix_address) == (
        0x000E36C0, 0x000E3700
    )

    # Index 2 addresses " 3" and "RD" six bytes per slot apart.
    plan_fn(2, ctypes.byref(plan))
    assert (plan.number_address, plan.suffix_address) == (
        0x000E36C0 + 12, 0x000E3700 + 12
    )

print("PASS: 0xe39c0 rank-string plan")
