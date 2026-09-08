#!/usr/bin/env python3
"""Validate the TAB/LF handler at i960 0x1cbb8."""
import ctypes
import pathlib
import subprocess
import tempfile


class State(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("column", "row", "state_changed")]


root = pathlib.Path(__file__).parents[2]
with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "control.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2",
                    str(root / "von/i960/recovered_text_control_handler_1cbb8.c"),
                    "-o", str(so)], check=True)
    fn = ctypes.CDLL(str(so)).recovered_text_control_handler_1cbb8
    fn.argtypes = [ctypes.c_uint32] * 4 + [ctypes.POINTER(State)]
    vectors = (
        (9, 12, 10, 20, (16, 20, 1)),
        (9, 12, 60, 20, (0, 21, 1)),
        (9, 12, 60, 46, (0, 47, 1)),
        (10, 12, 30, 20, (12, 21, 1)),
        (10, 12, 30, 46, (12, 47, 1)),
        (7, 12, 30, 20, (30, 20, 0)),
    )
    for character, origin, column, row, expected in vectors:
        out = State()
        fn(character, origin, column, row, ctypes.byref(out))
        actual = (out.column, out.row, out.state_changed)
        if actual != expected:
            raise SystemExit("1cbb8 control-handler mismatch")

print("PASS: 0x1cbb8 text control handler")
