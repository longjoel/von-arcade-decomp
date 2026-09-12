#!/usr/bin/env python3
"""Decode the i960 -> SHARC geometry FIFO command stream into packets.

The transform emitters write a fixed opcode program per body part to the FIFO
at 0x884000. The 0049 instrumentation logs each write as:

    vonj_emitter: time=<t> pc=<pc> data=<word> r6=<part> g0=<src> g2=<record>

Each part packet is (decimal opcodes, as written):

    transform : 5 47 <off0 off1 off2> 22 <rotA> 21 <rotB> 20 <rotC> 58 <read> [6]
    sequencer : 5 18 <a b c> 21 <d> 19 <e f g> [6]

`5`=0x05 advance, `47`=0x2f packed fixed-point interpolation, `22/21/20`=
0x16/0x15/0x14 Z/Y/X rotation, `58`=0x3a seeded table output; the trailing `6`=
0x06 counter decrement. See von/i960/sharc-command-annotations.md and
recovered_geometry_batch_packet_8d400.c.

`g2` is the per-part record pointer (stride 12 into the 0x0050xxxx working
set); `r6` is the emitter's source pointer (stride 12 into 0x020xxxxx), or the
small part index for the option emitter at 0x8de14.

This tool streams a (large) MAME error.log, groups the writes into packets, and
reports per-emitter statistics. `--csv` dumps every packet for downstream
analysis.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

LINE = re.compile(
    r"(?:vonj_emitter|vonj_fifo)[^:]*: time=([0-9.]+) pc=([0-9a-fA-F]+) "
    r"data=([0-9a-fA-F]+) r6=([0-9a-fA-F]+) g0=([0-9a-fA-F]+) g2=([0-9a-fA-F]+)")

TRANSFORM = [
    ("op", 5), ("op", 47), ("arg", "off0"), ("arg", "off1"), ("arg", "off2"),
    ("op", 22), ("arg", "rotA"), ("op", 21), ("arg", "rotB"),
    ("op", 20), ("arg", "rotC"), ("op", 58), ("arg", "readback"), ("op?", 6),
]
SEQUENCER = [
    ("op", 5), ("op", 18), ("arg", "a"), ("arg", "b"), ("arg", "c"),
    ("op", 21), ("arg", "d"), ("op", 19), ("arg", "e"), ("arg", "f"),
    ("arg", "g"), ("op?", 6),
]
PROGRAMS_BY_SECOND = {47: ("transform", TRANSFORM), 18: ("sequencer", SEQUENCER)}

CSV_FIELDS = ["time", "pc", "g2", "r6", "g0", "off0", "off1", "off2",
              "rotA", "rotB", "rotC", "readback", "program"]


def signed16(w: int) -> int:
    w &= 0xFFFF
    return w - 0x10000 if w & 0x8000 else w


class StreamDecoder:
    """Incremental packet decoder driven by a token program."""

    def __init__(self) -> None:
        self.reset()
        self.packets = 0
        self.resync = 0

    def reset(self) -> None:
        self.prog_name: str | None = None
        self.tokens: list = []
        self.pos = 0
        self.args: dict[str, int] = {}
        self.start: dict | None = None
        self.last: dict | None = None

    def feed(self, t: float, pc: int, data: int, r6: int, g0: int, g2: int):
        while True:
            if self.prog_name is None:
                if data == 5:
                    self.start = {"time": t, "pc": pc, "r6": r6, "g0": g0, "g2": g2}
                    self.last = self.start
                    self.pos = 0
                    self.args = {}
                    self.prog_name = "pending"
                    self.tokens = []
                return None
            if self.prog_name == "pending":
                entry = PROGRAMS_BY_SECOND.get(data)
                if entry is None:
                    self.reset()
                    return None
                self.prog_name, self.tokens = entry
                self.pos = 1  # leading opcode 5 was consumed as the start
            self.last = {"time": t, "pc": pc, "r6": r6, "g0": g0, "g2": g2}
            tok = self.tokens[self.pos]
            if tok[0] == "op":
                if data != tok[1]:
                    self.resync += 1
                    self.reset()
                    if data == 5:
                        self.feed(t, pc, data, r6, g0, g2)
                    return None
                self.pos += 1
            elif tok[0] == "op?":
                if data == tok[1]:
                    self.pos += 1
                else:
                    packet = self.finish()
                    if data == 5:
                        self.feed(t, pc, data, r6, g0, g2)
                    return packet
            else:
                self.args[tok[1]] = data
                self.pos += 1
            if self.pos == len(self.tokens):
                return self.finish()
            return None

    def finish(self):
        p = dict(self.start or {})
        p.update(self.args)
        p["program"] = self.prog_name
        p["end_time"] = self.last["time"] if self.last else p.get("time")
        for k in ("off0", "off1", "off2", "rotA", "rotB", "rotC"):
            p.setdefault(k, 0)
        self.packets += 1
        self.reset()
        return p

    def flush(self):
        """Finalize a packet left at its optional trailing token at EOF."""
        if (self.prog_name in ("transform", "sequencer")
                and self.pos < len(self.tokens)
                and self.tokens[self.pos][0] == "op?"):
            return self.finish()
        return None


def iter_words(path: Path):
    with path.open(errors="ignore") as fh:
        for line in fh:
            if "vonj_emitter" not in line and "vonj_fifo" not in line:
                continue
            m = LINE.search(line)
            if m:
                yield (float(m.group(1)), int(m.group(2), 16), int(m.group(3), 16),
                       int(m.group(4), 16), int(m.group(5), 16), int(m.group(6), 16))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("log", type=Path)
    ap.add_argument("--csv", type=Path, help="write every packet to a CSV file")
    ap.add_argument("--max", type=int, default=0, help="stop after N log words (debug)")
    args = ap.parse_args()

    dec = StreamDecoder()
    n = 0
    by_pc = defaultdict(lambda: {"count": 0, "g2": set(), "r6": set(),
                                 "prog": set(), "t0": None, "t1": None})
    csvf = args.csv.open("w", newline="") if args.csv else None
    writer = csv.DictWriter(csvf, fieldnames=CSV_FIELDS, extrasaction="ignore") if csvf else None
    if writer:
        writer.writeheader()

    def handle(pkt):
        st = by_pc[pkt["pc"]]
        st["count"] += 1
        st["g2"].add(pkt["g2"])
        st["r6"].add(pkt["r6"])
        st["prog"].add(pkt["program"])
        st["t0"] = pkt["time"] if st["t0"] is None else st["t0"]
        st["t1"] = pkt["end_time"]
        if writer:
            writer.writerow(pkt)

    for (t, pc, data, r6, g0, g2) in iter_words(args.log):
        n += 1
        if args.max and n > args.max:
            break
        pkt = dec.feed(t, pc, data, r6, g0, g2)
        if pkt is not None:
            handle(pkt)
    tail = dec.flush()
    if tail is not None:
        handle(tail)

    if csvf:
        csvf.close()

    print(f"words={n} packets={dec.packets} resync={dec.resync}")
    print(f"{'startpc':>9} {'packets':>9} {'g2':>7} {'r6':>7} {'programs':>12} {'t0':>8} {'t1':>8}")
    for pc in sorted(by_pc):
        st = by_pc[pc]
        print(f"{pc:>9x} {st['count']:>9} {len(st['g2']):>7} {len(st['r6']):>7} "
              f"{','.join(sorted(st['prog'])):>12} {st['t0']:>8.2f} {st['t1']:>8.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
