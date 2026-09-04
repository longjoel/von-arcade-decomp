#!/usr/bin/env python3
"""Report evidence-workflow metrics from authoritative JSON artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def load(path: Path | None) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path else {}


def metrics(ledger: dict[str, Any], worklist: dict[str, Any], coverage: dict[str, Any], comparison: dict[str, Any]) -> dict[str, Any]:
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
        "discovery": {
            "units": discovered,
            "modeled_conversion_percent": percentage(modeled, discovered),
            "integrated_conversion_percent": percentage(integrated, modeled),
            "active_modeled_units": worklist.get("active_modeled_units", []),
            "modeled_wip_limit": worklist.get("modeled_wip_limit", 1),
        },
        "coverage": {
            "tier": coverage.get("tier"),
            "possible_static_edges": coverage.get("possible_static_edge_count", 0),
            "observed_entry_points": coverage.get("observed_entry_point_count", 0),
        },
        "comparison": {
            "events_compared": comparison.get("compared_events", 0),
            "matched_prefix_events": comparison.get("matched_prefix_events", 0),
            "missed_checkpoints": comparison.get("missed_checkpoints", []),
            "unexpected_checkpoints": comparison.get("unexpected_checkpoints", []),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--worklist", type=Path)
    parser.add_argument("--coverage", type=Path)
    parser.add_argument("--comparison", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = metrics(load(args.ledger), load(args.worklist), load(args.coverage), load(args.comparison))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Evidence metrics: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
