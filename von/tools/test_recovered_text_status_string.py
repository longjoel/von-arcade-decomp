#!/usr/bin/env python3
"""Test the 0x1d880 status-string mode classifier."""

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_status_string.c"


class Plan(ctypes.Structure):
    _fields_ = [("font_mode", ctypes.c_uint32), ("emits_characters", ctypes.c_uint32)]


class AttributedPlan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("font_mode", "attributes", "renderer_target", "emits_characters")]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-status-string-") as directory:
        library = Path(directory) / "status-string.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2", SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        plan_fn = recovered.recovered_text_status_string_plan
        plan_fn.argtypes = [ctypes.c_char_p, ctypes.POINTER(Plan)]
        for text, expected in ((b"", (1, 0)), (b"ABC", (1, 1)),
                               (b"AbC", (0, 1)), (b"A-z", (0, 1)),
                               (b"a", (1, 1)), (b"A`{", (1, 1))):
            plan = Plan()
            plan_fn(text, ctypes.byref(plan))
            actual = (plan.font_mode, plan.emits_characters)
            assert actual == expected, (text, actual, expected)

        attributed = recovered.recovered_text_status_attributed_plan
        attributed.argtypes = [ctypes.c_char_p, ctypes.POINTER(AttributedPlan)]
        for text, expected_mode, expected_emit in (
                (b"", 1, 0), (b"ABC", 1, 1), (b"AbC", 0, 1),
                (b"A-z", 0, 1), (b"a", 1, 1)):
            plan = AttributedPlan()
            attributed(text, ctypes.byref(plan))
            assert (plan.font_mode, plan.attributes, plan.renderer_target,
                    plan.emits_characters) == (expected_mode, 0x4000,
                                               0x1d310, expected_emit)

    print("PASS: 0x1d880/0x1d930 status-string classifier and renderer connection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
