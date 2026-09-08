#!/usr/bin/env python3
"""Validate the bounded object-record dispatcher at 0x2b430."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_object_dispatch_2b430.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("object_address", ctypes.c_uint32),
        ("record_count", ctypes.c_uint32),
        ("slot_address", ctypes.c_uint32),
        ("slot_left", ctypes.c_uint32),
        ("slot_right", ctypes.c_uint32),
        ("route", ctypes.c_uint32),
        ("dispatch_index", ctypes.c_uint32),
        ("dispatch_target_address", ctypes.c_uint32),
        ("dispatch_count", ctypes.c_uint32),
        ("count_address", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "object-dispatch.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_geometry_object_dispatch_plan
    function.argtypes = [ctypes.c_uint32] * 6 + [ctypes.POINTER(Plan)]

    plan = Plan()
    function(7, 0, 3, 1, 9, 4, ctypes.byref(plan))
    assert (plan.object_address, plan.slot_address, plan.route,
            plan.dispatch_count, plan.dispatch_target_address) == (
        0x51C5B0 + 7 * 0x54, 0x51BB30 + 3 * 0x54, 0, 0, 0)

    function(7, 5, 3, 9, 9, 4, ctypes.byref(plan))
    assert (plan.route, plan.dispatch_target_address, plan.dispatch_count,
            plan.count_address) == (1, 0x6FD50, 5, 0x51BB30 + 3 * 0x54)

    function(7, 5, 3, 8, 9, 4, ctypes.byref(plan))
    assert (plan.route, plan.dispatch_target_address, plan.dispatch_count) == (
        2, 0x2B420 + 4 * 4, 5)

    listing = LISTING.read_text(encoding="utf-8")
    block = listing[listing.index("   2b430:"):listing.index("   2b500:")]
    for evidence in ("shlo\t2,r8", "0x51c5b0", "0x6fd50",
                     "cmpibl\tg5,g4", "callx", "0x2b420", "addo\tg4,1,g4"):
        if evidence not in block:
            raise AssertionError(f"2b430 listing evidence missing: {evidence}")

print("PASS: 0x2b430 object-record dispatcher plan")
