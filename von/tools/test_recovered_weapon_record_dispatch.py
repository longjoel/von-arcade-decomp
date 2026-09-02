#!/usr/bin/env python3
"""Validate the 0x20b50 record table and 0x211f0 dispatch contract."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [("record_address", ctypes.c_uint32),
                ("asset_pointer", ctypes.c_uint32),
                ("handler", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_weapon_record_dispatch.c"), "-o", str(so)],
                   check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_weapon_record_dispatch_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    assets = [0x02FE7554, 0x02FE7DCE, 0x02FE4AF2, 0x02FE6CDA,
              0x02FE536C, 0x02FE5BE6, 0x02FE39FE, 0x02FE4278,
              0x02FE6460, 0x02FE8648]
    handlers = [0x21240, 0x21314, 0x214BC, 0x21784,
                0x213E8, 0x216A0, 0x21674, 0x21580]
    for selector in range(12):
        plan = Plan()
        plan_fn(selector, ctypes.byref(plan))
        index = selector if selector < 10 else 9
        expected_handler = handlers[selector] if selector < 8 else 0x218A0
        assert (plan.record_address, plan.asset_pointer, plan.handler) == (
            0x20B50 + index * 0x68, assets[index], expected_handler
        )

print("PASS: 0x20b50 record table and 0x211f0 dispatch")
