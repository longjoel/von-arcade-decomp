#!/usr/bin/env python3
"""Enumerate the i960 -> SHARC FIFO "programs" from a traced MAME log.

The copro FIFO (0x884000) carries the SHARC opcode stream. Each writing PC
plays a fixed role: some write an opcode word, others write an argument. This
tool reports, per writing PC, the words it emits, and reconstructs the opcode
signature of a packet starting at a chosen PC.

The transform emitter packet is
`05 2f <off0..2> 16 <rotA> 15 <rotB> 14 <rotC> 3a <read> [06]`
(see decode_fifo_program.py). This tool surfaces the *other* programs, e.g. the
look-at service `25 <x y z>` (SHARC angular projection) at i960 0x9ed44 and the
spherical service `45` at 0x9ee58.
"""
from __future__ import annotations

import argparse
import re
import struct
from collections import defaultdict
from pathlib import Path

EMIT = re.compile(r"vonj_emitter: time=([0-9.]+) pc=([0-9a-f]+) data=([0-9a-f]+) r6=([0-9a-f]+) g0=([0-9a-f]+) g2=([0-9a-f]+)")

# SHARC opcodes (decimal word) -> short name, from sharc-command-annotations.md
OPCODE_NAME = {
    0x00: "fadd", 0x01: "fsub", 0x02: "fmul", 0x03: "fdiv", 0x04: "divresid",
    0x05: "rec-advance", 0x06: "rec-decrement", 0x07: "upload12", 0x08: "init",
    0x09: "transform4", 0x0a: "dot?", 0x0b: "cross", 0x0c: "normalize",
    0x0e: "store4", 0x0f: "angle-signed", 0x10: "identity", 0x11: "readback12",
    0x12: "matrix-vec-tail", 0x13: "rowscale3x3", 0x14: "rotX", 0x15: "rotY",
    0x16: "rotZ", 0x17: "determinant", 0x18: "table-window", 0x19: "counter-read",
    0x1a: "affine-out", 0x1b: "cos?", 0x1c: "sin?", 0x1d: "cos2?", 0x1e: "sin2?",
    0x1f: "dist", 0x20: "tail-read", 0x21: "store6", 0x22: "projection",
    0x23: "normalize-dir", 0x24: "frame-transpose", 0x25: "angular-projection",
    0x26: "store5", 0x27: "normal-path", 0x28: "projected-pred", 0x29: "state-init",
    0x2a: "matrix-scale", 0x2b: "status-ok", 0x2c: "trans+euler", 0x2d: "passthrough",
    0x2e: "packed-trans+euler", 0x2f: "interp-fixed", 0x30: "trans+scaledZ",
    0x31: "projection2", 0x32: "angle+trans", 0x33: "angle+trans2", 0x34: "vec2+angle",
    0x35: "stateful-div", 0x36: "trans-tail+scale", 0x37: "identity+trans",
    0x38: "packed-proj", 0x39: "table-copy", 0x3a: "seeded-output", 0x3b: "bridge",
    0x3c: "state-update", 0x3d: "state-update2", 0x3e: "math", 0x3f: "normal-3f",
    0x40: "base-addr", 0x41: "byte-lane", 0x42: "packed-euler", 0x43: "rowmajor-proj",
    0x44: "const-init", 0x45: "spherical-projection", 0x46: "state-upload7",
    0x47: "geometry-pred", 0x48: "state-upload5", 0x49: "dist3d", 0x4a: "pred-eager",
    0x4b: "pred-finite", 0x4c: "pred-eager2", 0x4d: "decision",
}


def f32(data: int) -> float:
    return struct.unpack(">f", (data & 0xFFFFFFFF).to_bytes(4, "big"))[0]


def scan(log: Path):
    per_pc = defaultdict(list)  # pc -> [data]
    seq = defaultdict(list)     # within-packet sequence is not tracked here
    for line in log.open(errors="ignore"):
        if "vonj_emitter" not in line:
            continue
        m = EMIT.search(line)
        if m:
            per_pc[int(m.group(2), 16)].append(int(m.group(3), 16) & 0xFFFFFFFF)
    return per_pc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("log", type=Path)
    ap.add_argument("--pc", type=lambda s: int(s, 0), action="append",
                    help="print the program signature for this start PC (data==5)")
    args = ap.parse_args()
    per_pc = scan(args.log)
    print(f"{'pc':>9} {'writes':>9} {'distinct':>9}  samples")
    for pc in sorted(per_pc):
        vals = per_pc[pc]
        distinct = sorted(set(vals))
        sample = ", ".join(f"0x{v:x}" for v in distinct[:4])
        print(f"{pc:>9x} {len(vals):>9} {len(distinct):>9}  {sample}")
    if args.pc:
        print("\nprogram signatures:")
        for pc in args.pc:
            vals = per_pc.get(pc, [])
            print(f"  start 0x{pc:x}: " + " ".join(f"0x{v:x}" for v in vals[:24]))
    # opcode usage: count only writes from PCs that emit exactly one distinct
    # word for the whole trace (a fixed opcode slot, not an argument slot).
    print("\nopcode word usage (constant-word writer PCs only):")
    for op in sorted(OPCODE_NAME):
        n = sum(len(v) for v in per_pc.values() if len(set(v)) == 1 and v[0] == op)
        if n:
            print(f"  0x{op:02x} {OPCODE_NAME[op]:20} {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
