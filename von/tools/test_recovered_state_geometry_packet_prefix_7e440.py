#!/usr/bin/env python3
"""Check the command-29/30 geometry prefix at i960 0x7e440."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_geometry_packet_prefix_7e440.c"


class Plan(ctypes.Structure):
    _fields_ = [("command", ctypes.c_uint32 * 8),
                ("lane", ctypes.c_uint32 * 8),
                ("payload", ctypes.c_uint32 * 8)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-geometry-packet-prefix.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_geometry_packet_prefix_7e440
    function.argtypes = [ctypes.c_int16] + [ctypes.c_uint32] * 3 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(-1, 0x11112222, 0x33334444, 0x20, ctypes.byref(plan))
    assert list(plan.command) == [29, 30, 29, 30, 29, 30, 29, 30]
    assert list(plan.lane) == [0x5fff, 0x5fff, 0x9fff, 0x5ffe,
                               0xffdf, 0xffdf, 0x001f, 0x001f]
    assert list(plan.payload) == [0x11112222] * 4 + [0x33334444] * 4

    plan = Plan()
    function(0x7fff, 0, 0, 0xffffffff, ctypes.byref(plan))
    assert (plan.lane[4], plan.lane[6]) == (0x8000, 0x7ffe)

print("recovered 0x7e440 geometry packet-prefix vectors: ok")
