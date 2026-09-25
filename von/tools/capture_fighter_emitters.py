#!/usr/bin/env python3
"""Recover a selected fighter's emitter -> OBA table over MAME's GDB stub.

The i960 transform emitters tag each part with its ROM **OBA** in `g4` (body
emitter `0x8e164`) or `r6` (limb/option emitter `0x8d488`), while the part's
record pointer sits in `g2`.  Breaking repeatedly at the emitters therefore
yields the exact `g2 -> OBA` and `r6 -> OBA` maps (see
`von-arcade-decomp/von/i960/motion-emitter-findings.md`).

Unlike the archived `von-discovery` probe, this drives the deterministic
`action_schedule.lua` machine-select path, so a *non-default* fighter (Viper II
needs four right presses) is actually present during the sampled window.  The
result labels every emitted part so a geometry trace can be joined to the
emitter's notion of the model.

Usage:
    python3 tools/capture_fighter_emitters.py --fighter Viper2 \
        --select-steps 4 --oba-prefix 0x00a1 \
        --out build/lineage/Viper2/emitters.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# i960 transform emitters observed on the original ROM.
DEFAULT_BREAKS = [0x8E164, 0x8DE14, 0x8D488, 0x8D714, 0x8E37C]
OBA_LO = 0x00800000
OBA_HI = 0x00B00000


def _decomp_root() -> Path:
    env = os.environ.get("VON_DECOMP")
    if env:
        return Path(env).resolve()
    return (ROOT / ".." / "von-arcade-decomp").resolve()


def oba_from_g4(g4: int) -> int:
    """The emitter's OBA is a ROM pointer in the 0x0080_0000..0x00b0_0000 bank."""
    return g4 if OBA_LO <= g4 <= OBA_HI else 0


def oba_for_breakpoint(ip: int, regs: dict[str, int]) -> int:
    """Read the OBA from the register the emitter holds it in at `ip`.

    The body emitter (`0x8de14`/`0x8e164`) has it in `g4`; the limb emitter
    (`0x8d488`) in `r6` and the option emitter (`0x8d714`) in `r10`, with `g5`
    as a fallback.  This is what lets a *limb* OBA (e.g. a far-leg part) be
    observed even though only the body map is keyed by `g2`.
    """
    if ip in (0x8DE14, 0x8E164):
        return oba_from_g4(regs.get("g4", 0))
    if ip == 0x8D488:
        return oba_from_g4(regs.get("r6", 0)) or oba_from_g4(regs.get("g5", 0))
    if ip == 0x8D714:
        return oba_from_g4(regs.get("r10", 0)) or oba_from_g4(regs.get("g5", 0))
    return 0


def is_body_breakpoint(ip: int) -> bool:
    return ip in (0x8DE14, 0x8E164)


def record(mapping: dict[str, str], key: int, oba: int) -> bool:
    """Merge one `key -> OBA` observation.  Returns True on a conflicting key."""
    entry = f"{oba:08x}"
    k = f"{key:08x}"
    conflict = k in mapping and mapping[k] != entry
    mapping[k] = entry
    return conflict


def _registers(mcp) -> dict[str, int]:
    regs = mcp.call("gdb_read_registers", {}).get("registers", [])
    out: dict[str, int] = {}
    for reg in regs:
        name = reg.get("name")
        if not name:
            continue
        raw = reg.get("hex", "")
        out[name] = int.from_bytes(bytes.fromhex(raw), "little") if raw else 0
    return out


def _load_mcp():
    decomp = _decomp_root()
    sys.path.insert(0, str(decomp / "tools" / "mame-mcp"))
    import mame_mcp  # noqa: E402

    return mame_mcp


def _runs(mcp, breaks, samples, seconds, oba_prefix, log_every) -> tuple[dict, dict, set, int, int]:
    for address in breaks:
        mcp.call("gdb_breakpoint", {"address": address})
    g2map: dict[str, str] = {}
    r6map: dict[str, str] = {}
    emitted: set[str] = set()
    conflicts = 0
    matched = 0
    started = time.time()
    for sample in range(samples):
        if time.time() - started > seconds:
            break
        try:
            mcp.call("gdb_continue", {})
        except Exception as exc:  # MAME reached -seconds_to_run or exited.
            print(f"emitter probe: run ended after {sample} samples ({exc})", file=sys.stderr)
            break
        regs = _registers(mcp)
        ip = regs.get("ip", 0)
        r6, g2 = regs.get("r6", 0), regs.get("g2", 0)
        oba = oba_for_breakpoint(ip, regs)
        if not oba or (oba >> 16) != oba_prefix:
            continue
        matched += 1
        emitted.add(f"{oba:08x}")
        if is_body_breakpoint(ip):
            conflicts += record(g2map, g2, oba)
        conflicts += record(r6map, r6, oba)
        if log_every and matched % log_every == 0:
            print(f"emitter probe: {matched} matched hits, g2={len(g2map)} "
                  f"r6={len(r6map)} obas={len(emitted)}")
    return g2map, r6map, emitted, conflicts, matched


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--fighter", required=True, help="display name, for the record")
    ap.add_argument("--select-steps", type=int, default=0,
                    help="machine-select right presses before confirming")
    ap.add_argument("--oba-prefix", type=lambda x: int(x, 0), required=True,
                    help="OBA family high word, e.g. 0x00a1 for Viper II")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--samples", type=int, default=200000, help="max gdb_continue hits")
    ap.add_argument("--max-seconds", type=float, default=900.0,
                    help="wall-clock budget for the sampling loop")
    ap.add_argument("--seconds-to-run", type=int, default=120,
                    help="MAME emulated seconds (must outlast the match start)")
    ap.add_argument("--start-frame", type=int, default=2120,
                    help="action_schedule confirm frame (default matches the bakes)")
    ap.add_argument("--schedule", type=Path,
                    default=_decomp_root() / "von" / "tools" / "action_schedule.lua")
    ap.add_argument("--mame", default=os.environ.get("VON_MAME_BIN", ""))
    ap.add_argument("--rompath", default=os.environ.get("VON_ROMPATH", ""))
    ap.add_argument("--work-dir", type=Path, default=None)
    ap.add_argument("--log-every", type=int, default=5000)
    args = ap.parse_args()

    decomp = _decomp_root()
    mame = args.mame or str(decomp / "bin" / "von")
    rompath = args.rompath or str(decomp / "von" / "build" / "disasm" / "rompath")
    work = args.work_dir or args.out.parent
    work.mkdir(parents=True, exist_ok=True)
    action_log = work / "emitter-actions.log"

    mame_mcp = _load_mcp()
    mcp = mame_mcp.MameMcp()
    schedule = str(args.schedule)
    mame_args = [
        "vonj", "-rompath", rompath, "-video", "none", "-sound", "none", "-oslog",
        "-autoboot_script", schedule, "-seconds_to_run", str(args.seconds_to_run),
        "-skip_gameinfo", "-nothrottle",
    ]
    env = {
        "VON_ACTION_LOG": str(action_log),
        "VON_ACTION_SECONDS": str(args.seconds_to_run),
        "VON_ACTION_START_FRAME": str(args.start_frame),
        "VON_ACTION_CYCLES": "1",
        "VON_ACTION_SELECT_STEPS": str(args.select_steps),
        "VON_FIFO_MAX": "1",
    }
    print(f"emitter probe: {args.fighter} select_steps={args.select_steps} "
          f"prefix={args.oba_prefix:#06x} mame={mame}")
    try:
        mcp.call("mame_start", {
            "executable": mame, "cwd": str(work), "args": mame_args, "env": env,
            "timeout": max(30.0, args.max_seconds),
            "connect_timeout": 60.0,
        })
        g2map, r6map, emitted, conflicts, matched = _runs(
            mcp, DEFAULT_BREAKS, args.samples, args.max_seconds,
            args.oba_prefix, args.log_every)
    finally:
        try:
            mcp.call("mame_stop", {})
        except Exception:
            pass

    document = {
        "schema": "von-fighter-emitter-oba/1",
        "fighter": args.fighter,
        "select_steps": args.select_steps,
        "oba_prefix": f"{args.oba_prefix:#06x}",
        "matched_hits": matched,
        "conflicts": conflicts,
        "emitted_obas": sorted(emitted),
        "g2": g2map,
        "r6": r6map,
    }
    args.out.write_text(json.dumps(document, indent=1, sort_keys=True) + "\n",
                        encoding="utf-8")
    print(f"emitter probe: {matched} matched hits, {len(g2map)} g2, "
          f"{len(r6map)} r6, {len(emitted)} obas, {conflicts} conflicts -> {args.out}")
    return 0 if g2map else 1


if __name__ == "__main__":
    raise SystemExit(main())
