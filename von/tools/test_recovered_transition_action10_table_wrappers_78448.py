#!/usr/bin/env python3
"""Validate paired action-10 table wrappers at 0x78448 and 0x78488."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_transition_action10_table_wrappers_78448.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("entry", ctypes.c_uint32), ("trampoline", ctypes.c_uint32),
        ("table", ctypes.c_uint32), ("selector_source", ctypes.c_uint32),
        ("action", ctypes.c_uint32),
        ("action_destination", ctypes.c_uint32),
        ("transition_destination", ctypes.c_uint32),
        ("return_register", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "action10-wrappers.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_transition_action10_table_wrappers_78448_plan
    function.argtypes = [ctypes.POINTER(Plan)]
    plans = (Plan * 2)()
    function(plans)
    assert [(item.entry, item.trampoline, item.table,
             item.selector_source, item.action, item.action_destination,
             item.transition_destination, item.return_register) for item in plans] == [
        (0x78448, 0x78478, 0x72990, 0x504d68, 10, 0x504db8,
         0x504d94, 0),
        (0x78488, 0x784b8, 0x729f0, 0x504d68, 10, 0x504db8,
         0x504d94, 0)]

    select = recovered.recovered_transition_action10_table_select
    select.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32]
    select.restype = ctypes.c_uint32
    table = (ctypes.c_uint32 * 3)(0x11, 0x22, 0x33)
    assert [select(table, index) for index in range(3)] == [0x11, 0x22, 0x33]

    listing = LISTING.read_text(encoding="utf-8")
    start = listing.index("   78448:")
    end = listing.index("   784bc:")
    block = listing[start:end]
    for evidence in (
            "mov\tg14,g0", "mov\t0,g14",
            "ld\t0x504d68,g4", "ld\t0x72990[g4*4],g4",
            "mov\t10,g5", "st\tg5,0x504db8",
            "st\tg4,0x504d94", "bx\t(g0)",
            "ld\t0x729f0[g4*4],g4"):
        if evidence not in block:
            raise AssertionError(f"action10 wrapper evidence missing: {evidence}")

print("PASS: 0x78448-0x784b8 action-10 table wrappers")
