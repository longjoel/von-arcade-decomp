#!/usr/bin/env python3
"""Audit the three-input 3x3 state writeback at SHARC opcode 0x13."""
from _sharc_listing import listing, require

lines = listing()
require(lines, {"2dc": "IF FLAG0_IN, JUMP", "2dd": "R0 = DM(I0, M0)",
                "2de": "IF FLAG0_IN, JUMP", "2df": "R1 = DM(I0, M0)",
                "2e0": "IF FLAG0_IN, JUMP", "2e1": "R2 = DM(I0, M0)",
                "2e2": "I7 = DM(0x00030101)", "2f3": "RTS (DB)",
                "2f4": "DM(0x00000007, I7) = R6", "2f5": "DM(0x00000008, I7) = R7"},
       "SHARC opcode-0x13")
print("PASS: SHARC opcode-0x13 3x3 state writeback contract")
