#!/usr/bin/env python3
"""Register a validated capture sidecar as canonical evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from capture_manifest import safe_path, validate as validate_capture


def register(
    manifest: dict, capture: dict, capture_path: Path, description: str,
    verifier: str, consumers: list[str], root: Path, ledger: dict | None = None,
) -> list[str]:
    errors = validate_capture(capture, root)
    if errors:
        return [f"capture: {error}" for error in errors]
    capture_id = capture.get("id")
    try:
        capture_relative = str(capture_path.resolve().relative_to(root.resolve()))
    except ValueError:
        capture_relative = ""
    if not safe_path(capture_relative) or not capture_path.is_file():
        return [f"missing capture manifest {capture_path}"]
    try:
        stored_capture = json.loads(capture_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"unable to read capture manifest {capture_path}: {exc}"]
    if stored_capture != capture:
        return ["capture manifest argument differs from on-disk sidecar"]
    entries = manifest.setdefault("entries", [])
    if any(entry.get("id") == capture_id for entry in entries):
        return [f"duplicate evidence id {capture_id}"]
    if not safe_path(verifier) or not (root / verifier).is_file():
        return [f"missing verifier {verifier}"]
    if not consumers:
        return ["at least one ledger consumer is required"]
    if ledger is not None:
        unit_ids = {
            unit.get("id") for image in ledger.get("images", [])
            for unit in image.get("work_units", [])
        }
        unknown = sorted(set(consumers) - unit_ids)
        if unknown:
            return [f"unknown ledger consumers: {', '.join(unknown)}"]
        for image in ledger.get("images", []):
            for unit in image.get("work_units", []):
                if unit.get("id") in consumers:
                    evidence = unit.setdefault("evidence", [])
                    if not isinstance(evidence, list):
                        return [f"ledger consumer {unit['id']} has invalid evidence list"]
                    if capture_id not in evidence:
                        evidence.append(capture_id)
    entry = {
        "id": capture_id,
        "canonical": True,
        "stimulus": {
            "kind": capture["stimulus"]["kind"],
            "description": description,
            "seconds": capture["stimulus"]["seconds"],
        },
        "configuration": capture["configuration"],
        "inputs": capture.get("inputs", []),
        "artifacts": capture.get("artifacts", []),
        "capture_manifest": capture_relative,
        "verifier": verifier,
        "outcome": "pass",
        "consumers": consumers,
    }
    entries.append(entry)
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--capture-manifest", type=Path, required=True)
    parser.add_argument("--verifier", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--consumer", action="append", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--ledger", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    capture = json.loads(args.capture_manifest.read_text(encoding="utf-8"))
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    errors = register(
        manifest, capture, args.capture_manifest, args.description,
        args.verifier, args.consumer, root, ledger,
    )
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    args.ledger.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    print(f"Registered canonical evidence: {capture['id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
