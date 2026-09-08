#!/usr/bin/env python3
"""Validate the bounded phase-advance update at i960 0x75300."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_phase_advance_update_75300.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("phase_source_register", ctypes.c_uint32),
        ("zero_phase_target", ctypes.c_uint32),
        ("phase_index_source", ctypes.c_uint32),
        ("phase_limit_table", ctypes.c_uint32),
        ("phase_index_destination", ctypes.c_uint32),
        ("phase_increment", ctypes.c_uint32),
        ("coordinate_source", ctypes.c_uint32),
        ("positive_coordinate_offset", ctypes.c_uint32),
        ("negative_coordinate_offset", ctypes.c_uint32),
        ("classifier", ctypes.c_uint32),
        ("result_table", ctypes.c_uint32),
        ("result_destination", ctypes.c_uint32),
        ("state_helper", ctypes.c_uint32),
        ("returned_state_destination", ctypes.c_uint32),
        ("phase_state_destination", ctypes.c_uint32),
        ("terminal_counter_destination", ctypes.c_uint32),
        ("terminal_counter", ctypes.c_uint32),
        ("return_address", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "phase-advance.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_phase_advance_update_75300_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.phase_source_register, plan.zero_phase_target,
            plan.phase_index_source, plan.phase_limit_table,
            plan.phase_index_destination, plan.phase_increment,
            plan.coordinate_source, plan.positive_coordinate_offset,
            plan.negative_coordinate_offset, plan.classifier,
            plan.result_table, plan.result_destination, plan.state_helper,
            plan.returned_state_destination, plan.phase_state_destination,
            plan.terminal_counter_destination, plan.terminal_counter,
            plan.return_address) == \
        (5, 0x7539c, 0x504d74, 0x504de0, 0x504d74, 1, 0x504d64,
         0x1800, 0xffffe800, 0x73508, 0x72780, 0x504d94, 0x79050,
         0x504db4, 0x504d74, 0x504db8, 30, 0x75398)

    increment = recovered.recovered_match_phase_index_increment
    increment.argtypes = [ctypes.c_uint32]
    increment.restype = ctypes.c_uint32
    assert [increment(value) for value in (0, 1, 0xffffffff)] == [1, 2, 0]
    offset = recovered.recovered_match_phase_coordinate_offset
    offset.argtypes = [ctypes.c_int32]
    offset.restype = ctypes.c_uint32
    assert [offset(value) for value in (-1, 0, 1)] == [0xffffe800, 0x1800, 0x1800]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   75300:")
    end = listing.index("   7539c:")
    block = listing[start:end]
    for evidence in (
            "cmpibe\t0,r5,0x7539c", "ld\t0x504d74,g5",
            "ld\t0x504de0,g4", "addo\tg5,1,g5",
            "st\tg5,0x504d74", "ld\t0x504d70,g4",
            "ldos\t0x504d64,g0", "lda\t0x1800(g0),g0",
            "lda\t0xffffe800(g0),g0", "bal\t0x73508",
            "ld\t0x72780[g0*4],g4", "st\tg4,0x504d94",
            "call\t0x79050", "st\tg14,0x504db4",
            "st\tg14,0x504d74", "st\tg2,0x504db8",
            "ret"):
        if evidence not in block:
            raise AssertionError(f"phase-advance evidence missing: {evidence}")

print("PASS: 0x75300-0x75398 phase-advance update")
