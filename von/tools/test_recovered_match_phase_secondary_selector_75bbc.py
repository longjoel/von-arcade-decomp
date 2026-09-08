#!/usr/bin/env python3
"""Validate the parallel phase selector at i960 0x75bbc."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_phase_secondary_selector_75bbc.c"
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
        ("dispatch_target", ctypes.c_uint32 * 15),
        ("default_target", ctypes.c_uint32),
        ("local_arm", ctypes.c_uint32 * 5),
        ("selected_status", ctypes.c_uint32 * 5),
        ("common_writer", ctypes.c_uint32),
        ("next_selector", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "secondary-selector.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_phase_secondary_selector_75bbc_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.state_register, plan.state_subtract, plan.state_lower_bound,
            plan.status_source, plan.status_subtract, plan.status_upper_bound,
            plan.dispatch_table, plan.dispatch_count,
            plan.default_target, plan.common_writer, plan.next_selector) == \
        (4, 3, 1, 0x504d94, 1, 14, 0x75be0, 15, 0x75c54,
         0x75cf0, 0x75c58)
    assert list(plan.dispatch_target) == [
        0x75c1c, 0x75c54, 0x75c54, 0x75c54, 0x75c54, 0x75c24,
        0x75c54, 0x75cc4, 0x75c54, 0x75c54, 0x75c2c, 0x75c54,
        0x75c54, 0x75c34, 0x75c3c]
    assert list(plan.local_arm) == [0x75c1c, 0x75c24, 0x75c2c,
                                    0x75c34, 0x75c3c]
    assert list(plan.selected_status) == [5, 4, 9, 16, 17]

    index = recovered.recovered_match_phase_secondary_selector_index
    index.argtypes = [ctypes.c_uint32]
    index.restype = ctypes.c_uint32
    assert [index(value) for value in (1, 2, 15)] == [0, 1, 14]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   75bbc:")
    end = listing.index("   75c58:")
    block = listing[start:end]
    for evidence in (
            "subo\t3,r4,g4", "cmpobl\t1,g4,0x75c58",
            "ld\t0x504d94,g4", "subo\t1,g4,g4",
            "cmpobl\t14,g4,0x75c54", "ld\t0x75be0[g4*4],g4",
            "bx\t(g4)", ".word\t0x00075c1c",
            ".word\t0x00075cc4", ".word\t0x00075c3c"):
        if evidence not in block:
            raise AssertionError(f"secondary-selector evidence missing: {evidence}")

print("PASS: 0x75bbc-0x75c54 parallel phase selector")
