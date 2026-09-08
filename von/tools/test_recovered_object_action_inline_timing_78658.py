#!/usr/bin/env python3
"""Validate the inline timing route at i960 0x78658."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_object_action_inline_timing_78658.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("object_state_offset", ctypes.c_uint32),
        ("status_dispatcher", ctypes.c_uint32),
        ("threshold_source", ctypes.c_uint32),
        ("current_source", ctypes.c_uint32),
        ("validity_constant", ctypes.c_uint32),
        ("status_destination", ctypes.c_uint32),
        ("status_value", ctypes.c_uint32),
        ("action5_target", ctypes.c_uint32),
        ("action10_target", ctypes.c_uint32),
        ("return_address", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "inline-timing.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_object_action_inline_timing_78658_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.object_state_offset, plan.status_dispatcher,
            plan.threshold_source, plan.current_source,
            plan.validity_constant, plan.status_destination,
            plan.status_value, plan.action5_target, plan.action10_target,
            plan.return_address) == \
        (0x64, 0x784c8, 0x504dd6, 0x504d60, 0x40340000, 0x504d84,
         1, 0x783c8, 0x78408, 0x786c0)
    route = recovered.recovered_object_action_inline_timing_route
    route.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
    route.restype = ctypes.c_uint32
    assert [route(value, 100) for value in (99, 100, 101)] == [
        0x78408, 0x783c8, 0x783c8]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   78658:")
    end = listing.index("   786d0:")
    block = listing[start:end]
    for evidence in (
            "ld\t0x64(g0),g0", "bal\t0x784c8",
            "ldis\t0x504dd6,g4", "cvtir\tg4,g6",
            "ld\t0x504d60,g5", "lda\t0x40340000,g3",
            "st\tg3,0x504d84", "bal\t0x783c8",
            "bal\t0x78408", "ret"):
        if evidence not in block:
            raise AssertionError(f"inline-timing evidence missing: {evidence}")

print("PASS: 0x78658-0x786c0 inline object-action timing")
