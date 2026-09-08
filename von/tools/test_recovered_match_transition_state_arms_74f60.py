#!/usr/bin/env python3
"""Validate the bounded state arms 4 and 5 at 0x74f60 and 0x74fa0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_transition_state_arms_74f60.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("arm4_entry", ctypes.c_uint32),
        ("arm4_saved_source", ctypes.c_uint32),
        ("arm4_boolean_destination", ctypes.c_uint32),
        ("arm4_zero_saved_target", ctypes.c_uint32),
        ("arm4_nonzero_state", ctypes.c_uint32),
        ("arm4_nonzero_state_destination", ctypes.c_uint32),
        ("arm4_nonzero_helper", ctypes.c_uint32),
        ("arm4_saved_destination", ctypes.c_uint32),
        ("arm5_entry", ctypes.c_uint32),
        ("arm5_boolean_destination", ctypes.c_uint32),
        ("arm5_state", ctypes.c_uint32),
        ("arm5_state_destination", ctypes.c_uint32),
        ("arm5_helper", ctypes.c_uint32),
        ("arm5_saved_source", ctypes.c_uint32),
        ("arm5_saved_destination", ctypes.c_uint32),
        ("continuation", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "state-arms45.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_transition_state_arms_74f60_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.arm4_entry, plan.arm4_saved_source,
            plan.arm4_boolean_destination, plan.arm4_zero_saved_target,
            plan.arm4_nonzero_state, plan.arm4_nonzero_state_destination,
            plan.arm4_nonzero_helper, plan.arm4_saved_destination) == \
        (0x74f60, 0x504d88, 0x504da8, 0x78090, 5, 0x504d7c,
         0x77e60, 0x504d88)
    assert (plan.arm5_entry, plan.arm5_boolean_destination, plan.arm5_state,
            plan.arm5_state_destination, plan.arm5_helper,
            plan.arm5_saved_source, plan.arm5_saved_destination,
            plan.continuation) == \
        (0x74fa0, 0x504da8, 6, 0x504d7c, 0x77e60, 14, 0x504d88,
         0x75134)

    choose_zero = recovered.recovered_match_transition_arm4_zero_saved
    choose_zero.argtypes = [ctypes.c_uint32]
    choose_zero.restype = ctypes.c_uint32
    assert [choose_zero(value) for value in (0, 1, 0xffffffff)] == [1, 0, 0]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   74f60:")
    end = listing.index("   74fc8:")
    block = listing[start:end]
    for evidence in (
            "ld\t0x504d88,g4", "st\tr6,0x504da8",
            "call\t0x78090", "st\tg14,0x504d88",
            "st\tr7,0x504d7c", "call\t0x77e60"):
        if evidence not in block:
            raise AssertionError(f"state-arm 4/5 evidence missing: {evidence}")

print("PASS: 0x74f60-0x74fc4 match-transition state arms")
