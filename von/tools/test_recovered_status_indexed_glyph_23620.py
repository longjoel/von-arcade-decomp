#!/usr/bin/env python3
"""Validate the recovered 0x23620 indexed-glyph wrapper."""
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "source", "source_index", "selected_character", "helper",
        "saved_origin_column_address", "saved_origin_row_address",
        "restored_origin_column_address", "restored_origin_row_address")]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "indexed-glyph.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(pathlib.Path(__file__).parents[1] / "i960" /
                        "recovered_status_indexed_glyph_23620.c"),
                    "-o", str(so)], check=True)
    lib = ctypes.CDLL(str(so))
    plan_fn = lib.recovered_status_indexed_glyph_plan
    plan_fn.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32,
                        ctypes.POINTER(Plan)]

    text = (ctypes.c_uint8 * 5)(ord("A"), ord("B"), ord("C"), ord("D"), 0)
    plan = Plan()
    plan_fn(text, 2, ctypes.byref(plan))
    assert (plan.source, plan.source_index, plan.selected_character,
            plan.helper) == (0, 2, ord("C"), 0x1CD18)
    assert (plan.saved_origin_column_address, plan.saved_origin_row_address,
            plan.restored_origin_column_address,
            plan.restored_origin_row_address) == (
                0x504D44, 0x504D40, 0x504D44, 0x504D40)

print("PASS: 0x23620 indexed status glyph wrapper")
