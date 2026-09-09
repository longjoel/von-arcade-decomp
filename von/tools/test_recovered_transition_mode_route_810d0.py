#!/usr/bin/env python3
"""Check the complete mode route at i960 0x810d0/0x81120."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_mode_route_810d0.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [("accepted", ctypes.c_uint32),
                ("mode_gate_used", ctypes.c_uint32),
                ("status_504d94", ctypes.c_uint32),
                ("status_504db8", ctypes.c_uint32),
                ("status_504d9c", ctypes.c_uint32),
                ("value_504da0", ctypes.c_uint32),
                ("secondary_dispatch", ctypes.c_uint32),
                ("callback_target", ctypes.c_uint32),
                ("return_value", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-mode-route.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_mode_route_810d0
    function.argtypes = [ctypes.c_int32, ctypes.c_uint16, ctypes.c_float,
                         ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan

    result = function(0x1f4, 0x16, 1.0, 0, 1, 2)
    assert (result.accepted, result.mode_gate_used,
            result.status_504d94, result.status_504db8,
            result.status_504d9c, result.value_504da0,
            result.secondary_dispatch) == (1, 0, 7, 30, 2, 100, 1)
    assert (result.callback_target, result.return_value) == (0x79D60, 0)
    result = function(0x1f4, 0x16, -1.0, 8, 5, 2)
    assert (result.accepted, result.mode_gate_used) == (1, 1)
    assert function(0x1f3, 0x16, 1.0, 0, 1, 2).accepted == 0
    assert function(0x1f4, 0x14, 1.0, 0, 1, 2).accepted == 0
    assert function(0x1f4, 0x15, 1.0, 0, 1, 2).accepted == 0
    assert function(0x1f4, 0x16, -1.0, 0, 1, 2).accepted == 0
    assert function(0x1f4, 0x16, 1.0, 0, 5, 6).accepted == 0


listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, text in (
    ("810dc", "cmpibg g4,g1,0x810e4"),
    ("810e8", "ldos 0x172(g5),g4"),
    ("810f4", "shlo 16,g4,g4"),
    ("810f8", "cmpible g4,g1,0x81114"),
    ("8110c", "cmpibg g4,g1,0x81114"),
    ("81110", "call 0x81120"),
    ("81144", "ldob 0x504e50,g4"),
    ("8114c", "bbc 3,g4,0x811b8"),
    ("81184", "st g3,0x504d94"),
    ("8118c", "call 0x79d60"),
    ("81194", "st g2,0x504db8"),
    ("811a4", "st g3,0x504d9c"),
    ("811ac", "st g2,0x504da0"),
):
    normalized_text = " ".join(text.split())
    assert any(address + ":" in line and normalized_text in line for line in listing), \
        f"810d0 listing dataflow missing: {address} {text}"

print("recovered 0x810d0/0x81120 mode-route vectors: ok")
