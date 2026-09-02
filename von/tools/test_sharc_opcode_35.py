#!/usr/bin/env python3
"""Audit the statically recovered SHARC opcode-0x35 handler shape."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def instruction(lines: dict[str, str], slot: str) -> str:
    try:
        return lines[slot]
    except KeyError as exc:
        raise SystemExit(f"missing SHARC listing slot {slot}") from exc


def main() -> int:
    lines: dict[str, str] = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body

    expected_reads = {
        "8f3": "R4 = DM(I0, M0)",
        "8f5": "R0 = DM(I0, M0)",
        "8f7": "R6 = DM(I0, M0)",
        "8f9": "R2 = DM(I0, M0)",
        "8fb": "R13 = DM(I0, M0)",
        "8fd": "R12 = DM(I0, M0)",
    }
    for slot, text in expected_reads.items():
        if text not in instruction(lines, slot):
            raise SystemExit(f"opcode 0x35 slot {slot} missing {text}")

    for slot in ("8f2", "8f4", "8f6", "8f8", "8fa", "8fc"):
        if "IF FLAG0_IN, JUMP" not in instruction(lines, slot):
            raise SystemExit(f"opcode 0x35 slot {slot} missing FIFO wait")

    preceding_boundary = {
        "8ef": "RTS (DB)",
        "8f0": "DM(0x0A, I7) = R9",
        "8f1": "DM(0x0000000B, I7) = R10",
        "8f2": "IF FLAG0_IN, JUMP (0x000008F2)",
    }
    for slot, fragment in preceding_boundary.items():
        if fragment not in instruction(lines, slot):
            raise SystemExit(f"opcode 0x34/0x35 boundary slot {slot} missing {fragment}")

    if "F0 = RECIPS F12" not in instruction(lines, "8ff"):
        raise SystemExit("opcode 0x35 does not seed reciprocal correction at 8ff")
    pipeline_checks = {
        "8f7": "F8 = F0 * F4",
        "8fb": "F12 = F2 * F6",
        "8fd": "F8 = F8 + F12",
        "8fe": "F0 = F8 + F13",
        "8ff": "R7 = R0",
    }
    for slot, fragment in pipeline_checks.items():
        if fragment not in instruction(lines, slot):
            raise SystemExit(f"opcode 0x35 slot {slot} missing {fragment}")
    # The visible result path is (F0_previous*w0 + F2_previous*w2 + w4) / w5.
    for slot in ("900", "902", "904"):
        if "F12 = F0 * F12" not in instruction(lines, slot):
            raise SystemExit(f"opcode 0x35 slot {slot} missing correction multiply")
    for slot in ("901", "903", "906"):
        if "F0 = F11 - F12" not in instruction(lines, slot):
            raise SystemExit(f"opcode 0x35 slot {slot} missing F11 correction")
    if "F0 = F0 * F7" not in instruction(lines, "907"):
        raise SystemExit("opcode 0x35 missing final corrected-numerator multiply")
    if "IF FLAG1_IN, JUMP" not in instruction(lines, "905"):
        raise SystemExit("opcode 0x35 missing output FIFO wait at 905")
    if "RTS (DB)" not in instruction(lines, "906"):
        raise SystemExit("opcode 0x35 missing delayed return at 906")
    if "DM(I1, M0) = R0" not in instruction(lines, "908"):
        raise SystemExit("opcode 0x35 does not emit R0 at 908")
    if "IF FLAG0_IN, JUMP" not in instruction(lines, "909"):
        raise SystemExit("opcode 0x35 boundary does not reach opcode 0x36")

    print("PASS: SHARC opcode-0x35 six-read, three-correction, one-write contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
