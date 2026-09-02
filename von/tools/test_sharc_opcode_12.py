#!/usr/bin/env python3
"""Audit the three-input state-tail update at SHARC opcode 0x12."""
from _sharc_listing import listing, require

lines = listing()
require(lines, {"2c5": "IF FLAG0_IN, JUMP", "2c6": "R0 = DM(I0, M0)",
                "2c7": "IF FLAG0_IN, JUMP", "2c8": "R1 = DM(I0, M0)",
                "2c9": "IF FLAG0_IN, JUMP", "2ca": "R2 = DM(I0, M0)",
                "2cb": "I7 = DM(0x00030101)", "2cc": "R8 = DM(0x00000009, I7)",
                "2d9": "RTS (DB)", "2da": "DM(0x0A, I7) = R9", "2db": "DM(0x0000000B, I7) = R10"},
       "SHARC opcode-0x12")
print("PASS: SHARC opcode-0x12 state-tail update contract")
