#!/usr/bin/env python3
"""Validate the bounded transition gate at 0x74860."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_status_transition_gate_74860.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("status_address", ctypes.c_uint32),
        ("object_pointer_offset", ctypes.c_uint32),
        ("setup_helper", ctypes.c_uint32),
        ("mode_address", ctypes.c_uint32),
        ("mode_required", ctypes.c_uint32),
        ("status_flag_address", ctypes.c_uint32),
        ("status_flag_required", ctypes.c_uint32),
        ("window_low", ctypes.c_uint32),
        ("window_high", ctypes.c_uint32),
        ("fallback_pair_address", ctypes.c_uint32),
        ("dispatch_table", ctypes.c_uint32),
        ("dispatch_count", ctypes.c_uint32),
        ("dispatch_target", ctypes.c_uint32 * 23),
        ("external_route", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "transition-gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_status_transition_gate_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.status_address, plan.object_pointer_offset, plan.setup_helper,
            plan.mode_address, plan.mode_required, plan.status_flag_address,
            plan.status_flag_required, plan.window_low, plan.window_high,
            plan.fallback_pair_address, plan.dispatch_table,
            plan.dispatch_count, plan.external_route) == \
        (0x504e42, 0x74, 0x7d1f0, 0x504e28, 1, 0x504d98, 1,
         0x150000, 0x190000, 0x504d90, 0x7497c, 23, 0x854a0)
    assert list(plan.dispatch_target) == [
        0x74d20, 0x749dc, 0x74a30, 0x74a6c, 0x74aec, 0x74afc,
        0x74b10, 0x74b20, 0x74b30, 0x74b44, 0x74c24, 0x74c38,
        0x74c50, 0x74b54, 0x74b80, 0x74bb0, 0x74bdc, 0x74bec,
        0x74c00, 0x74c6c, 0x74c88, 0x74cc0, 0x74d20]
    window = recovered.recovered_match_status_transition_window
    window.argtypes = [ctypes.c_uint32]
    window.restype = ctypes.c_uint32
    assert [window(v) for v in (0x14ffff, 0x150000, 0x190000, 0x190001)] == [0, 1, 1, 0]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   74860:")
    end = listing.index("   749dc:")
    block = listing[start:end]
    for evidence in (
            "ldos\t0x504e42,g4", "call\t0x854a0",
            "call\t0x7d1f0", "ld\t0x504e28,g4",
            "ld\t0x504d98,g4", "lda\t0x150000,g13",
            "lda\t0x190000,g13", "ldq\t0x504d90,g0",
            "ld\t0x7497c[g4*4],g4"):
        if evidence not in block:
            raise AssertionError(f"transition-gate listing evidence missing: {evidence}")

print("PASS: 0x74860 match-status transition gate")
