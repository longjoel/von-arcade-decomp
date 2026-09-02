#!/usr/bin/env python3
"""Turn observed attract call targets into a small-slice reconstruction queue."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def number(value: str | int) -> int:
    return int(value, 0) if isinstance(value, str) else value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--json", required=True, type=Path)
    parser.add_argument("--markdown", required=True, type=Path)
    args = parser.parse_args()

    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
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
        number(edge["target"]) for edge in coverage.get("executed_direct_edges", [])
    )
    units = []
    for target_text in coverage.get("executed_direct_targets", []):
        target = number(target_text)
        # Explicit milestone membership is authoritative. This avoids a newly
        # nested semantic helper silently changing the closure denominator.
        matched = milestone_units.get(target)
        stage = matched.get("stage") if matched else None
        represented = stage in {"modeled", "integrated", "trace-validated", "byte-validated"}
        units.append(
            {
                "entry": f"0x{target:08x}",
                "observed_call_edges": edge_counts[target],
                "triage": "modeled-integration-queue" if stage == "modeled" else ("integrated-validation-queue" if represented else "untriaged"),
                "stage": stage or "planned",
                "priority": 0 if stage == "modeled" else (1 if represented else 2),
                "weight": None,
                "work_unit": matched.get("id") if matched else None,
                "sources": matched.get("sources", []) if matched else [],
            }
        )

    units.sort(key=lambda unit: (unit["priority"], number(unit["entry"])))
    represented_count = sum(unit["priority"] < 2 for unit in units)
    modeled_count = sum(unit["stage"] == "modeled" for unit in units)
    integrated_count = sum(unit["stage"] in {"integrated", "trace-validated", "byte-validated"} for unit in units)
    output = {
        "schema_version": 1,
        "coverage_source": str(args.coverage),
        "discovered_units": len(units),
        "represented_units": represented_count,
        "modeled_units": modeled_count,
        "integrated_units": integrated_count,
        "untriaged_units": len(units) - represented_count,
        "ordering": "modeled integration queue first, then integrated validation, then untriaged; address order preserves dependency locality",
        "units": units,
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Attract Reconstruction Worklist",
        "",
        f"- Observed direct-call units: {len(units)}",
        f"- Modeled integration queue: {modeled_count}",
        f"- Integrated or validated: {integrated_count}",
        f"- Untriaged: {len(units) - represented_count}",
        "",
        "| Entry | Edges | Triage | Work unit |",
        "| --- | ---: | --- | --- |",
    ]
    for unit in units:
        lines.append(
            f"| `{unit['entry']}` | {unit['observed_call_edges']} | "
            f"{unit['triage']} | {unit['work_unit'] or ''} |"
        )
    args.markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:7]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
