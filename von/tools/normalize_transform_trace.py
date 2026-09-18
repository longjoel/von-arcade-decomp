#!/usr/bin/env python3
"""Normalize an ordered Lua i960/SHARC NDJSON trace into a compact fixture.

Raw captures remain local.  The output retains only fighter transform packets,
selector state, exact stack transitions, and commits joined by destination.
Joins use monotonically increasing event IDs and FIFO order, never timestamps
or spatial proximity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterable


EMITTERS = {
    0x8D488: "skeleton",
    0x8DD40: "option",
    0x8E164: "body",
}
PACKET_OPS = (0x05, 0x2F, None, None, None, 0x16, None,
              0x15, None, 0x14, None, 0x3A, None, 0x06)


class NormalizeError(ValueError):
    pass


def load_map(path: Path) -> dict[int, str]:
    return {int(key, 16): f"0x{int(value, 16):08x}"
            for key, value in json.loads(path.read_text()).items()}


def destination(word: int) -> str:
    return f"0x{0x01400000 + (word >> 2):08x}"


def resolve_identity(start: dict[str, Any], stream: str,
                     g2_map: dict[int, str], r6_map: dict[int, str]) -> tuple[str | None, int]:
    if stream == "body":
        return g2_map.get(start["g2"]), start["g2"]
    mapped = r6_map.get(start["r6"])
    if mapped:
        return mapped, start["g2"]
    # The skeleton/option emitter commonly carries the OBA directly in r6.
    if 0x00800000 <= start["r6"] <= 0x00BFFFFF:
        return f"0x{start['r6']:08x}", start["g2"]
    return None, start["g2"]


def normalize(lines: Iterable[bytes], source_sha256: str, *,
              g2_map: dict[int, str], r6_map: dict[int, str],
              frame_start: int = 0, frame_end: int = 2**31 - 1,
              oba_prefix: str | None = None, event_start: int = 0,
              event_end: int = 2**63 - 1) -> dict[str, Any]:
    selectors: list[dict[str, Any]] = []
    marker_writes: list[dict[str, Any]] = []
    marker_consumes: list[dict[str, Any]] = []
    packets: list[dict[str, Any]] = []
    output_packet_ids: set[int] = set()
    matched_packet_ids: set[int] = set()
    transitions: list[dict[str, Any]] = []
    part_programs: list[dict[str, Any]] = []
    pending: dict[str, deque[dict[str, Any]]] = defaultdict(deque)
    latest_push: dict[int, dict[str, Any]] = {}
    latest_service_source: dict[str, Any] | None = None
    open_programs: dict[int, dict[str, Any]] = {}
    packet_words: list[dict[str, Any]] | None = None
    queued_packet: dict[str, Any] | None = None
    raw_events = 0
    first_id: int | None = None
    last_id: int | None = None
    last_raw_id = 0
    unmatched_commits = 0

    for raw in lines:
        event = json.loads(raw)
        raw_events += 1
        event_id = event.get("event_id")
        if not isinstance(event_id, int) or event_id <= last_raw_id:
            raise NormalizeError("raw event IDs are not strictly increasing")
        last_raw_id = event_id
        frame = event.get("frame", -1)
        selected = (frame_start <= frame <= frame_end and
                    event_start <= event_id <= event_end)
        if selected:
            first_id = event_id if first_id is None else first_id
            last_id = event_id
        kind = event.get("kind")

        if kind == "motion_selector":
            if selected:
                selectors.append({key: event[key] for key in (
                    "event_id", "frame", "object", "selector_object",
                    "skeleton_header", "body_header", "selector", "state", "cursor")})
            continue

        if kind == "marker_slot_write":
            if selected:
                marker_writes.append({key: event[key] for key in (
                    "event_id", "frame", "pc", "address", "slot", "field",
                    "data", "mask")})
            continue

        if kind == "marker_slot_consume":
            if selected:
                marker_consumes.append({key: event[key] for key in (
                    "event_id", "frame", "pc", "address", "slot", "field",
                    "data", "mask", "slot_words", "r6", "g0", "g1", "g2",
                    "g3", "g4", "g5")})
            continue

        if kind == "i960_fifo":
            if packet_words is None:
                if event.get("data") == 5 and event.get("pc") in EMITTERS:
                    packet_words = [event]
                continue
            packet_words.append(event)
            index = len(packet_words) - 1
            expected = PACKET_OPS[index] if index < len(PACKET_OPS) else "overflow"
            if expected is not None and event.get("data") != expected:
                packet_words = ([event] if event.get("data") == 5 and
                                 event.get("pc") in EMITTERS else None)
                queued_packet = None
                continue
            # The SHARC commit is generated after the 0x3a copy-target word
            # (index 12), before the emitter's trailing 0x06.  Queue the
            # packet at that boundary so destination joins cannot drift to a
            # later frame; retain the object and append the terminator when
            # it arrives for fixture completeness.
            if index == 12:
                start = packet_words[0]
                stream = EMITTERS[start["pc"]]
                oba, record_address = resolve_identity(start, stream, g2_map, r6_map)
                words = [item["data"] for item in packet_words]
                dest = destination(words[12])
                packet = {
                    "event_id": start["event_id"],
                    "end_event_id": packet_words[-1]["event_id"],
                    "frame": start["frame"],
                    "writer_pc": f"0x{start['pc']:08x}",
                    "source_stream": stream,
                    "record_address": f"0x{record_address:08x}",
                    "oba": oba,
                    "destination": dest,
                    "words": words,
                }
                queued_packet = packet
                pending[dest].append(packet)
                if (frame_start <= start["frame"] <= frame_end and
                        event_start <= start["event_id"] <= event_end and
                        (oba_prefix is None or
                         (oba is not None and oba.startswith(oba_prefix)))):
                    packets.append(packet)
                    output_packet_ids.add(packet["event_id"])
                continue
            if index == 13:
                if queued_packet is not None:
                    queued_packet["words"].append(event["data"])
                    queued_packet["end_event_id"] = event["event_id"]
                packet_words = None
                queued_packet = None
            continue

        if kind == "sharc_service_source":
            latest_service_source = event
        elif kind == "push":
            push = {
                "event_id": event_id, "frame": frame, "kind": "push",
                "depth": event["depth"], "pointer": event["pointer"],
                "base_words": event["base_words"],
            }
            latest_push[event["depth"]] = push
        elif kind == "commit":
            queue = pending[event["destination"]]
            packet = queue.popleft() if queue else None
            if packet:
                matched_packet_ids.add(packet["event_id"])
            packet_selected = (packet is not None and
                               packet["event_id"] in output_packet_ids)
            if packet_selected:
                commit = {
                    "event_id": event_id, "frame": frame, "kind": "commit",
                    "depth": event["depth"], "destination": event["destination"],
                    "matrix_words": event["matrix_words"],
                    "packet_event_id": packet and packet["event_id"],
                    "oba": packet and packet["oba"],
                    "source_stream": packet and packet["source_stream"],
                    "record_address": packet and packet["record_address"],
                }
                if "stack_words" in event:
                    commit["stack_words"] = event["stack_words"]
                if (latest_service_source is not None and
                        latest_service_source.get("frame") == frame and
                        latest_service_source.get("event_id", 0) < event_id):
                    commit["service_source_words"] = latest_service_source.get(
                        "matrix_words", [])
                    commit["service_source_event_id"] = latest_service_source.get(
                        "event_id")
                push = latest_push.get(event["depth"])
                if push is None:
                    unmatched_commits += 1
                else:
                    open_programs[event["depth"]] = {
                        "packet_event_id": packet["event_id"],
                        "push": push, "commit": commit,
                    }
        elif kind == "pop":
            pop = {
                "event_id": event_id, "frame": frame, "kind": "pop",
                "depth": event["depth"], "depth_after": event["depth_after"],
                "pointer": event["pointer"],
                "restored_words": event["restored_words"],
            }
            program = open_programs.pop(event["depth"], None)
            if program is not None:
                program["pop"] = pop
                part_programs.append(program)
                transitions.extend((program["push"], program["commit"], pop))

    unresolved = sum(packet["oba"] is None for packet in packets)
    unmatched = sum(packet["event_id"] not in matched_packet_ids for packet in packets)
    return {
        "schema_version": 1,
        "source": {
            "sha256": source_sha256,
            "raw_event_count": raw_events,
            "selected_event_range": [first_id, last_id],
            "frame_range": [frame_start, frame_end],
        },
        "motion_selectors": selectors,
        "marker_slot_writes": marker_writes,
        "marker_slot_consumes": marker_consumes,
        "packets": packets,
        "stack_transitions": transitions,
        "part_programs": part_programs,
        "validation": {
            "unresolved_packet_obas": unresolved,
            "unmatched_packet_commits": unmatched,
            "unmatched_commits": unmatched_commits,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--frame-start", type=int, default=0)
    parser.add_argument("--frame-end", type=int, default=2**31 - 1)
    parser.add_argument("--event-start", type=int, default=0)
    parser.add_argument("--event-end", type=int, default=2**63 - 1)
    parser.add_argument("--oba-prefix",
                        help="retain only packets whose resolved OBA starts with this prefix")
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--g2-oba", type=Path, default=root / "i960/emitter-g2-oba.json")
    parser.add_argument("--r6-oba", type=Path, default=root / "i960/emitter-r6-oba.json")
    args = parser.parse_args()

    digest = hashlib.sha256()
    with args.trace.open("rb") as source:
        for line in source:
            digest.update(line)
    with args.trace.open("rb") as source:
        document = normalize(source, digest.hexdigest(),
                             g2_map=load_map(args.g2_oba),
                             r6_map=load_map(args.r6_oba),
                             frame_start=args.frame_start,
                             frame_end=args.frame_end,
                             oba_prefix=args.oba_prefix,
                             event_start=args.event_start,
                             event_end=args.event_end)
    args.output.write_text(json.dumps(document, sort_keys=True,
                                      separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
