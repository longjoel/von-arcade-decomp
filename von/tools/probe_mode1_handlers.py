#!/usr/bin/env python3
"""Instruction-level probe for the reachable mode-1 phase-table handlers.

Runs the original input-free attract on the MAME GDB stub, breaks once at each
reachable handler entry, and records the g-register file plus work-RAM windows
at that instant (JSONL). Diffing consecutive records attributes each handler's
writes. Usage: python3 von/tools/probe_mode1_handlers.py [output.jsonl]

The public attract fixture (von/tools/probe_mode_transitions.lua) shows the
phase order; this probe supplies the concrete effect data for translation.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/mame-mcp"))
from mame_mcp import MameMcp  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/handler_probes.jsonl"

# Reachable mode-1 phase-table targets (phase -> entry).
HANDLERS = {
    0x2b500: 0, 0x2b810: 3, 0x2b870: 4, 0x2dc50: 5, 0x2dd30: 6, 0x2ded0: 7,
    0x2b550: 8, 0x2b660: 9, 0xd24b0: 10, 0xd2560: 11, 0xd25b0: 12,
    0xe3ab0: 13, 0xe3d00: 14, 0x2b7b0: 1, 0x2b7e0: 2,
}
REG_G = {f"g{i}": 16 + i for i in range(15)}

WINDOWS = [
    (0x503a00, 0x1600),
    (0x504c00, 0x400),
    (0x51a000, 0x1000),
    (0x51c000, 0x1000),
    (0x577000, 0x800),
]

m = MameMcp()
out = open(OUT, "w")


def regs():
    raw = m.call("gdb_raw", {"packet": "g"})["reply"]
    data = bytes.fromhex(raw)
    values = {}
    for name, idx in REG_G.items():
        off = idx * 4
        values[name] = int.from_bytes(data[off:off + 4], "little")
    values["pc"] = int.from_bytes(data[34 * 4:34 * 4 + 4], "little")
    values["ip"] = int.from_bytes(data[36 * 4:36 * 4 + 4], "little")
    return values


def read_window(address, length):
    out_hex = []
    step = 0x400
    for off in range(0, length, step):
        n = min(step, length - off)
        reply = m.call("gdb_read_memory", {"address": address + off, "length": n})["hex"]
        out_hex.append(reply)
    return "".join(out_hex)


try:
    m.call("mame_start", {"executable": str(ROOT / "bin/von"),
        "args": ["vonj", "-rompath", str(ROOT / "von/build/disasm/rompath"),
                 "-video", "none", "-sound", "none", "-nothrottle", "-skip_gameinfo",
                 "-cfg_directory", "/tmp/mcp-handlers/cfg",
                 "-nvram_directory", "/tmp/mcp-handlers/nvram",
                 "-seconds_to_run", "95"],
        "cwd": str(ROOT), "timeout": 300, "connect_timeout": 30})
    for address in HANDLERS:
        m.call("gdb_breakpoint", {"address": address})

    hits = 0
    seen = set()
    pending = set(HANDLERS)
    while pending:
        try:
            stop = m.call("gdb_continue", {})
        except Exception as exc:
            print("continue ended:", exc)
            break
        reply = stop.get("stop", "")
        if not reply.startswith("T"):
            print("run ended:", reply)
            break
        r = regs()
        pc = r["ip"] & 0xffffff
        if pc not in HANDLERS:
            print("unexpected stop", hex(pc))
            continue
        record = {
            "hits": hits, "entry": hex(pc), "phase_index": HANDLERS[pc],
            "regs": {k: hex(v) for k, v in r.items()},
            "windows": {},
        }
        for address, length in WINDOWS:
            record["windows"][hex(address)] = read_window(address, length)
        out.write(json.dumps(record) + "\n")
        out.flush()
        hits += 1
        print(f"hit {hits}: {hex(pc)} phase {HANDLERS[pc]} g14={record['regs']['g14']}")
        seen.add(pc)
        pending.discard(pc)
        m.call("gdb_breakpoint", {"address": pc, "remove": True})
finally:
    out.close()
    print("stop:", m.call("mame_stop", {}))
