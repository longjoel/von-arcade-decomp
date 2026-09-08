#!/usr/bin/env python3
"""Validate the bounded result-prefix at 0x72ea0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_state_result_prefix_72ea0.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("mode_global", ctypes.c_uint32),
        ("state_global", ctypes.c_uint32),
        ("input_port", ctypes.c_uint32),
        ("input_mask", ctypes.c_uint32),
        ("record_base", ctypes.c_uint32),
        ("record_stride", ctypes.c_uint32),
        ("record_byte_offsets", ctypes.c_uint32 * 2),
        ("result_addresses", ctypes.c_uint32 * 2),
        ("state_gate", ctypes.c_uint32),
        ("mode_gate", ctypes.c_uint32),
        ("emit_targets", ctypes.c_uint32 * 2),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "result-prefix.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_state_result_prefix_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.mode_global, plan.state_global, plan.input_port,
            plan.input_mask, plan.record_base, plan.record_stride,
            plan.state_gate, plan.mode_gate) == \
        (0x503a08, 0x5039f4, 0x1a14002, 1, 0x5024f0, 0x100, 2, 4)
    assert list(plan.record_byte_offsets) == [0x514, 0x515]
    assert list(plan.result_addresses) == [0x504dac, 0x504db0]
    assert list(plan.emit_targets) == [0x882a8, 0x88318]

    offset = recovered.recovered_match_state_result_record_offset
    offset.argtypes = [ctypes.c_uint32]
    offset.restype = ctypes.c_uint32
    assert [offset(v) for v in (0, 1, 2, 3)] == [0, 0x100, 0, 0x100]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   72ea0:")
    end = listing.index("   72f48:")
    block = listing[start:end]
    for evidence in (
            "ld\t0x503a08,g4", "ld\t0x5039f4,g4",
            "ldob\t0x1a14002,g4", "and\t1,g4,g4",
            "lda\t0x5024f0(g5),g5", "ldob\t0x514(g5),g4",
            "ldob\t0x515(g5),g4", "st\tg4,0x504dac",
            "st\tg4,0x504db0", "bal\t0x882a8", "bal\t0x88318"):
        if evidence not in block:
            raise AssertionError(f"result-prefix listing evidence missing: {evidence}")

print("PASS: 0x72ea0 match-state result prefix")
