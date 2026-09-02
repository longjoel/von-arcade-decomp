#!/usr/bin/env python3
"""Audit the streamed table/geometry service at SHARC opcode 0x17."""
from _sharc_listing import listing, require

lines = listing()
require(lines, {"34a": "R15 = 0x00000000", "34b": "I7 = 0x00030400",
                "34d": "R0 = DM(I0, M0)", "34e": "M7 = R0",
                "34f": "I6 = DM(0x00030103)", "35f": "I4 = 0x0003010B",
                "355": "R0 = DM(I6, M1)", "357": "IF EQ, JUMP (0x0002037F)",
                "358": "LCNTR = R0, DO (0x0000037E)",
                "359": "R0 = DM(I6, M1)", "35a": "R14 = R0",
                "35b": "R0 = LSHIFT R0 BY 4", "35e": "MODIFY(I5, M7)",
                "360": "LCNTR = 0x000C", "376": "DM(0x0003011B) = R15",
                "377": "DM(0x0003011C) = R14", "378": "CALL (0x00020DE1)",
                "361": "R0 = DM(I5, M1)", "362": "DM(I4, M1) = R0",
                "363": "MODIFY (I4, 0xFFFFFFF4)",
                "364": "R0 = DM(0x00000000, I4)",
                "365": "DM(0x0000000C, I4) = R0",
                "366": "R0 = DM(0x00000001, I4)",
                "367": "DM(0x0000000D, I4) = R0",
                "368": "R0 = DM(0x00000002, I4)",
                "369": "DM(0x0000000E, I4) = R0",
                "36b": "R12 = DM(0x00000003, I4)",
                "36c": "F0 = F8 - F12", "36d": "F1 = F9 - F13",
                "36e": "F4 = F10 - F12", "36f": "F1 = F1 * F4",
                "370": "F0 = F0 * F4", "371": "F0 = F0 - F1",
                "372": "IF EQ, JUMP (0x0002037E)",
                "379": "R14 = DM(0x0003011C)", "37a": "R15 = DM(0x0003011B)",
                "37b": "R15 = R15 + 1",
                "37c": "DM(I7, M1) = R0", "37d": "DM(I7, M1) = R14",
                "37f": "IF FLAG1_IN, JUMP", "380": "DM(I1, M0) = R15",
                "382": "IF EQ, RTS", "383": "I7 = 0x00030400",
                "384": "LCNTR = R15, DO (0x0000038C)",
                "385": "R0 = DM(I7, M1)", "387": "DM(I1, M0) = R0",
                "388": "R0 = DM(I7, M1)", "38c": "DM(I1, M0) = R0"},
       "SHARC opcode-0x17")
print("PASS: SHARC opcode-0x17 streamed table/geometry contract")
