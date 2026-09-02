#!/usr/bin/env python3
"""Validate the 0x9d730 second flagged geometry state packet."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("flag_bit1", ctypes.c_uint32),
        ("state_word", ctypes.c_int16),
        ("state_low_nibble", ctypes.c_uint32),
        ("masked_state_parameter", ctypes.c_uint32),
        ("derived_packet_word", ctypes.c_uint32),
        ("fifo_address", ctypes.c_uint32),
        ("fifo_word_count", ctypes.c_uint32),
        ("fifo_word", ctypes.c_uint32 * 13),
        ("board_readback_address", ctypes.c_uint32),
        ("published_pointer_address", ctypes.c_uint32),
        ("published_pointer_offset", ctypes.c_uint32),
        ("control_address", ctypes.c_uint32),
        ("control_value", ctypes.c_uint32),
        ("frame_publish_address", ctypes.c_uint32),
        ("frame_word", ctypes.c_uint32 * 2),
        ("frame_tail", ctypes.c_uint32 * 2),
        ("frame_value", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "flagged_state.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2",
        str(pathlib.Path(__file__).parents[1] / "i960" /
            "recovered_geometry_second_flagged_state_packet_9d730.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    build = lib.recovered_geometry_second_flagged_state_packet_plan
    build.argtypes = [
        ctypes.c_uint32, ctypes.c_int16, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.c_uint32, ctypes.POINTER(Plan),
    ]

    plan = Plan()
    build(2, -9, 0x3f123456, 0x12345678, 0x802008,
          ctypes.byref(plan))
    assert (plan.flag_bit1, plan.state_word, plan.state_low_nibble,
            plan.masked_state_parameter, plan.derived_packet_word,
            plan.fifo_address, plan.fifo_word_count,
            list(plan.fifo_word)) == (
        1, -9, 7, 0x7000, 0x3f123456, 0x884000, 13, [
            29, 0x7000, 0x40400000,
            19, 0x3f123456, 0x42200000, 0x3f123456, 0x3f800000,
            18, 0x3f800000, 0, 0, 58,
        ])
    assert (plan.board_readback_address, plan.published_pointer_address,
            plan.published_pointer_offset, plan.control_address,
            plan.control_value, plan.frame_publish_address,
            list(plan.frame_word), list(plan.frame_tail),
            plan.frame_value) == (
        0x802008, 0x801008, 0x34, 0x800010, 0x101, 0x804000,
        [0x12345678, 0x40009c], [0x084553f, 1], 0x12345678)

    plan = Plan()
    build(1, 0x1234, 0, 0xabcdef01, 0x802008, ctypes.byref(plan))
    assert (plan.flag_bit1, plan.fifo_word_count,
            list(plan.frame_word)) == (0, 0, [0xabcdef01, 0x40009c])

print("PASS: 0x9d730 second flagged geometry state packet")
