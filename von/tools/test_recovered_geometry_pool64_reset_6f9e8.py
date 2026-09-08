#!/usr/bin/env python3
"""Validate the exact 64-slot pool reset at 0x6f9e8."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_pool64_reset_6f9e8.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("slot_table", ctypes.c_uint32),
        ("slot_count", ctypes.c_uint32),
        ("record_table", ctypes.c_uint32),
        ("record_stride", ctypes.c_uint32),
        ("record_clear_offset", ctypes.c_uint32),
        ("cursor_address", ctypes.c_uint32),
        ("cursor_value", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "pool64-reset.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_geometry_pool64_reset_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.slot_table, plan.slot_count, plan.record_table,
            plan.record_stride, plan.record_clear_offset,
            plan.cursor_address, plan.cursor_value) == \
        (0x51c860, 64, 0x51c5b0, 0x54, 0, 0x51c880, 0)
    count = recovered.recovered_geometry_pool64_slot_count
    count.restype = ctypes.c_uint32
    assert count() == 64

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   6f9e8:")
    end = listing.index("   6fa40:")
    block = listing[start:end]
    for evidence in (
            "lda\t0x3f,g7", "lda\t0x51c860,g6",
            "st\tg4,(g6)", "st\tg14,0x51c5b0(g5)",
            "addo\tg6,4,g6", "lda\t0x54(g5),g5",
            "st\tg14,0x51c880", "bx\t(g0)"):
        if evidence not in block:
            raise AssertionError(f"pool-reset listing evidence missing: {evidence}")

print("PASS: 0x6f9e8 geometry pool64 reset")
