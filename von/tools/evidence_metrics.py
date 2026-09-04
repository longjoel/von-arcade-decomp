#!/usr/bin/env python3
"""Report evidence-workflow metrics from authoritative JSON artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"metrics input must be an object: {path}")
    return document


def age_report(ledger: dict[str, Any], as_of: str | None = None) -> dict[str, Any]:
    """Report age only from declared unit timestamps, never filesystem mtimes."""
    reference = datetime.fromisoformat(as_of.replace("Z", "+00:00")) if as_of else None
    if reference is not None:
        if reference.tzinfo is None:
            raise ValueError("metrics as_of must include a timezone")
        reference = reference.astimezone(timezone.utc)
    ages: dict[str, list[tuple[float, str]]] = {}
    for image in ledger.get("images", []):
        for unit in image.get("work_units", []):
            created = unit.get("created_at")
            if created is None:
                continue
            if not isinstance(created, str) or reference is None:
                raise ValueError("metrics unit created_at requires an ISO timestamp and --as-of")
            try:
                timestamp = datetime.fromisoformat(created.replace("Z", "+00:00"))
            except ValueError as error:
                raise ValueError(f"metrics unit created_at is invalid: {created}") from error
            if timestamp.tzinfo is None:
                raise ValueError("metrics unit created_at must include a timezone")
            age = (reference - timestamp.astimezone(timezone.utc)).total_seconds()
            if age < 0:
                raise ValueError("metrics unit created_at cannot be in the future")
            stage = unit.get("stage")
            if isinstance(stage, str):
                ages.setdefault(stage, []).append((age, str(unit.get("id", "?"))))
    result: dict[str, Any] = {}
    for stage in ("planned", "modeled", "integrated", "trace-validated", "byte-validated", "blocked"):
        values = sorted(ages.get(stage, []))
        if not values:
            result[stage] = {"timestamped_items": 0, "median_age_seconds": None,
                             "oldest_age_seconds": None, "oldest_unit_id": None}
            continue
        age_values = [value[0] for value in values]
        middle = len(age_values) // 2
        median = age_values[middle] if len(age_values) % 2 else (age_values[middle - 1] + age_values[middle]) / 2
        oldest_age, oldest_id = max(values)
        result[stage] = {"timestamped_items": len(values),
                         "median_age_seconds": median,
                         "oldest_age_seconds": oldest_age,
                         "oldest_unit_id": oldest_id}
    return result


def metrics(ledger: dict[str, Any], worklist: dict[str, Any], coverage: dict[str, Any],
            comparison: dict[str, Any], experiments: dict[str, Any] | None = None,
            as_of: str | None = None) -> dict[str, Any]:
    for name, document in (("ledger", ledger), ("worklist", worklist),
                           ("coverage", coverage), ("comparison", comparison)):
        if not isinstance(document, dict):
            raise ValueError(f"metrics {name} input must be an object")
    if experiments is not None and not isinstance(experiments, dict):
        raise ValueError("metrics experiments input must be an object")
    stages = Counter(
        unit.get("stage") for image in ledger.get("images", [])
        for unit in image.get("work_units", [])
    )
    discovered = worklist.get("discovered_units", 0)
    modeled = stages.get("modeled", 0)
    integrated = stages.get("integrated", 0) + stages.get("trace-validated", 0) + stages.get("byte-validated", 0)
    def percentage(value: int, total: int) -> float | None:
        return round(value * 100.0 / total, 2) if total else None
    return {
        "schema_version": 1,
        "stages": {stage: stages.get(stage, 0) for stage in
                   ("planned", "modeled", "integrated", "trace-validated", "byte-validated", "blocked")},
        "age": age_report(ledger, as_of),
        "discovery": {
            "units": discovered,
            "modeled_conversion_percent": percentage(modeled, discovered),
            "integrated_conversion_percent": percentage(integrated, discovered),
            "active_modeled_units": worklist.get("active_modeled_units", []),
            "modeled_wip_limit": worklist.get("modeled_wip_limit", 1),
        },
        "coverage": {
            "tier": coverage.get("tier"),
            "possible_static_edges": coverage.get("possible_static_edge_count", 0),
            "confirmed_dynamic_edges": coverage.get("confirmed_dynamic_edge_count", 0),
            "observed_entry_points": coverage.get("observed_entry_point_count", 0),
        },
        "comparison": {
            "events_compared": comparison.get("compared_events", 0),
            "matched_prefix_events": comparison.get("matched_prefix_events", 0),
            "checkpoints_passed": [name for name in comparison.get("original_checkpoints", [])
                                   if name not in comparison.get("missed_checkpoints", [])],
            "missed_checkpoints": comparison.get("missed_checkpoints", []),
            "unexpected_checkpoints": comparison.get("unexpected_checkpoints", []),
        },
        "experiments": {
            "changed_decision": (experiments or {}).get("changed_decision", 0),
            "quarantined": (experiments or {}).get("quarantined", 0),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--worklist", type=Path)
    parser.add_argument("--coverage", type=Path)
    parser.add_argument("--comparison", type=Path)
    parser.add_argument("--experiments", type=Path)
    parser.add_argument("--as-of", help="UTC ISO timestamp used for declared unit age metrics")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = metrics(load(args.ledger), load(args.worklist), load(args.coverage),
                         load(args.comparison), load(args.experiments), args.as_of)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Evidence metrics: {error}")
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Evidence metrics: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
