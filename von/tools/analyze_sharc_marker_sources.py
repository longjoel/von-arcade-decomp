#!/usr/bin/env python3
"""Associate nested SHARC pushes with explicitly consumed marker-table slots.

This is deliberately a candidate extractor, not a parent fitter. A candidate
is emitted only when a compact trace records exactly one marker slot consumed
after the most recent marker-table rewrite and before the i960 packet that led
to the nested SHARC push. The result names a slot and producer/consumer PCs;
it does *not* invent a parent OBA.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def analyze(document: dict) -> dict:
    writes = sorted(document.get("marker_slot_writes", []), key=lambda e: e["event_id"])
    consumes = sorted(document.get("marker_slot_consumes", []), key=lambda e: e["event_id"])
    programs = sorted(document.get("part_programs", []),
                      key=lambda program: program["push"]["event_id"])
    candidates, unresolved, ambiguous = [], [], []

    for index, program in enumerate(programs):
        push = program["push"]
        if push["depth"] <= 1:
            continue
        packet_id = program.get("packet_event_id")
        if not isinstance(packet_id, int):
            unresolved.append({"program": index, "reason": "no_packet_id"})
            continue
        frame = push["frame"]
        prior_writes = [e for e in writes if e["frame"] == frame and e["event_id"] < packet_id]
        # A rewrite is an epoch boundary. This avoids attributing a slot read
        # from a prior sibling/traversal to the current push.
        epoch = prior_writes[-1]["event_id"] if prior_writes else 0
        prior_consumes = [e for e in consumes if e["frame"] == frame and
                          epoch < e["event_id"] < packet_id]
        slots = sorted({e["slot"] for e in prior_consumes})
        base = {
            "program": index,
            "oba": program["commit"].get("oba"),
            "packet_event_id": packet_id,
            "push_event_id": push["event_id"],
            "depth": push["depth"],
            "required_parent_depth": push["depth"] - 1,
            "marker_epoch_event_id": epoch or None,
        }
        if len(slots) != 1:
            base["slots"] = slots
            (unresolved if not slots else ambiguous).append(base)
            continue
        slot = slots[0]
        slot_consumes = [e for e in prior_consumes if e["slot"] == slot]
        # The last field read carries the complete slot snapshot logged by the
        # tap. It is an audit record for later mapping to a named root.
        consume = slot_consumes[-1]
        base.update({
            "slot": slot,
            "consume_event_ids": [e["event_id"] for e in slot_consumes],
            "consumer_pc": f"0x{consume['pc']:08x}",
            "slot_words": consume["slot_words"],
            "consumer_registers": {name: consume[name] for name in
                                   ("r6", "g0", "g1", "g2", "g3", "g4", "g5")},
        })
        candidates.append(base)

    return {
        "schema_version": 1,
        "policy": "marker-consume-epoch-v1",
        "candidates": candidates,
        "unresolved": unresolved,
        "ambiguous": ambiguous,
        "validation": {
            "nested_programs": len(candidates) + len(unresolved) + len(ambiguous),
            "candidates": len(candidates), "unresolved": len(unresolved),
            "ambiguous": len(ambiguous),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true",
                        help="fail unless every nested program has one slot candidate")
    args = parser.parse_args()
    result = analyze(json.loads(args.fixture.read_text()))
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["validation"], sort_keys=True, separators=(",", ":")))
    if args.check and (result["unresolved"] or result["ambiguous"]):
        raise SystemExit("marker sources are not uniquely consumed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
