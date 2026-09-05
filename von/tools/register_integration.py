#!/usr/bin/env python3
"""Register validated integration evidence for one ledger work unit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


STAGES = {"integrated", "trace-validated", "byte-validated"}


def safe_file(root: Path, value: Any) -> bool:
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        return False
    path = root / value
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, RuntimeError, ValueError):
        return False
    current = root
    for part in path.relative_to(root).parts:
        current /= part
        if current.is_symlink():
            return False
    return path.is_file()


def register(ledger: dict[str, Any], unit_id: str, image: str,
             checkpoint: str, test: str, root: Path) -> list[str]:
    if not isinstance(ledger, dict):
        return ["ledger must be an object"]
    images = ledger.get("images")
    if not isinstance(images, list):
        return ["ledger images must be an array"]
    if not checkpoint:
        return ["integration checkpoint must be non-empty"]
    if not safe_file(root, image):
        return [f"missing or unsafe integration image {image}"]
    if not safe_file(root, test):
        return [f"missing or unsafe integration test {test}"]
    matches = [
        unit for image_entry in images if isinstance(image_entry, dict)
        for unit in image_entry.get("work_units", [])
        if isinstance(unit, dict) and unit.get("id") == unit_id
    ]
    if not matches:
        return [f"unknown ledger work unit {unit_id}"]
    if len(matches) != 1:
        return [f"duplicate ledger work unit {unit_id}"]
    unit = matches[0]
    if unit.get("stage") not in STAGES:
        return [f"work unit {unit_id} is not integration-promoted"]
    modeling = unit.get("modeling")
    if not isinstance(modeling, dict):
        return [f"work unit {unit_id} is missing modeling evidence"]
    for field in ("boundary", "test", "unresolved_behavior"):
        if not isinstance(modeling.get(field), str) or not modeling[field]:
            return [f"work unit {unit_id} is missing modeling.{field}"]
    if not safe_file(root, modeling["test"]):
        return [f"work unit {unit_id} has missing or unsafe modeling test {modeling['test']}"]
    if "integration" in unit:
        return [f"work unit {unit_id} already has integration evidence"]
    unit["integration"] = {
        "image": image,
        "checkpoint": checkpoint,
        "test": test,
    }
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--unit", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--test", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
        print(f"Integration registration: unable to read ledger: {error}")
        return 1
    errors = register(ledger, args.unit, args.image, args.checkpoint, args.test, root)
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1
    args.ledger.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    print(f"Registered integration evidence: {args.unit}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
