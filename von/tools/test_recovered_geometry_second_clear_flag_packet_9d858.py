#!/usr/bin/env python3
"""Validate the 0x9d858 second clear-flag geometry packet."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("object_1e2", ctypes.c_int16),
        ("derived_packet_word", ctypes.c_uint32),
        ("fifo_address", ctypes.c_uint32),
        ("fifo_word_count", ctypes.c_uint32),
        ("fifo_word", ctypes.c_uint32 * 9),
        ("board_readback_address", ctypes.c_uint32),
        ("published_pointer_address", ctypes.c_uint32),
        ("published_pointer_offset", ctypes.c_uint32),
        ("object_flag_1dd", ctypes.c_uint32),
        ("frame_value", ctypes.c_uint32),
        ("control_address", ctypes.c_uint32),
        ("control_value", ctypes.c_uint32),
        ("frame_publish_address", ctypes.c_uint32),
        ("frame_slot_offset", ctypes.c_uint32),
        ("frame_word", ctypes.c_uint32 * 2),
        ("frame_tail_offset", ctypes.c_uint32),
        ("frame_tail", ctypes.c_uint32 * 2),
        ("frame_variant", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "second_clear.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2",
        str(pathlib.Path(__file__).parents[1] / "i960" /
            "recovered_geometry_second_clear_flag_packet_9d858.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    build = lib.recovered_geometry_second_clear_flag_packet_plan
    build.argtypes = [
        ctypes.c_int16, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.c_uint32, ctypes.POINTER(Plan),
    ]

    def run(flag):
        plan = Plan()
        build(-2345, 0x3f13579b, flag, 0x12345678, 0x802008,
              ctypes.byref(plan))
        return plan

    plan = run(0)
    assert (plan.object_1e2, plan.derived_packet_word,
            plan.fifo_address, plan.fifo_word_count,
            list(plan.fifo_word)) == (
        -2345, 0x3f13579b, 0x884000, 9,
        [19, 0x3f13579b, 0x40a00000, 0x3f800000,
         18, 0x3f800000, 0, 0, 58])
    assert (plan.frame_slot_offset, list(plan.frame_word),
            plan.frame_tail_offset, list(plan.frame_tail),
            plan.frame_variant) == (0x50, [0x12345678, 0x40005c],
                                     0x58, [0x084553f, 1], 0)

    plan = run(1)
    assert (plan.frame_slot_offset, list(plan.frame_word),
            plan.frame_tail_offset, plan.frame_variant) == (
        0x60, [0x12345678, 0x40002c], 0x68, 1)

print("PASS: 0x9d858 second clear-flag geometry packet")
