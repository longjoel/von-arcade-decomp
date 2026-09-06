#!/usr/bin/env python3
"""GameShark-style memory search over gameplay_progress.lua RAM snapshots.

Snapshots are text files with one `AAAAAAAA: bb bb ...` row per 16 bytes
(little-endian words assumed for multi-byte reads). Typical cheat-search
flow for a small discovery task:

  1. capture a baseline snapshot (e.g. cursor on Temjin)
  2. change game state (move the cursor), capture again
  3. memsearch.py diff base.txt moved.txt > round1.txt   # changed bytes
  4. change state back / to a third value, capture, then narrow:
     memsearch.py narrow round1.txt back.txt --unchanged  # keep bytes
        that returned to their baseline value
  5. memsearch.py track candidates.txt s1.txt s2.txt s3.txt  # trajectory

Subcommands:
  diff A B [--width 1|2|4]  print ADDR old new for words that differ
  narrow C SNAP --eq V|--ne V|--changed-from BASE|--unchanged-from BASE
  track C S...              print candidate values across snapshots
  stable S...               print addresses identical across all snapshots
"""
from __future__ import annotations

import argparse
import struct
import sys


def load(path: str) -> dict[int, bytes]:
    mem: dict[int, bytearray] = {}
    with open(path, errors="replace") as fh:
        for line in fh:
            addr_s, _, hex_s = line.partition(":")
            try:
                addr = int(addr_s.strip(), 16)
            except ValueError:
                continue
            chunk = bytearray()
            for tok in hex_s.split():
                if len(tok) == 2:
                    try:
                        chunk.append(int(tok, 16))
                    except ValueError:
                        pass
            if chunk:
                mem[addr] = chunk
    out: dict[int, bytes] = {}
    for addr, chunk in mem.items():
        out[addr] = bytes(chunk)
    return out


def words(mem: dict[int, bytes], width: int):
    """Yield (addr, value) for every width-sized little-endian word."""
    blob = bytearray()
    base = min(mem) if mem else 0
    top = max((a + len(c)) for a, c in mem.items()) if mem else 0
    size = top - base
    blob = bytearray(b"\x00") * size
    for addr, chunk in mem.items():
        blob[addr - base:addr - base + len(chunk)] = chunk
    fmt = {1: "<B", 2: "<H", 4: "<I"}[width]
    for off in range(0, size - width + 1, width):
        yield base + off, struct.unpack_from(fmt, blob, off)[0]


def cmd_diff(a: argparse.Namespace) -> int:
    ma, mb = load(a.a), load(a.b)
    wa = dict(words(ma, a.width))
    wb = dict(words(mb, a.width))
    n = 0
    for addr in sorted(set(wa) & set(wb)):
        if wa[addr] != wb[addr]:
            print(f"{addr:08x} {wa[addr]:0{a.width * 2}x} -> {wb[addr]:0{a.width * 2}x}")
            n += 1
    print(f"# {n} differing words (width {a.width})", file=sys.stderr)
    return 0


def load_candidates(path: str) -> set[int]:
    out = set()
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            out.add(int(line.split()[0], 16))
    return out


def cmd_narrow(a: argparse.Namespace) -> int:
    cands = load_candidates(a.candidates)
    mem = load(a.snap)
    wm = dict(words(mem, a.width))
    keep = set()
    if a.eq is not None:
        want = int(a.eq, 0)
        for addr in cands:
            if wm.get(addr) == want:
                keep.add(addr)
    elif a.ne is not None:
        want = int(a.ne, 0)
        for addr in cands:
            if wm.get(addr) != want:
                keep.add(addr)
    elif a.changed_from is not None:
        base = dict(words(load(a.changed_from), a.width))
        for addr in cands:
            if addr in wm and addr in base and wm[addr] != base[addr]:
                keep.add(addr)
    elif a.unchanged_from is not None:
        base = dict(words(load(a.unchanged_from), a.width))
        for addr in cands:
            if wm.get(addr) == base.get(addr):
                keep.add(addr)
    for addr in sorted(keep):
        print(f"{addr:08x}")
    print(f"# {len(keep)}/{len(cands)} candidates kept", file=sys.stderr)
    return 0


def cmd_track(a: argparse.Namespace) -> int:
    cands = load_candidates(a.candidates)
    snaps = [dict(words(load(p), a.width)) for p in a.snaps]
    for addr in sorted(cands):
        vals = " ".join(
            f"{s.get(addr, 0):0{a.width * 2}x}" if addr in s else "??"
            for s in snaps
        )
        print(f"{addr:08x} {vals}")
    return 0


def cmd_stable(a: argparse.Namespace) -> int:
    snaps = [dict(words(load(p), a.width)) for p in a.snaps]
    if not snaps:
        return 0
    common = set(snaps[0])
    for s in snaps[1:]:
        common &= set(s)
    n = 0
    for addr in sorted(common):
        if all(s[addr] == snaps[0][addr] for s in snaps):
            print(f"{addr:08x} {snaps[0][addr]:0{a.width * 2}x}")
            n += 1
    print(f"# {n} stable words", file=sys.stderr)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("diff", "narrow", "track", "stable"):
        sub.add_parser(name)
    args, rest = ap.parse_known_args()
    # Re-parse per subcommand for simplicity.
    if args.cmd == "diff":
        p = argparse.ArgumentParser()
        p.add_argument("a")
        p.add_argument("b")
        p.add_argument("--width", type=int, default=1, choices=(1, 2, 4))
        return cmd_diff(p.parse_args(rest))
    if args.cmd == "narrow":
        p = argparse.ArgumentParser()
        p.add_argument("candidates")
        p.add_argument("snap")
        p.add_argument("--width", type=int, default=1, choices=(1, 2, 4))
        g = p.add_mutually_exclusive_group(required=True)
        g.add_argument("--eq")
        g.add_argument("--ne")
        g.add_argument("--changed-from")
        g.add_argument("--unchanged-from")
        return cmd_narrow(p.parse_args(rest))
    if args.cmd == "track":
        p = argparse.ArgumentParser()
        p.add_argument("candidates")
        p.add_argument("snaps", nargs="+")
        p.add_argument("--width", type=int, default=1, choices=(1, 2, 4))
        return cmd_track(p.parse_args(rest))
    if args.cmd == "stable":
        p = argparse.ArgumentParser()
        p.add_argument("snaps", nargs="+")
        p.add_argument("--width", type=int, default=1, choices=(1, 2, 4))
        return cmd_stable(p.parse_args(rest))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
