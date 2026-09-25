#!/usr/bin/env python3
"""Recover the opponent-AI class -> command mapping over MAME's GDB stub.

Lua data write taps do not fire on the i960 object RAM in this build (see
``probe_ai_commands.lua``), so this uses the debugger instead: a hardware
**write watchpoint** on the CPU object's command word (``object+0x108``) stops
execution at the write, where the behaviour class (``0x504d94``) and the command
word are read together. That gives a clean class -> command map to validate the
Godot AI port (``scripts/von_ai.gd``).

    python3 probe_ai_commands_gdb.py --out build/ai-commands.json --samples 400
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

CMD = 0x005041D8        # CPU object + 0x108 (synthesised command word)
CLASS = 0x00504D94
SECTOR = 0x00504D68
PLAYER_CMD = 0x00503BD8  # player object + 0x108 (for contrast)


def _decomp_root() -> Path:
    env = os.environ.get("VON_DECOMP")
    if env:
        return Path(env).resolve()
    return (Path(__file__).resolve().parents[2]).resolve()


def _load_mcp():
    decomp = _decomp_root()
    sys.path.insert(0, str(decomp / "tools" / "mame-mcp"))
    import mame_mcp  # noqa: E402

    return mame_mcp


def _u16(mcp, address: int) -> int:
    reply = mcp.call("gdb_read_memory", {"address": address, "length": 2})
    raw = reply.get("bytes") or reply.get("data") or reply.get("value")
    if isinstance(raw, str):
        data = bytes.fromhex(raw)
    elif isinstance(raw, list):
        data = bytes(int(x) for x in raw)
    else:
        return -1
    return int.from_bytes(data[:2], "little")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--samples", type=int, default=400)
    ap.add_argument("--max-seconds", type=float, default=600.0)
    ap.add_argument("--seconds-to-run", type=int, default=180)
    ap.add_argument("--mame", default=os.environ.get("VON_MAME_BIN", ""))
    ap.add_argument("--rompath", default=os.environ.get("VON_ROMPATH", ""))
    ap.add_argument("--work-dir", type=Path, default=None)
    args = ap.parse_args()

    decomp = _decomp_root()
    mame = args.mame or str(decomp / "bin" / "von")
    rompath = args.rompath or str(decomp / "von" / "build" / "disasm" / "rompath")
    work = args.work_dir or args.out.parent
    work.mkdir(parents=True, exist_ok=True)

    mame_mcp = _load_mcp()
    mcp = mame_mcp.MameMcp()
    mame_args = [
        "vonj", "-rompath", rompath, "-video", "none", "-sound", "none", "-oslog",
        "-seconds_to_run", str(args.seconds_to_run), "-skip_gameinfo", "-nothrottle",
    ]
    print(f"ai-probe: {mame} -> {args.out}")
    records = []
    try:
        mcp.call("mame_start", {
            "executable": mame, "cwd": str(work), "args": mame_args,
            "timeout": args.max_seconds, "connect_timeout": 60.0,
        })
        # Hardware write watchpoint on the CPU command word.
        wpset = mcp.call("gdb_monitor", {"command": f"wpset {CMD:x},2,w"})
        print("wpset:", wpset.get("output", "").strip())
        started = time.time()
        for _ in range(args.samples):
            if time.time() - started > args.max_seconds:
                break
            try:
                mcp.call("gdb_continue", {})
            except Exception as exc:  # MAME reached -seconds_to_run or exited.
                print(f"ai-probe: run ended ({exc})", file=sys.stderr)
                break
            cls = _u16(mcp, CLASS)
            sector = _u16(mcp, SECTOR)
            command = _u16(mcp, CMD)
            records.append({"class": cls, "sector": sector, "command": command})
    finally:
        try:
            mcp.call("mame_stop", {})
        except Exception:
            pass

    by_class: dict[str, dict[str, int]] = {}
    for record in records:
        bucket = by_class.setdefault(str(record["class"]), {})
        key = f"{record['command']:04x}"
        bucket[key] = bucket.get(key, 0) + 1
    document = {
        "schema": "von-ai-commands/1",
        "samples": len(records),
        "class_command": by_class,
        "wpset": wpset.get("output", ""),
        "records": records,
    }
    args.out.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n")
    print(f"ai-probe: {len(records)} stops -> {args.out}")
    for cls in sorted(by_class, key=lambda x: int(x)):
        common = sorted(by_class[cls].items(), key=lambda kv: -kv[1])[:4]
        print(f"  class {cls:>3}: {common}")
    return 0 if records else 1


if __name__ == "__main__":
    raise SystemExit(main())
