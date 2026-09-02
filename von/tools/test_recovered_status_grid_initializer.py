#!/usr/bin/env python3
"""Validate the 0x227b0 4x8 status grid initializer."""
import ctypes
import pathlib
import subprocess
import tempfile


class Cell(ctypes.Structure):
    _fields_ = [("column", ctypes.c_uint32), ("row", ctypes.c_uint32)]


class Plan(ctypes.Structure):
    _fields_ = [("selected", ctypes.c_uint32),
                ("period", ctypes.c_uint32),
                ("remainder", ctypes.c_uint32),
                ("source", ctypes.c_uint32),
                ("first_helper", ctypes.c_uint32),
                ("second_helper", ctypes.c_uint32),
                ("width", ctypes.c_uint32),
                ("height", ctypes.c_uint32),
                ("cell_count", ctypes.c_uint32),
                ("cell", Cell * 32)]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "grid.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_status_grid_initializer.c"), "-o", str(so)],
                   check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_status_grid_initializer_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    plan_fn(0x180, ctypes.byref(plan))
    assert (plan.selected, plan.period, plan.remainder, plan.source,
            plan.first_helper, plan.second_helper, plan.width, plan.height,
            plan.cell_count) == (1, 192, 0, 0x02FE8FC4, 0x1DE80,
                                  0x1DE00, 16, 8, 32)
    expected = [(column << 4, row << 3)
                for row in range(8) for column in range(4)]
    assert [(cell.column, cell.row) for cell in plan.cell] == expected

    plan_fn(0x181, ctypes.byref(plan))
    assert (plan.selected, plan.remainder) == (0, 1)

print("PASS: 0x227b0 status grid initializer")
