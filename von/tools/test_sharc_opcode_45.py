#!/usr/bin/env python3
"""Audit the three-input, three-result SHARC helper at opcode 0x45."""

from __future__ import annotations

import math
import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"
MODEL = ROOT / "von/i960/recovered_sharc_opcode_45.c"
REDUCTION_MODEL = ROOT / "von/i960/recovered_sharc_helper_20dbe.c"


def spherical_projection(a: float, b: float, scale: float) -> tuple[float, float, float]:
    return (
        scale * math.sin(a),
        scale * math.cos(a) * math.cos(b),
        -scale * math.cos(a) * math.sin(b),
    )


def main() -> int:
    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body

    for slot, register in zip(("bac", "bae", "bb0"), ("R0", "R13", "R15")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x45 slot {slot} missing {register} FIFO read")
    for slot in ("bab", "bad", "baf"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x45 slot {slot} missing FIFO wait")

    checks = {
        "bb4": "R1 = 0x38C9116D",
        "bb5": "CALL (0x00020DBE)",
        "bb8": "CALL (0x00020DC4)",
        "bbe": "R1 = 0x38C9116D",
        "bbf": "CALL (0x00020DBE)",
        "bc2": "CALL (0x00020DC4)",
        "bc5": "IF FLAG1_IN, JUMP",
        "bc6": "DM(I1, M0) = R3",
        "bc8": "IF FLAG1_IN, JUMP",
        "bc9": "DM(I1, M0) = R1",
        "bca": "IF FLAG1_IN, JUMP",
        "bcb": "RTS (DB)",
        "bcc": "F0 = -F0",
        "bcd": "DM(I1, M0) = R0",
        "bce": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x45 slot {slot} missing {fragment}")

    expected = spherical_projection(math.pi / 4.0, math.pi / 2.0, 2.0)
    observed = (1.4142475, -0.0000678, -1.4141798)
    if not all(math.isclose(actual, target, rel_tol=0.0, abs_tol=1e-4)
               for actual, target in zip(observed, expected)):
        raise SystemExit(f"SHARC opcode-0x45 spherical projection mismatch: {expected}")

    with tempfile.TemporaryDirectory(prefix="von-sharc-45-") as directory:
        library = Path(directory) / "libopcode_45.so"
        subprocess.run(["cc", "-std=c99", "-O2", "-fPIC", "-shared",
                        str(MODEL), str(REDUCTION_MODEL), "-o", str(library)], check=True)
        lib = ctypes.CDLL(str(library))
        project = lib.recovered_sharc_opcode_45_project_fixed
        project.argtypes = [ctypes.c_int16, ctypes.c_int16, ctypes.c_uint32,
                            ctypes.POINTER(ctypes.c_uint32)]
        project.restype = None
        words = ctypes.c_uint32 * 3
        vectors = (
            (0x0000, 0x0000, 0x3f800000, (0x00000000, 0x3f7ffffe, 0x80000000)),
            (0x4000, 0x0000, 0x40000000, (0x40000000, 0xb8c92eee, 0x00000000)),
            (0x0000, 0x4000, 0x40000000, (0x00000000, 0xb8c92eee, 0xbfffffff)),
            (0x2000, 0x2000, 0x40000000, (0x3fb50610, 0x3f7ffcdf, 0xbf800001)),
            (-0x2000, 0x2000, 0x3fc00000, (0xbf87c48c, 0x3f3ffda7, 0xbf400002)),
            (0x2000, -0x2000, 0x3fc00000, (0x3f87c48c, 0x3f3ffda7, 0x3f400002)),
        )
        for angle_a, angle_b, scale, expected_words in vectors:
            output = words()
            project(angle_a, angle_b, scale, output)
            if tuple(output) != expected_words:
                raise SystemExit(
                    f"opcode 0x45 fixed model mismatch for {angle_a:#x}/{angle_b:#x}: "
                    f"{tuple(output)!r} != {expected_words!r}"
                )

    print("PASS: SHARC opcode-0x45 three-input three-result helper contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
