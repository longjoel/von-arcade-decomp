#!/usr/bin/env python3
"""Validate the bounded common update at i960 0x75134."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_transition_common_update_75134.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("mode_source", ctypes.c_uint32),
        ("mode_low_subtract", ctypes.c_uint32),
        ("mode_low_bound", ctypes.c_uint32),
        ("mode_high_subtract", ctypes.c_uint32),
        ("mode_high_bound", ctypes.c_uint32),
        ("saved_pair_source", ctypes.c_uint32),
        ("counter_source", ctypes.c_uint32),
        ("counter_destination", ctypes.c_uint32),
        ("counter_addend", ctypes.c_uint32),
        ("zero_selector", ctypes.c_uint32),
        ("equal_selector", ctypes.c_uint32),
        ("primary_helper", ctypes.c_uint32),
        ("floating_source", ctypes.c_uint32),
        ("floating_zero", ctypes.c_uint32),
        ("floating_upper_bits", ctypes.c_uint32),
        ("mode_filter_source", ctypes.c_uint32),
        ("secondary_helper", ctypes.c_uint32),
        ("fallback_value", ctypes.c_uint32),
        ("fallback_destination", ctypes.c_uint32),
        ("return_address", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "common-update.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_transition_common_update_75134_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.mode_source, plan.mode_low_subtract, plan.mode_low_bound,
            plan.mode_high_subtract, plan.mode_high_bound,
            plan.saved_pair_source, plan.counter_source,
            plan.counter_destination, plan.counter_addend,
            plan.zero_selector, plan.equal_selector, plan.primary_helper) == \
        (0x504d80, 13, 30, 5, 6, 0x504d90, 0x504d8c, 0x504d8c, 1,
         0, 0x504d90, 0x82040)
    assert (plan.floating_source, plan.floating_zero,
            plan.floating_upper_bits, plan.mode_filter_source,
            plan.secondary_helper, plan.fallback_value,
            plan.fallback_destination, plan.return_address) == \
        (0x504d60, 0, 0x40690000, 0x504d80, 0x82650, 0xffffffff,
         0x504d8c, 0x751e8)

    candidate = recovered.recovered_match_transition_counter_candidate
    candidate.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    candidate.restype = ctypes.c_uint32
    assert candidate(0, 0x1234, 9) == 10
    assert candidate(1, 0x1234, 9) == 0x1235
    fallback = recovered.recovered_match_transition_fallback_counter
    fallback.restype = ctypes.c_uint32
    assert fallback() == 0xffffffff

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   75134:")
    end = listing.index("   75200:")
    block = listing[start:end]
    for evidence in (
            "ld\t0x504d80,g5", "subo\t13,g5,g4",
            "cmpobge\t30,g4,0x7514c", "subo\t5,g5,g4",
            "ldq\t0x504d90,g0", "ld\t0x504d8c,g4",
            "call\t0x82040", "ld\t0x504d60,g4",
            "call\t0x82650", "st\tg14,0x504d8c",
            "subo\t1,0,r7", "st\tr7,0x504d8c",
            "ret"):
        if evidence not in block:
            raise AssertionError(f"common-update evidence missing: {evidence}")

print("PASS: 0x75134-0x751f4 match-transition common update")
