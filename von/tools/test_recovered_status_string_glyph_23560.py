#!/usr/bin/env python3
"""Validate the recovered 0x23560 status string/glyph selector."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "saved_origin_column_address", "saved_origin_row_address",
        "restored_origin_column_address", "restored_origin_row_address",
        "glyph_helper", "attributes", "has_lowercase_suffix",
        "selected_index", "selected_character", "font_mode")]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "string-glyph.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_status_string_glyph_23560.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_status_string_glyph_plan
    plan_fn.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(Plan)]

    plan = Plan()
    plain = (ctypes.c_uint8 * 3)(ord("A"), ord("B"), 0)
    plan_fn(plain, ctypes.byref(plan))
    assert (plan.glyph_helper, plan.attributes, plan.has_lowercase_suffix,
            plan.selected_index, plan.selected_character, plan.font_mode) == (
                0x1D310, 0x4000, 0, 1, ord("B"), 1)

    mixed = (ctypes.c_uint8 * 4)(ord("A"), ord("b"), ord("C"), 0)
    plan_fn(mixed, ctypes.byref(plan))
    assert (plan.has_lowercase_suffix, plan.selected_index,
            plan.selected_character, plan.font_mode) == (1, 0, ord("A"), 0)
    assert (plan.saved_origin_column_address, plan.saved_origin_row_address,
            plan.restored_origin_column_address,
            plan.restored_origin_row_address) == (
                0x504D40, 0x504D44, 0x504D40, 0x504D44)

print("PASS: 0x23560 status string/glyph selector")
