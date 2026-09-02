#!/usr/bin/env python3
"""Validate opcode 0x4d's Euclidean horizontal seed against the listing."""
import ctypes
import math
import pathlib
import subprocess
import tempfile


listing = pathlib.Path(__file__).parents[1] / "build/disasm/vonj-sharc-bootstrap.lst"
lines = {}
for line in listing.read_text(encoding="utf-8").splitlines():
    if ":" in line:
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body
assert "F8 = F0 * F4" in lines["d00"]
assert "F2 = F10 - F14" in lines["d04"]
assert "R4 = R2" in lines["d05"]
assert "F12 = F2 * F4" in lines["d06"]
assert "F1 = F8 + F12" in lines["d07"]


with tempfile.TemporaryDirectory() as td:
    so = pathlib.Path(td) / "opcode4d_seed.so"
    subprocess.run([
        "cc", "-shared", "-fPIC", "-O2",
        str(pathlib.Path(__file__).parents[1] / "i960" /
            "recovered_sharc_opcode_4d_horizontal_seed.c"),
        "-o", str(so),
    ], check=True)
    lib = ctypes.CDLL(str(so))
    seed = lib.recovered_sharc_opcode_4d_horizontal_seed
    seed.argtypes = [ctypes.c_float, ctypes.c_float]
    seed.restype = ctypes.c_float

    assert math.isclose(seed(3.0, 0.0), 9.0)
    assert math.isclose(seed(3.0, 3.0), 18.0)
    assert math.isclose(seed(3.0, 4.0), 25.0)

print("PASS: SHARC opcode-0x4d Euclidean horizontal seed")
