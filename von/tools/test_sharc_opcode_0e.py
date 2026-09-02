#!/usr/bin/env python3
"""Audit the four-word SHARC state upload service at opcode 0x0e."""
from _sharc_listing import listing, require

lines = listing()
require(lines, {
    "271": "IF FLAG0_IN, JUMP", "272": "R0 = DM(I0, M0)",
    "273": "IF FLAG0_IN, JUMP", "274": "R1 = DM(I0, M0)",
    "275": "IF FLAG0_IN, JUMP", "276": "R2 = DM(I0, M0)",
    "277": "IF FLAG0_IN, JUMP", "278": "R3 = DM(I0, M0)",
    "279": "DM(0x00030105) = R0", "27a": "DM(0x00030106) = R1",
    "27b": "RTS (DB)", "27c": "DM(0x00030107) = R2",
    "27d": "DM(0x00030108) = R3",
}, "SHARC opcode-0x0e")
print("PASS: SHARC opcode-0x0e four-word state upload contract")
