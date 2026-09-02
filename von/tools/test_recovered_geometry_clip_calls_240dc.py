#!/usr/bin/env python3
"""Validate the four raw 0x701a0 calls prepared at 0x240dc."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("clip_dispatch", ctypes.c_uint32),
        ("frame_zero_offset", ctypes.c_uint32),
        ("frame_selected_offset", ctypes.c_uint32),
        ("frame_constants", ctypes.c_uint32 * 2),
        ("control_address", ctypes.c_uint32),
        ("control_value", ctypes.c_uint32),
        ("frame_publish_address", ctypes.c_uint32),
        ("frame_publish_offset", ctypes.c_uint32),
        ("call_count", ctypes.c_uint32),
        ("call_argument", (ctypes.c_uint32 * 7) * 4),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "clip_calls.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2",
        str(pathlib.Path(__file__).parents[1] / "i960" /
            "recovered_geometry_clip_calls_240dc.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    build = lib.recovered_geometry_clip_calls_plan
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    build(0x12345678, 0x89abcdef, ctypes.byref(plan))
    assert (plan.clip_dispatch, plan.frame_zero_offset,
            plan.frame_selected_offset, list(plan.frame_constants),
            plan.control_address, plan.control_value,
            plan.frame_publish_address, plan.frame_publish_offset,
            plan.call_count) == (
        0x701A0, 0xC0, 0xC4, [0x084553F, 1],
        0x800010, 0x101, 0x804000, 0x400028, 4)
    assert [list(row) for row in plan.call_argument] == [
        [0xc2040000, 0x43310000, 0x3f800000, 0x12345678,
         0x43310000, 0x3f800000, 0x400028],
        [0xc2040000, 0x431f0000, 0x3f800000, 0x12345678,
         0x3f800000, 0x3f800000, 0x400028],
        [0xc2040000, 0x43310000, 0x3f800000, 0xc2040000,
         0x431f0000, 0x3f800000, 0x400028],
        [0x89abcdef, 0x43310000, 0x3f800000, 0x89abcdef,
         0x431f0000, 0x3f800000, 0x400028],
    ]

print("PASS: 0x240dc geometry clip calls")
