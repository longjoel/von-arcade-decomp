#!/usr/bin/env python3
"""Validate the bounded entry prefix at 0x32810."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_object_state_prefix_32810.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("fifo_address", ctypes.c_uint32),
        ("object_source_pointer_offset", ctypes.c_uint32),
        ("source_pointer_fields", ctypes.c_uint32 * 2),
        ("object_copy_destinations", ctypes.c_uint32 * 2),
        ("packet_selectors", ctypes.c_uint32 * 2),
        ("packet_selector_count", ctypes.c_uint32),
        ("first_response_destination", ctypes.c_uint32),
        ("difference_response_destination", ctypes.c_uint32),
        ("state_field_offset", ctypes.c_uint32),
        ("dispatch_table_address", ctypes.c_uint32),
        ("dispatch_target", ctypes.c_uint32 * 14),
        ("dispatch_target_count", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "object-state-prefix.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_geometry_object_state_prefix_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))

    assert (plan.fifo_address, plan.object_source_pointer_offset,
            plan.packet_selector_count, plan.first_response_destination,
            plan.difference_response_destination, plan.state_field_offset,
            plan.dispatch_table_address, plan.dispatch_target_count) == \
        (0x884000, 0x74, 2, 0x7c, 0x84, 0x1b2, 0x32968, 14)
    assert list(plan.source_pointer_fields) == [8, 16]
    assert list(plan.object_copy_destinations) == [0xa4, 0xa8]
    assert list(plan.packet_selectors) == [31, 10]
    assert list(plan.dispatch_target) == [
        0x329c4, 0x329a0, 0x32a88, 0x32af4, 0x32b20, 0x32b7c,
        0x32bc0, 0x32c1c, 0x32cfc, 0x32dcc, 0x32e40, 0x32e74,
        0x32ea4, 0x32fd0]

    selector = recovered.recovered_geometry_object_state_selector
    selector.argtypes = [ctypes.c_uint32]
    selector.restype = ctypes.c_uint32
    difference = recovered.recovered_geometry_object_state_difference_response
    difference.argtypes = [ctypes.c_uint32]
    difference.restype = ctypes.c_uint32
    assert selector(0x1234abcd) == 0xabcd
    assert difference(0x1234abcd) == 0xabcd

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   32810:")
    end = listing.index("   329a0:")
    block = listing[start:end]
    for evidence in (
            "ld\t0x74(g0),r9", "ld\t0x8(r9),r10",
            "st\tr10,0xa4(g0)", "st\tr11,0xa8(g0)",
            "mov\t31,r10", "mov\t10,r10", "st\tr11,0x7c(g0)",
            "stos\tg4,0x84(g0)", "cmpobl\t13,g4,0x33080",
            "ld\t0x32968[g4*4],g4"):
        if evidence not in block:
            raise AssertionError(f"object-state listing evidence missing: {evidence}")

print("PASS: 0x32810 geometry object-state prefix")
