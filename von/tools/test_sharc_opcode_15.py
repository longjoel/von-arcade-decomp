#!/usr/bin/env python3
"""Audit the scalar state projection at SHARC opcode 0x15."""
from _sharc_listing import listing, require

lines = listing()
require(lines, {"312": "IF FLAG0_IN, JUMP", "313": "R0 = DM(I0, M0)",
                "318": "CALL (0x00020DBE) (DB)", "31b": "CALL (0x00020DC4) (DB)",
                "31e": "I7 = DM(0x00030101)", "32b": "RTS (DB)"}, "SHARC opcode-0x15")
print("PASS: SHARC opcode-0x15 scalar state projection contract")
