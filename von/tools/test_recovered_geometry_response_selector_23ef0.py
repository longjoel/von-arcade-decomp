#!/usr/bin/env python3
"""Validate the 0x23ef0 geometry response/state selector."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("fifo_read_address", ctypes.c_uint32),
        ("table_address", ctypes.c_uint32),
        ("table_index", ctypes.c_uint32),
        ("selected_value", ctypes.c_uint32),
        ("fallback_pointer", ctypes.c_uint32),
        ("route", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "selector.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2",
        str(pathlib.Path(__file__).parents[1] / "i960" /
            "recovered_geometry_response_selector_23ef0.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    select = lib.recovered_geometry_response_selector_plan
    select.argtypes = [
        ctypes.c_int16, ctypes.c_int16, ctypes.c_int16, ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(Plan),
    ]

    table = (ctypes.c_uint32 * 32)(*[0x70000000 + i for i in range(32)])

    def run(ca0, ca2, ca8, state):
        plan = Plan()
        select(ca0, ca2, ca8, state, table, ctypes.byref(plan))
        return plan

    plan = run(20, 30, 100, 3)
    assert (plan.route, plan.fallback_pointer,
            plan.selected_value) == (4, 0x49C980, 0x49C980)
    plan = run(20, 30, 100, 2)
    assert (plan.route, plan.fallback_pointer,
            plan.selected_value) == (3, 0x40005C, 0x40005C)

    plan = run(20, 10, 100, 7)
    assert (plan.route, plan.table_index, plan.selected_value) == (0, 14, 0x7000000E)
    plan = run(30, 10, 100, 7)
    assert (plan.route, plan.table_index, plan.selected_value) == (1, 7, 0x70000007)
    plan = run(40, 10, 100, 7)
    assert (plan.route, plan.table_index, plan.selected_value) == (2, 3, 0x70000003)
    plan = run(50, 10, 100, 7)
    assert (plan.route, plan.fallback_pointer,
            plan.selected_value) == (4, 0x49C980, 0x49C980)

    # Equality at each threshold takes the later branch, as in cmpibge.
    plan = run(25, 10, 100, 1)
    assert plan.route == 1
    plan = run(100, 10, 100, 1)
    assert plan.route == 4

print("PASS: 0x23ef0 geometry response selector")
