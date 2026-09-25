#!/usr/bin/env python3
"""Offline tests for the saved-report JEV benchmark scorer."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from jev_trace_benchmark import score  # noqa: E402


def report(ranking: list[tuple[str, float]], *, abstained: bool = False) -> dict:
    return {
        "classification": "advisory-discovery-only",
        "abstained": abstained,
        "ranked_candidates": [
            {"address": address, "support": support} for address, support in ranking
        ],
        "usage": {"input_tokens": 100, "output_tokens": 5, "cost": 0.001},
    }


def main() -> int:
    with tempfile.TemporaryDirectory() as directory_text:
        root = Path(directory_text)
        winning = report([("0x2000", 0.9), ("0x1000", 0.1)])
        losing = report([("0x1000", 0.85), ("0x2000", 0.15)])
        for name, value in (("win1.json", winning), ("win2.json", winning),
                            ("win3.json", winning), ("lose.json", losing)):
            (root / name).write_text(json.dumps(value), encoding="utf-8")
        manifest = {
            "schema_version": 1,
            "cases": [
                {"id": "right", "expected_addresses": ["0x2000"],
                 "baseline_ranked_addresses": ["0x1000", "0x2000"],
                 "reports": ["win1.json", "win2.json", "win3.json"]},
                {"id": "wrong", "expected_addresses": ["0x2000"],
                 "baseline_ranked_addresses": ["0x2000", "0x1000"],
                 "reports": ["lose.json"]},
            ],
        }
        result = score(manifest, root)
        metrics = result["metrics"]
        assert metrics["case_count"] == 2
        assert metrics["jev_top1_accuracy"] == 0.5
        assert metrics["jev_top3_recall"] == 1.0
        assert metrics["jev_mean_reciprocal_rank"] == 0.75
        assert metrics["baseline_mean_reciprocal_rank"] == 0.75
        assert metrics["high_confidence_error_rate"] == 0.5
        assert metrics["top_choice_stability"] == 1.0
        assert metrics["total_cost"] == 0.004
        assert not result["gates"]["at_least_20_cases"]
        assert not result["gates"]["mrr_improves_10_percent"]
        assert not result["recommended"]

        duplicate = {"schema_version": 1, "cases": [manifest["cases"][0], manifest["cases"][0]]}
        try:
            score(duplicate, root)
        except ValueError as error:
            assert "unique" in str(error)
        else:
            raise AssertionError("duplicate benchmark id was accepted")

    print("PASS: JEV benchmark accuracy, ranking, stability, cost, and adoption gates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
