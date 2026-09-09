#!/usr/bin/env python3
"""Check the branch-specific transition route at i960 0x80710."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_route_80710.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [("route", ctypes.c_int),
                ("band_index", ctypes.c_uint32),
                ("adjusted_current", ctypes.c_int32),
                ("raw_difference", ctypes.c_int32),
                ("result_table", ctypes.c_uint32),
                ("result_value", ctypes.c_uint32),
                ("result_destination", ctypes.c_uint32),
                ("action_504db8", ctypes.c_uint32),
                ("action_value", ctypes.c_uint32),
                ("action_destination", ctypes.c_uint32),
                ("state_destination", ctypes.c_uint32),
                ("state_call_target", ctypes.c_uint32),
                ("threshold_call_82800", ctypes.c_uint32)]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libtransition-route-80710.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_transition_route_80710
    function.argtypes = [ctypes.c_int32, ctypes.c_int16, ctypes.c_int16,
                         ctypes.c_float, ctypes.c_float, ctypes.c_uint32]
    function.restype = Plan

    result = function(1, 100, 100, 5.0, 4.0, 0x12345678)
    assert (result.route, result.adjusted_current,
            result.raw_difference, result.band_index,
            result.action_504db8, result.threshold_call_82800) == (
                1, 100 - 0x6800, 0x6800, 4, 10, 1)
    assert (result.result_table, result.result_value, result.result_destination,
            result.action_value, result.action_destination,
            result.state_destination, result.state_call_target) == (
                0x72630, 0x12345678, 0x504d94, 10, 0x504db8,
                0x504d80, 0x82800)
    result = function(9, 100, 100, 4.0, 4.0, 0xABCDEF01)
    assert (result.adjusted_current, result.raw_difference,
            result.band_index, result.threshold_call_82800) == (
                100 + 0x6800, -0x6800, 5, 0)
    assert function(10, 100, 100, 1.0, 0.0, 0).route == 0


listing = [" ".join(line.split()) for line in LISTING.read_text(encoding="utf-8").splitlines()]
for address, text in (
    ("8072c", "ldos 0x184(g5),g4"),
    ("80730", "ldos 0x184(g0),g0"),
    ("80744", "lda 0xffff9800(g0),g0"),
    ("80750", "subo 8,g4,g4"),
    ("80770", "lda 0x6800(g0),g0"),
    ("80778", "subo g0,g4,g0"),
    ("8077c", "bal 0x73508"),
    ("8079c", "ld 0x72630[g6*4],g4"),
    ("807a4", "st g4,0x504d94"),
    ("807b4", "call 0x82800"),
    ("807c4", "st g1,0x504db8"),
):
    normalized_text = " ".join(text.split())
    assert any(address + ":" in line and normalized_text in line for line in listing), \
        f"80710 listing dataflow missing: {address} {text}"

print("recovered 0x80710 transition-route vectors: ok")
