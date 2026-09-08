#!/usr/bin/env python3
"""Validate the bounded call graph at 0x72c10."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_state_geometry_orchestrator_72c10.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("state_global", ctypes.c_uint32),
        ("mode_global", ctypes.c_uint32),
        ("divisor_global", ctypes.c_uint32),
        ("object_gate_offset", ctypes.c_uint32),
        ("modulo_base", ctypes.c_uint32),
        ("modulo_threshold", ctypes.c_uint32),
        ("call_targets", ctypes.c_uint32 * 18),
        ("call_count", ctypes.c_uint32),
        ("final_pair_address", ctypes.c_uint32),
        ("final_status_address", ctypes.c_uint32),
        ("continuation", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "match-state-orchestrator.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_state_geometry_orchestrator_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.state_global, plan.mode_global, plan.divisor_global,
            plan.object_gate_offset, plan.modulo_base, plan.modulo_threshold,
            plan.call_count, plan.final_pair_address,
            plan.final_status_address, plan.continuation) == \
        (0x503a00, 0x5039f4, 0x504db4, 0x68, 30, 14, 18,
         0x504db0, 0x504dac, 0x72e94)
    assert list(plan.call_targets) == [
        0x76590, 0x77c40, 0x842d0, 0x74e60, 0x82ae0, 0x85080,
        0x7fca0, 0x807d0, 0x7ea10, 0x7f4d0, 0x810d0, 0x7dcc0,
        0x86960, 0x75200, 0x735d0, 0x73498, 0x76b00, 0x74860]
    bucket = recovered.recovered_match_state_geometry_phase_bucket
    bucket.argtypes = [ctypes.c_uint32]
    bucket.restype = ctypes.c_uint32
    assert bucket(0) == 0
    assert bucket(59) == 29
    assert bucket(60) == 0

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   72c10:")
    end = listing.index("   72e94:")
    block = listing[start:end]
    for evidence in (
            "ld\t0x5039f4,g4", "ld\t0x503a00,g4",
            "remo\t30,g4,g4", "cmpobl\t14,g4",
            "call\t0x76590", "call\t0x77c40", "call\t0x842d0",
            "call\t0x74e60", "call\t0x82ae0", "call\t0x85080",
            "call\t0x807d0", "call\t0x735d0", "bal\t0x73498",
            "call\t0x76b00", "call\t0x74860",
            "ldq\t0x504db0,g4", "ld\t0x504dac,g0"):
        if evidence not in block:
            raise AssertionError(f"orchestrator listing evidence missing: {evidence}")

print("PASS: 0x72c10 match-state geometry orchestrator")
