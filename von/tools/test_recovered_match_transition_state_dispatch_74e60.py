#!/usr/bin/env python3
"""Validate the bounded state-dispatch prefix at 0x74e60."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_transition_state_dispatch_74e60.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("threshold_source", ctypes.c_uint32),
        ("threshold", ctypes.c_uint32),
        ("boolean_destination", ctypes.c_uint32),
        ("selector_source", ctypes.c_uint32),
        ("selector_limit", ctypes.c_uint32),
        ("dispatch_table", ctypes.c_uint32),
        ("dispatch_count", ctypes.c_uint32),
        ("dispatch_target", ctypes.c_uint32 * 8),
        ("first_arm_threshold", ctypes.c_uint32),
        ("first_arm_state", ctypes.c_uint32),
        ("first_arm_destination", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "state-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_transition_state_dispatch_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.threshold_source, plan.threshold, plan.boolean_destination,
            plan.selector_source, plan.selector_limit, plan.dispatch_table,
            plan.dispatch_count, plan.first_arm_threshold,
            plan.first_arm_state, plan.first_arm_destination) == \
        (0x504dc0, 0x96, 0x504da4, 0x504d7c, 7, 0x74ea4, 8, 120, 3, 0x504da8)
    assert list(plan.dispatch_target) == [
        0x74ec4, 0x74ef0, 0x74f28, 0x74f3c,
        0x74f60, 0x74fa0, 0x74fc8, 0x75048]
    flag = recovered.recovered_match_transition_threshold_flag
    flag.argtypes = [ctypes.c_uint32]
    flag.restype = ctypes.c_uint32
    assert [flag(v) for v in (0x95, 0x96, 0x97)] == [0, 0, 1]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   74e60:")
    end = listing.index("   74ec8:")
    block = listing[start:end]
    for evidence in (
            "ld\t0x504dc0,g5", "lda\t0x96,r7",
            "st\tg6,0x504da4", "ld\t0x504d7c,g4",
            "cmpo\t7,g4", "ld\t0x74ea4[g4*4],g4",
            "shlo\t3,15,r6"):
        if evidence not in block:
            raise AssertionError(f"state-dispatch listing evidence missing: {evidence}")

print("PASS: 0x74e60 match-transition state dispatch")
