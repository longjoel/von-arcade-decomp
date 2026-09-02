#!/usr/bin/env python3
"""Validate the 0x24eb4 object-state packet and status latch."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("lookup_helper", ctypes.c_uint32),
        ("lookup_arg0", ctypes.c_uint32),
        ("lookup_arg1", ctypes.c_uint32),
        ("fifo_address", ctypes.c_uint32),
        ("packet_count", ctypes.c_uint32),
        ("packet", ctypes.c_uint32 * 7),
        ("board_readback_address", ctypes.c_uint32),
        ("response_consumer", ctypes.c_uint32),
        ("status_byte", ctypes.c_uint32),
        ("status_threshold", ctypes.c_uint32),
        ("status_global_active", ctypes.c_uint32),
        ("state_word", ctypes.c_uint32),
        ("current_status", ctypes.c_uint32),
        ("current_frame_value", ctypes.c_uint32),
        ("status_store", ctypes.c_uint32),
        ("status_update_helper", ctypes.c_uint32),
        ("status_update_arg", ctypes.c_uint32),
        ("status_update_called", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "state_packet.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2",
        str(pathlib.Path(__file__).parents[1] / "i960" /
            "recovered_geometry_object_state_packet_24eb4.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    build = lib.recovered_geometry_object_state_packet_plan
    build.argtypes = [
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Plan),
    ]

    helper = (ctypes.c_uint32 * 3)(0x11111111, 0x22222222, 0x33333333)
    obj = (ctypes.c_uint32 * 3)(0xaaaaaaaa, 0xbbbbbbbb, 0xcccccccc)

    def run(status_byte, active, state, current_status, frame):
        plan = Plan()
        build(helper, obj, 0x802008, status_byte, active, state,
              current_status, frame, ctypes.byref(plan))
        return plan

    plan = run(0x7f, 0, 0x1234, 0, 0xdeadbeef)
    assert (plan.lookup_helper, plan.lookup_arg0, plan.lookup_arg1,
            plan.fifo_address, plan.packet_count,
            list(plan.packet), plan.board_readback_address,
            plan.response_consumer) == (
        0x1cac8, 10, 24, 0x884000, 7,
        [31, 0x11111111, 0xaaaaaaaa, 0x22222222, 0xbbbbbbbb,
         0x33333333, 0xcccccccc], 0x802008, 0x1e370)
    assert (plan.status_store, plan.status_update_helper,
            plan.status_update_arg, plan.status_update_called) == (
        0x101, 0x1f080, 0, 1)

    plan = run(0xc9, 1, 0x1236, 0, 0xdeadbeef)
    assert (plan.status_store, plan.status_update_arg,
            plan.status_update_called) == (2, 2, 1)
    plan = run(0xc9, 1, 0x1235, 0, 0xdeadbeef)
    assert plan.status_store == 0

    # Threshold equality is inactive; an existing latch is preserved.
    plan = run(0xc8, 1, 2, 0x55, 0xdeadbeef)
    assert (plan.status_store, plan.status_update_called) == (0x55, 0)
    plan = run(0x10, 0, 2, 0x55, 0xdeadbeef)
    assert (plan.status_store, plan.status_update_called) == (0x55, 0)

print("PASS: 0x24eb4 object-state packet")
