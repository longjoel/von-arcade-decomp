#!/usr/bin/env python3
"""Validate the recovered 0x292d8 geometry-port word pump plan."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("select_address", ctypes.c_uint32),
        ("select_value", ctypes.c_uint32),
        ("port_address", ctypes.c_uint32),
        ("header_words", ctypes.c_uint32 * 2),
        ("pair_count", ctypes.c_uint32),
        ("words_per_pair", ctypes.c_uint32),
        ("words_total", ctypes.c_uint32),
        ("saves_return_link", ctypes.c_uint32),
        ("clears_g14", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "fifo-upload.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_fifo_upload_292d8.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_fifo_upload_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.POINTER(Plan)]

    # The 0x294b0 setup call writes headers (0, 32) then 64 table words.
    plan = Plan()
    plan_fn(0, 32, ctypes.byref(plan))
    assert (plan.select_address, plan.select_value,
            plan.port_address) == (0x00800060, 0x606, 0x00804000)
    assert list(plan.header_words) == [0, 32]
    assert (plan.pair_count, plan.words_per_pair,
            plan.words_total) == (32, 2, 64)
    assert (plan.saves_return_link, plan.clears_g14) == (1, 1)

    plan_fn(7, 1, ctypes.byref(plan))
    assert list(plan.header_words) == [7, 1]
    assert plan.words_total == 2

print("PASS: 0x292d8 FIFO word pump plan")
