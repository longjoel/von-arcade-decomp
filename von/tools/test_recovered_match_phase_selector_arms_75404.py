#!/usr/bin/env python3
"""Validate local phase-selector arms at i960 0x75404-0x75444."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_phase_selector_arms_75404.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("count", ctypes.c_uint32),
        ("entry", ctypes.c_uint32 * 6),
        ("selected_status", ctypes.c_uint32 * 6),
        ("status_destination", ctypes.c_uint32),
        ("counter_destination", ctypes.c_uint32),
        ("counter_value", ctypes.c_uint32),
        ("common_status_store", ctypes.c_uint32),
        ("direct_status_store", ctypes.c_uint32),
        ("continuation", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "phase-arms.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_phase_selector_arms_75404_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert plan.count == 6
    assert list(plan.entry) == [0x75404, 0x7540c, 0x75414,
                                0x75424, 0x7542c, 0x75434]
    assert list(plan.selected_status) == [5, 4, 10, 9, 16, 17]
    assert (plan.status_destination, plan.counter_destination,
            plan.counter_value, plan.common_status_store,
            plan.direct_status_store, plan.continuation) == \
        (0x504d94, 0x504db8, 10, 0x75438, 0x75418, 0x75cf8)
    counter = recovered.recovered_match_phase_selector_counter_value
    counter.restype = ctypes.c_uint32
    assert counter() == 10

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   75404:")
    end = listing.index("   75450:")
    block = listing[start:end]
    for evidence in (
            "mov\t5,g2", "mov\t4,g2", "mov\t10,g2",
            "mov\t9,g2", "mov\t16,g2", "mov\t17,g2",
            "st\tg2,0x504d94", "st\tg2,0x504db8",
            "mov\t10,g2", "b\t0x75cf8"):
        if evidence not in block:
            raise AssertionError(f"phase-arm evidence missing: {evidence}")
    if "st\tg2,0x504d94" not in block:
        raise AssertionError("phase-arm status publication missing")

print("PASS: 0x75404-0x7544c phase-selector arms")
