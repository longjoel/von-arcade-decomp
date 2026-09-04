#!/usr/bin/env python3
"""Compare two Tier A coverage reports without treating edges as executed."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_report(path: Path) -> dict[str, Any]:
    if path.is_symlink():
        raise ValueError(f"coverage report must not be a symlink: {path}")
    document = json.loads(path.read_text(encoding="utf-8"))
    validate_report(document, str(path))
    return document


def validate_report(document: Any, label: str = "coverage report") -> None:
    if not isinstance(document, dict):
        raise ValueError(f"coverage report must be an object: {label}")
    if document.get("tier") != "A" or document.get("edge_semantics") != "possible_static_edges":
        raise ValueError(f"coverage report must be Tier A possible_static_edges: {label}")
    for field in ("visited_instruction_count",):
        value = document.get(field, 0)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ValueError(f"coverage field {field} must be a nonnegative integer")


def values(document: dict[str, Any], field: str) -> set[str]:
    value = document.get(field, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"coverage field {field} must be a string array")
    return set(value)


def edges(document: dict[str, Any]) -> set[tuple[str, str]]:
    value = document.get("possible_static_edges", [])
    if not isinstance(value, list):
        raise ValueError("coverage field possible_static_edges must be an array")
    result = set()
    for edge in value:
        if not isinstance(edge, dict) or not isinstance(edge.get("caller"), str) \
                or not isinstance(edge.get("target"), str):
            raise ValueError("possible_static_edges must contain caller/target strings")
        result.add((edge["caller"], edge["target"]))
    return result


def compare(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    validate_report(before, "before coverage report")
    validate_report(after, "after coverage report")
    before_entries, after_entries = values(before, "observed_entry_points"), values(after, "observed_entry_points")
    before_edges, after_edges = edges(before), edges(after)
    before_ranges, after_ranges = before.get("ranges", []), after.get("ranges", [])
    if not isinstance(before_ranges, list) or not isinstance(after_ranges, list):
        raise ValueError("coverage field ranges must be arrays")
    return {
        "schema_version": 1,
        "semantics": "possible_static_edges",
        "before_capture_id": before.get("capture_id"),
        "after_capture_id": after.get("capture_id"),
        "before_phase": before.get("phase"),
        "after_phase": after.get("phase"),
        "visited_instruction_delta": after.get("visited_instruction_count", 0) - before.get("visited_instruction_count", 0),
        "visited_range_delta": len(after_ranges) - len(before_ranges),
        "new_observed_entry_points": sorted(after_entries - before_entries),
        "removed_observed_entry_points": sorted(before_entries - after_entries),
        "new_possible_static_edges": [
            {"caller": caller, "target": target}
            for caller, target in sorted(after_edges - before_edges)
        ],
        "removed_possible_static_edges": [
            {"caller": caller, "target": target}
            for caller, target in sorted(before_edges - after_edges)
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--before", type=Path, required=True)
    parser.add_argument("--after", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    for label, path in (("before", args.before), ("after", args.after), ("output", args.output)):
        if path.is_symlink():
            print(f"coverage phase comparison: {label} path must not be a symlink: {path}")
            return 1
        try:
            path.resolve().relative_to(root)
        except (OSError, RuntimeError, ValueError):
            print(f"coverage phase comparison: {label} path escapes root: {path}")
            return 1
        if label != "output" and not path.is_file():
            print(f"coverage phase comparison: missing {label} report: {path}")
            return 1
    try:
        result = compare(load_report(args.before), load_report(args.after))
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"coverage phase comparison: {error}")
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Coverage phase comparison: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
