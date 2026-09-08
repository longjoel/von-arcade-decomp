#!/usr/bin/env python3
"""Validate the bounded entry prefix of transition helper 0x78120."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_helper_prefix_78120.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("threshold_source", ctypes.c_uint32),
        ("threshold", ctypes.c_uint32),
        ("one_time_gate", ctypes.c_uint32),
        ("linked_object_offset", ctypes.c_uint32),
        ("input_source", ctypes.c_uint32),
        ("input_mask", ctypes.c_uint32),
        ("input_upper_bound", ctypes.c_uint32),
        ("state_destination", ctypes.c_uint32),
        ("state_value", ctypes.c_uint32),
        ("bit_source_register", ctypes.c_uint32),
        ("low_bit_helper", ctypes.c_uint32),
        ("high_bit_helper", ctypes.c_uint32),
        ("bypass_target", ctypes.c_uint32),
        ("state2_body", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "helper-prefix.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_transition_helper_prefix_78120_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.threshold_source, plan.threshold, plan.one_time_gate,
            plan.linked_object_offset, plan.input_source, plan.input_mask,
            plan.input_upper_bound, plan.state_destination, plan.state_value,
            plan.bit_source_register, plan.low_bit_helper,
            plan.high_bit_helper, plan.bypass_target, plan.state2_body) == \
        (0x504dc0, 99, 0x504dd0, 0x74, 0x504d6c, 0xffff, 0x7ffe,
         0x504d7c, 2, 5, 0x78448, 0x78488, 0x7834c, 0x78190)

    threshold = recovered.recovered_transition_helper_threshold_pass
    threshold.argtypes = [ctypes.c_uint32]
    threshold.restype = ctypes.c_uint32
    assert [threshold(value) for value in (98, 99, 100)] == [1, 1, 0]
    mask = recovered.recovered_transition_helper_mask_input
    mask.argtypes = [ctypes.c_uint32]
    mask.restype = ctypes.c_uint32
    assert [mask(value) for value in (0, 0x12345678, 0xffffffff)] == [
        0, 0x5678, 0xffff]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   78120:")
    end = listing.index("   78190:")
    block = listing[start:end]
    for evidence in (
            "ld\t0x504dc0,g4", "lda\t0x63,g13",
            "cmpi\tg4,g13", "ld\t0x74(g0),g2",
            "ld\t0x504dd0,g4", "cmpibne\t0,g4,0x7834c",
            "ldos\t0x504d6c,g5", "lda\t0xffff,g3",
            "lda\t0x7ffe,g13", "and\tg3,g4,g4",
            "st\tg13,0x504d7c", "bbs\t15,g5,0x78188",
            "bal\t0x78448", "bal\t0x78488", "ret"):
        if evidence not in block:
            raise AssertionError(f"helper-prefix evidence missing: {evidence}")

print("PASS: 0x78120-0x7818c transition-helper prefix")
