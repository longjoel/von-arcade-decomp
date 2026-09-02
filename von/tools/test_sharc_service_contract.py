#!/usr/bin/env python3
"""Test the recovered SHARC opcode-0x40/0x41 integer service contract."""

from __future__ import annotations

from sharc_service_contract import opcode_18_state_window, opcode_40_base, opcode_41_lookup


def main() -> int:
    for operand in range(0, 256):
        expected = ((operand << 16) + 0x01C00000) & 0xFFFFFFFF
        if opcode_40_base(operand) != expected:
            raise SystemExit(f"opcode 0x40 mismatch for {operand:#x}")

    base = opcode_40_base(5)
    for operand in range(0, 4096):
        address = (base + (operand >> 2)) & 0xFFFFFFFF
        data = ((operand & 0xFF) * 0x01010101) & 0xFFFFFFFF
        got = opcode_41_lookup(operand, base, {address: data})
        expected = (data >> ((operand & 3) * 8)) & 0xFF
        if got != expected:
            raise SystemExit(f"opcode 0x41 mismatch for {operand:#x}")

    memory = {0x30104: 0x9000}
    selector = 7
    source = 0x9000 + (selector << 4)
    expected_state = tuple((0xA5000000 + index) & 0xFFFFFFFF for index in range(16))
    memory.update({source + index: value for index, value in enumerate(expected_state)})
    state, output = opcode_18_state_window(selector, memory)
    if state != expected_state or output != expected_state[:12]:
            raise SystemExit(f"opcode 0x18 mismatch: state={state!r} output={output!r}")

    print("PASS: SHARC opcode-0x18 state window, opcode-0x40 base, and opcode-0x41 byte lookup")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
