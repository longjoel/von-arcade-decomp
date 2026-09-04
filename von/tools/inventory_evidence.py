#!/usr/bin/env python3
"""Inventory evidence-related files without modifying or deleting them."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def classify(path: str, tracked: bool) -> tuple[str, str]:
    normalized = path.replace("\\", "/")
    if normalized.startswith("von/build/"):
        return "reproducible-generated", "delete-after-recipe-review"
    if any(part in normalized.split("/") for part in ("rompath", "roms", "private-rom")):
        return "private-rom-material", "keep-ignored"
    if normalized.startswith("von/evidence/") or normalized.endswith("/manifest.json") and "evidence" in normalized:
        return "canonical-evidence", "keep-with-manifest"
    if tracked and (
        normalized.startswith("von/tools/")
        or normalized.startswith("von/i960/")
        or normalized.startswith("scripts/")
    ):
        return "source-and-tests", "keep"
    return "legacy-or-ambiguous", "quarantine-after-review"


def inventory_path(path: Path, root: Path, tracked_paths: set[str]) -> dict[str, Any]:
    relative = str(path.resolve().relative_to(root.resolve()))
    tracked = relative in tracked_paths
    classification, decision = classify(relative, tracked)
    return {
        "path": relative,
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "tracked": tracked,
        "producer": None,
        "consumers": [],
        "classification": classification,
        "decision": decision,
    }


def tracked_files(root: Path) -> set[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files"], capture_output=True, text=True, check=True
    )
    return set(result.stdout.splitlines())


def duplicate_groups(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_hash: dict[str, list[str]] = defaultdict(list)
    for record in records:
        by_hash[record["sha256"]].append(record["path"])
    return [
        {"sha256": digest, "paths": paths, "aliases": paths[1:]}
        for digest, paths in sorted(by_hash.items()) if len(paths) > 1
    ]


def apply_relations(records: list[dict[str, Any]], relations: dict[str, Any]) -> None:
    """Apply reviewed path-to-producer/consumer annotations in place."""
    for record in records:
        relation = relations.get(record["path"], {})
        if not isinstance(relation, dict):
            continue
        producer = relation.get("producer")
        consumers = relation.get("consumers", [])
        if isinstance(producer, str) and producer:
            record["producer"] = producer
        if isinstance(consumers, list) and all(isinstance(item, str) for item in consumers):
            record["consumers"] = consumers


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--path", action="append", required=True, type=Path,
                        help="file or directory to inventory; may be repeated")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--relations", type=Path,
                        help="optional JSON map of relative paths to producer/consumers")
    args = parser.parse_args()
    root = args.root.resolve()
    tracked = tracked_files(root)
    files: list[Path] = []
    for requested in args.path:
        target = requested if requested.is_absolute() else root / requested
        if target.is_file():
            files.append(target)
        elif target.is_dir():
            files.extend(item for item in sorted(target.rglob("*")) if item.is_file())
        else:
            parser.error(f"path does not exist: {requested}")
    records = [inventory_path(path, root, tracked) for path in files]
    if args.relations:
        apply_relations(records, json.loads(args.relations.read_text(encoding="utf-8")))
    document = {
        "schema_version": 1,
        "root": str(root),
        "files": records,
        "duplicate_groups": duplicate_groups(records),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"Inventoried {len(files)} file(s): {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
