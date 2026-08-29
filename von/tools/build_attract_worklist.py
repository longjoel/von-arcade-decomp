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
    slices = []
    for image in ledger.get("images", []):
        if image.get("name") != "maincpu":
            continue
        for entry in image.get("slices", []):
            if entry.get("classification") == "code":
                slices.append((number(entry["start"]), number(entry["end"]), entry))

    edge_counts = Counter(
        number(edge["target"]) for edge in coverage.get("executed_direct_edges", [])
    )
    units = []
    for target_text in coverage.get("executed_direct_targets", []):
        target = number(target_text)
        matched = next((entry for start, end, entry in slices if start <= target < end), None)
        represented = bool(matched and matched.get("status") in {"provisional", "byte-validated"})
        units.append(
            {
                "entry": f"0x{target:08x}",
                "observed_call_edges": edge_counts[target],
                "triage": "represented-needs-integration" if represented else "untriaged",
                "weight": None,
                "slice": matched.get("name") if matched else None,
                "source": matched.get("source") if matched else None,
            }
        )

    represented_count = sum(unit["triage"] == "represented-needs-integration" for unit in units)
    output = {
        "schema_version": 1,
        "coverage_source": str(args.coverage),
        "discovered_units": len(units),
        "represented_units": represented_count,
        "untriaged_units": len(units) - represented_count,
        "units": units,
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Attract Reconstruction Worklist",
        "",
        f"- Observed direct-call units: {len(units)}",
        f"- Already represented in replacement source, pending validation: {represented_count}",
        f"- Untriaged: {len(units) - represented_count}",
        "",
        "| Entry | Edges | Triage | Existing slice |",
        "| --- | ---: | --- | --- |",
    ]
    for unit in units:
        lines.append(
            f"| `{unit['entry']}` | {unit['observed_call_edges']} | "
            f"{unit['triage']} | {unit['slice'] or ''} |"
        )
    args.markdown.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:7]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
