#!/usr/bin/env python3
"""Summarize bounded Virtual-On MAME boundary events from an oslog trace."""

from __future__ import annotations

import argparse
import gzip
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from capture_manifest import validate as validate_capture


EVENT_RE = re.compile(r"^\[[^]]+\]\s+(?P<event>\w+):\s+(?P<body>.*)$")
SAMPLE_RE = re.compile(r"^sample=(?P<body>.*)$")
FIELD_RE = re.compile(r"(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>[^ ]+)")
FIFO_RE = re.compile(r"data=(?P<data>[0-9a-fA-F]+)")
GEO_RE = re.compile(r"pc=(?P<pc>[0-9a-fA-F]+) address=(?P<address>[0-9a-fA-F]+) data=(?P<data>[0-9a-fA-F]+)")


def fields(body: str) -> dict[str, str | int | float]:
    result: dict[str, str | int | float] = {}
    hexadecimal = {"pc", "address", "data", "read", "write", "slot", "byte", "value"}
    for match in FIELD_RE.finditer(body):
        key, value = match.group("key"), match.group("value")
        try:
            if key == "time":
                result[key] = float(value)
            elif key in hexadecimal:
                result[key] = int(value, 16)
            elif value.isdigit():
                result[key] = int(value)
            else:
                result[key] = value
        except ValueError:
            result[key] = value
    return result


def ndjson_event(line: str, seq: int) -> dict | None:
    match = EVENT_RE.match(line)
    if match:
        event = {"seq": seq, "kind": match.group("event")}
        event.update(fields(match.group("body")))
        return event
    sample = SAMPLE_RE.match(line)
    if sample:
        event = {"seq": seq, "kind": "audio-queue-sample"}
        event.update(fields(sample.group("body")))
        return event
    return None


def read_trace(path: Path) -> str:
    """Read plain or content-addressed gzip traces without changing provenance."""
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8", errors="replace") as stream:
            return stream.read()
    return path.read_text(encoding="utf-8", errors="replace")


def select_events(events: list[dict], max_events: int | None = None,
                  event_kinds: set[str] | None = None,
                  pc_min: int | None = None, pc_max: int | None = None) -> list[dict]:
    selected = []
    for event in events:
        if event_kinds and event.get("kind") not in event_kinds:
            continue
        pc = event.get("pc")
        if pc_min is not None and (not isinstance(pc, int) or pc < pc_min):
            continue
        if pc_max is not None and (not isinstance(pc, int) or pc > pc_max):
            continue
        selected.append(event)
        if max_events is not None and len(selected) >= max_events:
            break
    for seq, event in enumerate(selected):
        event["seq"] = seq
    return selected


def summary(events: list[dict], source: Path, max_events: int | None = None,
            event_kinds: set[str] | None = None, pc_min: int | None = None,
            pc_max: int | None = None, provenance: dict[str, Any] | None = None) -> dict:
    selected = select_events(events, max_events, event_kinds, pc_min, pc_max)
    counts = Counter(event.get("kind") for event in selected)
    result = {
        "schema_version": 1,
        "source": str(source),
        "event_count": len(selected),
        "event_counts": dict(sorted(counts.items())),
        "first_event": selected[0] if selected else None,
        "last_event": selected[-1] if selected else None,
        "filters": {
            "max_events": max_events,
            "event_kinds": sorted(event_kinds or set()),
            "pc_min": pc_min,
            "pc_max": pc_max,
        },
    }
    if provenance is not None:
        result["provenance"] = provenance
    return result


def load_provenance(manifest_path: Path, root: Path, source: Path) -> dict[str, Any]:
    """Validate and bind the normalized source to a canonical capture sidecar."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = validate_capture(manifest, root)
    if errors:
        raise ValueError("capture manifest: " + "; ".join(errors))
    try:
        source_relative = str(source.resolve().relative_to(root.resolve()))
    except ValueError as error:
        raise ValueError("trace source escapes capture root") from error
    artifacts = manifest.get("artifacts", [])
    artifact_paths = {item.get("path") for item in artifacts if isinstance(item, dict)}
    if source_relative not in artifact_paths:
        raise ValueError(f"trace source is not declared as a capture artifact: {source_relative}")
    return {
        "capture_id": manifest["id"],
        "objective": manifest["objective"],
        "stimulus": manifest["stimulus"],
        "artifact": source_relative,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    parser.add_argument("--ndjson", type=Path,
                        help="also write normalized ordered events")
    parser.add_argument("--summary", type=Path,
                        help="also write a compact normalized-event summary")
    parser.add_argument("--max-events", type=int)
    parser.add_argument("--event-kind", action="append", default=[])
    parser.add_argument("--pc-min", type=lambda value: int(value, 0))
    parser.add_argument("--pc-max", type=lambda value: int(value, 0))
    parser.add_argument("--capture-manifest", type=Path,
                        help="canonical sidecar that declares the input trace artifact")
    parser.add_argument("--capture-root", type=Path,
                        help="root used to resolve paths in --capture-manifest (defaults to its parent)")
    args = parser.parse_args()
    if args.max_events is not None and args.max_events < 0:
        parser.error("--max-events must be non-negative")
    if args.pc_min is not None and args.pc_max is not None and args.pc_min > args.pc_max:
        parser.error("--pc-min cannot exceed --pc-max")

    provenance = None
    if args.capture_manifest:
        capture_root = (args.capture_root or args.capture_manifest.parent).resolve()
        try:
            provenance = load_provenance(args.capture_manifest, capture_root, args.trace)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            print(f"Trace provenance: {error}")
            return 1

    counts: Counter[str] = Counter()
    fifo: list[tuple[int, str, str]] = []
    geo: list[tuple[int, str, str, str]] = []
    tile_count = 0

    normalized: list[dict] = []
    for line_number, line in enumerate(read_trace(args.trace).splitlines(), 1):
        event_record = ndjson_event(line, len(normalized))
        if event_record is not None:
            event_record["source_line"] = line_number
            normalized.append(event_record)
        match = EVENT_RE.match(line)
        if not match:
            continue
        event = match.group("event")
        body = match.group("body")
        counts[event] += 1
        if event == "vonj_copro_fifo":
            data = FIFO_RE.search(body)
            if data:
                pc = re.search(r"pc=([0-9a-fA-F]+)", body)
                fifo.append((line_number, pc.group(1) if pc else "?", data.group("data")))
        elif event == "vonj_geo_cmd":
            match_geo = GEO_RE.search(body)
            if match_geo:
                geo.append((line_number, match_geo.group("pc"), match_geo.group("address"), match_geo.group("data")))
        elif event == "vonj_tile_write":
            tile_count += 1

    print("Event counts:")
    for event, count in sorted(counts.items()):
        print(f"  {event}: {count}")

    print("FIFO sequence:")
    for line_number, pc, data in fifo:
        print(f"  line={line_number} pc={pc} data={data}")

    print("First Geo events:")
    for line_number, pc, address, data in geo[:32]:
        print(f"  line={line_number} pc={pc} address={address} data={data}")

    print(f"Tile writes: {tile_count}")
    event_kinds = set(args.event_kind)
    all_normalized = normalized
    if args.ndjson or args.summary:
        normalized = select_events(normalized, args.max_events, event_kinds, args.pc_min, args.pc_max)
    if args.ndjson:
        args.ndjson.parent.mkdir(parents=True, exist_ok=True)
        args.ndjson.write_text(
            "".join(json.dumps(event, sort_keys=True) + "\n" for event in normalized),
            encoding="utf-8",
        )
        print(f"Normalized events: {len(normalized)} -> {args.ndjson}")
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(json.dumps(
            summary(all_normalized, args.trace, args.max_events, event_kinds,
                    args.pc_min, args.pc_max, provenance), indent=2
        ) + "\n", encoding="utf-8")
        print(f"Event summary: {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
