#!/usr/bin/env python3
"""Validate the exact startup table clear schedule at 0x423a8."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_startup_record_table_clear_423a8.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("first_table", ctypes.c_uint32),
        ("first_stride", ctypes.c_uint32),
        ("first_limit", ctypes.c_uint32),
        ("second_table", ctypes.c_uint32),
        ("second_stride", ctypes.c_uint32),
        ("second_limit", ctypes.c_uint32),
        ("sentinel", ctypes.c_uint32),
        ("pool_a", ctypes.c_uint32),
        ("pool_b", ctypes.c_uint32),
        ("pool_stride", ctypes.c_uint32),
        ("pool_count", ctypes.c_uint32),
        ("pool_field_offset", ctypes.c_uint32),
        ("cleared_global", ctypes.c_uint32 * 2),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "record-table-clear.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_startup_record_table_clear_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.first_table, plan.first_stride, plan.first_limit,
            plan.second_table, plan.second_stride, plan.second_limit,
            plan.sentinel, plan.pool_a, plan.pool_b, plan.pool_stride,
            plan.pool_count, plan.pool_field_offset) == \
        (0x51ad10, 0x24, 0x33c, 0x51b070, 0x38, 0x508, 0xffff,
         0x51b5b0, 0x51b850, 0x1c, 11, 0x150)
    assert list(plan.cleared_global) == [0x51baf4, 0x51baf0]

    count = recovered.recovered_startup_record_table_entry_count
    count.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    count.restype = ctypes.c_uint32
    assert count(0x33c, 0x24) == 24
    assert count(0x508, 0x38) == 24

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   423a8:")
    end = listing.index("   42460:")
    block = listing[start:end]
    for evidence in (
            "lda\t0x51ad10,g7", "stos\tg6,0x2(g4)[g7]",
            "stos\tg5,0x51ad10(g4)", "lda\t0x33c,g0",
            "lda\t0x51b070,g6", "stos\tg5,0x2(g4)[g6]",
            "lda\t0x508,g0", "lda\t0x51b850,g5",
            "lda\t0x51b5b0,g4", "stos\tg7,0x150(g4)",
            "stos\tg7,0x150(g5)", "st\tg14,0x51baf4",
            "st\tg14,0x51baf0", "bx\t(g1)"):
        if evidence not in block:
            raise AssertionError(f"record-table listing evidence missing: {evidence}")

print("PASS: 0x423a8 startup record-table clear")
