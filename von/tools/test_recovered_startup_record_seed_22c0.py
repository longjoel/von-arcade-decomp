#!/usr/bin/env python3
"""Validate the fixed startup-record seed schedule."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "copy_helper", "copy_source", "copy_destination", "copy_length",
        "type_address", "type_value")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "seed.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_startup_record_seed_22c0.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    fn = lib.recovered_startup_record_seed_plan
    fn.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    fn(ctypes.byref(plan))
    assert tuple(getattr(plan, name) for name, _ in Plan._fields_) == (
        0xf5d40, 0x22a0, 0x1d00016, 20, 0x1d00028, 2)

print("PASS: 0x22c0 startup record seed plan")
