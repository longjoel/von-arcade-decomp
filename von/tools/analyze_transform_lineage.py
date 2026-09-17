#!/usr/bin/env python3
"""Recover exact fighter-part lineage from ordered SHARC stack events.

The input is a JSON object with an ``events`` array. Matrices are twelve raw
u32 words, so equality is bit-exact. Event order, explicit stack nesting, and
commit destinations are authoritative; this tool never scores spatial
distance or matrix error. Ambiguous bases and uncommitted submissions fail.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class LineageError(ValueError):
    pass


def matrix(event: dict[str, Any], field: str = "matrix_words") -> tuple[int, ...]:
    words = event.get(field)
    if not isinstance(words, list) or len(words) != 12:
        raise LineageError(f"event {event.get('event_id')}: {field} must contain 12 u32 words")
    if any(not isinstance(word, int) or word < 0 or word > 0xFFFFFFFF for word in words):
        raise LineageError(f"event {event.get('event_id')}: {field} contains a non-u32 word")
    return tuple(words)


@dataclass(frozen=True)
class Source:
    key: str
    kind: str
    matrix: tuple[int, ...]
    event_id: int


@dataclass(frozen=True)
class Frame:
    base: Source
    depth: int


def analyze(document: dict[str, Any]) -> dict[str, Any]:
    events = document.get("events")
    if not isinstance(events, list):
        raise LineageError("events must be an array")
    sources: dict[str, Source] = {}
    by_matrix: dict[tuple[int, ...], list[Source]] = {}
    commits_by_destination: dict[str, list[dict[str, Any]]] = {}
    stack: list[Frame] = []
    current: Source | None = None
    parts: list[dict[str, Any]] = []
    submissions: list[dict[str, Any]] = []
    last_id = -1

    def register(source: Source) -> None:
        if source.key in sources:
            raise LineageError(f"event {source.event_id}: duplicate source {source.key}")
        sources[source.key] = source
        by_matrix.setdefault(source.matrix, []).append(source)

    for event in events:
        event_id = event.get("event_id")
        kind = event.get("kind")
        if not isinstance(event_id, int) or event_id <= last_id:
            raise LineageError("event_id values must be strictly increasing integers")
        last_id = event_id
        if kind == "root":
            name = event.get("name")
            root_kind = event.get("root_kind", "object_root")
            if not isinstance(name, str) or root_kind not in ("object_root", "marker"):
                raise LineageError(f"event {event_id}: invalid root")
            source = Source(name, root_kind, matrix(event), event_id)
            register(source)
            if event.get("select", current is None):
                if stack:
                    raise LineageError(f"event {event_id}: cannot select a root inside a push")
                current = source
        elif kind == "load":
            if stack:
                raise LineageError(f"event {event_id}: cannot load a root inside a push")
            name = event.get("source")
            if name not in sources:
                raise LineageError(f"event {event_id}: unknown source {name!r}")
            current = sources[name]
            if "matrix_words" in event and matrix(event) != current.matrix:
                raise LineageError(f"event {event_id}: loaded matrix does not match {name}")
        elif kind == "push":
            base_matrix = matrix(event, "base_words")
            depth = event.get("depth")
            if depth != len(stack) + 1 or depth > 7:
                raise LineageError(f"event {event_id}: invalid push depth {depth}")
            if current is not None and current.matrix == base_matrix:
                base = current
            else:
                candidates = [candidate for candidate in by_matrix.get(base_matrix, [])
                              if candidate.event_id < event_id]
                if len(candidates) != 1:
                    keys = [candidate.key for candidate in candidates]
                    raise LineageError(f"event {event_id}: ambiguous base matrix candidates={keys}")
                base = candidates[0]
            stack.append(Frame(base, depth))
            current = base
        elif kind == "commit":
            if not stack:
                raise LineageError(f"event {event_id}: commit without push")
            if event.get("depth") != len(stack):
                raise LineageError(f"event {event_id}: commit depth mismatch")
            destination = event.get("destination")
            oba = event.get("oba")
            if not isinstance(destination, str) or not isinstance(oba, str):
                raise LineageError(f"event {event_id}: commit needs destination and oba")
            key = f"part:{event_id}:{oba}"
            source = Source(key, "part", matrix(event), event_id)
            register(source)
            record = {
                "event_id": event_id,
                "oba": oba,
                "destination": destination,
                "parent": {"kind": stack[-1].base.kind, "source": stack[-1].base.key},
                "source_stream": event.get("source_stream"),
                "record_slot": event.get("record_slot"),
                "matrix_words": list(source.matrix),
            }
            parts.append(record)
            commits_by_destination.setdefault(destination, []).append(record)
            current = source
        elif kind == "pop":
            if not stack or event.get("depth") != len(stack):
                raise LineageError(f"event {event_id}: pop depth mismatch")
            frame = stack.pop()
            current = frame.base
            if "restored_words" in event and matrix(event, "restored_words") != current.matrix:
                raise LineageError(f"event {event_id}: pop did not restore its pushed base")
        elif kind == "submit":
            destination = event.get("destination")
            candidates = [record for record in commits_by_destination.get(destination, [])
                          if record["event_id"] < event_id]
            if not candidates:
                raise LineageError(f"event {event_id}: submission has no prior commit")
            latest_id = max(record["event_id"] for record in candidates)
            latest = [record for record in candidates if record["event_id"] == latest_id]
            if len(latest) != 1:
                raise LineageError(f"event {event_id}: ambiguous destination {destination}")
            record = latest[0]
            if event.get("oba") != record["oba"]:
                raise LineageError(f"event {event_id}: submission OBA does not match commit")
            submissions.append({"event_id": event_id, "commit_event_id": latest_id,
                                "oba": record["oba"], "active": event.get("active", True)})
        else:
            raise LineageError(f"event {event_id}: unknown kind {kind!r}")
    if stack:
        raise LineageError(f"fixture ended with {len(stack)} unpopped stack frames")
    # Inactive submissions still account for an optional part's destination;
    # visibility is contract state, not permission to drop its lineage.
    submitted = {item["commit_event_id"] for item in submissions}
    missing = [item["event_id"] for item in parts
               if item.get("rendered", True) and item["event_id"] not in submitted]
    if missing:
        raise LineageError(f"rendered commits lack submissions: {missing}")
    return {"schema_version": 1, "parts": parts, "submissions": submissions}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = analyze(json.loads(args.fixture.read_text()))
    except (json.JSONDecodeError, OSError, LineageError) as error:
        raise SystemExit(f"lineage error: {error}") from error
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
