#!/usr/bin/env python3
"""Join fuzz RAM state series against annotation pose segments.

Reads `fuzz: state` rows from a fuzz_battle_ram log (VON_FUZZ_STATELOG) and
the pose_segments of an annotate_bout v2 annotation, matched by timestamp
(fuzz frame / 60 = trace machine seconds). For each mech segment the modal
RAM row is the segment signature; word slots that hold steady inside every
segment but differ across segments are the state-byte candidates -- the RAM
half of the per-unit state-ID tables.

Usage: join_state_segments.py --fuzz-log p1-fuzz.log --annotation annot.json
    --statelog-base 0x5039c0 --output state-table.json
"""
from __future__ import annotations
import argparse
import json
import re
from collections import Counter
from pathlib import Path

STATE_RE = re.compile(r"fuzz: state f(\d+)(?: @([0-9a-f]+))? "
                      r"((?:[0-9a-f?]{8} ?)+)")
HOLD_RE = re.compile(r"fuzz: frame (\d+) (hold|release) (\S+)")
SNAP_RE = re.compile(r"fuzz: frame (\d+) snapshot (\S+)")
MARK_RE = re.compile(r"mark f(\d+) #(\d+)")


def load_states(log: Path, default_base: int = 0):
    """State rows as (frame, base, vector); untagged rows take default_base."""
    rows = []
    holds = []
    marks = []
    for line in log.read_text(errors="replace").splitlines():
        m = STATE_RE.search(line)
        if m:
            base = int(m.group(2), 16) if m.group(2) else default_base
            rows.append((int(m.group(1)), base, m.group(3).split()))
            continue
        m = MARK_RE.search(line)
        if m:
            marks.append({"frame": int(m.group(1)),
                          "mark": int(m.group(2)),
                          "t": int(m.group(1)) / 60.0})
            continue
        m = HOLD_RE.search(line)
        if m:
            holds.append({"frame": int(m.group(1)), "kind": m.group(2),
                          "input": m.group(3), "t": int(m.group(1)) / 60.0})
    return rows, holds, marks


def load_snapshots(log: Path, snap_dir: Path):
    """Snapshot files as (frame, region_base, vector) rows.

    Snapshots are sparse (pre/post/settled per hold) but cover all four
    fuzz regions; frames come from the log's snapshot lines.
    """
    tag_frame = {}
    for line in log.read_text(errors="replace").splitlines():
        m = SNAP_RE.search(line)
        if m:
            tag_frame[m.group(2)] = int(m.group(1))
    rows = []
    for path in sorted(snap_dir.glob("snap-*.txt")):
        parts = path.stem.split("-")
        base = int(parts[-1], 16)
        tag = "-".join(parts[1:-1])
        if tag not in tag_frame:
            continue
        vec = {}
        for line in path.read_text().splitlines():
            addr, val = line.split()
            vec[int(addr, 16)] = val
        addrs = sorted(vec)
        rows.append((tag_frame[tag], base,
                     [vec[a] for a in range(base, base + len(addrs) * 4, 4)
                      if a in vec]))
    return rows


def modal(rows):
    keyed = Counter(tuple(r) for _, r in rows)
    vec, _ = keyed.most_common(1)[0]
    return list(vec)


def analyze(rows, seglist, width, max_distinct: int = 8):
    """Segment signatures + state-byte candidates for one row series."""
    if not rows:
        return [], []
    period = (rows[1][0] - rows[0][0]) / 60.0 if len(rows) > 1 else 0.1
    eps = period / 2 + 1e-9
    seg_out = []
    for s in seglist:
        inside = [(f, r) for f, r in rows
                  if s["t0"] - eps <= f / 60.0 <= s["t1"] + eps]
        if not inside:
            seg_out.append({**s, "signature": None, "coverage": 0})
            continue
        sig = modal(inside)
        agree = [sum(1 for _, r in inside if r[w] == sig[w]) / len(inside)
                 for w in range(width)]
        seg_out.append({**s, "signature": sig, "coverage": len(inside),
                        "word_agree": [round(v, 3) for v in agree]})
    covered = [s for s in seg_out if s["signature"] is not None]
    # Churn guard: position floats take a distinct value per row; state
    # bytes take few. Steady-within + few-distinct + differs-across.
    distinct = [len({s["signature"][w] for s in covered})
                for w in range(width)] if covered else []
    cands = []
    for w in range(width):
        if not covered or distinct[w] > max_distinct:
            continue
        # Veto churn only where a majority can exist: sparse snapshot pairs
        # straddling a transition tie at 0.5 and must not veto.
        if any(s["word_agree"][w] < 0.9 for s in covered
               if s["coverage"] >= 3):
            continue
        vals = sorted({s["signature"][w] for s in covered})
        if len(vals) > 1:
            cands.append({"word": w, "values": vals,
                          "per_segment": [s["signature"][w] for s in covered]})
    return seg_out, cands


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fuzz-log", type=Path, required=True)
    p.add_argument("--annotation", type=Path, required=True)
    p.add_argument("--statelog-base", type=lambda v: int(v, 0), required=True)
    p.add_argument("--snap-dir", type=Path, required=False, default=None)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    rows, holds, marks = load_states(a.fuzz_log, a.statelog_base)
    if not rows:
        raise SystemExit("no fuzz: state rows in log (set VON_FUZZ_STATELOG)")
    annot = json.loads(a.annotation.read_text())
    segs = annot["summary"]["pose_segments"]

    out = {"statelog_base": f"{a.statelog_base:#x}", "holds": holds,
           "marks": marks, "statelog": {}, "mechs": {}}
    by_base: dict[int, list] = {}
    for frame, base, vec in rows:
        by_base.setdefault(base, []).append((frame, vec))
    for base in sorted(by_base):
        brows = sorted(by_base[base])
        width = len(brows[0][1])
        out["statelog"][f"{base:#x}"] = {"width_words": width, "rows": len(brows)}
    # Legacy single-series shape for the default base (keeps "mechs").
    main_rows = sorted(by_base.get(a.statelog_base, []))
    if main_rows:
        width = len(main_rows[0][1])
        for tag, seglist in segs.items():
            seg_out, cands = analyze(main_rows, seglist, width)
            for c in cands:
                c["addr"] = f"{a.statelog_base + 4 * c['word']:#x}"
            out["mechs"][tag] = {"segments": seg_out, "state_bytes": cands}
    if a.snap_dir is not None:
        out["snap_regions"] = {}
        by_region: dict[int, list] = {}
        for frame, base, vec in load_snapshots(a.fuzz_log, a.snap_dir):
            by_region.setdefault(base, []).append((frame, vec))
        for base in sorted(by_region):
            rrows = sorted(by_region[base])
            w = len(rrows[0][1])
            reg_out = {}
            for tag, seglist in segs.items():
                seg_out, cands = analyze(rrows, seglist, w)
                for c in cands:
                    c["addr"] = f"{base + 4 * c['word']:#x}"
                reg_out[tag] = {"segments": len(seg_out),
                                "covered": sum(1 for s in seg_out
                                               if s["coverage"]),
                                "state_bytes": cands}
            out["snap_regions"][f"{base:#x}"] = reg_out
    a.output.write_text(json.dumps(out, indent=1) + "\n")
    nb = sum(len(m["state_bytes"]) for m in out["mechs"].values())
    ns = sum(len(r[tag]["state_bytes"]) for r in out.get("snap_regions", {}).values() for tag in r)
    print(f"wrote {a.output}: {nb} statelog + {ns} snapshot candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
