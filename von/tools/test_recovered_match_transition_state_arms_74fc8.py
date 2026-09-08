#!/usr/bin/env python3
"""Validate the bounded state arms 6 and 7 at 0x74fc8 and 0x75048."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_transition_state_arms_74fc8.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("arm6_entry", ctypes.c_uint32), ("arm7_entry", ctypes.c_uint32),
        ("threshold_source", ctypes.c_uint32),
        ("threshold_99", ctypes.c_uint32),
        ("threshold_120", ctypes.c_uint32),
        ("object_state_offset", ctypes.c_uint32),
        ("mode_source", ctypes.c_uint32),
        ("boolean_destination", ctypes.c_uint32),
        ("saved_destination", ctypes.c_uint32),
        ("state_destination", ctypes.c_uint32),
        ("transition_destination", ctypes.c_uint32),
        ("state3", ctypes.c_uint32), ("state6", ctypes.c_uint32),
        ("low_path_helper", ctypes.c_uint32),
        ("high_path_helper", ctypes.c_uint32),
        ("shared_high_path", ctypes.c_uint32),
        ("shared_post_action", ctypes.c_uint32),
        ("continuation", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "state-arms67.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_transition_state_arms_74fc8_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.arm6_entry, plan.arm7_entry, plan.threshold_source,
            plan.threshold_99, plan.threshold_120, plan.object_state_offset,
            plan.mode_source, plan.boolean_destination, plan.saved_destination,
            plan.state_destination, plan.transition_destination,
            plan.state3, plan.state6) == \
        (0x74fc8, 0x75048, 0x504dc0, 99, 120, 0x64, 0x504d80,
         0x504da8, 0x504d88, 0x504d7c, 0x504da4, 3, 6)
    assert (plan.low_path_helper, plan.high_path_helper,
            plan.shared_high_path, plan.shared_post_action,
            plan.continuation) == \
        (0x77e60, 0x78090, 0x7508c, 0x750e0, 0x75134)

    threshold = recovered.recovered_match_transition_state_threshold
    threshold.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    threshold.restype = ctypes.c_uint32
    assert [threshold(value, 99) for value in (99, 100)] == [0, 1]
    assert [threshold(value, 120) for value in (120, 121)] == [0, 1]
    decrement = recovered.recovered_match_transition_saved_decrement
    decrement.argtypes = [ctypes.c_uint32]
    decrement.restype = ctypes.c_uint32
    assert [decrement(value) for value in (0, 1, 2, 9)] == [1, 1, 1, 8]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   74fc8:")
    end = listing.index("   75134:")
    block = listing[start:end]
    for evidence in (
            "st\tr6,0x504da4", "ld\t0x64(g0),g4",
            "ld\t0x504d80,g4", "lda\t0x63,r6",
            "call\t0x77e60", "call\t0x78090",
            "st\tr7,0x504e1c", "b\t0x75134"):
        if evidence not in block:
            raise AssertionError(f"state-arm 6/7 evidence missing: {evidence}")
    for evidence in ("call\t0x77e60", "st\tg14,0x504da4",
                     "st\tg14,0x504da8", "st\tr6,0x504d7c"):
        if evidence not in block:
            raise AssertionError(f"state-arm 7 low-path evidence missing: {evidence}")

print("PASS: 0x74fc8-0x75130 match-transition state arms")
