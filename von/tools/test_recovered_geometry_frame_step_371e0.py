#!/usr/bin/env python3
"""Validate the bounded per-frame prefix at 0x371e0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_frame_step_371e0.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("global_gate_address", ctypes.c_uint32),
        ("object_pointer_offset", ctypes.c_uint32),
        ("timer_offsets", ctypes.c_uint32 * 2),
        ("fixed_point_offsets", ctypes.c_uint32 * 2),
        ("phase_offset", ctypes.c_uint32),
        ("secondary_state_offset", ctypes.c_uint32),
        ("dispatch_table_address", ctypes.c_uint32),
        ("dispatch_helper_when_gated", ctypes.c_uint32),
        ("dispatch_helper_when_clear", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "frame-step.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_geometry_frame_step_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.global_gate_address, plan.object_pointer_offset,
            plan.phase_offset, plan.secondary_state_offset,
            plan.dispatch_table_address, plan.dispatch_helper_when_gated,
            plan.dispatch_helper_when_clear) == \
        (0x503a60, 0x6c, 0x172, 0x198, 0x37130, 0x25040, 0x24f98)
    assert list(plan.timer_offsets) == [0x1db, 0x1dc]
    assert list(plan.fixed_point_offsets) == [0x32, 0x34]

    timer = recovered.recovered_geometry_frame_timer_step
    timer.argtypes = [ctypes.c_uint8]
    timer.restype = ctypes.c_uint8
    phase = recovered.recovered_geometry_frame_phase_index
    phase.argtypes = [ctypes.c_uint32]
    phase.restype = ctypes.c_int32
    assert [timer(v) for v in (0, 1, 0xff)] == [0, 0, 0xfe]
    assert phase(0x0001) == 1
    assert phase(0xffff) == -1

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   371e0:")
    end = listing.index("   3738c:")
    block = listing[start:end]
    for evidence in (
            "ld\t0x503a60,g4", "ld\t0x6c(g0),g5",
            "ldob\t0x1db(r4),g4", "stob\tg4,0x1db(r4)",
            "ldob\t0x1dc(r4),g4", "stob\tg4,0x1dc(r4)",
            "ldos\t0x32(r4),g5", "stos\tg5,0x32(r4)",
            "ldos\t0x34(r4),g4", "stos\tg4,0x34(r4)",
            "ldos\t0x172(r4),g4", "ld\t0x37130(g4),g1",
            "callx\t(g1)"):
        if evidence not in block:
            raise AssertionError(f"frame-step listing evidence missing: {evidence}")

print("PASS: 0x371e0 geometry frame-step prefix")
