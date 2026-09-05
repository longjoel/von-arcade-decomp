#!/usr/bin/env python3
"""Validate the recovered 0x18538 ring-queue pump plan."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("queue_base", ctypes.c_uint32),
        ("head_addr", ctypes.c_uint32),
        ("tail_addr", ctypes.c_uint32),
        ("port0", ctypes.c_uint32),
        ("port1", ctypes.c_uint32),
        ("drain_addr", ctypes.c_uint32),
        ("drain_src", ctypes.c_uint32),
        ("queue_mask", ctypes.c_uint32),
        ("pops", ctypes.c_uint32),
        ("emit0", ctypes.c_uint32),
        ("emit1", ctypes.c_uint32),
        ("new_head", ctypes.c_uint32),
        ("drains", ctypes.c_uint32),
        ("new_drain", ctypes.c_uint32),
        ("emit_drain", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "queue-pump.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_queue_pump_18538.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_queue_pump_plan
    plan_fn.argtypes = [ctypes.c_uint32] * 5 + [ctypes.POINTER(Plan)]

    # Nonempty queue pops one byte to both ports, head wraps mod 16.
    plan = Plan()
    plan_fn(3, 7, 0x41, 0, 0, ctypes.byref(plan))
    assert (plan.queue_base, plan.head_addr, plan.tail_addr, plan.port0,
            plan.port1, plan.drain_addr, plan.drain_src,
            plan.queue_mask) == (
        0x504C60, 0x504C70, 0x504C74, 0x1C00008, 0x503312,
        0x504C78, 0x502512, 15
    )
    assert (plan.pops, plan.emit0, plan.emit1, plan.new_head,
            plan.drains) == (1, 0x41, 0x41, 4, 0)

    plan_fn(15, 0, 0x142, 0, 0, ctypes.byref(plan))
    assert (plan.emit0, plan.new_head) == (0x42, 0)

    # Empty queue with a stale drain refreshes and emits the low byte.
    plan_fn(5, 5, 0, 0x100, 0x142, ctypes.byref(plan))
    assert (plan.pops, plan.drains, plan.new_drain,
            plan.emit_drain) == (0, 1, 0x142, 0x42)

    # Empty queue with a fresh drain stays idle.
    plan_fn(5, 5, 0, 0x142, 0x142, ctypes.byref(plan))
    assert (plan.pops, plan.drains) == (0, 0)

print("PASS: 0x18538 ring-queue pump plan")
