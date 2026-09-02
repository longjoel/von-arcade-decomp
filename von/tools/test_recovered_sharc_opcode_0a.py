#!/usr/bin/env python3
"""Test the recovered SHARC opcode-0x0a atan2/fixed-angle contract."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    source = ROOT / "von/i960/recovered_sharc_opcode_0a.c"
    helper = ROOT / "von/i960/recovered_sharc_helper_20d68_candidate.c"
    with tempfile.TemporaryDirectory(prefix="von-opcode-0a-") as directory:
        library = Path(directory) / "opcode_0a.so"
        subprocess.run(
            ["cc", "-std=c99", "-O2", "-ffp-contract=off", "-fPIC", "-shared",
             str(source), str(helper), "-o", str(library)],
            check=True,
        )
        recovered = ctypes.CDLL(str(library)).recovered_sharc_opcode_0a_angle
        recovered.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        recovered.restype = ctypes.c_uint32
        recovered_registers = ctypes.CDLL(str(library)).recovered_sharc_opcode_0a_angle_registers
        recovered_registers.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        recovered_registers.restype = ctypes.c_uint32
        vectors = (
            (0x3F800000, 0x00000000, 0x00000000),
            (0x00000000, 0x3F800000, 0x00003FFF),
            (0x3F800000, 0x3F800000, 0x00001FFF),
            (0xBF800000, 0x3F800000, 0x00005FFF),
        )
        for first, second, expected in vectors:
            actual = recovered(first, second)
            if actual != expected:
                raise SystemExit(
                    f"opcode 0x0a mismatch first={first:#x} second={second:#x}: "
                    f"{actual:#010x} != {expected:#010x}"
                )
        if recovered_registers(0x3F800000, 0x00000000) != 0x00003FFF:
            raise SystemExit("opcode 0x0a register order lost: (R0=1, R1=0)")
    print("PASS: recovered SHARC opcode-0x0a atan2/fixed-angle contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
