#!/usr/bin/env python3
"""Audit the exact FIFO shape of the SHARC scalar services 0x00-0x02."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def main() -> int:
    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body

    operations = {"137": "F0 = F0 + F1", "13f": "F0 = F0 - F1", "147": "F0 = F0 * F1"}
    for start, operation in (("133", operations["137"]), ("13b", operations["13f"]), ("143", operations["147"])):
        service_slots = [f"{int(start, 16) + offset:03x}" for offset in range(8)]
        expected = {
            service_slots[0]: "IF FLAG0_IN, JUMP",
            service_slots[1]: "R0 = DM(I0, M0)",
            service_slots[2]: "IF FLAG0_IN, JUMP",
            service_slots[3]: "R1 = DM(I0, M0)",
            service_slots[4]: operation,
            service_slots[5]: "IF FLAG1_IN, JUMP",
            service_slots[6]: "DM(I1, M0) = R0",
            service_slots[7]: "RTS",
        }
        for slot, fragment in expected.items():
            if fragment not in lines.get(slot, ""):
                raise SystemExit(f"SHARC scalar service {start} slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x00/0x01/0x02 two-input scalar service contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
