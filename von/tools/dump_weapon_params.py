#!/usr/bin/env python3
"""Dump the per-fighter weapon parameter table from the i960 program image.

Each fighter profile (pointer table at 0x19360, names at 0x19390) holds a weapon
parameter block starting at ``+0x5c0``.  The cooldown columns at ``+0x5d0`` /
``+0x5d4`` / ``+0x5d8`` / ``+0x5dc`` match the runtime resource timers we
measured in a live bout (Temjin ``10/300/180/300`` = right/left/center/reload),
which pins the block.  The reader families are the cooldown service at
``0x4a430`` (and ``0x646c0``) plus per-field readers (``0x2ff40``/``0x3138c``
read ``+0x660``; ``0x31e18`` reads ``+0x644``; ``0x333f0``/``0x33524`` read
``+0x640``/``+0x648``).

Field semantics beyond the cooldowns are not yet named; the offsets are emitted
so the readers can be aligned.  Writes JSON to ``--out`` (default stdout).

Action timing (recovered from the action-duration writer at i960 ``0x30660``): a
mech object holds its action in ``object+0x174`` (1/2/3 = the three weapons, 16 =
a special) and its phase in ``object+0x176`` (0/1/2).  Each frame it stores the
selected profile duration to ``object+0x18e`` and counts ``object+0x17e`` up to
it before advancing the phase.  The phase -> offset map is:

    action 1 (RIGHT):  0x176=0 -> +0x5ec, =1 -> +0x5f0, =2 -> +0x5e8
    action 2 (LEFT):   0x176=0 -> +0x5f8, =1 -> +0x5fc, =2 -> +0x5f4
    action 3 (CENTER): 0x176=0 -> +0x604, =1 -> +0x608, =2 -> +0x600

The weapon cooldown service at ``0x4a430`` charges a per-weapon object timer by
``+0x5d0/+0x5d4/+0x5d8`` per tick, capped at ``+0x5dc/+0x5e0/+0x5e4``; the
right/left/center column labels come from the live-pinned runtime timers.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from dump_motion_tables import load_maincpu, _ROM_DIR  # noqa: E402

PROFILE_TABLE = 0x19360
NAME_TABLE = 0x19390
NAME_STRIDE = 0x10
BLOCK_START = 0x5c0
BLOCK_END = 0x680
# 16-bit slots that carry a distinct value (high half of each pair is unused).
SLOTS = list(range(BLOCK_START, BLOCK_END, 4)) + \
        [0x610, 0x614, 0x644, 0x648, 0x64c, 0x650, 0x654, 0x658, 0x65c,
         0x660, 0x664, 0x668, 0x66c]
COOLDOWN_SLOTS = {0x5d0: "right", 0x5d4: "left", 0x5d8: "center", 0x5dc: "reload"}
# (action id, weapon label, phase offsets, cooldown increment/max offsets).
ACTION_GROUPS = (
    (1, "right",  (0x5ec, 0x5f0, 0x5e8), 0x5d0, 0x5dc),
    (2, "left",   (0x5f8, 0x5fc, 0x5f4), 0x5d4, 0x5e0),
    (3, "center", (0x604, 0x608, 0x600), 0x5d8, 0x5e4),
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rom-dir", type=Path, default=_ROM_DIR)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    mc = load_maincpu(args.rom_dir)
    ptrs = list(struct.unpack_from("<10I", mc, PROFILE_TABLE))
    fighters = []
    for i, base in enumerate(ptrs):
        raw = mc[NAME_TABLE + i * NAME_STRIDE:NAME_TABLE + (i + 1) * NAME_STRIDE]
        name = raw.split(b"\0", 1)[0].decode("ascii", "replace")
        fields = {}
        for off in sorted(set(SLOTS)):
            fields[f"0x{off:x}"] = struct.unpack_from("<H", mc, base + off)[0]
        # +0x614..0x63b: 10 per-fighter floats (movement/physics; slot 6 is the
        # recovered gravity 0.030, slot 0 is written to object+0x150).
        floats = [round(v, 5) for v in struct.unpack_from("<10f", mc, base + 0x614)]
        # +0x5e8..0x608: three 3-value per-action duration groups, written to
        # object+0x18e (state 0/1/2 selected by object+0x176).  Group A is the
        # 0x5ec/0x5f0/0x5e8 trio, B the 0x5f8/0x5fc/0x5f4 trio, C 0x604/0x608/0x600.
        dur = {f"0x{o:x}": fields[f"0x{o:x}"]
               for o in range(0x5e8, 0x60c, 4)}
        actions = {}
        for action_id, label, phases, inc_off, max_off in ACTION_GROUPS:
            actions[label] = {
                "action": action_id,
                "phases": [fields[f"0x{o:x}"] for o in phases],
                "cooldown_inc": fields[f"0x{inc_off:x}"],
                "cooldown_max": fields[f"0x{max_off:x}"],
            }
        fighters.append({"fighter": name, "profile": f"0x{base:06x}",
                         "fields": fields, "movement_floats": floats,
                         "action_durations": dur, "actions": actions,
                         "cooldowns": {k: fields.get(f"0x{o:x}")
                                       for o, k in COOLDOWN_SLOTS.items()}})

    payload = {"source": "vonj-maincpu profile block +0x5c0..0x680",
               "fighters": fighters}
    encoded = json.dumps(payload, indent=1)
    if args.out:
        args.out.write_text(encoded + "\n")
        print(f"wrote {args.out}")
    else:
        print(encoded)

    print(f"{'fighter':11s} {'right':>6s} {'left':>6s} {'center':>7s} {'reload':>7s}")
    for f in fighters:
        c = f["cooldowns"]
        print(f"{f['fighter']:11s} {c['right']:6d} {c['left']:6d} "
              f"{c['center']:7d} {c['reload']:7d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
