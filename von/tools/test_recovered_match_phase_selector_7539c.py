#!/usr/bin/env python3
"""Validate the nested phase selector at i960 0x7539c."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_phase_selector_7539c.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("frame_source_offset", ctypes.c_uint32),
        ("frame_gate_subtract", ctypes.c_uint32),
        ("frame_gate_bound", ctypes.c_uint32),
        ("state_source_register", ctypes.c_uint32),
        ("state_gate", ctypes.c_uint32),
        ("status_source", ctypes.c_uint32),
        ("status_decrement", ctypes.c_uint32),
        ("status_lower_bound", ctypes.c_uint32),
        ("status_upper_bound", ctypes.c_uint32),
        ("dispatch_table", ctypes.c_uint32),
        ("dispatch_count", ctypes.c_uint32),
        ("dispatch_target", ctypes.c_uint32 * 15),
        ("reject_target", ctypes.c_uint32),
        ("first_arm", ctypes.c_uint32),
        ("last_arm", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "phase-selector7539c.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_phase_selector_7539c_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.frame_source_offset, plan.frame_gate_subtract,
            plan.frame_gate_bound, plan.state_source_register,
            plan.state_gate, plan.status_source, plan.status_decrement,
            plan.status_lower_bound, plan.status_upper_bound,
            plan.dispatch_table, plan.dispatch_count, plan.reject_target,
            plan.first_arm, plan.last_arm) == \
        (0x40, 2, 5, 4, 2, 0x504d94, 1, 1, 14, 0x753c8, 15,
         0x75cf8, 0x75404, 0x75434)
    assert list(plan.dispatch_target) == [
        0x75404, 0x75cf8, 0x75cf8, 0x75cf8, 0x75cf8,
        0x7540c, 0x75cf8, 0x75414, 0x75cf8, 0x75cf8,
        0x75424, 0x75cf8, 0x75cf8, 0x7542c, 0x75434]

    index = recovered.recovered_match_phase_selector_index
    index.argtypes = [ctypes.c_uint32]
    index.restype = ctypes.c_uint32
    assert [index(value) for value in (1, 2, 14, 15)] == [0, 1, 13, 14]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   7539c:")
    end = listing.index("   75404:")
    block = listing[start:end]
    for evidence in (
            "ld\t0x40(fp),g5", "subo\t2,g5,g6",
            "cmpobge\t5,g6,0x75628", "cmpibl\t2,r4,0x75450",
            "ld\t0x504d94,g4", "subo\t1,g4,g4",
            "cmpobl\t14,g4,0x75cf8", "ld\t0x753c8[g4*4],g4",
            "bx\t(g4)", ".word\t0x00075404",
            ".word\t0x00075434"):
        if evidence not in block:
            raise AssertionError(f"nested phase-selector evidence missing: {evidence}")

print("PASS: 0x7539c-0x75400 nested phase selector")
