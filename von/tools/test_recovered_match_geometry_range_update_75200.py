#!/usr/bin/env python3
"""Validate the bounded entry prefix at i960 0x75200."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_geometry_range_update_75200.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("object_pointer_preserved_register", ctypes.c_uint32),
        ("object_link_offset", ctypes.c_uint32),
        ("frame_base_offset", ctypes.c_uint32),
        ("geometry_helper", ctypes.c_uint32),
        ("linked_record_offset", ctypes.c_uint32),
        ("classifier", ctypes.c_uint32),
        ("first_result_register", ctypes.c_uint32),
        ("zero_return", ctypes.c_uint32),
        ("nonzero_continuation", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "range-update.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_geometry_range_update_75200_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.object_pointer_preserved_register, plan.object_link_offset,
            plan.frame_base_offset, plan.geometry_helper,
            plan.linked_record_offset, plan.classifier,
            plan.first_result_register, plan.zero_return,
            plan.nonzero_continuation) == \
        (6, 0x74, 0x40, 0x77470, 0x184, 0x73508, 5, 0x7522c, 0x75230)

    zero_result = recovered.recovered_match_geometry_range_zero_result
    zero_result.argtypes = [ctypes.c_uint32]
    zero_result.restype = ctypes.c_uint32
    assert [zero_result(value) for value in (0, 1, 0xffffffff)] == [1, 0, 0]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   75200:")
    end = listing.index("   75230:")
    block = listing[start:end]
    for evidence in (
            "mov\tg0,r6", "ld\t0x74(g0),g4", "lda\t0x40(fp),g1",
            "call\t0x77470", "mov\tg0,r5", "ldos\t0x184(r6),g0",
            "bal\t0x73508", "cmpi\tr5,0", "bne\t0x75230",
            "ret"):
        if evidence not in block:
            raise AssertionError(f"geometry-range prefix evidence missing: {evidence}")

print("PASS: 0x75200-0x7522c match geometry-range prefix")
