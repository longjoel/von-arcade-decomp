#!/usr/bin/env python3
"""Validate the recovered 0x29d2c upload-state initializer.

Provenance: synthetic (vonj-maincpu.lst 0x29d2c-0x29d48); no
trace-derived vectors. Proves the code matches the reading, not the original.
"""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("value_addr", ctypes.c_uint32),
        ("mode_addr", ctypes.c_uint32),
        ("counter_addr", ctypes.c_uint32),
        ("value_stored", ctypes.c_uint32),
        ("mode_stored", ctypes.c_uint32),
        ("counter_stored", ctypes.c_int32),
        ("uploader_active", ctypes.c_int32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "upload-state-init.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_upload_state_init_29d2c.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_upload_state_init_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    for link in (0x00000000, 0x00029C4C, 0xDEADBEEF):
        plan = Plan()
        plan_fn(link, ctypes.byref(plan))
        assert (plan.value_addr, plan.mode_addr,
                plan.counter_addr) == (0x51A260, 0x51A268, 0x51A264)
        assert plan.value_stored == link, hex(link)
        assert plan.mode_stored == link, hex(link)
        assert plan.counter_stored == 4
        # Preset counter clears the 0x29d50 sub-3 early-return guard.
        assert plan.uploader_active == 1

print("PASS: 0x29d2c upload-state initializer")
