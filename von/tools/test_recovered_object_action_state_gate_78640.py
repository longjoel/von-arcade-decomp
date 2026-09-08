#!/usr/bin/env python3
"""Validate the object-action state gate at i960 0x78640."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_object_action_state_gate_78640.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("object_state_offset", ctypes.c_uint32),
        ("state8", ctypes.c_uint32),
        ("state8_target", ctypes.c_uint32),
        ("non_state8_continuation", ctypes.c_uint32),
        ("return_address", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "state-gate.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_object_action_state_gate_78640_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.object_state_offset, plan.state8, plan.state8_target,
            plan.non_state8_continuation, plan.return_address) == \
        (0x64, 8, 0x78790, 0x78658, 0x78654)
    target = recovered.recovered_object_action_state_gate_target
    target.argtypes = [ctypes.c_uint32]
    target.restype = ctypes.c_uint32
    assert [target(value) for value in (0, 7, 8, 9, 0xffffffff)] == [
        0x78658, 0x78658, 0x78790, 0x78658, 0x78658]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   78640:")
    end = listing.index("   78658:")
    block = listing[start:end]
    for evidence in ("ld\t0x64(g0),g4", "cmpi\t8,g4",
                     "mov\tg0,r4", "bne\t0x78658",
                     "call\t0x78790", "ret"):
        if evidence not in block:
            raise AssertionError(f"object-action gate evidence missing: {evidence}")
    if "   78658:" not in listing:
        raise AssertionError("object-action non-state8 continuation missing")

print("PASS: 0x78640 object-action state gate")
