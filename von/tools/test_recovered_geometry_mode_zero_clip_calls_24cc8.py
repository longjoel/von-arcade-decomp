#!/usr/bin/env python3
"""Validate the common 0x24cc8 mode-zero geometry clip sequence."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("fifo_address", ctypes.c_uint32),
        ("fifo_prefix_count", ctypes.c_uint32),
        ("fifo_prefix", ctypes.c_uint32 * 15),
        ("frame_pointer", ctypes.c_uint32),
        ("frame_pointer_offset", ctypes.c_uint32),
        ("frame_constant_address", ctypes.c_uint32),
        ("frame_constant", ctypes.c_uint32),
        ("frame_flag_offset", ctypes.c_uint32),
        ("frame_flag", ctypes.c_uint32),
        ("board_readback_address", ctypes.c_uint32),
        ("control_address", ctypes.c_uint32),
        ("control_value", ctypes.c_uint32),
        ("frame_publish_address", ctypes.c_uint32),
        ("clip_dispatch", ctypes.c_uint32),
        ("call_count", ctypes.c_uint32),
        ("call_argument", (ctypes.c_uint32 * 7) * 4),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "clip_calls.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2",
        str(pathlib.Path(__file__).parents[1] / "i960" /
            "recovered_geometry_mode_zero_clip_calls_24cc8.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    build = lib.recovered_geometry_mode_zero_clip_calls_plan
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    build(0x12345678, 0x802008, ctypes.byref(plan))
    assert (plan.fifo_address, plan.fifo_prefix_count,
            list(plan.fifo_prefix)) == (
        0x884000, 15, [
            5, 16, 18, 0xbe8f5c29, 0x3e8bf259, 0x3f800000,
            19, 0x3ada740e, 0x3ada740e, 0x3f800000,
            19, 0x428c0000, 0x41400000, 0x3f800000, 58,
        ])
    assert (plan.frame_pointer, plan.frame_pointer_offset,
            plan.frame_constant_address, plan.frame_constant,
            plan.frame_flag_offset, plan.frame_flag,
            plan.board_readback_address, plan.control_address,
            plan.control_value, plan.frame_publish_address,
            plan.clip_dispatch, plan.call_count) == (
        0x12345678, 0xb0, 0x40000c, 0x084553f, 0xbc, 1,
        0x802008, 0x800010, 0x101, 0x804000, 0x701a0, 4)
    assert [list(row) for row in plan.call_argument] == [
        [0xc2c40000, 0x432f0000, 0x3f800000, 0xc36f0000,
         0x432f0000, 0x3f800000, 0x400028],
        [0xc36f0000, 0x43170000, 0x3f800000, 0xc2c40000,
         0x43170000, 0x3f800000, 0x400028],
        [0xc36f0000, 0x432f0000, 0x3f800000, 0xc36f0000,
         0x43170000, 0x3f800000, 0x400028],
        [0xc2c40000, 0x43170000, 0x3f800000, 0xc36f0000,
         0x432f0000, 0x3f800000, 0x400028],
    ]

print("PASS: 0x24cc8 mode-zero geometry clip calls")
