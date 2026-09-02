#!/usr/bin/env python3
"""Schema-v2 reconstruction ledger validation and accounting helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

CLASSIFICATIONS = {"code", "data", "padding", "unknown", "behavior"}
PHYSICAL_CLASSIFICATIONS = CLASSIFICATIONS - {"behavior"}
STAGES = {
    "planned", "modeled", "integrated", "trace-validated",
    "byte-validated", "blocked",
}


def number(value: str | int) -> int:
    return int(value, 0) if isinstance(value, str) else value


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def merged_intervals(intervals: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    for start, end in sorted(intervals):
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged]


def code_coverage(ledger: dict[str, Any]) -> dict[str, int]:
    """Count the union of physical code ranges, never semantic work units."""
    by_image: dict[str, int] = {}
    for image in ledger.get("images", []):
        ranges = [
            (number(item["start"]), number(item["end"]))
            for item in image.get("physical_ranges", [])
            if item.get("classification") == "code"
        ]
        by_image[image["name"]] = sum(end - start for start, end in merged_intervals(ranges))
    by_image["total"] = sum(by_image.values())
    return by_image


def validate(ledger: dict[str, Any], root: Path | None = None) -> list[str]:
    errors: list[str] = []
    if ledger.get("schema_version") != 2:
        errors.append("schema_version must be 2")
    seen_ids: set[str] = set()
    for image_index, image in enumerate(ledger.get("images", [])):
        prefix = f"images[{image_index}]"
        size = image.get("size")
        previous_end = -1
        for range_index, item in enumerate(image.get("physical_ranges", [])):
            where = f"{prefix}.physical_ranges[{range_index}]"
            classification = item.get("classification")
            if classification not in PHYSICAL_CLASSIFICATIONS:
                errors.append(f"{where}: invalid physical classification {classification!r}")
                continue
            try:
                start, end = number(item["start"]), number(item["end"])
            except (KeyError, TypeError, ValueError):
                errors.append(f"{where}: start/end must be integers")
                continue
            if start < 0 or end <= start:
                errors.append(f"{where}: invalid half-open range")
            if start < previous_end:
                errors.append(f"{where}: overlaps the preceding physical range")
            if isinstance(size, int) and end > size:
                errors.append(f"{where}: exceeds image size")
            previous_end = max(previous_end, end)

        for unit_index, unit in enumerate(image.get("work_units", [])):
            where = f"{prefix}.work_units[{unit_index}]"
            unit_id = unit.get("id")
            if not isinstance(unit_id, str) or not unit_id:
                errors.append(f"{where}: missing stable id")
            elif unit_id in seen_ids:
                errors.append(f"{where}: duplicate id {unit_id}")
            else:
                seen_ids.add(unit_id)
            if unit.get("classification") not in CLASSIFICATIONS:
                errors.append(f"{where}: invalid classification")
            if unit.get("stage") not in STAGES:
                errors.append(f"{where}: invalid stage")
            sources = unit.get("sources")
            if not isinstance(sources, list) or not all(isinstance(v, str) for v in sources):
                errors.append(f"{where}: sources must be a string array")
            if "source" in unit or "status" in unit:
                errors.append(f"{where}: legacy source/status field is forbidden")
            ranges = unit.get("ranges", [])
            if unit.get("classification") == "behavior" and ranges:
                errors.append(f"{where}: behavior units cannot claim physical bytes")
            for semantic_range in ranges:
                try:
                    start = number(semantic_range["start"])
                    end = number(semantic_range["end"])
                    if start < 0 or end <= start or (isinstance(size, int) and end > size):
                        raise ValueError
                except (KeyError, TypeError, ValueError):
                    errors.append(f"{where}: invalid semantic range")
                    break
            if root is not None:
                for source in sources or []:
                    if source.startswith("von/") or source.startswith("scripts/"):
                        if not (root / source).exists():
                            errors.append(f"{where}: missing source {source}")
    if not isinstance(ledger.get("images"), list):
        errors.append("images must be an array")
    return errors
