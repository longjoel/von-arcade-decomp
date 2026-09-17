#!/usr/bin/env python3
"""Tests for deterministic ordered transform-trace normalization."""

import json
import hashlib
from pathlib import Path

from normalize_transform_trace import normalize


I = [0x3F800000, 0, 0, 0, 0x3F800000, 0, 0, 0, 0x3F800000, 0, 0, 0]
M = I[:9] + [0x40000000, 0, 0]


def main():
    events = []

    def add(kind, frame=10, **fields):
        events.append({"event_id": len(events) + 1, "kind": kind,
                       "frame": frame, **fields})

    packet = [5, 0x2F, 1, 2, 3, 0x16, 4, 0x15, 5, 0x14, 6, 0x3A, 0x100, 6]
    for index, word in enumerate(packet):
        add("i960_fifo", pc=0x8E164 if index == 0 else 0x8E170 + index * 4,
            data=word, mask=0xFFFFFFFF, r6=0x1234, g0=0,
            g2=0x00504730, g4=word)
    add("push", depth=1, pointer=0x3020C, base_words=I)
    add("commit", depth=1, destination="0x01400040", matrix_words=M)
    add("pop", depth=1, depth_after=0, pointer=0x30200, restored_words=I)
    add("motion_selector", object=1, selector_object=2,
        skeleton_header=3, body_header=4, selector=5, state=6, cursor=7)

    lines = [(json.dumps(event) + "\n").encode() for event in events]
    result = normalize(lines, "0" * 64,
                       g2_map={0x00504730: "0x009e3300"}, r6_map={})
    assert result["packets"][0]["words"] == packet
    assert result["packets"][0]["oba"] == "0x009e3300"
    commit = result["stack_transitions"][1]
    assert commit["packet_event_id"] == 1
    assert commit["matrix_words"] == M
    assert result["stack_transitions"][2]["depth"] == 1
    assert result["validation"] == {
        "unresolved_packet_obas": 0, "unmatched_packet_commits": 0,
        "unmatched_commits": 0}

    bad = [dict(event) for event in events]
    bad[1]["event_id"] = 1
    try:
        normalize([(json.dumps(event) + "\n").encode() for event in bad],
                  "0" * 64, g2_map={}, r6_map={})
    except ValueError as error:
        assert "strictly increasing" in str(error)
    else:
        raise AssertionError("non-monotonic IDs must fail")

    von_root = Path(__file__).resolve().parents[1]
    fixture_dir = von_root / "tests/fixtures/render-contract"
    fixture_path = fixture_dir / "temjin-idle-1925.json"
    manifest = json.loads((fixture_dir / "temjin-idle-1925.manifest.json").read_text())
    fixture_bytes = fixture_path.read_bytes()
    assert hashlib.sha256(fixture_bytes).hexdigest() == manifest["fixture"]["sha256"]
    assert (hashlib.sha256((von_root / "tools/gameplay_progress.lua").read_bytes()).hexdigest()
            == manifest["runtime"]["instrumentation_sha256"])
    assert (hashlib.sha256((von_root / "tools/normalize_transform_trace.py").read_bytes()).hexdigest()
            == manifest["normalization"]["tool_sha256"])
    fixture = json.loads(fixture_bytes)
    assert len(fixture["part_programs"]) == 18
    assert len(fixture["packets"]) == 18
    assert len(fixture["marker_slot_writes"]) == 12
    assert {write["slot"] for write in fixture["marker_slot_writes"]} == {
        0, 1, 2, 3}
    assert fixture["validation"] == {
        "unresolved_packet_obas": 0, "unmatched_packet_commits": 0,
        "unmatched_commits": 0}
    assert {packet["source_stream"] for packet in fixture["packets"]} == {
        "body", "skeleton"}
    for program in fixture["part_programs"]:
        assert (program["push"]["event_id"] < program["commit"]["event_id"] <
                program["pop"]["event_id"])
        assert program["push"]["base_words"] == program["pop"]["restored_words"]
    print("PASS: packet validation, ordered destination join, selectors, raw hash")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
