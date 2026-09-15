#!/usr/bin/env python3
"""Prove an emitted SHARC motion packet comes from a ROM motion-table record.

The ROM record layout is ``x_angle,y_angle,z_angle,tx,ty,tz`` whereas the
i960 sends ``tx,ty,tz,z,y,x`` in its 0x2f/0x16/0x15/0x14 packet.  This tool
matches a retained VON_EMITTER capture against every raw Temjin record and can
pin a known table/frame/part prefix for regression use.
"""
from __future__ import annotations
import argparse, base64, json, re, struct
from pathlib import Path

EMIT = re.compile(r"vonj_emitter: time=([\d.]+) pc=(\w+) data=(\w+) .* g2=(\w+)")

def records(path: Path):
    for ci, clip in enumerate(json.loads(path.read_text())["clips"]):
        words = struct.unpack("<" + "H" * (clip["frames"] * clip["parts"] * 6),
                              base64.b64decode(clip["records_b64"]))
        for i in range(0, len(words), 6):
            yield ci, i // 6 // clip["parts"], (i // 6) % clip["parts"], tuple(words[i:i + 6])

def packets(log: Path):
    run = []
    for line in log.open(errors="replace"):
        m = EMIT.search(line)
        if not m or int(m.group(2), 16) < 0x8D000 or int(m.group(2), 16) >= 0x8F000:
            continue
        data = int(m.group(3), 16) & 0xffff
        if data == 5: run = [(data, m.group(4))]
        elif run: run.append((data, m.group(4)))
        if len(run) == 12:
            vals = [x[0] for x in run]
            if vals[1] == 0x2f and vals[5] == 0x16 and vals[7] == 0x15 and vals[9] == 0x14 and vals[11] == 0x3a:
                # Returned tuple is in ROM order, not FIFO order.
                yield run[0][1], (vals[10], vals[8], vals[6], vals[2], vals[3], vals[4])
            run = []

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--motion", type=Path, required=True)
    ap.add_argument("--log", type=Path, required=True)
    ap.add_argument("--expect", action="append", default=[],
                    help="table,frame,count or table,frame,start,count; repeatable")
    ap.add_argument("--expect-run", action="append", default=[],
                    help="table,part,length: require a contiguous 0..length-1 frame run")
    a = ap.parse_args()
    index = {}
    for ci, fr, part, record in records(a.motion): index.setdefault(record, []).append((ci, fr, part))
    got = []
    for g2, record in packets(a.log):
        hit = index.get(record, [])
        if hit: got.append((g2, hit))
    print(f"matched_packets={len(got)}")
    for g2, hit in got[:16]: print(f"  g2={g2} rom={hit[:4]}")
    for expectation in a.expect:
        fields = list(map(int, expectation.split(",")))
        if len(fields) == 3: ci, fr, count = fields; start = 0
        elif len(fields) == 4: ci, fr, start, count = fields
        else: raise SystemExit("--expect needs table,frame,count or table,frame,start,count")
        exact = [h for _, hits in got for h in hits if h[0] == ci and h[1] == fr]
        parts = {h[2] for h in exact}
        wanted = set(range(start, start + count))
        if not wanted.issubset(parts):
            raise SystemExit(f"missing expected table {ci} frame {fr} parts {start}..{start + count - 1}: got {sorted(parts)}")
        print(f"PASS: table={ci} frame={fr} contains parts {start}..{start + count - 1}")
    for expectation in a.expect_run:
        ci, part, length = map(int, expectation.split(","))
        series = []
        for _, hits in got:
            frame_hits = [h[1] for h in hits if h[0] == ci and h[2] == part]
            if frame_hits: series.append(frame_hits[0])
        # The trace includes repeated geometry submission passes. They do not
        # advance the ROM motion index, so compare the logical frame sequence.
        logical = []
        for frame in series:
            if not logical or frame != logical[-1]: logical.append(frame)
        target = list(range(length))
        if not any(logical[i:i + length] == target for i in range(len(logical) - length + 1)):
            raise SystemExit(f"missing table {ci} part {part} frame run {target}; got {logical[:64]}")
        print(f"PASS: table={ci} part={part} advances frames 0..{length - 1} in MAME order")

if __name__ == "__main__": main()
