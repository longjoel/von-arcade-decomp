#!/usr/bin/env python3
"""Validate the bounded pool/packet contract at 0x41f20."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_runtime_packet_dispatch_41f20.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("status_pool", ctypes.c_uint32),
        ("status_pool_stride", ctypes.c_uint32),
        ("status_pool_count", ctypes.c_uint32),
        ("status_offset", ctypes.c_uint32),
        ("handler_table", ctypes.c_uint32),
        ("selector_mask", ctypes.c_uint32),
        ("runtime_pool", ctypes.c_uint32),
        ("runtime_pool_stride", ctypes.c_uint32),
        ("runtime_pool_count", ctypes.c_uint32),
        ("runtime_active_mask", ctypes.c_uint32),
        ("command_selectors", ctypes.c_uint32 * 2),
        ("command_selector_count", ctypes.c_uint32),
        ("readback_address", ctypes.c_uint32),
        ("publication_address", ctypes.c_uint32),
        ("completion_address", ctypes.c_uint32),
        ("completion_value", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "runtime-packet-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_geometry_runtime_packet_dispatch_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.status_pool, plan.status_pool_stride, plan.status_pool_count,
            plan.status_offset, plan.handler_table, plan.selector_mask,
            plan.runtime_pool, plan.runtime_pool_stride, plan.runtime_pool_count,
            plan.runtime_active_mask, plan.command_selector_count,
            plan.readback_address, plan.publication_address,
            plan.completion_address, plan.completion_value) == \
        (0x51ad10, 0x24, 24, 2, 0x41c50, 0xffff, 0x51b070, 0x38,
         24, 0xffff, 2, 0x802008, 0x801008, 0x800010, 6)
    assert list(plan.command_selectors) == [5, 9]

    selector = recovered.recovered_geometry_runtime_packet_selector
    selector.argtypes = [ctypes.c_uint32]
    selector.restype = ctypes.c_uint32
    assert selector(0x12345678) == 0x5678

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   41f20:")
    end = listing.index("   420d0:")
    block = listing[start:end]
    for evidence in (
            "lda\t0x51ad10,r6", "lda\t0x33c,g2", "cmpi\tr4,g2",
            "ld\t0x41c50[g4*4],g1", "callx\t(g1)",
            "lda\t0x51b070,g5", "lda\t0x101,r6",
            "mov\t5,g2", "mov\t9,g2", "ldq\t0x8(r4),g4",
            "ld\t0x802008,g5", "st\tg5,0x884000",
            "st\tg5,0x801008", "st\tr6,0x800010",
            "mov\t6,g2", "st\tg2,0x884000"):
        if evidence not in block:
            raise AssertionError(f"runtime-dispatch listing evidence missing: {evidence}")

print("PASS: 0x41f20 runtime packet dispatch prefix")
