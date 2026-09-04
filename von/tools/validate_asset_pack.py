#!/usr/bin/env python3
"""Validate provenance and claim status for a generated evidence asset pack."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


STATUSES = {"legacy-unreviewed", "candidate", "observed", "validated", "rejected", "reference-capture"}
CLAIM_STATUSES = STATUSES | {"unresolved"}
CLAIM_NAMES = {
    "geometry", "source_ranges", "transform_association", "identity", "textures",
    "hierarchy", "animation", "audio_descriptor", "audio_sequence", "source_bytes",
}
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def safe_path(path_text: Any) -> bool:
    if not isinstance(path_text, str):
        return False
    path = Path(path_text)
    return not path.is_absolute() and ".." not in path.parts


def rooted(root: Path, path_text: Any) -> Path | None:
    if not safe_path(path_text):
        return None
    candidate = root / path_text
    try:
        candidate.resolve().relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(pack: dict[str, Any], evidence: dict[str, Any], root: Path,
             rom_manifest: Path | None = None, expected_tool_revision: str | None = None,
             expected_map_revision: str | None = None) -> list[str]:
    errors: list[str] = []
    if pack.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if pack.get("kind") != "von-evidence-asset-pack":
        errors.append("kind must be von-evidence-asset-pack")
    if not pack.get("id"):
        errors.append("missing pack id")
    basis = pack.get("basis", {})
    for field in ("romset_hash", "map_revision", "capture_id", "tool_revision"):
        if not basis.get(field):
            errors.append(f"missing basis.{field}")
    if basis.get("romset_hash") and not SHA256_RE.fullmatch(str(basis["romset_hash"])):
        errors.append("basis.romset_hash must be a SHA-256 digest")
    if expected_tool_revision is not None and basis.get("tool_revision") != expected_tool_revision:
        errors.append("basis.tool_revision does not match expected tool revision")
    if expected_map_revision is not None and basis.get("map_revision") != expected_map_revision:
        errors.append("basis.map_revision does not match expected map revision")
    if rom_manifest is not None:
        if not rom_manifest.is_file():
            errors.append(f"missing ROM manifest {rom_manifest}")
        elif basis.get("romset_hash") != sha256(rom_manifest):
            errors.append("basis.romset_hash does not match ROM manifest")
    canonical_ids = {
        item.get("id") for item in evidence.get("entries", [])
        if item.get("canonical") and isinstance(item.get("id"), str)
    }
    if basis.get("capture_id") not in canonical_ids:
        errors.append(f"unknown canonical basis capture id {basis.get('capture_id')}")
    assets = pack.get("assets")
    if not isinstance(assets, list) or not assets:
        errors.append("assets must be a non-empty array")
        return errors
    seen: set[str] = set()
    for index, asset in enumerate(assets):
        where = f"assets[{index}]"
        if not isinstance(asset, dict):
            errors.append(f"{where}: asset must be an object")
            continue
        asset_id = asset.get("id")
        if not isinstance(asset_id, str) or not asset_id or asset_id in seen:
            errors.append(f"{where}: missing or duplicate id")
        else:
            seen.add(asset_id)
        for field in ("media_type", "payload", "sha256"):
            if not asset.get(field):
                errors.append(f"{where}: missing {field}")
        status = asset.get("status")
        if status not in STATUSES:
            errors.append(f"{where}: invalid status {status!r}")
        payload_text = asset.get("payload")
        payload = rooted(root, payload_text)
        if payload is None or not payload.is_file():
            errors.append(f"{where}: missing payload {asset.get('payload')}")
        elif asset.get("sha256") != sha256(payload):
            errors.append(f"{where}: payload hash mismatch")
        claims = asset.get("claims")
        if not isinstance(claims, dict) or not claims:
            errors.append(f"{where}: claims must be a non-empty object")
        elif any(not isinstance(name, str) or name not in CLAIM_NAMES
                 or not isinstance(value, str) or value not in CLAIM_STATUSES
                 for name, value in claims.items()):
            errors.append(f"{where}: claims must use the supported claim/status vocabulary")
        evidence_ids = asset.get("evidence_ids", [])
        if not isinstance(evidence_ids, list):
            errors.append(f"{where}: evidence_ids must be an array")
            evidence_ids = []
        for evidence_id in evidence_ids:
            if evidence_id not in canonical_ids:
                errors.append(f"{where}: unknown canonical evidence id {evidence_id}")
        verifiers = asset.get("verifiers")
        if not isinstance(verifiers, list) or not verifiers or not all(isinstance(item, str) and item for item in verifiers):
            errors.append(f"{where}: verifiers must be a non-empty string array")
            verifiers = []
        if status in {"observed", "validated", "reference-capture"} and not evidence_ids:
            errors.append(f"{where}: {status} assets require evidence_ids")
        if status == "validated":
            results = asset.get("verifier_results")
            if (not isinstance(results, dict)
                    or set(results) != set(verifiers)
                    or any(result not in {"pass", "fail", "error"} for result in results.values())
                    or any(results.get(verifier) != "pass" for verifier in verifiers)):
                errors.append(f"{where}: validated assets require passing verifier_results")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--evidence-manifest", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--rom-manifest", type=Path,
                        help="optional ROM manifest whose hash must match basis.romset_hash")
    parser.add_argument("--tool-revision",
                        help="optional expected tool revision")
    parser.add_argument("--map-revision",
                        help="optional expected map revision")
    args = parser.parse_args()
    pack = json.loads(args.manifest.read_text(encoding="utf-8"))
    evidence = json.loads(args.evidence_manifest.read_text(encoding="utf-8"))
    errors = validate(pack, evidence, args.root, args.rom_manifest,
                      args.tool_revision, args.map_revision)
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Asset pack validation: {len(pack['assets'])} asset(s) healthy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
