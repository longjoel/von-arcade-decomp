#!/usr/bin/env python3
"""Validate the deterministic transition-helper bypass at 0x7834c."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_helper_bypass_7834c.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("selector_source", ctypes.c_uint32),
        ("state_destination", ctypes.c_uint32),
        ("state_value", ctypes.c_uint32),
        ("selector_threshold", ctypes.c_uint32),
        ("low_status", ctypes.c_uint32),
        ("high_status", ctypes.c_uint32),
        ("status_destination", ctypes.c_uint32),
        ("counter_value", ctypes.c_uint32),
        ("counter_destination", ctypes.c_uint32),
        ("return_address", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "helper-bypass.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_transition_helper_bypass_7834c_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.selector_source, plan.state_destination, plan.state_value,
            plan.selector_threshold, plan.low_status, plan.high_status,
            plan.status_destination, plan.counter_value,
            plan.counter_destination, plan.return_address) == \
        (0x504d68, 0x504d7c, 3, 4, 12, 13, 0x504d94, 5, 0x504db8,
         0x78384)
    status = recovered.recovered_transition_helper_bypass_status
    status.argtypes = [ctypes.c_uint32]
    status.restype = ctypes.c_uint32
    assert [status(value) for value in (0, 4, 5, 0xffffffff)] == [12, 12,
                                                                      13, 13]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   7834c:")
    end = listing.index("   78390:")
    block = listing[start:end]
    for evidence in (
            "ld\t0x504d68,g4", "mov\t3,g13", "cmpi\tg4,4",
            "st\tg13,0x504d7c", "mov\t13,g13", "bg\t0x78370",
            "mov\t12,g13", "st\tg13,0x504d94", "mov\t5,g13",
            "st\tg13,0x504db8", "ret"):
        if evidence not in block:
            raise AssertionError(f"helper-bypass evidence missing: {evidence}")

print("PASS: 0x7834c-0x78384 transition-helper bypass")
