#!/usr/bin/env python3
"""Validate the bounded 0x2196c status upload route."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [("selected", ctypes.c_uint32),
                ("source", ctypes.c_uint32),
                ("helper", ctypes.c_uint32),
                ("column", ctypes.c_uint32),
                ("row", ctypes.c_uint32),
                ("width", ctypes.c_uint32),
                ("height", ctypes.c_uint32),
                ("attribute_mask", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "upload.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_status_low_latch_upload.c"), "-o", str(so)],
                   check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_status_low_latch_upload_plan
    plan_fn.argtypes = [ctypes.c_int32, ctypes.POINTER(Plan)]

    for latch in (0, 4, 8):
        plan = Plan()
        plan_fn(latch, ctypes.byref(plan))
        assert (plan.selected, plan.source, plan.helper, plan.column,
            plan.row, plan.width, plan.height, plan.attribute_mask) == (
            1, 0x02FE8FC4, 0x1DE80, 0, (latch - 8) & 0xffffffff,
            0x40, 8, 0x40
        )

    plan = Plan()
    plan_fn(9, ctypes.byref(plan))
    assert plan.selected == 0

print("PASS: 0x2196c low-latch upload")
