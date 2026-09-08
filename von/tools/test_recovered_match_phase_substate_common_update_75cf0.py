#!/usr/bin/env python3
"""Validate the shared phase-substate publication at 0x75cf0."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_match_phase_substate_common_update_75cf0.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("selected_value_register", ctypes.c_uint32),
        ("selected_value_destination", ctypes.c_uint32),
        ("counter_value", ctypes.c_uint32),
        ("counter_destination", ctypes.c_uint32),
        ("return_address", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "substate-common.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_match_phase_substate_common_update_75cf0_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plan = Plan()
    function(ctypes.byref(plan))
    assert (plan.selected_value_register, plan.selected_value_destination,
            plan.counter_value, plan.counter_destination,
            plan.return_address) == (2, 0x504d94, 10, 0x504db8, 0x75d04)
    counter = recovered.recovered_match_phase_substate_common_counter
    counter.restype = ctypes.c_uint32
    assert counter() == 10

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   75cf0:")
    end = listing.index("   75d08:")
    block = listing[start:end]
    for evidence in ("st\tg2,0x504d94", "mov\t10,g2",
                     "st\tg2,0x504db8", "ret"):
        if evidence not in block:
            raise AssertionError(f"substate-common evidence missing: {evidence}")

print("PASS: 0x75cf0-0x75d04 phase-substate common update")
