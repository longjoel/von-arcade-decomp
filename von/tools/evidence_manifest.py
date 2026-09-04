#!/usr/bin/env python3
"""Validate canonical evidence metadata and optionally execute verifiers."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def validate(manifest: dict, ledger: dict, root: Path) -> list[str]:
    errors: list[str] = []
    unit_ids = {unit["id"] for image in ledger.get("images", []) for unit in image.get("work_units", [])}
    ids: set[str] = set()
    for index, entry in enumerate(manifest.get("entries", [])):
        where = f"entries[{index}]"
        evidence_id = entry.get("id")
        if not evidence_id or evidence_id in ids:
            errors.append(f"{where}: missing or duplicate stable id")
        ids.add(evidence_id)
        if not entry.get("canonical"):
            continue
        stimulus = entry.get("stimulus", {})
        if not stimulus.get("kind") or not stimulus.get("description"):
            errors.append(f"{where}: canonical stimulus is incomplete")
        if stimulus.get("kind") in {"input-free-attract", "bounded-trace", "causal-trace"}:
            sidecar = entry.get("capture_manifest")
            if not isinstance(sidecar, str) or not sidecar:
                errors.append(f"{where}: runtime evidence requires capture_manifest")
            else:
                sidecar_path = root / sidecar
                if not sidecar_path.is_file():
                    errors.append(f"{where}: missing capture manifest {sidecar}")
                else:
                    try:
                        from capture_manifest import validate as validate_capture

                        capture_document = json.loads(sidecar_path.read_text(encoding="utf-8"))
                        sidecar_errors = validate_capture(capture_document, root)
                        if capture_document.get("id") != evidence_id:
                            sidecar_errors.append("capture manifest id does not match evidence id")
                    except (OSError, json.JSONDecodeError) as exc:
                        sidecar_errors = [f"unable to read capture manifest: {exc}"]
                    errors.extend(f"{where}: {error}" for error in sidecar_errors)
        configuration = entry.get("configuration", {})
        for field in ("mame_revision", "patch_profile", "execution_engine"):
            if not configuration.get(field):
                errors.append(f"{where}: missing configuration.{field}")
        if entry.get("outcome") != "pass":
            errors.append(f"{where}: canonical outcome must be pass")
        verifier = entry.get("verifier")
        if not verifier or not (root / verifier).is_file():
            errors.append(f"{where}: verifier is missing")
        consumers = entry.get("consumers", [])
        if not consumers or any(consumer not in unit_ids for consumer in consumers):
            errors.append(f"{where}: must name existing ledger consumers")
        artifacts = entry.get("artifacts", [])
        if not artifacts:
            errors.append(f"{where}: no artifacts")
        for artifact in artifacts:
            path = root / artifact.get("path", "")
            if not path.is_file():
                errors.append(f"{where}: missing artifact {artifact.get('path')}")
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != artifact.get("sha256"):
                errors.append(f"{where}: hash mismatch for {artifact.get('path')}")
    return errors


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
