#!/usr/bin/env python3
"""Check the status tail at i960 0x8168c."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_status_tail_8168c.c"


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-status-tail.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_status_tail_8168c
    function.argtypes = [ctypes.c_int32, ctypes.c_int32]
    function.restype = ctypes.c_uint32

    for value in (0, 119, 120, 239, 240, 359, -1, -120, -121):
        remainder = value % 240 if value >= 0 else -((-value) % 240)
        expected = 18 if remainder <= 119 else 19
        assert function(0, value) == expected
        assert function(2, value) == 18
        assert function(7, value) == 18


listing = [" ".join(line.split()) for line in (ROOT / "von/build/disasm/vonj-maincpu.lst").read_text(encoding="utf-8").splitlines()]
for address, text in (
    ("8168c", "cmpibe 2,g4,0x816ac"),
    ("81690", "cmpibe 7,g4,0x816bc"),
    ("816a0", "remo g13,g4,g4"),
    ("816a8", "cmpobg g4,g13,0x816bc"),
    ("816b0", "st g13,0x504d94"),
    ("816c0", "st g13,0x504d94"),
):
    normalized_text = " ".join(text.split())
    assert any(address + ":" in line and normalized_text in line for line in listing), \
        f"8168c listing dataflow missing: {address} {text}"

print("recovered 0x8168c status-tail vectors: ok")
