#!/usr/bin/env python3
"""Validate the paired ABI epilogues at 0x2e1c8 and 0x2e1e8."""

import ctypes
import pathlib
import subprocess
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_geometry_status_trampolines_2e1c8.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class Plan(ctypes.Structure):
    _fields_ = [
        ("entry", ctypes.c_uint32),
        ("link_load_address", ctypes.c_uint32),
        ("return_stub", ctypes.c_uint32),
        ("moves_link_to_g0", ctypes.c_uint32),
        ("clears_g14", ctypes.c_uint32),
        ("indirect_branch", ctypes.c_uint32),
    ]


with tempfile.TemporaryDirectory() as directory:
    library = pathlib.Path(directory) / "status-trampolines.so"
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", SOURCE, "-o", library],
                   check=True)
    recovered = ctypes.CDLL(str(library))
    function = recovered.recovered_geometry_status_trampoline_plan
    function.argtypes = [ctypes.c_uint32, ctypes.POINTER(Plan)]

    plan = Plan()
    for alternate, expected in (
            (0, (0x2e1c8, 0x2e1c0, 0x2e1d4)),
            (1, (0x2e1e8, 0x2e1e0, 0x2e1f4))):
        function(alternate, ctypes.byref(plan))
        assert (plan.entry, plan.link_load_address, plan.return_stub) == expected
        assert (plan.moves_link_to_g0, plan.clears_g14, plan.indirect_branch) == (1, 1, 1)

    listing = LISTING.read_text(encoding="utf-8")
    for entry, stub in (("2e1c8:", "2e1d4:"), ("2e1e8:", "2e1f4:")):
        block = listing[listing.index("   " + entry):listing.index("   " + stub) + 10]
        for evidence in ("mov\tg14,g0", "mov\t0,g14", "bx\t(g0)"):
            if evidence not in block:
                raise AssertionError(f"trampoline listing evidence missing: {entry} {evidence}")

print("PASS: 0x2e1c8/0x2e1e8 status trampolines")
