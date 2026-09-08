#!/usr/bin/env python3
"""Validate the fixed packet contract at 0x3ef50."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_status_record_geometry_emit_3ef50.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("pool_address", ctypes.c_uint32),
        ("record_stride", ctypes.c_uint32),
        ("record_count", ctypes.c_uint32),
        ("status_offset", ctypes.c_uint32),
        ("table_address", ctypes.c_uint32),
        ("fifo_address", ctypes.c_uint32),
        ("packet_selectors", ctypes.c_uint32 * 4),
        ("packet_selector_count", ctypes.c_uint32),
        ("response_offsets", ctypes.c_uint32 * 2),
        ("constant_offset", ctypes.c_uint32),
        ("constant_word", ctypes.c_uint32),
        ("final_zero_offset", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "status-record-emit.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_status_record_geometry_emit_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.pool_address, plan.record_stride, plan.record_count,
            plan.status_offset, plan.table_address, plan.fifo_address,
            plan.packet_selector_count, plan.constant_offset,
            plan.constant_word, plan.final_zero_offset) == \
        (0x51ad10, 0x24, 23, 2, 0x3eca0, 0x884000, 4, 0x12,
         0xbe99999a, 0)
    assert list(plan.packet_selectors) == [8, 13, 29, 30]
    assert list(plan.response_offsets) == [0x0e, 0x16]

    selector = recovered.recovered_status_record_geometry_selector
    selector.argtypes = [ctypes.c_uint32]
    selector.restype = ctypes.c_uint32
    assert selector(0x12345678) == 0x5678

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   3ef50:")
    end = listing.index("   3f120:")
    block = listing[start:end]
    for evidence in (
            "lda\t0x51ad10,r8", "cmpi\t23,g5",
            "mov\t8,g3", "mov\t13,g3", "mov\t29,g3", "mov\t30,g3",
            "st\tg3,0x884000", "st\tg4,0xe(r5)",
            "st\tg3,0x12(r5)", "stos\tg14,(r5)", "ret"):
        if evidence not in block:
            raise AssertionError(f"record-emitter listing evidence missing: {evidence}")

print("PASS: 0x3ef50 status-record geometry emitter")
