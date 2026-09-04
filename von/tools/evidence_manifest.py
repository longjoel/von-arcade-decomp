#!/usr/bin/env python3
"""Validate canonical evidence metadata and optionally execute verifiers."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def safe_path(path_text: object) -> bool:
    if not isinstance(path_text, str):
        return False
    path = Path(path_text)
    return not path.is_absolute() and ".." not in path.parts


def rooted(root: Path, path_text: object) -> Path | None:
    if not safe_path(path_text):
        return None
    candidate = root / path_text
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def validate(manifest: dict, ledger: dict, root: Path) -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["evidence manifest must be an object"]
    if manifest.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    unit_ids = {
        unit.get("id") for image in ledger.get("images", [])
        for unit in image.get("work_units", [])
        if isinstance(unit, dict) and isinstance(unit.get("id"), str)
    }
    ids: set[str] = set()
    entries = manifest.get("entries", [])
    if not isinstance(entries, list):
        return ["entries must be an array"]
    for index, entry in enumerate(entries):
        where = f"entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{where}: entry must be an object")
            continue
        evidence_id = entry.get("id")
        if not isinstance(evidence_id, str) or not evidence_id or evidence_id in ids:
            errors.append(f"{where}: missing or duplicate stable id")
        elif evidence_id:
            ids.add(evidence_id)
        if not entry.get("canonical"):
            continue
        stimulus = entry.get("stimulus", {})
        if not isinstance(stimulus, dict):
            stimulus = {}
        if not isinstance(stimulus, dict) or not stimulus.get("kind") or not stimulus.get("description"):
            errors.append(f"{where}: canonical stimulus is incomplete")
        if stimulus.get("kind") in {"input-free-attract", "bounded-trace", "causal-trace"}:
            sidecar = entry.get("capture_manifest")
            if not safe_path(sidecar):
                errors.append(f"{where}: runtime evidence requires capture_manifest")
            else:
                sidecar_path = rooted(root, sidecar)
                if sidecar_path is None or not sidecar_path.is_file():
                    errors.append(f"{where}: missing capture manifest {sidecar}")
                else:
                    try:
                        from capture_manifest import validate as validate_capture

                        capture_document = json.loads(sidecar_path.read_text(encoding="utf-8"))
                        if not isinstance(capture_document, dict):
                            sidecar_errors = ["capture manifest must be an object"]
                        else:
                            sidecar_errors = validate_capture(capture_document, root)
                            if capture_document.get("id") != evidence_id:
                                sidecar_errors.append("capture manifest id does not match evidence id")
                            capture_stimulus = capture_document.get("stimulus", {})
                            if (isinstance(capture_stimulus, dict)
                                    and capture_stimulus.get("kind") != stimulus.get("kind")):
                                sidecar_errors.append("capture stimulus kind does not match evidence entry")
                            if (isinstance(stimulus.get("seconds"), (int, float))
                                    and capture_stimulus.get("seconds") != stimulus.get("seconds")):
                                sidecar_errors.append("capture stimulus duration does not match evidence entry")
                            capture_configuration = capture_document.get("configuration", {})
                            if isinstance(capture_configuration, dict):
                                for field, value in configuration_fields(entry).items():
                                    if capture_configuration.get(field) != value:
                                        sidecar_errors.append(
                                            f"capture configuration.{field} does not match evidence entry")
                            capture_artifacts = capture_document.get("artifacts", [])
                            if isinstance(capture_artifacts, list) and isinstance(entry.get("artifacts"), list):
                                if capture_artifacts != entry["artifacts"]:
                                    sidecar_errors.append("capture artifacts do not match evidence entry")
                    except (OSError, json.JSONDecodeError, TypeError) as exc:
                        sidecar_errors = [f"unable to read capture manifest: {exc}"]
                    errors.extend(f"{where}: {error}" for error in sidecar_errors)
        configuration = entry.get("configuration", {})
        for field in ("mame_revision", "patch_profile", "execution_engine"):
            if not configuration.get(field):
                errors.append(f"{where}: missing configuration.{field}")
        if entry.get("outcome") != "pass":
            errors.append(f"{where}: canonical outcome must be pass")
        verifier = entry.get("verifier")
        verifier_path = rooted(root, verifier)
        if verifier_path is None or not verifier_path.is_file():
            errors.append(f"{where}: verifier is missing")
        consumers = entry.get("consumers", [])
        if (not isinstance(consumers, list) or not consumers
                or not all(isinstance(consumer, str) for consumer in consumers)
                or any(consumer not in unit_ids for consumer in consumers)):
            errors.append(f"{where}: must name existing ledger consumers")
        artifacts = entry.get("artifacts", [])
        if not isinstance(artifacts, list) or not artifacts:
            errors.append(f"{where}: no artifacts")
        for artifact in artifacts if isinstance(artifacts, list) else []:
            if not isinstance(artifact, dict) or not safe_path(artifact.get("path")):
                errors.append(f"{where}: invalid artifact path")
                continue
            path = rooted(root, artifact["path"])
            if path is None:
                errors.append(f"{where}: invalid artifact path")
                continue
            if not path.is_file():
                errors.append(f"{where}: missing artifact {artifact.get('path')}")
                continue
            if not isinstance(artifact.get("sha256"), str) or not SHA256_RE.fullmatch(artifact["sha256"]):
                errors.append(f"{where}: artifact sha256 must be a SHA-256 digest")
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != artifact.get("sha256"):
                errors.append(f"{where}: hash mismatch for {artifact.get('path')}")
    return errors


def configuration_fields(entry: dict) -> dict:
    """Return sidecar-bound configuration fields declared by the evidence entry."""
    configuration = entry.get("configuration", {})
    if not isinstance(configuration, dict):
        return {}
    return {field: configuration[field] for field in
            ("set", "mame_revision", "patch_profile", "execution_engine")
            if field in configuration}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("von/evidence/manifest.json"))
    parser.add_argument("--ledger", type=Path, default=Path("von/reconstruction_ledger.json"))
    parser.add_argument("--run-verifiers", action="store_true")
    args = parser.parse_args()
    root = Path.cwd()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    ledger = json.loads(args.ledger.read_text(encoding="utf-8"))
    errors = validate(manifest, ledger, root)
    if errors:
        print(f"Evidence validation: {len(errors)} error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    canonical = [entry for entry in manifest.get("entries", []) if entry.get("canonical")]
    if args.run_verifiers:
        for entry in canonical:
            completed = subprocess.run([sys.executable, entry["verifier"]], cwd=root)
            if completed.returncode:
                return completed.returncode
    print(f"Evidence validation: {len(canonical)}/{len(canonical)} canonical entries healthy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
