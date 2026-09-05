#!/usr/bin/env python3
"""Validate the recovered 0x29c50 re-arm stores (both entries).

Provenance: synthetic (vonj-maincpu.lst 0x29c50-0x29c9c); no
trace-derived vectors. Proves the code matches the reading, not the original.
"""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("value_addr", ctypes.c_uint32),
        ("value_stored", ctypes.c_int32),
        ("counter_addr", ctypes.c_uint32),
        ("counter_stored", ctypes.c_uint32),
        ("mode_addr", ctypes.c_uint32),
        ("mode_stored", ctypes.c_uint32),
        ("uploader_active", ctypes.c_int32),
    ]


def clamp(value):
    return 0 if value < 0 else (0x100 if value > 0x100 else value)


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "rearm-store.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_rearm_store_29c50.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    forced_fn = lib.recovered_rearm_store_plan
    forced_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32,
                          ctypes.POINTER(Plan)]
    link_fn = lib.recovered_rearm_link_store_plan
    link_fn.argtypes = [ctypes.c_int32, ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.POINTER(Plan)]

    for value in (-0x80000000, -256, -1, 0, 1, 0x50, 0x100, 0x101,
                  0x7FFFFFFF):
        for mode in (0x0, 0x1, 0x29C4C):
            # 0x29c50 entry: forced link re-arms regardless of inputs.
            plan = Plan()
            forced_fn(value, mode, ctypes.byref(plan))
            assert (plan.value_addr, plan.counter_addr,
                    plan.mode_addr) == (0x51A260, 0x51A264, 0x51A268)
            assert plan.value_stored == clamp(value), (value, mode)
            assert plan.counter_stored == 0x29C9C, (value, mode)
            assert plan.mode_stored == mode, (value, mode)
            assert plan.uploader_active == 1, (value, mode)

            # 0x29c58 entry: the counter follows the caller link.
            for link, active in ((0x0, 0), (0x2, 0), (0x3, 1),
                                 (0x1B968, 1), (0xDC77C, 1)):
                plan = Plan()
                link_fn(value, link, mode, ctypes.byref(plan))
                assert plan.value_stored == clamp(value), (value, link)
                assert plan.counter_stored == link, (value, link)
                assert plan.mode_stored == mode, (value, link)
                assert plan.uploader_active == active, (value, link)

print("PASS: 0x29c50 re-arm stores (both entries)")
