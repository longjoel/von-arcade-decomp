#!/usr/bin/env python3
"""Audit the 12-word state readback service at SHARC opcode 0x11."""
from _sharc_listing import listing, require

lines = listing()
require(lines, {"29e": "I7 = DM(0x00030101)", "29f": "R0 = DM(I7, M1)",
                "2a0": "IF FLAG1_IN, JUMP", "2a1": "DM(I1, M0) = R0",
                "2c0": "R0 = DM(I7, M1)", "2c1": "IF FLAG1_IN, JUMP",
                "2c2": "RTS (DB)", "2c3": "DM(I1, M0) = R0"}, "SHARC opcode-0x11")
print("PASS: SHARC opcode-0x11 12-word state readback contract")
