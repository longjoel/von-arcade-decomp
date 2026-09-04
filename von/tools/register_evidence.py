#!/usr/bin/env python3
"""Register a validated capture sidecar as canonical evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from capture_manifest import rooted, safe_path, validate as validate_capture


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def register(
    manifest: dict, capture: dict, capture_path: Path, description: str,
    verifier: str, consumers: list[str], root: Path, ledger: dict | None = None,
) -> list[str]:
    if not isinstance(manifest, dict):
        return ["evidence manifest must be an object"]
    if manifest.get("schema_version") != 1:
        return ["evidence manifest schema_version must be 1"]
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        return ["evidence manifest entries must be an array"]
    existing_ids: set[str] = set()
    for index, existing in enumerate(entries):
        if not isinstance(existing, dict) or not isinstance(existing.get("id"), str) or not existing.get("id"):
            return [f"evidence manifest entries[{index}] must have a stable id"]
        if not isinstance(existing.get("canonical"), bool):
            return [f"evidence manifest entries[{index}] canonical must be boolean"]
        if existing["id"] in existing_ids:
            return [f"duplicate evidence id {existing['id']}"]
        existing_ids.add(existing["id"])
    errors = validate_capture(capture, root)
    if errors:
        return [f"capture: {error}" for error in errors]
    capture_id = capture.get("id")
    try:
        capture_relative = str(capture_path.resolve().relative_to(root.resolve()))
    except (OSError, RuntimeError, ValueError):
        capture_relative = ""
    if not safe_path(capture_relative) or capture_path.is_symlink() or not capture_path.is_file():
        return [f"missing capture manifest {capture_path}"]
    try:
        stored_capture = json.loads(capture_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"unable to read capture manifest {capture_path}: {exc}"]
    if stored_capture != capture:
        return ["capture manifest argument differs from on-disk sidecar"]
    if any(entry.get("id") == capture_id for entry in entries):
        return [f"duplicate evidence id {capture_id}"]
    verifier_path = rooted(root, verifier)
    if verifier_path is None or verifier_path.is_symlink() or not verifier_path.is_file():
        return [f"missing verifier {verifier}"]
    if not isinstance(consumers, list) or not all(
        isinstance(consumer, str) and consumer for consumer in consumers
    ):
        return ["ledger consumers must be a non-empty string array"]
    if not consumers:
        return ["at least one ledger consumer is required"]
    if len(set(consumers)) != len(consumers):
        return ["ledger consumers must be unique"]
    if ledger is not None:
        if not isinstance(ledger, dict):
            return ["ledger must be an object"]
        images = ledger.get("images")
        if not isinstance(images, list):
            return ["ledger images must be an array"]
        for image_index, image in enumerate(images):
            if not isinstance(image, dict):
                return [f"ledger images[{image_index}] must be an object"]
            work_units = image.get("work_units")
            if not isinstance(work_units, list):
                return [f"ledger images[{image_index}] work_units must be an array"]
            for unit_index, unit in enumerate(work_units):
                if not isinstance(unit, dict) or not isinstance(unit.get("id"), str) or not unit.get("id"):
                    return [f"ledger images[{image_index}] work_units[{unit_index}] must have a stable id"]
        unit_ids = {
            unit.get("id") for image in ledger.get("images", [])
            for unit in image.get("work_units", [])
        }
        unknown = sorted(set(consumers) - unit_ids)
        if unknown:
            return [f"unknown ledger consumers: {', '.join(unknown)}"]
        consumer_units = []
        for image in ledger.get("images", []):
            for unit in image.get("work_units", []):
                if unit.get("id") in consumers:
                    evidence = unit.get("evidence")
                    if evidence is not None and not isinstance(evidence, list):
                        return [f"ledger consumer {unit['id']} has invalid evidence list"]
                    consumer_units.append((unit, evidence))
        for unit, evidence in consumer_units:
            if evidence is None:
                evidence = []
                unit["evidence"] = evidence
            if capture_id not in evidence:
                evidence.append(capture_id)
    stimulus = {
        "kind": capture["stimulus"]["kind"],
        "description": description,
        "seconds": capture["stimulus"]["seconds"],
    }
    if capture["stimulus"].get("phase") is not None:
        stimulus["phase"] = capture["stimulus"]["phase"]
    entry = {
        "id": capture_id,
        "canonical": True,
        "hypothesis": capture["hypothesis"],
        "expected_discriminator": capture["expected_discriminator"],
        "stimulus": stimulus,
        "checkpoints": capture["checkpoints"],
        "configuration": capture["configuration"],
        "inputs": capture.get("inputs", []),
        "artifacts": capture.get("artifacts", []),
        "capture_manifest": capture_relative,
        "capture_manifest_sha256": sha256(capture_path),
        "verifier": verifier,
        "verifier_sha256": sha256(verifier_path),
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
    for label, path in (("manifest", args.manifest),
                        ("capture manifest", args.capture_manifest),
                        ("ledger", args.ledger)):
        if path.is_symlink():
            print(f"Evidence registration: {label} path must not be a symlink")
            return 1
        try:
            path.resolve().relative_to(root)
        except (OSError, RuntimeError, ValueError):
            print(f"Evidence registration: {label} path escapes root: {path}")
            return 1
        if not path.is_file():
            print(f"Evidence registration: missing {label}: {path}")
            return 1
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
