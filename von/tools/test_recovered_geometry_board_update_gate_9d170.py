#!/usr/bin/env python3
"""Validate the 0x9d170 geometry-board update gate and prefix."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("state_word", ctypes.c_uint32),
        ("state_bit0", ctypes.c_uint32),
        ("control_address", ctypes.c_uint32),
        ("control_value", ctypes.c_uint32),
        ("frame_address", ctypes.c_uint32 * 2),
        ("frame_value", ctypes.c_uint32),
        ("fifo_address", ctypes.c_uint32),
        ("update_enabled", ctypes.c_uint32),
        ("prefix_count", ctypes.c_uint32),
        ("prefix", ctypes.c_uint32 * 5),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "board_gate.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2",
        str(pathlib.Path(__file__).parents[1] / "i960" /
            "recovered_geometry_board_update_gate_9d170.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    build = lib.recovered_geometry_board_update_gate_plan
    build.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    build(0x12345679, ctypes.byref(plan))
    assert (plan.state_bit0, plan.control_address, plan.control_value,
            list(plan.frame_address), plan.frame_value, plan.fifo_address,
            plan.update_enabled, plan.prefix_count,
            list(plan.prefix)) == (
        1, 0x800090, 0x909, [0x804000, 0x804004], 0x44160000,
        0x884000, 1, 5,
        [5, 55, 0x3e23d70a, 0xbdf92c60, 0x3f800000])

    # bno skips the FIFO prefix when state bit 0 is clear.
    plan = Plan()
    build(0x12345678, ctypes.byref(plan))
    assert (plan.state_bit0, plan.update_enabled, plan.prefix_count) == (0, 0, 0)

print("PASS: 0x9d170 geometry-board update gate")
