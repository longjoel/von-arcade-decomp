#!/usr/bin/env python3
"""Score saved JEV trace-triage reports against a blinded benchmark manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"unable to read {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def normalize_address(value: Any) -> str:
    if not isinstance(value, (str, int)) or isinstance(value, bool):
        raise ValueError(f"invalid benchmark address: {value!r}")
    try:
        numeric = int(value, 0) if isinstance(value, str) else value
    except ValueError:
        try:
            numeric = int(value, 16)
        except ValueError as error:
            raise ValueError(f"invalid benchmark address: {value!r}") from error
    return f"0x{numeric:08x}"


def reciprocal_rank(ranking: list[str], expected: set[str]) -> float:
    for index, candidate in enumerate(ranking, 1):
        if candidate in expected:
            return 1.0 / index
    return 0.0


def score(manifest: dict[str, Any], root: Path) -> dict[str, Any]:
    if manifest.get("schema_version") != 1:
        raise ValueError("benchmark schema_version must be 1")
    cases = manifest.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("benchmark cases must be a non-empty array")
    identifiers: set[str] = set()
    rows = []
    totals = {
        "jev_top1": 0, "jev_top3": 0, "jev_rr": 0.0, "abstentions": 0,
        "high_confidence_wrong": 0, "stable": 0, "stability_eligible": 0,
        "baseline_top1": 0, "baseline_top3": 0, "baseline_rr": 0.0,
        "cost": 0.0, "input_tokens": 0, "output_tokens": 0,
    }
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            raise ValueError(f"case {index} must be an object")
        identifier = case.get("id")
        if not isinstance(identifier, str) or not identifier or identifier in identifiers:
            raise ValueError(f"case {index} requires a unique non-empty id")
        identifiers.add(identifier)
        expected_values = case.get("expected_addresses")
        if not isinstance(expected_values, list) or not expected_values:
            raise ValueError(f"case {identifier} requires expected_addresses")
        expected = {normalize_address(value) for value in expected_values}
        report_values = case.get("reports")
        if not isinstance(report_values, list) or not report_values:
            raise ValueError(f"case {identifier} requires at least one saved report")
        reports = [load_object(root / value) for value in report_values]
        first = reports[0]
        if first.get("classification") != "advisory-discovery-only":
            raise ValueError(f"case {identifier} report is not an advisory triage report")
        ranking = [normalize_address(item.get("address"))
                   for item in first.get("ranked_candidates", []) if isinstance(item, dict)]
        if not ranking:
            raise ValueError(f"case {identifier} report has no ranked candidates")
        baseline_values = case.get("baseline_ranked_addresses")
        if not isinstance(baseline_values, list) or not baseline_values:
            raise ValueError(f"case {identifier} requires baseline_ranked_addresses")
        baseline = [normalize_address(value) for value in baseline_values]
        rr = reciprocal_rank(ranking, expected)
        baseline_rr = reciprocal_rank(baseline, expected)
        top_support = first["ranked_candidates"][0].get("support")
        high_confidence_wrong = (
            isinstance(top_support, (int, float)) and top_support >= 0.8
            and ranking[0] not in expected
        )
        choices = []
        for report in reports:
            candidates = report.get("ranked_candidates", [])
            if candidates and isinstance(candidates[0], dict):
                choices.append(normalize_address(candidates[0].get("address")))
        stable = len(reports) >= 3 and len(choices) == len(reports) and len(set(choices)) == 1
        totals["jev_top1"] += int(ranking[0] in expected)
        totals["jev_top3"] += int(bool(expected.intersection(ranking[:3])))
        totals["jev_rr"] += rr
        totals["abstentions"] += int(bool(first.get("abstained")))
        totals["high_confidence_wrong"] += int(high_confidence_wrong)
        totals["baseline_top1"] += int(baseline[0] in expected)
        totals["baseline_top3"] += int(bool(expected.intersection(baseline[:3])))
        totals["baseline_rr"] += baseline_rr
        for report in reports:
            usage = report.get("usage") if isinstance(report.get("usage"), dict) else {}
            totals["cost"] += float(usage.get("cost", 0) or 0)
            totals["input_tokens"] += int(usage.get("input_tokens", 0) or 0)
            totals["output_tokens"] += int(usage.get("output_tokens", 0) or 0)
        if len(reports) >= 3 and not first.get("abstained"):
            totals["stability_eligible"] += 1
            totals["stable"] += int(stable)
        rows.append({
            "id": identifier, "expected_addresses": sorted(expected), "jev_ranking": ranking,
            "baseline_ranking": baseline, "jev_reciprocal_rank": rr,
            "baseline_reciprocal_rank": baseline_rr, "abstained": bool(first.get("abstained")),
            "high_confidence_wrong": high_confidence_wrong,
            "stable_top_choice": stable if len(reports) >= 3 else None,
        })
    count = len(rows)
    metrics = {
        "case_count": count,
        "jev_top1_accuracy": totals["jev_top1"] / count,
        "jev_top3_recall": totals["jev_top3"] / count,
        "jev_mean_reciprocal_rank": totals["jev_rr"] / count,
        "baseline_top1_accuracy": totals["baseline_top1"] / count,
        "baseline_top3_recall": totals["baseline_top3"] / count,
        "baseline_mean_reciprocal_rank": totals["baseline_rr"] / count,
        "abstention_rate": totals["abstentions"] / count,
        "high_confidence_error_rate": totals["high_confidence_wrong"] / count,
        "top_choice_stability": (totals["stable"] / totals["stability_eligible"]
                                 if totals["stability_eligible"] else None),
        "total_cost": totals["cost"],
        "input_tokens": totals["input_tokens"],
        "output_tokens": totals["output_tokens"],
    }
    repeated_all_non_abstaining = totals["stability_eligible"] == count - totals["abstentions"]
    stability_pass = (repeated_all_non_abstaining
                      and metrics["top_choice_stability"] is not None
                      and metrics["top_choice_stability"] >= 0.9)
    gates = {
        "at_least_20_cases": count >= 20,
        "top3_not_below_baseline": metrics["jev_top3_recall"] >= metrics["baseline_top3_recall"],
        "mrr_improves_10_percent": (
            metrics["jev_mean_reciprocal_rank"] >= metrics["baseline_mean_reciprocal_rank"] * 1.10
            and metrics["jev_mean_reciprocal_rank"] > metrics["baseline_mean_reciprocal_rank"]
        ),
        "high_confidence_error_at_most_10_percent": metrics["high_confidence_error_rate"] <= 0.10,
        "top_choice_stability_at_least_90_percent": stability_pass,
    }
    return {
        "schema_version": 1, "classification": "advisory-benchmark-only",
        "metrics": metrics, "gates": gates, "recommended": all(gates.values()), "cases": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        result = score(load_object(args.manifest), args.root)
    except ValueError as error:
        print(f"jev trace benchmark: {error}", file=sys.stderr)
        return 2
    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(encoded)
    return 0 if result["recommended"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
