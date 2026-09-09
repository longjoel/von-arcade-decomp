#!/usr/bin/env python3
"""Check the alternate mode-2/mode-3 glyph-string selector."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_text_alt_string.c"


class GlyphStringPlan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("font_mode", "attributes", "renderer_target", "emits_characters")]


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "libtext_alt_string.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
        api = ctypes.CDLL(str(library))
        function = api.recovered_text_alt_string_font_mode
        function.argtypes = [ctypes.c_char_p]
        function.restype = ctypes.c_uint32
        cases = {
            b"": 3,
            b"ABC": 3,
            b"A1_Z": 3,
            b"AbC": 2,
            b"A-z": 2,
            b"a": 3,
        }
        for text, expected in cases.items():
            actual = function(text)
            assert actual == expected, (text, actual, expected)

        connected = api.recovered_text_alt_glyph_string_plan
        connected.argtypes = [ctypes.c_char_p, ctypes.POINTER(GlyphStringPlan)]
        for text, expected_mode, expected_emit in (
                (b"", 3, 0), (b"ABC", 3, 1), (b"AbC", 2, 1),
                (b"A-z", 2, 1)):
            plan = GlyphStringPlan()
            connected(text, ctypes.byref(plan))
            assert (plan.font_mode, plan.attributes, plan.renderer_target,
                    plan.emits_characters) == (expected_mode, 0x4000,
                                               0x1d310, expected_emit)

    print("PASS: 0x1d7d0 alternate mode and renderer connection vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
