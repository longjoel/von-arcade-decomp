#!/usr/bin/env python3
"""Integer contracts for the SHARC opcode-0x40/0x41 byte lookup pair."""

from __future__ import annotations


U32_MASK = 0xFFFFFFFF
OPCODE_40_BIAS = 0x01C00000
OPCODE_1E_TABLE_BASE_POINTER = 0x00030104


def opcode_40_base(operand: int) -> int:
    """Reproduce 0x20af2's ``(operand << 16) + 0x1c00000`` store."""

    return ((operand << 16) + OPCODE_40_BIAS) & U32_MASK


def opcode_41_lookup(operand: int, base: int, data_memory: dict[int, int]) -> int:
    """Return the byte selected by the 0x20af9 handler.

    The SHARC handler forms ``address = base + (operand >> 2)`` and performs a
    logical right shift by ``8 * (operand & 3)`` before masking to one byte.
    ``data_memory`` contains 32-bit DM words keyed by byte-addressed service
    addresses as represented in the extracted listing.
    """

    operand &= U32_MASK
    address = (base + (operand >> 2)) & U32_MASK
    word = data_memory[address] & U32_MASK
    return (word >> ((operand & 3) * 8)) & 0xFF


def opcode_18_state_window(selector: int, data_memory: dict[int, int]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Model opcode 0x18's 16-word state copy and 12-word output stream."""

    selector &= U32_MASK
    table_base = data_memory[OPCODE_1E_TABLE_BASE_POINTER] & U32_MASK
    source = (table_base + (selector << 4)) & U32_MASK
    state = tuple(data_memory[(source + index) & U32_MASK] & U32_MASK for index in range(16))
    return state, state[:12]
