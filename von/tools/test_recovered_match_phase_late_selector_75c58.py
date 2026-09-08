#!/usr/bin/env python3
"""Validate the late phase selector at i960 0x75c58."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_phase_late_selector_75c58.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("state_register", ctypes.c_uint32),
        ("state_subtract", ctypes.c_uint32),
        ("state_lower_bound", ctypes.c_uint32),
        ("status_source", ctypes.c_uint32),
        ("status_subtract", ctypes.c_uint32),
        ("status_upper_bound", ctypes.c_uint32),
        ("dispatch_table", ctypes.c_uint32),
        ("dispatch_count", ctypes.c_uint32),
        ("dispatch_target", ctypes.c_uint32 * 14),
        ("default_target", ctypes.c_uint32),
        ("local_arm", ctypes.c_uint32 * 5),
        ("selected_status", ctypes.c_uint32 * 5),
        ("next_dispatch", ctypes.c_uint32),
        ("common_writer", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "late-selector.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_phase_late_selector_75c58_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.state_register, plan.state_subtract, plan.state_lower_bound,
            plan.status_source, plan.status_subtract, plan.status_upper_bound,
            plan.dispatch_table, plan.dispatch_count,
            plan.default_target, plan.next_dispatch,
            plan.common_writer) == \
        (4, 5, 1, 0x504d94, 4, 13, 0x75c7c, 14, 0x75d04,
         0x75d08, 0x75cf0)
    assert list(plan.dispatch_target) == [
        0x75cb4, 0x75d04, 0x75cbc, 0x75d04, 0x75d04, 0x75cc4,
        0x75d04, 0x75cdc, 0x75d04, 0x75d04, 0x75d04, 0x75d04,
        0x75ce4, 0x75cec]
    assert list(plan.local_arm) == [0x75cb4, 0x75cbc, 0x75cc4,
                                    0x75cdc, 0x75ce4]
    assert list(plan.selected_status) == [5, 1, 10, 8, 14]

    index = recovered.recovered_match_phase_late_selector_index
    index.argtypes = [ctypes.c_uint32]
    index.restype = ctypes.c_uint32
    assert [index(value) for value in (4, 5, 17)] == [0, 1, 13]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   75c58:")
    end = listing.index("   75cb4:")
    block = listing[start:end]
    for evidence in (
            "subo\t5,r4,g4", "cmpobl\t1,g4,0x75d08",
            "ld\t0x504d94,g4", "subo\t4,g4,g4",
            "cmpobl\t13,g4,0x75d04", "ld\t0x75c7c[g4*4],g4",
            "bx\t(g4)", ".word\t0x00075cb4",
            ".word\t0x00075cc4", ".word\t0x00075cec"):
        if evidence not in block:
            raise AssertionError(f"late-selector evidence missing: {evidence}")

print("PASS: 0x75c58-0x75cb0 late phase selector")
