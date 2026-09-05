#!/usr/bin/env python3
"""Validate the results-screen alias thunks from the listing."""
import pathlib
import re

LISTING = (pathlib.Path(__file__).parents[1] / "build" / "disasm" /
           "vonj-maincpu.lst").read_text(encoding="utf-8").splitlines()

INSTR = re.compile(r"^\s+([0-9a-f]+):\t([0-9a-f ]+)\t([a-z]+)\t?(.*)$")


def instr_at(address):
    for index, line in enumerate(LISTING):
        match = INSTR.match(line)
        if match and int(match.group(1), 16) == address:
            return index, match.group(3), match.group(4).strip()
    raise AssertionError(f"address {address:#x} not in listing")


def check_thunk(address, target):
    index, mnemonic, operands = instr_at(address)
    assert mnemonic == "call", f"{address:#x}: expected call, got {mnemonic}"
    assert f"{target:#x}" in operands, (
        f"{address:#x}: expected target {target:#x}, got {operands}")
    follow, mnemonic, _ = instr_at(address + 4)
    assert mnemonic == "ret", (
        f"{address:#x}+4: expected ret, got {mnemonic}")
    assert follow == index + 1, f"{address:#x}: ret must be adjacent"


check_thunk(0xE39F0, 0x1D1B0)
check_thunk(0xE3A00, 0x1D880)

print("PASS: results-screen alias thunks")
