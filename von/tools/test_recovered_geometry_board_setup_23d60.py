#!/usr/bin/env python3
"""Validate the deterministic setup-prefix contract at 0x23d60."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("control_address", ctypes.c_uint32),
        ("control_value", ctypes.c_uint32),
        ("secondary_control_address", ctypes.c_uint32 * 2),
        ("secondary_control_value", ctypes.c_uint32),
        ("fifo_address", ctypes.c_uint32),
        ("fifo_word_count", ctypes.c_uint32),
        ("fifo_word", ctypes.c_uint32 * 20),
        ("derived_word", ctypes.c_uint32),
        ("board_readback_address", ctypes.c_uint32),
        ("published_pointer_address", ctypes.c_uint32),
        ("published_pointer_offset", ctypes.c_uint32),
        ("fixed_pointer_bias", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "board_setup.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2",
        str(pathlib.Path(__file__).parents[1] / "i960" /
            "recovered_geometry_board_setup_23d60.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    setup = lib.recovered_geometry_board_setup_prefix_plan
    setup.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    setup(0x12345678, 0x802008, ctypes.byref(plan))
    assert (plan.control_address, plan.control_value,
            list(plan.secondary_control_address),
            plan.secondary_control_value) == (
        0x800090, 0x909, [0x804000, 0x804004], 0x44160000)
    assert (plan.fifo_address, plan.fifo_word_count) == (0x884000, 20)
    assert list(plan.fifo_word) == [
        5, 16, 18, 0xbd5a740e, 0x3e8f5c29, 0x3f800000,
        19, 0x12345678, 0x3ada740e, 0x3ada740e, 0x3f800000, 5,
        19, 0x12345678, 0x41100000, 0x3f800000, 18, 0, 0, 58,
    ]
    assert (plan.derived_word, plan.board_readback_address,
            plan.published_pointer_address, plan.published_pointer_offset,
            plan.fixed_pointer_bias) == (0x12345678, 0x802008,
                                          0x801008, 0x34, 0x34)

print("PASS: 0x23d60 geometry-board setup prefix")
