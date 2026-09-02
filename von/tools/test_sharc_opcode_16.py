#!/usr/bin/env python3
"""Audit the scalar state projection at SHARC opcode 0x16."""
from _sharc_listing import listing, require

lines = listing()
require(lines, {"32e": "IF FLAG0_IN, JUMP", "32f": "R0 = DM(I0, M0)",
                "334": "CALL (0x00020DBE) (DB)", "337": "CALL (0x00020DC4) (DB)",
                "347": "RTS (DB)", "349": "DM(0x00000005, I7) = R9"}, "SHARC opcode-0x16")
print("PASS: SHARC opcode-0x16 scalar state projection contract")
