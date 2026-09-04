#!/usr/bin/env python3
"""Schema-v2 reconstruction ledger validation and accounting helpers."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

CLASSIFICATIONS = {"code", "data", "padding", "unknown", "behavior"}
PHYSICAL_CLASSIFICATIONS = CLASSIFICATIONS - {"behavior"}
STAGES = {
    "planned", "modeled", "integrated", "trace-validated",
    "byte-validated", "blocked",
}
STAGE_ORDER = {stage: index for index, stage in enumerate(
    ("planned", "modeled", "integrated", "trace-validated", "byte-validated")
)}
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def validate_lifecycle(
    ledger: dict[str, Any], manifest: dict[str, Any], root: Path | None = None
) -> list[str]:
    """Validate stage-specific promotion evidence.

    This is intentionally separate from schema validation: existing ledgers can
    be inspected for structural problems while migration debt is made explicit
    with the strict lifecycle check.
    """
    errors: list[str] = []

    def safe_reference(value: Any) -> bool:
        if not isinstance(value, str) or not value:
            return False
        path = Path(value)
        if path.is_absolute() or ".." in path.parts:
            return False
        if root is not None:
            try:
                (root / path).resolve().relative_to(root.resolve())
            except (OSError, RuntimeError, ValueError):
                return False
        return True

    def existing_reference(value: str) -> bool:
        if root is None:
            return True
        path = root / value
        return not path.is_symlink() and path.is_file()

    def verifier_hash_errors(where: str, entry: dict[str, Any]) -> None:
        digest = entry.get("verifier_sha256")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            errors.append(f"{where}: canonical evidence requires verifier_sha256")
            return
        verifier = entry.get("verifier")
        if root is not None and isinstance(verifier, str) and existing_reference(verifier):
            actual = hashlib.sha256((root / verifier).read_bytes()).hexdigest()
            if actual != digest:
                errors.append(f"{where}: canonical verifier hash mismatch")

    def nonempty_text(value: Any) -> bool:
        return isinstance(value, str) and bool(value)

    def validate_modeling(where: str, unit: dict[str, Any]) -> None:
        modeling = unit.get("modeling")
        if not isinstance(modeling, dict):
            errors.append(f"{where}: {unit.get('stage')} requires preceding modeling evidence")
            return
        for field in ("boundary", "test", "unresolved_behavior"):
            if not nonempty_text(modeling.get(field)):
                errors.append(f"{where}: {unit.get('stage')} requires modeling.{field}")
        test = modeling.get("test")
        if test and not safe_reference(test):
            errors.append(f"{where}: modeling.test must be a safe relative path")
        elif isinstance(test, str) and not existing_reference(test):
            errors.append(f"{where}: missing modeling test {test}")

    def validate_integration(where: str, unit: dict[str, Any]) -> None:
        integration = unit.get("integration")
        if not isinstance(integration, dict):
            errors.append(f"{where}: {unit.get('stage')} requires preceding integration evidence")
            return
        image = integration.get("image")
        if not nonempty_text(image):
            errors.append(f"{where}: {unit.get('stage')} requires integration.image")
        elif not safe_reference(image):
            errors.append(f"{where}: integration.image must be a safe relative path")
        elif root is not None and not existing_reference(image):
            errors.append(f"{where}: missing integration image {image}")
        if not nonempty_text(integration.get("checkpoint")):
            errors.append(f"{where}: {unit.get('stage')} requires integration.checkpoint")
        test = integration.get("test")
        if not nonempty_text(test):
            errors.append(f"{where}: {unit.get('stage')} requires integration.test")
        elif not safe_reference(test):
            errors.append(f"{where}: integration.test must be a safe relative path")
        elif not existing_reference(test):
            errors.append(f"{where}: missing integration test {test}")

    def validate_evidence_checkpoint(where: str, unit: dict[str, Any],
                                     evidence_entry: dict[str, Any]) -> None:
        checkpoint = unit.get("integration", {}).get("checkpoint")
        checkpoints = evidence_entry.get("checkpoints")
        if not isinstance(checkpoints, list) or checkpoint not in checkpoints:
            errors.append(f"{where}: canonical evidence does not declare integration checkpoint")

    active_modeled: list[str] = []
    manifest_entries = manifest.get("entries", []) if isinstance(manifest, dict) else []
    manifest_ids: set[str] = set()
    if isinstance(manifest_entries, list):
        for index, entry in enumerate(manifest_entries):
            if not isinstance(entry, dict):
                continue
            evidence_id = entry.get("id")
            if isinstance(evidence_id, str) and evidence_id:
                if evidence_id in manifest_ids:
                    errors.append(f"manifest.entries[{index}]: duplicate stable id")
                manifest_ids.add(evidence_id)
            if not isinstance(entry.get("canonical"), bool):
                errors.append(f"manifest.entries[{index}]: canonical must be boolean")
    canonical_entries = {
        entry.get("id"): entry
        for entry in manifest_entries
        if isinstance(entry, dict) and entry.get("canonical") is True and isinstance(entry.get("id"), str)
    } if isinstance(manifest_entries, list) else {}
    canonical_ids = set(canonical_entries)
    for image in ledger.get("images", []):
        image_name = image.get("name", "?")
        for index, unit in enumerate(image.get("work_units", [])):
            where = f"images[{image_name}].work_units[{index}]"
            stage = unit.get("stage")
            if "active" in unit and not isinstance(unit.get("active"), bool):
                errors.append(f"{where}: active must be boolean")
            if unit.get("active") is True and stage != "modeled":
                errors.append(f"{where}: active work-in-progress must be modeled")
            if stage == "modeled" and unit.get("active") is True:
                active_modeled.append(str(unit.get("id", "<missing>")))
            stage_rank = STAGE_ORDER.get(stage, -1)
            if stage_rank >= STAGE_ORDER["modeled"]:
                validate_modeling(where, unit)
            if stage_rank >= STAGE_ORDER["integrated"]:
                validate_integration(where, unit)
            if stage == "planned":
                if not nonempty_text(unit.get("notes")):
                    errors.append(f"{where}: planned requires a reason in notes")
            elif stage == "modeled":
                pass
            elif stage == "integrated":
                pass
            elif stage == "trace-validated":
                evidence_id = unit.get("canonical_evidence_id")
                if not isinstance(evidence_id, str) or evidence_id not in canonical_ids:
                    errors.append(f"{where}: trace-validated requires canonical evidence id")
                verifier = unit.get("verifier")
                if not isinstance(verifier, str) or not verifier:
                    errors.append(f"{where}: trace-validated requires verifier")
                elif not safe_reference(verifier):
                    errors.append(f"{where}: verifier must be a safe relative path")
                elif not existing_reference(verifier):
                    errors.append(f"{where}: missing verifier {verifier}")
                registered_entry = canonical_entries.get(evidence_id, {}) if isinstance(evidence_id, str) else {}
                registered_verifier = registered_entry.get("verifier")
                if isinstance(evidence_id, str) and evidence_id in canonical_ids and registered_verifier != verifier:
                    errors.append(f"{where}: verifier differs from canonical evidence entry")
                if (isinstance(evidence_id, str) and evidence_id in canonical_ids
                        and registered_entry.get("outcome") != "pass"):
                    errors.append(f"{where}: canonical evidence outcome must be pass")
                if isinstance(evidence_id, str) and evidence_id in canonical_ids:
                    verifier_hash_errors(where, registered_entry)
                    validate_evidence_checkpoint(where, unit, registered_entry)
                verification = unit.get("verification")
                if not isinstance(verification, dict) or verification.get("result") != "pass":
                    errors.append(f"{where}: trace-validated requires verification.result=pass")
                consumers = registered_entry.get("consumers", [])
                if (isinstance(evidence_id, str) and evidence_id in canonical_ids
                        and (not isinstance(consumers, list) or unit.get("id") not in consumers)):
                    errors.append(f"{where}: canonical evidence does not name this unit as a consumer")
            elif stage == "byte-validated":
                evidence_id = unit.get("canonical_evidence_id")
                if not isinstance(evidence_id, str) or evidence_id not in canonical_ids:
                    errors.append(f"{where}: byte-validated requires preceding canonical evidence id")
                else:
                    registered_entry = canonical_entries[evidence_id]
                    if registered_entry.get("outcome") != "pass":
                        errors.append(f"{where}: byte-validated requires passing canonical evidence")
                    if unit.get("id") not in registered_entry.get("consumers", []):
                        errors.append(f"{where}: canonical evidence does not name this byte-validation consumer")
                    validate_evidence_checkpoint(where, unit, registered_entry)
                    if registered_entry.get("verifier") != unit.get("verifier"):
                        errors.append(f"{where}: verifier differs from canonical evidence entry")
                    verifier_hash_errors(where, registered_entry)
                verifier = unit.get("verifier")
                if not isinstance(verifier, str) or not verifier:
                    errors.append(f"{where}: byte-validated requires verifier")
                elif not safe_reference(verifier):
                    errors.append(f"{where}: verifier must be a safe relative path")
                elif not existing_reference(verifier):
                    errors.append(f"{where}: missing verifier {verifier}")
                if not isinstance(unit.get("verification"), dict) or unit["verification"].get("result") != "pass":
                    errors.append(f"{where}: byte-validated requires verification.result=pass")
                comparison = unit.get("byte_validation")
                if not isinstance(comparison, dict):
                    errors.append(f"{where}: byte-validated requires byte validation evidence")
                else:
                    for field in ("original_range", "reconstructed_range", "comparison"):
                        if not nonempty_text(comparison.get(field)):
                            errors.append(f"{where}: byte-validated requires byte_validation.{field}")
                    if comparison.get("comparison") != "match":
                        errors.append(f"{where}: byte validation comparison must be match")
            elif stage == "blocked":
                blocked = unit.get("blocked")
                required = ("missing_fact", "failed_discriminator", "next_experiment")
                if not isinstance(blocked, dict) or any(
                        not nonempty_text(blocked.get(field)) for field in required):
                    errors.append(f"{where}: blocked requires missing fact, discriminator, and next experiment")
    if len(active_modeled) > 1:
        errors.append(
            "modeled work-in-progress limit exceeded: " + ", ".join(active_modeled)
        )
    return errors


def number(value: str | int) -> int:
    return int(value, 0) if isinstance(value, str) else value


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def merged_intervals(intervals: Iterable[tuple[int, int]]) -> list[tuple[int, int]]:
    merged: list[list[int]] = []
    for start, end in sorted(intervals):
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return [(start, end) for start, end in merged]


def code_coverage(ledger: dict[str, Any]) -> dict[str, int]:
    """Count the union of physical code ranges, never semantic work units."""
    by_image: dict[str, int] = {}
    for image in ledger.get("images", []):
        ranges = [
            (number(item["start"]), number(item["end"]))
            for item in image.get("physical_ranges", [])
            if item.get("classification") == "code"
        ]
        by_image[image["name"]] = sum(end - start for start, end in merged_intervals(ranges))
    by_image["total"] = sum(by_image.values())
    return by_image


def validate(ledger: dict[str, Any], root: Path | None = None) -> list[str]:
    errors: list[str] = []
    if ledger.get("schema_version") != 2:
        errors.append("schema_version must be 2")
    seen_ids: set[str] = set()
    for image_index, image in enumerate(ledger.get("images", [])):
        prefix = f"images[{image_index}]"
        size = image.get("size")
        previous_end = -1
        for range_index, item in enumerate(image.get("physical_ranges", [])):
            where = f"{prefix}.physical_ranges[{range_index}]"
            classification = item.get("classification")
            if classification not in PHYSICAL_CLASSIFICATIONS:
                errors.append(f"{where}: invalid physical classification {classification!r}")
                continue
            try:
                start, end = number(item["start"]), number(item["end"])
            except (KeyError, TypeError, ValueError):
                errors.append(f"{where}: start/end must be integers")
                continue
            if start < 0 or end <= start:
                errors.append(f"{where}: invalid half-open range")
            if start < previous_end:
                errors.append(f"{where}: overlaps the preceding physical range")
            if isinstance(size, int) and end > size:
                errors.append(f"{where}: exceeds image size")
            previous_end = max(previous_end, end)

        for unit_index, unit in enumerate(image.get("work_units", [])):
            where = f"{prefix}.work_units[{unit_index}]"
            unit_id = unit.get("id")
            if not isinstance(unit_id, str) or not unit_id:
                errors.append(f"{where}: missing stable id")
            elif unit_id in seen_ids:
                errors.append(f"{where}: duplicate id {unit_id}")
            else:
                seen_ids.add(unit_id)
            if unit.get("classification") not in CLASSIFICATIONS:
                errors.append(f"{where}: invalid classification")
            if unit.get("stage") not in STAGES:
                errors.append(f"{where}: invalid stage")
            sources = unit.get("sources")
            if not isinstance(sources, list) or not all(isinstance(v, str) for v in sources):
                errors.append(f"{where}: sources must be a string array")
            if "source" in unit or "status" in unit:
                errors.append(f"{where}: legacy source/status field is forbidden")
            ranges = unit.get("ranges", [])
            if unit.get("classification") == "behavior" and ranges:
                errors.append(f"{where}: behavior units cannot claim physical bytes")
            for semantic_range in ranges:
                try:
                    start = number(semantic_range["start"])
                    end = number(semantic_range["end"])
                    if start < 0 or end <= start or (isinstance(size, int) and end > size):
                        raise ValueError
                except (KeyError, TypeError, ValueError):
                    errors.append(f"{where}: invalid semantic range")
                    break
            if root is not None:
                for source in sources or []:
                    if source.startswith("von/") or source.startswith("scripts/"):
                        if not (root / source).exists():
                            errors.append(f"{where}: missing source {source}")
    if not isinstance(ledger.get("images"), list):
        errors.append("images must be an array")
    return errors
