#!/usr/bin/env python3
"""Validate the compact result-phase selector at i960 0x75230."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_result_phase_selector_75230.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("phase_source_register", ctypes.c_uint32),
        ("required_phase", ctypes.c_uint32),
        ("global_gate", ctypes.c_uint32),
        ("status_input", ctypes.c_uint32),
        ("status_bit", ctypes.c_uint32),
        ("bit_set_status", ctypes.c_uint32),
        ("bit_set_helper", ctypes.c_uint32),
        ("bit_set_counter", ctypes.c_uint32),
        ("table", ctypes.c_uint32), ("table_count", ctypes.c_uint32),
        ("table_index_subtract", ctypes.c_uint32),
        ("table_lower_bound", ctypes.c_uint32),
        ("table_upper_bound", ctypes.c_uint32),
        ("status_destination", ctypes.c_uint32),
        ("counter_destination", ctypes.c_uint32),
        ("counter_base", ctypes.c_uint32),
        ("bypass_target", ctypes.c_uint32),
        ("bit_set_target", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "phase-selector.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_result_phase_selector_75230_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.phase_source_register, plan.required_phase, plan.global_gate,
            plan.status_input, plan.status_bit, plan.bit_set_status,
            plan.bit_set_helper, plan.bit_set_counter, plan.table,
            plan.table_count, plan.table_index_subtract,
            plan.table_lower_bound, plan.table_upper_bound,
            plan.status_destination, plan.counter_destination,
            plan.counter_base, plan.bypass_target, plan.bit_set_target) == \
        (5, 1, 0x504d9c, 0x504e50, 6, 7, 0x79d60, 30, 0x75294, 12,
         8, 5, 11, 0x504d94, 0x504db8, 31, 0x75300, 0x75300)

    value = recovered.recovered_match_result_phase_table_value
    value.argtypes = [ctypes.c_uint32]
    value.restype = ctypes.c_uint32
    assert [value(index) for index in range(12)] == [4, 6, 1, 6, 5, 5,
                                                      5, 5, 5, 5, 6, 5]
    assert value(12) == 0
    counter = recovered.recovered_match_result_phase_counter
    counter.argtypes = [ctypes.c_uint32]
    counter.restype = ctypes.c_uint32
    assert [counter(index) for index in (0, 2, 11)] == [31, 33, 42]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   75230:")
    end = listing.index("   75300:")
    block = listing[start:end]
    for evidence in (
            "cmpibne\t1,r5,0x75300", "ld\t0x504d9c,g4",
            "cmpibe\t0,g4,0x75300", "ldob\t0x504e50,g4",
            "bbc\t6,g4,0x75270", "mov\t7,g2",
            "call\t0x79d60", "mov\t30,g2",
            "subo\t8,g5,g4", "ld\t0x75294[g4*4],g4",
            "st\tg2,0x504d94", "addo\t31,9,g2",
            "st\tg2,0x504db8", "ret"):
        if evidence not in block:
            raise AssertionError(f"phase-selector evidence missing: {evidence}")

print("PASS: 0x75230-0x752fc result-phase selector")
