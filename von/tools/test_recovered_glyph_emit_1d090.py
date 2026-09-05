#!/usr/bin/env python3
"""Validate the recovered 0x1d090 plane-0 glyph emitter plan."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("masked_byte", ctypes.c_uint32),
        ("biased_byte", ctypes.c_int32),
        ("control_selector", ctypes.c_uint32),
        ("control_tiles", ctypes.c_uint32 * 2),
        ("glyph_table", ctypes.c_uint32),
        ("table_index", ctypes.c_int32),
        ("plane_base", ctypes.c_uint32),
        ("glyph_attr", ctypes.c_uint32),
        ("tile_addresses", ctypes.c_uint32 * 2),
        ("column_wrap", ctypes.c_uint32),
        ("next_column", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "glyph-emit.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_glyph_emit_1d090.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_glyph_emit_plan
    plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                        ctypes.c_uint32, ctypes.POINTER(Plan)]

    # Printable 'A' renders table glyph 33 as a vertical tile pair.
    plan = Plan()
    plan_fn(0x41, 8, 12, ctypes.byref(plan))
    assert (plan.masked_byte, plan.biased_byte,
            plan.control_selector) == (0x41, 33, 0)
    assert (plan.glyph_table, plan.table_index, plan.plane_base,
            plan.glyph_attr) == (0x02EA0FD0, 33, 0x01000000, 0xC000)
    assert list(plan.tile_addresses) == [0x01000610, 0x01000690]
    assert (plan.column_wrap, plan.next_column) == (61, 9)

    # Biased values 0x4b/0x54 select the fixed control tile pairs.
    plan_fn(0x6B, 8, 12, ctypes.byref(plan))
    assert plan.control_selector == 1
    assert list(plan.control_tiles) == [0x837C, 0x837D]
    plan_fn(0x74, 8, 12, ctypes.byref(plan))
    assert plan.control_selector == 2
    assert list(plan.control_tiles) == [0x837E, 0x837F]

    # Control bytes keep negative table indices; high bit is masked off.
    plan_fn(0x05, 8, 12, ctypes.byref(plan))
    assert (plan.masked_byte, plan.biased_byte, plan.table_index) == (
        5, -27, -27)
    plan_fn(0x85, 8, 12, ctypes.byref(plan))
    assert (plan.masked_byte, plan.biased_byte) == (5, -27)

    # Column holds past the wrap limit instead of advancing.
    plan_fn(0x41, 62, 12, ctypes.byref(plan))
    assert plan.next_column == 62

print("PASS: 0x1d090 glyph emitter plan")
