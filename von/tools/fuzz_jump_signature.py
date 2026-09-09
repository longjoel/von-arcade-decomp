#!/usr/bin/env python3
"""Jump + locomotion signature extractor for fuzz_battle_ram runs.

Reads a fuzz.log (VON_FUZZ_STATELOG workspace series + hold/release markers)
and prints, per input combo, the Y-channel (workspace word 71) arc stats for
jump combos and the X displacement for locomotion combos.

Usage: fuzz_jump_signature.py <run-dir> [<run-dir> ...]
"""
import re
import struct
import sys
from pathlib import Path

WS_BASE = 0x5039C0
Y_IDX = 71     # jump arc channel (float)
X_ADDRS = (0x503B5C, 0x503B68)


def f32(u):
    return struct.unpack(">f", struct.pack(">I", u))[0]


def series(run, idx):
    out = []
    for ln in (run / "fuzz.log").read_text(errors="replace").splitlines():
        m = re.match(r"fuzz: state f(\d+) @005039c0 ((?:[0-9a-f?]{8} ?)+)", ln)
        if not m:
            continue
        words = m.group(2).split()
        if idx < len(words) and "?" not in words[idx]:
            out.append((int(m.group(1)), int(words[idx], 16)))
    return out


def holds(run):
    hs, rs = {}, {}
    for ln in (run / "fuzz.log").read_text(errors="replace").splitlines():
        m = re.match(r"fuzz: frame (\d+) (hold|release) (\S+)", ln)
        if m:
            (hs if m.group(2) == "hold" else rs)[m.group(3)] = int(m.group(1))
    return hs, rs


def main():
    for d in sys.argv[1:]:
        run = Path(d)
        hs, rs = holds(run)
        y = dict(series(run, Y_IDX))
        print(f"== {d}")
        for combo, f0 in hs.items():
            f1 = rs.get(combo, f0)
            window = [(f, f32(v)) for f, v in y.items() if f0 - 10 <= f <= f1 + 160]
            if not window:
                print(f"  {combo}: no series")
                continue
            if "r_right" in combo or "r_up" in combo:
                air = [(f, v) for f, v in window if v > 0.5]
                if not air:
                    print(f"  {combo}: grounded (no liftoff)")
                    continue
                liftoff = air[0][0]
                apex = max(air, key=lambda p: p[1])
                land = next((f for f, v in window if f > apex[0] and v == 0.0), None)
                print(f"  {combo}: liftoff f{liftoff} (+{liftoff - f0}f) "
                      f"apex {apex[1]:.2f}u f{apex[0]} "
                      f"touchdown f{land} (air {land - liftoff if land else '?'}f)")
            else:
                xs = []
                for addr in X_ADDRS:
                    idx = (addr - WS_BASE) // 4
                    s = dict(series(run, idx))
                    pre = [f32(v) for f, v in s.items() if f0 - 60 <= f < f0]
                    hold = [f32(v) for f, v in s.items() if f0 <= f <= f1]
                    if pre and hold:
                        base = sorted(pre)[len(pre) // 2]
                        dev = max(hold, key=lambda v: abs(v - base)) - base
                        xs.append(dev)
                if xs:
                    print(f"  {combo}: peak dX={xs[0]:+.2f}u over {f1 - f0}f")
                else:
                    print(f"  {combo}: no baseline")


if __name__ == "__main__":
    main()
