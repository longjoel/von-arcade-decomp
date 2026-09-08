#!/usr/bin/env python3
"""Check response/difference preparation at i960 0x7e5e8."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_state_geometry_difference_prep_7e5e8.c"


class Plan(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in
                ("frame_plus_60", "g1", "g2", "g3", "g5", "g6", "g7",
                 "g8", "r4", "r5", "r7", "r8", "r9", "r10", "r11", "r12",
                 "r13", "r15", "g13", "command10_payload")]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "libstate-geometry-difference-prep.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE),
                    "-o", str(library)], check=True)
    api = ctypes.CDLL(str(library))
    function = api.recovered_state_geometry_difference_prep_7e5e8
    function.argtypes = [ctypes.c_uint32] * 10 + [ctypes.POINTER(Plan)]
    function.restype = None

    plan = Plan()
    function(0x10, 0x20, 0x30, 0x40, 0x50, 0x60,
             0x100, 0x200, 0x300, 0x400, ctypes.byref(plan))
    assert plan.frame_plus_60 == 0
    assert (plan.r10, plan.r8) == (0x200, 0xfffffe00)
    assert plan.command10_payload == 0x440
    assert (plan.r11, plan.r15, plan.r9) == (0xfffffc20, 0xffffffe0, 0x60)
    assert (plan.g1, plan.g2, plan.g3, plan.g5) == (0x390, 0x1b0,
                                                     0x200, 0x2e0)
    assert (plan.g6, plan.g7, plan.r4, plan.g13) == (0xfffffdc0,
                                                       0xfffffe40, 0x2c0,
                                                       0xfffffff0)

print("recovered 0x7e5e8 geometry-difference vectors: ok")
