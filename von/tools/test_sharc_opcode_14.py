#!/usr/bin/env python3
"""Audit the scalar state projection at SHARC opcode 0x14."""
from _sharc_listing import listing, require

lines = listing()
require(lines, {"2f6": "IF FLAG0_IN, JUMP", "2f7": "R0 = DM(I0, M0)",
                "2fa": "F0 = FLOAT R0", "2fc": "CALL (0x00020DBE) (DB)",
                "2ff": "CALL (0x00020DC4) (DB)", "31e": "I7 = DM(0x00030101)",
                "32b": "RTS (DB)"}, "SHARC opcode-0x14")
print("PASS: SHARC opcode-0x14 scalar state projection contract")
