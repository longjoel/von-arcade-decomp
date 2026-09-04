#!/usr/bin/env python3
"""Audit the static boundary and high-confidence guards of i960 0x79d60."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"
# The checked-in worklist is authoritative.  The 60-second trace output is
# reproducible, but is intentionally prunable and must not be required by the
# contract suite.
WORKLIST = ROOT / "von/attract_worklist.json"


def main() -> int:
    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        address, body = line.split(":", 1)
        address = address.strip()
        if len(address) == 5 and all(char in "0123456789abcdef" for char in address):
            lines[address] = body

    checks = {
        "79d60": "mov\tg0,r4",
        "79d64": "ld\t0x74(r4),r5",
        "79d68": "bal\t0xf5058",
        "79d6c": "ld\t0x64(r4),g4",
        "79d70": "cmpo\t9,g4",
        "79d74": "remi\t10,g0,g0",
        "79d80": "ld\t0x79d8c[g4*4],g4",
        "79d88": "bx\t(g4)",
        "79db4": "ld\t0x504e30,g4",
        "79dbc": "chkbit\t1,g4",
        "79dc8": "bno\t0x7a1f4",
        "79dd4": "cvtir\tg4,fp0",
        "79ddc": "mov\t0,g2",
        "79de8": "ld\t0xffffff30(g5),g4",
        "79dfc": "bg\t0x7a1f4",
        "79e08": "ble\t0x7a11c",
        "79e0c": "b\t0x7a1f4",
        # State 1: timing bands, related-object tag bands, and mode/state exits.
        "79e10": "ld\t0x504d60,g4",
        "79e20": "lda\t0x40590000,r7",
        "79e28": "cmprl\tfp0,r6",
        "79e30": "ldos\t0x172(r5),g4",
        "79e40": "cmpible\tg4,r7,0x79e58",
        "79e54": "cmpible\tg4,r6,0x7a204",
        "79e68": "lda\t0x4062c000,r7",
        "79e70": "cmprl\tfp0,r6",
        "79e78": "cmpibl\t5,g0,0x7a1e4",
        "79e7c": "cmpibl\t2,g0,0x7a1cc",
        "79e80": "b\t0x7a204",
        "79e84": "cmpibl\t4,g0,0x7a080",
        "79e88": "b\t0x7a11c",
        # State 5: timing bands and direct transition-selector writes.
        "79f5c": "ld\t0x504d60,g4",
        "79f78": "ldl\t0x504d98,g6",
        "79f80": "bl\t0x79fdc",
        "79f94": "bge\t0x79fcc",
        "79f98": "cmpibge\t4,g0,0x79fb0",
        "79fa4": "bbc\t1,g4,0x79fb0",
        "79fa8": "mov\t14,g6",
        "79fb0": "shro\t31,g0,g4",
        "79fbc": "subo\tg4,g0,g4",
        "79fc4": "mov\t15,g6",
        "79fcc": "cmpibl\t2,g0,0x79fa8",
        "79fd8": "bbs\t1,g4,0x79fa8",
        "79fdc": "mov\t13,g6",
        "79fe8": "st\tg6,0x504d98",
        # State 6: related-object state/tag gate, timing window, and mode exits.
        "7a098": "ld\t0x64(r5),g4",
        "7a09c": "cmpibne\t3,g4,0x7a0bc",
        "7a0a0": "ld\t0x504e4c,g4",
        "7a0ac": "cmpibne\t6,g4,0x7a0bc",
        "7a0b8": "bbs\t1,g4,0x7a11c",
        "7a0bc": "ld\t0x504d60,g4",
        "7a0cc": "lda\t0x40568000,r7",
        "7a0d8": "bl\t0x7a0f0",
        "7a0e0": "lda\t0x405b8000,r7",
        "7a0ec": "ble\t0x7a110",
        "7a0f0": "ld\t0x504d9c,g4",
        "7a110": "ld\t0x504e30,g4",
        "7a118": "bbc\t1,g4,0x7a12c",
        "7a11c": "mov\t14,r7",
        "7a120": "st\tr7,0x504d98",
        # State 7: related-object tag/state gates and the mode-dependent exits.
        "7a150": "ldos\t0x172(r5),g4",
        "7a160": "cmpible\tg4,r7,0x7a178",
        "7a174": "cmpible\tg4,r6,0x7a1b4",
        "7a178": "ld\t0x64(r5),g4",
        "7a17c": "cmpibne\t4,g4,0x7a18c",
        "7a188": "cmpibge\t3,g4,0x7a1b4",
        "7a190": "cmpibne\t1,g4,0x7a1a0",
        "7a19c": "cmpibne\t0,g4,0x7a1b4",
        "7a1a4": "cmpibne\t6,g4,0x7a1c0",
        "7a1b0": "cmpibe\t0,g4,0x7a1c0",
        "7a1bc": "bbs\t2,g4,0x7a1e4",
        "7a1c8": "bbc\t1,g4,0x7a1dc",
        "7a1cc": "mov\t14,r6",
        "7a1d0": "st\tr6,0x504d98",
        # State 2: timing bands and mode-bit exits.
        "79e8c": "ld\t0x504d60,g4",
        "79e9c": "lda\t0x4062c000,r7",
        "79ea4": "cmprl\tfp0,r6",
        "79eac": "ld\t0x504e30,g4",
        "79eb4": "bbs\t2,g4,0x7a1e4",
        "79eb8": "b\t0x7a1f4",
        "79ec0": "lda\t0x40790000,r7",
        "79ecc": "bge\t0x79ee4",
        "79ed0": "ld\t0x504e30,g4",
        "79ed8": "bbs\t2,g4,0x7a1e4",
        "79edc": "bbs\t1,g4,0x7a1cc",
        "79ee0": "b\t0x7a204",
        "79eec": "bbs\t2,g4,0x7a080",
        "79ef0": "b\t0x7a204",
        # State 3: timing bands, caller-state, related-state, and mode gates.
        "79ef4": "ld\t0x504d60,g4",
        "79f04": "lda\t0x40590000,r7",
        "79f10": "bge\t0x79f48",
        "79f14": "cmpibl\t2,g0,0x7a204",
        "79f18": "ld\t0x64(r5),g4",
        "79f1c": "cmpibe\t6,g4,0x7a204",
        "79f24": "cmpibe\t3,g4,0x7a204",
        "79f28": "cmpibge\t1,g0,0x79f38",
        "79f34": "bbs\t2,g4,0x7a080",
        "79f40": "bbs\t1,g4,0x7a11c",
        "79f44": "b\t0x7a1f4",
        "79f48": "cmpibl\t3,g0,0x7a204",
        "79f54": "bbs\t2,g4,0x7a080",
        "79f58": "b\t0x7a204",
        # State 4: timing bands and absolute caller-state selector logic.
        "79f5c": "ld\t0x504d60,g4",
        "79f6c": "lda\t0x40590000,r7",
        "79f78": "ldl\t0x504d98,g6",
        "79f80": "bl\t0x79fdc",
        "79f88": "lda\t0x40690000,r7",
        "79f94": "bge\t0x79fcc",
        "79f98": "cmpibge\t4,g0,0x79fb0",
        "79fa4": "bbc\t1,g4,0x79fb0",
        "79fa8": "mov\t14,g6",
        "79fb0": "shro\t31,g0,g4",
        "79fbc": "subo\tg4,g0,g4",
        "79fc0": "cmpibne\t1,g4,0x79fdc",
        "79fc4": "mov\t15,g6",
        "79fcc": "cmpibl\t2,g0,0x79fa8",
        "79fd8": "bbs\t1,g4,0x79fa8",
        "79fdc": "mov\t13,g6",
        "79fe8": "st\tg6,0x504d98",
        # States 8/9 and shared terminal exits.
        "7a204": "mov\t13,r7",
        "7a208": "st\tr7,0x504d98",
        "7a214": "ret",
        "7a1e4": "mov\t15,r7",
        "7a1e8": "st\tr7,0x504d98",
        "7a1f4": "mov\t13,r6",
        "7a1f8": "st\tr6,0x504d98",
        "7a218": "ret",
    }
    for address, fragment in checks.items():
        if fragment not in lines.get(address, ""):
            raise SystemExit(f"secondary dispatcher slot {address} missing {fragment}")

    targets = [
        "00079db4", "00079e10", "00079e8c", "00079ef4", "00079f5c",
        "00079ff4", "0007a098", "0007a150", "0007a204", "0007a214",
    ]
    table_addresses = [
        "79d8c", "79d90", "79d94", "79d98", "79d9c",
        "79da0", "79da4", "79da8", "79dac", "79db0",
    ]
    for index, (address, target) in enumerate(zip(table_addresses, targets)):
        body = lines.get(address, "")
        if target not in body:
            raise SystemExit(f"secondary dispatcher table entry {index} missing {target}")

    worklist_entry = next(
        entry for entry in json.loads(WORKLIST.read_text(encoding="utf-8"))["units"]
        if entry.get("entry") == "0x00079d60"
    )
    if worklist_entry.get("observed_call_edges") != 5:
        raise SystemExit("secondary dispatcher worklist edge count changed")
    if worklist_entry.get("triage") != "modeled-integration-queue":
        raise SystemExit("secondary dispatcher worklist triage changed")

    print("PASS: secondary object-state dispatcher boundary plus states 0-9 and terminal exits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
