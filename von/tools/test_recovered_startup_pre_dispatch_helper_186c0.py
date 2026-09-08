#!/usr/bin/env python3
"""Validate the startup wrapper at i960 0x186c0."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("command_byte", "command_cleared", "buffer_address",
                 "clear_byte_count", "clear_helper")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "startup.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_startup_pre_dispatch_helper_186c0.c"),
                    "-o", str(so)], check=True)
    fn = ctypes.CDLL(str(so)).recovered_startup_pre_dispatch_helper_186c0
    fn.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    fn(ctypes.byref(plan))
    actual = tuple(getattr(plan, name) for name, _ in Plan._fields_)
    if actual != (3, 1, 0x005770C0, 16, 0x000C5D48):
        raise SystemExit("0x186c0 startup helper mismatch")

print("PASS: 0x186c0 startup pre-dispatch helper")
