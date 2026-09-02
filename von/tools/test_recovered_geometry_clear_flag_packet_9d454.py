#!/usr/bin/env python3
"""Validate the 0x9d454 clear-flag geometry packet."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("object_1e4", ctypes.c_int16),
        ("derived_packet_word", ctypes.c_uint32),
        ("fifo_address", ctypes.c_uint32),
        ("fifo_word_count", ctypes.c_uint32),
        ("fifo_word", ctypes.c_uint32 * 9),
        ("board_readback_address", ctypes.c_uint32),
        ("published_pointer_address", ctypes.c_uint32),
        ("published_pointer_offset", ctypes.c_uint32),
        ("object_flag_1de", ctypes.c_uint32),
        ("frame_value", ctypes.c_uint32),
        ("control_address", ctypes.c_uint32),
        ("control_value", ctypes.c_uint32),
        ("frame_publish_address", ctypes.c_uint32),
        ("frame_word", ctypes.c_uint32 * 2),
        ("frame_tail", ctypes.c_uint32 * 2),
        ("frame_variant", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "clear_flag.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2",
        str(pathlib.Path(__file__).parents[1] / "i960" /
            "recovered_geometry_clear_flag_packet_9d454.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    derive = lib.recovered_geometry_clear_flag_derived_word
    derive.argtypes = [ctypes.c_int16]
    derive.restype = ctypes.c_uint32
    build = lib.recovered_geometry_clear_flag_packet_plan
    build.argtypes = [
        ctypes.c_int16, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.c_uint32, ctypes.POINTER(Plan),
    ]

    def run(flag):
        plan = Plan()
        build(-1234, 0x3f2468ac, flag, 0x12345678, 0x802008,
              ctypes.byref(plan))
        return plan

    assert [derive(value) for value in (-32768, -1234, -1, 0, 1, 1234, 32767)] == [
        0xc6e739ce, 0xc48b5295, 0xbf6739ce, 0x00000000,
        0x3f6739ce, 0x448b5295, 0x46e73800,
    ]

    plan = run(0)
    assert (plan.object_1e4, plan.derived_packet_word,
            plan.fifo_address, plan.fifo_word_count,
            list(plan.fifo_word)) == (
        -1234, 0x3f2468ac, 0x884000, 9,
        [19, 0x3f2468ac, 0x40a00000, 0x3f800000,
         18, 0x3f800000, 0, 0, 58])
    assert (plan.board_readback_address, plan.published_pointer_address,
            plan.published_pointer_offset, plan.control_address,
            plan.control_value, plan.frame_publish_address,
            list(plan.frame_word), list(plan.frame_tail),
            plan.frame_variant) == (
        0x802008, 0x801008, 0x34, 0x800010, 0x101, 0x804000,
        [0, 0x40005c], [0x084553f, 1], 0)

    plan = run(1)
    assert (list(plan.frame_word), plan.frame_variant,
            plan.frame_value) == ([0x12345678, 0x40002c], 1, 0x12345678)

print("PASS: 0x9d454 clear-flag geometry packet")
