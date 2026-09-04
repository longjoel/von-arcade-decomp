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
MEDIA_TYPES = {"model", "texture", "audio-sample", "audio-sequence", "video", "image"}
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
    except (OSError, RuntimeError, ValueError):
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
    if not isinstance(pack, dict):
        return ["asset pack must be an object"]
    if not isinstance(evidence, dict):
        return ["evidence manifest must be an object"]
    if pack.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if pack.get("kind") != "von-evidence-asset-pack":
        errors.append("kind must be von-evidence-asset-pack")
    if not isinstance(pack.get("id"), str) or not pack.get("id"):
        errors.append("missing pack id")
    basis = pack.get("basis", {})
    if not isinstance(basis, dict):
        errors.append("basis must be an object")
        basis = {}
    for field in ("romset_hash", "map_revision", "capture_id", "tool_revision"):
        if not isinstance(basis.get(field), str) or not basis.get(field):
            errors.append(f"missing basis.{field}")
    if basis.get("romset_hash") and not SHA256_RE.fullmatch(str(basis["romset_hash"])):
        errors.append("basis.romset_hash must be a SHA-256 digest")
    if expected_tool_revision is not None and basis.get("tool_revision") != expected_tool_revision:
        errors.append("basis.tool_revision does not match expected tool revision")
    if expected_map_revision is not None and basis.get("map_revision") != expected_map_revision:
        errors.append("basis.map_revision does not match expected map revision")
    if rom_manifest is not None:
        try:
            rom_manifest.resolve().relative_to(root.resolve())
        except (OSError, RuntimeError, ValueError):
            errors.append(f"ROM manifest escapes pack root: {rom_manifest}")
        if rom_manifest.is_symlink() or not rom_manifest.is_file():
            errors.append(f"missing ROM manifest {rom_manifest}")
        elif not any("escapes pack root" in error for error in errors):
            if basis.get("romset_hash") != sha256(rom_manifest):
                errors.append("basis.romset_hash does not match ROM manifest")
    evidence_entries = evidence.get("entries", [])
    if not isinstance(evidence_entries, list):
        errors.append("evidence entries must be an array")
        evidence_entries = []
    evidence_ids: set[str] = set()
    for index, entry in enumerate(evidence_entries):
        where = f"evidence.entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{where}: entry must be an object")
            continue
        evidence_id = entry.get("id")
        if not isinstance(evidence_id, str) or not evidence_id:
            errors.append(f"{where}: id must be a non-empty string")
        elif evidence_id in evidence_ids:
            errors.append(f"{where}: duplicate evidence id {evidence_id}")
        else:
            evidence_ids.add(evidence_id)
        if not isinstance(entry.get("canonical"), bool):
            errors.append(f"{where}: canonical must be boolean")
    canonical_ids = {
        item.get("id") for item in evidence_entries
        if isinstance(item, dict) and item.get("canonical") is True and isinstance(item.get("id"), str)
    }
    canonical_entries = {
        item.get("id"): item for item in evidence_entries
        if isinstance(item, dict) and item.get("canonical") is True and isinstance(item.get("id"), str)
    }
    for evidence_id, entry in canonical_entries.items():
        verifier = entry.get("verifier")
        verifier_path = rooted(root, verifier)
        if verifier_path is None or verifier_path.is_symlink() or not verifier_path.is_file():
            errors.append(f"canonical evidence {evidence_id} has missing verifier")
            continue
        verifier_digest = entry.get("verifier_sha256")
        if not isinstance(verifier_digest, str) or not SHA256_RE.fullmatch(verifier_digest):
            errors.append(f"canonical evidence {evidence_id} requires verifier_sha256")
        elif verifier_digest != sha256(verifier_path):
            errors.append(f"canonical evidence {evidence_id} verifier hash mismatch")
    if basis.get("capture_id") not in canonical_ids:
        errors.append(f"unknown canonical basis capture id {basis.get('capture_id')}")
    elif canonical_entries[basis["capture_id"]].get("outcome") != "pass":
        errors.append("basis capture evidence outcome must be pass")
    assets = pack.get("assets")
    if not isinstance(assets, list) or not assets:
        errors.append("assets must be a non-empty array")
        return errors
    seen: set[str] = set()
    payload_paths: set[Path] = set()
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
        if asset.get("media_type") not in MEDIA_TYPES:
            errors.append(f"{where}: unsupported media_type {asset.get('media_type')!r}")
        status = asset.get("status")
        if status not in STATUSES:
            errors.append(f"{where}: invalid status {status!r}")
        payload_text = asset.get("payload")
        payload = rooted(root, payload_text)
        if payload is None or payload.is_symlink() or not payload.is_file():
            errors.append(f"{where}: missing payload {asset.get('payload')}")
        else:
            try:
                resolved_payload = payload.resolve()
            except (OSError, RuntimeError) as error:
                errors.append(f"{where}: invalid payload path {asset.get('payload')}: {error}")
                continue
            if resolved_payload in payload_paths:
                errors.append(f"{where}: payload is shared by multiple assets")
            else:
                payload_paths.add(resolved_payload)
            if asset.get("sha256") != sha256(payload):
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
        elif all(isinstance(item, str) for item in evidence_ids) and len(set(evidence_ids)) != len(evidence_ids):
            errors.append(f"{where}: evidence_ids must be unique")
        for evidence_id in evidence_ids:
            if not isinstance(evidence_id, str) or not evidence_id:
                errors.append(f"{where}: evidence_ids must contain non-empty strings")
            elif evidence_id not in canonical_ids:
                errors.append(f"{where}: unknown canonical evidence id {evidence_id}")
            elif canonical_entries[evidence_id].get("outcome") != "pass":
                errors.append(f"{where}: evidence id {evidence_id} does not have a passing outcome")
        verifiers = asset.get("verifiers")
        if not isinstance(verifiers, list) or not verifiers or not all(isinstance(item, str) and item for item in verifiers):
            errors.append(f"{where}: verifiers must be a non-empty string array")
            verifiers = []
        elif len(set(verifiers)) != len(verifiers):
            errors.append(f"{where}: verifiers must be unique")
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
    root = args.root.resolve()
    paths = [("asset pack", args.manifest), ("evidence manifest", args.evidence_manifest)]
    if args.rom_manifest:
        paths.append(("ROM manifest", args.rom_manifest))
    for label, path in paths:
        if path.is_symlink():
            print(f"Asset pack validation: {label} path must not be a symlink")
            return 1
        try:
            path.resolve().relative_to(root)
        except (OSError, RuntimeError, ValueError):
            print(f"Asset pack validation: {label} path escapes root: {path}")
            return 1
        if not path.is_file():
            print(f"Asset pack validation: missing {label}: {path}")
            return 1
    try:
        pack = json.loads(args.manifest.read_text(encoding="utf-8"))
        evidence = json.loads(args.evidence_manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
        print(f"Asset pack validation: unable to read validation document: {error}")
        return 1
    errors = validate(pack, evidence, root, args.rom_manifest,
                      args.tool_revision, args.map_revision)
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Asset pack validation: {len(pack['assets'])} asset(s) healthy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
