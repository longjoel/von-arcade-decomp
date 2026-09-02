#!/usr/bin/env python3
"""Audit the four-input SHARC clipped state projection at opcode 0x22."""

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

    for slot, register in zip(("42a", "42c", "42e", "430"), ("R0", "R1", "R2", "R3")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x22 slot {slot} missing {register} FIFO read")
    for slot in ("429", "42b", "42d", "42f"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x22 slot {slot} missing FIFO wait")

    checks = {
        "431": "I7 = DM(0x00030101)",
        "432": "R4 = DM(0x00000002, I7)",
        "433": "R4 = DM(0x05, I7)",
        "434": "R4 = DM(0x08, I7)",
        "435": "R15 = DM(0x0B, I7)",
        "437": "F15 = F8 + F15",
        "438": "IF LT, JUMP (0x00020467)",
        "43b": "R13 = DM(0x09, I7)",
        "440": "R12 = DM(0x0A, I7)",
        "442": "R12 = R15",
        "443": "I6 = 0x00030136",
        "446": "F0 = RECIPS F12",
        "453": "COMP(F2, F6)",
        "454": "IF GE, JUMP (0x00020463)",
        "45f": "IF FLAG1_IN, JUMP",
        "461": "DM(I1, M0) = R15",
        "463": "IF FLAG1_IN, JUMP",
        "465": "DM(I1, M0) = 0xBF800000",
        "467": "IF FLAG1_IN, JUMP",
        "469": "DM(I1, M0) = 0xC0000000",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x22 slot {slot} missing {fragment}")

    # Exact column-major coefficient order for the three affine accumulators.
    for slot, offset in (("432", "02"), ("433", "05"), ("434", "08"),
                         ("435", "0B"), ("436", "00"), ("439", "03"),
                         ("43a", "06"), ("43b", "09"), ("43c", "01"),
                         ("43d", "04"), ("43e", "07"), ("440", "0A")):
        fragments = (f"DM(0x{offset}, I7)",
                     f"DM(0x000000{offset}, I7)")
        if not any(fragment in lines.get(slot, "") for fragment in fragments):
            raise SystemExit(f"SHARC opcode-0x22 coefficient slot {slot} missing offset {offset}")

    print("PASS: SHARC opcode-0x22 clipped state-projection contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
