#!/usr/bin/env python3
import ctypes
import pathlib
import subprocess
import tempfile


class Plan(ctypes.Structure):
    _fields_ = [
        ("glyph_index", ctypes.c_uint32),
        ("first_tile", ctypes.c_uint32),
        ("second_tile", ctypes.c_uint32),
        ("attribute", ctypes.c_uint32),
        ("next_column", ctypes.c_uint32),
    ]


root = pathlib.Path(__file__).resolve().parents[2]
source = root / "von/i960/recovered_text_alt_glyph.c"
with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "alt-glyph.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2", "-o", str(library), str(source)
    ], check=True)
    lib = ctypes.CDLL(str(library))
    lib.recovered_text_alt_glyph_plan.argtypes = [
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.POINTER(Plan),
    ]
    for character in range(256):
        plan = Plan()
        lib.recovered_text_alt_glyph_plan(character, 7, 12, 0, ctypes.byref(plan))
        expected = ((character & 0x7f) - 0x20) & 0xffffffff
        if expected > 95:
            expected = 0
        assert plan.glyph_index == expected
        assert plan.first_tile == 7 * 64 + 12
        assert plan.second_tile == plan.first_tile + 64
        assert plan.attribute == 0
        assert plan.next_column == 13

    for column in (30, 31, 63, 0xffffffff):
        plan = Plan()
        lib.recovered_text_alt_glyph_plan(0x41, 2, column, 1, ctypes.byref(plan))
        assert plan.attribute == 0xc000
        assert plan.next_column == (column + 1 if column <= 30 else column)

print("recovered alternate glyph sink vectors: ok")
