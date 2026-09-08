#!/usr/bin/env python3
"""Validate the fixed frame-service initializer at 0x2be30."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_frame_service_initialize_2be30.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("profile_helper", ctypes.c_uint32),
        ("fifo_prefix", ctypes.c_uint32 * 2),
        ("clear_address", ctypes.c_uint32 * 2),
        ("service_helper", ctypes.c_uint32),
        ("service_arg0", ctypes.c_uint32),
        ("service_arg1", ctypes.c_uint32),
        ("old_counter", ctypes.c_uint32),
        ("next_counter", ctypes.c_uint32),
        ("counter_reset", ctypes.c_uint32),
        ("phase_clear", ctypes.c_uint32),
        ("phase_before", ctypes.c_uint32),
        ("phase_after", ctypes.c_uint32),
        ("dispatch_index", ctypes.c_uint32),
        ("dispatch_table_address", ctypes.c_uint32),
        ("dispatch_target", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "frame-service.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_geometry_frame_service_initialize_plan
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    function(4, 7, ctypes.byref(plan))
    assert (plan.profile_helper, list(plan.fifo_prefix),
            list(plan.clear_address), plan.service_helper,
            plan.service_arg0, plan.service_arg1) == (
        0x295d0, [8, 16], [0x50427a, 0x503c7a], 0x2a990, 0xd000, 0)
    assert (plan.old_counter, plan.next_counter, plan.counter_reset,
            plan.phase_clear, plan.phase_after, plan.dispatch_index,
            plan.dispatch_table_address, plan.dispatch_target) == (
        4, 5, 0, 0, 7, 7, 0x2bee4, 0x2d4e4)

    function(0xb4, 11, ctypes.byref(plan))
    assert (plan.next_counter, plan.counter_reset, plan.phase_clear,
            plan.phase_after, plan.dispatch_index, plan.dispatch_target) == (
        0, 1, 1, 12, 0, 0x2c118)

    listing = LISTING.read_text(encoding="utf-8")
    block = listing[listing.index("   2be30:"):listing.index("   2bee4:")]
    for evidence in ("call\t0x295d0", "mov\t8,r14", "mov\t16,r15",
                     "0x50427a", "0x503c7a", "0xd000", "call\t0x2a990",
                     "0xb4"):
        if evidence not in block:
            raise AssertionError(f"2be30 listing evidence missing: {evidence}")

print("PASS: 0x2be30 frame-service initializer plan")
