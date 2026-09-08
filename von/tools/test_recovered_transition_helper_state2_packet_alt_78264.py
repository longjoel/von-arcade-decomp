#!/usr/bin/env python3
"""Validate the alternate state-2 packet at i960 0x78264."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_helper_state2_packet_alt_78264.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("entry", ctypes.c_uint32),
        ("linked_object_offset", ctypes.c_uint32),
        ("fifo", ctypes.c_uint32),
        ("selector_first", ctypes.c_uint32),
        ("selector_second", ctypes.c_uint32),
        ("selector_final", ctypes.c_uint32),
        ("halfword_mask", ctypes.c_uint32),
        ("adjustment", ctypes.c_uint32),
        ("fixed_float", ctypes.c_uint32),
        ("response_first_register", ctypes.c_uint32),
        ("response_second_register", ctypes.c_uint32),
        ("object_x_offset", ctypes.c_uint32),
        ("object_y_offset", ctypes.c_uint32),
        ("classifier", ctypes.c_uint32),
        ("result_table", ctypes.c_uint32),
        ("continuation", ctypes.c_uint32),
        ("result_counter", ctypes.c_uint32),
        ("result_counter_destination", ctypes.c_uint32),
        ("result_destination", ctypes.c_uint32),
        ("return_address", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "state2-alt.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_transition_helper_state2_packet_alt_78264_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.entry, plan.linked_object_offset, plan.fifo,
            plan.selector_first, plan.selector_second, plan.selector_final,
            plan.halfword_mask, plan.adjustment, plan.fixed_float,
            plan.response_first_register, plan.response_second_register,
            plan.object_x_offset, plan.object_y_offset, plan.classifier,
            plan.result_table, plan.continuation, plan.result_counter,
            plan.result_counter_destination, plan.result_destination,
            plan.return_address) == \
        (0x78264, 0x74, 0x884000, 29, 30, 10, 0xffff, 0xffffc000,
         0x43160000, 1, 5, 0x10, 8, 0x73508, 0x72960, 0x78334, 5,
         0x504db8, 0x504d94, 0x78348)

    adjust = recovered.recovered_transition_helper_state2_alt_adjust
    adjust.argtypes = [ctypes.c_uint32]
    adjust.restype = ctypes.c_uint32
    assert [adjust(value) for value in (0, 0x4000, 0xffff)] == [
        0xc000, 0, 0xbfff]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   78264:")
    end = listing.index("   7834c:")
    block = listing[start:end]
    for evidence in (
            "ldos\t0x184(g2),g4", "mov\t29,g13",
            "lda\t0xffffc000,g6", "and\tg3,g4,g4",
            "lda\t0x43160000,g4", "ld\t0x884000,g1",
            "mov\t30,g13", "ld\t0x10(g2),g4",
            "mov\t10,g13", "ld\t0x72960[g0*4],g4",
            "mov\t5,g13", "st\tg13,0x504db8",
            "st\tg4,0x504d94", "ret"):
        if evidence not in block:
            raise AssertionError(f"alternate state2 evidence missing: {evidence}")

print("PASS: 0x78264-0x78348 alternate state-2 packet")
