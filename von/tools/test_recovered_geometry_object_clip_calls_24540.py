#!/usr/bin/env python3
"""Validate the four 0x701a0 calls prepared at 0x24540."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("clip_dispatch", ctypes.c_uint32),
        ("selected_pointer", ctypes.c_uint32),
        ("frame_selected_offset", ctypes.c_uint32),
        ("frame_pointer_offset", ctypes.c_uint32),
        ("frame_constants", ctypes.c_uint32 * 2),
        ("control_address", ctypes.c_uint32),
        ("control_value", ctypes.c_uint32),
        ("frame_publish_address", ctypes.c_uint32),
        ("frame_pointer_address", ctypes.c_uint32),
        ("fifo_address", ctypes.c_uint32),
        ("call_count", ctypes.c_uint32),
        ("call_argument", (ctypes.c_uint32 * 7) * 4),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "clip_calls.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2",
        str(pathlib.Path(__file__).parents[1] / "i960" /
            "recovered_geometry_object_clip_calls_24540.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    build = lib.recovered_geometry_object_clip_calls_plan
    build.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    build(0x12345678, 0x89ABCDEF, ctypes.byref(plan))
    assert (plan.clip_dispatch, plan.selected_pointer,
            plan.frame_selected_offset,
            plan.frame_pointer_offset, list(plan.frame_constants),
            plan.control_address, plan.control_value,
            plan.frame_publish_address, plan.frame_pointer_address,
            plan.fifo_address, plan.call_count) == (
        0x701A0, 0x12345678, 0x50, 0x54, [0x084553F, 1],
        0x800010, 0x101, 0x804000, 0x804004, 0x884000, 4)
    assert [list(row) for row in plan.call_argument] == [
        [0xc2040000, 0x431c0000, 0x3f800000, 0xc2040000,
         0x43130000, 0x3f800000, 0x400028],
        [0x89abcdef, 0x431c0000, 0x3f800000, 0x89abcdef,
         0x43130000, 0x3f800000, 0x400028],
        [0xc2040000, 0x43130000, 0x3f800000, 0x89abcdef,
         0x43130000, 0x3f800000, 0x400028],
        [0xc2040000, 0x431c0000, 0x3f800000, 0x89abcdef,
         0x431c0000, 0x3f800000, 0x400028],
    ]

print("PASS: 0x24540 object clip calls")
