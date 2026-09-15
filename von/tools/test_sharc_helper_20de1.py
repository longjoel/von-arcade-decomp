#!/usr/bin/env python3
"""Audit the shared streamed-geometry helper at SHARC target 0x20de1.

Deterministic contract: the bootstrap disassembly must match the recovered
instruction schedule, and the opcode-0x17 sweep probe must keep its delayed
reset/seed protocol. The former runtime-trace taps are being re-expressed
through the engine's Lua API.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"
SWEEP_PROBE = ROOT / "von/tools/probe_sharc_opcode_17_helper_sweep.lua"


def main() -> int:
    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body

    checks = {
        "de1": "DM(0x00030109) = R8",
        "de2": "DM(0x0003010A) = R9",
        "de3": "I4 = 0x0003010B",
        "de4": "R0 = DM(0x00000003, I4)",
        "de5": "R4 = DM(0x00000006, I4)",
        "de6": "F1 = F0 - F4",
        "de7": "R5 = DM(0x00000008, I4)",
        "de8": "F2 = F0 - F5",
        "de9": "F3 = F0 - F4",
        "dea": "F6 = F0 - F5",
        "deb": "IF EQ, JUMP (0x00020DFC) (DB)",
        "dec": "F4 = F8 - F4",
        "ded": "F5 = F9 - F5",
        "df3": "F7 = RECIPS F12",
        "df2": "F12 = F8 - F12",
        "dfa": "F15 = F0 * F7",
        "dfb": "JUMP (0x00020E05)",
        "dfc": "R12 = R2",
        "e05": "F3 = PASS F3",
        "e06": "IF EQ, JUMP (0x00020E13)",
        "e12": "JUMP (0x00020E1E)",
        "e13": "F8 = F1 * F5",
        "e14": "F12 = F4 * F2",
        "e15": "F12 = F1 * F6",
        "e22": "R0 = DM(0x00000006, I4)",
        "e23": "DM(0x00000003, I4) = R0",
        "e24": "R0 = DM(0x00000007, I4)",
        "e25": "DM(0x00000004, I4) = R0",
        "e26": "R0 = DM(0x00000008, I4)",
        "e2d": "DM(0x00000008, I4) = R0",
        "e37": "F13 = F2 * F5",
        "e38": "F1 = F8 - F13",
        "e39": "F15 = F2 * F4",
        "e3a": "IF EQ, JUMP (0x00020E50) (DB)",
        "e3b": "F3 = F10 - F15",
        "e43": "F8 = F8 - F12",
        "e45": "F7 = RECIPS F12",
        "e4d": "RTS (DB)",
        "e4e": "R8 = DM(0x00030109)",
        "e4f": "R9 = DM(0x0003010A)",
        "e50": "R0 = 0xBDCCCCCD",
        "e51": "RTS (DB)",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC helper-0x20de1 slot {slot} missing {fragment}")
    if "F14 = F0 * F6" not in lines.get("e35", ""):
        raise SystemExit("SHARC helper-0x20de1 slot e35 missing equality product")
    equality_schedule = {
        "e32": "F1 = F11 - F14",
        "e33": "F6 = F11 - F15",
        "e34": "F8 = F1 * F6",
        "e35": "F14 = F0 * F6",
        "e36": "F10 = F0 * F5",
        "e37": "F13 = F2 * F5",
        "e38": "F1 = F8 - F13",
        "e39": "F15 = F2 * F4",
    }
    for slot, fragment in equality_schedule.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC helper-0x20de1 equality schedule missing {slot}: {fragment}")
    if "R0 = DM(0x05, I4)" not in lines.get("de6", ""):
        raise SystemExit("SHARC helper-0x20de1 slot de6 missing scratch read")

    caller_checks = {
        "36f": "F1 = F1 * F4",
        "370": "F0 = F0 * F4",
        "371": "F0 = F0 - F1",
        "372": "IF EQ, JUMP (0x0002037E)",
        "378": "CALL (0x00020DE1)",
    }
    for slot, fragment in caller_checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x17 edge gate slot {slot} missing {fragment}")

    for slot in ("dee", "def", "df0", "df1", "e07", "e13", "e14", "e15"):
        if " * " not in lines.get(slot, ""):
            raise SystemExit(f"SHARC helper-0x20de1 slot {slot} missing interpolation arithmetic")

    sweep_probe = SWEEP_PROBE.read_text(encoding="utf-8")
    reset_order = (
        "command(0x0d, 0x00000000)",
        "pending_case = case_index",
        "pending_frame = frame + (true_selector and 60 or 10)",
        "if pending_case and frame == pending_frame then",
        "seed(records[test[3]], true_selector and (test[3] - 1) or 0)",
        "write_17(test[1], test[2])",
    )
    positions = [sweep_probe.find(fragment) for fragment in reset_order]
    if any(position < 0 for position in positions):
        raise SystemExit("opcode-0x17 sweep probe lacks delayed reset/seed protocol")
    if positions != sorted(positions):
        raise SystemExit("opcode-0x17 sweep probe seeds before delayed opcode-0x0d reset")
    selector_probe = (
        'true_selector = tonumber(os.getenv("VON_SHARC_17_TRUE_SELECTOR") or "0") ~= 0',
        'data_space:write_u32(0x00030201, selector or 0)',
        'if true_selector then',
        '0x00030300 + (bank - 1) * 16 + index - 1',
        'seed(records[test[3]], true_selector and (test[3] - 1) or 0)',
    )
    for fragment in selector_probe:
        if fragment not in sweep_probe:
            raise SystemExit(f"opcode-0x17 sweep probe missing selector experiment: {fragment}")
    print("PASS: SHARC helper-0x20de1 geometry interpolation/validation contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
