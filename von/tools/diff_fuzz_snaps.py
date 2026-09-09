#!/usr/bin/env python3
"""Diff twin fuzz snapshots into per-input RAM signatures.

For each driven input, compares pre/post/settled snapshots on the P1 side
(reverted = input-driven) against the same-frame P2 snapshots (idle dummy).
P1-only reverted addresses are the driven-action fields; shared addresses
are global/background effects.

Usage: diff_fuzz_snaps.py <p1snapdir> <p2snapdir> <output.json>
Snapshot files: snap-<input>-<pre|post|settled>-<base>.txt ("%08x %08x").
"""
from __future__ import annotations
import argparse
import glob
import json
import sys
from pathlib import Path

REGIONS = [0x515000, 0x504c80, 0x5039c0, 0x500000]


def discover_inputs(snaps: dict) -> list:
    order: dict = {}
    for tag in snaps:
        if tag.endswith("-pre"):
            base = tag[:-4]
            if base + "-post" in snaps and base + "-settled" in snaps:
                order[base] = True
    return sorted(order)


def load(path: Path) -> dict[int, int]:
    data = {}
    for line in path.read_text().splitlines():
        addr, val = line.split()
        data[int(addr, 16)] = int(val, 16)
    return data


def load_side(directory: Path) -> dict:
    snaps: dict = {}
    for name in glob.glob(str(directory / "snap-*.txt")):
        stem = Path(name).stem
        parts = stem.split("-")
        base = int(parts[-1], 16)
        tag = "-".join(parts[1:-1])
        snaps.setdefault(tag, {})[base] = load(Path(name))
    return snaps


def signatures(snaps: dict, inputs: list) -> dict:
    out = {}
    for inp in inputs:
        pre = snaps.get(inp + "-pre", {})
        post = snaps.get(inp + "-post", {})
        settled = snaps.get(inp + "-settled", {})
        sig = {}
        for base in REGIONS:
            A, B, C = (pre.get(base, {}), post.get(base, {}),
                       settled.get(base, {}))
            for addr in set(A) & set(B) & set(C):
                if A[addr] != B[addr] and C[addr] == A[addr]:
                    sig[f"{addr:08x}"] = [f"{A[addr]:08x}",
                                          f"{B[addr]:08x}"]
        out[inp] = sig
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("p1snapdir", type=Path)
    p.add_argument("p2snapdir", type=Path)
    p.add_argument("output", type=Path)
    a = p.parse_args()
    p1snaps, p2snaps = load_side(a.p1snapdir), load_side(a.p2snapdir)
    inputs = discover_inputs(p1snaps)
    s1, s2 = signatures(p1snaps, inputs), signatures(p2snaps, inputs)
    report = {}
    for inp in inputs:
        only = {k: v for k, v in s1[inp].items() if k not in s2[inp]}
        report[inp] = {"p1_only": only,
                       "shared": sorted(set(s1[inp]) & set(s2[inp])),
                       "p2_only": sorted(set(s2[inp]) - set(s1[inp]))}
    a.output.write_text(json.dumps(report, indent=1) + "\n")
    for inp in inputs:
        print(f"{inp:28s} p1-only={len(report[inp]['p1_only']):3d} "
              f"shared={len(report[inp]['shared']):3d} "
              f"p2-only={len(report[inp]['p2_only']):3d}")
    print(f"wrote {a.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
