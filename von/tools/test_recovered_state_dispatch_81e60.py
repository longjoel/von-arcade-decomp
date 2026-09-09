#!/usr/bin/env python3
"""Check the state dispatcher at i960 0x81e60."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_dispatch_81e60.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [("startup_call_84d90", ctypes.c_uint32),
                ("dispatched", ctypes.c_uint32),
                ("target", ctypes.c_uint32),
                ("handler_object", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-dispatch-81e60.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_dispatch_81e60
    function.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_int16,
                         ctypes.c_uint32, ctypes.c_uint32]
    function.restype = Plan

    result = function(4, 10, 0, 0, 0x12345678)
    assert (result.startup_call_84d90, result.dispatched,
            result.target, result.handler_object) == (1, 1, 0x81edc,
                                                       0x12345678)
    assert function(0, 0, 0, 9, 0x2000).target == 0x81f48
    assert function(4, 10, 1, 0, 0x2000).dispatched == 0
    assert function(4, 10, 0, 10, 0x2000).dispatched == 0


listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, text in (
    ("81e68", "cmpi 4,g4"),
    ("81e7c", "cmpibne 10,g4,0x81e90"),
    ("81e80", "ldos 0x504e42,g4"),
    ("81e88", "cmpibne 0,g4,0x81e90"),
    ("81e8c", "call 0x84d90"),
    ("81e90", "ldos 0x504e42,g4"),
    ("81e9c", "ld 0x64(r4),g4"),
    ("81ea0", "cmpobl 9,g4,0x81f54"),
    ("81ea8", "ld 0x81eb4[g4*4],g4"),
    ("81eb0", "bx (g4)"),
):
    normalized_text = " ".join(text.split())
    assert any(address + ":" in line and normalized_text in line for line in listing), \
        f"81e60 listing dataflow missing: {address} {text}"

print("recovered 0x81e60 state-dispatch vectors: ok")
