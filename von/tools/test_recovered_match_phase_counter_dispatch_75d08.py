#!/usr/bin/env python3
"""Validate the phase-counter dispatcher at i960 0x75d08."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_phase_counter_dispatch_75d08.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("state_register", ctypes.c_uint32),
        ("state_bound", ctypes.c_uint32),
        ("status_source", ctypes.c_uint32),
        ("status_subtract", ctypes.c_uint32),
        ("status_lower_bound", ctypes.c_uint32),
        ("status_upper_bound", ctypes.c_uint32),
        ("dispatch_table", ctypes.c_uint32),
        ("dispatch_count", ctypes.c_uint32),
        ("dispatch_target", ctypes.c_uint32 * 14),
        ("default_target", ctypes.c_uint32),
        ("local_arm", ctypes.c_uint32 * 5),
        ("selected_status", ctypes.c_uint32 * 5),
        ("common_writer", ctypes.c_uint32),
        ("counter_return", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "counter-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_phase_counter_dispatch_75d08_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.state_register, plan.state_bound, plan.status_source,
            plan.status_subtract, plan.status_lower_bound,
            plan.status_upper_bound, plan.dispatch_table,
            plan.dispatch_count, plan.default_target,
            plan.common_writer, plan.counter_return) == \
        (4, 6, 0x504d94, 4, 1, 13, 0x75d28, 14, 0x75d88,
         0x75cf0, 0x75cf8)
    assert list(plan.dispatch_target) == [
        0x75d60, 0x75d68, 0x75d88, 0x75d88, 0x75d88, 0x75d70,
        0x75d78, 0x75d88, 0x75d88, 0x75d88, 0x75d88, 0x75d88,
        0x75d80, 0x75cec]
    assert list(plan.local_arm) == [0x75d60, 0x75d68, 0x75d70,
                                    0x75d78, 0x75d80]
    assert list(plan.selected_status) == [6, 1, 11, 8, 14]

    index = recovered.recovered_match_phase_counter_dispatch_index
    index.argtypes = [ctypes.c_uint32]
    index.restype = ctypes.c_uint32
    assert [index(value) for value in (4, 5, 17)] == [0, 1, 13]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   75d08:")
    end = listing.index("   75d60:")
    block = listing[start:end]
    for evidence in (
            "cmpibge\t6,r4,0x75d88", "ld\t0x504d94,g4",
            "subo\t4,g4,g4", "cmpobl\t13,g4,0x75d88",
            "ld\t0x75d28[g4*4],g4", "bx\t(g4)",
            ".word\t0x00075d60", ".word\t0x00075cec"):
        if evidence not in block:
            raise AssertionError(f"counter-dispatch evidence missing: {evidence}")

print("PASS: 0x75d08-0x75d5c phase-counter dispatcher")
