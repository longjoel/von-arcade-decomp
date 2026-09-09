#!/usr/bin/env python3
"""Validate the fixed text-startup workspace reset schedule."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("zeroed_header_count", ctypes.c_uint32),
        ("zeroed_header_addresses", ctypes.c_uint32 * 10),
        ("record_count", ctypes.c_uint32),
        ("record_stride", ctypes.c_uint32),
        ("record_zero_field_count", ctypes.c_uint32),
        ("record_zero_offsets", ctypes.c_uint32 * 4),
        ("record_zero_write_count", ctypes.c_uint32),
        ("sentinel_address", ctypes.c_uint32),
        ("sentinel_value", ctypes.c_int32),
        ("status_latch_address", ctypes.c_uint32),
        ("status_latch_value", ctypes.c_uint32),
        ("table_initializer_called", ctypes.c_uint32),
        ("table_copy_called", ctypes.c_uint32),
        ("table_initializer_address", ctypes.c_uint32),
        ("table_copy_address", ctypes.c_uint32),
    ]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "reset.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_text_startup_workspace_reset_2350.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    fn = lib.recovered_text_startup_workspace_reset_plan
    fn.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    fn(ctypes.byref(plan))

    assert plan.zeroed_header_count == 10
    assert tuple(plan.zeroed_header_addresses) == tuple(0x1d00038 + 4 * i for i in range(10))
    assert (plan.record_count, plan.record_stride, plan.record_zero_field_count,
            plan.record_zero_write_count) == (10, 0x10, 4, 40)
    assert tuple(plan.record_zero_offsets) == (0xa4, 0xa8, 0xac, 0xb0)
    assert (plan.sentinel_address, plan.sentinel_value) == (0x1d00060, -1)
    assert (plan.status_latch_address, plan.status_latch_value) == (0x5039f8, 0)
    assert (plan.table_initializer_called, plan.table_copy_called,
            plan.table_initializer_address, plan.table_copy_address) == (1, 1, 0xe3740, 0x2330)

print("PASS: 0x2350 text-startup workspace reset plan")
