#!/usr/bin/env python3
"""Extract the emitter -> part-OBA mapping from a FIFO trace.

Some emitters carry the model part's OBA in the i960 `r6` register (first
observed in the `0x8d488` option/limb emitter): r6 is a value in
`0x0080_0000..0x00b0_0000`, not a pointer. Their packets therefore identify
the part directly, unlike the body emitters (`0x8d714`/`0x8e164`) whose r6 is a
source-record pointer.

This scans a `vonj_emitter` log (via decode_fifo_program), reports which PCs
tag OBAs and the distinct OBAs they emit, and optionally writes the mapping.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from decode_fifo_program import StreamDecoder, iter_words  # noqa: E402

OBA_LO = 0x00800000
OBA_HI = 0x00B00000


def is_oba(v: int) -> bool:
    return OBA_LO <= v <= OBA_HI


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("log", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    dec = StreamDecoder()
    by_pc = defaultdict(lambda: defaultdict(int))
    per_frame = defaultdict(list)  # frame -> [(pc, oba)]
    for (t, pc, data, r6, g0, g2) in iter_words(args.log):
        pkt = dec.feed(t, pc, data, r6, g0, g2)
        if pkt is None:
            continue
        r6 = pkt["r6"]
        if is_oba(r6):
            by_pc[pkt["pc"]][r6] += 1
            per_frame[round(pkt["time"] * 60)].append((pkt["pc"], r6))

    tagged = {pc: dict(c) for pc, c in by_pc.items() if c}
    print(f"OBA-tagged emitter PCs: {[hex(p) for p in sorted(tagged)]}")
    for pc in sorted(tagged):
        obas = tagged[pc]
        print(f"  0x{pc:x}: {len(obas)} distinct OBAs, {sum(obas.values())} packets")
        for oba, n in sorted(obas.items(), key=lambda kv: -kv[1])[:8]:
            print(f"    {oba:08x} {n}")

    # Show one frame's tag order (the per-frame part order for that emitter).
    if per_frame:
        k = sorted(per_frame)[len(per_frame) // 2]
        print(f"frame {k} tag order: " + " ".join(f"{o:08x}" for _, o in per_frame[k]))

    if args.out:
        payload = {
            "oba_tagged_pcs": {f"{pc:x}": {f"{o:08x}": n for o, n in c.items()}
                               for pc, c in tagged.items()},
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, indent=1) + "\n")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
