#!/usr/bin/env python3
"""Build a non-destructive cleanup plan from an evidence inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


CLASS_ACTIONS = {
    "source-and-tests": ("retain", "keep"),
    "canonical-evidence": ("retain", "keep-with-manifest"),
    "private-rom-material": ("retain-private", "keep-ignored"),
    "reproducible-generated": ("remove-after-review", "delete-after-recipe-review"),
    "legacy-or-ambiguous": ("quarantine-after-review", "quarantine-after-review"),
}
SHA256_LENGTH = 64


def inventory_digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _valid_digest(value: Any) -> bool:
    return isinstance(value, str) and len(value) == SHA256_LENGTH and all(
        character in "0123456789abcdef" for character in value
    )


def validate_inventory(document: Any) -> list[str]:
    if not isinstance(document, dict):
        return ["inventory must be an object"]
    if document.get("schema_version") != 1:
        return ["inventory schema_version must be 1"]
    files = document.get("files")
    if not isinstance(files, list):
        return ["inventory files must be an array"]
    errors: list[str] = []
    seen: set[str] = set()
    path_hashes: dict[str, str] = {}
    for index, record in enumerate(files):
        where = f"files[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{where}: record must be an object")
            continue
        path = record.get("path")
        if not isinstance(path, str) or not path or Path(path).is_absolute() \
                or ".." in Path(path).parts:
            errors.append(f"{where}: path must be a safe relative path")
        elif path in seen:
            errors.append(f"{where}: duplicate path {path}")
        else:
            seen.add(path)
            path_hashes[path] = record.get("sha256", "")
        size = record.get("bytes")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            errors.append(f"{where}: bytes must be a nonnegative integer")
        if not _valid_digest(record.get("sha256")):
            errors.append(f"{where}: sha256 must be a lowercase SHA-256 digest")
        if not isinstance(record.get("tracked"), bool):
            errors.append(f"{where}: tracked must be boolean")
        classification = record.get("classification")
        if classification not in CLASS_ACTIONS:
            errors.append(f"{where}: unsupported classification {classification!r}")
        producer = record.get("producer")
        consumers = record.get("consumers")
        if producer is not None and (not isinstance(producer, str) or not producer):
            errors.append(f"{where}: producer must be a non-empty string or null")
        if not isinstance(consumers, list) or not all(isinstance(item, str) and item for item in consumers):
            errors.append(f"{where}: consumers must be a string array")
        decision = record.get("decision")
        if classification in CLASS_ACTIONS and decision != CLASS_ACTIONS[classification][1]:
            errors.append(f"{where}: decision does not match classification")
    groups = document.get("duplicate_groups")
    if not isinstance(groups, list):
        errors.append("inventory duplicate_groups must be an array")
    else:
        grouped_paths: set[str] = set()
        for index, group in enumerate(groups):
            where = f"duplicate_groups[{index}]"
            if not isinstance(group, dict):
                errors.append(f"{where}: group must be an object")
                continue
            digest = group.get("sha256")
            paths = group.get("paths")
            aliases = group.get("aliases")
            if not _valid_digest(digest):
                errors.append(f"{where}: sha256 must be a lowercase SHA-256 digest")
            if (not isinstance(paths, list) or len(paths) < 2
                    or not all(isinstance(path, str) and path for path in paths)
                    or len(set(paths)) != len(paths)):
                errors.append(f"{where}: paths must be a unique list of at least two paths")
                paths = []
            if not isinstance(aliases, list) or aliases != paths[1:]:
                errors.append(f"{where}: aliases must equal paths after the canonical path")
                aliases = []
            for path in paths:
                if path not in path_hashes:
                    errors.append(f"{where}: unknown inventory path {path}")
                elif path_hashes[path] != digest:
                    errors.append(f"{where}: path hash differs from group sha256 for {path}")
                if path in grouped_paths:
                    errors.append(f"{where}: path appears in multiple duplicate groups {path}")
                grouped_paths.add(path)
    return errors


def plan(document: dict[str, Any], source_sha256: str) -> dict[str, Any]:
    errors = validate_inventory(document)
    if errors:
        raise ValueError("; ".join(errors))
    actions: list[dict[str, Any]] = []
    totals: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "bytes": 0})
    dispositions: dict[str, dict[str, int]] = {
        key: {"files": 0, "bytes": 0}
        for key in ("retained", "compressed", "quarantined", "eligible_for_deletion")
    }
    incomplete: list[str] = []
    for record in sorted(document["files"], key=lambda item: item["path"]):
        classification = record["classification"]
        action, _ = CLASS_ACTIONS[classification]
        item = {
            "path": record["path"],
            "bytes": record["bytes"],
            "sha256": record["sha256"],
            "classification": classification,
            "action": action,
            "reversible": action != "retain-private",
            "producer": record["producer"],
            "consumers": record["consumers"],
        }
        if not record["producer"] or not record["consumers"]:
            incomplete.append(record["path"])
        actions.append(item)
        totals[action]["files"] += 1
        totals[action]["bytes"] += record["bytes"]
        disposition = {
            "retain": "retained",
            "retain-private": "retained",
            "quarantine-after-review": "quarantined",
            "remove-after-review": "eligible_for_deletion",
        }[action]
        dispositions[disposition]["files"] += 1
        dispositions[disposition]["bytes"] += record["bytes"]
    duplicate_groups = document.get("duplicate_groups", [])
    if not isinstance(duplicate_groups, list):
        raise ValueError("inventory duplicate_groups must be an array")
    return {
        "schema_version": 1,
        "kind": "von-evidence-cleanup-plan",
        "inventory_sha256": source_sha256,
        "mutation": "none",
        "review_required": True,
        "incomplete_provenance_paths": incomplete,
        "summary": {key: totals[key] for key in sorted(totals)},
        "disposition_summary": dispositions,
        "duplicate_groups": duplicate_groups,
        "actions": actions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        source = args.inventory.read_bytes()
        document = json.loads(source)
        result = plan(document, inventory_digest(source))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Evidence cleanup plan: {error}")
        return 1
    print(f"Evidence cleanup plan: {args.output} ({len(result['actions'])} action(s), no mutation)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
