#!/usr/bin/env python3
"""Audit the four-input difference service at SHARC opcode 0x0f."""
from _sharc_listing import listing, require

lines = listing()
require(lines, {"27e": "IF FLAG0_IN, JUMP", "27f": "R1 = DM(I0, M0)",
                "280": "IF FLAG0_IN, JUMP", "281": "R0 = DM(I0, M0)",
                "282": "IF FLAG0_IN, JUMP", "283": "R3 = DM(I0, M0)",
                "284": "IF FLAG0_IN, JUMP", "285": "F1 = F1 - F3",
                "286": "F0 = F0 - F2", "287": "CALL (0x00020D68)",
                "288": "R1 = 0x4622F83D", "289": "F0 = F0 * F1",
                "28a": "R0 = FIX F0", "28c": "DM(I1, M0) = R0", "28d": "RTS"},
       "SHARC opcode-0x0f")
print("PASS: SHARC opcode-0x0f four-input difference service contract")
