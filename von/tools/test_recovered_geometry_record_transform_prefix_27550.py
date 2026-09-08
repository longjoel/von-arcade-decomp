#!/usr/bin/env python3
"""Validate the profile route prefix at i960 0x27550."""
import ctypes
import pathlib
import subprocess
import tempfile


class Prefix(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "record_zero_fields", "record_one_field", "reset_transform_fields",
        "profile_route", "selected_profile_pointer", "profile_helper_called",
        "stage_selector_called", "producer_called")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "prefix.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_geometry_record_transform_prefix_27550.c"),
                    "-o", str(so)], check=True)
    fn = ctypes.CDLL(str(so)).recovered_geometry_record_transform_prefix_27550
    fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.POINTER(Prefix)]
    for mode, kind, route, pointer, helper in (
        (0, 9, 1, 0x274A0, 1), (0, 8, 2, 0x26D60, 0),
        (1, 9, 1, 0x274A0, 1), (1, 8, 3, 0x273F0, 0),
        (3, 0, 5, 0x27130, 0), (4, 0, 4, 0x273D0, 0),
        (2, 0, 0, 0, 0)):
        out = Prefix()
        fn(mode, kind, ctypes.byref(out))
        actual = (out.record_zero_fields, out.record_one_field,
                  out.reset_transform_fields, out.profile_route,
                  out.selected_profile_pointer, out.profile_helper_called,
                  out.stage_selector_called, out.producer_called)
        if actual != (1, 1, 1, route, pointer, helper, 1, 1):
            raise SystemExit("0x27550 profile route mismatch")

print("PASS: 0x27550 geometry transform prefix")
