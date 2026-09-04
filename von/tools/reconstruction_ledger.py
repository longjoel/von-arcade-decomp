#!/usr/bin/env python3
"""Schema-v2 reconstruction ledger validation and accounting helpers."""

from __future__ import annotations

import json
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


def validate_lifecycle(
    ledger: dict[str, Any], manifest: dict[str, Any], root: Path | None = None
) -> list[str]:
    """Validate stage-specific promotion evidence.

    This is intentionally separate from schema validation: existing ledgers can
    be inspected for structural problems while migration debt is made explicit
    with the strict lifecycle check.
    """
    errors: list[str] = []
    active_modeled: list[str] = []
    canonical_entries = {
        entry.get("id"): entry
        for entry in manifest.get("entries", [])
        if entry.get("canonical") and isinstance(entry.get("id"), str)
    }
    canonical_ids = set(canonical_entries)
    for image in ledger.get("images", []):
        image_name = image.get("name", "?")
        for index, unit in enumerate(image.get("work_units", [])):
            where = f"images[{image_name}].work_units[{index}]"
            stage = unit.get("stage")
            if stage == "modeled" and unit.get("active") is True:
                active_modeled.append(str(unit.get("id", "<missing>")))
            stage_rank = STAGE_ORDER.get(stage, -1)
            if stage_rank >= STAGE_ORDER["modeled"] and not isinstance(unit.get("modeling"), dict):
                errors.append(f"{where}: {stage} requires preceding modeling evidence")
            if stage_rank >= STAGE_ORDER["integrated"] and not isinstance(unit.get("integration"), dict):
                errors.append(f"{where}: {stage} requires preceding integration evidence")
            if stage == "planned":
                if not unit.get("notes"):
                    errors.append(f"{where}: planned requires a reason in notes")
            elif stage == "modeled":
                modeling = unit.get("modeling")
                if not isinstance(modeling, dict):
                    errors.append(f"{where}: modeled requires modeling evidence")
                    continue
                for field in ("boundary", "test", "unresolved_behavior"):
                    if not modeling.get(field):
                        errors.append(f"{where}: modeled requires modeling.{field}")
                test = modeling.get("test")
                if isinstance(test, str) and root is not None and not (root / test).is_file():
                    errors.append(f"{where}: missing modeling test {test}")
            elif stage == "integrated":
                integration = unit.get("integration")
                if not isinstance(integration, dict):
                    errors.append(f"{where}: integrated requires integration evidence")
                    continue
                if not integration.get("image"):
                    errors.append(f"{where}: integrated requires integration.image")
                if not integration.get("checkpoint"):
                    errors.append(f"{where}: integrated requires integration.checkpoint")
                test = integration.get("test")
                if not isinstance(test, str) or not test:
                    errors.append(f"{where}: integrated requires integration.test")
                elif root is not None and not (root / test).is_file():
                    errors.append(f"{where}: missing integration test {test}")
            elif stage == "trace-validated":
                evidence_id = unit.get("canonical_evidence_id")
                if evidence_id not in canonical_ids:
                    errors.append(f"{where}: trace-validated requires canonical evidence id")
                verifier = unit.get("verifier")
                if not isinstance(verifier, str) or not verifier:
                    errors.append(f"{where}: trace-validated requires verifier")
                elif root is not None and not (root / verifier).is_file():
                    errors.append(f"{where}: missing verifier {verifier}")
                registered_verifier = canonical_entries.get(evidence_id, {}).get("verifier")
                if registered_verifier and registered_verifier != verifier:
                    errors.append(f"{where}: verifier differs from canonical evidence entry")
                consumers = canonical_entries.get(evidence_id, {}).get("consumers", [])
                if evidence_id in canonical_ids and unit.get("id") not in consumers:
                    errors.append(f"{where}: canonical evidence does not name this unit as a consumer")
            elif stage == "byte-validated":
                comparison = unit.get("byte_validation")
                if not isinstance(comparison, dict):
                    errors.append(f"{where}: byte-validated requires byte validation evidence")
                else:
                    for field in ("original_range", "reconstructed_range", "comparison"):
                        if not comparison.get(field):
                            errors.append(f"{where}: byte-validated requires byte_validation.{field}")
                    if comparison.get("comparison") != "match":
                        errors.append(f"{where}: byte validation comparison must be match")
            elif stage == "blocked":
                blocked = unit.get("blocked")
                required = ("missing_fact", "failed_discriminator", "next_experiment")
                if not isinstance(blocked, dict) or any(not blocked.get(field) for field in required):
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
