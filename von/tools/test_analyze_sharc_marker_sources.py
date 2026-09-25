#!/usr/bin/env python3
"""Synthetic evidence gates for marker-slot source association."""

from analyze_sharc_marker_sources import analyze


def event(event_id, kind, **fields):
    return {"event_id": event_id, "kind": kind, "frame": 7, **fields}


def writes(slot, start):
    return [event(start + field, "marker_slot_write", slot=slot, field=field,
                  pc=0x8000, address=0x562430 + slot * 12 + field * 4,
                  data=field, mask=0xffffffff) for field in range(3)]


def consumes(slot, start):
    return [event(start + field, "marker_slot_consume", slot=slot, field=field,
                  pc=0x8100, address=0x562430 + slot * 12 + field * 4,
                  data=field, mask=0xffffffff, slot_words=[1, 2, 3],
                  r6=6, g0=0, g1=1, g2=2, g3=3, g4=4, g5=5)
            for field in range(3)]


def program(packet_id):
    return {"packet_event_id": packet_id,
            "push": {"event_id": packet_id + 10, "frame": 7, "depth": 3},
            "commit": {"oba": "0x009e410d"}}


def main():
    one = {"marker_slot_writes": writes(3, 1),
           "marker_slot_consumes": consumes(3, 4),
           "part_programs": [program(10)]}
    result = analyze(one)
    assert result["validation"] == {"nested_programs": 1, "candidates": 1,
                                    "unresolved": 0, "ambiguous": 0}
    candidate = result["candidates"][0]
    assert candidate["slot"] == 3 and candidate["required_parent_depth"] == 2
    assert candidate["consumer_pc"] == "0x00008100"

    many = dict(one)
    many["marker_slot_consumes"] = consumes(2, 4) + consumes(3, 7)
    result = analyze(many)
    assert result["validation"]["ambiguous"] == 1
    assert result["ambiguous"][0]["slots"] == [2, 3]

    # A slot rewrite starts a new epoch: an old consume cannot be carried into
    # the following sibling packet.
    stale = dict(one)
    stale["marker_slot_writes"] = writes(3, 1) + writes(3, 7)
    result = analyze(stale)
    assert result["validation"]["unresolved"] == 1
    print("PASS: marker consume epoch, uniqueness, and rewrite isolation")


if __name__ == "__main__":
    main()
