#!/usr/bin/env python3
"""Validate the recovered 0x1ccf8 MMIO doorbell.

Provenance: synthetic (vonj-maincpu.lst 0x1ccf8-0x1cd0c); no
trace-derived vectors. Proves the code matches the reading, not the original.
"""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("reg_addr", ctypes.c_uint32),
        ("reg_stored", ctypes.c_uint16),
        ("link_saved", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "doorbell.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_doorbell_1ccf8.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_doorbell_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.POINTER(Plan)]

    for value, link in ((0x0, 0x1BA38), (0x1, 0x1B988), (0x1013, 0x1BA48),
                        (0xFFFF, 0x1B990), (0x10000, 0x1BA3C),
                        (0x12345678, 0xDEADBEEF)):
        plan = Plan()
        plan_fn(value, link, ctypes.byref(plan))
        assert plan.reg_addr == 0x1800000, hex(value)
        # Halfword store keeps only the low 16 bits of g0.
        assert plan.reg_stored == value & 0xFFFF, hex(value)
        assert plan.link_saved == link, hex(link)

print("PASS: 0x1ccf8 MMIO doorbell")
