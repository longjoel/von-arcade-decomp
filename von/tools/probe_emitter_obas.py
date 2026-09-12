#!/usr/bin/env python3
"""Probe the transform emitters to recover the exact emitter -> OBA table.

Uses the MAME GDB stub (via tools/mame-mcp) to break repeatedly at the i960
transform emitters. At the body emitter (`0x8e164`) the part's OBA is in `g4`
(also `r10`); at the option/limb emitter (`0x8d488`) it is in `r6`. This records
`(pc, r6, g2, g4)` and emits the `g2 -> OBA` and `r6 -> OBA` maps so a FIFO
trace's packets can be labelled with their part OBA.

Requires an instrumented MAME build with the i960 GDB stub (patch 0043) at
`bin/von`, and the staged ROM path.

    python3 von/tools/probe_emitter_obas.py --samples 600
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "mame-mcp"))
from mame_mcp import MameMcp  # noqa: E402

DEFAULT_BREAKS = [0x8E164, 0x8DE14, 0x8D488, 0x8D714, 0x8E37C]


def reg_val(r):
    h = r.get("hex", "")
    return int.from_bytes(bytes.fromhex(h), "little") if h else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--executable", default=str(ROOT / "bin" / "von"))
    ap.add_argument("--rompath", default=str(ROOT / "von" / "build" / "disasm" / "rompath"))
    ap.add_argument("--samples", type=int, default=400)
    ap.add_argument("--out-dir", type=Path, default=ROOT / "von" / "i960")
    args = ap.parse_args()

    srv = MameMcp()
    srv.call("mame_start", {
        "executable": args.executable, "cwd": str(ROOT),
        "args": ["vonj", "-rompath", args.rompath, "-video", "none", "-sound", "none",
                 "-skip_gameinfo", "-seconds_to_run", "240"],
        "timeout": 180.0, "connect_timeout": 30.0,
    })
    g2map: dict[str, str] = {}
    r6map: dict[str, str] = {}
    conflicts = 0
    try:
        for br in DEFAULT_BREAKS:
            srv.call("gdb_breakpoint", {"address": br})
        for _ in range(args.samples):
            srv.call("gdb_continue", {})
            regs = srv.call("gdb_read_registers", {}).get("registers", [])
            d = {r["name"]: reg_val(r) for r in regs if r.get("name")}
            r6, g2, g4 = d.get("r6", 0), d.get("g2", 0), d.get("g4", 0)
            oba = g4 if 0x00800000 <= g4 <= 0x00B00000 else 0
            if oba:
                for mp, key in ((g2map, f"{g2:08x}"), (r6map, f"{r6:08x}")):
                    if key in mp and mp[key] != f"{oba:08x}":
                        conflicts += 1
                    mp[key] = f"{oba:08x}"
    finally:
        srv.call("mame_stop", {})

    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "emitter-g2-oba.json").write_text(json.dumps(g2map, indent=1) + "\n")
    (args.out_dir / "emitter-r6-oba.json").write_text(json.dumps(r6map, indent=1) + "\n")
    print(f"g2->OBA: {len(g2map)}  r6->OBA: {len(r6map)}  conflicts: {conflicts}")
    for k in sorted(g2map):
        print(f"  g2 {k} -> {g2map[k]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
