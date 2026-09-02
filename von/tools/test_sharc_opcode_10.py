#!/usr/bin/env python3
"""Audit the 12-word identity-state initializer at SHARC opcode 0x10."""
from _sharc_listing import listing, require

lines = listing()
require(lines, {"28e": "I7 = DM(0x00030101)", "28f": "R0 = 0x00000000",
                "290": "R1 = 0x3F800000", "291": "DM(0x00000000, I7) = R1",
                "299": "DM(0x00000008, I7) = R1", "29b": "RTS (DB)",
                "29c": "DM(0x0000000A, I7) = R0", "29d": "DM(0x0000000B, I7) = R0"},
       "SHARC opcode-0x10")
print("PASS: SHARC opcode-0x10 12-word identity-state initializer contract")
