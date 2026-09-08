#!/usr/bin/env python3
"""Validate the phase-substate dispatcher at i960 0x75450."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_phase_substate_dispatch_75450.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("state_register", ctypes.c_uint32),
        ("state_subtract", ctypes.c_uint32),
        ("state_lower_bound", ctypes.c_uint32),
        ("status_source", ctypes.c_uint32),
        ("status_subtract", ctypes.c_uint32),
        ("status_lower_bound", ctypes.c_uint32),
        ("status_upper_bound", ctypes.c_uint32),
        ("dispatch_table", ctypes.c_uint32),
        ("dispatch_count", ctypes.c_uint32),
        ("dispatch_target", ctypes.c_uint32 * 14),
        ("reject_target", ctypes.c_uint32),
        ("local_arm", ctypes.c_uint32 * 5),
        ("selected_status", ctypes.c_uint32 * 5),
        ("status_destination", ctypes.c_uint32),
        ("counter_destination", ctypes.c_uint32),
        ("counter_value", ctypes.c_uint32),
        ("continuation", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "substate-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_phase_substate_dispatch_75450_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.state_register, plan.state_subtract, plan.state_lower_bound,
            plan.status_source, plan.status_subtract, plan.status_lower_bound,
            plan.status_upper_bound, plan.dispatch_table,
            plan.dispatch_count, plan.reject_target,
            plan.status_destination, plan.counter_destination,
            plan.counter_value, plan.continuation) == \
        (4, 3, 1, 0x504d94, 4, 1, 13, 0x75474, 14, 0x754e4,
         0x504d94, 0x504db8, 10, 0x75cf0)
    assert list(plan.dispatch_target) == [
        0x754ac, 0x754e4, 0x754b4, 0x754e4, 0x754e4, 0x75cc4,
        0x754e4, 0x754bc, 0x754e4, 0x754e4, 0x754e4, 0x754e4,
        0x754c4, 0x754cc]
    assert list(plan.local_arm) == [0x754ac, 0x754b4, 0x754bc,
                                    0x754c4, 0x754cc]
    assert list(plan.selected_status) == [5, 1, 8, 14, 15]

    index = recovered.recovered_match_phase_substate_index
    index.argtypes = [ctypes.c_uint32]
    index.restype = ctypes.c_uint32
    assert [index(value) for value in (4, 5, 17)] == [0, 1, 13]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   75450:")
    end = listing.index("   754ac:")
    block = listing[start:end]
    for evidence in (
            "subo\t3,r4,g4", "cmpobl\t1,g4,0x754e8",
            "ld\t0x504d94,g4", "subo\t4,g4,g4",
            "cmpobl\t13,g4,0x754e4", "ld\t0x75474[g4*4],g4",
            "bx\t(g4)", ".word\t0x000754ac",
            ".word\t0x00075cc4", ".word\t0x000754cc"):
        if evidence not in block:
            raise AssertionError(f"substate-dispatch evidence missing: {evidence}")

print("PASS: 0x75450-0x754a8 phase-substate dispatcher")
