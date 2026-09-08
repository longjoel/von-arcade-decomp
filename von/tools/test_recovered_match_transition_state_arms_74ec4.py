#!/usr/bin/env python3
"""Validate the bounded first four state arms after 0x74e60."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_transition_state_arms_74ec4.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Arm(ctypes.Structure):
    _fields_ = [("entry", ctypes.c_uint32), ("threshold", ctypes.c_uint32),
                ("state", ctypes.c_uint32),
                ("boolean_destination", ctypes.c_uint32),
                ("state_destination", ctypes.c_uint32),
                ("writes_saved_value", ctypes.c_uint32),
                ("saved_value_source", ctypes.c_uint32),
                ("calls_helper", ctypes.c_uint32),
                ("helper", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


class Plan(ctypes.Structure):
    _fields_ = [("count", ctypes.c_uint32), ("arm", Arm * 4)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "state-arms.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_transition_state_arms_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert plan.count == 4
    assert [arm.entry for arm in plan.arm] == [0x74ec4, 0x74ef0,
                                                0x74f28, 0x74f3c]
    assert [arm.threshold for arm in plan.arm] == [120, 120, 120, 24]
    assert all(arm.state == 3 for arm in plan.arm)
    assert all(arm.boolean_destination == 0x504da8 for arm in plan.arm)
    assert all(arm.state_destination == 0x504d7c for arm in plan.arm)
    assert [arm.writes_saved_value for arm in plan.arm] == [0, 1, 0, 0]
    assert [arm.saved_value_source for arm in plan.arm] == [0, 14, 0, 0]
    assert [arm.calls_helper for arm in plan.arm] == [0, 1, 1, 1]
    assert [arm.helper for arm in plan.arm] == [0, 0x78120, 0x78120, 0x78120]
    assert all(arm.continuation == 0x75134 for arm in plan.arm)

    boolean = recovered.recovered_match_transition_arm_boolean
    boolean.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    boolean.restype = ctypes.c_uint32
    assert [boolean(value, 120) for value in (119, 120, 121)] == [0, 0, 1]
    assert [boolean(value, 24) for value in (23, 24, 25)] == [0, 0, 1]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   74ec4:")
    end = listing.index("   74f60:")
    block = listing[start:end]
    for evidence in (
            "shlo\t3,15,r6", "st\tg4,0x504da8",
            "st\tr7,0x504d7c", "st\tg14,0x504d88",
            "call\t0x78120", "b\t0x75134"):
        if evidence not in block:
            raise AssertionError(f"state-arm listing evidence missing: {evidence}")
    if "shlo\t3,15,r7" not in block:
        raise AssertionError("state-arm 3 threshold evidence missing")

print("PASS: 0x74ec4-0x74f5c match-transition state arms")
