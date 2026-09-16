#!/usr/bin/env python3
"""Validate the bounded state-dispatch/integrator slice at 0x32810."""

import ctypes
import pathlib
import struct
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_object_update_32810.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

HANDLERS = [
    0x0002F580, 0x0002F930, 0x0002E450, 0x0002E590, 0x0002E6F0,
    0x0002E860, 0x0002E990, 0x0002EAA0, 0x0002EBB0, 0x0002ECE0,
    0x0002EF90, 0x0002F010, 0x0002F360, 0x0002F260, 0x0002F460,
    0x0002FA20, 0x0002FB20, 0x0002FD50, 0x00031910, 0x00031AB0,
    0x00031D20, 0x00032120, 0x0002FE30, 0x0002FF80, 0x000300C0,
    0x00030230, 0x00032330, 0x000303E0, 0x00030460, 0x00030590,
    0x00030420, 0x00030660, 0x00030C20, 0x00030D40, 0x00030E40,
    0x00030FF0, 0x00031210, 0x000313E0, 0x000315A0, 0x000316D0,
    0x000317F0, 0x000324E0, 0x00032540,
]


class Plan(ctypes.Structure):
    _fields_ = [
        ("state_field_offset", ctypes.c_uint32),
        ("state_table_address", ctypes.c_uint32),
        ("state_table_stride", ctypes.c_uint32),
        ("state_handler_count", ctypes.c_uint32),
        ("state_max", ctypes.c_uint32),
        ("action_field_offset", ctypes.c_uint32),
        ("action_max", ctypes.c_uint32),
        ("state_handler", ctypes.c_uint32 * 43),
    ]


class Position(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_uint32),
        ("z", ctypes.c_uint32),
        ("vx", ctypes.c_uint32),
        ("vz", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "object-update-32810.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))

    plan_fn = recovered.recovered_object_update_32810_plan
    plan_fn.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    plan_fn(ctypes.byref(plan))
    assert (plan.state_field_offset, plan.state_table_address,
            plan.state_table_stride, plan.state_handler_count, plan.state_max,
            plan.action_field_offset, plan.action_max) == \
        (0x172, 0x32560, 16, 43, 42, 0x1b2, 13)
    assert list(plan.state_handler) == HANDLERS

    selector = recovered.recovered_object_update_32810_state_selector
    selector.argtypes = [ctypes.c_uint32]
    selector.restype = ctypes.c_uint32
    assert selector(0x1234ABCD) == 0xABCD

    in_range = recovered.recovered_object_update_32810_state_in_range
    in_range.argtypes = [ctypes.c_uint32]
    in_range.restype = ctypes.c_uint32
    for state, expected in ((0, 1), (42, 1), (43, 0), (0x8000, 0),
                            (0xFFFF, 0), (0x10000, 1)):
        assert in_range(state) == expected, (state, in_range(state))

    integrate = recovered.recovered_object_update_32810_integrate_position
    integrate.argtypes = [ctypes.POINTER(Position)]
    def fbits(value):
        return struct.unpack("<I", struct.pack("<f", value))[0]
    position = Position(x=fbits(10.0), z=fbits(20.0), vx=fbits(5.0), vz=fbits(-3.0))
    integrate(ctypes.byref(position))
    assert (position.x, position.z) == (fbits(15.0), fbits(17.0)), (position.x, position.z)

    listing = LISTING.read_text(encoding="utf-8")
    dispatch = listing[listing.index("   33ae8:"):listing.index("   33b1c:")]
    for evidence in (
            "ldos\t0x172(r8),g4", "bbs\t15,g4,0x33b1c",
            "cmpibg\tg4,g5,0x33b1c", "ld\t0x32560(g4),g1", "callx\t(g1)"):
        if evidence not in dispatch:
            raise AssertionError(f"state-dispatch listing evidence missing: {evidence}")
    integrator = listing[listing.index("   363bc:"):listing.index("   363e0:")]
    for evidence in ("st\tg4,0x8(r8)", "st\tg4,0x10(r8)"):
        if evidence not in integrator:
            raise AssertionError(f"integrator listing evidence missing: {evidence}")

print("PASS: 0x32810 state dispatch and position integrator")
