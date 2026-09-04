#!/usr/bin/env python3
"""Turn observed attract call targets into a small-slice reconstruction queue."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def number(value: str | int) -> int:
    return int(value, 0) if isinstance(value, str) else value


def missing_dynamic_edges(comparison: dict) -> list[tuple[int, int]]:
    raw_edges = comparison.get("missing_dynamic_edges", [])
    if not isinstance(raw_edges, list):
        raise ValueError("comparison missing_dynamic_edges must be an array")
    edges = []
    for index, edge in enumerate(raw_edges):
        if not isinstance(edge, list) or len(edge) != 2:
            raise ValueError(f"comparison missing_dynamic_edges[{index}] must be a caller/target pair")
        try:
            edges.append((number(edge[0]), number(edge[1])))
        except (TypeError, ValueError) as error:
            raise ValueError(f"comparison missing_dynamic_edges[{index}] must contain addresses") from error
    return edges


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--comparison", type=Path,
                        help="optional ordered comparison used for causal prioritization")
    parser.add_argument("--json", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()

    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    comparison = None
    causal_edges: list[tuple[int, int]] = []
    if args.comparison:
        comparison = json.loads(args.comparison.read_text(encoding="utf-8"))
        if not isinstance(comparison, dict):
            raise SystemExit("comparison must be a JSON object")
        try:
            causal_edges = missing_dynamic_edges(comparison)
        except ValueError as error:
            raise SystemExit(str(error)) from error
    if coverage.get("tier") != "A" or coverage.get("edge_semantics") != "possible_static_edges":
        raise SystemExit("coverage must be a Tier A possible_static_edges report")
    work_units = []
    milestone_units = {}
    for image in ledger.get("images", []):
        if image.get("name") != "maincpu":
            continue
        for entry in image.get("work_units", []):
            milestone = entry.get("milestones", {}).get("c-only-i960-attract-60s", {})
            for target in milestone.get("entries", []):
                milestone_units[number(target)] = entry
            if entry.get("classification") != "code":
                continue
            for semantic_range in entry.get("ranges", []):
                work_units.append((number(semantic_range["start"]), number(semantic_range["end"]), entry))

    edge_counts = Counter(
        number(edge["target"]) for edge in coverage.get("possible_static_edges", [])
    )
    units = []
    for target_text in coverage.get("observed_entry_points", []):
        target = number(target_text)
        # Explicit milestone membership is authoritative. This avoids a newly
        # nested semantic helper silently changing the closure denominator.
        matched = milestone_units.get(target)
        stage = matched.get("stage") if matched else None
        represented = stage in {"modeled", "integrated", "trace-validated", "byte-validated"}
        dependencies = [[f"0x{caller:08x}", f"0x{callee:08x}"]
                        for caller, callee in causal_edges if callee == target]
        units.append(
            {
                "entry": f"0x{target:08x}",
                "possible_static_edges": edge_counts[target],
                "dynamic_dependencies": dependencies,
                "causal_priority": 0 if dependencies else 1,
                "triage": "modeled-integration-queue" if stage == "modeled" else ("integrated-validation-queue" if represented else "untriaged"),
                "stage": stage or "planned",
                "priority": 0 if stage == "modeled" else (1 if represented else 2),
                "weight": None,
                "work_unit": matched.get("id") if matched else None,
                "sources": matched.get("sources", []) if matched else [],
            }
        )

    units.sort(key=lambda unit: ((unit["causal_priority"], unit["priority"], number(unit["entry"]))
                                 if comparison is not None else
                                 (unit["priority"], number(unit["entry"]))))
    represented_count = sum(unit["priority"] < 2 for unit in units)
    modeled_count = sum(unit["stage"] == "modeled" for unit in units)
    integrated_count = sum(unit["stage"] in {"integrated", "trace-validated", "byte-validated"} for unit in units)
    active_modeled = [
        entry["id"] for image in ledger.get("images", [])
        for entry in image.get("work_units", [])
        if entry.get("stage") == "modeled" and entry.get("active") is True
    ]
    if len(active_modeled) > 1:
        raise SystemExit("modeled work-in-progress limit exceeded: more than one active unit")
    output = {
        "schema_version": 1,
        "coverage_tier": coverage["tier"],
        "edge_semantics": coverage["edge_semantics"],
        "coverage_source": str(args.coverage),
        "discovered_units": len(units),
        "represented_units": represented_count,
        "modeled_units": modeled_count,
        "integrated_units": integrated_count,
        "untriaged_units": len(units) - represented_count,
        "modeled_wip_limit": 1,
        "active_modeled_units": active_modeled,
        "ordering": ("causal dynamic dependencies first, then modeled integration queue, then integrated validation, then untriaged"
                     if comparison is not None else
                     "modeled integration queue first, then integrated validation, then untriaged; address order preserves dependency locality"),
        "units": units,
    }
    if comparison is not None:
        output["comparison_source"] = str(args.comparison)
        output["missing_dynamic_edge_count"] = len(causal_edges)
        output["missed_checkpoints"] = comparison.get("missed_checkpoints", [])
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Attract Reconstruction Worklist",
        "",
        f"- Observed entry-point units: {len(units)}",
        f"- Modeled integration queue: {modeled_count}",
        f"- Integrated or validated: {integrated_count}",
        f"- Untriaged: {len(units) - represented_count}",
        "",
        "| Entry | Edges | Triage | Work unit |",
        "| --- | ---: | --- | --- |",
    ]
    for unit in units:
        lines.append(
            f"| `{unit['entry']}` | {unit['possible_static_edges']} | "
            f"{unit['triage']} | {unit['work_unit'] or ''} |"
        )
    args.markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:7]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
