#!/usr/bin/env python3
"""Migrate the reconstruction ledger from schema v1 to schema v2."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from reconstruction_ledger import merged_intervals, number, validate


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def model_sources(entry: dict) -> list[str]:
    values = [entry.get("source"), *entry.get("sources", []), *entry.get("evidence", [])]
    expanded = []
    for value in values:
        if not isinstance(value, str):
            continue
        expanded.extend(part.strip() for part in value.split(", ") if part.strip())
    return list(dict.fromkeys(expanded))


def migrate(old: dict) -> dict:
    if old.get("schema_version") == 2:
        return old
    result = {
        "schema_version": 2,
        "objective": "c-only-i960-attract-60s",
        "metric": {
            "byte_coverage": "union of non-overlapping physical code ranges",
            "delivery_gate": "integrated and trace-validated attract work units",
        },
        "images": [],
    }
    for image in old.get("images", []):
        units = []
        by_classification: dict[str, list[tuple[int, int]]] = {}
        for entry in image.get("slices", []):
            classification = entry.get("classification", "unknown")
            sources = model_sources(entry)
            recovered = [path for path in sources if re.search(r"/recovered_[^/]+\.c$", path)]
            stage = entry.get("status", "planned")
            if stage == "provisional":
                stage = "modeled" if recovered else "planned"
            unit = {
                "id": f"{image['name']}.{slug(entry['name'])}",
                "name": entry["name"],
                "classification": classification,
                "stage": stage,
                "sources": sources,
                "evidence": list(entry.get("evidence", [])),
            }
            if classification != "behavior" and "start" in entry and "end" in entry:
                start, end = number(entry["start"]), number(entry["end"])
                # A few v1 marker records used identical endpoints. They are
                # semantic labels, not physical byte claims.
                if end > start:
                    unit["ranges"] = [{"start": f"0x{start:08x}", "end": f"0x{end:08x}"}]
                    by_classification.setdefault(classification, []).append((start, end))
            for key in ("symbol", "notes"):
                if key in entry:
                    unit[key] = entry[key]
            units.append(unit)

        physical_ranges = []
        # Classification conflicts are resolved conservatively. Code wins only
        # because the v1 ledger explicitly identified executable addresses.
        occupied: list[tuple[int, int]] = []
        serial = 0
        for classification in ("code", "data", "padding", "unknown"):
            for start, end in merged_intervals(by_classification.get(classification, [])):
                fragments = [(start, end)]
                for taken_start, taken_end in occupied:
                    next_fragments = []
                    for left, right in fragments:
                        if right <= taken_start or left >= taken_end:
                            next_fragments.append((left, right))
                        else:
                            if left < taken_start:
                                next_fragments.append((left, taken_start))
                            if right > taken_end:
                                next_fragments.append((taken_end, right))
                    fragments = next_fragments
                for left, right in fragments:
                    serial += 1
                    physical_ranges.append({
                        "id": f"{image['name']}.physical-{serial:04d}",
                        "start": f"0x{left:08x}", "end": f"0x{right:08x}",
                        "classification": classification,
                    })
                    occupied.append((left, right))
                    occupied.sort()
        physical_ranges.sort(key=lambda item: number(item["start"]))
        migrated_image = {key: value for key, value in image.items() if key != "slices"}
        migrated_image["physical_ranges"] = physical_ranges
        migrated_image["work_units"] = units
        result["images"].append(migrated_image)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    migrated = migrate(json.loads(args.ledger.read_text(encoding="utf-8")))
    errors = validate(migrated)
    if errors:
        raise SystemExit("\n".join(errors))
    text = json.dumps(migrated, indent=2) + "\n"
    if args.write:
        args.ledger.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
