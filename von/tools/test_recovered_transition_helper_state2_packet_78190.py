#!/usr/bin/env python3
"""Validate the bounded state-2 packet body at i960 0x78190."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_helper_state2_packet_78190.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("linked_object_offset", ctypes.c_uint32),
        ("object_x_offset", ctypes.c_uint32),
        ("object_y_offset", ctypes.c_uint32),
        ("fifo", ctypes.c_uint32),
        ("selector_first", ctypes.c_uint32),
        ("selector_second", ctypes.c_uint32),
        ("selector_delta", ctypes.c_uint32),
        ("halfword_mask", ctypes.c_uint32),
        ("positive_adjustment", ctypes.c_uint32),
        ("negative_adjustment", ctypes.c_uint32),
        ("fixed_float", ctypes.c_uint32),
        ("response_first_register", ctypes.c_uint32),
        ("response_second_register", ctypes.c_uint32),
        ("board_x_offset", ctypes.c_uint32),
        ("board_y_offset", ctypes.c_uint32),
        ("selector_final", ctypes.c_uint32),
        ("classifier", ctypes.c_uint32),
        ("result_table", ctypes.c_uint32),
        ("positive_branch", ctypes.c_uint32),
        ("negative_branch", ctypes.c_uint32),
        ("continuation", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "state2-packet.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_transition_helper_state2_packet_78190_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.linked_object_offset, plan.object_x_offset,
            plan.object_y_offset, plan.fifo, plan.selector_first,
            plan.selector_second, plan.selector_delta, plan.halfword_mask,
            plan.positive_adjustment, plan.negative_adjustment,
            plan.fixed_float, plan.response_first_register,
            plan.response_second_register, plan.board_x_offset,
            plan.board_y_offset, plan.selector_final, plan.classifier,
            plan.result_table, plan.positive_branch, plan.negative_branch,
            plan.continuation) == \
        (0x74, 0x184, 8, 0x884000, 29, 30, 10, 0xffff, 0x4000,
         0xffffc000, 0x43160000, 1, 5, 0x10, 8, 10, 0x73508,
         0x72930, 0x78190, 0x78264, 0x78334)

    adjust = recovered.recovered_transition_helper_state2_adjust
    adjust.argtypes = [ctypes.c_uint32, ctypes.c_int32]
    adjust.restype = ctypes.c_uint32
    assert [adjust(value, 0x4000) for value in (0, 0xc000, 0xffff)] == [
        0x4000, 0, 0x3fff]
    assert [adjust(value, -0x4000) for value in (0x4000, 0, 0xffff)] == [
        0, 0xc000, 0xbfff]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   78190:")
    end = listing.index("   78264:")
    block = listing[start:end]
    for evidence in (
            "ldos\t0x184(g2),g4", "mov\t29,g13",
            "setbit\t14,0,g6", "ldos\t0x184(g2),g5",
            "and\tg3,g4,g4", "lda\t0x43160000,g4",
            "ld\t0x884000,g1", "ld\t0x8(g2),g7",
            "mov\t30,g13", "ld\t0x884000,g5",
            "ld\t0x10(g2),g4", "subr\tg1,g7,g7",
            "ld\t0x10(g0),g4", "ld\t0x8(g0),g5",
            "mov\t10,g13", "ldos\t0x184(g0),g5",
            "bal\t0x73508", "ld\t0x72930[g0*4],g4",
            "b\t0x78334"):
        if evidence not in block:
            raise AssertionError(f"state2-packet evidence missing: {evidence}")

print("PASS: 0x78190-0x78260 state-2 packet body")
