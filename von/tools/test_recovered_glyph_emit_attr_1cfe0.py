#!/usr/bin/env python3
"""Validate the recovered 0x1cfe0 attributed glyph emitter plan."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("masked_byte", ctypes.c_uint32),
        ("biased_byte", ctypes.c_int32),
        ("zeroed", ctypes.c_uint32),
        ("glyph_table", ctypes.c_uint32),
        ("table_index", ctypes.c_int32),
        ("plane_base", ctypes.c_uint32),
        ("glyph_attr", ctypes.c_uint32),
        ("attr_forces_bank", ctypes.c_uint32),
        ("tile_addresses", ctypes.c_uint32 * 2),
        ("column_wrap", ctypes.c_uint32),
        ("next_column", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "glyph-emit-attr.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_glyph_emit_attr_1cfe0.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_glyph_emit_attr_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.c_uint32, ctypes.POINTER(Plan)]

    # Printable 'A' renders table glyph 33 with forced bank attributes.
    plan = Plan()
    plan_fn(0x41, 8, 12, ctypes.byref(plan))
    assert (plan.masked_byte, plan.biased_byte, plan.zeroed) == (
        0x41, 33, 0)
    assert (plan.glyph_table, plan.table_index, plan.plane_base,
            plan.glyph_attr, plan.attr_forces_bank) == (
        0x02EA0FD0, 33, 0x01002000, 0xC000, 1)
    assert list(plan.tile_addresses) == [0x01002610, 0x01002690]
    assert (plan.column_wrap, plan.next_column) == (61, 9)

    # Control bytes keep negative table indices; high bit is masked off.
    plan_fn(0x05, 8, 12, ctypes.byref(plan))
    assert (plan.masked_byte, plan.biased_byte, plan.table_index) == (
        5, -27, -27)

    # Column holds past the wrap limit instead of advancing.
    plan_fn(0x41, 62, 12, ctypes.byref(plan))
    assert plan.next_column == 62

print("PASS: 0x1cfe0 glyph emitter plan")
