#!/usr/bin/env python3
"""Test the exact ROM signature comparator at i960 0x2040."""

import ctypes
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_rom_signature_compare_2040.c"
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


class ProbePlan(ctypes.Structure):
    _fields_ = [("first_source", ctypes.c_uint32),
                ("second_source", ctypes.c_uint32),
                ("probe_bytes", ctypes.c_uint32),
                ("first_result", ctypes.c_uint32),
                ("second_result", ctypes.c_uint32),
                ("second_probe_performed", ctypes.c_uint32),
                ("accepted", ctypes.c_uint32),
                ("return_value", ctypes.c_uint32),
                ("continuation", ctypes.c_uint32)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-rom-signature-") as directory:
        library = Path(directory) / "signature.so"
        subprocess.run([os.environ.get("CC", "cc"), "-shared", "-fPIC", "-O2",
                        SOURCE, "-o", library], check=True)
        recovered = ctypes.CDLL(str(library))
        check = recovered.recovered_rom_signature_compare_2040
        check.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
        check.restype = ctypes.c_uint32
        plan_fn = recovered.recovered_rom_signature_probe_plan_2040
        plan_fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                            ctypes.POINTER(ProbePlan)]
        plan_fn.restype = ctypes.c_uint32
        for accepted in (b"SEGA", b"S32A"):
            candidate = (ctypes.c_uint8 * 4).from_buffer_copy(accepted)
            assert check(candidate) == 1
        for rejected in (b"SEGB", b"XXXX", b"S32B"):
            candidate = (ctypes.c_uint8 * 4).from_buffer_copy(rejected)
            assert check(candidate) == 0
        plan = ProbePlan()
        assert plan_fn(0, 1, ctypes.byref(plan)) == 1
        assert (plan.second_probe_performed, plan.accepted,
                plan.return_value, plan.continuation) == (0, 1, 1, 0x2070)
        assert plan_fn(1, 0, ctypes.byref(plan)) == 1
        assert (plan.second_probe_performed, plan.accepted,
                plan.continuation) == (1, 1, 0x2070)
        assert plan_fn(1, 1, ctypes.byref(plan)) == 1
        assert (plan.second_probe_performed, plan.accepted,
                plan.return_value, plan.continuation) == (1, 0, 0, 0x2078)
        assert (plan.first_source, plan.second_source, plan.probe_bytes) == (
            0x2030, 0x2038, 4)
        listing = LISTING.read_text(encoding="utf-8")
        for instruction in (r"2040:.*mov.*g0,r4",
                            r"2050:.*0xf5c58",
                            r"2068:.*0xf5c58",
                            r"2074:.*ret",
                            r"207c:.*ret"):
            assert re.search(instruction, listing)
    print("PASS: 0x2040 ROM signature comparator")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
